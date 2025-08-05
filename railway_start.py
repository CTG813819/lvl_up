#!/usr/bin/env python3
"""
Railway deployment startup script
Uses main_unified.py to avoid import issues
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Railway environment setup
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Get port from Railway environment
PORT = int(os.environ.get("PORT", 8000))

def main():
    """Start the Railway server"""
    print("🚀 Starting Railway AI Backend Server...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🌐 Port: {PORT}")
    print(f"🐍 Python path: {sys.path[0]}")
    
    # Import the unified app
    try:
        from main_unified import app
        print("✅ Successfully imported unified app")
    except ImportError as e:
        print(f"❌ Failed to import unified app: {e}")
        print("📋 Available files in current directory:")
        for file in os.listdir("."):
            if file.endswith(".py"):
                print(f"  - {file}")
        return 1
    
    # Start the server
    try:
        print(f"🌐 Starting server on port {PORT}...")
        uvicorn.run(
            "main_unified:app",
            host="0.0.0.0",
            port=PORT,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 