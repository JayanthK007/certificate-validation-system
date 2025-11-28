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
          data: response,
        })
      } else if (response.verified && !response.valid) {
        setResult({
          type: 'error',
          message: 'Certificate found but has been revoked or is invalid.',
        })
      } else {
        setResult({
          type: 'error',
          message: 'Certificate not found in the blockchain.',
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
              <div className="certificate">
                <div className="certificate-details">
                  <div>
                    <strong>Student:</strong> {result.data.certificate.student_name}
                  </div>
                  <div>
                    <strong>Student ID:</strong> {result.data.certificate.student_id}
                  </div>
                  <div>
                    <strong>Course:</strong> {result.data.certificate.course_name}
                  </div>
                  <div>
                    <strong>Grade:</strong> {result.data.certificate.grade}
                  </div>
                  <div>
                    <strong>Issuer:</strong> {result.data.certificate.issuer_name}
                  </div>
                  <div>
                    <strong>Issue Date:</strong>{' '}
                    {new Date(
                      result.data.certificate.timestamp * 1000
                    ).toLocaleDateString()}
                  </div>
                </div>
                <div className="certificate-id">
                  <strong>Certificate ID:</strong>{' '}
                  {result.data.certificate.certificate_id}
                </div>
              </div>
              <p>
                <strong>Blockchain Proof:</strong> Block{' '}
                {result.data.blockchain_proof.block_index} | Hash:{' '}
                {result.data.blockchain_proof.block_hash.substring(0, 20)}...
              </p>
              {result.data.blockchain_proof.merkle_root && (
                <p>
                  <strong>Merkle Root:</strong>{' '}
                  {result.data.blockchain_proof.merkle_root.substring(0, 20)}...
                </p>
              )}
              {result.data.signature_verified !== undefined && (
                <p>
                  <strong>Digital Signature:</strong>{' '}
                  {result.data.signature_verified ? (
                    <span>✅ Verified</span>
                  ) : (
                    <span>❌ Invalid</span>
                  )}
                </p>
              )}
            </>
          ) : (
            <div>❌ {result.message}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default VerifyCertificate

