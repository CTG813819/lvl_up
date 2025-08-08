@echo off
echo Fixing backend service and dependencies...
echo.

REM Get EC2 IP from environment
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo Installing missing dependencies...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && pip install aiohttp>=3.8.0 joblib>=1.3.2 scikit-learn>=1.3.0"

echo.
echo Copying service file...
scp -i "New.pem" ai-backend-python.service %EC2_HOST%:/tmp/

echo.
echo Installing service file...
ssh -i "New.pem" %EC2_HOST% "sudo cp /tmp/ai-backend-python.service /etc/systemd/system/"

echo.
echo Reloading and starting service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl daemon-reload"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl enable ai-backend-python"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo.
echo Checking service status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo Testing backend...
curl -s http://%EC2_IP%:4000/health

echo.
echo Testing AI endpoints...
curl -s http://%EC2_IP%:4000/api/conquest/status
curl -s http://%EC2_IP%:4000/api/growth/status
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo Backend should now be running!
pause 