from typing import List, Dict, Any
from .block import Block
from .certificate import Certificate

class Blockchain:
    """Blockchain class for certificate validation system"""
    
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_certificates = []
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the blockchain"""
        return Block(0, [], "0")
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_certificate(self, certificate_data: Dict) -> Dict[str, Any]:
        """Add a new certificate to the blockchain"""
        try:
            # Create new block with the certificate
            new_block = Block(
                index=len(self.chain),
                certificates=[certificate_data],
                previous_hash=self.get_latest_block().hash
            )
            self.chain.append(new_block)
            
            return {
                'success': True,
                'message': 'Certificate added to blockchain successfully',
                'block_index': new_block.index,
                'block_hash': new_block.hash,
                'certificate_id': certificate_data.get('certificate_id')
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding certificate: {str(e)}'
            }
    
    def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """Verify if a certificate exists and is valid"""
        try:
            for block in self.chain:
                for cert in block.certificates:
                    if cert.get('certificate_id') == certificate_id:
                        return {
                            'found': True,
                            'valid': cert.get('status') == 'active',
                            'certificate': cert,
                            'block_index': block.index,
                            'block_hash': block.hash,
                            'timestamp': block.timestamp
                        }
            return {'found': False, 'valid': False}
        except Exception as e:
            return {
                'found': False,
                'valid': False,
                'error': str(e)
            }
    
    def get_all_certificates(self) -> List[Dict]:
        """Get all certificates from the blockchain"""
        all_certs = []
        for block in self.chain:
            all_certs.extend(block.certificates)
        return all_certs
    
    def get_certificates_by_student(self, student_id: str) -> List[Dict]:
        """Get all certificates for a specific student"""
        student_certs = []
        for block in self.chain:
            for cert in block.certificates:
                if cert.get('student_id') == student_id:
                    student_certs.append(cert)
        return student_certs
    
    def get_certificates_by_issuer(self, issuer_id: str) -> List[Dict]:
        """Get all certificates issued by a specific institution"""
        issuer_certs = []
        for block in self.chain:
            for cert in block.certificates:
                if cert.get('issuer_id') == issuer_id:
                    issuer_certs.append(cert)
        return issuer_certs
    
    def revoke_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """Revoke a certificate (mark as revoked)"""
        try:
            for block in self.chain:
                for cert in block.certificates:
                    if cert.get('certificate_id') == certificate_id:
                        cert['status'] = 'revoked'
                        return {
                            'success': True,
                            'message': 'Certificate revoked successfully',
                            'certificate_id': certificate_id
                        }
            return {
                'success': False,
                'message': 'Certificate not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error revoking certificate: {str(e)}'
            }
    
    def get_blockchain_info(self) -> Dict[str, Any]:
        """Get blockchain statistics and information"""
        total_certificates = len(self.get_all_certificates())
        active_certificates = len([c for c in self.get_all_certificates() if c.get('status') == 'active'])
        revoked_certificates = total_certificates - active_certificates
        
        return {
            'total_blocks': len(self.chain),
            'total_certificates': total_certificates,
            'active_certificates': active_certificates,
            'revoked_certificates': revoked_certificates,
            'latest_block_hash': self.get_latest_block().hash,
            'chain_length': len(self.chain)
        }
    
    def validate_chain(self) -> bool:
        """Validate the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

# Global blockchain instance
blockchain = Blockchain()
