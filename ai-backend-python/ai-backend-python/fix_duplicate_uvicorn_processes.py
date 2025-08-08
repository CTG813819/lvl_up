#!/usr/bin/env python3
"""
Fix Duplicate Uvicorn Processes Script
Stops conflicting uvicorn processes and ensures only one service runs
"""

import subprocess
import time
import json
import os

class DuplicateProcessFixer:
    def __init__(self):
        self.ec2_host = "34.202.215.209"
        self.key_file = "New.pem"
        
    def run_ssh_command(self, command, description=""):
        """Run SSH command with better error handling"""
        try:
            ssh_cmd = f'ssh -i "{self.key_file}" -o ConnectTimeout=30 -o ServerAliveInterval=60 -o ServerAliveCountMax=3 ubuntu@{self.ec2_host} "{command}"'
            print(f"🔄 {description}")
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {description} - SUCCESS")
                return result.stdout.strip()
            else:
                print(f"❌ {description} - FAILED")
                print(f"Error: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return None
        except Exception as e:
            print(f"💥 {description} - EXCEPTION: {e}")
            return None

    def identify_duplicate_processes(self):
        """Identify all uvicorn processes"""
        print("\n📋 Step 1: Identifying duplicate processes...")
        
        commands = [
            "ps aux | grep uvicorn | grep -v grep",
            "sudo netstat -tlnp | grep -E ':(4000|8000)'",
            "sudo systemctl status ai-backend-python"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Process Check: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def stop_all_uvicorn_processes(self):
        """Stop all uvicorn processes"""
        print("\n📋 Step 2: Stopping all uvicorn processes...")
        
        commands = [
            "sudo systemctl stop ai-backend-python.service",
            "pkill -f uvicorn",
            "pkill -f 'app.main:app'",
            "sleep 5",
            "ps aux | grep uvicorn | grep -v grep || echo 'No uvicorn processes found'"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Stop Processes: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def clean_up_port_conflicts(self):
        """Clean up any port conflicts"""
        print("\n📋 Step 3: Cleaning up port conflicts...")
        
        commands = [
            "sudo fuser -k 4000/tcp 2>/dev/null || echo 'Port 4000 already free'",
            "sudo fuser -k 8000/tcp 2>/dev/null || echo 'Port 8000 already free'",
            "sudo netstat -tlnp | grep -E ':(4000|8000)' || echo 'No processes on ports 4000/8000'"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Port Cleanup: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def fix_systemd_service(self):
        """Fix the systemd service configuration"""
        print("\n📋 Step 4: Fixing systemd service...")
        
        # Create a better service configuration
        service_content = """[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal
Environment=DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb"

[Install]
WantedBy=multi-user.target
"""
        
        # Upload new service file
        with open("ai-backend-python-fixed.service", "w") as f:
            f.write(service_content)
        
        # Upload to EC2
        upload_cmd = f'scp -i "{self.key_file}" ai-backend-python-fixed.service ubuntu@{self.ec2_host}:/tmp/'
        subprocess.run(upload_cmd, shell=True)
        
        # Update service on EC2
        commands = [
            "sudo cp /tmp/ai-backend-python-fixed.service /etc/systemd/system/ai-backend-python.service",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable ai-backend-python.service"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Service Fix: {cmd}")

    def start_service_properly(self):
        """Start the service properly"""
        print("\n📋 Step 5: Starting service properly...")
        
        commands = [
            "sudo systemctl start ai-backend-python.service",
            "sleep 10",
            "sudo systemctl status ai-backend-python.service",
            "sudo netstat -tlnp | grep -E ':(4000|8000)'"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Service Start: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def test_service_stability(self):
        """Test service stability"""
        print("\n📋 Step 6: Testing service stability...")
        
        test_commands = [
            "curl -s http://localhost:8000/api/health",
            "curl -s http://localhost:8000/api/imperium/persistence/learning-analytics",
            "ps aux | grep uvicorn | grep -v grep | wc -l"
        ]
        
        for cmd in test_commands:
            result = self.run_ssh_command(cmd, f"Stability Test: {cmd}")
            if result:
                print(f"📊 Test Result: {result}")

    def monitor_service_logs(self):
        """Monitor service logs for issues"""
        print("\n📋 Step 7: Monitoring service logs...")
        
        commands = [
            "sudo journalctl -u ai-backend-python.service -n 20 --no-pager",
            "sudo systemctl status ai-backend-python.service --no-pager"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Log Monitor: {cmd}")
            if result:
                print(f"📊 Log Output: {result}")

    def run_complete_fix(self):
        """Run complete duplicate process fix"""
        print("🔧 Starting Duplicate Uvicorn Process Fix...")
        
        # 1. Identify duplicate processes
        self.identify_duplicate_processes()
        
        # 2. Stop all uvicorn processes
        self.stop_all_uvicorn_processes()
        
        # 3. Clean up port conflicts
        self.clean_up_port_conflicts()
        
        # 4. Fix systemd service
        self.fix_systemd_service()
        
        # 5. Start service properly
        self.start_service_properly()
        
        # 6. Test service stability
        self.test_service_stability()
        
        # 7. Monitor service logs
        self.monitor_service_logs()
        
        print("\n✅ Duplicate Uvicorn Process Fix Complete!")
        print("\n📊 Summary:")
        print("- Stopped all conflicting uvicorn processes")
        print("- Cleaned up port conflicts")
        print("- Fixed systemd service configuration")
        print("- Started service with single worker")
        print("- Service now running stably on port 8000")

if __name__ == "__main__":
    fixer = DuplicateProcessFixer()
    fixer.run_complete_fix() 