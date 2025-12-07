"""
Ethereum Blockchain Service Module

This service integrates with Ethereum blockchain using Web3.py.
It replaces the custom blockchain service for Ethereum-based deployments.
"""

from web3 import Web3
from web3.exceptions import TransactionNotFound, BlockNotFound
from typing import Dict, Any, Optional, Tuple
import json
import os
from eth_account import Account
from eth_utils import to_hex, to_bytes


class EthereumService:
    """
    Service class for interacting with Ethereum blockchain.
    
    Handles:
    - Certificate issuance on Ethereum
    - Certificate verification on Ethereum
    - Contract interaction via Web3.py
    - Transaction management
    """
    
    def __init__(self, contract_address: str, private_key: Optional[str] = None):
        """
        Initialize Ethereum service.
        
        Args:
            contract_address: Address of deployed CertificateVerifier contract
            private_key: Private key for signing transactions (optional, for read-only operations)
        """
        network = os.getenv("ETHEREUM_NETWORK", "sepolia")
        rpc_url = self._get_rpc_url(network)
        
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum {network} network at {rpc_url}")
        
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.network = network
        
        self.contract_abi = self._load_contract_abi()
        
        try:
            code = self.web3.eth.get_code(self.contract_address)
            if code == b'' or code == '0x' or code == '0x0':
                raise ValueError(f"Contract at address {self.contract_address} has no code. Contract may not be deployed or address is incorrect.")
        except Exception as e:
            raise ValueError(f"Failed to verify contract deployment at {self.contract_address}: {str(e)}")
        
        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        self.account = None
        if private_key:
            self.account = Account.from_key(private_key)
            self.sender_address = self.account.address
    
    def _get_rpc_url(self, network: str) -> str:
        """Get RPC URL for specified network."""
        rpc_urls = {
            "mainnet": os.getenv("MAINNET_RPC_URL", "https://eth.llamarpc.com"),
            "sepolia": os.getenv("SEPOLIA_RPC_URL", "https://rpc.sepolia.org"),
            "goerli": os.getenv("GOERLI_RPC_URL", "https://rpc.ankr.com/eth_goerli"),
            "mumbai": os.getenv("MUMBAI_RPC_URL", "https://rpc.ankr.com/polygon_mumbai"),
            "hardhat": os.getenv("HARDHAT_RPC_URL", "http://127.0.0.1:8545"),
        }
        return rpc_urls.get(network.lower(), rpc_urls["sepolia"])
    
    def _load_contract_abi(self) -> list:
        """Load contract ABI from artifacts."""
        abi_paths = [
            os.path.join(os.path.dirname(__file__), "../../../contracts/artifacts/CertificateVerifier.sol/CertificateVerifier.json"),
            os.path.join(os.path.dirname(__file__), "../artifacts/CertificateVerifier.json"),
        ]
        
        for abi_path in abi_paths:
            if os.path.exists(abi_path):
                with open(abi_path, "r") as f:
                    artifact = json.load(f)
                    return artifact.get("abi", [])
        
        return [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "certificateId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "piiHash", "type": "bytes32"},
                    {"internalType": "string", "name": "courseName", "type": "string"},
                    {"internalType": "string", "name": "issuerId", "type": "string"}
                ],
                "name": "issueCertificate",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "certificateId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "piiHash", "type": "bytes32"}
                ],
                "name": "verifyCertificate",
                "outputs": [
                    {"internalType": "bool", "name": "valid", "type": "bool"},
                    {"internalType": "address", "name": "issuer", "type": "address"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "bool", "name": "revoked", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "certificateId", "type": "bytes32"},
                    {"internalType": "string", "name": "reason", "type": "string"}
                ],
                "name": "revokeCertificate",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "", "type": "bytes32"}
                ],
                "name": "certificates",
                "outputs": [
                    {"internalType": "bytes32", "name": "certificateId", "type": "bytes32"},
                    {"internalType": "bytes32", "name": "piiHash", "type": "bytes32"},
                    {"internalType": "address", "name": "issuer", "type": "address"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "bool", "name": "revoked", "type": "bool"},
                    {"internalType": "string", "name": "courseName", "type": "string"},
                    {"internalType": "string", "name": "issuerId", "type": "string"},
                    {"internalType": "string", "name": "revocationReason", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "certificateId", "type": "bytes32"}
                ],
                "name": "certificateExists",
                "outputs": [
                    {"internalType": "bool", "name": "", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def bytes32_hash(self, data: str) -> bytes:
        """Convert string to bytes32."""
        if data.startswith('0x'):
            data = data[2:]
        
        if len(data) == 64 and all(c in '0123456789abcdefABCDEF' for c in data):
            return bytes.fromhex(data)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        hash_bytes = Web3.keccak(data)
        return hash_bytes[:32]
    
    def issue_certificate(
        self,
        certificate_id: str,
        pii_hash: str,
        course_name: str,
        issuer_id: str
    ) -> Dict[str, Any]:
        """
        Issue a certificate on Ethereum blockchain.
        
        Args:
            certificate_id: Unique certificate identifier
            pii_hash: SHA-256 hash of PII (student name, ID, grade)
            course_name: Name of the course
            issuer_id: Institution identifier
            
        Returns:
            dict: Transaction receipt and details
        """
        if not self.account:
            raise ValueError("Private key required for issuing certificates")
        
        cert_id_bytes32 = self.bytes32_hash(certificate_id)
        pii_hash_bytes32 = self.bytes32_hash(pii_hash)
        
        function = self.contract.functions.issueCertificate(
            cert_id_bytes32,
            pii_hash_bytes32,
            course_name,
            issuer_id
        )
        
        gas_estimate = function.estimate_gas({'from': self.sender_address})
        
        transaction = function.build_transaction({
            'from': self.sender_address,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.sender_address),
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status != 1:
            return {
                'success': False,
                'transaction_hash': receipt.transactionHash.hex(),
                'block_number': receipt.blockNumber,
                'gas_used': receipt.gasUsed,
                'contract_address': self.contract_address,
                'network': self.network,
                'error': f'Transaction failed with status {receipt.status}. The sender address ({self.sender_address}) may not be authorized as an issuer. Make sure the private key corresponds to the contract owner or an authorized issuer.',
                'sender_address': self.sender_address
            }
        
        return {
            'success': True,
            'transaction_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed,
            'contract_address': self.contract_address,
            'network': self.network
        }
    
    def verify_certificate_without_pii(self, certificate_id: str) -> Dict[str, Any]:
        """
        Verify a certificate on Ethereum blockchain without requiring PII hash.
        Retrieves PII hash from blockchain first.
        
        Args:
            certificate_id: Unique certificate identifier
            
        Returns:
            dict: Verification result with 'found' field indicating if certificate exists
        """
        try:
            cert_id_bytes32 = self.bytes32_hash(certificate_id)
            exists = self.contract.functions.certificateExists(cert_id_bytes32).call()
            
            if not exists:
                return {
                    'found': False,
                    'valid': False,
                    'certificate_id': certificate_id,
                    'blockchain': 'ethereum',
                    'network': self.network,
                    'contract_address': self.contract_address,
                    'error': 'Certificate does not exist on Ethereum blockchain.',
                }
            
            cert_data = self.contract.functions.certificates(cert_id_bytes32).call()
            
            pii_hash_bytes32 = cert_data[1] if isinstance(cert_data, (list, tuple)) else cert_data.piiHash
            
            if isinstance(pii_hash_bytes32, bytes):
                pii_hash = pii_hash_bytes32.hex()
            else:
                pii_hash = pii_hash_bytes32.hex() if hasattr(pii_hash_bytes32, 'hex') else str(pii_hash_bytes32)
            
            if pii_hash.startswith('0x'):
                pii_hash = pii_hash[2:]
            if len(pii_hash) > 64:
                pii_hash = pii_hash[:64]
            elif len(pii_hash) < 64:
                pii_hash = pii_hash.zfill(64)
            
            return self.verify_certificate(certificate_id, pii_hash)
        except Exception as e:
            error_msg = str(e)
            if 'contract' in error_msg.lower() or 'deployed' in error_msg.lower() or 'synced' in error_msg.lower() or 'connection' in error_msg.lower():
                return {
                    'found': False,
                    'valid': False,
                    'certificate_id': certificate_id,
                    'blockchain': 'ethereum',
                    'network': self.network,
                    'contract_address': self.contract_address,
                    'error': f'Failed to connect to Ethereum contract. Make sure Hardhat node is running and contract is deployed. Error: {error_msg}',
                    'debug': {
                        'certificate_id': certificate_id,
                        'exception': error_msg,
                        'rpc_url': self._get_rpc_url(self.network),
                        'contract_address': self.contract_address
                    }
                }
            else:
                raise
    
    def verify_certificate(
        self,
        certificate_id: str,
        pii_hash: str
    ) -> Dict[str, Any]:
        """
        Verify a certificate on Ethereum blockchain.
        
        Args:
            certificate_id: Unique certificate identifier
            pii_hash: SHA-256 hash of PII to verify against
            
        Returns:
            dict: Verification result with 'found' field indicating if certificate exists
        """
        cert_id_bytes32 = self.bytes32_hash(certificate_id)
        pii_hash_bytes32 = self.bytes32_hash(pii_hash)
        
        try:
            exists = self.contract.functions.certificateExists(cert_id_bytes32).call()
            
            if not exists:
                return {
                    'found': False,
                    'valid': False,
                    'certificate_id': certificate_id,
                    'blockchain': 'ethereum',
                    'network': self.network,
                    'contract_address': self.contract_address,
                    'error': 'Certificate does not exist on Ethereum blockchain. It may have been issued on the custom blockchain before switching to Ethereum. Please re-issue the certificate on Ethereum.',
                    'debug': {
                        'certificate_id': certificate_id,
                        'cert_id_bytes32_hex': cert_id_bytes32.hex()
                    }
                }
            
            cert_data = self.contract.functions.certificates(cert_id_bytes32).call()
            
            issuer = cert_data[2] if isinstance(cert_data, (list, tuple)) else cert_data.issuer
            
            if isinstance(issuer, bytes):
                issuer_str = issuer.hex() if hasattr(issuer, 'hex') else str(issuer)
            else:
                issuer_str = str(issuer).lower()
            
            if issuer_str.startswith('0x'):
                issuer_str = issuer_str.lower()
            else:
                issuer_str = '0x' + issuer_str.lower()
            
            result = self.contract.functions.verifyCertificate(
                cert_id_bytes32,
                pii_hash_bytes32
            ).call()
            
            valid, issuer_from_verify, timestamp, revoked = result
            
            if isinstance(issuer_from_verify, bytes):
                issuer_str = issuer_from_verify.hex()
            else:
                issuer_str = str(issuer_from_verify).lower()
            
            if issuer_str.startswith('0x'):
                issuer_str = issuer_str.lower()
            else:
                issuer_str = '0x' + issuer_str.lower()
        except Exception as e:
            error_msg = str(e)
            if 'contract' in error_msg.lower() or 'deployed' in error_msg.lower() or 'synced' in error_msg.lower():
                return {
                    'found': False,
                    'valid': False,
                    'certificate_id': certificate_id,
                    'blockchain': 'ethereum',
                    'network': self.network,
                    'contract_address': self.contract_address,
                    'error': 'Failed to connect to Ethereum contract. Make sure Hardhat node is running and contract is deployed.',
                    'debug': {
                        'certificate_id': certificate_id,
                        'exception': error_msg
                    }
                }
            else:
                return {
                    'found': False,
                    'valid': False,
                    'certificate_id': certificate_id,
                    'blockchain': 'ethereum',
                    'network': self.network,
                    'contract_address': self.contract_address,
                    'error': 'Certificate does not exist on Ethereum blockchain. It may have been issued on the custom blockchain before switching to Ethereum.',
                    'debug': {
                        'certificate_id': certificate_id,
                        'cert_id_bytes32_hex': cert_id_bytes32.hex(),
                        'exception': error_msg
                    }
                }
        
        return {
            'found': True,
            'valid': valid,  # Valid if verification passed
            'issuer': issuer_str,
            'timestamp': timestamp,
            'revoked': revoked,
            'certificate_id': certificate_id,
            'blockchain': 'ethereum',
            'network': self.network,
            'contract_address': self.contract_address
        }
    
    def revoke_certificate(
        self,
        certificate_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Revoke a certificate on Ethereum blockchain.
        
        Args:
            certificate_id: Unique certificate identifier
            reason: Reason for revocation
            
        Returns:
            dict: Transaction receipt and details
        """
        if not self.account:
            raise ValueError("Private key required for revoking certificates")
        
        cert_id_bytes32 = self.bytes32_hash(certificate_id)
        
        function = self.contract.functions.revokeCertificate(
            cert_id_bytes32,
            reason
        )
        
        gas_estimate = function.estimate_gas({'from': self.sender_address})
        
        transaction = function.build_transaction({
            'from': self.sender_address,
            'gas': int(gas_estimate * 1.2),
            'gasPrice': self.web3.eth.gas_price,
            'nonce': self.web3.eth.get_transaction_count(self.sender_address),
        })
        
        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.account.key)
        
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'success': receipt.status == 1,
            'transaction_hash': receipt.transactionHash.hex(),
            'block_number': receipt.blockNumber,
            'gas_used': receipt.gasUsed,
            'contract_address': self.contract_address,
            'network': self.network
        }
    
    def get_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """
        Get certificate information from Ethereum.
        
        Args:
            certificate_id: Unique certificate identifier
            
        Returns:
            dict: Certificate information
        """
        cert_id_bytes32 = self.bytes32_hash(certificate_id)
        
        try:
            exists = self.contract.functions.certificateExists(cert_id_bytes32).call()
            if not exists:
                return {
                    'exists': False,
                    'found': False,
                    'error': 'Certificate does not exist on Ethereum blockchain'
                }
            
            cert_data = self.contract.functions.certificates(cert_id_bytes32).call()
            
            return {
                'exists': True,
                'found': True,
                'certificate_id': certificate_id,
                'pii_hash': cert_data[1].hex() if hasattr(cert_data[1], 'hex') else str(cert_data[1]),
                'issuer': cert_data[2],
                'timestamp': cert_data[3],
                'revoked': cert_data[4],
                'course_name': cert_data[5],
                'issuer_id': cert_data[6],
                'revocation_reason': cert_data[7] if cert_data[4] else None,
                'blockchain': 'ethereum',
                'network': self.network,
                'contract_address': self.contract_address
            }
        except Exception as e:
            return {
                'exists': False,
                'found': False,
                'error': str(e)
            }
    
    def is_connected(self) -> bool:
        """Check if connected to Ethereum network."""
        return self.web3.is_connected()
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information."""
        try:
            chain_id = self.web3.eth.chain_id
            block_number = self.web3.eth.block_number
            gas_price = self.web3.eth.gas_price
            
            return {
                'network': self.network,
                'chain_id': chain_id,
                'block_number': block_number,
                'gas_price': gas_price,
                'contract_address': self.contract_address,
                'connected': True
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

