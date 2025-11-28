/**
 * Authentication Context Provider
 * 
 * This module provides React Context for managing authentication state
 * throughout the application. It handles:
 * - User login and registration
 * - JWT token management (storage and retrieval)
 * - User session persistence (localStorage)
 * - Authentication state (logged in/out, user role)
 * - Automatic token validation on app load
 * 
 * Usage:
 *   const { user, login, logout, isAuthenticated } = useAuth()
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI, extractErrorMessage } from '../services/api'

// ============================================================================
// Context Creation
// ============================================================================

/**
 * Create Authentication Context
 * 
 * This context will hold the authentication state and functions.
 * Components can access it via the useAuth hook.
 */
const AuthContext = createContext(null)

// ============================================================================
// useAuth Hook
// ============================================================================

/**
 * Custom hook to access authentication context
 * 
 * This hook provides a convenient way to access authentication state
 * and functions from any component. It throws an error if used outside
 * of an AuthProvider.
 * 
 * @returns {Object} Authentication context value
 * @throws {Error} If used outside AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

// ============================================================================
// AuthProvider Component
// ============================================================================

/**
 * Authentication Provider Component
 * 
 * This component provides authentication state and functions to all
 * child components via React Context. It manages:
 * - User state (current user data)
 * - Token state (JWT token)
 * - Loading state (during initialization)
 * - Login, register, and logout functions
 * - Authentication status checks
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const AuthProvider = ({ children }) => {
  // ========================================================================
  // State Management
  // ========================================================================
  
  /**
   * Current user data (from API)
   * Contains: id, username, email, role, issuer_id, issuer_name, etc.
   */
  const [user, setUser] = useState(null)
  
  /**
   * JWT authentication token
   * Retrieved from localStorage on mount, set during login
   */
  const [token, setToken] = useState(localStorage.getItem('authToken'))
  
  /**
   * Loading state during authentication initialization
   * Prevents rendering before auth state is determined
   */
  const [loading, setLoading] = useState(true)

  // ========================================================================
  // Effect: Initialize Authentication on Mount
  // ========================================================================
  
  /**
   * Effect: Initialize authentication state on component mount
   * 
   * This effect runs once when the component mounts and:
   * 1. Checks localStorage for stored token and user data
   * 2. If found, validates the token by calling /auth/me
   * 3. If token is valid, sets user state
   * 4. If token is invalid, clears storage and logs out
   * 5. Sets loading to false when done
   */
  useEffect(() => {
    const initAuth = async () => {
      // Get stored authentication data
      const storedToken = localStorage.getItem('authToken')
      const storedUser = localStorage.getItem('currentUser')

      // If we have stored data, try to restore session
      if (storedToken && storedUser) {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
        
        // Verify token is still valid by calling API
        try {
          const userData = await authAPI.getMe()
          setUser(userData)
          localStorage.setItem('currentUser', JSON.stringify(userData))
        } catch (error) {
          // Token is invalid or expired, clear storage
          logout()
        }
      }
      
      // Mark initialization as complete
      setLoading(false)
    }

    initAuth()
  }, [])  // Empty dependency array: run only on mount

  // ========================================================================
  // Authentication Functions
  // ========================================================================
  
  /**
   * Login function
   * 
   * Authenticates user with username and password, then:
   * 1. Calls login API endpoint
   * 2. Stores JWT token in localStorage
   * 3. Fetches user data from /auth/me
   * 4. Stores user data in localStorage
   * 5. Updates state with token and user
   * 
   * @param {string} username - Username
   * @param {string} password - Password
   * @returns {Promise<Object>} Result object with success status and optional error
   */
  const login = async (username, password) => {
    try {
      // Call login API endpoint
      const result = await authAPI.login(username, password)
      const token = result.access_token
      
      // Store token in localStorage
      localStorage.setItem('authToken', token)
      setToken(token)

      // Fetch and store user data
      const userData = await authAPI.getMe()
      localStorage.setItem('currentUser', JSON.stringify(userData))
      setUser(userData)

      return { success: true }
    } catch (error) {
      // Extract error message using helper function
      return {
        success: false,
        error: extractErrorMessage(error) || 'Login failed',
      }
    }
  }

  /**
   * Register function
   * 
   * Registers a new user account. After successful registration,
   * user must log in separately.
   * 
   * @param {Object} userData - Registration data
   * @param {string} userData.username - Username
   * @param {string} userData.email - Email address
   * @param {string} userData.password - Password
   * @param {string} userData.role - User role (admin, institution, student)
   * @param {string} [userData.issuer_id] - Institution ID (for institutions)
   * @param {string} [userData.issuer_name] - Institution name (for institutions)
   * @returns {Promise<Object>} Result object with success status and optional error
   */
  const register = async (userData) => {
    try {
      await authAPI.register(userData)
      return { success: true }
    } catch (error) {
      // Extract error message using helper function
      return {
        success: false,
        error: extractErrorMessage(error) || 'Registration failed',
      }
    }
  }

  /**
   * Logout function
   * 
   * Logs out the current user by:
   * 1. Optionally calling backend logout endpoint
   * 2. Clearing token and user from localStorage
   * 3. Clearing token and user from state
   * 
   * Note: With JWT tokens, logout is primarily client-side. The backend
   * call is optional but good practice for consistency.
   */
  const logout = async () => {
    try {
      // Call backend logout endpoint (optional, but good practice)
      if (token) {
        await authAPI.logout()
      }
    } catch (error) {
      // Even if backend call fails, clear local storage
      console.error('Logout error:', error)
    } finally {
      // Always clear local storage and state
      localStorage.removeItem('authToken')
      localStorage.removeItem('currentUser')
      setToken(null)
      setUser(null)
    }
  }

  // ========================================================================
  // Authentication Status Checks
  // ========================================================================
  
  /**
   * Check if user is authenticated
   * 
   * @returns {boolean} True if user has valid token and user data
   */
  const isAuthenticated = () => {
    return !!token && !!user
  }

  /**
   * Check if user is an institution or admin
   * 
   * Used to determine if user can access institution-only features
   * (like issuing certificates).
   * 
   * @returns {boolean} True if user role is 'institution' or 'admin'
   */
  const isInstitution = () => {
    return user?.role === 'institution' || user?.role === 'admin'
  }

  // ========================================================================
  // Context Value
  // ========================================================================
  
  /**
   * Context value object
   * 
   * This object is provided to all child components via Context.
   * It includes all state and functions needed for authentication.
   */
  const value = {
    user,              // Current user data
    token,             // JWT token
    loading,           // Loading state
    login,             // Login function
    register,          // Register function
    logout,            // Logout function
    isAuthenticated,   // Check if authenticated
    isInstitution,     // Check if institution/admin
  }

  // ========================================================================
  // Render
  // ========================================================================
  
  /**
   * Render AuthProvider with context value
   * 
   * Wraps children with AuthContext.Provider to make authentication
   * state and functions available to all descendants.
   */
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
