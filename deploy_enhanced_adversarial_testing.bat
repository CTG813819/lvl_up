@echo off
echo ========================================
echo    Deploying Enhanced Adversarial Testing
echo ========================================
echo.

REM Get EC2 IP from environment or use default
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    set EC2_IP=34.202.215.209
)

set EC2_HOST=ubuntu@%EC2_IP%

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo ========================================
echo UPLOADING ENHANCED ADVERSARIAL TESTING
echo ========================================
echo.

echo Uploading standalone enhanced adversarial testing service...
scp -i "New.pem" "ai-backend-python/standalone_enhanced_adversarial_testing.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/

echo.
echo ========================================
echo INSTALLING DEPENDENCIES
echo ========================================
echo.

echo Installing FastAPI and uvicorn dependencies...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && pip install fastapi uvicorn structlog"

echo.
echo ========================================
echo CREATING SYSTEMD SERVICE
echo ========================================
echo.

echo Creating systemd service for enhanced adversarial testing...
ssh -i "New.pem" %EC2_HOST% "sudo tee /etc/systemd/system/enhanced-adversarial-testing.service > /dev/null << 'EOF'
[Unit]
Description=Enhanced Adversarial Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python standalone_enhanced_adversarial_testing.py
Restart=always
RestartSec=10

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
echo STARTING SERVICE
echo ========================================
echo.

echo Enabling and starting enhanced adversarial testing service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl enable enhanced-adversarial-testing"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start enhanced-adversarial-testing"

echo.
echo ========================================
echo WAITING FOR SERVICE TO START
echo ========================================
echo.

echo Waiting for service to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo CHECKING SERVICE STATUS
echo ========================================
echo.

echo Checking service status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status enhanced-adversarial-testing --no-pager"

echo.
echo ========================================
echo TESTING ENDPOINTS
echo ========================================
echo.

echo Testing health endpoint...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:8001/health"

echo.
echo Testing overview endpoint...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:8001/ | head -c 200"

echo.
echo ========================================
echo CHECKING PORTS
echo ========================================
echo.

echo Checking if port 8001 is listening...
ssh -i "New.pem" %EC2_HOST% "netstat -tlnp | grep 8001"

echo.
echo ========================================
echo TESTING FROM LOCAL MACHINE
echo ========================================
echo.

echo Testing from local machine...
curl -s http://%EC2_IP%:8001/health

echo.
echo ========================================
echo DEPLOYMENT COMPLETE
echo ========================================
echo.

echo Enhanced Adversarial Testing Service deployed successfully!
echo.
echo Service Details:
echo - URL: http://%EC2_IP%:8001
echo - Health Check: http://%EC2_IP%:8001/health
echo - Overview: http://%EC2_IP%:8001/
echo - Generate Test: POST http://%EC2_IP%:8001/generate-and-execute
echo.
echo Flutter app should now be able to connect to the enhanced adversarial testing service.
echo.

pause 