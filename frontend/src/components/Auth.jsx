import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'

const Auth = () => {
  const { login, register } = useAuth()
  const [activeTab, setActiveTab] = useState('login')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [messageType, setMessageType] = useState(null)

  // Login form state
  const [loginData, setLoginData] = useState({
    username: '',
    password: '',
  })

  // Register form state
  const [registerData, setRegisterData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'student',
    issuer_id: '',
    issuer_name: '',
  })

  const showMessage = (msg, type) => {
    setMessage(msg)
    setMessageType(type)
    setTimeout(() => {
      setMessage(null)
      setMessageType(null)
    }, 5000)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    const result = await login(loginData.username, loginData.password)

    if (result.success) {
      showMessage('✅ Login successful!', 'success')
      setLoginData({ username: '', password: '' })
    } else {
      showMessage(`❌ ${result.error}`, 'error')
    }

    setLoading(false)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    // Build user data object, only including issuer fields for institutions
    const userData = {
      username: registerData.username,
      email: registerData.email,
      password: registerData.password,
      role: registerData.role,
    }
    
    // Only include issuer_id and issuer_name for institutions
    // Convert empty strings to null to match backend Optional[str] type
    if (registerData.role === 'institution') {
      userData.issuer_id = registerData.issuer_id?.trim() || null
      userData.issuer_name = registerData.issuer_name?.trim() || null
    }

    // Register the user
    const registerResult = await register(userData)

    if (registerResult.success) {
      // After successful registration, automatically log in the user
      showMessage('✅ Registration successful! Logging you in...', 'success')
      
      // Automatically log in with the same credentials
      const loginResult = await login(registerData.username, registerData.password)
      
      if (loginResult.success) {
        // Login successful - user is now authenticated
        showMessage('✅ Registration and login successful!', 'success')
        // Clear registration form
        setRegisterData({
          username: '',
          email: '',
          password: '',
          role: 'student',
          issuer_id: '',
          issuer_name: '',
        })
        // Note: Don't switch to login tab - user is already logged in
        // The App component will handle navigation based on user role
      } else {
        // Registration succeeded but login failed
        showMessage(`✅ Registration successful! However, login failed: ${loginResult.error}. Please login manually.`, 'error')
        setActiveTab('login')
        // Pre-fill the login form with the username
        setLoginData({
          username: registerData.username,
          password: '',
        })
      }
    } else {
      // Registration failed
      showMessage(`❌ ${registerResult.error}`, 'error')
    }

    setLoading(false)
  }

  return (
    <div className="card">
      <h2>
        <i className="fas fa-sign-in-alt"></i> Authentication
      </h2>

      <div className="auth-tabs">
        <button
          className={`auth-tab-btn ${activeTab === 'login' ? 'active' : ''}`}
          onClick={() => setActiveTab('login')}
        >
          Login
        </button>
        <button
          className={`auth-tab-btn ${activeTab === 'register' ? 'active' : ''}`}
          onClick={() => setActiveTab('register')}
        >
          Register
        </button>
      </div>

      {/* Login Form */}
      {activeTab === 'login' && (
        <form className="form auth-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="loginUsername">Username *</label>
            <input
              type="text"
              id="loginUsername"
              required
              placeholder="Enter username"
              value={loginData.username}
              onChange={(e) =>
                setLoginData({ ...loginData, username: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="loginPassword">Password *</label>
            <input
              type="password"
              id="loginPassword"
              required
              placeholder="Enter password"
              value={loginData.password}
              onChange={(e) =>
                setLoginData({ ...loginData, password: e.target.value })
              }
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <i className="fas fa-sign-in-alt"></i>{' '}
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      )}

      {/* Register Form */}
      {activeTab === 'register' && (
        <form className="form auth-form" onSubmit={handleRegister}>
          <div className="form-group">
            <label htmlFor="regUsername">Username *</label>
            <input
              type="text"
              id="regUsername"
              required
              placeholder="Enter username"
              value={registerData.username}
              onChange={(e) =>
                setRegisterData({ ...registerData, username: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="regEmail">Email *</label>
            <input
              type="email"
              id="regEmail"
              required
              placeholder="Enter email"
              value={registerData.email}
              onChange={(e) =>
                setRegisterData({ ...registerData, email: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="regPassword">Password *</label>
            <input
              type="password"
              id="regPassword"
              required
              placeholder="Enter password"
              value={registerData.password}
              onChange={(e) =>
                setRegisterData({ ...registerData, password: e.target.value })
              }
            />
          </div>
          <div className="form-group">
            <label htmlFor="regRole">Role *</label>
            <select
              id="regRole"
              required
              value={registerData.role}
              onChange={(e) =>
                setRegisterData({ ...registerData, role: e.target.value })
              }
            >
              <option value="student">Student</option>
              <option value="institution">Institution</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          {registerData.role === 'institution' && (
            <>
              <div className="form-group">
                <label htmlFor="regIssuerId">Issuer ID *</label>
                <input
                  type="text"
                  id="regIssuerId"
                  required
                  placeholder="Enter institution ID"
                  value={registerData.issuer_id}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      issuer_id: e.target.value,
                    })
                  }
                />
              </div>
              <div className="form-group">
                <label htmlFor="regIssuerName">Issuer Name *</label>
                <input
                  type="text"
                  id="regIssuerName"
                  required
                  placeholder="Enter institution name"
                  value={registerData.issuer_name}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      issuer_name: e.target.value,
                    })
                  }
                />
              </div>
            </>
          )}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <i className="fas fa-user-plus"></i>{' '}
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>
      )}

      {message && (
        <div className={`result ${messageType}`} style={{ marginTop: '20px' }}>
          {message}
        </div>
      )}
    </div>
  )
}

export default Auth

