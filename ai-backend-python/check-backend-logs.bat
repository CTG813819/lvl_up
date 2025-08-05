@echo off
echo Checking backend logs and fixing service configuration...
echo.

REM Get EC2 IP from environment or use default
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

REM Convert IP to EC2 hostname format
set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo Checking backend logs...
ssh -i "New.pem" %EC2_HOST% "sudo journalctl -u ai-backend-python -n 20 --no-pager"

echo.
echo Checking current service configuration...
ssh -i "New.pem" %EC2_HOST% "sudo cat /etc/systemd/system/ai-backend-python.service"

echo.
echo Checking virtual environment...
ssh -i "New.pem" %EC2_HOST% "ls -la /home/ubuntu/ai-backend-python/venv/bin/"

echo.
echo Testing Python manually...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python -c 'import sys; print(sys.executable)'"

echo.
echo Updating systemd service configuration...
ssh -i "New.pem" %EC2_HOST% "sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo.
echo Reloading systemd and restarting service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl daemon-reload"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl stop ai-backend-python"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo.
echo Checking backend status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo Testing backend...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:4000/health"

echo.
echo Testing from local machine...
curl -s http://%EC2_IP%:4000/health

echo.
echo Service configuration updated! Backend should now be running.
echo.
pause 