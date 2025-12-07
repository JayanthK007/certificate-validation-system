import React, { useState } from 'react'
import { certificateAPI, extractErrorMessage } from '../services/api'

const StudentPortfolio = () => {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [studentId, setStudentId] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    try {
      const response = await certificateAPI.getByStudent(studentId)

      if (response.certificates && response.certificates.length > 0) {
        setResult({
          type: 'success',
          data: response,
        })
      } else if (response.note) {
        // Ethereum limitation - show informational message
        setResult({
          type: 'info',
          message: response.note,
        })
      } else {
        setResult({
          type: 'info',
          message: `No certificates found for Student ID: ${studentId}. Please verify certificates individually by certificate ID in the "Verify Certificate" tab.`,
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
        <i className="fas fa-user-graduate"></i> Student Portfolio
      </h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="viewStudentId">Student ID *</label>
          <input
            type="text"
            id="viewStudentId"
            required
            placeholder="Enter student ID to view certificates"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          <i className="fas fa-eye"></i>{' '}
          {loading ? 'Loading...' : 'View Certificates'}
        </button>
      </form>

      {result && (
        <div className={`result ${result.type}`}>
          {result.type === 'success' && result.data ? (
            <>
              <h3>
                📚 Student Portfolio - {result.data.student_id}
              </h3>
              <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#e7f3ff', borderRadius: '4px', fontSize: '0.9em' }}>
                <strong>Total Certificates:</strong> {result.data.count} course(s) completed
              </div>
              
              <div style={{ display: 'grid', gap: '15px' }}>
                {result.data.certificates.map((cert, index) => (
                  <div key={index} className="certificate" style={{ 
                    border: '2px solid #e0e0e0', 
                    borderRadius: '8px', 
                    padding: '15px',
                    backgroundColor: cert.revoked ? '#fff5f5' : '#fff'
                  }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      marginBottom: '10px',
                      paddingBottom: '10px',
                      borderBottom: '1px solid #e0e0e0'
                    }}>
                      <h4 style={{ margin: 0, color: '#1976d2' }}>
                        📖 {cert.course_name || 'Course Name Not Available'}
                      </h4>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        fontSize: '0.85em',
                        fontWeight: 'bold',
                        backgroundColor: cert.status === 'active' && !cert.revoked ? '#e8f5e9' : '#ffebee',
                        color: cert.status === 'active' && !cert.revoked ? '#2e7d32' : '#c62828'
                      }}>
                        {cert.revoked ? '❌ REVOKED' : cert.status ? cert.status.toUpperCase() : '✅ ACTIVE'}
                      </span>
                    </div>
                    
                    <div className="certificate-details" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                      {cert.issuer_id && (
                        <div>
                          <strong>🏫 Institution:</strong> {cert.issuer_id}
                        </div>
                      )}
                      {cert.timestamp && (
                        <div>
                          <strong>📅 Completed:</strong>{' '}
                          {new Date(cert.timestamp * 1000).toLocaleDateString('en-US', { 
                            year: 'numeric', 
                            month: 'long', 
                            day: 'numeric' 
                          })}
                        </div>
                      )}
                      {cert.revocation_reason && (
                        <div style={{ gridColumn: '1 / -1', padding: '8px', backgroundColor: '#ffebee', borderRadius: '4px', fontSize: '0.9em' }}>
                          <strong>⚠️ Revocation Reason:</strong> {cert.revocation_reason}
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
                    
                    {cert.blockchain_verified !== undefined && (
                      <div style={{ 
                        marginTop: '8px', 
                        fontSize: '0.85em',
                        color: cert.blockchain_verified ? '#2e7d32' : '#f57c00'
                      }}>
                        {cert.blockchain_verified ? (
                          <span>✅ Verified on Ethereum blockchain</span>
                        ) : (
                          <div>
                            <span>⚠️ Not verified on Ethereum blockchain</span>
                            {cert.note && cert.note.includes('Ethereum') && (
                              <div style={{ marginTop: '5px', fontSize: '0.9em', fontStyle: 'italic' }}>
                                This certificate may have been issued before Ethereum deployment or the Hardhat node was restarted.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {cert.note && (
                      <div style={{ 
                        marginTop: '10px', 
                        padding: '8px', 
                        backgroundColor: '#fff3cd', 
                        borderRadius: '4px', 
                        fontSize: '0.85em' 
                      }}>
                        ℹ️ {cert.note}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <>
              <h3>
                {result.type === 'info' ? 'ℹ️' : '❌'}{' '}
                {result.type === 'info' ? 'Information' : 'Error'}
              </h3>
              <p style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>
                {result.message}
              </p>
              {result.type === 'info' && (
                <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#e7f3ff', borderRadius: '4px' }}>
                  <strong>💡 Tip:</strong> To verify a certificate, go to the "Verify Certificate" tab and enter the certificate ID.
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default StudentPortfolio

