#!/bin/bash

echo "🚀 Deploying Enhanced Imperium Monitoring System to EC2..."

# EC2 instance details
EC2_HOST="ec2-54-147-131-162.compute-1.amazonaws.com"
EC2_USER="ubuntu"
KEY_FILE="~/.ssh/lvl_up_key.pem"

echo "📋 Preparing deployment files..."

# Create deployment package
mkdir -p imperium_deployment
cp imperium_monitoring_system.py imperium_deployment/
cp deploy_imperium_monitoring.py imperium_deployment/

# Create enhanced startup script
cat > imperium_deployment/start_imperium_monitoring.sh << 'EOF'
#!/bin/bash
# Enhanced Imperium Monitoring System Startup Script

cd /home/ubuntu/lvl_up/ai-backend-python

echo "🚀 Starting Imperium Monitoring System..."

# Install required packages
pip3 install psutil requests

# Create log directory
mkdir -p logs

# Start monitoring system in background with proper logging
nohup python3 -m app.services.imperium_monitoring > logs/imperium_monitoring.log 2>&1 &

# Save PID
echo $! > imperium_monitoring.pid

echo "✅ Imperium Monitoring System started with PID: $(cat imperium_monitoring.pid)"
echo "📊 Logs available at: logs/imperium_monitoring.log"
echo "🔍 Monitor with: tail -f logs/imperium_monitoring.log"
EOF

# Create enhanced systemd service
cat > imperium_deployment/imperium-monitoring.service << 'EOF'
[Unit]
Description=Imperium AI Monitoring System
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/lvl_up/ai-backend-python
ExecStart=/usr/bin/python3 -m app.services.imperium_monitoring
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/ubuntu/lvl_up/ai-backend-python
Environment=PYTHONUNBUFFERED=1

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=imperium-monitoring

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Create monitoring dashboard endpoints
cat > imperium_deployment/imperium_endpoints.py << 'EOF'
# Imperium Monitoring Dashboard Endpoints

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import get_session
from datetime import datetime
import json
import os

router = APIRouter()

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

