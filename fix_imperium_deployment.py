#!/usr/bin/env python3
"""
Fix script for Imperium Master Orchestrator deployment issues
Resolves Python path, uvicorn installation, and service configuration
"""

import os
import subprocess
import time

# Configuration
EC2_HOST = "ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER = "ubuntu"
SSH_KEY = "C:\\projects\\lvl_up\\New.pem"
PROJECT_DIR = "/home/ubuntu"
BACKEND_DIR = f"{PROJECT_DIR}/ai-backend-python"

def run_ssh(command, description=""):
    """Run SSH command on EC2"""
    if description:
        print(f"\n🔄 {description}")
    
    ssh_cmd = f'ssh -i "{SSH_KEY}" {EC2_USER}@{EC2_HOST} "{command}"'
    print(f"Running: {ssh_cmd}")
    
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {str(e)}")
        return False

def fix_deployment():
    """Fix the deployment issues"""
    print("🔧 Fixing Imperium Master Orchestrator Deployment")
    print("=" * 50)
    
    # Step 1: Check current status
    print("\n📊 Step 1: Checking current status")
    run_ssh("sudo systemctl status imperium_master", "Checking service status")
    
    # Step 2: Install Python dependencies
    print("\n📦 Step 2: Installing Python dependencies")
    
    # Check if pip3 is available
    if not run_ssh("which pip3", "Checking pip3 availability"):
        print("Installing pip3...")
        run_ssh("sudo apt update", "Updating package list")
        run_ssh("sudo apt install -y python3-pip", "Installing pip3")
    
    # Install required packages
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "asyncpg",
        "structlog",
        "requests",
        "aiofiles"
    ]
    
    for package in packages:
        run_ssh(f"pip3 install {package}", f"Installing {package}")
    
    # Step 3: Create Python symlink
    print("\n🔗 Step 3: Creating Python symlink")
    run_ssh("sudo ln -sf /usr/bin/python3 /usr/local/bin/python", "Creating python symlink")
    
    # Step 4: Update systemd service
    print("\n⚙️ Step 4: Updating systemd service")
    
    service_content = f"""[Unit]
Description=Imperium Master Orchestrator
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory={BACKEND_DIR}
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file locally
    with open("imperium_master_fixed.service", "w") as f:
        f.write(service_content)
    
    # Upload and install service file
    scp_cmd = f'scp -i "{SSH_KEY}" imperium_master_fixed.service {EC2_USER}@{EC2_HOST}:/tmp/imperium_master.service'
    print(f"Uploading fixed service file: {scp_cmd}")
    subprocess.run(scp_cmd, shell=True)
    
    run_ssh("sudo mv /tmp/imperium_master.service /etc/systemd/system/", "Installing fixed service file")
    run_ssh("sudo systemctl daemon-reload", "Reloading systemd")
    
    # Clean up local file
    os.remove("imperium_master_fixed.service")
    
    # Step 5: Run database migration with python3
    print("\n🗄️ Step 5: Running database migration")
    run_ssh(f"cd {BACKEND_DIR} && python3 create_imperium_tables.py", "Creating Imperium tables with python3")
    
    # Step 6: Check if main.py has proper imports
    print("\n📄 Step 6: Checking main.py")
    run_ssh(f"cat {BACKEND_DIR}/app/main.py", "Checking main.py content")
    
    # Step 7: Test uvicorn manually
    print("\n🧪 Step 7: Testing uvicorn manually")
    run_ssh(f"cd {BACKEND_DIR} && timeout 10s uvicorn app.main:app --host 0.0.0.0 --port 8001", "Testing uvicorn on port 8001")
    
    # Step 8: Start the service
    print("\n🔄 Step 8: Starting Imperium service")
    
    # Stop any existing service
    run_ssh("sudo systemctl stop imperium_master", "Stopping existing service")
    
    # Start the service
    if run_ssh("sudo systemctl start imperium_master", "Starting service"):
        print("✅ Service started successfully")
    else:
        print("❌ Service failed to start")
        run_ssh("sudo journalctl -u imperium_master -n 20", "Checking service logs")
        return False
    
    # Step 9: Verify deployment
    print("\n🔍 Step 9: Verifying deployment")
    
    # Wait for service to start
    print("Waiting for service to start...")
    time.sleep(10)
    
    # Check service status
    if not run_ssh("sudo systemctl status imperium_master", "Checking service status"):
        return False
    
    # Test endpoints
    print("\n🧪 Step 10: Testing endpoints")
    
    test_endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/imperium/status", "Imperium status"),
    ]
    
    for method, endpoint, description in test_endpoints:
        curl_cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:8000{endpoint}"
        if run_ssh(curl_cmd, f"Testing {description}"):
            print(f"✅ {description} - Accessible")
        else:
            print(f"⚠️ {description} - May need time to initialize")
    
    # Step 11: Show deployment summary
    print("\n📊 Step 11: Deployment Summary")
    print("=" * 50)
    print(f"✅ Imperium Master Orchestrator deployment fixed!")
    print(f"📍 Target: {EC2_USER}@{EC2_HOST}")
    print(f"📁 Backend Directory: {BACKEND_DIR}")
    print(f"🔧 Service Name: imperium_master")
    print(f"🌐 API Base URL: http://{EC2_HOST}:8000")
    print(f"📚 API Documentation: http://{EC2_HOST}:8000/docs")
    
    print("\n🔧 Useful Commands:")
    print(f"  View logs: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo journalctl -u imperium_master -f'")
    print(f"  Restart service: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo systemctl restart imperium_master'")
    print(f"  Check status: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo systemctl status imperium_master'")
    print(f"  Test API: curl http://{EC2_HOST}:8000/api/imperium/status")
    
    print("\n🎉 Deployment fix completed successfully!")
    return True

def main():
    """Main function"""
    print("Imperium Master Orchestrator - Deployment Fix")
    print("=" * 50)
    
    # Check if SSH key exists
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        return
    
    try:
        success = fix_deployment()
        if success:
            print("\n✅ Deployment fix completed successfully!")
        else:
            print("\n❌ Deployment fix failed!")
    except KeyboardInterrupt:
        print("\n⚠️ Fix interrupted by user")
    except Exception as e:
        print(f"\n❌ Fix failed with exception: {str(e)}")

if __name__ == "__main__":
    main() 