/**
 * Direct Ethereum Certificate Verification Component
 * 
 * Verifies certificates directly on Ethereum blockchain without backend
 */

import React, { useState } from 'react'
import { getEthereumService } from '../services/ethereum'
import './DirectEthereumVerify.css'

const DirectEthereumVerify = ({ contractAddress, networkName }) => {
  const [certificateId, setCertificateId] = useState('')
  const [piiHash, setPiiHash] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState(null)

  const ethereumService = getEthereumService(contractAddress, networkName)

  // Check connection on mount
  React.useEffect(() => {
    const checkConnection = async () => {
      try {
        // Try to get a simple contract call to verify connection
        const contract = ethereumService.getReadOnlyContract()
        // Try to get network info
        const provider = contract.provider || contract.runner?.provider
        if (provider) {
          const network = await provider.getNetwork()
          setConnectionStatus({
            connected: true,
            network: networkName,
            chainId: Number(network.chainId)
          })
        }
      } catch (err) {
        setConnectionStatus({
          connected: false,
          error: err.message || 'Failed to connect to Ethereum network'
        })
      }
    }
    
    if (contractAddress) {
      checkConnection()
    } else {
      setConnectionStatus({
        connected: false,
        error: 'Contract address not configured'
      })
    }
  }, [contractAddress, networkName])

  const handleVerify = async () => {
    if (!certificateId.trim()) {
      setError('Please enter a certificate ID')
      return
    }

    setVerifying(true)
    setError(null)
    setResult(null)

    try {
      // If no PII hash provided, try to get certificate info first
      let hashToVerify = piiHash.trim()

      if (!hashToVerify) {
        // Try to get certificate info to see if it exists and get PII hash
        const certInfo = await ethereumService.getCertificate(certificateId)
        if (!certInfo.success) {
          let errorMsg = certInfo.error || 'Certificate not found on blockchain'
          if (errorMsg.includes('does not exist')) {
            errorMsg += '\n\nPossible reasons:\n' +
              '• Certificate ID is incorrect\n' +
              '• Certificate was not issued on Ethereum\n' +
              '• Hardhat node was restarted (contract state lost)\n' +
              '• Contract was not deployed\n\n' +
              'Solution: Issue the certificate first, or verify the certificate ID is correct.'
          } else if (errorMsg.includes('connect') || errorMsg.includes('network')) {
            errorMsg += '\n\nMake sure:\n' +
              '• Hardhat node is running: cd contracts && npx hardhat node\n' +
              '• Contract is deployed: cd contracts && npx hardhat run scripts/deploy.js --network localhost\n' +
              '• Contract address is correct in frontend/.env'
          }
          setError(errorMsg)
          setVerifying(false)
          return
        }
        // Use the stored PII hash from blockchain
        hashToVerify = certInfo.piiHash
        // Auto-fill PII hash field for user reference
        setPiiHash(certInfo.piiHash)
      }

      // Verify certificate with PII hash
      const verifyResult = await ethereumService.verifyCertificate(
        certificateId,
        hashToVerify
      )

      if (verifyResult.success) {
        setResult({
          ...verifyResult,
          type: 'verification'
        })
      } else {
        setError(verifyResult.error || 'Verification failed')
      }
    } catch (err) {
      console.error('Verification error:', err)
      setError(err.message || 'An error occurred during verification. Make sure Hardhat node is running.')
    } finally {
      setVerifying(false)
    }
  }

  const handleGetCertificateInfo = async () => {
    if (!certificateId.trim()) {
      setError('Please enter a certificate ID')
      return
    }

    setVerifying(true)
    setError(null)
    setResult(null)

    try {
      const certInfo = await ethereumService.getCertificate(certificateId)
      
      if (certInfo.success) {
        setResult({
          ...certInfo,
          type: 'certificate_info'
        })
        // Auto-fill PII hash if available
        if (certInfo.piiHash) {
          setPiiHash(certInfo.piiHash)
        }
      } else {
        let errorMsg = certInfo.error || 'Certificate not found on blockchain'
        if (errorMsg.includes('does not exist')) {
          errorMsg += '\n\nPossible reasons:\n' +
            '• Certificate ID is incorrect\n' +
            '• Certificate was not issued on Ethereum\n' +
            '• Hardhat node was restarted (contract state lost)\n' +
            '• Contract was not deployed\n\n' +
            'Solution: Issue the certificate first, or verify the certificate ID is correct.'
        } else if (errorMsg.includes('connect') || errorMsg.includes('network')) {
          errorMsg += '\n\nMake sure:\n' +
            '• Hardhat node is running: cd contracts && npx hardhat node\n' +
            '• Contract is deployed: cd contracts && npx hardhat run scripts/deploy.js --network localhost\n' +
            '• Contract address is correct in frontend/.env'
        }
        setError(errorMsg)
      }
    } catch (err) {
      setError(err.message || 'An error occurred')
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div className="direct-ethereum-verify">
      <h2>🔗 Direct Ethereum Verification</h2>
      <p className="subtitle">Verify certificates directly on Ethereum blockchain</p>

      {connectionStatus && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '10px', 
          borderRadius: '4px',
          backgroundColor: connectionStatus.connected ? '#e8f5e9' : '#ffebee',
          color: connectionStatus.connected ? '#2e7d32' : '#c62828'
        }}>
          {connectionStatus.connected ? (
            <div>
              ✅ Connected to {networkName} network (Chain ID: {connectionStatus.chainId})
              <div style={{ fontSize: '0.85em', marginTop: '5px' }}>
                Contract: {contractAddress ? `${contractAddress.substring(0, 20)}...` : 'Not configured'}
              </div>
            </div>
          ) : (
            <div>
              ❌ Connection Error: {connectionStatus.error}
              <div style={{ fontSize: '0.85em', marginTop: '5px' }}>
                {networkName === 'hardhat' && 'Make sure Hardhat node is running: cd contracts && npx hardhat node'}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="verify-form">
        <div className="form-group">
          <label htmlFor="certificate-id">Certificate ID:</label>
          <input
            id="certificate-id"
            type="text"
            value={certificateId}
            onChange={(e) => setCertificateId(e.target.value)}
            placeholder="Enter certificate ID"
            disabled={verifying}
          />
        </div>

        <div className="form-group">
          <label htmlFor="pii-hash">PII Hash (optional):</label>
          <input
            id="pii-hash"
            type="text"
            value={piiHash}
            onChange={(e) => setPiiHash(e.target.value)}
            placeholder="Enter PII hash (will fetch from blockchain if empty)"
            disabled={verifying}
          />
          <small>If empty, will retrieve from blockchain</small>
        </div>

        <div className="button-group">
          <button
            onClick={handleGetCertificateInfo}
            disabled={verifying || !certificateId.trim()}
            className="btn-secondary"
          >
            {verifying ? 'Loading...' : 'Get Certificate Info'}
          </button>
          <button
            onClick={handleVerify}
            disabled={verifying || !certificateId.trim()}
            className="btn-primary"
          >
            {verifying ? 'Verifying...' : 'Verify Certificate'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message" style={{ whiteSpace: 'pre-line' }}>
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div className="verification-result">
          <h3>Verification Result</h3>
          
          {result.type === 'certificate_info' ? (
            <div className="certificate-details">
              <div className="detail-row">
                <strong>Certificate ID:</strong>
                <span>{certificateId}</span>
              </div>
              <div className="detail-row">
                <strong>Course:</strong>
                <span>{result.courseName}</span>
              </div>
              <div className="detail-row">
                <strong>Issuer:</strong>
                <span>{ethereumService.formatAddress(result.issuer)}</span>
              </div>
              <div className="detail-row">
                <strong>Issued:</strong>
                <span>{new Date(result.timestamp * 1000).toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <strong>Status:</strong>
                <span className={result.revoked ? 'status-revoked' : 'status-active'}>
                  {result.revoked ? '❌ Revoked' : '✅ Active'}
                </span>
              </div>
              {result.revoked && result.revocationReason && (
                <div className="detail-row">
                  <strong>Revocation Reason:</strong>
                  <span>{result.revocationReason}</span>
                </div>
              )}
            </div>
          ) : result.type === 'verification' ? (
            <div className="verification-details">
              <div className={`status-badge ${result.valid ? 'valid' : 'invalid'}`}>
                {result.valid ? '✅ Valid Certificate' : '❌ Invalid Certificate'}
              </div>
              
              {result.valid ? (
                <div className="detail-list">
                  <div className="detail-item">
                    <strong>Issuer Address:</strong> {ethereumService.formatAddress(result.issuer)}
                  </div>
                  <div className="detail-item">
                    <strong>Issued:</strong> {new Date(result.timestamp * 1000).toLocaleString()}
                  </div>
                  <div className="detail-item">
                    <strong>Revoked:</strong> {result.revoked ? '❌ Yes' : '✅ No'}
                  </div>
                  {result.revoked && (
                    <div className="detail-item" style={{ color: '#c62828', fontWeight: 'bold' }}>
                      This certificate has been revoked and is no longer valid.
                    </div>
                  )}
                </div>
              ) : (
                <div className="detail-list">
                  <div className="detail-item" style={{ color: '#c62828' }}>
                    Certificate verification failed. The certificate may be revoked or the PII hash does not match.
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="verification-details">
              <div className="status-badge invalid">
                ❌ Invalid Response
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DirectEthereumVerify

