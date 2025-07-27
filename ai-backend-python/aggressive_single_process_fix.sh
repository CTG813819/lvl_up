#!/bin/bash

echo "🔥 AGGRESSIVE SINGLE PROCESS FIX"
echo "================================"

# Step 1: Nuclear option - kill everything
echo "💥 Step 1: Nuclear process cleanup..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo systemctl stop integrated-ai-manager.service 2>/dev/null || true
sudo systemctl stop conquest-ai-simple.service 2>/dev/null || true
sudo systemctl stop sandbox-ai-simple.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true

# Kill ALL possible processes
echo "🔪 Killing ALL possible processes..."
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sudo pkill -f 'python3.*main:app'
sudo pkill -f 'run_uvicorn'
sudo pkill -f 'start_clean_backend'
sudo pkill -f 'start_single_backend'
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait longer for processes to fully stop
sleep 15

# Force kill any remaining processes
echo "💀 Force killing any remaining processes..."
sudo pkill -9 -f uvicorn 2>/dev/null || true
sudo pkill -9 -f 'python.*main:app' 2>/dev/null || true
sudo pkill -9 -f 'python3.*main:app' 2>/dev/null || true

sleep 5

# Verify no processes are running
echo "🔍 Verifying no processes are running..."
if pgrep -f uvicorn > /dev/null; then
    echo "❌ Uvicorn processes still running:"
    pgrep -f uvicorn -a
    echo "💀 Force killing with SIGKILL..."
    sudo pkill -9 -f uvicorn
    sleep 5
fi

# Check if port 8000 is free
echo "🔍 Checking if port 8000 is free..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 is still in use, force killing..."
    sudo lsof -ti:8000 | xargs sudo kill -9
    sleep 5
fi

# Step 2: Create a process monitor script
echo "📝 Step 2: Creating process monitor script..."
cat > monitor_single_process.py << 'EOF'
#!/usr/bin/env python3
"""
Single Process Monitor
Ensures only one uvicorn process runs
"""

import os
import sys
import time
import signal
import subprocess
import psutil
from pathlib import Path

def kill_all_uvicorn():
    """Kill all uvicorn processes"""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                print(f"🔪 Killing uvicorn process: {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=3)
                killed += 1
        except (psutil.NoSuchProcess, psutil.TimeoutExpired):
            try:
                proc.kill()
                killed += 1
            except psutil.NoSuchProcess:
                pass
    return killed

def check_port_available(port=8000):
    """Check if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def main():
    print("🔍 Starting single process monitor...")
    
    # Kill any existing uvicorn processes
    killed = kill_all_uvicorn()
    print(f"🔪 Killed {killed} existing uvicorn processes")
    
    # Wait for processes to fully terminate
    time.sleep(5)
    
    # Check if port is available
    if not check_port_available(8000):
        print("❌ Port 8000 is still in use. Force killing...")
        os.system("sudo lsof -ti:8000 | xargs sudo kill -9")
        time.sleep(5)
        if not check_port_available(8000):
            print("❌ Port 8000 still in use after force kill. Exiting.")
            sys.exit(1)
    
    # Get the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Set environment variables
    env = os.environ.copy()
    env['DISABLE_BACKGROUND_TASKS'] = 'true'
    env['DISABLE_AI_CYCLES'] = 'true'
    env['DISABLE_AUTONOMOUS_CYCLES'] = 'true'
    env['DISABLE_LEARNING_CYCLES'] = 'true'
    env['PYTHONPATH'] = str(script_dir)
    
    # Build uvicorn command
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--workers', '1',
        '--loop', 'asyncio',
        '--limit-concurrency', '50'
    ]
    
    print(f"🚀 Starting uvicorn: {' '.join(cmd)}")
    
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
        
        # Monitor for multiple processes
        while True:
            if process.poll() is not None:
                print(f"❌ Uvicorn process exited with code: {process.returncode}")
                break
            
            # Check for multiple uvicorn processes
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
                kill_all_uvicorn()
                break
            
            time.sleep(10)
    
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

chmod +x monitor_single_process.py

# Step 3: Update systemd service to use the monitor
echo "📝 Step 3: Updating systemd service..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
Environment=DISABLE_BACKGROUND_TASKS=true
Environment=DISABLE_AI_CYCLES=true
Environment=DISABLE_AUTONOMOUS_CYCLES=true
Environment=DISABLE_LEARNING_CYCLES=true

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/monitor_single_process.py
ExecStop=/bin/kill -TERM $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 4: Reload and start
echo "🔄 Step 4: Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python.service
sudo systemctl start ai-backend-python.service

# Step 5: Wait and verify
echo "⏳ Step 5: Waiting for service to start..."
sleep 20

# Check service status
echo "🔍 Step 6: Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for single process
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Only one PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,cmd
        
        # Check CPU usage
        echo "📊 CPU usage:"
        top -p $pid -b -n 1 | tail -2
        
        echo "🎉 AGGRESSIVE SINGLE PROCESS FIX COMPLETED SUCCESSFULLY!"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        echo "🔪 Force killing all processes and trying again..."
        sudo pkill -9 -f uvicorn
        sleep 5
        sudo systemctl restart ai-backend-python.service
        sleep 15
        
        pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
        if [ "$pids" -eq 1 ]; then
            pid=$(pgrep -f 'uvicorn.*app.main:app')
            echo "✅ SUCCESS after restart! Only one PID: $pid"
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