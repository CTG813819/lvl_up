@echo off
REM Check and Start EC2 Backend
REM This script helps diagnose and fix EC2 backend issues

echo 🔍 Checking EC2 Backend Status
echo =============================

set EC2_IP=44.204.184.21
set EC2_USER=ubuntu

echo [INFO] Testing connection to %EC2_IP%:4000...

REM Test port connectivity
powershell -Command "Test-NetConnection -ComputerName %EC2_IP% -Port 4000"

echo.
echo [INFO] Connection test completed.
echo.

if %errorlevel% equ 0 (
    echo [SUCCESS] Port 4000 is accessible!
    echo [INFO] Backend should be working.
) else (
    echo [WARNING] Port 4000 is not accessible.
    echo.
    echo [INFO] Possible issues:
    echo 1. Backend not running on EC2
    echo 2. Security group blocking port 4000
    echo 3. Backend running on different port
    echo.
    echo [INFO] To fix this, SSH into your EC2 and run:
    echo.
    echo ssh -i New.pem %EC2_USER%@%EC2_IP%
    echo.
    echo Then check if backend is running:
    echo pm2 status
    echo netstat -tlnp ^| grep 4000
    echo.
    echo If not running, start it:
    echo cd /home/ubuntu/ai-learning-backend
    echo pm2 start src/index.js --name ai-learning-backend
    echo pm2 save
    echo.
    echo Check security group in AWS Console:
    echo - EC2 ^> Instances ^> Your instance ^> Security tab
    echo - Add inbound rule: Custom TCP, Port 4000, Source 0.0.0.0/0
)

echo.
echo [INFO] After fixing the backend, test again with:
echo test-ec2-connection.bat
echo.

pause 