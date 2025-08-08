#!/bin/bash

# Enable Automatic Custodes Testing Script
# This script enables automatic Custodes Protocol testing on the EC2 instance

echo "🛡️ Enabling Automatic Custodes Testing on EC2..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Check if the backend is running
echo "📊 Checking backend status..."
if curl -s http://localhost:8000/api/imperium/status > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is not running. Starting it..."
    # Start the backend if it's not running
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    sleep 10
fi

# Enable automatic Custodes testing by updating the service
echo "🔄 Enabling automatic Custodes testing..."

# Create a script to run automatic testing
cat > run_automatic_custodes.py << 'EOF'
#!/usr/bin/env python3
"""
Automatic Custodes Testing Service
Runs Custodes tests automatically based on the configured schedule
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import schedule
import time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.custody_protocol_service import CustodyProtocolService
from app.core.database import init_database
import structlog

logger = structlog.get_logger()

class AutomaticCustodesService:
    def __init__(self):
        self.custody_service = None
        self.ai_types = ['imperium', 'guardian', 'sandbox', 'conquest']
        
    async def initialize(self):
        """Initialize the automatic Custodes service"""
        await init_database()
        self.custody_service = CustodyProtocolService()
        logger.info("🛡️ Automatic Custodes Service initialized")
        
    async def run_regular_tests(self):
        """Run regular Custodes tests every 4 hours"""
        try:
            logger.info("🛡️ Running regular Custodes tests...")
            for ai_type in self.ai_types:
                await self.custody_service.administer_custody_test(ai_type)
                await asyncio.sleep(30)  # Wait 30 seconds between tests
            logger.info("✅ Regular Custodes tests completed")
        except Exception as e:
            logger.error(f"❌ Error in regular tests: {e}")
            
    async def run_comprehensive_tests(self):
        """Run comprehensive Custodes tests daily at 6 AM"""
        try:
            logger.info("🛡️ Running comprehensive Custodes tests...")
            for ai_type in self.ai_types:
                await self.custody_service.administer_custody_test(ai_type)
                await asyncio.sleep(60)  # Wait 1 minute between comprehensive tests
            logger.info("✅ Comprehensive Custodes tests completed")
        except Exception as e:
            logger.error(f"❌ Error in comprehensive tests: {e}")
            
    async def check_and_test_eligibility(self):
        """Check AI eligibility and run tests if needed"""
        try:
            logger.info("🔍 Checking AI eligibility for proposals...")
            for ai_type in self.ai_types:
                # Check if AI needs a test to be eligible for proposals
                can_create_proposals = await self.custody_service._check_proposal_eligibility(ai_type)
                if not can_create_proposals:
                    logger.info(f"🧪 Running eligibility test for {ai_type} AI")
                    await self.custody_service.administer_custody_test(ai_type)
                    await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"❌ Error checking eligibility: {e}")

async def main():
    """Main function to run automatic Custodes testing"""
    service = AutomaticCustodesService()
    await service.initialize()
    
    # Schedule regular tests every 4 hours
    schedule.every(4).hours.do(lambda: asyncio.create_task(service.run_regular_tests()))
    
    # Schedule comprehensive tests daily at 6 AM
    schedule.every().day.at("06:00").do(lambda: asyncio.create_task(service.run_comprehensive_tests()))
    
    # Schedule eligibility checks every 2 hours
    schedule.every(2).hours.do(lambda: asyncio.create_task(service.check_and_test_eligibility()))
    
    logger.info("🛡️ Automatic Custodes testing scheduled:")
    logger.info("   - Regular tests: Every 4 hours")
    logger.info("   - Comprehensive tests: Daily at 6:00 AM")
    logger.info("   - Eligibility checks: Every 2 hours")
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Check every minute

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Make the script executable
chmod +x run_automatic_custodes.py

# Create a systemd service to run automatic Custodes testing
echo "📋 Creating systemd service for automatic Custodes testing..."

sudo tee /etc/systemd/system/automatic-custodes.service > /dev/null << EOF
[Unit]
Description=Automatic Custodes Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
ExecStart=/usr/bin/python3 /home/ubuntu/ai-backend-python/run_automatic_custodes.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
echo "🚀 Enabling and starting automatic Custodes service..."
sudo systemctl daemon-reload
sudo systemctl enable automatic-custodes.service
sudo systemctl start automatic-custodes.service

# Check service status
echo "📊 Checking automatic Custodes service status..."
sudo systemctl status automatic-custodes.service --no-pager

# Show the schedule
echo "📅 Automatic Custodes Testing Schedule:"
echo "   - Regular tests: Every 4 hours"
echo "   - Comprehensive tests: Daily at 6:00 AM"
echo "   - Eligibility checks: Every 2 hours"
echo "   - Service will restart automatically if it fails"

# Test the service by running one test cycle
echo "🧪 Testing automatic Custodes service..."
python3 run_automatic_custodes.py &
sleep 10
pkill -f "run_automatic_custodes.py"

echo "✅ Automatic Custodes testing has been enabled!"
echo "📋 To check service status: sudo systemctl status automatic-custodes.service"
echo "📋 To view logs: sudo journalctl -u automatic-custodes.service -f"
echo "📋 To stop service: sudo systemctl stop automatic-custodes.service" 