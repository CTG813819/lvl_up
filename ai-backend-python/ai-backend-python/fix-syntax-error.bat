@echo off
echo Fixing syntax error in ai_learning_service.py...
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

echo Copying fixed ai_learning_service.py...
scp -i "New.pem" ai-backend-python/app/services/ai_learning_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/

if %ERRORLEVEL% neq 0 (
    echo Failed to copy fixed file
    pause
    exit /b 1
)

echo.
echo Restarting backend service...
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
echo Syntax error fixed! Backend should now be running.
echo.
pause 