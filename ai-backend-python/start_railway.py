#!/usr/bin/env python3
"""
Railway-specific startup script for AI Backend
Handles PORT environment variable validation and startup
"""

import os
import sys
import subprocess

def validate_port(port_str):
    """Validate and convert port string to integer"""
    try:
        port = int(port_str)
        if 1 <= port <= 65535:
            return port
        else:
            print(f"❌ Port {port} out of valid range (1-65535)")
            return None
    except (ValueError, TypeError):
        print(f"❌ Invalid port value: '{port_str}' - not a number")
        return None

def main():
    print("🚀 Starting Railway AI Backend with main_unified.py...")
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Get and validate PORT environment variable
    port_env = os.environ.get('PORT')
    print(f"🌍 Environment PORT: {port_env}")
    
    if port_env:
        port = validate_port(port_env)
        if port is None:
            print("🔧 Using default port 8000 due to invalid PORT env var")
            port = 8000
    else:
        print("🔧 PORT not set, using default: 8000")
        port = 8000
    
    print(f"🔧 Final port: {port}")
    
    # Check if main_unified.py exists
    if not os.path.exists('main_unified.py'):
        print("❌ main_unified.py not found!")
        print("📋 Python files in directory:")
        for file in os.listdir('.'):
            if file.endswith('.py'):
                print(f"   - {file}")
        sys.exit(1)
    
    print("✅ Found main_unified.py")
    
    # Set environment variables
    os.environ['PORT'] = str(port)
    os.environ['PYTHONPATH'] = os.getcwd()
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'main_unified:app', 
        '--host', '0.0.0.0', 
        '--port', str(port)
    ]
    
    print(f"🌐 Starting server: {' '.join(cmd)}")
    
    try:
        # Use exec to replace the current process
        os.execvp(sys.executable, cmd)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()