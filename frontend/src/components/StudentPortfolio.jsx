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

      if (response.certificates.length > 0) {
        setResult({
          type: 'success',
          data: response,
        })
      } else {
        setResult({
          type: 'error',
          message: `No certificates found for Student ID: ${studentId}`,
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
                📚 Found {result.data.count} certificate(s) for Student ID:{' '}
                {result.data.student_id}
              </h3>
              {result.data.certificates.map((cert, index) => (
                <div key={index} className="certificate">
                  <h4>Certificate {index + 1}</h4>
                  <div className="certificate-details">
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
            <div>❌ {result.message}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default StudentPortfolio

