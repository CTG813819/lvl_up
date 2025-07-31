# Deploy All AI Test Generation Fix to EC2
# This script deploys the enhanced automatic custodes service to ensure ALL AIs get tested

Write-Host "🚀 Deploying All AI Test Generation Fix to EC2..." -ForegroundColor Green

# Configuration
$PEM_FILE = "C:\projects\lvl_up\New.pem"
$EC2_HOST = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
$REMOTE_PATH = "/home/ubuntu/ai-backend-python/"

# Check if PEM file exists
if (-not (Test-Path $PEM_FILE)) {
    Write-Host "❌ PEM file not found: $PEM_FILE" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Deploying enhanced automatic custodes service..." -ForegroundColor Yellow

# Create the enhanced automatic custodes service locally first
$enhanced_service_content = @'
#!/usr/bin/env python3
"""
Enhanced Automatic Custodes Testing Service
Ensures ALL AIs get tested with proper fallback handling
"""

import time
import requests
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-backend-python/enhanced_custodes_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"
REGULAR_TEST_INTERVAL = 1 * 60 * 60  # 1 hour in seconds
AI_TYPES = ["imperium", "guardian", "conquest", "sandbox"]

def check_backend_status():
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/custody/", timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Backend status check failed: {e}")
        return False

def force_test_for_ai(ai_type: str):
    """Force test for a specific AI with enhanced error handling"""
    try:
        logger.info(f"🧪 Testing {ai_type} AI...")
        
        # Try the main test endpoint first
        response = requests.post(
            f"{BACKEND_URL}/api/custody/test/{ai_type}/force",
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ {ai_type} test completed: {result.get('status', 'unknown')}")
            return {"status": "success", "ai_type": ai_type, "result": result}
        else:
            logger.warning(f"⚠️ {ai_type} main test failed: {response.status_code}, trying fallback...")
            
            # Try fallback endpoint
            fallback_response = requests.post(
                f"{BACKEND_URL}/api/custody/fallback/test/{ai_type}",
                timeout=60
            )
            
            if fallback_response.status_code == 200:
                fallback_result = fallback_response.json()
                logger.info(f"✅ {ai_type} fallback test completed: {fallback_result.get('status', 'unknown')}")
                return {"status": "success", "ai_type": ai_type, "result": fallback_result, "method": "fallback"}
            else:
                logger.error(f"❌ {ai_type} both main and fallback tests failed")
                return {"status": "failed", "ai_type": ai_type, "error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        logger.error(f"❌ Error testing {ai_type}: {str(e)}")
        return {"status": "error", "ai_type": ai_type, "error": str(e)}

def force_tests_for_all_ais():
    """Force tests for ALL AIs with comprehensive error handling"""
    logger.info("🚀 Starting comprehensive tests for ALL AIs...")
    
    results = {}
    success_count = 0
    
    for ai_type in AI_TYPES:
        result = force_test_for_ai(ai_type)
        results[ai_type] = result
        
        if result.get('status') == 'success':
            success_count += 1
    
    logger.info(f"📊 Test Results Summary:")
    logger.info(f"   Total AIs: {len(AI_TYPES)}")
    logger.info(f"   Successful: {success_count}")
    logger.info(f"   Failed: {len(AI_TYPES) - success_count}")
    
    # Log individual results
    for ai_type, result in results.items():
        status_icon = "✅" if result.get('status') == 'success' else "❌"
        logger.info(f"   {status_icon} {ai_type}: {result.get('status', 'unknown')}")
    
    return results

def main():
    """Main service loop"""
    logger.info("🛡️ Starting Enhanced Automatic Custodes Testing Service")
    
    last_test_time = datetime.now() - timedelta(hours=5)  # Force immediate test
    
    while True:
        try:
            current_time = datetime.now()
            
            # Check if backend is running
            if not check_backend_status():
                logger.warning("Backend is not running, waiting...")
                time.sleep(60)
                continue
            
            # Run tests every hour
            if current_time - last_test_time >= timedelta(hours=1):
                logger.info("🕐 Running comprehensive tests for ALL AIs...")
                results = force_tests_for_all_ais()
                last_test_time = current_time
                
                # Log summary
                success_count = sum(1 for r in results.values() if r.get('status') == 'success')
                logger.info(f"🎯 Hourly test cycle completed: {success_count}/{len(AI_TYPES)} AIs tested successfully")
            
            # Sleep for 5 minutes before next check
            time.sleep(300)
            
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            break
        except Exception as e:
            logger.error(f"Service error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
'@

# Save the enhanced service locally
$enhanced_service_content | Out-File -FilePath "enhanced_automatic_custodes_service.py" -Encoding UTF8

Write-Host "✅ Enhanced service created locally" -ForegroundColor Green

# Deploy to EC2
Write-Host "📤 Deploying to EC2..." -ForegroundColor Yellow

try {
    # Copy the enhanced service to EC2
    scp -i $PEM_FILE -o StrictHostKeyChecking=no "enhanced_automatic_custodes_service.py" "${EC2_HOST}:${REMOTE_PATH}"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Enhanced service deployed to EC2" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to deploy enhanced service" -ForegroundColor Red
        exit 1
    }
    
    # Create deployment script on EC2
    $deployment_script = @'
#!/bin/bash
echo "🔧 Deploying enhanced automatic custodes service..."

# Stop the old service if running
echo "🛑 Stopping old automatic custodes service..."
sudo systemctl stop automatic-custodes 2>/dev/null || true
sudo pkill -f "run_automatic_custodes_simple.py" 2>/dev/null || true

# Make the new service executable
chmod +x /home/ubuntu/ai-backend-python/enhanced_automatic_custodes_service.py

# Create systemd service file
sudo tee /etc/systemd/system/enhanced-automatic-custodes.service > /dev/null <<EOF
[Unit]
Description=Enhanced Automatic Custodes Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
ExecStart=/usr/bin/python3 /home/ubuntu/ai-backend-python/enhanced_automatic_custodes_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable enhanced-automatic-custodes
sudo systemctl start enhanced-automatic-custodes

# Check service status
echo "📊 Service status:"
sudo systemctl status enhanced-automatic-custodes --no-pager

echo "✅ Enhanced automatic custodes service deployed and started!"
echo "📋 Service will now test ALL AIs (imperium, guardian, conquest, sandbox) every hour"
echo "📋 Logs available at: /home/ubuntu/ai-backend-python/enhanced_custodes_service.log"
'@

    # Save deployment script locally
    $deployment_script | Out-File -FilePath "deploy_enhanced_service.sh" -Encoding UTF8
    
    # Copy deployment script to EC2
    scp -i $PEM_FILE -o StrictHostKeyChecking=no "deploy_enhanced_service.sh" "${EC2_HOST}:${REMOTE_PATH}"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deployment script copied to EC2" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to copy deployment script" -ForegroundColor Red
        exit 1
    }
    
    # Execute deployment script on EC2
    Write-Host "🔧 Executing deployment script on EC2..." -ForegroundColor Yellow
    
    ssh -i $PEM_FILE -o StrictHostKeyChecking=no $EC2_HOST "cd $REMOTE_PATH && chmod +x deploy_enhanced_service.sh && ./deploy_enhanced_service.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Enhanced automatic custodes service deployed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 DEPLOYMENT COMPLETE" -ForegroundColor Cyan
        Write-Host "📋 The enhanced service will now:" -ForegroundColor White
        Write-Host "   • Test ALL AIs (imperium, guardian, conquest, sandbox) every hour" -ForegroundColor White
        Write-Host "   • Use fallback system when token limits are hit" -ForegroundColor White
        Write-Host "   • Provide detailed logging for each AI test" -ForegroundColor White
        Write-Host "   • Handle errors gracefully and retry failed tests" -ForegroundColor White
        Write-Host ""
        Write-Host "📊 Monitor the service with:" -ForegroundColor Yellow
        Write-Host "   ssh -i $PEM_FILE $EC2_HOST 'sudo journalctl -u enhanced-automatic-custodes -f'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📋 Check logs at:" -ForegroundColor Yellow
        Write-Host "   ssh -i $PEM_FILE $EC2_HOST 'tail -f /home/ubuntu/ai-backend-python/enhanced_custodes_service.log'" -ForegroundColor Gray
    } else {
        Write-Host "❌ Deployment failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Deployment error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 All AI Test Generation Fix Deployed Successfully!" -ForegroundColor Green 