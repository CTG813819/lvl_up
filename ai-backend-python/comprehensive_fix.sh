#!/bin/bash

echo "🔧 Comprehensive Backend Fix - PID + Database Issues"
echo "=================================================="

# Stop all services and kill all processes
echo "🛑 Stopping all services and killing processes..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo systemctl stop integrated-ai-manager.service 2>/dev/null || true

# Kill ALL uvicorn processes
echo "🔪 Killing all uvicorn processes..."
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sudo pkill -f 'python3.*main:app'
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to fully stop
sleep 5

# Verify no uvicorn processes are running
echo "🔍 Verifying no uvicorn processes are running..."
if pgrep -f uvicorn > /dev/null; then
    echo "❌ Uvicorn processes still running:"
    pgrep -f uvicorn -a
    echo "🔪 Force killing remaining processes..."
    sudo pkill -9 -f uvicorn
    sleep 2
else
    echo "✅ No uvicorn processes running"
fi

# Run database schema fix
echo "🔧 Running database schema fix..."
cd /home/ubuntu/ai-backend-python
source venv/bin/activate
python fix_database_schema.py

# Create a more robust Python wrapper script
echo "📝 Creating robust single process wrapper..."
cat > /home/ubuntu/ai-backend-python/run_uvicorn_single.py << 'EOF'
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
EOF

chmod +x /home/ubuntu/ai-backend-python/run_uvicorn_single.py

# Update service configuration to be more robust
echo "📝 Updating service configuration..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=PYTHONPATH=/home/ubuntu/ai-backend-python
Environment=PYTHONUNBUFFERED=1
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/run_uvicorn_single.py
ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/ubuntu/ai-backend-python

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Start the service
echo "🚀 Starting backend service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 8

# Check service status
echo "🔍 Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for multiple PIDs
    echo "🔍 Checking for multiple PIDs..."
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Only one PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,cmd
        
        # Test endpoint
        echo "🧪 Testing health endpoint..."
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo "✅ Health endpoint responding"
        else
            echo "❌ Health endpoint not responding"
        fi
        
        echo "🎉 Comprehensive fix completed successfully!"
        echo "📊 Summary:"
        echo "   - Single PID: $pid"
        echo "   - Port: 8000"
        echo "   - Database schema: Fixed"
        echo "   - No conflicts"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        echo "🔪 Killing all processes and trying again..."
        sudo pkill -f uvicorn
        sleep 3
        sudo systemctl restart ai-backend-python.service
        sleep 5
        
        pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
        if [ "$pids" -eq 1 ]; then
            echo "✅ Fixed after restart! PID: $(pgrep -f 'uvicorn.*app.main:app')"
        else
            echo "❌ Still multiple PIDs after restart"
            exit 1
        fi
    fi
    
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 