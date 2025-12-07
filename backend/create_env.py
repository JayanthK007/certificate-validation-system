"""
Script to create .env file for the backend.
Run this to set up your environment configuration.
"""

import os
import secrets

def create_env_file():
    """Create .env file with default configuration."""
    
    env_content = """# ============================================================================
# Certificate Validation System - Environment Variables
# ============================================================================

# ============================================================================
# Database Configuration
# ============================================================================
DATABASE_URL=sqlite:///./certificates.db

# ============================================================================
# JWT Secret Key (auto-generated)
# ============================================================================
SECRET_KEY={secret_key}

# ============================================================================
# Ethereum Configuration
# ============================================================================
# Ethereum Network (hardhat, sepolia, goerli, mumbai, mainnet)
ETHEREUM_NETWORK=hardhat

# Contract address (set after deploying smart contract)
# Deploy contract: cd contracts && npx hardhat run scripts/deploy.js --network hardhat
CONTRACT_ADDRESS=

# Private key for signing transactions (NEVER commit this to Git!)
# For Hardhat testing, use Account #0 private key from Hardhat node output
# Format: 0x... (64 hex characters)
# Run 'npx hardhat node' to see available test accounts
ETHEREUM_PRIVATE_KEY=

# ============================================================================
# Optional: Custom RPC URLs (uses public RPCs by default if not set)
# ============================================================================
# HARDHAT_RPC_URL=http://127.0.0.1:8545
# SEPOLIA_RPC_URL=https://rpc.sepolia.org
# GOERLI_RPC_URL=https://rpc.ankr.com/eth_goerli
# MUMBAI_RPC_URL=https://rpc.ankr.com/polygon_mumbai
# MAINNET_RPC_URL=https://eth.llamarpc.com

# ============================================================================
# Optional: Infura/Alchemy API keys (for better reliability)
# ============================================================================
# INFURA_API_KEY=your_infura_key
# ALCHEMY_API_KEY=your_alchemy_key
""".format(secret_key=secrets.token_urlsafe(32))
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled. .env file not modified.")
            return
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print(f"📍 Location: {env_path}")
    print("\n📝 Next steps:")
    print("1. Review .env file and update settings as needed")
    print("2. If using Ethereum, deploy contract and set CONTRACT_ADDRESS")
    print("3. Set ETHEREUM_PRIVATE_KEY if using Ethereum blockchain")

if __name__ == "__main__":
    create_env_file()

