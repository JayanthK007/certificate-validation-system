import hashlib
import json
import time
from typing import List, Dict, Any

class Block:
    """Block class for storing certificates in the blockchain"""
    
    def __init__(self, index: int, certificates: List[Dict], previous_hash: str, timestamp: float = None):
        self.index = index
        self.certificates = certificates
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'certificates': self.certificates,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for serialization"""
        return {
            'index': self.index,
            'certificates': self.certificates,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'hash': self.hash
        }
    
    def __str__(self) -> str:
        return f"Block {self.index}: {self.hash[:10]}..."
