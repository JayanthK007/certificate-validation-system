"""
Blockchain Service Module

This service manages all blockchain operations with database persistence.
It handles:
- Block creation and management
- Certificate addition to blockchain (with privacy-preserving hashes)
- Certificate verification using Merkle proofs
- Blockchain integrity validation
- Certificate querying and revocation

Key Features:
- Database persistence (replaces in-memory storage)
- Merkle tree support for efficient verification
- Privacy-preserving (only PII hashes on blockchain)
- Transaction management (doesn't commit, lets caller manage)
"""

from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..models.db_models import Block, BlockchainEntry, CertificateDB
from ..utils.merkle_tree import build_merkle_tree, get_merkle_proof, verify_merkle_proof
from ..utils.merkle_tree import hash_data
import hashlib
import json
import time

# ============================================================================
# Blockchain Service Class
# ============================================================================

class BlockchainService:
    """
    Service class for managing blockchain operations with database persistence.
    
    This service provides a clean interface for blockchain operations while
    maintaining transactional integrity. It does NOT commit transactions -
    the calling code manages commits to ensure atomicity.
    
    Responsibilities:
    - Block creation and management
    - Certificate addition to blockchain
    - Certificate verification with Merkle proofs
    - Blockchain integrity validation
    - Certificate querying and management
    """
    
    def __init__(self, db: Session):
        """
        Initialize blockchain service with database session.
        
        Args:
            db: SQLAlchemy database session for database operations
        """
        self.db = db
    
    # ========================================================================
    # Block Management
    # ========================================================================
    
    def get_latest_block(self) -> Optional[Block]:
        """
        Get the most recent block in the blockchain.
        
        Returns:
            Block: The latest block, or None if blockchain is empty
        """
        return self.db.query(Block).order_by(Block.index.desc()).first()
    
    def create_genesis_block(self) -> Block:
        """
        Create the genesis block (first block) if it doesn't exist.
        
        The genesis block is special:
        - Index is 0
        - Previous hash is "0" (no previous block)
        - Empty Merkle root (no certificates yet)
        
        This function is idempotent - safe to call multiple times.
        
        Returns:
            Block: The genesis block (newly created or existing)
        """
        # Check if genesis block already exists
        existing = self.db.query(Block).filter(Block.index == 0).first()
        if existing:
            return existing
        
        # Create genesis block
        genesis = Block(
            index=0,
            previous_hash="0",  # Special value for first block
            merkle_root="",  # Empty (no certificates yet)
            hash=self._calculate_block_hash(0, [], "0", time.time()),
            timestamp=time.time()
        )
        
        # Save to database
        self.db.add(genesis)
        self.db.commit()  # Genesis block creation is independent
        self.db.refresh(genesis)
        return genesis
    
    # ========================================================================
    # Certificate Addition to Blockchain
    # ========================================================================
    
    def add_certificate_to_blockchain(
        self, 
        certificate: CertificateDB, 
        pii_hash: str
    ) -> Dict[str, Any]:
        """
        Add a certificate to the blockchain with Merkle tree support.
        
        This function:
        1. Creates a new block (or uses existing pending block)
        2. Builds a Merkle tree from certificate hashes
        3. Creates a blockchain entry (with PII hash, not actual PII)
        4. Links everything together
        
        Important: This function does NOT commit the transaction.
        The calling code must commit to ensure atomicity across
        certificate, signature, and blockchain entry.
        
        Args:
            certificate: CertificateDB object (full certificate with PII)
            pii_hash: SHA-256 hash of PII data (for privacy-preserving storage)
        
        Returns:
            dict: Result dictionary with:
                - success: Boolean indicating success
                - message: Status message
                - block_index: Index of the block containing this certificate
                - block_hash: Hash of the block
                - merkle_root: Merkle tree root hash
                - certificate_id: ID of the certificate
        
        Note:
            Currently creates one block per certificate for simplicity.
            In production, you might batch multiple certificates per block
            for better efficiency.
        """
        try:
            # ================================================================
            # Get or Create Latest Block
            # ================================================================
            latest_block = self.get_latest_block()
            if not latest_block:
                # No blocks exist, create genesis block
                latest_block = self.create_genesis_block()
            
            # ================================================================
            # Prepare Certificate Hash for Merkle Tree
            # ================================================================
            # For simplicity, we create one block per certificate
            # In production, you might batch multiple certificates per block
            entry_hashes = [pii_hash]
            
            # ================================================================
            # Build Merkle Tree
            # ================================================================
            # Merkle tree allows efficient verification without processing entire block
            merkle_root = build_merkle_tree(entry_hashes)
            
            # ================================================================
            # Create New Block
            # ================================================================
            new_block = Block(
                index=latest_block.index + 1,  # Next block number
                previous_hash=latest_block.hash,  # Link to previous block
                merkle_root=merkle_root,  # Merkle tree root
                hash="",  # Will be calculated below
                timestamp=time.time()
            )
            
            # Calculate block hash (includes all block data)
            new_block.hash = self._calculate_block_hash(
                new_block.index,
                entry_hashes,
                new_block.previous_hash,
                new_block.timestamp,
                merkle_root
            )
            
            # Add block to database (not committed yet)
            self.db.add(new_block)
            self.db.flush()  # Flush to get block.id
            
            # ================================================================
            # Create Blockchain Entry
            # ================================================================
            # This entry stores only the PII hash, not the actual PII data
            # Full certificate data is in CertificateDB (private database)
            blockchain_entry = BlockchainEntry(
                certificate_id=certificate.certificate_id,
                certificate_db_id=certificate.id,  # Link to full certificate data
                pii_hash=pii_hash,  # Privacy-preserving hash
                block_index=new_block.index,
                block_hash=new_block.hash,
                previous_hash=new_block.previous_hash,
                merkle_root=merkle_root,
                timestamp=new_block.timestamp
            )
            blockchain_entry.block_id = new_block.id
            self.db.add(blockchain_entry)
            
            # ================================================================
            # Transaction Management
            # ================================================================
            # Don't commit here - let the calling code manage the transaction
            # This ensures transactional integrity across certificate, signature, and blockchain entry
            # If any part fails, the entire transaction can be rolled back
            self.db.flush()  # Flush changes but don't commit
            
            # Determine if genesis block was just created
            genesis_created = (new_block.index == 1 and latest_block.index == 0)
            
            return {
                'success': True,
                'message': 'Certificate added to blockchain successfully',
                'block_index': new_block.index,
                'block_hash': new_block.hash,
                'merkle_root': merkle_root,
                'certificate_id': certificate.certificate_id,
                'genesis_created': genesis_created  # Indicates if genesis block was just created
            }
        except Exception as e:
            # Rollback is handled by the calling code
            return {
                'success': False,
                'message': f'Error adding certificate: {str(e)}'
            }
    
    # ========================================================================
    # Certificate Verification
    # ========================================================================
    
    def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """
        Verify a certificate using Merkle proof.
        
        This function verifies:
        1. Certificate exists in blockchain
        2. Certificate exists in private database
        3. Certificate status is active
        4. Merkle proof is valid (certificate is in the block)
        
        Process:
        1. Find blockchain entry (contains PII hash)
        2. Find certificate in private database (contains full data)
        3. Find block containing the entry
        4. Generate Merkle proof for the certificate
        5. Verify Merkle proof against block's Merkle root
        
        Args:
            certificate_id: Unique certificate identifier to verify
        
        Returns:
            dict: Verification result with:
                - found: Boolean indicating if certificate was found
                - valid: Boolean indicating if certificate is valid
                - certificate: Full certificate data (if found)
                - blockchain_proof: Merkle proof and block information
                - error: Error message (if verification failed)
        """
        try:
            # ================================================================
            # Find Blockchain Entry
            # ================================================================
            # This entry contains the PII hash stored on blockchain
            entry = self.db.query(BlockchainEntry).filter(
                BlockchainEntry.certificate_id == certificate_id
            ).first()
            
            if not entry:
                return {'found': False, 'valid': False}
            
            # ================================================================
            # Find Certificate in Private Database
            # ================================================================
            # This contains the full certificate data including PII
            certificate = self.db.query(CertificateDB).filter(
                CertificateDB.certificate_id == certificate_id
            ).first()
            
            if not certificate:
                return {'found': False, 'valid': False}
            
            # ================================================================
            # Find Block Containing This Entry
            # ================================================================
            block = self.db.query(Block).filter(Block.id == entry.block_id).first()
            
            # Check if block exists (safety check)
            if not block:
                return {
                    'found': True,
                    'valid': False,
                    'error': 'Block not found for certificate entry'
                }
            
            # ================================================================
            # Verify Merkle Proof
            # ================================================================
            # Get all entries in the same block
            block_entries = self.db.query(BlockchainEntry).filter(
                BlockchainEntry.block_id == block.id
            ).all()
            
            # Extract PII hashes from all entries in the block
            entry_hashes = [e.pii_hash for e in block_entries]
            
            # Generate Merkle proof for this specific certificate
            merkle_proof = get_merkle_proof(entry_hashes, entry.pii_hash)
            
            # Verify the Merkle proof
            # This proves the certificate hash is part of the block without
            # needing to process all certificates in the block
            is_valid_merkle = verify_merkle_proof(
                entry.pii_hash,
                block.merkle_root,
                merkle_proof
            )
            
            # ================================================================
            # Return Verification Result
            # ================================================================
            return {
                'found': True,
                'valid': certificate.status == 'active' and is_valid_merkle,
                'certificate': {
                    'certificate_id': certificate.certificate_id,
                    'student_name': certificate.student_name,
                    'student_id': certificate.student_id,
                    'course_name': certificate.course_name,
                    'grade': certificate.grade,
                    'issuer_name': certificate.issuer_name,
                    'issuer_id': certificate.issuer_id,
                    'course_duration': certificate.course_duration,
                    'issue_date': certificate.issue_date,
                    'timestamp': certificate.timestamp,
                    'status': certificate.status
                },
                'blockchain_proof': {
                    'block_index': entry.block_index,
                    'block_hash': entry.block_hash,
                    'merkle_root': entry.merkle_root,
                    'merkle_proof': merkle_proof,  # Proof for efficient verification
                    'timestamp': entry.timestamp
                }
            }
        except Exception as e:
            return {
                'found': False,
                'valid': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Certificate Querying
    # ========================================================================
    
    def get_all_certificates(self) -> List[Dict]:
        """
        Get all certificates from the database.
        
        Returns:
            List[Dict]: List of certificate dictionaries
        """
        certificates = self.db.query(CertificateDB).all()
        return [self._cert_to_dict(cert) for cert in certificates]
    
    def get_certificates_by_student(self, student_id: str) -> List[Dict]:
        """
        Get all certificates for a specific student.
        
        Args:
            student_id: Student identifier to search for
        
        Returns:
            List[Dict]: List of certificates for the student
        """
        certificates = self.db.query(CertificateDB).filter(
            CertificateDB.student_id == student_id
        ).all()
        return [self._cert_to_dict(cert) for cert in certificates]
    
    def get_certificates_by_issuer(self, issuer_id: str) -> List[Dict]:
        """
        Get all certificates issued by a specific institution.
        
        Args:
            issuer_id: Institution identifier to search for
        
        Returns:
            List[Dict]: List of certificates issued by the institution
        """
        certificates = self.db.query(CertificateDB).filter(
            CertificateDB.issuer_id == issuer_id
        ).all()
        return [self._cert_to_dict(cert) for cert in certificates]
    
    # ========================================================================
    # Certificate Revocation
    # ========================================================================
    
    def revoke_certificate(self, certificate_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Revoke a certificate by marking it as revoked.
        
        Revocation:
        - Changes certificate status to 'revoked'
        - Stores revocation reason
        - Certificate remains in blockchain (immutable)
        - Verification will return valid=False for revoked certificates
        
        Args:
            certificate_id: Certificate identifier to revoke
            reason: Optional reason for revocation
        
        Returns:
            dict: Result dictionary with success status and message
        """
        try:
            # Find certificate
            certificate = self.db.query(CertificateDB).filter(
                CertificateDB.certificate_id == certificate_id
            ).first()
            
            if not certificate:
                return {
                    'success': False,
                    'message': 'Certificate not found'
                }
            
            # Revoke certificate
            certificate.status = 'revoked'
            certificate.revocation_reason = reason
            
            # Commit the revocation
            self.db.commit()
            
            return {
                'success': True,
                'message': 'Certificate revoked successfully',
                'certificate_id': certificate_id
            }
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'message': f'Error revoking certificate: {str(e)}'
            }
    
    # ========================================================================
    # Blockchain Information and Statistics
    # ========================================================================
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """
        Get blockchain statistics and information.
        
        Returns:
            dict: Blockchain statistics including:
                - total_blocks: Number of blocks in chain
                - total_certificates: Total certificates issued
                - active_certificates: Number of active certificates
                - revoked_certificates: Number of revoked certificates
                - latest_block_hash: Hash of the most recent block
                - chain_length: Length of the blockchain
        """
        # Count blocks and certificates
        total_blocks = self.db.query(Block).count()
        total_certificates = self.db.query(CertificateDB).count()
        active_certificates = self.db.query(CertificateDB).filter(
            CertificateDB.status == 'active'
        ).count()
        revoked_certificates = total_certificates - active_certificates
        
        # Get latest block
        latest_block = self.get_latest_block()
        
        return {
            'total_blocks': total_blocks,
            'total_certificates': total_certificates,
            'active_certificates': active_certificates,
            'revoked_certificates': revoked_certificates,
            'latest_block_hash': latest_block.hash if latest_block else "0",
            'chain_length': total_blocks
        }
    
    # ========================================================================
    # Blockchain Validation
    # ========================================================================
    
    def validate_chain(self) -> Dict[str, Any]:
        """
        Validate the integrity of the entire blockchain.
        
        This function checks:
        1. Genesis block is valid (index 0, previous_hash="0")
        2. Each block's hash is correct
        3. Each block correctly links to previous block
        4. Chain is continuous (no gaps)
        
        Returns:
            dict: Validation result with:
                - valid: Boolean indicating if blockchain is valid
                - message: Human-readable message
                - block_count: Number of blocks in chain
                - certificate_count: Number of certificates in chain
        
        Note:
            This is a comprehensive check that validates the entire chain.
            For production, you might want to cache validation results.
        """
        try:
            # Get all blocks in order
            blocks = self.db.query(Block).order_by(Block.index).all()
            block_count = len(blocks)
            
            # Count certificates
            certificate_count = self.db.query(BlockchainEntry).count()
            
            # Empty blockchain is valid (just means no certificates issued yet)
            if block_count == 0:
                return {
                    'valid': True,
                    'message': 'Blockchain is empty (no certificates issued yet). This is valid.',
                    'block_count': 0,
                    'certificate_count': 0
                }
            
            # ================================================================
            # Validate Genesis Block
            # ================================================================
            if blocks[0].index != 0 or blocks[0].previous_hash != "0":
                return {
                    'valid': False,
                    'message': 'Genesis block is invalid (index must be 0, previous_hash must be "0")',
                    'block_count': block_count,
                    'certificate_count': certificate_count
                }
            
            # ================================================================
            # Validate Each Block
            # ================================================================
            for i in range(1, len(blocks)):
                current_block = blocks[i]
                previous_block = blocks[i - 1]
                
                # Verify current block's hash is correct
                calculated_hash = self._calculate_block_hash(
                    current_block.index,
                    [],  # We'd need to reconstruct entry hashes for full validation
                    current_block.previous_hash,
                    current_block.timestamp,
                    current_block.merkle_root
                )
                
                if current_block.hash != calculated_hash:
                    return {
                        'valid': False,
                        'message': f'Block {current_block.index} has invalid hash',
                        'block_count': block_count,
                        'certificate_count': certificate_count
                    }
                
                # Verify block links to previous block correctly
                if current_block.previous_hash != previous_block.hash:
                    return {
                        'valid': False,
                        'message': f'Block {current_block.index} does not link correctly to previous block',
                        'block_count': block_count,
                        'certificate_count': certificate_count
                    }
            
            # All validations passed
            if certificate_count == 0:
                return {
                    'valid': True,
                    'message': f'Blockchain is valid ({block_count} block(s), but no certificates found yet)',
                    'block_count': block_count,
                    'certificate_count': 0
                }
            else:
                return {
                    'valid': True,
                    'message': f'Blockchain is valid ({block_count} block(s), {certificate_count} certificate(s))',
                    'block_count': block_count,
                    'certificate_count': certificate_count
                }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}',
                'block_count': 0,
                'certificate_count': 0
            }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _calculate_block_hash(
        self, 
        index: int, 
        entry_hashes: List[str], 
        previous_hash: str, 
        timestamp: float,
        merkle_root: str = None
    ) -> str:
        """
        Calculate the SHA-256 hash of a block.
        
        The block hash is calculated from:
        - Block index
        - Previous block hash
        - Timestamp
        - Merkle root (represents all certificates in the block)
        
        Args:
            index: Block index number
            entry_hashes: List of certificate hashes (for reference, not used in hash)
            previous_hash: Hash of previous block
            timestamp: Block creation timestamp
            merkle_root: Merkle tree root hash
        
        Returns:
            str: SHA-256 hash of the block
        """
        block_data = {
            'index': index,
            'previous_hash': previous_hash,
            'timestamp': timestamp,
            'merkle_root': merkle_root or ""
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _cert_to_dict(self, cert: CertificateDB) -> Dict:
        """
        Convert a CertificateDB model to a dictionary.
        
        This helper function converts SQLAlchemy models to plain dictionaries
        for JSON serialization in API responses.
        
        Args:
            cert: CertificateDB model instance
        
        Returns:
            dict: Dictionary representation of the certificate
        """
        return {
            'certificate_id': cert.certificate_id,
            'student_name': cert.student_name,
            'student_id': cert.student_id,
            'course_name': cert.course_name,
            'grade': cert.grade,
            'issuer_name': cert.issuer_name,
            'issuer_id': cert.issuer_id,
            'course_duration': cert.course_duration,
            'issue_date': cert.issue_date,
            'timestamp': cert.timestamp,
            'status': cert.status
        }
