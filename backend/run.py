#!/usr/bin/env python3
"""
Certificate Validation System - Backend Runner
Simple script to start the FastAPI backend server
"""

import uvicorn
import sys
import os

def main():
    """Start the FastAPI server"""
    print("🎓 Certificate Validation System - Backend")
    print("=" * 50)
    print("🚀 Starting FastAPI server...")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔄 Hot reload enabled for development")
    print("=" * 50)
    
    try:
        # Run the FastAPI app with uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
        print("✅ Server stopped successfully!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
