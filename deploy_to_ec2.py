#!/usr/bin/env python3
"""
Quick deployment script for Imperium Master Orchestrator to EC2
Tailored for the specific EC2 instance setup
"""

import os
import subprocess
import time
from datetime import datetime

# Configuration - Update these for your setup
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

def upload_file(local_path, remote_path, description=""):
    """Upload file to EC2"""
    if description:
        print(f"\n📤 {description}")
    
    scp_cmd = f'scp -i "{SSH_KEY}" "{local_path}" {EC2_USER}@{EC2_HOST}:{remote_path}'
    print(f"Running: {scp_cmd}")
    
    try:
        result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
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

def deploy_imperium():
    """Deploy Imperium Master Orchestrator"""
    print("🚀 Deploying Imperium Master Orchestrator to EC2")
    print(f"Target: {EC2_USER}@{EC2_HOST}")
    print(f"Project Directory: {PROJECT_DIR}")
    
    # Step 1: Check if backend directory exists
    print("\n📁 Step 1: Checking backend directory")
    if not run_ssh(f"test -d {BACKEND_DIR}", "Checking if backend directory exists"):
        print(f"Creating backend directory: {BACKEND_DIR}")
        if not run_ssh(f"mkdir -p {BACKEND_DIR}", "Creating backend directory"):
            return False
    
    # Step 2: Create backup
    print("\n📦 Step 2: Creating backup")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{PROJECT_DIR}/imperium_backup_{timestamp}"
    
    if not run_ssh(f"mkdir -p {backup_dir}", "Creating backup directory"):
        return False
    
    if not run_ssh(f"cp -r {BACKEND_DIR} {backup_dir}/", "Backing up current backend"):
        print("No existing backend to backup (this is normal for first deployment)")
    
    # Step 3: Upload enhanced files
    print("\n📤 Step 3: Uploading Imperium files")
    
    files_to_upload = [
        ("ai-backend-python/app/models/sql_models.py", f"{BACKEND_DIR}/app/models/"),
        ("ai-backend-python/app/services/imperium_learning_controller.py", f"{BACKEND_DIR}/app/services/"),
        ("ai-backend-python/app/routers/imperium_learning.py", f"{BACKEND_DIR}/app/routers/"),
        ("ai-backend-python/create_imperium_tables.py", f"{BACKEND_DIR}/"),
    ]
    
    for local_file, remote_dir in files_to_upload:
        if not upload_file(local_file, remote_dir, f"Uploading {os.path.basename(local_file)}"):
            return False
    
    # Step 4: Create necessary directories
    print("\n📁 Step 4: Creating necessary directories")
    directories = [
        f"{BACKEND_DIR}/app/models",
        f"{BACKEND_DIR}/app/services", 
        f"{BACKEND_DIR}/app/routers",
        f"{BACKEND_DIR}/app/core"
    ]
    
    for directory in directories:
        if not run_ssh(f"mkdir -p {directory}", f"Creating {directory}"):
            return False
    
    # Step 5: Check if main.py exists, if not create a basic one
    print("\n📄 Step 5: Checking main.py")
    if not run_ssh(f"test -f {BACKEND_DIR}/app/main.py", "Checking if main.py exists"):
        print("Creating basic main.py")
        main_py_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Create FastAPI app
