#!/usr/bin/env python3
"""
Simple Single Process Uvicorn Wrapper
Ensures only one uvicorn process runs without complex monitoring
"""

import os
import sys
import subprocess
import time
import psutil
from pathlib import Path

def kill_existing_uvicorn():
    """Kill any existing uvicorn processes"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                print(f"🔪 Killing existing uvicorn process: {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

def main():
    # Kill any existing uvicorn processes
    kill_existing_uvicorn()
    
    # Wait a moment for processes to fully terminate
    time.sleep(2)
    
    # Get the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Set environment variables for single process
    env = os.environ.copy()
    env['UVICORN_WORKERS'] = '1'
    env['PYTHONPATH'] = str(script_dir)
    
    # Build uvicorn command with explicit single process settings
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--workers', '1',  # Explicitly set to 1
        '--loop', 'asyncio',  # Use asyncio instead of uvloop to avoid conflicts
        '--reload', 'false',  # Disable reload to prevent multiple processes
        '--log-level', 'info'
    ]
    
    print(f"🚀 Starting uvicorn with single process: {' '.join(cmd)}")
    
    # Start uvicorn process and replace current process
    os.execv(sys.executable, [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--workers', '1', '--loop', 'asyncio', '--reload', 'false', '--log-level', 'info'])

if __name__ == "__main__":
    main() 