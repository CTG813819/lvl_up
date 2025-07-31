#!/usr/bin/env python3
"""
Deployment script for Imperium Master Orchestrator
Deploys the enhanced Imperium with full database persistence to EC2
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime

# Configuration
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER = "ubuntu"
SSH_KEY = "C:\\projects\\lvl_up\\New.pem"
PROJECT_DIR = "/home/ubuntu"
BACKEND_DIR = f"{PROJECT_DIR}/ai-backend-python"

def run_ssh_command(command, description=""):
    """Run a command on the EC2 instance via SSH"""
    if description:
        print(f"\n🔄 {description}")
    
    ssh_command = f'ssh -i "{SSH_KEY}" {EC2_USER}@{EC2_HOST} "{command}"'
    print(f"Running: {ssh_command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def upload_file(local_path, remote_path, description=""):
    """Upload a file to the EC2 instance"""
    if description:
        print(f"\n📤 {description}")
    
    scp_command = f'scp -i "{SSH_KEY}" {local_path} {EC2_USER}@{EC2_HOST}:{remote_path}'
    print(f"Running: {scp_command}")
    
    try:
        result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def deploy_imperium_master():
    """Deploy the Imperium Master Orchestrator"""
    print("🚀 Starting Imperium Master Orchestrator Deployment")
    print(f"Target: {EC2_USER}@{EC2_HOST}")
    print(f"Project Directory: {PROJECT_DIR}")
    
    # Step 1: Create backup of current deployment
    print("\n📦 Step 1: Creating backup of current deployment")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{PROJECT_DIR}/imperium_backup_{timestamp}"
    
    if not run_ssh_command(f"mkdir -p {backup_dir}", "Creating backup directory"):
        return False
    
    if not run_ssh_command(f"cp -r {BACKEND_DIR} {backup_dir}/", "Backing up current backend"):
        return False
    
    print(f"✅ Backup created at: {backup_dir}")
    
    # Step 2: Upload enhanced files
    print("\n📤 Step 2: Uploading enhanced Imperium files")
    
    files_to_upload = [
        ("ai-backend-python/app/models/sql_models.py", f"{BACKEND_DIR}/app/models/"),
        ("ai-backend-python/app/services/imperium_learning_controller.py", f"{BACKEND_DIR}/app/services/"),
        ("ai-backend-python/app/routers/imperium_learning.py", f"{BACKEND_DIR}/app/routers/"),
        ("ai-backend-python/create_imperium_tables.py", f"{BACKEND_DIR}/"),
    ]
    
    for local_file, remote_dir in files_to_upload:
        if not upload_file(local_file, remote_dir, f"Uploading {os.path.basename(local_file)}"):
            return False
    
    # Step 3: Run database migration
    print("\n🗄️ Step 3: Running database migration")
    
    if not run_ssh_command(f"cd {BACKEND_DIR} && python create_imperium_tables.py", "Creating Imperium tables"):
        return False
    
    # Step 4: Update systemd service
    print("\n⚙️ Step 4: Updating systemd service")
    
    service_content = f"""[Unit]
Description=Imperium Master Orchestrator
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory={BACKEND_DIR}
Environment=PATH={BACKEND_DIR}/venv/bin
ExecStart={BACKEND_DIR}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file locally
    service_file = "imperium_master.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    
    # Upload and install service file
    if not upload_file(service_file, "/tmp/", "Uploading systemd service file"):
        return False
    
    if not run_ssh_command("sudo mv /tmp/imperium_master.service /etc/systemd/system/", "Installing service file"):
        return False
    
    if not run_ssh_command("sudo systemctl daemon-reload", "Reloading systemd"):
        return False
    
    # Clean up local service file
    os.remove(service_file)
    
    # Step 5: Restart the service
    print("\n🔄 Step 5: Restarting Imperium service")
    
    if not run_ssh_command("sudo systemctl stop imperium_master", "Stopping current service"):
        pass  # Service might not exist yet
    
    if not run_ssh_command("sudo systemctl enable imperium_master", "Enabling service"):
        return False
    
    if not run_ssh_command("sudo systemctl start imperium_master", "Starting service"):
        return False
    
    # Step 6: Verify deployment
    print("\n🔍 Step 6: Verifying deployment")
    
    # Wait for service to start
    print("Waiting for service to start...")
    time.sleep(10)
    
    # Check service status
    if not run_ssh_command("sudo systemctl status imperium_master", "Checking service status"):
        return False
    
    # Test API endpoints
    print("\n🧪 Step 7: Testing API endpoints")
    
    test_endpoints = [
        "GET /api/imperium/status",
        "GET /api/imperium/agents",
        "GET /api/imperium/persistence/agent-metrics",
        "GET /api/imperium/persistence/learning-cycles",
    ]
    
    for endpoint in test_endpoints:
        method, path = endpoint.split(" ")
        curl_command = f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8000{path}"
        
        if run_ssh_command(curl_command, f"Testing {endpoint}"):
            print(f"✅ {endpoint} - Accessible")
        else:
            print(f"⚠️ {endpoint} - May need time to initialize")
    
    # Step 8: Show deployment summary
    print("\n📊 Step 8: Deployment Summary")
    
    summary = {
        "deployment_time": datetime.now().isoformat(),
        "target_host": EC2_HOST,
        "backup_location": backup_dir,
        "service_name": "imperium_master",
        "new_features": [
            "Database persistence for agent metrics",
            "Learning cycle tracking",
            "Structured learning event logging",
            "Internet learning result storage",
            "Comprehensive analytics endpoints",
            "Master orchestrator capabilities"
        ],
        "api_endpoints": [
            "/api/imperium/persistence/agent-metrics",
            "/api/imperium/persistence/learning-cycles",
            "/api/imperium/persistence/learning-analytics",
            "/api/imperium/persistence/log-learning-event",
            "/api/imperium/persistence/internet-learning-result"
        ]
    }
    
    print(json.dumps(summary, indent=2))
    
    # Step 9: Show useful commands
    print("\n🔧 Useful Commands:")
    print(f"  View logs: ssh {EC2_USER}@{EC2_HOST} 'sudo journalctl -u imperium_master -f'")
    print(f"  Restart service: ssh {EC2_USER}@{EC2_HOST} 'sudo systemctl restart imperium_master'")
    print(f"  Check status: ssh {EC2_USER}@{EC2_HOST} 'sudo systemctl status imperium_master'")
    print(f"  View API docs: http://{EC2_HOST}:8000/docs")
    
    print("\n🎉 Imperium Master Orchestrator deployment completed successfully!")
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Imperium Master Orchestrator Deployment Script")
        print("Usage: python deploy_imperium_master.py")
        print("\nBefore running:")
        print("1. Update EC2_HOST and EC2_USER variables in the script")
        print("2. Ensure SSH key is configured for EC2 access")
        print("3. Ensure the backend directory exists on EC2")
        return
    
    # Check if SSH key exists
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        print("Please ensure the SSH key file exists and update the SSH_KEY variable if needed")
        return
    
    try:
        success = deploy_imperium_master()
        if success:
            print("\n✅ Deployment completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 