/**
 * Ethereum Wallet Connection Component
 * 
 * Allows users to connect MetaMask wallet and interact with Ethereum contracts
 */

import { useState, useEffect } from 'react'
import { getEthereumService } from '../services/ethereum'
import './EthereumConnect.css'

const EthereumConnect = ({ contractAddress, networkName, onConnected }) => {
  const [connected, setConnected] = useState(false)
  const [connecting, setConnecting] = useState(false)
  const [account, setAccount] = useState(null)
  const [error, setError] = useState(null)
  const [network, setNetwork] = useState(null)

  const ethereumService = getEthereumService(contractAddress, networkName)

  useEffect(() => {
    // Check if already connected
    checkConnection()
    
    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', handleAccountsChanged)
      window.ethereum.on('chainChanged', handleChainChanged)
    }

    return () => {
      if (window.ethereum) {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
        window.ethereum.removeListener('chainChanged', handleChainChanged)
      }
    }
  }, [])

  const checkConnection = async () => {
    try {
      const address = await ethereumService.getCurrentAccount()
      if (address) {
        setAccount(address)
        setConnected(true)
        const networkName = await ethereumService.getNetworkName()
        setNetwork(networkName)
        if (onConnected) onConnected(address)
      }
    } catch (error) {
      console.error('Connection check error:', error)
    }
  }

  const handleAccountsChanged = (accounts) => {
    if (accounts.length === 0) {
      setConnected(false)
      setAccount(null)
    } else {
      setAccount(accounts[0])
      setConnected(true)
      if (onConnected) onConnected(accounts[0])
    }
  }

  const handleChainChanged = () => {
    window.location.reload()
  }

  const connectWallet = async () => {
    setConnecting(true)
    setError(null)

    try {
      const result = await ethereumService.connectWallet()
      
      if (result.success) {
        setConnected(true)
        setAccount(result.address)
        const networkName = await ethereumService.getNetworkName()
        setNetwork(networkName)
        if (onConnected) onConnected(result.address)
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError(err.message || 'Failed to connect wallet')
    } finally {
      setConnecting(false)
    }
  }

  const disconnect = () => {
    ethereumService.disconnect()
    setConnected(false)
    setAccount(null)
    setNetwork(null)
    if (onConnected) onConnected(null)
  }

  const isMetaMaskInstalled = typeof window.ethereum !== 'undefined'

  if (!isMetaMaskInstalled) {
    return (
      <div className="ethereum-connect">
        <div className="ethereum-warning">
          <h3>🔌 MetaMask Not Installed</h3>
          <p>To interact with Ethereum contracts, please install MetaMask:</p>
          <a 
            href="https://metamask.io/download/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="metamask-link"
          >
            Install MetaMask
          </a>
          <p className="note">You can still use the system through the backend API without MetaMask.</p>
        </div>
      </div>
    )
  }

  if (connected && account) {
    return (
      <div className="ethereum-connect">
        <div className="ethereum-connected">
          <div className="connection-status">
            <span className="status-indicator connected"></span>
            <span>Connected</span>
          </div>
          <div className="wallet-info">
            <div className="wallet-address">
              <strong>Wallet:</strong> {ethereumService.formatAddress(account)}
            </div>
            {network && (
              <div className="network-name">
                <strong>Network:</strong> {network}
              </div>
            )}
          </div>
          <button onClick={disconnect} className="btn-disconnect">
            Disconnect
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="ethereum-connect">
      <div className="ethereum-disconnected">
        <h3>🔗 Connect to Ethereum</h3>
        <p>Connect your MetaMask wallet to interact directly with smart contracts</p>
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}
        <button 
          onClick={connectWallet} 
          disabled={connecting}
          className="btn-connect"
        >
          {connecting ? 'Connecting...' : 'Connect MetaMask'}
        </button>
        <p className="note">
          This allows direct interaction with Ethereum contracts. 
          You can still use the backend API without connecting.
        </p>
      </div>
    </div>
  )
}

export default EthereumConnect

