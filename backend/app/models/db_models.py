"""
SQLAlchemy Database Models Module

This module defines all database tables using SQLAlchemy ORM.
The models represent the database schema for:
- User accounts and authentication
- Institution ECDSA keys
- Certificates (with PII stored privately)
- Blockchain blocks and entries
- Certificate digital signatures

Database Design:
- PII (Personally Identifiable Information) is stored in CertificateDB table
- Only hashes of PII are stored in BlockchainEntry (privacy feature)
- Relationships link certificates to users, blocks, and signatures
"""

from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import hashlib
import time
from datetime import datetime

# ============================================================================
# User Model
# ============================================================================

class User(Base):
    """
    User model for authentication and authorization.
    
    This table stores user accounts with their roles and authentication information.
    Supports three roles: admin, institution, and student.
    
    Fields:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        hashed_password: Bcrypt-hashed password (never store plain text!)
        role: User role (admin, institution, student)
        issuer_id: For institutions - unique identifier
        issuer_name: For institutions - institution name
        is_active: Whether account is active (can be deactivated)
        created_at: Account creation timestamp
    
    Relationships:
        certificates_issued: Certificates issued by this user (if institution)
        private_keys: ECDSA key pairs (if institution)
    """
    __tablename__ = "users"
    
    # Primary key and identification
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)  # Bcrypt hash
    
    # Role and permissions
    role = Column(String(50), nullable=False, default="student")  # admin, institution, student
    
    # Institution-specific fields (only for institutions)
    issuer_id = Column(String(100), nullable=True, index=True)  # Unique institution identifier
    issuer_name = Column(String(255), nullable=True)  # Institution display name
    
    # Account status
    is_active = Column(Boolean, default=True)  # Can be set to False to disable account
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    certificates_issued = relationship(
        "CertificateDB", 
        back_populates="issuer_user", 
        foreign_keys="CertificateDB.issuer_user_id"
    )
    private_keys = relationship("InstitutionKey", back_populates="user")

# ============================================================================
# Institution Key Model
# ============================================================================

class InstitutionKey(Base):
    """
    ECDSA key pair storage for institutions.
    
    This table stores the cryptographic keys used by institutions to sign certificates.
    Each institution gets a unique key pair upon registration.
    
    Security Note:
        - Private keys are stored encrypted (should be encrypted in production!)
        - Public keys can be shared for verification
        - Keys are generated using SECP256R1 curve
    
    Fields:
        id: Primary key
        user_id: Foreign key to User table
        issuer_id: Institution identifier (for quick lookup)
        private_key_encrypted: Base64-encoded PEM private key
        public_key: Base64-encoded PEM public key (used for verification)
        created_at: Key generation timestamp
    
    Relationships:
        user: The user (institution) that owns this key
        signatures: Certificates signed with this key
    """
    __tablename__ = "institution_keys"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Institution identifier (for quick lookup)
    issuer_id = Column(String(100), nullable=False, index=True)
    
    # Cryptographic keys (base64-encoded PEM format)
    private_key_encrypted = Column(Text, nullable=False)  # Should be encrypted in production!
    public_key = Column(Text, nullable=False)  # Can be shared publicly
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="private_keys")
    signatures = relationship("CertificateSignature", back_populates="key")

# ============================================================================
# Certificate Model (Private Database Storage)
# ============================================================================

class CertificateDB(Base):
    """
    Certificate model for private database storage (contains PII).
    
    This table stores the full certificate information including PII (Personally
    Identifiable Information) like student name and grade. This data is NOT
    stored on the blockchain for privacy compliance.
    
    Privacy Design:
        - Full certificate data stored here (private database)
        - Only hash of PII stored on blockchain (BlockchainEntry)
        - Allows verification without exposing personal information
    
    Fields:
        id: Primary key
        certificate_id: Unique certificate identifier (indexed for fast lookup)
        student_name: Student's full name (PII)
        student_id: Student identifier
        course_name: Name of the course
        grade: Student's grade (PII)
        issuer_name: Institution name
        issuer_id: Institution identifier
        issuer_user_id: Foreign key to User who issued this
        course_duration: Duration of the course
        issue_date: Date certificate was issued
        timestamp: Unix timestamp of issuance
        status: Certificate status (active, revoked, expired)
        revocation_reason: Reason for revocation (if revoked)
        created_at: Record creation timestamp
    
    Relationships:
        issuer_user: User who issued this certificate
        blockchain_entry: Corresponding entry on blockchain (hash only)
        signature: Digital signature for this certificate
    """
    __tablename__ = "certificates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Certificate identification
    certificate_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Student information (PII - stored privately, not on blockchain)
    student_name = Column(String(255), nullable=False)  # PII
    student_id = Column(String(100), index=True, nullable=False)
    
    # Course information
    course_name = Column(String(255), nullable=False)
    grade = Column(String(10), nullable=False)  # PII
    
    # Issuer information
    issuer_name = Column(String(255), nullable=False)
    issuer_id = Column(String(100), index=True, nullable=False)
    issuer_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Additional information
    course_duration = Column(String(100), nullable=True)
    issue_date = Column(String(50), nullable=False)  # Format: YYYY-MM-DD
    timestamp = Column(Float, nullable=False)  # Unix timestamp
    
    # Certificate status
    status = Column(String(20), default="active")  # active, revoked, expired
    revocation_reason = Column(Text, nullable=True)  # Reason if revoked
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    issuer_user = relationship("User", foreign_keys=[issuer_user_id])
    blockchain_entry = relationship("BlockchainEntry", back_populates="certificate", uselist=False)
    signature = relationship("CertificateSignature", back_populates="certificate", uselist=False)

