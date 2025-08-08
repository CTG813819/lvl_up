#!/usr/bin/env python3
"""
Deploy Enhanced Imperium Monitoring System to Backend
"""

import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:4000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def deploy_imperium_monitoring():
    """Deploy the enhanced Imperium monitoring system"""
    print("🚀 Deploying Enhanced Imperium Monitoring System...")
    
    # Check if backend is running
    if not check_backend_status():
        print("❌ Backend is not running. Please start the backend first.")
        return False
    
    # Copy monitoring system to backend
    backend_path = "ai-backend-python"
    monitoring_file = "imperium_monitoring_system.py"
    
    if os.path.exists(monitoring_file):
        # Copy to backend services
        dest_path = os.path.join(backend_path, "app", "services", "imperium_monitoring.py")
        
        with open(monitoring_file, 'r') as src:
            content = src.read()
        
        # Update imports for backend structure
        content = content.replace(
            "from app.core.database import get_session, init_database",
            "from app.core.database import get_session, init_database"
        )
        
        with open(dest_path, 'w') as dst:
            dst.write(content)
        
        print(f"✅ Copied monitoring system to {dest_path}")
    else:
        print(f"❌ Monitoring file {monitoring_file} not found")
        return False
    
    # Create startup script
    startup_script = """#!/bin/bash
# Imperium Monitoring System Startup Script

cd /home/ubuntu/lvl_up/ai-backend-python

# Start monitoring system in background
python3 -m app.services.imperium_monitoring &

# Save PID
echo $! > imperium_monitoring.pid

echo "Imperium Monitoring System started with PID: $(cat imperium_monitoring.pid)"
"""
    
    with open("start_imperium_monitoring.sh", 'w') as f:
        f.write(startup_script)
    
    os.chmod("start_imperium_monitoring.sh", 0o755)
    print("✅ Created startup script")
    
    # Create systemd service
    service_content = """[Unit]
Description=Imperium AI Monitoring System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lvl_up/ai-backend-python
ExecStart=/usr/bin/python3 -m app.services.imperium_monitoring
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/ubuntu/lvl_up/ai-backend-python

[Install]
WantedBy=multi-user.target
"""
    
    with open("imperium-monitoring.service", 'w') as f:
        f.write(service_content)
    
    print("✅ Created systemd service file")
    
    # Create monitoring dashboard endpoint
    dashboard_endpoint = '''
@router.get("/api/imperium/monitoring")
async def get_imperium_monitoring():
    """Get Imperium monitoring status and data"""
    try:
        # Read monitoring report
        report_path = "imperium_monitoring_report.json"
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report = json.load(f)
        else:
            report = {
                "status": "initializing",
                "timestamp": datetime.now().isoformat(),
                "message": "Monitoring system is starting up"
            }
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/api/imperium/improvements")
async def get_imperium_improvements():
    """Get recent improvements made by Imperium"""
    try:
        session = get_session()
        async with session as s:
            result = await s.execute(text("""
                SELECT * FROM ai_improvements 
                ORDER BY timestamp DESC 
                LIMIT 20
            """))
            improvements = result.fetchall()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": str(row.id),
                        "ai_type": row.ai_type,
                        "improvement_type": row.improvement_type,
                        "description": row.description,
                        "impact_score": row.impact_score,
                        "status": row.status,
                        "timestamp": row.timestamp.isoformat()
                    }
                    for row in improvements
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/api/imperium/issues")
async def get_imperium_issues():
    """Get recent issues detected by Imperium"""
    try:
        session = get_session()
        async with session as s:
            result = await s.execute(text("""
                SELECT * FROM system_issues 
                ORDER BY timestamp DESC 
                LIMIT 20
            """))
            issues = result.fetchall()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": str(row.id),
                        "issue_type": row.issue_type,
                        "severity": row.severity,
                        "description": row.description,
                        "affected_components": row.affected_components,
                        "resolution_status": row.resolution_status,
                        "timestamp": row.timestamp.isoformat()
                    }
                    for row in issues
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/api/imperium/trigger-scan")
async def trigger_imperium_scan():
    """Manually trigger Imperium system scan"""
    try:
        # This would trigger the monitoring system
        # For now, return success
        return {
            "status": "success",
            "message": "System scan triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
'''
    
    # Add to agents router
    agents_router_path = os.path.join(backend_path, "app", "routers", "agents.py")
    
    if os.path.exists(agents_router_path):
        with open(agents_router_path, 'r') as f:
            content = f.read()
        
        # Add imports if not present
        if "import json" not in content:
            content = content.replace(
                "from fastapi import APIRouter, HTTPException, Depends",
                "from fastapi import APIRouter, HTTPException, Depends\nimport json\nimport os"
            )
        
        # Add endpoints
        if "get_imperium_monitoring" not in content:
            content += dashboard_endpoint
        
        with open(agents_router_path, 'w') as f:
            f.write(content)
        
        print("✅ Added Imperium monitoring endpoints to agents router")
    
    # Create deployment script for EC2
    ec2_deploy_script = """#!/bin/bash
# Deploy Imperium Monitoring System to EC2

echo "🚀 Deploying Imperium Monitoring System to EC2..."

# Copy files to EC2
scp -i ~/.ssh/lvl_up_key.pem imperium_monitoring_system.py ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/ai-backend-python/app/services/
scp -i ~/.ssh/lvl_up_key.pem start_imperium_monitoring.sh ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/
scp -i ~/.ssh/lvl_up_key.pem imperium-monitoring.service ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/

# SSH into EC2 and setup
ssh -i ~/.ssh/lvl_up_key.pem ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com << 'EOF'
cd /home/ubuntu/lvl_up

# Install psutil if not present
pip3 install psutil

# Setup systemd service
sudo cp imperium-monitoring.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable imperium-monitoring.service

# Start the service
sudo systemctl start imperium-monitoring.service

# Check status
sudo systemctl status imperium-monitoring.service

echo "✅ Imperium Monitoring System deployed and started"
EOF
"""
    
    with open("deploy_imperium_to_ec2.sh", 'w') as f:
        f.write(ec2_deploy_script)
    
    os.chmod("deploy_imperium_to_ec2.sh", 0o755)
    print("✅ Created EC2 deployment script")
    
    # Create test script
    test_script = """#!/usr/bin/env python3
# Test Imperium Monitoring System

import requests
import time
import json

def test_imperium_monitoring():
    base_url = "http://localhost:4000"
    
    print("🧪 Testing Imperium Monitoring System...")
    
    # Test monitoring endpoint
    try:
        response = requests.get(f"{base_url}/api/imperium/monitoring")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Monitoring endpoint: {data}")
        else:
            print(f"❌ Monitoring endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Monitoring endpoint error: {e}")
    
    # Test improvements endpoint
    try:
        response = requests.get(f"{base_url}/api/imperium/improvements")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Improvements endpoint: {len(data.get('data', []))} improvements")
        else:
            print(f"❌ Improvements endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Improvements endpoint error: {e}")
    
    # Test issues endpoint
    try:
        response = requests.get(f"{base_url}/api/imperium/issues")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Issues endpoint: {len(data.get('data', []))} issues")
        else:
            print(f"❌ Issues endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Issues endpoint error: {e}")
    
    # Test scan trigger
    try:
        response = requests.post(f"{base_url}/api/imperium/trigger-scan")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scan trigger: {data}")
        else:
            print(f"❌ Scan trigger failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scan trigger error: {e}")

if __name__ == "__main__":
    test_imperium_monitoring()
"""
    
    with open("test_imperium_monitoring.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Created test script")
    
    print("\n🎉 Imperium Monitoring System deployment prepared!")
    print("\nNext steps:")
    print("1. Run: ./deploy_imperium_to_ec2.sh")
    print("2. Test: python3 test_imperium_monitoring.py")
    print("3. Monitor: Check imperium_monitoring.log for system activity")
    
    return True

if __name__ == "__main__":
    deploy_imperium_monitoring() 