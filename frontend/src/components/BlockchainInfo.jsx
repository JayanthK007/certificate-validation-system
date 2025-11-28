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
        // Build a more informative message with block/certificate counts
        let message = response.message
        if (response.block_count !== undefined && response.certificate_count !== undefined) {
          message += ` (${response.block_count} block(s), ${response.certificate_count} certificate(s))`
        }
        setResult({
          type: response.valid ? 'success' : 'error',
          message: message,
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

  const handleViewAll = async () => {
    setLoading(true)
    setResult(null)

    try {
      const response = await certificateAPI.getAll()
      if (response.certificates.length > 0) {
        setResult({
          type: 'success',
          data: response,
        })
      } else {
        setResult({
          type: 'error',
          message: 'No certificates found in the blockchain.',
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
          onClick={handleViewAll}
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
              <div>
                <strong>Total Blocks:</strong> {info.total_blocks}
              </div>
              <div>
                <strong>Total Certificates:</strong> {info.total_certificates}
              </div>
              <div>
                <strong>Active Certificates:</strong> {info.active_certificates}
              </div>
              <div>
                <strong>Revoked Certificates:</strong> {info.revoked_certificates}
              </div>
              <div>
                <strong>Chain Length:</strong> {info.chain_length}
              </div>
            </div>
            <div className="certificate-id">
              <strong>Latest Block Hash:</strong>{' '}
              {info.latest_block_hash.substring(0, 30)}...
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
                  <h3>📋 All Certificates ({result.data.count})</h3>
                  {result.data.certificates.map((cert, index) => (
                    <div key={index} className="certificate">
                      <h4>Certificate {index + 1}</h4>
                      <div className="certificate-details">
                        <div>
                          <strong>Student:</strong> {cert.student_name} (
                          {cert.student_id})
                        </div>
                        <div>
                          <strong>Course:</strong> {cert.course_name}
                        </div>
                        <div>
                          <strong>Grade:</strong> {cert.grade}
                        </div>
                        <div>
                          <strong>Issuer:</strong> {cert.issuer_name}
                        </div>
                        <div>
                          <strong>Issue Date:</strong>{' '}
                          {new Date(cert.timestamp * 1000).toLocaleDateString()}
                        </div>
                        <div>
                          <strong>Status:</strong>{' '}
                          <span
                            style={{
                              color: cert.status === 'active' ? 'green' : 'red',
                            }}
                          >
                            {cert.status.toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div className="certificate-id">
                        <strong>Certificate ID:</strong> {cert.certificate_id}
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <>
                  <h3>🔗 Blockchain Information</h3>
                  <div className="certificate">
                    <div className="certificate-details">
                      <div>
                        <strong>Total Blocks:</strong> {result.data.total_blocks}
                      </div>
                      <div>
                        <strong>Total Certificates:</strong>{' '}
                        {result.data.total_certificates}
                      </div>
                      <div>
                        <strong>Active Certificates:</strong>{' '}
                        {result.data.active_certificates}
                      </div>
                      <div>
                        <strong>Revoked Certificates:</strong>{' '}
                        {result.data.revoked_certificates}
                      </div>
                      <div>
                        <strong>Chain Length:</strong> {result.data.chain_length}
                      </div>
                    </div>
                    <div className="certificate-id">
                      <strong>Latest Block Hash:</strong>{' '}
                      {result.data.latest_block_hash.substring(0, 30)}...
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
                    {result.type === 'success' ? '✅' : '❌'}{' '}
                    {result.type === 'success'
                      ? 'Blockchain Validation Successful!'
                      : 'Blockchain Validation Failed!'}
                  </h3>
                  <p>{result.message}</p>
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

