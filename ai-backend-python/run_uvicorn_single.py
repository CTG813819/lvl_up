#!/usr/bin/env python3
"""
Single Process Uvicorn Wrapper
Ensures only one uvicorn process runs to prevent PID conflicts
"""

import os
import sys
import signal
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

def check_port_available(port=8000):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def main():
    # Kill any existing uvicorn processes
    kill_existing_uvicorn()
    
    # Wait a moment for processes to fully terminate
    time.sleep(2)
    
    # Check if port is available
    if not check_port_available(8000):
        print("❌ Port 8000 is still in use. Waiting...")
        time.sleep(5)
        if not check_port_available(8000):
            print("❌ Port 8000 still in use after waiting. Exiting.")
            sys.exit(1)
    
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
    
    try:
        # Start uvicorn process
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"✅ Uvicorn started with PID: {process.pid}")
        
        # Monitor the process
        while True:
            if process.poll() is not None:
                print(f"❌ Uvicorn process exited with code: {process.returncode}")
                break
            
            # Check if there are multiple uvicorn processes
            uvicorn_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                        uvicorn_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if len(uvicorn_processes) > 1:
                print(f"⚠️  Multiple uvicorn processes detected: {uvicorn_processes}")
                print("🔪 Terminating all uvicorn processes...")
                kill_existing_uvicorn()
                break
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
    except Exception as e:
        print(f"❌ Error running uvicorn: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 