app = FastAPI(title="Imperium Master Orchestrator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
# Import routers
try:
    from app.routers import imperium_learning
    app.include_router(imperium_learning.router)
    print("✅ Imperium learning router loaded")
except Exception as e:
    print(f"⚠️ Could not load imperium_learning router: {e}")

@app.get("/")
async def root():
    return {"message": "Imperium Master Orchestrator is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Imperium Master Orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        # Write main.py locally and upload
        with open("main.py", "w") as f:
            f.write(main_py_content)
        
        if not upload_file("main.py", f"{BACKEND_DIR}/app/", "Uploading main.py"):
            return False
        
        os.remove("main.py")
    
    # Step 6: Run database migration
    print("\n🗄️ Step 6: Running database migration")
    if not run_ssh(f"cd {BACKEND_DIR} && python create_imperium_tables.py", "Creating Imperium tables"):
        print("⚠️ Database migration failed - this might be expected if database is not configured")
        print("You can run the migration manually later")
    
    # Step 7: Create systemd service
    print("\n⚙️ Step 7: Creating systemd service")
    service_content = f"""[Unit]
Description=Imperium Master Orchestrator
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory={BACKEND_DIR}
Environment=PATH={BACKEND_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # Write service file locally
    with open("imperium_master.service", "w") as f:
        f.write(service_content)
    
    # Upload service file
    if not upload_file("imperium_master.service", "/tmp/", "Uploading systemd service file"):
        return False
    
    # Install service
    if not run_ssh("sudo mv /tmp/imperium_master.service /etc/systemd/system/", "Installing service file"):
        return False
    
    if not run_ssh("sudo systemctl daemon-reload", "Reloading systemd"):
        return False
    
    # Clean up local service file
    os.remove("imperium_master.service")
    
    # Step 8: Start the service
    print("\n🔄 Step 8: Starting Imperium service")
    
    # Stop existing service if running
    run_ssh("sudo systemctl stop imperium_master", "Stopping existing service")
    
    if not run_ssh("sudo systemctl enable imperium_master", "Enabling service"):
        return False
    
    if not run_ssh("sudo systemctl start imperium_master", "Starting service"):
        return False
    
    # Step 9: Verify deployment
    print("\n🔍 Step 9: Verifying deployment")
    
    # Wait for service to start
    print("Waiting for service to start...")
    time.sleep(10)
    
    # Check service status
    if not run_ssh("sudo systemctl status imperium_master", "Checking service status"):
        return False
    
    # Test basic endpoints
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
    print(f"✅ Imperium Master Orchestrator deployed successfully!")
    print(f"📍 Target: {EC2_USER}@{EC2_HOST}")
    print(f"📁 Project Directory: {PROJECT_DIR}")
    print(f"📁 Backend Directory: {BACKEND_DIR}")
    print(f"📦 Backup Location: {backup_dir}")
    print(f"🔧 Service Name: imperium_master")
    print(f"🌐 API Base URL: http://{EC2_HOST}:8000")
    print(f"📚 API Documentation: http://{EC2_HOST}:8000/docs")
    
    print("\n🔧 Useful Commands:")
    print(f"  View logs: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo journalctl -u imperium_master -f'")
    print(f"  Restart service: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo systemctl restart imperium_master'")
    print(f"  Check status: ssh -i \"{SSH_KEY}\" {EC2_USER}@{EC2_HOST} 'sudo systemctl status imperium_master'")
    print(f"  Test API: curl http://{EC2_HOST}:8000/api/imperium/status")
    
    print("\n🎉 Deployment completed successfully!")
    return True

def main():
    """Main function"""
    print("Imperium Master Orchestrator - EC2 Deployment")
    print("=" * 50)
    
    # Check if SSH key exists
    if not os.path.exists(SSH_KEY):
        print(f"❌ SSH key not found: {SSH_KEY}")
        print("Please ensure the SSH key file exists and update the SSH_KEY variable if needed")
        return
    
    # Check if required files exist
    required_files = [
        "ai-backend-python/app/models/sql_models.py",
        "ai-backend-python/app/services/imperium_learning_controller.py",
        "ai-backend-python/app/routers/imperium_learning.py",
        "ai-backend-python/create_imperium_tables.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        return
    
    try:
        success = deploy_imperium()
        if success:
            print("\n✅ Deployment completed successfully!")
        else:
            print("\n❌ Deployment failed!")
    except KeyboardInterrupt:
        print("\n⚠️ Deployment interrupted by user")
    except Exception as e:
        print(f"\n❌ Deployment failed with exception: {str(e)}")

if __name__ == "__main__":
    main() 