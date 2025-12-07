import React, { useState } from 'react'
import { certificateAPI, extractErrorMessage } from '../services/api'

const VerifyCertificate = () => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [certificateId, setCertificateId] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    try {
      const response = await certificateAPI.verify(certificateId)

      if (response.verified && response.valid) {
        setResult({
          type: 'success',
          data: response
        })
      } else if (response.verified && !response.valid) {
        let message = 'Certificate found but has been revoked or is invalid.'
        if (response.blockchain_proof && response.blockchain_proof.revoked) {
          message += ' This certificate has been revoked.'
        }
        setResult({
          type: 'error',
          message: message,
        })
      } else {
        // Check if there's a more specific error message
        const errorMsg = response.error || response.message || 'Certificate not found in the blockchain.'
        
        // Check if it's a connection error
        const isConnectionError = errorMsg.includes('Failed to connect') || 
                                  errorMsg.includes('Hardhat node') || 
                                  (errorMsg.includes('contract') && errorMsg.includes('deployed'))
        
        let displayMessage = errorMsg
        
        if (isConnectionError) {
          displayMessage = `⚠️ ${errorMsg}\n\n` +
            `To fix this:\n` +
            `1. Start Hardhat node: cd contracts && npx hardhat node\n` +
            `2. Deploy contract: cd contracts && npx hardhat run scripts/deploy.js --network hardhat\n` +
            `3. Update CONTRACT_ADDRESS in backend/.env with the deployed address\n` +
            `4. Restart the backend server`
        } else if (errorMsg.includes('previous') || errorMsg.includes('database')) {
          displayMessage = errorMsg + '\n\nThese certificates were issued on a previous system version and are not on Ethereum.'
        } else {
          displayMessage = errorMsg || 'Certificate not found in the blockchain.'
        }
        
        setResult({
          type: 'error',
          message: displayMessage
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
        <i className="fas fa-search"></i> Verify Certificate
      </h2>
      
      <form className="form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="certificateId">Certificate ID *</label>
          <input
            type="text"
            id="certificateId"
            required
            placeholder="Enter certificate ID to verify"
            value={certificateId}
            onChange={(e) => setCertificateId(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          <i className="fas fa-check"></i>{' '}
          {loading ? 'Verifying...' : 'Verify Certificate'}
        </button>
      </form>

      {result && (
        <div className={`result ${result.type}`}>
          {result.type === 'success' && result.data ? (
            <>
              <h3>✅ Certificate Verified Successfully!</h3>
              {result.data.certificate && (
                <div className="certificate">
                  <div className="certificate-details">
                    {result.data.certificate.certificate_id && (
                      <div>
                        <strong>Certificate ID:</strong> {result.data.certificate.certificate_id}
                      </div>
                    )}
                    {result.data.certificate.course_name && (
                      <div>
                        <strong>Course:</strong> {result.data.certificate.course_name}
                      </div>
                    )}
                    {result.data.certificate.issuer_id && (
                      <div>
                        <strong>Issuer ID:</strong> {result.data.certificate.issuer_id}
                      </div>
                    )}
                    {result.data.certificate.timestamp && (
                      <div>
                        <strong>Issue Date:</strong>{' '}
                        {new Date(
                          result.data.certificate.timestamp * 1000
                        ).toLocaleDateString()}
                      </div>
                    )}
                    <div>
                      <strong>Status:</strong>{' '}
                      <span style={{ 
                        color: result.data.certificate.status === 'active' ? 'green' : 'red',
                        fontWeight: 'bold'
                      }}>
                        {result.data.certificate.status ? result.data.certificate.status.toUpperCase() : 'ACTIVE'}
                      </span>
                    </div>
                    {(result.data.certificate.student_name || result.data.certificate.student_id || result.data.certificate.grade) && (
                      <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#e7f3ff', borderRadius: '4px', fontSize: '0.9em' }}>
                        <strong>Note:</strong> PII (Student Name, Student ID, Grade) is not stored on Ethereum blockchain for privacy. 
                        Only a hash of this information is stored.
                      </div>
                    )}
                  </div>
                </div>
              )}
              {result.data.blockchain_proof && (
                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                  <strong>Blockchain Proof:</strong>
                  {result.data.blockchain_proof.network && (
                    <div>
                      <strong>Network:</strong> {result.data.blockchain_proof.network}
                    </div>
                  )}
                  {result.data.blockchain_proof.contract_address && (
                    <div>
                      <strong>Contract Address:</strong>{' '}
                      <code style={{ fontSize: '0.9em' }}>
                        {result.data.blockchain_proof.contract_address.substring(0, 20)}...
                        {result.data.blockchain_proof.contract_address.substring(result.data.blockchain_proof.contract_address.length - 10)}
                      </code>
                    </div>
                  )}
                  {result.data.blockchain_proof.timestamp && (
                    <div>
                      <strong>Block Timestamp:</strong>{' '}
                      {new Date(result.data.blockchain_proof.timestamp * 1000).toLocaleString()}
                    </div>
                  )}
                  {result.data.blockchain_proof.issuer && (
                    <div>
                      <strong>Issuer Address:</strong>{' '}
                      <code style={{ fontSize: '0.9em' }}>
                        {result.data.blockchain_proof.issuer.substring(0, 20)}...
                        {result.data.blockchain_proof.issuer.substring(result.data.blockchain_proof.issuer.length - 10)}
                      </code>
                    </div>
                  )}
                  <div>
                    <strong>Valid:</strong>{' '}
                    {result.data.blockchain_proof.valid ? (
                      <span style={{ color: 'green', fontWeight: 'bold' }}>✅ Yes</span>
                    ) : (
                      <span style={{ color: 'red', fontWeight: 'bold' }}>❌ No</span>
                    )}
                  </div>
                  {result.data.blockchain_proof.revoked && (
                    <div>
                      <strong>Revoked:</strong>{' '}
                      <span style={{ color: 'red', fontWeight: 'bold' }}>❌ Yes</span>
                    </div>
                  )}
                </div>
              )}
              {result.data.note && (
                <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#fff3cd', borderRadius: '4px', fontSize: '0.9em' }}>
                  ℹ️ {result.data.note}
                </div>
              )}
            </>
          ) : (
            <div style={{ whiteSpace: 'pre-line' }}>❌ {result.message}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default VerifyCertificate

