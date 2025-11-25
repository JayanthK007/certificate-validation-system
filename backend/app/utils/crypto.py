import hashlib
import secrets
import string
from typing import str

def generate_secure_id(length: int = 16) -> str:
    """Generate a secure random ID"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_data(data: str) -> str:
    """Create SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()

def verify_hash(data: str, hash_value: str) -> bool:
    """Verify if data matches the hash"""
    return hash_data(data) == hash_value

def create_certificate_hash(certificate_data: dict) -> str:
    """Create a hash for certificate data"""
    # Sort keys to ensure consistent hashing
    sorted_data = sorted(certificate_data.items())
    data_string = str(sorted_data)
    return hash_data(data_string)
