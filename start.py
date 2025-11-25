#!/usr/bin/env python3
"""
Certificate Validation System - Startup Script
This script helps you start the backend server easily.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Start the server using uvicorn with proper import string
        subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
        
        print("✅ Backend server started!")
        print("🌐 API available at: http://localhost:8000")
        print("📚 API docs available at: http://localhost:8000/docs")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def open_frontend():
    """Open the frontend in the browser"""
    print("🌐 Opening frontend...")
    frontend_path = Path("frontend/index.html").absolute()
    
    if frontend_path.exists():
        webbrowser.open(f"file://{frontend_path}")
        print("✅ Frontend opened in browser!")
        return True
    else:
        print("❌ Frontend file not found!")
        return False

def main():
    """Main startup function"""
    print("🎓 Certificate Validation System")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Start backend
    if not start_backend():
        return
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Open frontend
    open_frontend()
    
    print("\n🎉 System is ready!")
    print("=" * 40)
    print("📋 What you can do:")
    print("1. Issue certificates using the web interface")
    print("2. Verify certificates instantly")
    print("3. View student portfolios")
    print("4. Check blockchain information")
    print("\n💡 Tips:")
    print("- Use the API docs at http://localhost:8000/docs")
    print("- Check the README.md for detailed instructions")
    print("- Press Ctrl+C to stop the server")
    
    try:
        # Keep the script running
        print("\n🔄 Server is running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        print("✅ Certificate Validation System stopped!")

if __name__ == "__main__":
    main()
