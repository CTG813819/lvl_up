@echo off
echo ========================================
echo    Restarting Backend with DB Fix
echo ========================================
echo.

REM Configuration
set EC2_IP=34.202.215.209
set EC2_USER=ubuntu
set KEY_FILE=New.pem

echo [INFO] Connecting to EC2 instance: %EC2_USER%@%EC2_IP%
echo.

REM Check if key file exists
if not exist "%KEY_FILE%" (
    echo [ERROR] Key file %KEY_FILE% not found!
    echo Please place your New.pem file in the project root directory
    pause
    exit /b 1
)

echo [INFO] Step 1: Checking current service status...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo [INFO] Step 2: Stopping backend service...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "sudo systemctl stop ai-backend-python"

echo.
echo [INFO] Step 3: Waiting for service to stop...
timeout /t 5 /nobreak >nul

echo.
echo [INFO] Step 4: Starting backend service with updated configuration...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "sudo systemctl start ai-backend-python"

echo.
echo [INFO] Step 5: Waiting for service to start...
timeout /t 10 /nobreak >nul

echo.
echo [INFO] Step 6: Checking service status...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo [INFO] Step 7: Testing backend connectivity...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "curl -s -o /dev/null -w 'HTTP Status: %%{http_code}' http://localhost:8000/api/imperium/status"

echo.
echo [INFO] Step 8: Checking recent logs for database connection issues...
ssh -i "%KEY_FILE%" %EC2_USER%@%EC2_IP% "sudo journalctl -u ai-backend-python --since '5 minutes ago' --no-pager | grep -i 'database\|connection\|pool' | tail -10"

echo.
echo ========================================
echo    Restart Complete
echo ========================================
echo.
echo [INFO] The backend service has been restarted with updated database connection pool settings:
echo       - Pool size increased to 50
echo       - Max overflow increased to 100
echo       - Pool timeout increased to 120 seconds
echo       - LIFO connection management enabled
echo.
echo [INFO] Monitor the logs for any remaining connection issues.
echo.
pause 