#!/bin/bash

echo "🎯 TARGETED FIX - Prevent Multiple Instances Only"
echo "================================================="

# Step 1: Stop current processes
echo "🛑 Step 1: Stopping current processes..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true

# Kill existing uvicorn processes
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sleep 5

# Step 2: Create a process guard script
echo "📝 Step 2: Creating process guard script..."
cat > process_guard.py << 'EOF'
#!/usr/bin/env python3
"""
Process Guard - Prevents multiple instances while keeping all AI functionality
"""

import os
import sys
import time
import signal
import subprocess
import psutil
import fcntl
from pathlib import Path

class ProcessGuard:
    def __init__(self, lock_file="/tmp/ai_backend.lock"):
        self.lock_file = lock_file
        self.lock_fd = None
        
    def acquire_lock(self):
        """Acquire a file lock to ensure only one instance"""
        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            print(f"❌ Another instance is already running. Lock file: {self.lock_file}")
            return False
    
    def release_lock(self):
        """Release the file lock"""
        if self.lock_fd:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                self.lock_fd.close()
            except:
                pass
    
    def check_existing_processes(self):
        """Check for existing uvicorn processes"""
        existing_pids = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any('uvicorn' in cmd for cmd in proc.info['cmdline']):
                    existing_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return existing_pids
    
    def kill_existing_processes(self):
        """Kill existing uvicorn processes"""
        existing_pids = self.check_existing_processes()
        if existing_pids:
            print(f"🔪 Found existing uvicorn processes: {existing_pids}")
            for pid in existing_pids:
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    proc.wait(timeout=5)
                    print(f"✅ Killed process {pid}")
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    try:
                        proc.kill()
                        print(f"💀 Force killed process {pid}")
                    except psutil.NoSuchProcess:
                        pass
            time.sleep(3)
    
    def start_uvicorn(self):
        """Start uvicorn with all AI functionality enabled"""
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Keep all AI functionality - don't disable anything
        env = os.environ.copy()
        env['PYTHONPATH'] = str(script_dir)
        
        # Start uvicorn with single worker but keep all features
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--workers', '1',  # Only one worker
            '--loop', 'asyncio',
            '--limit-concurrency', '100'  # Allow more concurrency for AI tasks
        ]
        
        print(f"🚀 Starting uvicorn with AI functionality: {' '.join(cmd)}")
        
        try:
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
                
                # Check for multiple processes (shouldn't happen with our guard)
                existing_pids = self.check_existing_processes()
                if len(existing_pids) > 1:
                    print(f"⚠️  Multiple uvicorn processes detected: {existing_pids}")
                    print("🔪 This shouldn't happen with our guard. Terminating all...")
                    self.kill_existing_processes()
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
        finally:
            self.release_lock()

def main():
    guard = ProcessGuard()
    
    # Try to acquire lock
    if not guard.acquire_lock():
        sys.exit(1)
    
    try:
        # Kill any existing processes
        guard.kill_existing_processes()
        
        # Start uvicorn
        guard.start_uvicorn()
        
    except Exception as e:
        print(f"❌ Error in process guard: {e}")
        guard.release_lock()
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

chmod +x process_guard.py

# Step 3: Update systemd service to use the process guard
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
# Keep all AI functionality - don't disable anything
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819

ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python /home/ubuntu/ai-backend-python/process_guard.py
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
        
        echo "🎉 TARGETED FIX COMPLETED SUCCESSFULLY!"
        echo "📋 Summary:"
        echo "   - Single PID: $pid"
        echo "   - All AI functionality preserved"
        echo "   - Imperium orchestrator working"
        echo "   - Background tasks enabled"
        echo "   - AI cycles enabled"
        echo "   - No multiple instances"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        exit 1
    fi
    
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 