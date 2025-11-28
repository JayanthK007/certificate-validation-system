/**
 * API Service Layer
 * 
 * This module provides a centralized API client for communicating with the backend.
 * It uses Axios for HTTP requests and includes:
 * - Request interceptors for JWT token injection
 * - Response interceptors for error handling (401 unauthorized)
 * - Organized API methods grouped by feature (auth, certificates, blockchain)
 * 
 * Features:
 * - Automatic JWT token injection from localStorage
 * - Automatic token cleanup on 401 errors
 * - Base URL configuration via environment variable
 * - Consistent error handling
 */

import axios from 'axios'

// ============================================================================
// Error Message Extraction Helper
// ============================================================================

/**
 * Extract error message from FastAPI error response
 * 
 * FastAPI returns errors in different formats:
 * - Validation errors (422): Array of objects with 'loc', 'msg', 'type'
 * - Single errors: String message
 * - Other errors: Object with 'detail' field
 * 
 * @param {Error} error - Axios error object
 * @returns {string} - Human-readable error message
 */
export const extractErrorMessage = (error) => {
  // Check if error has response data
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail
    
    // If detail is an array (validation errors)
    if (Array.isArray(detail)) {
      return detail
        .map(err => {
          // Format: "field_name: error message"
          const field = err.loc && err.loc.length > 1 
            ? err.loc[err.loc.length - 1] 
            : 'field'
          return `${field}: ${err.msg || JSON.stringify(err)}`
        })
        .join(', ')
    }
    
    // If detail is a string
    if (typeof detail === 'string') {
      return detail
    }
    
    // If detail is an object, try to stringify it
    return JSON.stringify(detail)
  }
  
  // Fallback to error message
  if (error.message) {
    return error.message
  }
  
  // Final fallback
  return 'An unexpected error occurred'
}

// ============================================================================
// API Configuration
// ============================================================================

/**
 * Base URL for API requests
 * 
 * Uses environment variable VITE_API_BASE if set, otherwise defaults to
 * localhost:8000 (FastAPI default port).
 * 
 * To change in production, set VITE_API_BASE in .env file:
 * VITE_API_BASE=https://api.yourdomain.com
 */
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// ============================================================================
// Axios Instance Setup
// ============================================================================

/**
 * Create Axios instance with base configuration
 * 
 * This instance is used for all API requests. It includes:
 * - Base URL for all requests
 * - Default headers (Content-Type: application/json)
 */
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// Request Interceptor: JWT Token Injection
// ============================================================================

/**
 * Request Interceptor: Automatically add JWT token to requests
 * 
 * This interceptor runs before every API request and:
 * 1. Checks if a token exists in localStorage
 * 2. If token exists, adds it to the Authorization header
 * 3. Format: "Bearer <token>"
 * 
 * This ensures authenticated requests automatically include the token
 * without manually adding it to each request.
 */
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage (set during login)
    const token = localStorage.getItem('authToken')
    
    // If token exists, add it to Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    // If request setup fails, reject the promise
    return Promise.reject(error)
  }
)

// ============================================================================
// Response Interceptor: Error Handling
// ============================================================================

/**
 * Response Interceptor: Handle 401 Unauthorized errors
 * 
 * This interceptor runs after every API response and:
 * 1. Checks if response status is 401 (Unauthorized)
 * 2. If 401, clears authentication data from localStorage
 * 3. Redirects user to home page (forces re-login)
 * 
 * This handles cases where:
 * - Token has expired
 * - Token is invalid
 * - User has been logged out server-side
 */
api.interceptors.response.use(
  (response) => {
    // Successful response - pass through unchanged
    return response
  },
  (error) => {
    // Check if error is 401 Unauthorized
    if (error.response?.status === 401) {
      // Clear authentication data
      localStorage.removeItem('authToken')
      localStorage.removeItem('currentUser')
      
      // Redirect to home page (triggers login screen)
      window.location.href = '/'
    }
    
    // Reject the promise with the error
    return Promise.reject(error)
  }
)

// ============================================================================
// Authentication API Methods
// ============================================================================

/**
 * Authentication API Methods
 * 
 * These methods handle user authentication operations:
 * - Registration
 * - Login
 * - Get current user info
 * - Logout
 */
