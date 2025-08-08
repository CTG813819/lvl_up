@echo off
echo Fixing all backend issues...
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

echo Installing dependencies in virtual environment...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && pip install aiohttp>=3.8.0 joblib>=1.3.2 scikit-learn>=1.3.0"

echo.
echo Unmasking and fixing systemd service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl unmask ai-backend-python"

echo.
echo Creating new systemd service file...
ssh -i "New.pem" %EC2_HOST% "sudo bash -c 'cat > /etc/systemd/system/ai-backend-python.service << \"EOF\"
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
Environment=DATABASE_URL=\"postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb\"

[Install]
WantedBy=multi-user.target
EOF'"

echo.
echo Reloading systemd and starting service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl daemon-reload"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl enable ai-backend-python"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 15 /nobreak >nul

echo.
echo Checking backend status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo Testing backend locally...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:4000/health"

echo.
echo Testing from local machine...
curl -s http://%EC2_IP%:4000/health

echo.
echo Testing Conquest AI...
curl -s http://%EC2_IP%:4000/api/conquest/status

echo.
echo Testing AI Growth System...
curl -s http://%EC2_IP%:4000/api/growth/status

echo.
echo Testing AI Agents...
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo All issues fixed! Complete AI System should now be running.
echo.
echo Available endpoints:
echo   - POST http://%EC2_IP%:4000/api/conquest/create-app
echo   - GET  http://%EC2_IP%:4000/api/conquest/status
echo   - POST http://%EC2_IP%:4000/api/agents/run/all
echo   - GET  http://%EC2_IP%:4000/api/growth/status
echo.
pause 