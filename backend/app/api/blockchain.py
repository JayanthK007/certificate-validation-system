from fastapi import APIRouter, HTTPException
from ..models.blockchain import blockchain

router = APIRouter(prefix="/blockchain", tags=["blockchain"])

@router.get("/info")
async def get_blockchain_info():
    """Get blockchain statistics and information"""
    try:
        info = blockchain.get_blockchain_info()
        return {
            "success": True,
            "blockchain_info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/validate")
async def validate_blockchain():
    """Validate the integrity of the blockchain"""
    try:
        is_valid = blockchain.validate_chain()
        return {
            "success": True,
            "valid": is_valid,
            "message": "Blockchain is valid" if is_valid else "Blockchain integrity compromised"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/blocks")
async def get_all_blocks():
    """Get all blocks in the blockchain (for demo purposes)"""
    try:
        blocks = [block.to_dict() for block in blockchain.chain]
        return {
            "success": True,
            "blocks": blocks,
            "count": len(blocks)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/latest-block")
async def get_latest_block():
    """Get the latest block in the blockchain"""
    try:
        latest_block = blockchain.get_latest_block()
        return {
            "success": True,
            "block": latest_block.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
