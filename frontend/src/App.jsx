/**
 * Main Application Component
 * 
 * This is the root component of the Certificate Validation System frontend.
 * It manages:
 * - Application-wide authentication state (via AuthProvider)
 * - Tab-based navigation between different features
 * - Conditional rendering based on user authentication and role
 * - Header with authentication status and logout functionality
 * 
 * Component Structure:
 * - AuthProvider: Wraps entire app to provide authentication context
 * - AppContent: Main application content with navigation and routing
 * - Header: Logo, authentication status, and navigation tabs
 * - Main Content: Conditionally rendered based on active tab
 * - Footer: Application footer
 */

import React, { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import Auth from './components/Auth'
import IssueCertificate from './components/IssueCertificate'
import VerifyCertificate from './components/VerifyCertificate'
import StudentPortfolio from './components/StudentPortfolio'
import BlockchainInfo from './components/BlockchainInfo'
import RevokeCertificate from './components/RevokeCertificate'
import EthereumConnect from './components/EthereumConnect'
import DirectEthereumVerify from './components/DirectEthereumVerify'
import './index.css'

/**
 * Main Application Content Component
 * 
 * This component contains the actual application UI and logic.
 * It uses the AuthContext to access authentication state and functions.
 */
const AppContent = () => {
  // Get authentication state and functions from context
  const { user, logout, isAuthenticated, isInstitution } = useAuth()
  
  // State for managing active tab/section
  const [activeTab, setActiveTab] = useState('login')

  /**
   * Effect: Set initial tab based on authentication status
   * 
   * When the component mounts or authentication state changes:
   * - If authenticated as institution/admin: show 'issue' tab
   * - If authenticated as student: show 'verify' tab
   * - If not authenticated: show 'login' tab
   */
  useEffect(() => {
    if (isAuthenticated()) {
      if (isInstitution()) {
        setActiveTab('issue')  // Institutions see issue tab first
      } else {
        setActiveTab('verify')  // Students see verify tab first
      }
    } else {
      setActiveTab('login')  // Not authenticated: show login
    }
  }, [user, isAuthenticated, isInstitution]) // Include 'user' to react to auth state changes

  /**
   * Navigation Tabs Configuration
   * 
   * Defines all available tabs with their labels and icons.
   * The 'issue' tab is filtered out for non-institution users.
   */
  // Get Ethereum config from environment or use defaults
  const ethereumContractAddress = import.meta.env.VITE_ETHEREUM_CONTRACT_ADDRESS || ''
  const ethereumNetwork = import.meta.env.VITE_ETHEREUM_NETWORK || 'sepolia'
  const useEthereum = import.meta.env.VITE_USE_ETHEREUM === 'true' || ethereumContractAddress !== ''

  const tabs = [
    { id: 'login', label: 'Login/Register', icon: 'fas fa-sign-in-alt' },
    { id: 'issue', label: 'Issue Certificate', icon: 'fas fa-graduation-cap' },
    { id: 'revoke', label: 'Revoke Certificate', icon: 'fas fa-ban' },
    { id: 'verify', label: 'Verify Certificate', icon: 'fas fa-search' },
    ...(useEthereum ? [{ id: 'ethereum', label: 'Ethereum Direct', icon: 'fab fa-ethereum' }] : []),
    { id: 'student', label: 'Student Portfolio', icon: 'fas fa-user-graduate' },
    { id: 'blockchain', label: 'Blockchain Info', icon: 'fas fa-link' },
  ]

  return (
    <div className="container">
      {/* ==================================================================== */}
      {/* Header Section */}
      {/* ==================================================================== */}
      <header className="header">
        {/* Logo and Title */}
        <div className="logo">
          <i className="fas fa-certificate"></i>
          <h1>Certificate Validation System</h1>
        </div>

        {/* Header Content: Auth Status and Navigation */}
        <div className="header-content">
          {/* Authentication Status Section */}
          <div className="auth-section">
            <div className="auth-status">
              {/* Display current user or "Not logged in" */}
              <span>
                {isAuthenticated()
                  ? `Logged in as: ${user?.username} (${user?.role})`
                  : 'Not logged in'}
              </span>
              
              {/* Logout Button (only shown when authenticated) */}
              {isAuthenticated() && (
                <button className="btn btn-small btn-secondary" onClick={logout}>
                  Logout
                </button>
              )}
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="nav">
            {tabs
              // Filter tabs based on user authentication and role
              // 'login' tab is only visible when NOT authenticated
              // 'issue' and 'revoke' tabs are only visible to institutions/admins
              .filter((tab) => {
                // Hide login tab when authenticated
                if (tab.id === 'login') {
                  return !isAuthenticated()  // Only show login when not authenticated
                }
                // Filter issue and revoke tabs for institutions/admins only
                if (tab.id === 'issue' || tab.id === 'revoke') {
                  return isInstitution()  // Only institutions/admins can issue/revoke/mine
                }
                return true  // All other tabs are visible to everyone
              })
              // Render navigation buttons
              .map((tab) => (
                <button
                  key={tab.id}
                  className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
          </nav>
        </div>
      </header>

      {/* ==================================================================== */}
      {/* Main Content Section */}
      {/* ==================================================================== */}
      <main className="main-content">
        {/* Conditionally render component based on active tab */}
        {/* Only show Auth component when not authenticated */}
        {activeTab === 'login' && !isAuthenticated() && <Auth />}
        {activeTab === 'issue' && <IssueCertificate />}
        {activeTab === 'revoke' && <RevokeCertificate />}
        {activeTab === 'verify' && <VerifyCertificate />}
        {activeTab === 'ethereum' && useEthereum && (
          <div>
            <EthereumConnect 
              contractAddress={ethereumContractAddress}
              networkName={ethereumNetwork}
              onConnected={(address) => {
                console.log('Ethereum wallet connected:', address)
              }}
            />
            <DirectEthereumVerify 
              contractAddress={ethereumContractAddress}
              networkName={ethereumNetwork}
            />
          </div>
        )}
        {activeTab === 'student' && <StudentPortfolio />}
        {activeTab === 'blockchain' && <BlockchainInfo />}
      </main>

      {/* ==================================================================== */}
      {/* Footer Section */}
      {/* ==================================================================== */}
      <footer className="footer">
        <p>&copy; 2024 Certificate Validation System. Built with Blockchain Technology.</p>
      </footer>
    </div>
  )
}

/**
 * Root App Component
 * 
 * This component wraps the entire application with the AuthProvider,
 * which provides authentication context to all child components.
 * 
 * The AuthProvider must wrap the app so that all components can access
 * authentication state and functions via the useAuth hook.
 */
const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
