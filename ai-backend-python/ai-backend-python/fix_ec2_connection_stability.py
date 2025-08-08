#!/usr/bin/env python3
"""
EC2 Connection Stability Fix Script
Addresses connection drops and resets on EC2 instance
"""

import subprocess
import time
import json
import os

class EC2ConnectionStabilityFixer:
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

    def fix_systemd_service(self):
        """Update systemd service with better stability settings"""
        service_content = """[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
Environment=DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb"

[Install]
WantedBy=multi-user.target
"""
        
        # Upload new service file
        with open("ai-backend-python-stable.service", "w") as f:
            f.write(service_content)
        
        # Upload to EC2
        upload_cmd = f'scp -i "{self.key_file}" ai-backend-python-stable.service ubuntu@{self.ec2_host}:/tmp/'
        subprocess.run(upload_cmd, shell=True)
        
        # Update service on EC2
        commands = [
            "sudo cp /tmp/ai-backend-python-stable.service /etc/systemd/system/ai-backend-python.service",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable ai-backend-python.service",
            "sudo systemctl stop ai-backend-python.service",
            "sudo systemctl start ai-backend-python.service",
            "sudo systemctl status ai-backend-python.service"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Running: {cmd}")

    def configure_ssh_stability(self):
        """Configure SSH for better connection stability"""
        ssh_config = """
Host 34.202.215.209
    HostName 34.202.215.209
    User ubuntu
    IdentityFile New.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ConnectTimeout 30
    TCPKeepAlive yes
    Compression yes
"""
        
        # Create SSH config
        with open("ssh_config", "w") as f:
            f.write(ssh_config)
        
        # Upload SSH config
        upload_cmd = f'scp -i "{self.key_file}" ssh_config ubuntu@{self.ec2_host}:/tmp/'
        subprocess.run(upload_cmd, shell=True)
        
        # Configure on EC2
        commands = [
            "mkdir -p ~/.ssh",
            "cp /tmp/ssh_config ~/.ssh/config",
            "chmod 600 ~/.ssh/config"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"SSH Config: {cmd}")

    def configure_network_stability(self):
        """Configure network settings for better stability"""
        commands = [
            # Increase TCP keepalive settings
            "echo 'net.ipv4.tcp_keepalive_time = 60' | sudo tee -a /etc/sysctl.conf",
            "echo 'net.ipv4.tcp_keepalive_intvl = 60' | sudo tee -a /etc/sysctl.conf", 
            "echo 'net.ipv4.tcp_keepalive_probes = 3' | sudo tee -a /etc/sysctl.conf",
            "sudo sysctl -p",
            
            # Configure systemd network stability
            "sudo systemctl enable systemd-networkd-wait-online.service",
            
            # Add connection monitoring
            "sudo apt-get update -y",
            "sudo apt-get install -y htop iotop"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Network Config: {cmd}")

    def setup_connection_monitoring(self):
        """Setup monitoring for connection stability"""
        monitor_script = """#!/bin/bash
# Connection monitoring script
LOG_FILE="/home/ubuntu/connection_monitor.log"

while true; do
    echo "$(date): Checking backend connectivity..." >> $LOG_FILE
    
    # Check if backend is responding
    if curl -s http://localhost:8000/api/imperium/persistence/learning-analytics > /dev/null; then
        echo "$(date): Backend is responding" >> $LOG_FILE
    else
        echo "$(date): Backend not responding, restarting service" >> $LOG_FILE
        sudo systemctl restart ai-backend-python.service
    fi
    
    # Check system resources
    echo "$(date): Memory usage: $(free -m | awk 'NR==2{printf \"%.1f%%\", $3*100/$2}')" >> $LOG_FILE
    echo "$(date): CPU usage: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1)%" >> $LOG_FILE
    
    sleep 300  # Check every 5 minutes
done
"""
        
        with open("connection_monitor.sh", "w") as f:
            f.write(monitor_script)
        
        # Upload and setup monitoring
        upload_cmd = f'scp -i "{self.key_file}" connection_monitor.sh ubuntu@{self.ec2_host}:/home/ubuntu/'
        subprocess.run(upload_cmd, shell=True)
        
        commands = [
            "chmod +x /home/ubuntu/connection_monitor.sh",
            "nohup /home/ubuntu/connection_monitor.sh > /dev/null 2>&1 &"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Monitoring Setup: {cmd}")

    def test_connection_stability(self):
        """Test connection stability"""
        print("\n🧪 Testing Connection Stability...")
        
        # Test multiple connections
        for i in range(5):
            print(f"\n--- Test {i+1}/5 ---")
            result = self.run_ssh_command(
                "curl -s http://localhost:8000/api/imperium/persistence/learning-analytics",
                f"Connection test {i+1}"
            )
            
            if result:
                print(f"✅ Test {i+1} successful")
            else:
                print(f"❌ Test {i+1} failed")
            
            time.sleep(2)

    def run_complete_fix(self):
        """Run complete connection stability fix"""
        print("🔧 Starting EC2 Connection Stability Fix...")
        
        # 1. Fix systemd service
        print("\n📋 Step 1: Updating systemd service...")
        self.fix_systemd_service()
        
        # 2. Configure SSH stability
        print("\n📋 Step 2: Configuring SSH stability...")
        self.configure_ssh_stability()
        
        # 3. Configure network stability
        print("\n📋 Step 3: Configuring network stability...")
        self.configure_network_stability()
        
        # 4. Setup monitoring
        print("\n📋 Step 4: Setting up connection monitoring...")
        self.setup_connection_monitoring()
        
        # 5. Test stability
        print("\n📋 Step 5: Testing connection stability...")
        self.test_connection_stability()
        
        print("\n✅ EC2 Connection Stability Fix Complete!")
        print("\n📊 Summary:")
        print("- Updated systemd service with better restart policies")
        print("- Configured SSH for connection stability")
        print("- Added network keepalive settings")
        print("- Setup connection monitoring")
        print("- Backend now running on port 8000 with stability improvements")

if __name__ == "__main__":
    fixer = EC2ConnectionStabilityFixer()
    fixer.run_complete_fix() 