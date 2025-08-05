#!/usr/bin/env python3
"""
Script to restart the backend with logging and rate limiting fixes
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def main():
    print("🔄 Restarting backend with logging and rate limiting fixes...")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    try:
        # Stop any running backend processes
        print("🛑 Stopping existing backend processes...")
        subprocess.run(["pkill", "-f", "uvicorn"], check=False)
        subprocess.run(["pkill", "-f", "main.py"], check=False)
        time.sleep(2)
        
        # Start the backend
        print("🚀 Starting backend with fixes...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Backend stopped by user")
    except Exception as e:
        print(f"❌ Error restarting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 