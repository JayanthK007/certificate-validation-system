"""
Cryptographic Utility Functions Module

This module provides general-purpose cryptographic utilities used throughout
the application. These are simple helper functions for hashing and ID generation.

Note: This module contains basic utilities. For ECDSA signing, see ecdsa_utils.py
For Merkle tree hashing, see merkle_tree.py
"""

import hashlib
import secrets
import string

# ============================================================================
# Secure ID Generation
# ============================================================================

def generate_secure_id(length: int = 16) -> str:
    """
    Generate a cryptographically secure random ID.
    
    Uses Python's secrets module which is designed for cryptographic purposes.
    Suitable for generating session IDs, nonces, or other security-sensitive identifiers.
    
    Args:
        length: Length of the ID to generate (default: 16)
    
    Returns:
        str: Random alphanumeric string of specified length
    
    Security:
        Uses secrets.choice() which is cryptographically secure (not predictable)
        Suitable for security-sensitive applications
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ============================================================================
# Hash Functions
# ============================================================================

def hash_data(data: str) -> str:
    """
    Create SHA-256 hash of data.
    
    This is a simple wrapper for SHA-256 hashing. Used for creating
    deterministic hashes of data for integrity verification.
    
    Args:
        data: String data to hash
    
    Returns:
        str: Hexadecimal SHA-256 hash (64 characters)
    
    Note:
        Same input always produces same output (deterministic)
        Small changes in input produce completely different output
    """
    return hashlib.sha256(data.encode()).hexdigest()

def verify_hash(data: str, hash_value: str) -> bool:
    """
    Verify if data matches a given hash.
    
    This function hashes the provided data and compares it with the expected hash.
    Used for password verification, data integrity checks, etc.
    
    Args:
        data: Original data to verify
        hash_value: Expected hash to compare against
    
    Returns:
        bool: True if data hash matches expected hash, False otherwise
    """
    return hash_data(data) == hash_value

# ============================================================================
# Certificate Hash Generation
# ============================================================================

def create_certificate_hash(certificate_data: dict) -> str:
    """
    Create a hash for certificate data.
    
    This function creates a deterministic hash of certificate data by:
    1. Sorting dictionary items by key (ensures consistent ordering)
    2. Converting to string representation
    3. Hashing with SHA-256
    
    Args:
        certificate_data: Dictionary containing certificate information
    
    Returns:
        str: SHA-256 hash of the certificate data
    
    Note:
        Keys are sorted to ensure same data always produces same hash
        regardless of dictionary insertion order
    """
    # Sort keys to ensure consistent hashing
    sorted_data = sorted(certificate_data.items())
    data_string = str(sorted_data)
    return hash_data(data_string)
