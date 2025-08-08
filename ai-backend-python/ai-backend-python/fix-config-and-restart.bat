@echo off
echo ========================================
echo    Fixing Configuration and Restarting
echo ========================================
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

echo ========================================
echo COPYING FIXED CONFIGURATION
echo ========================================
echo.

echo Copying fixed config.py to EC2 instance...
scp -i "New.pem" "ai-backend-python/app/core/config.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/app/core/config.py

echo.
echo ========================================
echo RESTARTING BACKEND SERVICE
echo ========================================
echo.

echo Restarting backend service with fixed configuration...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo CHECKING BACKEND STATUS
echo ========================================
echo.

echo Checking if backend service is running...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager -l"

echo.
echo ========================================
echo TESTING BACKEND CONNECTION
echo ========================================
echo.

echo Testing backend health endpoint...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/health

echo.
echo Testing AI agents status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo ========================================
echo TRIGGERING AI AGENTS
echo ========================================
echo.

echo Triggering all AI agents with fixed configuration...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all

echo.
echo Waiting for agents to process...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo FINAL STATUS CHECK
echo ========================================
echo.

echo Final AI agent status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Testing GitHub integration:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/github/status

echo.
echo ========================================
echo SUCCESS! 🎉
echo ========================================
echo.
echo Configuration has been fixed and backend restarted!
echo All AI agents should now be working with your GitHub credentials.
echo.
pause 