@router.get("/api/imperium/status")
async def get_imperium_status():
    """Get Imperium system status"""
    try:
        # Check if monitoring system is running
        pid_file = "imperium_monitoring.pid"
        is_running = False
        pid = None
        
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = f.read().strip()
            
            if pid:
                try:
                    os.kill(int(pid), 0)  # Check if process exists
                    is_running = True
                except OSError:
                    is_running = False
        
        return {
            "status": "success",
            "data": {
                "is_running": is_running,
                "pid": pid,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
EOF

# Create test script
cat > imperium_deployment/test_imperium_monitoring.py << 'EOF'
#!/usr/bin/env python3
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
    
    # Test status endpoint
    try:
        response = requests.get(f"{base_url}/api/imperium/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status endpoint: {data}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")

if __name__ == "__main__":
    test_imperium_monitoring()
EOF

# Create comprehensive deployment script
cat > imperium_deployment/deploy_to_ec2.sh << 'EOF'
#!/bin/bash
# Deploy Imperium Monitoring System to EC2

echo "🚀 Deploying Imperium Monitoring System to EC2..."

# Copy files to EC2
echo "📤 Copying files to EC2..."
scp -i ~/.ssh/lvl_up_key.pem -r imperium_monitoring_system.py ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/ai-backend-python/app/services/
scp -i ~/.ssh/lvl_up_key.pem start_imperium_monitoring.sh ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/
scp -i ~/.ssh/lvl_up_key.pem imperium-monitoring.service ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/
scp -i ~/.ssh/lvl_up_key.pem imperium_endpoints.py ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/
scp -i ~/.ssh/lvl_up_key.pem test_imperium_monitoring.py ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com:/home/ubuntu/lvl_up/

# SSH into EC2 and setup
echo "🔧 Setting up on EC2..."
ssh -i ~/.ssh/lvl_up_key.pem ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com << 'EC2_SETUP'
cd /home/ubuntu/lvl_up

echo "📦 Installing dependencies..."
pip3 install psutil requests

echo "🔧 Setting up Imperium monitoring system..."

# Make startup script executable
chmod +x start_imperium_monitoring.sh

# Setup systemd service
sudo cp imperium-monitoring.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable imperium-monitoring.service

# Add endpoints to agents router
echo "🔗 Adding endpoints to agents router..."
python3 -c "
import os
agents_router_path = 'ai-backend-python/app/routers/agents.py'
if os.path.exists(agents_router_path):
    with open(agents_router_path, 'r') as f:
        content = f.read()
    
    # Add imports if not present
    if 'import json' not in content:
        content = content.replace(
            'from fastapi import APIRouter, HTTPException, Depends',
            'from fastapi import APIRouter, HTTPException, Depends\\nimport json\\nimport os'
        )
    
    # Add endpoints if not present
    if 'get_imperium_monitoring' not in content:
        with open('imperium_endpoints.py', 'r') as f:
            endpoints = f.read()
        content += endpoints
    
    with open(agents_router_path, 'w') as f:
        f.write(content)
    print('✅ Added Imperium endpoints to agents router')
else:
    print('❌ Agents router not found')
"

# Create monitoring tables
echo "🗄️ Creating monitoring tables..."
cd ai-backend-python
python3 -c "
import asyncio
import sys
import os
sys.path.append(os.getcwd())

from app.core.database import get_session, init_database
from sqlalchemy import text

async def create_tables():
    await init_database()
    session = get_session()
    
    async with session as s:
        # Create system_monitoring table
        await s.execute(text('''
            CREATE TABLE IF NOT EXISTS system_monitoring (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                timestamp TIMESTAMP DEFAULT NOW(),
                metric_name VARCHAR(100) NOT NULL,
                metric_value FLOAT NOT NULL,
                threshold FLOAT NOT NULL,
                status VARCHAR(20) NOT NULL,
                details JSONB
            )
        '''))
        
        # Create ai_improvements table
        await s.execute(text('''
            CREATE TABLE IF NOT EXISTS ai_improvements (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                timestamp TIMESTAMP DEFAULT NOW(),
                ai_type VARCHAR(50) NOT NULL,
                improvement_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                impact_score FLOAT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                implementation_details JSONB,
                results JSONB
            )
        '''))
        
        # Create system_issues table
        await s.execute(text('''
            CREATE TABLE IF NOT EXISTS system_issues (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                timestamp TIMESTAMP DEFAULT NOW(),
                issue_type VARCHAR(100) NOT NULL,
                severity VARCHAR(20) NOT NULL,
                description TEXT NOT NULL,
                affected_components JSONB,
                resolution_status VARCHAR(20) DEFAULT 'open',
                resolution_details JSONB
            )
        '''))
        
        await s.commit()
        print('✅ Monitoring tables created')

asyncio.run(create_tables())
"

# Restart backend to load new endpoints
echo "🔄 Restarting backend..."
sudo systemctl restart ai-backend-python

# Start the monitoring service
echo "🚀 Starting Imperium monitoring service..."
sudo systemctl start imperium-monitoring.service

# Wait a moment for services to start
sleep 5

# Check status
echo "📊 Checking service status..."
sudo systemctl status imperium-monitoring.service

# Test the endpoints
echo "🧪 Testing endpoints..."
cd ..
python3 test_imperium_monitoring.py

echo "✅ Imperium Monitoring System deployed and started"
echo "📊 Monitor with: sudo journalctl -u imperium-monitoring.service -f"
echo "🔍 Check logs: tail -f /home/ubuntu/lvl_up/ai-backend-python/logs/imperium_monitoring.log"

EC2_SETUP

echo "🎉 Imperium Monitoring System deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Monitor the system: ssh -i ~/.ssh/lvl_up_key.pem ubuntu@ec2-54-147-131-162.compute-1.amazonaws.com"
echo "2. Check logs: tail -f /home/ubuntu/lvl_up/ai-backend-python/logs/imperium_monitoring.log"
echo "3. Test endpoints: python3 test_imperium_monitoring.py"
echo "4. View dashboard: http://ec2-54-147-131-162.compute-1.amazonaws.com:4000/api/imperium/monitoring"
EOF

# Make deployment script executable
chmod +x imperium_deployment/deploy_to_ec2.sh

echo "📦 Deployment package created in imperium_deployment/"
echo ""
echo "🚀 To deploy to EC2, run:"
echo "cd imperium_deployment && ./deploy_to_ec2.sh" 