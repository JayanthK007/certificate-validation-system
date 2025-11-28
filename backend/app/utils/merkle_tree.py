"""
Merkle Tree Implementation Module

This module implements Merkle trees for efficient certificate verification in the blockchain.
Merkle trees allow verification of a single certificate without processing the entire block,
making verification faster and more scalable.

How Merkle Trees Work:
1. Each certificate hash is a leaf node
2. Parent nodes are hashes of their children
3. Root hash represents all certificates in the block
4. Merkle proof provides minimal data needed to verify a certificate

Benefits:
- Fast verification: O(log n) instead of O(n)
- Efficient storage: Only need root hash in block header
- Scalability: Works with any number of certificates per block
"""

import hashlib
from typing import List

# ============================================================================
# Hash Function
# ============================================================================

def hash_data(data: str) -> str:
    """
    Create SHA-256 hash of data.
    
    This is a simple wrapper around SHA-256 hashing used throughout
    the Merkle tree implementation.
    
    Args:
        data: String data to hash
    
    Returns:
        str: Hexadecimal hash string (64 characters)
    """
    return hashlib.sha256(data.encode()).hexdigest()

# ============================================================================
# Merkle Tree Construction
# ============================================================================

def build_merkle_tree(hashes: List[str]) -> str:
    """
    Build a Merkle tree from a list of hashes and return the root hash.
    
    This function recursively builds a binary Merkle tree:
    1. If empty list, return empty string
    2. If single hash, return it as root
    3. If odd number, duplicate last hash to make even
    4. Pair adjacent hashes and hash them together
    5. Recursively process until one root hash remains
    
    Example:
        Input: [hash1, hash2, hash3, hash4]
        Level 1: hash(hash1+hash2), hash(hash3+hash4)
        Level 2: hash(hash(hash1+hash2) + hash(hash3+hash4))
        Root: Final hash
    
    Args:
        hashes: List of hash strings (leaf nodes)
    
    Returns:
        str: Root hash of the Merkle tree (empty string if input is empty)
    """
    # Base case: empty list
    if not hashes:
        return ""
    
    # Base case: single hash is the root
    if len(hashes) == 1:
        return hashes[0]
    
    # If odd number of hashes, duplicate the last one
    # This ensures we can always pair them up
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])
    
    # Build next level by pairing adjacent hashes
    next_level = []
    for i in range(0, len(hashes), 2):
        # Combine two hashes and hash the result
        combined = hashes[i] + hashes[i + 1]
        next_level.append(hash_data(combined))
    
    # Recursively build tree until we have a single root
    return build_merkle_tree(next_level)

# ============================================================================
# Merkle Proof Generation
# ============================================================================

def get_merkle_proof(hashes: List[str], target_hash: str) -> List[dict]:
    """
    Generate a Merkle proof for a specific hash.
    
    A Merkle proof is a minimal set of hashes needed to verify that a target
    hash is part of the Merkle tree. It consists of sibling hashes at each level.
    
    Process:
    1. Find target hash in the list
    2. At each level, identify the sibling hash
    3. Record sibling hash and its position (left/right)
    4. Move up the tree until reaching root
    
    Args:
        hashes: List of all hashes in the block (leaf nodes)
        target_hash: The specific hash to generate proof for
    
    Returns:
        List[dict]: List of proof steps, each containing:
            - 'hash': Sibling hash at this level
            - 'position': "left" or "right" (where sibling is relative to target)
    
    Note:
        Returns empty list if target_hash is not in the list
    """
    # Check if target exists
    if target_hash not in hashes:
        return []
    
    # Base case: single hash needs no proof
    if len(hashes) == 1:
        return []
    
    proof = []
    current_level = hashes.copy()
    target_index = current_level.index(target_hash)
    
    # Build proof by traversing up the tree
    while len(current_level) > 1:
        # If odd number, duplicate last to make even
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])
        
        # Determine sibling based on target position
        # Even index (0, 2, 4...) -> sibling is right (index+1)
        # Odd index (1, 3, 5...) -> sibling is left (index-1)
        if target_index % 2 == 0:
            sibling_index = target_index + 1
            position = "right"
        else:
            sibling_index = target_index - 1
            position = "left"
        
        # Add sibling hash to proof
        sibling_hash = current_level[sibling_index]
        proof.append({"hash": sibling_hash, "position": position})
        
        # Build next level of tree
        next_level = []
        for i in range(0, len(current_level), 2):
            combined = current_level[i] + current_level[i + 1]
            next_level.append(hash_data(combined))
        
        # Move to next level
        current_level = next_level
        target_index = target_index // 2
    
    return proof

# ============================================================================
# Merkle Proof Verification
# ============================================================================

def verify_merkle_proof(target_hash: str, merkle_root: str, proof: List[dict]) -> bool:
    """
    Verify a Merkle proof.
    
    This function reconstructs the path from target hash to root using the proof.
    If the reconstructed root matches the provided root, the proof is valid.
    
    Process:
    1. Start with target hash
    2. For each proof step, combine with sibling hash (in correct order)
    3. Hash the combination to get parent hash
    4. Repeat until reaching root
    5. Compare computed root with provided root
    
    Args:
        target_hash: The hash being verified (leaf node)
        merkle_root: The expected root hash of the Merkle tree
        proof: List of proof steps from get_merkle_proof()
    
    Returns:
        bool: True if proof is valid (target is in tree), False otherwise
    
    Example:
        Target: hash1
        Proof: [{"hash": hash2, "position": "right"}, {"hash": hash34, "position": "left"}]
        Step 1: hash(hash1 + hash2) = hash12
        Step 2: hash(hash34 + hash12) = root
        Compare: root == merkle_root
    """
    current_hash = target_hash
    
    # Reconstruct path to root using proof
    for step in proof:
        # Combine with sibling hash in correct order
        # Position indicates where sibling is relative to current hash
        if step["position"] == "left":
            # Sibling is on left, so: hash(sibling + current)
            combined = step["hash"] + current_hash
        else:
            # Sibling is on right, so: hash(current + sibling)
            combined = current_hash + step["hash"]
        
        # Hash the combination to get parent hash
        current_hash = hash_data(combined)
    
    # If computed root matches provided root, proof is valid
    return current_hash == merkle_root
