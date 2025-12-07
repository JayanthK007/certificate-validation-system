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
from dotenv import load_dotenv

load_dotenv()

from .api import certificates, blockchain, auth

from .database import init_db

app = FastAPI(
    title="Certificate Validation System",
    description="A blockchain-based system for issuing and verifying academic certificates",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

app.include_router(auth.router)

app.include_router(certificates.router)

app.include_router(blockchain.router)

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
        "docs": "/docs",
        "endpoints": {
            "certificates": "/certificates",
            "blockchain": "/blockchain",
            "authentication": "/auth"
        }
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
