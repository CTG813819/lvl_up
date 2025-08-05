#!/usr/bin/env python3
"""
Startup script for the unified AI backend server
This uses main_unified.py to avoid import issues
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("LOG_LEVEL", "INFO")

def main():
    """Start the unified server"""
    print("🚀 Starting Unified AI Backend Server...")
    print(f"📁 Working directory: {os.getcwd()}")
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
        print("🌐 Starting server on port 8000...")
        uvicorn.run(
            "main_unified:app",
            host="0.0.0.0",
            port=8000,
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