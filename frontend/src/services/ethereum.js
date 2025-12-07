/**
 * Ethereum Service Layer
 * 
 * Direct interaction with Ethereum smart contracts using ethers.js
 * Provides both direct contract interaction and MetaMask integration
 */

import { ethers } from 'ethers'

// ============================================================================
// Contract ABI (Application Binary Interface)
// ============================================================================

const CERTIFICATE_VERIFIER_ABI = [
  "function issueCertificate(bytes32 certificateId, bytes32 piiHash, string memory courseName, string memory issuerId) public",
  "function verifyCertificate(bytes32 certificateId, bytes32 piiHash) public view returns (bool valid, address issuer, uint256 timestamp, bool revoked)",
  "function revokeCertificate(bytes32 certificateId, string memory reason) public",
  "function getCertificate(bytes32 certificateId) public view returns (bytes32 certificateId, bytes32 piiHash, address issuer, uint256 timestamp, bool revoked, string memory courseName, string memory issuerId, string memory revocationReason)",
  "function certificateExists(bytes32 certificateId) public view returns (bool)",
  "function isAuthorizedIssuer(address issuer) public view returns (bool)",
  "function certificates(bytes32) public view returns (bytes32 certificateId, bytes32 piiHash, address issuer, uint256 timestamp, bool revoked, string memory courseName, string memory issuerId, string memory revocationReason)",
  "event CertificateIssued(bytes32 indexed certificateId, bytes32 indexed piiHash, address indexed issuer, uint256 timestamp, string courseName, string issuerId)",
  "event CertificateRevoked(bytes32 indexed certificateId, address indexed issuer, uint256 timestamp, string reason)"
]

// ============================================================================
// Network Configuration
// ============================================================================

const NETWORKS = {
  sepolia: {
    chainId: '0xaa36a7', // 11155111
    chainName: 'Sepolia Test Network',
    nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
    rpcUrls: ['https://rpc.sepolia.org'],
    blockExplorerUrls: ['https://sepolia.etherscan.io']
  },
  goerli: {
    chainId: '0x5', // 5
    chainName: 'Goerli Test Network',
    nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
    rpcUrls: ['https://rpc.ankr.com/eth_goerli'],
    blockExplorerUrls: ['https://goerli.etherscan.io']
  },
  mumbai: {
    chainId: '0x13881', // 80001
    chainName: 'Polygon Mumbai',
    nativeCurrency: { name: 'MATIC', symbol: 'MATIC', decimals: 18 },
    rpcUrls: ['https://rpc.ankr.com/polygon_mumbai'],
    blockExplorerUrls: ['https://mumbai.polygonscan.com']
  },
  hardhat: {
    chainId: '0x539', // 1337
    chainName: 'Hardhat Local',
    nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
    rpcUrls: ['http://127.0.0.1:8545'],
    blockExplorerUrls: []
  }
}

// ============================================================================
// Ethereum Service Class
// ============================================================================

class EthereumService {
  constructor(contractAddress, networkName = 'sepolia') {
    this.contractAddress = contractAddress
    this.networkName = networkName
    this.provider = null
    this.signer = null
    this.contract = null
    this.connected = false
  }

  // ============================================================================
  // Connection Methods
  // ============================================================================

  /**
   * Check if MetaMask is installed
   */
  async isMetaMaskInstalled() {
    return typeof window.ethereum !== 'undefined'
  }

  /**
   * Connect to MetaMask wallet
   */
  async connectWallet() {
    try {
      if (!await this.isMetaMaskInstalled()) {
        throw new Error('MetaMask is not installed. Please install MetaMask extension.')
      }

      // Request account access
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' })
      
      if (accounts.length === 0) {
        throw new Error('No accounts found. Please unlock MetaMask.')
      }

      // Get provider and signer
      this.provider = new ethers.BrowserProvider(window.ethereum)
      this.signer = await this.provider.getSigner()
      
      // Get contract instance
      this.contract = new ethers.Contract(
        this.contractAddress,
        CERTIFICATE_VERIFIER_ABI,
        this.signer
      )

      // Check network
      await this.ensureCorrectNetwork()

      this.connected = true
      
      return {
        success: true,
        address: accounts[0],
        network: this.networkName
      }
    } catch (error) {
      console.error('Wallet connection error:', error)
      return {
        success: false,
        error: error.message
      }
    }
  }

