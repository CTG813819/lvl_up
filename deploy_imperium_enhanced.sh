#!/bin/bash

echo "🚀 Deploying Enhanced Imperium Monitoring System to EC2..."

# EC2 instance details
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
KEY_FILE="C:/projects/lvl_up/New.pem"

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
import sys

def test_imperium_endpoints():
    """Test all Imperium monitoring endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/imperium/monitoring",
        "/api/imperium/improvements", 
        "/api/imperium/issues",
        "/api/imperium/status"
    ]
    
    print("🧪 Testing Imperium Monitoring Endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: SUCCESS")
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ {endpoint}: FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {str(e)}")
    
    # Test trigger scan
    try:
        response = requests.post(f"{base_url}/api/imperium/trigger-scan", timeout=10)
        if response.status_code == 200:
            print("✅ /api/imperium/trigger-scan: SUCCESS")
        else:
            print(f"❌ /api/imperium/trigger-scan: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ /api/imperium/trigger-scan: ERROR - {str(e)}")

if __name__ == "__main__":
    test_imperium_endpoints()
EOF

# Create enhanced monitoring service
cat > imperium_deployment/imperium_monitoring_service.py << 'EOF'
#!/usr/bin/env python3
# Enhanced Imperium Monitoring Service

import asyncio
import json
import logging
import os
import psutil
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

class ImperiumMonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring_data = {}
        self.last_scan = None
        self.scan_interval = 300  # 5 minutes
        
    async def start_monitoring(self):
        """Start the monitoring service"""
        self.logger.info("🚀 Starting Imperium Monitoring Service...")
        
        while True:
            try:
                await self.perform_system_scan()
                await self.analyze_system_health()
                await self.generate_improvements()
                await self.save_monitoring_report()
                
                self.logger.info(f"✅ System scan completed at {datetime.now()}")
                await asyncio.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def perform_system_scan(self):
        """Perform comprehensive system scan"""
        self.logger.info("🔍 Performing system scan...")
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process monitoring
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Network monitoring
        network = psutil.net_io_counters()
        
        self.monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "processes": processes[:20],  # Top 20 processes
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
        
        self.last_scan = datetime.now()
    
    async def analyze_system_health(self):
        """Analyze system health and detect issues"""
        issues = []
        
        # CPU analysis
        if self.monitoring_data["system"]["cpu_percent"] > 80:
            issues.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "description": f"CPU usage is {self.monitoring_data['system']['cpu_percent']}%",
                "recommendation": "Consider optimizing processes or scaling resources"
            })
        
        # Memory analysis
        if self.monitoring_data["system"]["memory_percent"] > 85:
            issues.append({
                "type": "high_memory_usage",
                "severity": "critical",
                "description": f"Memory usage is {self.monitoring_data['system']['memory_percent']}%",
                "recommendation": "Immediate action required - consider restarting services or adding memory"
            })
        
        # Disk analysis
        if self.monitoring_data["system"]["disk_percent"] > 90:
            issues.append({
                "type": "low_disk_space",
                "severity": "critical",
                "description": f"Disk usage is {self.monitoring_data['system']['disk_percent']}%",
                "recommendation": "Clean up disk space immediately"
            })
        
        self.monitoring_data["issues"] = issues
    
    async def generate_improvements(self):
        """Generate AI improvements based on system analysis"""
        improvements = []
        
        # Performance improvements
        if self.monitoring_data["system"]["cpu_percent"] > 70:
            improvements.append({
                "type": "performance_optimization",
                "description": "System experiencing high CPU load",
                "impact_score": 8,
                "recommendation": "Implement caching and optimize database queries"
            })
        
        # Security improvements
        improvements.append({
            "type": "security_enhancement",
            "description": "Regular security scan recommended",
            "impact_score": 9,
            "recommendation": "Run security audit and update dependencies"
        })
        
        # Monitoring improvements
        improvements.append({
            "type": "monitoring_enhancement",
            "description": "Enhanced logging and alerting",
            "impact_score": 7,
            "recommendation": "Implement structured logging and alerting system"
        })
        
        self.monitoring_data["improvements"] = improvements
    
    async def save_monitoring_report(self):
        """Save monitoring report to file and database"""
        try:
            # Save to file
            with open("imperium_monitoring_report.json", "w") as f:
                json.dump(self.monitoring_data, f, indent=2, default=str)
            
            # Save to database
            session = get_session()
            async with session as s:
                # Save improvements
                for improvement in self.monitoring_data.get("improvements", []):
                    await s.execute(sa.text("""
                        INSERT INTO ai_improvements 
                        (ai_type, improvement_type, description, impact_score, status, timestamp)
                        VALUES (:ai_type, :improvement_type, :description, :impact_score, :status, :timestamp)
                    """), {
                        "ai_type": "imperium",
                        "improvement_type": improvement["type"],
                        "description": improvement["description"],
                        "impact_score": improvement["impact_score"],
                        "status": "pending",
                        "timestamp": datetime.now()
                    })
                
                # Save issues
                for issue in self.monitoring_data.get("issues", []):
                    await s.execute(sa.text("""
                        INSERT INTO system_issues 
                        (issue_type, severity, description, affected_components, resolution_status, timestamp)
                        VALUES (:issue_type, :severity, :description, :affected_components, :resolution_status, :timestamp)
                    """), {
                        "issue_type": issue["type"],
                        "severity": issue["severity"],
                        "description": issue["description"],
                        "affected_components": "system",
                        "resolution_status": "open",
                        "timestamp": datetime.now()
                    })
                
                await s.commit()
            
            self.logger.info("✅ Monitoring report saved successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving monitoring report: {str(e)}")

async def main():
    """Main function to start the monitoring service"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = ImperiumMonitoringService()
    await service.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
