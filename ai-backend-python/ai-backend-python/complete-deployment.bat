@echo off
echo Completing AI System deployment...
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

echo Installing dependencies and restarting backend...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && pip install joblib>=1.3.2 scikit-learn>=1.3.0 aiohttp>=3.8.0"

echo.
echo Stopping backend service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl stop ai-backend-python"

echo.
echo Starting backend with Complete AI System...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl start ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 15 /nobreak >nul

echo.
echo Checking backend status...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo Testing core endpoints...
ssh -i "New.pem" %EC2_HOST% "curl -s http://localhost:4000/health"

echo.
echo Complete AI System deployment finished!
echo.
echo Testing endpoints from local machine...
echo.

echo Testing Health Check:
curl -s http://%EC2_IP%:4000/health

echo.
echo Testing Conquest AI:
curl -s http://%EC2_IP%:4000/api/conquest/status

echo.
echo Testing AI Growth System:
curl -s http://%EC2_IP%:4000/api/growth/status

echo.
echo Testing AI Agents:
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo Complete AI System is now live and running!
echo.
echo Available endpoints:
echo   - POST http://%EC2_IP%:4000/api/conquest/create-app
echo   - GET  http://%EC2_IP%:4000/api/conquest/status
echo   - POST http://%EC2_IP%:4000/api/agents/run/all
echo   - GET  http://%EC2_IP%:4000/api/growth/status
echo.
pause 