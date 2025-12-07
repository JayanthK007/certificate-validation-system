import React, { useState, useEffect } from 'react'
import { blockchainAPI, certificateAPI, extractErrorMessage } from '../services/api'

const BlockchainInfo = () => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [info, setInfo] = useState(null)

  useEffect(() => {
    loadInfo()
  }, [])

  const loadInfo = async () => {
    try {
      const response = await blockchainAPI.getInfo()
      if (response.success) {
        setInfo(response.blockchain_info)
      }
    } catch (error) {
      console.error('Error loading blockchain info:', error)
    }
  }

  const handleGetInfo = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await blockchainAPI.getInfo()
      if (response.success) {
        setResult({
          type: 'success',
          data: response.blockchain_info,
        })
        setInfo(response.blockchain_info)
      }
    } catch (error) {
      setResult({
        type: 'error',
        message: extractErrorMessage(error) || 'Network error',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleValidate = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await blockchainAPI.validate()
      if (response.success) {
        setResult({
          type: response.valid ? 'success' : 'error',
          message: response.message,
        })
      }
    } catch (error) {
      setResult({
        type: 'error',
        message: extractErrorMessage(error) || 'Network error',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleViewAllCertificates = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await certificateAPI.getAll()
      if (response && response.certificates && response.certificates.length > 0) {
        setResult({
          type: 'success',
          data: response,
        })
      } else {
        setResult({
          type: 'info',
          message: response?.note || 'No certificates found in the index. Certificates will be added when you issue them.',
        })
      }
    } catch (error) {
      setResult({
        type: 'error',
        message: extractErrorMessage(error) || 'Network error',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2>
        <i className="fas fa-link"></i> Blockchain Information
      </h2>
      <div className="blockchain-actions">
        <button
          onClick={handleGetInfo}
          className="btn btn-secondary"
          disabled={loading}
        >
          <i className="fas fa-info-circle"></i> Get Blockchain Info
        </button>
        <button
          onClick={handleValidate}
          className="btn btn-secondary"
          disabled={loading}
        >
          <i className="fas fa-shield-alt"></i> Validate Blockchain
        </button>
        <button
          onClick={handleViewAllCertificates}
          className="btn btn-secondary"
          disabled={loading}
        >
          <i className="fas fa-list"></i> View All Certificates
        </button>
      </div>

      {info && !result && (
        <div className="result info">
          <h3>🔗 Blockchain Information</h3>
          <div className="certificate">
            <div className="certificate-details">
              <>
                <div>
                  <strong>Blockchain Type:</strong> Ethereum
                </div>
                <div>
                  <strong>Network:</strong> {info.network}
                </div>
                <div>
                  <strong>Chain ID:</strong> {info.chain_id}
                </div>
                <div>
                  <strong>Block Number:</strong> {info.block_number}
                </div>
                <div>
                  <strong>Connected:</strong> {info.connected ? '✅ Yes' : '❌ No'}
                </div>
                {info.contract_address && (
                  <div>
                    <strong>Contract Address:</strong> {info.contract_address.substring(0, 20)}...
                  </div>
                )}
              </>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className={`result ${result.type}`}>
          {result.type === 'success' && result.data ? (
            <>
              {result.data.certificates ? (
                <>
                  <h3>📋 All Certificates on Blockchain</h3>
                  <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
                    <strong>Summary:</strong> {result.data.count} total | {' '}
                    <span style={{ color: '#2e7d32' }}>✅ {result.data.verified_count || 0} verified on Ethereum</span> | {' '}
                    <span style={{ color: '#f57c00' }}>⚠️ {result.data.not_verified_count || 0} not found</span>
                  </div>
                  <div style={{ display: 'grid', gap: '15px' }}>
                    {result.data.certificates.map((cert, index) => (
                      <div key={index} className="certificate" style={{ 
                        border: '2px solid #e0e0e0', 
                        borderRadius: '8px', 
                        padding: '15px',
                        backgroundColor: cert.blockchain_verified ? '#f1f8e9' : '#fff3e0'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                          <h4 style={{ margin: 0, color: '#1976d2' }}>
                            📖 {cert.course_name || 'Course Name Not Available'}
                          </h4>
                          {cert.blockchain_verified !== undefined && (
                            <span style={{
                              padding: '4px 12px',
                              borderRadius: '12px',
                              fontSize: '0.85em',
                              fontWeight: 'bold',
                              backgroundColor: cert.blockchain_verified ? '#e8f5e9' : '#ffebee',
                              color: cert.blockchain_verified ? '#2e7d32' : '#c62828'
                            }}>
                              {cert.blockchain_verified ? '✅ Verified on Ethereum' : '❌ Not on Ethereum'}
                            </span>
                          )}
                        </div>
                        <div className="certificate-details" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                          <div>
                            <strong>👤 Student ID:</strong> {cert.student_id}
                          </div>
                          <div>
                            <strong>🏫 Issuer:</strong> {cert.issuer_id}
                          </div>
                          <div>
                            <strong>📅 Issued:</strong>{' '}
                            {cert.timestamp ? new Date(cert.timestamp * 1000).toLocaleDateString() : 'N/A'}
                          </div>
                          <div>
                            <strong>Status:</strong>{' '}
                            <span style={{ 
                              color: cert.status === 'active' ? 'green' : 'red',
                              fontWeight: 'bold'
                            }}>
                              {cert.status ? cert.status.toUpperCase() : 'ACTIVE'}
                            </span>
                          </div>
                          {cert.blockchain_verified && cert.blockchain_revoked && (
                            <div style={{ gridColumn: '1 / -1', padding: '8px', backgroundColor: '#ffebee', borderRadius: '4px' }}>
                              <strong>⚠️ Revoked on Blockchain:</strong> {cert.blockchain_revocation_reason || 'No reason provided'}
                            </div>
                          )}
                          {!cert.blockchain_verified && cert.blockchain_error && (
                            <div style={{ gridColumn: '1 / -1', padding: '8px', backgroundColor: '#fff3cd', borderRadius: '4px', fontSize: '0.9em' }}>
                              <strong>Error:</strong> {cert.blockchain_error}
                            </div>
                          )}
                        </div>
                        <div style={{ 
                          marginTop: '10px', 
                          padding: '10px', 
                          backgroundColor: '#f5f5f5', 
                          borderRadius: '4px',
                          fontSize: '0.85em',
                          fontFamily: 'monospace'
                        }}>
                          <strong>Certificate ID:</strong> {cert.certificate_id}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <h3>🔗 Blockchain Information</h3>
                  <div className="certificate">
                    <div className="certificate-details">
                      <>
                        <div>
                          <strong>Blockchain Type:</strong> Ethereum
                        </div>
                        <div>
                          <strong>Network:</strong> {result.data.network || result.data.blockchain_info?.network || 'N/A'}
                        </div>
                        <div>
                          <strong>Chain ID:</strong> {result.data.chain_id || result.data.blockchain_info?.chain_id || 'N/A'}
                        </div>
                        <div>
                          <strong>Block Number:</strong> {result.data.block_number || result.data.blockchain_info?.block_number || 0}
                        </div>
                        <div>
                          <strong>Connected:</strong> {(result.data.connected || result.data.blockchain_info?.connected) ? '✅ Yes' : '❌ No'}
                        </div>
                        {(result.data.contract_address || result.data.blockchain_info?.contract_address) && (
                          <div>
                            <strong>Contract Address:</strong> {(result.data.contract_address || result.data.blockchain_info?.contract_address || '').substring(0, 20)}...
                          </div>
                        )}
                      </>
                    </div>
                  </div>
                </>
              )}
            </>
          ) : (
            <>
              {result.message && (
                <>
                  <h3>
                    {result.type === 'success' ? '✅' : result.type === 'info' ? 'ℹ️' : '❌'}{' '}
                    {result.type === 'success'
                      ? 'Blockchain Validation Successful!'
                      : result.type === 'info'
                      ? 'Information'
                      : 'Blockchain Validation Failed!'}
                  </h3>
                  <p style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>{result.message}</p>
                </>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default BlockchainInfo

