@echo off
REM Training Ground System - EC2 Deployment Script (Batch)
REM ======================================================
REM This script deploys the training ground system to your EC2 instance

setlocal enabledelayedexpansion

REM Configuration
set PEM_PATH=C:\projects\lvl_up\New.pem
set EC2_HOST=ec2-34-202-215-209.compute-1.amazonaws.com
set EC2_USER=ubuntu
set REMOTE_PATH=/home/ubuntu/ai-backend-python

echo ==========================================
echo   TRAINING GROUND SYSTEM DEPLOYMENT
echo ==========================================
echo.

REM Check if PEM file exists
if not exist "%PEM_PATH%" (
    echo [ERROR] PEM file not found at: %PEM_PATH%
    echo Please update the PEM_PATH variable or ensure the file exists
    pause
    exit /b 1
)
echo [SUCCESS] PEM file found: %PEM_PATH%

REM Check if required files exist
set REQUIRED_FILES=training_ground_server.py app\routers\training_ground.py app\services\sandbox_ai_service.py start_training_ground.sh
for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo [ERROR] Required file not found: %%f
        echo Please ensure all required files are in the current directory
        pause
        exit /b 1
    )
)
echo [SUCCESS] All required files found

REM Test EC2 connection
echo [INFO] Testing connection to EC2...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "echo 'Connection successful'"
if errorlevel 1 (
    echo [ERROR] Cannot connect to EC2. Please check your credentials and network connection.
    pause
    exit /b 1
)
echo [SUCCESS] EC2 connection test successful

REM Deploy files
echo [INFO] Starting deployment to EC2...
for %%f in (%REQUIRED_FILES%) do (
    echo [INFO] Deploying %%f...
    scp -i "%PEM_PATH%" %%f %EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/
    if errorlevel 1 (
        echo [ERROR] Failed to deploy %%f
        pause
        exit /b 1
    )
    echo [SUCCESS] Successfully deployed %%f
)

REM Setup permissions and start services on EC2
echo [INFO] Setting up training ground system on EC2...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "cd %REMOTE_PATH% && chmod +x start_training_ground.sh"

REM Stop any existing training ground server
echo [INFO] Stopping any existing training ground server...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "cd %REMOTE_PATH% && pkill -f training_ground_server.py || true"

REM Start the training ground server
echo [INFO] Starting training ground server on port 8002...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "cd %REMOTE_PATH% && ./start_training_ground.sh"

REM Wait a moment for the server to start
timeout /t 5 /nobreak > nul

REM Test the training ground server
echo [INFO] Testing training ground server...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "curl -s http://localhost:8002/health"
if errorlevel 1 (
    echo [WARNING] Training ground server health check failed
    echo [INFO] You may need to manually start the server
) else (
    echo [SUCCESS] Training ground server is healthy and running
)

REM Create systemd service for auto-start
echo [INFO] Creating systemd service for auto-start...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "sudo tee /etc/systemd/system/training-ground.service > /dev/null << 'EOF'
[Unit]
Description=Training Ground Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=%REMOTE_PATH%
Environment=PATH=%REMOTE_PATH%/venv/bin
ExecStart=%REMOTE_PATH%/venv/bin/python training_ground_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

REM Enable and start the service
echo [INFO] Enabling and starting training ground service...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "sudo systemctl daemon-reload && sudo systemctl enable training-ground && sudo systemctl start training-ground"

REM Check service status
echo [INFO] Checking service status...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "sudo systemctl status training-ground --no-pager"

echo.
echo ==========================================
echo   DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo [INFO] Training Ground System Details:
echo - Server: http://%EC2_HOST%:8002
echo - Health Check: http://%EC2_HOST%:8002/health
echo - API Documentation: http://%EC2_HOST%:8002/docs
echo.
echo [INFO] Available endpoints:
echo - POST /custody/training-ground/scenario
echo - POST /custody/training-ground/deploy
echo - POST /custody/weapons/save
echo - GET /custody/weapons/list
echo - POST /custody/weapons/use
echo - GET /custody/training-ground/status
echo.
echo [INFO] Service management:
echo - Check status: sudo systemctl status training-ground
echo - Start service: sudo systemctl start training-ground
echo - Stop service: sudo systemctl stop training-ground
echo - Restart service: sudo systemctl restart training-ground
echo - View logs: sudo journalctl -u training-ground -f
echo.
echo [INFO] The training ground server will automatically start on boot
echo.
pause 