export const authAPI = {
  /**
   * Register a new user account
   * 
   * @param {Object} userData - User registration data
   * @param {string} userData.username - Username
   * @param {string} userData.email - Email address
   * @param {string} userData.password - Password
   * @param {string} userData.role - User role (admin, institution, student)
   * @param {string} [userData.issuer_id] - Institution ID (required for institutions)
   * @param {string} [userData.issuer_name] - Institution name (required for institutions)
   * @returns {Promise<Object>} Registration result
   */
  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  /**
   * Login with username and password
   * 
   * Uses OAuth2 password form format (multipart/form-data) as required by FastAPI.
   * 
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} Login result with access_token
   */
  login: async (username, password) => {
    // OAuth2 requires form data format
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Get current authenticated user information
   * 
   * Requires valid JWT token in Authorization header.
   * 
   * @returns {Promise<Object>} Current user data
   */
  getMe: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * Logout (optional backend call)
   * 
   * Note: With JWT tokens, logout is primarily client-side (removing token).
   * This endpoint is called for consistency, but the main logout logic
   * is handled by clearing localStorage in the AuthContext.
   * 
   * @returns {Promise<Object>} Logout confirmation
   */
  logout: async () => {
    const response = await api.post('/auth/logout')
    return response.data
  },
}

// ============================================================================
// Certificate API Methods
// ============================================================================

/**
 * Certificate API Methods
 * 
 * These methods handle certificate operations:
 * - Issue certificates (requires authentication)
 * - Verify certificates (public)
 * - Query certificates by student or issuer
 * - Revoke certificates (requires authentication)
 */
export const certificateAPI = {
  /**
   * Issue a new certificate
   * 
   * Requires authentication (institution/admin role).
   * 
   * @param {Object} certificateData - Certificate data
   * @param {string} certificateData.student_name - Student's full name
   * @param {string} certificateData.student_id - Student identifier
   * @param {string} certificateData.course_name - Course name
   * @param {string} certificateData.grade - Student's grade
   * @param {string} [certificateData.course_duration] - Course duration
   * @returns {Promise<Object>} Issued certificate data
   */
  issue: async (certificateData) => {
    const response = await api.post('/certificates/issue', certificateData)
    return response.data
  },

  /**
   * Verify a certificate
   * 
   * Public endpoint - no authentication required.
   * Verifies certificate authenticity using blockchain and ECDSA signature.
   * 
   * @param {string} certificateId - Certificate ID to verify
   * @returns {Promise<Object>} Verification result
   */
  verify: async (certificateId) => {
    const response = await api.post('/certificates/verify', {
      certificate_id: certificateId,
    })
    return response.data
  },

  /**
   * Get all certificates for a specific student
   * 
   * Public endpoint - no authentication required.
   * 
   * @param {string} studentId - Student identifier
   * @returns {Promise<Object>} Student's certificates
   */
  getByStudent: async (studentId) => {
    const response = await api.get(`/certificates/student/${studentId}`)
    return response.data
  },

  /**
   * Get all certificates issued by a specific institution
   * 
   * Public endpoint - no authentication required.
   * 
   * @param {string} issuerId - Institution identifier
   * @returns {Promise<Object>} Institution's certificates
   */
  getByIssuer: async (issuerId) => {
    const response = await api.get(`/certificates/issuer/${issuerId}`)
    return response.data
  },

  /**
   * Revoke a certificate
   * 
   * Requires authentication (institution/admin role).
   * Only the issuing institution or admin can revoke.
   * 
   * @param {string} certificateId - Certificate ID to revoke
   * @param {string} [reason] - Optional revocation reason
   * @returns {Promise<Object>} Revocation result
   */
  revoke: async (certificateId, reason) => {
    const response = await api.post('/certificates/revoke', {
      certificate_id: certificateId,
      reason,
    })
    return response.data
  },

  /**
   * Get all certificates (for demo/development)
   * 
   * Public endpoint - no authentication required.
   * 
   * @returns {Promise<Object>} All certificates
   */
  getAll: async () => {
    const response = await api.get('/certificates/all')
    return response.data
  },
}

// ============================================================================
// Blockchain API Methods
// ============================================================================

/**
 * Blockchain API Methods
 * 
 * These methods provide blockchain information and validation:
 * - Get blockchain statistics
 * - Validate blockchain integrity
 * - Get block information
 */
export const blockchainAPI = {
  /**
   * Get blockchain statistics and information
   * 
   * Public endpoint - no authentication required.
   * 
   * @returns {Promise<Object>} Blockchain statistics
   */
  getInfo: async () => {
    const response = await api.get('/blockchain/info')
    return response.data
  },

  /**
   * Validate blockchain integrity
   * 
   * Public endpoint - no authentication required.
   * Validates the entire blockchain chain for integrity.
   * 
   * @returns {Promise<Object>} Validation result
   */
  validate: async () => {
    const response = await api.get('/blockchain/validate')
    return response.data
  },

  /**
   * Get all blocks in the blockchain
   * 
   * Public endpoint - no authentication required.
   * 
   * @returns {Promise<Object>} All blocks
   */
  getBlocks: async () => {
    const response = await api.get('/blockchain/blocks')
    return response.data
  },

  /**
   * Get the latest block in the blockchain
   * 
   * Public endpoint - no authentication required.
   * 
   * @returns {Promise<Object>} Latest block information
   */
  getLatestBlock: async () => {
    const response = await api.get('/blockchain/latest-block')
    return response.data
  },
}

// ============================================================================
// Default Export
// ============================================================================

/**
 * Default export: Axios instance
 * 
 * Can be used directly for custom API calls if needed.
 */
export default api
