import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { certificateAPI, extractErrorMessage } from '../services/api'

const IssueCertificate = () => {
  const { isAuthenticated, isInstitution } = useAuth()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [formData, setFormData] = useState({
    student_name: '',
    student_id: '',
    course_name: '',
    grade: '',
    course_duration: '',
  })

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!isAuthenticated()) {
      setResult({
        type: 'error',
        message: 'Please login first to issue certificates.',
      })
      return
    }

    if (!isInstitution()) {
      setResult({
        type: 'error',
        message: 'Only institutions and admins can issue certificates.',
      })
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await certificateAPI.issue(formData)

      if (response.success) {
        setResult({
          type: 'success',
          data: response,
        })
        setFormData({
          student_name: '',
          student_id: '',
          course_name: '',
          grade: '',
          course_duration: '',
        })
      } else {
        setResult({
          type: 'error',
          message: response.message || 'Failed to issue certificate',
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

  if (!isAuthenticated()) {
    return (
      <div className="card">
        <h2>
          <i className="fas fa-graduation-cap"></i> Issue Certificate
        </h2>
        <div className="result error">
          Please login first to issue certificates.
        </div>
      </div>
    )
  }

  if (!isInstitution()) {
    return (
      <div className="card">
        <h2>
          <i className="fas fa-graduation-cap"></i> Issue Certificate
        </h2>
        <div className="result error">
          Only institutions and admins can issue certificates.
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2>
        <i className="fas fa-graduation-cap"></i> Issue Certificate
      </h2>
      <form className="form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="studentName">Student Name *</label>
            <input
              type="text"
              id="studentName"
              required
              placeholder="Enter student's full name"
              value={formData.student_name}
              onChange={(e) =>
                setFormData({ ...formData, student_name: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="studentId">Student ID *</label>
            <input
              type="text"
              id="studentId"
              required
              placeholder="Enter student ID"
              value={formData.student_id}
              onChange={(e) =>
                setFormData({ ...formData, student_id: e.target.value })
              }
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="courseName">Course Name *</label>
            <input
              type="text"
              id="courseName"
              required
              placeholder="Enter course name"
              value={formData.course_name}
              onChange={(e) =>
                setFormData({ ...formData, course_name: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="grade">Grade *</label>
            <select
              id="grade"
              required
              value={formData.grade}
              onChange={(e) =>
                setFormData({ ...formData, grade: e.target.value })
              }
            >
              <option value="">Select Grade</option>
              <option value="A+">A+ (Excellent)</option>
              <option value="A">A (Very Good)</option>
              <option value="B+">B+ (Good)</option>
              <option value="B">B (Satisfactory)</option>
              <option value="C+">C+ (Average)</option>
              <option value="C">C (Below Average)</option>
              <option value="D">D (Poor)</option>
              <option value="F">F (Fail)</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="courseDuration">Course Duration</label>
          <input
            type="text"
            id="courseDuration"
            placeholder="e.g., 4 years, 6 months"
            value={formData.course_duration}
            onChange={(e) =>
              setFormData({ ...formData, course_duration: e.target.value })
            }
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          <i className="fas fa-plus"></i>{' '}
          {loading ? 'Issuing...' : 'Issue Certificate'}
        </button>
      </form>

      {result && (
        <div className={`result ${result.type}`}>
          {result.type === 'success' && result.data ? (
            <>
              <h3>✅ Certificate Issued Successfully!</h3>
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
                    <strong>Duration:</strong> {result.data.certificate.course_duration}
                  </div>
                </div>
                <div className="certificate-id">
                  <strong>Certificate ID:</strong>{' '}
                  {result.data.certificate.certificate_id}
                </div>
              </div>
              <p>
                <strong>Blockchain Info:</strong> Block{' '}
                {result.data.blockchain_info.block_index} | Hash:{' '}
                {result.data.blockchain_info.block_hash.substring(0, 20)}...
                {result.data.blockchain_info.genesis_created && (
                  <span style={{ display: 'block', marginTop: '5px', fontSize: '0.9em', color: '#666' }}>
                    ℹ️ Note: Genesis block (Block 0) was created automatically. This is normal for the first certificate.
                  </span>
                )}
              </p>
              {result.data.signature && (
                <p>
                  <strong>Signature:</strong>{' '}
                  {result.data.signature.signed ? (
                    <span>✅ Digitally Signed</span>
                  ) : (
                    <span>❌ Not Signed</span>
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

export default IssueCertificate

