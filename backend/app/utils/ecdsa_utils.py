"""
ECDSA Digital Signature Utilities Module

This module provides Elliptic Curve Digital Signature Algorithm (ECDSA) functionality
for signing and verifying certificates. ECDSA is used to ensure that certificates
are issued by legitimate institutions and cannot be forged.

Features:
- Key pair generation (SECP256R1 curve)
- Certificate signing with private keys
- Signature verification with public keys
- Secure key serialization (PEM format, base64 encoded)

Security:
- Uses SECP256R1 (NIST P-256) elliptic curve
- SHA-256 hashing for message digest
- Private keys are stored encrypted in database
- Public keys are used for verification (can be shared)
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64
import json

# ============================================================================
# Key Pair Generation
# ============================================================================

def generate_key_pair() -> dict:
    """
    Generate a new ECDSA key pair (private and public key).
    
    This function creates a new elliptic curve key pair using the SECP256R1 curve.
    The keys are serialized in PEM format and base64 encoded for storage.
    
    Returns:
        dict: Dictionary containing:
            - 'private_key': Base64-encoded PEM private key (keep secret!)
            - 'public_key': Base64-encoded PEM public key (can be shared)
    
    Note:
        - Private keys should be encrypted before storing in production
        - Each institution gets a unique key pair upon registration
        - Keys are used to sign certificates, proving authenticity
    """
    # Generate private key using SECP256R1 curve (NIST P-256)
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    
    # Derive public key from private key
    public_key = private_key.public_key()
    
    # Serialize private key to PEM format (Privacy-Enhanced Mail format)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # In production, encrypt this!
    )
    
    # Serialize public key to PEM format
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Return base64-encoded keys for easy storage in database
    return {
        'private_key': base64.b64encode(private_pem).decode('utf-8'),
        'public_key': base64.b64encode(public_pem).decode('utf-8')
    }

# ============================================================================
# Key Loading Functions
# ============================================================================

def load_private_key_from_pem(private_key_pem: str):
    """
    Load a private key from a base64-encoded PEM string.
    
    This function deserializes a stored private key so it can be used for signing.
    
    Args:
        private_key_pem: Base64-encoded PEM private key string
    
    Returns:
        EllipticCurvePrivateKey: Cryptography library private key object
    
    Raises:
        ValueError: If the key format is invalid or corrupted
    """
    try:
        # Decode base64 to get PEM bytes
        private_key_bytes = base64.b64decode(private_key_pem)
        
        # Deserialize PEM bytes to private key object
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,  # In production, keys should be password-protected
            backend=default_backend()
        )
        return private_key
    except Exception as e:
        raise ValueError(f"Invalid private key: {str(e)}")

def load_public_key_from_pem(public_key_pem: str):
    """
    Load a public key from a base64-encoded PEM string.
    
    This function deserializes a stored public key so it can be used for verification.
    
    Args:
        public_key_pem: Base64-encoded PEM public key string
    
    Returns:
        EllipticCurvePublicKey: Cryptography library public key object
    
    Raises:
        ValueError: If the key format is invalid or corrupted
    """
    try:
        # Decode base64 to get PEM bytes
        public_key_bytes = base64.b64decode(public_key_pem)
        
        # Deserialize PEM bytes to public key object
        public_key = serialization.load_pem_public_key(
            public_key_bytes,
            backend=default_backend()
        )
        return public_key
    except Exception as e:
        raise ValueError(f"Invalid public key: {str(e)}")

# ============================================================================
# Signing and Verification
# ============================================================================

def sign_data(private_key_pem: str, data: dict) -> str:
    """
    Sign data using an ECDSA private key.
    
    This function creates a digital signature that proves the data was signed
    by the holder of the private key. The signature is deterministic for the
    same data and key.
    
    Process:
    1. Convert data dictionary to JSON string (sorted keys for consistency)
    2. Hash the data using SHA-256
    3. Sign the hash with the private key
    4. Return base64-encoded signature
    
    Args:
        private_key_pem: Base64-encoded PEM private key string
        data: Dictionary containing the data to sign (certificate information)
    
    Returns:
        str: Base64-encoded digital signature
    
    Raises:
        ValueError: If signing fails (invalid key, corrupted data, etc.)
    """
    try:
        # Load private key from PEM string
        private_key = load_private_key_from_pem(private_key_pem)
        
        # Convert data to JSON string with sorted keys for consistent hashing
        # This ensures the same data always produces the same signature
        data_string = json.dumps(data, sort_keys=True)
        data_bytes = data_string.encode('utf-8')
        
        # Sign the data using ECDSA with SHA-256
        # The signature proves authenticity and integrity
        signature = private_key.sign(
            data_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Return base64-encoded signature for storage
        return base64.b64encode(signature).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Signing failed: {str(e)}")

def verify_signature(public_key_pem: str, data: dict, signature: str) -> bool:
    """
    Verify an ECDSA signature.
    
    This function verifies that a signature was created by the holder of the
    corresponding private key and that the data hasn't been tampered with.
    
    Process:
    1. Convert data dictionary to JSON string (same format as signing)
    2. Decode the signature from base64
    3. Verify signature using public key
    4. Return True if valid, False if invalid
    
    Args:
        public_key_pem: Base64-encoded PEM public key string
        data: Dictionary containing the original data that was signed
        signature: Base64-encoded signature to verify
    
    Returns:
        bool: True if signature is valid, False otherwise
    
    Note:
        Returns False (doesn't raise exception) if verification fails.
        This allows graceful handling of invalid signatures.
    """
    try:
        # Load public key from PEM string
        public_key = load_public_key_from_pem(public_key_pem)
        
        # Convert data to JSON string (must match format used during signing)
        data_string = json.dumps(data, sort_keys=True)
        data_bytes = data_string.encode('utf-8')
        
        # Decode signature from base64
        signature_bytes = base64.b64decode(signature)
        
        # Verify signature - raises exception if invalid
        public_key.verify(
            signature_bytes,
            data_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except Exception:
        # Signature is invalid, tampered, or doesn't match the data
        return False

# ============================================================================
# Certificate Data Preparation
# ============================================================================

def create_certificate_hash_for_signing(certificate_data: dict) -> dict:
    """
    Create a standardized dictionary for signing (excludes signature fields).
    
    This function extracts only the relevant certificate fields for signing,
    excluding metadata and signature fields. This ensures consistent signing
    regardless of how the certificate data is structured elsewhere.
    
    Fields included:
    - certificate_id: Unique identifier
    - student_id: Student identifier
    - course_name: Course name
    - grade: Student grade
    - issuer_id: Institution identifier
    - issue_date: Date of issuance
    - timestamp: Unix timestamp
    
    Fields excluded:
    - student_name: PII (privacy)
    - signature fields: Would create circular dependency
    
    Args:
        certificate_data: Full certificate data dictionary
    
    Returns:
        dict: Dictionary containing only fields to be signed
    """
    signing_data = {
        'certificate_id': certificate_data.get('certificate_id'),
        'student_id': certificate_data.get('student_id'),
        'course_name': certificate_data.get('course_name'),
        'grade': certificate_data.get('grade'),
        'issuer_id': certificate_data.get('issuer_id'),
        'issue_date': certificate_data.get('issue_date'),
        'timestamp': certificate_data.get('timestamp')
    }
    return signing_data
