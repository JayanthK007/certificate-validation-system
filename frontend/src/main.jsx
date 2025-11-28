/**
 * React Application Entry Point
 * 
 * This is the main entry point for the React application. It:
 * - Renders the root App component
 * - Wraps the app in React.StrictMode for development warnings
 * - Mounts the React application to the DOM
 * 
 * The application is served by Vite, which handles hot module replacement
 * and development server functionality.
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Get the root DOM element (defined in index.html)
const rootElement = document.getElementById('root')

// Create React root and render the application
ReactDOM.createRoot(rootElement).render(
  // StrictMode enables additional checks and warnings in development
  // It helps identify potential problems in the application
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
