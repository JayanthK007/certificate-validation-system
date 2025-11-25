from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .api import certificates, blockchain

# Create FastAPI app
app = FastAPI(
    title="Certificate Validation System",
    description="A blockchain-based system for issuing and verifying academic certificates",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(certificates.router)
app.include_router(blockchain.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Certificate Validation System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "certificates": "/certificates",
            "blockchain": "/blockchain"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Serve frontend files (if running in development)
@app.get("/frontend")
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "../../frontend/index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Frontend not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
