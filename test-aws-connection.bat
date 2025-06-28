@echo off
echo 🔍 Testing AWS EC2 Connection
echo.

REM Configuration
set EC2_IP=44.204.184.21
set KEY_FILE=New.pem

echo 📋 Testing connection to: %EC2_IP%
echo 🔑 Using key file: %KEY_FILE%
echo.

REM Check if key file exists
if not exist "%KEY_FILE%" (
    echo ❌ Key file %KEY_FILE% not found
    echo Please place your New.pem file in the project root directory
    pause
    exit /b 1
)

echo 🔐 Testing SSH connection...
ssh -i "%KEY_FILE%" -o ConnectTimeout=10 -o BatchMode=yes ubuntu@%EC2_IP% "echo 'SSH connection successful'"
if errorlevel 1 (
    echo ❌ SSH connection failed
    echo.
    echo 🔧 Troubleshooting steps:
    echo 1. Check if your EC2 instance is running
    echo 2. Verify the IP address is correct: %EC2_IP%
    echo 3. Check security group allows SSH (port 22)
    echo 4. Verify key file permissions
    echo.
    pause
    exit /b 1
)

echo ✅ SSH connection successful!
echo.

echo 🌐 Testing backend health...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" http://%EC2_IP%:4000/api/health
if errorlevel 1 (
    echo ❌ Backend health check failed
    echo.
    echo 🔧 Backend might not be running. Try:
    echo ssh -i "%KEY_FILE%" ubuntu@%EC2_IP% "pm2 status"
    echo.
) else (
    echo ✅ Backend is responding!
)

echo.
echo 🎉 Connection test completed!
pause 