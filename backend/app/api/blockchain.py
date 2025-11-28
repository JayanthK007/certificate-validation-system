"""
Blockchain Information API Endpoints Module

This module provides REST API endpoints for querying blockchain information:
- Blockchain statistics and metrics
- Blockchain integrity validation
- Block information retrieval
- Latest block information

All endpoints are public (no authentication required) as they only provide
read-only information about the blockchain state.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.blockchain_service import BlockchainService

# ============================================================================
# API Router Setup
# ============================================================================

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

# ============================================================================
# Blockchain Information Endpoint
# ============================================================================

@router.get("/info")
async def get_blockchain_info(db: Session = Depends(get_db)):
    """
    Get blockchain statistics and information.
    
    This endpoint provides comprehensive statistics about the blockchain:
    - Total number of blocks
    - Total number of certificates
    - Active vs revoked certificates
    - Latest block information
    
    This is a public endpoint (no authentication required) as it only
    provides read-only information.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Blockchain statistics and information
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        # Create blockchain service instance
        blockchain_service = BlockchainService(db)
        
        # Get blockchain statistics
        info = blockchain_service.get_blockchain_info()
        
        return {
            "success": True,
            "blockchain_info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Blockchain Validation Endpoint
# ============================================================================

@router.get("/validate")
async def validate_blockchain(db: Session = Depends(get_db)):
    """
    Validate the integrity of the blockchain.
    
    This endpoint performs a comprehensive validation of the entire blockchain:
    - Verifies genesis block is correct
    - Checks each block's hash is valid
    - Verifies block linking (each block points to previous)
    - Ensures chain continuity
    
    This is a public endpoint (no authentication required) as validation
    is a read-only operation.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Validation result with:
            - success: Boolean indicating operation success
            - valid: Boolean indicating if blockchain is valid
            - message: Human-readable validation message
    
    Raises:
        HTTPException: 400 if an error occurs during validation
    """
    try:
        # Create blockchain service instance
        blockchain_service = BlockchainService(db)
        
        # Validate blockchain integrity (now returns dict with details)
        validation_result = blockchain_service.validate_chain()
        
        return {
            "success": True,
            "valid": validation_result['valid'],
            "message": validation_result['message'],
            "block_count": validation_result.get('block_count', 0),
            "certificate_count": validation_result.get('certificate_count', 0)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# All Blocks Endpoint
# ============================================================================

@router.get("/blocks")
async def get_all_blocks(db: Session = Depends(get_db)):
    """
    Get all blocks in the blockchain.
    
    This endpoint returns information about all blocks in the blockchain.
    Useful for debugging, auditing, or displaying blockchain structure.
    
    Note: This is a demo/development endpoint. In production, you might
    want to paginate results for large blockchains.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: All blocks with:
            - success: Boolean indicating operation success
            - blocks: List of block dictionaries
            - count: Number of blocks
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        # Import Block model
        from ..models.db_models import Block
        
        # Query all blocks ordered by index
        blocks = db.query(Block).order_by(Block.index).all()
        
        # Convert to dictionary format for JSON response
        blocks_data = [{
            'index': block.index,
            'previous_hash': block.previous_hash,
            'merkle_root': block.merkle_root,
            'hash': block.hash,
            'timestamp': block.timestamp
        } for block in blocks]
        
        return {
            "success": True,
            "blocks": blocks_data,
            "count": len(blocks_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Latest Block Endpoint
# ============================================================================

@router.get("/latest-block")
async def get_latest_block(db: Session = Depends(get_db)):
    """
    Get the latest block in the blockchain.
    
    This endpoint returns information about the most recent block added
    to the blockchain. Useful for monitoring blockchain growth.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Latest block information with:
            - success: Boolean indicating operation success
            - block: Block dictionary (or None if no blocks exist)
            - message: Informational message (if no blocks)
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        # Create blockchain service instance
        blockchain_service = BlockchainService(db)
        
        # Get latest block
        latest_block = blockchain_service.get_latest_block()
        
        if latest_block:
            # Return block information
            return {
                "success": True,
                "block": {
                    'index': latest_block.index,
                    'previous_hash': latest_block.previous_hash,
                    'merkle_root': latest_block.merkle_root,
                    'hash': latest_block.hash,
                    'timestamp': latest_block.timestamp
                }
            }
        else:
            # No blocks exist yet
            return {
                "success": True,
                "block": None,
                "message": "No blocks in blockchain"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
