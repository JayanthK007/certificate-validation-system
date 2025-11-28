"""
FastAPI Application Main Module

This is the main entry point for the Certificate Validation System API.
It sets up the FastAPI application, configures middleware, registers routes,
and initializes the database.

The application provides:
- RESTful API endpoints for certificate management
- JWT-based authentication
- Blockchain-based certificate storage
- ECDSA digital signatures
- Privacy-preserving certificate verification
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Import API routers
from .api import certificates, blockchain, auth

# Import database initialization function
from .database import init_db

# ============================================================================
# FastAPI Application Instance
# ============================================================================

# Create FastAPI application with metadata
app = FastAPI(
    title="Certificate Validation System",
    description="A blockchain-based system for issuing and verifying academic certificates",
    version="1.0.0"
)

# ============================================================================
# CORS Middleware Configuration
# ============================================================================

# Enable Cross-Origin Resource Sharing (CORS) for frontend communication
# This allows the React frontend (running on different port) to make API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins (e.g., ["https://yourdomain.com"])
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (including Authorization)
)

# ============================================================================
# Application Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    This function runs once when the FastAPI application starts.
    It initializes the database by creating all necessary tables
    if they don't already exist.
    
    Note:
        - Safe to call multiple times (idempotent)
        - Only creates missing tables, doesn't modify existing ones
    """
    init_db()

# ============================================================================
# API Route Registration
# ============================================================================

# Register API routers - these handle different groups of endpoints
# Each router is prefixed and tagged for organization in API docs

# Authentication endpoints (login, register, logout, user info)
app.include_router(auth.router)

# Certificate management endpoints (issue, verify, revoke, query)
app.include_router(certificates.router)

# Blockchain information endpoints (info, validation, blocks)
app.include_router(blockchain.router)

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - provides API information and available endpoints.
    
    Returns:
        dict: API metadata including version, documentation links, and endpoint groups
    """
    return {
        "message": "Certificate Validation System API",
        "version": "1.0.0",
        "docs": "/docs",  # Swagger UI documentation
        "endpoints": {
            "certificates": "/certificates",
            "blockchain": "/blockchain",
            "authentication": "/auth"
        }
    }

# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint can be used by monitoring tools, load balancers, or
    orchestration systems to check if the API is running and healthy.
    
    Returns:
        dict: Health status information
    """
    return {"status": "healthy", "message": "API is running"}

# ============================================================================
# Development Notes
# ============================================================================

# Note: In production, serve React build files through a web server like Nginx
# For development, React app runs on Vite dev server (port 3000)

# ============================================================================
# Application Entry Point (for direct execution)
# ============================================================================

if __name__ == "__main__":
    # Run the application using uvicorn
    # This is used when running: python -m app.main
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
