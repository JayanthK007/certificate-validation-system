"""
Helper module to get EthereumService instance.
Provides a single point of configuration for Ethereum service.
"""

import os
from .ethereum_service import EthereumService

def get_ethereum_service(require_private_key: bool = False) -> EthereumService:
    """
    Get EthereumService instance with configuration from environment variables.
    
    Args:
        require_private_key: If True, raises error if private key is not set.
                           If False, allows read-only operations without private key.
    
    Returns:
        EthereumService: Configured Ethereum service instance
        
    Raises:
        ValueError: If required environment variables are not set
    """
    contract_address = os.getenv("CONTRACT_ADDRESS")
    private_key = os.getenv("ETHEREUM_PRIVATE_KEY")
    
    if not contract_address:
        raise ValueError("CONTRACT_ADDRESS environment variable is required")
    
    if require_private_key and not private_key:
        raise ValueError("ETHEREUM_PRIVATE_KEY environment variable is required for write operations")
    
    return EthereumService(contract_address, private_key)

