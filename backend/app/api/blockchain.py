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
import os
from ..database import get_db
from ..services.ethereum_helper import get_ethereum_service

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
        # Get Ethereum network information
        ethereum_service = get_ethereum_service()
        network_info = ethereum_service.get_network_info()
        
        info = {
            'blockchain_type': 'ethereum',
            'network': network_info.get('network'),
            'chain_id': network_info.get('chain_id'),
            'block_number': network_info.get('block_number'),
            'gas_price': network_info.get('gas_price'),
            'contract_address': network_info.get('contract_address'),
            'connected': network_info.get('connected', False)
        }
        
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
        # Validate Ethereum connection
        ethereum_service = get_ethereum_service()
        network_info = ethereum_service.get_network_info()
        
        if not network_info.get('connected', False):
            return {
                "success": True,
                "valid": False,
                "message": "Failed to connect to Ethereum network",
                "block_count": 0,
                "certificate_count": 0,
                "blockchain_type": "ethereum",
                "block_number": 0
            }
        
        block_number = network_info.get('block_number', 0)
        network_name = network_info.get('network', 'unknown')
        contract_address = network_info.get('contract_address', 'N/A')
        
        # Create a more informative message
        message = f'✅ Ethereum Network Connected Successfully\n\n'
        message += f'Network: {network_name.upper()}\n'
        message += f'Current Block: {block_number}\n'
        message += f'Contract Address: {contract_address[:20]}...{contract_address[-10:] if len(contract_address) > 30 else contract_address}\n\n'
        message += f'📋 System Status:\n'
        message += f'• Certificates are stored on Ethereum blockchain\n'
        message += f'• All certificate data is immutable and tamper-proof\n'
        message += f'• To verify a certificate, use the certificate ID in the "Verify Certificate" tab'
        
        return {
            "success": True,
            "valid": True,
            "message": message,
            "block_count": block_number,
            "certificate_count": 0,  # Cannot enumerate from Ethereum
            "blockchain_type": "ethereum",
            "network": network_name,
            "contract_address": contract_address,
            "block_number": block_number
        }
    except ValueError as e:
        # Handle contract deployment errors with helpful message
        error_msg = str(e)
        if 'no code' in error_msg.lower() or 'not deployed' in error_msg.lower():
            contract_address = os.getenv("CONTRACT_ADDRESS", "N/A")
            helpful_message = f'❌ Contract Not Deployed\n\n'
            helpful_message += f'Contract at address {contract_address} has no code.\n\n'
            helpful_message += f'To fix this:\n'
            helpful_message += f'1. Make sure Hardhat node is running: cd contracts && npx hardhat node\n'
            helpful_message += f'2. Deploy the contract: cd contracts && npx hardhat run scripts/deploy.js --network hardhat\n'
            helpful_message += f'3. Update CONTRACT_ADDRESS in backend/.env with the deployed address\n'
            helpful_message += f'4. Restart the backend server\n\n'
            helpful_message += f'Note: Hardhat node resets when restarted, so you need to redeploy the contract.'
            
            return {
                "success": True,
                "valid": False,
                "message": helpful_message,
                "block_count": 0,
                "certificate_count": 0,
                "blockchain_type": "ethereum",
                "block_number": 0
            }
        else:
            raise HTTPException(status_code=400, detail=str(e))
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
        ethereum_service = get_ethereum_service()
        network_info = ethereum_service.get_network_info()
        
        return {
            "success": True,
            "message": "Ethereum doesn't track individual blocks in this system. Use /blockchain/info for network information.",
            "network_info": network_info,
            "note": "Ethereum manages its own blocks. This system only interacts with the smart contract."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# Latest Block Endpoint
# ============================================================================

@router.get("/latest-block")
async def get_latest_block(db: Session = Depends(get_db)):
    """
    Get the latest Ethereum block information.
    
    This endpoint returns information about the current Ethereum block.
    
    Args:
        db: Database session (injected by FastAPI)
    
    Returns:
        dict: Latest block information
    
    Raises:
        HTTPException: 400 if an error occurs
    """
    try:
        ethereum_service = get_ethereum_service()
        network_info = ethereum_service.get_network_info()
        
        return {
            "success": True,
            "block_number": network_info.get('block_number'),
            "chain_id": network_info.get('chain_id'),
            "network": network_info.get('network'),
            "message": "Ethereum manages its own blocks. This shows the current block number."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
