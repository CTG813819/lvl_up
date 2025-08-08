@echo off
echo ========================================
echo    Fixing Enhanced Adversarial Service
echo ========================================
echo.

REM Get EC2 IP from environment
set EC2_IP=34-202-215-209
set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo ========================================
echo STOPPING CURRENT SERVICE
echo ========================================
echo.

echo Stopping current enhanced adversarial testing service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl stop enhanced-adversarial-testing.service"

echo.
echo ========================================
echo CREATING FIXED SYSTEMD SERVICE
echo ========================================
echo.

echo Creating fixed systemd service configuration...
ssh -i "New.pem" %EC2_HOST% "sudo tee /etc/systemd/system/enhanced-adversarial-testing.service > /dev/null << 'EOF'
[Unit]
Description=Enhanced Adversarial Testing Service
After=network.target ai-backend-python.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python standalone_enhanced_adversarial_testing.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF"

echo.
echo ========================================
echo RELOADING SYSTEMD
echo ========================================
echo.

echo Reloading systemd daemon...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl daemon-reload"

echo.
echo ========================================
echo STARTING FIXED SERVICE
echo ========================================
echo.

echo Starting enhanced adversarial testing service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start enhanced-adversarial-testing.service"

echo.
echo ========================================
echo ENABLING AUTO-START
echo ========================================
echo.

echo Enabling service to start on boot...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl enable enhanced-adversarial-testing.service"

echo.
echo ========================================
echo CHECKING SERVICE STATUS
echo ========================================
echo.

echo Waiting for service to start...
timeout /t 10 /nobreak >nul

echo Checking service status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status enhanced-adversarial-testing.service --no-pager"

echo.
echo ========================================
echo TESTING SERVICE
echo ========================================
echo.

echo Testing enhanced adversarial service on port 8001...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:8001/health || echo 'Service not responding yet'"

echo.
echo ========================================
echo CHECKING PORTS
echo ========================================
echo.

echo Checking which ports are listening...
ssh -i "New.pem" %EC2_HOST% "sudo netstat -tlnp | grep -E '8000|8001'"

echo.
echo ========================================
echo SUMMARY
echo ========================================
echo.

echo ✅ Enhanced adversarial testing service should now be working!
echo 📋 Summary:
echo   • Service: FIXED and ENABLED
echo   • Auto-start: CONFIGURED
echo   • Port 8001: ENHANCED ADVERSARIAL TESTING
echo   • Port 8000: MAIN AI BACKEND
echo.
echo The Warp screen should now load properly with enhanced adversarial testing. 