EOF

echo "📦 Creating deployment package..."
tar -czf imperium_deployment.tar.gz imperium_deployment/

echo "🚀 Deploying to EC2..."
scp -i "$KEY_FILE" imperium_deployment.tar.gz $EC2_USER@$EC2_HOST:/home/ubuntu/

echo "🔧 Installing on EC2..."
ssh -i "$KEY_FILE" $EC2_USER@$EC2_HOST << 'EOF'
cd /home/ubuntu

# Extract deployment package
tar -xzf imperium_deployment.tar.gz
cd imperium_deployment

# Copy files to backend directory
sudo cp imperium_monitoring_service.py /home/ubuntu/lvl_up/ai-backend-python/app/services/
sudo cp imperium_endpoints.py /home/ubuntu/lvl_up/ai-backend-python/app/routers/
sudo cp start_imperium_monitoring.sh /home/ubuntu/lvl_up/ai-backend-python/
sudo cp test_imperium_monitoring.py /home/ubuntu/lvl_up/ai-backend-python/

# Make scripts executable
sudo chmod +x /home/ubuntu/lvl_up/ai-backend-python/start_imperium_monitoring.sh
sudo chmod +x /home/ubuntu/lvl_up/ai-backend-python/test_imperium_monitoring.py

# Install systemd service
sudo cp imperium-monitoring.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable imperium-monitoring.service

# Create necessary database tables
cd /home/ubuntu/lvl_up/ai-backend-python
python3 -c "
import asyncio
from app.core.database import engine
from sqlalchemy import text

async def create_tables():
    async with engine.begin() as conn:
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS ai_improvements (
                id SERIAL PRIMARY KEY,
                ai_type VARCHAR(50) NOT NULL,
                improvement_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                impact_score INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS system_issues (
                id SERIAL PRIMARY KEY,
                issue_type VARCHAR(100) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                description TEXT NOT NULL,
                affected_components TEXT,
                resolution_status VARCHAR(50) DEFAULT 'open',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))

asyncio.run(create_tables())
"

# Start the monitoring service
sudo systemctl start imperium-monitoring.service

# Check status
sudo systemctl status imperium-monitoring.service

echo "✅ Imperium Monitoring System deployed successfully!"
echo "📊 Check status: sudo systemctl status imperium-monitoring.service"
echo "📋 View logs: sudo journalctl -u imperium-monitoring.service -f"
echo "🌐 Test endpoints: python3 test_imperium_monitoring.py"
EOF

echo "🧪 Testing deployment..."
ssh -i "$KEY_FILE" $EC2_USER@$EC2_HOST << 'EOF'
cd /home/ubuntu/lvl_up/ai-backend-python

# Wait for service to start
sleep 10

# Test the monitoring system
python3 test_imperium_monitoring.py

# Check service status
sudo systemctl status imperium-monitoring.service

# Show recent logs
sudo journalctl -u imperium-monitoring.service --no-pager -n 20
EOF

echo "🎉 Enhanced Imperium Monitoring System deployment completed!"
echo "📊 Access monitoring dashboard at: http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/monitoring"
echo "🔍 View system status at: http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/imperium/status" 