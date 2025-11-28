/**
 * RevokeCertificate Component
 * 
 * This component provides the user interface for revoking certificates.
 * It allows authenticated institutions/admins to revoke certificates they issued
 * (or any certificate for admins).
 * 
 * Features:
 * - Form for entering certificate ID and optional revocation reason
 * - Role-based access control: only visible and functional for institutions/admins
 * - Displays success or error messages based on API response
 * - Integrates with `useAuth` hook for authentication checks
 * - Integrates with `certificateAPI` for backend communication
 */

import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { certificateAPI, extractErrorMessage } from '../services/api'

const RevokeCertificate = () => {
  // ========================================================================
  // Context and State Management
  // ========================================================================

  // Access authentication status and role from AuthContext
  const { isAuthenticated, isInstitution } = useAuth()
  
  // Loading state for form submission
  const [loading, setLoading] = useState(false)
  
  // State for displaying API results (success/error)
  const [result, setResult] = useState(null)
  
  // Form data state for revocation details
  const [formData, setFormData] = useState({
    certificate_id: '',
    reason: '',
  })

  // ========================================================================
  // Event Handlers
  // ========================================================================

  /**
   * Handles the form submission for revoking a certificate.
   * 
   * Performs client-side role checks, sends data to the backend,
   * and updates the UI with the result.
   * 
   * @param {Event} e - The form submission event.
   */
  const handleSubmit = async (e) => {
    e.preventDefault()

    // Client-side authentication and role check
    if (!isAuthenticated()) {
      setResult({
        type: 'error',
        message: 'Please login first to revoke certificates.',
      })
      return
    }

    if (!isInstitution()) {
      setResult({
        type: 'error',
        message: 'Only institutions and admins can revoke certificates.',
      })
      return
    }

    setLoading(true)
    setResult(null) // Clear previous results

    try {
      const response = await certificateAPI.revoke(
        formData.certificate_id,
        formData.reason || null
      )

      if (response.success) {
        setResult({
          type: 'success',
          data: response,
        })
        // Clear form fields on success
        setFormData({
          certificate_id: '',
          reason: '',
        })
      } else {
        setResult({
          type: 'error',
          message: response.message || 'Failed to revoke certificate',
        })
      }
    } catch (error) {
      setResult({
        type: 'error',
        message: extractErrorMessage(error),
      })
    } finally {
      setLoading(false)
    }
  }

  // ========================================================================
  // Conditional Rendering based on Authentication/Role
  // ========================================================================

  // Display message if not authenticated
  if (!isAuthenticated()) {
    return (
      <div className="card">
        <h2>
          <i className="fas fa-ban"></i> Revoke Certificate
        </h2>
        <div className="result error">
          Please login first to revoke certificates.
        </div>
      </div>
    )
  }

  // Display message if not an institution or admin
  if (!isInstitution()) {
    return (
      <div className="card">
        <h2>
          <i className="fas fa-ban"></i> Revoke Certificate
        </h2>
        <div className="result error">
          Only institutions and admins can revoke certificates.
        </div>
      </div>
    )
  }

  // ========================================================================
  // Render Method
  // ========================================================================

  return (
    <div className="card">
      <h2>
        <i className="fas fa-ban"></i> Revoke Certificate
      </h2>
      <form className="form" onSubmit={handleSubmit}>
        {/* Certificate ID Input */}
        <div className="form-group">
          <label htmlFor="revokeCertificateId">Certificate ID *</label>
          <input
            type="text"
            id="revokeCertificateId"
            required
            placeholder="Enter certificate ID to revoke"
            value={formData.certificate_id}
            onChange={(e) =>
              setFormData({ ...formData, certificate_id: e.target.value })
            }
          />
        </div>

        {/* Revocation Reason Input */}
        <div className="form-group">
          <label htmlFor="revocationReason">Revocation Reason (Optional)</label>
          <textarea
            id="revocationReason"
            rows="4"
            placeholder="Enter reason for revocation (e.g., 'Certificate issued in error', 'Student misconduct', etc.)"
            value={formData.reason}
            onChange={(e) =>
              setFormData({ ...formData, reason: e.target.value })
            }
          />
        </div>

        {/* Warning Message */}
        <div className="result error" style={{ marginBottom: '20px' }}>
          <strong>⚠️ Warning:</strong> Revoking a certificate marks it as invalid. 
          This action cannot be undone through the UI. The certificate will remain 
          on the blockchain (immutable record) but will show as revoked and invalid 
          during verification. Anyone verifying this certificate will see it as revoked.
        </div>

        {/* Submit Button */}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          <i className="fas fa-ban"></i>{' '}
          {loading ? 'Revoking...' : 'Revoke Certificate'}
        </button>
      </form>

      {/* Display API Result */}
      {result && (
        <div className={`result ${result.type}`}>
          {result.type === 'success' && result.data ? (
            <>
              <h3>✅ Certificate Revoked Successfully!</h3>
              <div className="certificate">
                <div className="certificate-details">
                  <div>
                    <strong>Certificate ID:</strong> {result.data.certificate_id}
                  </div>
                  {result.data.reason && (
                    <div>
                      <strong>Reason:</strong> {result.data.reason}
                    </div>
                  )}
                </div>
              </div>
              <p>
                <strong>Status:</strong> This certificate is now marked as revoked. 
                Verification will show it as invalid.
              </p>
            </>
          ) : (
            <div>❌ {result.message}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default RevokeCertificate