# ============================================================================
# Block Model (Blockchain)
# ============================================================================

class Block(Base):
    """
    Block model for blockchain storage.
    
    This table stores blockchain blocks. Each block contains:
    - Block metadata (index, hash, timestamp)
    - Merkle root hash (for efficient verification)
    - Link to previous block (chain integrity)
    
    Blockchain Structure:
        - Genesis block (index 0) has previous_hash="0"
        - Each block links to previous block via hash
        - Merkle root allows verification without processing all entries
    
    Fields:
        id: Primary key
        index: Block index in chain (0 = genesis block)
        previous_hash: Hash of previous block (for chain integrity)
        merkle_root: Root hash of Merkle tree (for certificate verification)
        hash: This block's hash (calculated from all block data)
        timestamp: Block creation timestamp
        created_at: Record creation timestamp
    
    Relationships:
        entries: Blockchain entries (certificate hashes) in this block
    """
    __tablename__ = "blocks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Block identification
    index = Column(Integer, unique=True, index=True, nullable=False)  # Block number in chain
    
    # Blockchain linking
    previous_hash = Column(String(64), nullable=False)  # Hash of previous block
    
    # Merkle tree root (for efficient verification)
    merkle_root = Column(String(64), nullable=True)  # Root hash of Merkle tree
    
    # Block hash (calculated from all block data)
    hash = Column(String(64), unique=True, index=True, nullable=False)
    
    # Timestamps
    timestamp = Column(Float, nullable=False)  # Unix timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    entries = relationship("BlockchainEntry", back_populates="block")

# ============================================================================
# Blockchain Entry Model (Privacy-Preserving)
# ============================================================================

class BlockchainEntry(Base):
    """
    Blockchain entry - stores only hash of PII, not the actual data.
    
    This table stores certificate entries on the blockchain. For privacy compliance,
    only a hash of PII (student name, student ID, grade) is stored, not the actual
    data. The full certificate data is stored in CertificateDB (private database).
    
    Privacy Feature:
        - PII hash stored here (on blockchain)
        - Full PII stored in CertificateDB (private database)
        - Allows verification without exposing personal information
        - Hash ensures data integrity
    
    Fields:
        id: Primary key
        certificate_id: Unique certificate identifier
        certificate_db_id: Foreign key to CertificateDB (full data)
        block_id: Foreign key to Block (which block contains this entry)
        pii_hash: SHA-256 hash of PII data (student_name, student_id, grade)
        block_index: Block index (denormalized for quick lookup)
        block_hash: Block hash (denormalized for quick lookup)
        previous_hash: Previous block hash (denormalized)
        merkle_root: Merkle tree root for this block
        timestamp: Entry timestamp
        created_at: Record creation timestamp
    
    Relationships:
        certificate: Full certificate data (in private database)
        block: Block containing this entry
    """
    __tablename__ = "blockchain_entries"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Certificate reference
    certificate_id = Column(String(100), unique=True, index=True, nullable=False)
    certificate_db_id = Column(Integer, ForeignKey("certificates.id"), nullable=False)
    
    # Block reference
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=True)
    
    # Privacy-preserving hash (NOT the actual PII data)
    pii_hash = Column(String(64), nullable=False)  # SHA-256 hash of PII
    
    # Denormalized block information (for quick lookup without joins)
    block_index = Column(Integer, nullable=False, index=True)
    block_hash = Column(String(64), nullable=False, index=True)
    previous_hash = Column(String(64), nullable=False)
    merkle_root = Column(String(64), nullable=True)  # Merkle tree root for verification
    
    # Timestamps
    timestamp = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    certificate = relationship("CertificateDB", back_populates="blockchain_entry")
    block = relationship("Block", back_populates="entries")

# ============================================================================
# Certificate Signature Model
# ============================================================================

class CertificateSignature(Base):
    """
    Digital signature storage for certificates.
    
    This table stores ECDSA digital signatures for certificates. Each certificate
    is signed by the issuing institution's private key, proving authenticity.
    
    Signature Process:
        1. Institution signs certificate data with private key
        2. Signature is stored here with public key
        3. Verification uses public key to verify signature
        4. Proves certificate was issued by legitimate institution
    
    Fields:
        id: Primary key
        certificate_id: Foreign key to certificate
        institution_key_id: Foreign key to InstitutionKey used for signing
        signature: Base64-encoded ECDSA signature
        public_key: Public key used for verification (denormalized for convenience)
        created_at: Signature creation timestamp
    
    Relationships:
        certificate: The certificate this signature belongs to
        key: The institution key used to create this signature
    """
    __tablename__ = "certificate_signatures"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Certificate reference
    certificate_id = Column(String(100), ForeignKey("certificates.certificate_id"), nullable=False, index=True)
    
    # Key reference
    institution_key_id = Column(Integer, ForeignKey("institution_keys.id"), nullable=False)
    
    # Signature data
    signature = Column(Text, nullable=False)  # Base64-encoded ECDSA signature
    public_key = Column(Text, nullable=False)  # Public key for verification (denormalized)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    certificate = relationship("CertificateDB", back_populates="signature")
    key = relationship("InstitutionKey", back_populates="signatures")