  /**
   * Ensure user is on the correct network
   */
  async ensureCorrectNetwork() {
    if (this.networkName === 'hardhat') {
      // For local Hardhat, just check if it's localhost
      const network = await this.provider.getNetwork()
      if (network.chainId !== 1337n) {
        console.warn('Expected Hardhat network (chainId: 1337), but got:', network.chainId)
      }
      return
    }

    const targetNetwork = NETWORKS[this.networkName]
    if (!targetNetwork) {
      throw new Error(`Unknown network: ${this.networkName}`)
    }

    try {
      // Request network switch
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: targetNetwork.chainId }]
      })
    } catch (switchError) {
      // If network doesn't exist, add it
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [targetNetwork]
          })
        } catch (addError) {
          throw new Error(`Failed to add network: ${addError.message}`)
        }
      } else {
        throw switchError
      }
    }
  }

  /**
   * Get current account address
   */
  async getCurrentAccount() {
    if (!this.signer) {
      return null
    }
    try {
      return await this.signer.getAddress()
    } catch (error) {
      return null
    }
  }

  /**
   * Disconnect wallet
   */
  disconnect() {
    this.provider = null
    this.signer = null
    this.contract = null
    this.connected = false
  }

  // ============================================================================
  // Read-Only Contract Methods
  // ============================================================================

  /**
   * Create read-only contract instance (no signer needed)
   */
  getReadOnlyContract() {
    // If we already have a provider, use it
    if (this.provider) {
      return new ethers.Contract(
        this.contractAddress,
        CERTIFICATE_VERIFIER_ABI,
        this.provider
      )
    }

    // For Hardhat (local network), connect directly to localhost
    if (this.networkName === 'hardhat') {
      const hardhatProvider = new ethers.JsonRpcProvider('http://127.0.0.1:8545')
      return new ethers.Contract(
        this.contractAddress,
        CERTIFICATE_VERIFIER_ABI,
        hardhatProvider
      )
    }

    // Try to use window.ethereum (MetaMask) as fallback
    if (typeof window.ethereum !== 'undefined') {
      this.provider = new ethers.BrowserProvider(window.ethereum)
      return new ethers.Contract(
        this.contractAddress,
        CERTIFICATE_VERIFIER_ABI,
        this.provider
      )
    }

    throw new Error('No provider available. For Hardhat, make sure the Hardhat node is running on http://127.0.0.1:8545')
  }

  /**
   * Verify certificate (read-only, no transaction needed)
   */
  async verifyCertificate(certificateId, piiHash) {
    try {
      // Use read-only contract (doesn't require wallet connection)
      const contract = this.getReadOnlyContract()
      
      // Convert strings to bytes32
      const certIdBytes32 = this.stringToBytes32(certificateId)
      
      // First check if certificate exists
      const exists = await contract.certificateExists(certIdBytes32)
      if (!exists) {
        return {
          success: false,
          error: 'Certificate does not exist on blockchain'
        }
      }
      
      // Convert PII hash to bytes32
      const piiHashBytes32 = this.hexToBytes32(piiHash)

      // Verify certificate
      const result = await contract.verifyCertificate(certIdBytes32, piiHashBytes32)
      
      return {
        success: true,
        valid: result[0],
        issuer: result[1],
        timestamp: Number(result[2]),
        revoked: result[3]
      }
    } catch (error) {
      console.error('Verify certificate error:', error)
      const errorMessage = error.message || error.reason || String(error)
      
      // Check if it's a connection error
      if (errorMessage.includes('network') || 
          errorMessage.includes('connection') ||
          errorMessage.includes('ECONNREFUSED') ||
          errorMessage.includes('Failed to fetch')) {
        return {
          success: false,
          error: 'Failed to connect to Ethereum network. Make sure Hardhat node is running on http://127.0.0.1:8545'
        }
      }
      
      return {
        success: false,
        error: errorMessage || 'Verification failed'
      }
    }
  }

  /**
   * Get certificate information
   */
  async getCertificate(certificateId) {
    try {
      // Use read-only contract (doesn't require wallet connection)
      const contract = this.getReadOnlyContract()
      
      const certIdBytes32 = this.stringToBytes32(certificateId)
      
      // First check if certificate exists
      const exists = await contract.certificateExists(certIdBytes32)
      if (!exists) {
        return {
          success: false,
          error: 'Certificate does not exist on blockchain'
        }
      }
      
      // Certificate exists, get full data
      // Use the certificates mapping directly instead of getCertificate function
      // to avoid the require statement that throws
      const result = await contract.certificates(certIdBytes32)
      
      // Convert bytes32 piiHash to hex string if needed
      let piiHashHex = result[1]
      if (typeof piiHashHex === 'string' && piiHashHex.startsWith('0x')) {
        piiHashHex = piiHashHex.slice(2) // Remove 0x prefix
      } else if (typeof piiHashHex === 'object' && piiHashHex.hex) {
        piiHashHex = piiHashHex.hex.slice(2) // Remove 0x prefix
      } else if (typeof piiHashHex === 'object' && piiHashHex.length) {
        // Handle bytes array
        piiHashHex = ethers.hexlify(piiHashHex).slice(2)
      }
      
      return {
        success: true,
        certificateId: certificateId,
        piiHash: piiHashHex,
        issuer: result[2],
        timestamp: Number(result[3]),
        revoked: result[4],
        courseName: result[5],
        issuerId: result[6],
        revocationReason: result[7] || null
      }
    } catch (error) {
      console.error('Get certificate error:', error)
      
      // Check if it's a connection error
      const errorMessage = error.message || error.reason || String(error)
      if (errorMessage.includes('network') || 
          errorMessage.includes('connection') ||
          errorMessage.includes('ECONNREFUSED') ||
          errorMessage.includes('Failed to fetch')) {
        return {
          success: false,
          error: 'Failed to connect to Ethereum network. Make sure Hardhat node is running on http://127.0.0.1:8545'
        }
      }
      
      // Check if it's a "Certificate does not exist" error
      if (errorMessage.includes('Certificate does not exist') || 
          errorMessage.includes('revert') ||
          errorMessage.includes('execution reverted')) {
        return {
          success: false,
          error: 'Certificate does not exist on blockchain'
        }
      }
      
      return {
        success: false,
        error: errorMessage || 'Failed to retrieve certificate'
      }
    }
  }

  /**
   * Check if certificate exists
   */
  async certificateExists(certificateId) {
    try {
      const contract = this.contract || this.getReadOnlyContract()
      const certIdBytes32 = this.stringToBytes32(certificateId)
      return await contract.certificateExists(certIdBytes32)
    } catch (error) {
      console.error('Certificate exists check error:', error)
      return false
    }
  }

  /**
   * Check if address is authorized issuer
   */
  async isAuthorizedIssuer(address) {
    try {
      const contract = this.contract || this.getReadOnlyContract()
      return await contract.isAuthorizedIssuer(address)
    } catch (error) {
      console.error('Authorized issuer check error:', error)
      return false
    }
  }

  // ============================================================================
  // Transaction Methods (Requires Wallet Connection)
  // ============================================================================

  /**
   * Issue certificate (requires transaction)
   */
  async issueCertificate(certificateId, piiHash, courseName, issuerId) {
    try {
      if (!this.contract) {
        throw new Error('Wallet not connected. Please connect MetaMask first.')
      }

      const certIdBytes32 = this.stringToBytes32(certificateId)
      const piiHashBytes32 = this.hexToBytes32(piiHash)

      // Estimate gas
      const gasEstimate = await this.contract.issueCertificate.estimateGas(
        certIdBytes32,
        piiHashBytes32,
        courseName,
        issuerId
      )

      // Send transaction
      const tx = await this.contract.issueCertificate(
        certIdBytes32,
        piiHashBytes32,
        courseName,
        issuerId,
        { gasLimit: gasEstimate * 120n / 100n } // Add 20% buffer
      )

      // Wait for transaction
      const receipt = await tx.wait()

      return {
        success: true,
        transactionHash: receipt.hash,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString()
      }
    } catch (error) {
      console.error('Issue certificate error:', error)
      return {
        success: false,
        error: error.message || 'Transaction failed'
      }
    }
  }

  /**
   * Revoke certificate (requires transaction)
   */
  async revokeCertificate(certificateId, reason = '') {
    try {
      if (!this.contract) {
        throw new Error('Wallet not connected. Please connect MetaMask first.')
      }

      const certIdBytes32 = this.stringToBytes32(certificateId)

      // Estimate gas
      const gasEstimate = await this.contract.revokeCertificate.estimateGas(
        certIdBytes32,
        reason
      )

      // Send transaction
      const tx = await this.contract.revokeCertificate(
        certIdBytes32,
        reason,
        { gasLimit: gasEstimate * 120n / 100n } // Add 20% buffer
      )

      // Wait for transaction
      const receipt = await tx.wait()

      return {
        success: true,
        transactionHash: receipt.hash,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString()
      }
    } catch (error) {
      console.error('Revoke certificate error:', error)
      return {
        success: false,
        error: error.message || 'Transaction failed'
      }
    }
  }

  // ============================================================================
  // Event Listeners
  // ============================================================================

  /**
   * Listen for CertificateIssued events
   */
  onCertificateIssued(callback) {
    if (!this.contract) {
      const contract = this.getReadOnlyContract()
      contract.on('CertificateIssued', callback)
    } else {
      this.contract.on('CertificateIssued', callback)
    }
  }

  /**
   * Listen for CertificateRevoked events
   */
  onCertificateRevoked(callback) {
    if (!this.contract) {
      const contract = this.getReadOnlyContract()
      contract.on('CertificateRevoked', callback)
    } else {
      this.contract.on('CertificateRevoked', callback)
    }
  }

  // ============================================================================
  // Utility Methods
  // ============================================================================

  /**
   * Convert string to bytes32 (using keccak256 hash)
   */
  stringToBytes32(str) {
    return ethers.id(str)
  }

  /**
   * Convert hex string to bytes32
   */
  hexToBytes32(hex) {
    // Remove 0x prefix if present
    const cleanHex = hex.replace(/^0x/, '')
    
    // Convert to bytes and pad to 32 bytes
    const bytes = ethers.getBytes('0x' + cleanHex.padStart(64, '0'))
    return ethers.hexlify(bytes.slice(0, 32))
  }

  /**
   * Format address for display
   */
  formatAddress(address) {
    if (!address) return ''
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  /**
   * Get network name from chain ID
   */
  async getNetworkName() {
    try {
      if (!this.provider) {
        if (typeof window.ethereum !== 'undefined') {
          this.provider = new ethers.BrowserProvider(window.ethereum)
        } else {
          return 'unknown'
        }
      }
      
      const network = await this.provider.getNetwork()
      const chainId = Number(network.chainId)
      
      const networkMap = {
        11155111: 'sepolia',
        5: 'goerli',
        80001: 'mumbai',
        1337: 'hardhat'
      }
      
      return networkMap[chainId] || 'unknown'
    } catch (error) {
      return 'unknown'
    }
  }
}

// ============================================================================
// Create Singleton Instance
// ============================================================================

let ethereumServiceInstance = null

/**
 * Get or create Ethereum service instance
 */
export function getEthereumService(contractAddress, networkName = 'sepolia') {
  if (!ethereumServiceInstance || 
      ethereumServiceInstance.contractAddress !== contractAddress ||
      ethereumServiceInstance.networkName !== networkName) {
    ethereumServiceInstance = new EthereumService(contractAddress, networkName)
  }
  return ethereumServiceInstance
}

// Export class for direct instantiation
export { EthereumService }

// Export default
export default getEthereumService

