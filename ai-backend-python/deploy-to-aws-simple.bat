@echo off
echo 🚀 Quick AWS Deployment - Replace PC Backend
echo.

REM Configuration - UPDATE THESE VALUES
set EC2_IP=44.204.184.21
set KEY_FILE=New.pem

echo 📋 Configuration:
echo EC2 IP: %EC2_IP%
echo Key File: %KEY_FILE%
echo.

REM Check if key file exists
if not exist "%KEY_FILE%" (
    echo ❌ Key file %KEY_FILE% not found in current directory
    echo Please place your New.pem file in the project root directory
    pause
    exit /b 1
)

REM Check if values are set
if "%EC2_IP%"=="your-ec2-ip-here" (
    echo ❌ Please update EC2_IP in this script with your AWS EC2 IP address
    pause
    exit /b 1
)

echo 📦 Building application...
cd ai-backend
call npm install --production
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo 📦 Creating deployment package...
powershell -Command "Compress-Archive -Path * -DestinationPath ..\ai-learning-backend.zip -Force"
if errorlevel 1 (
    echo ❌ Package creation failed
    pause
    exit /b 1
)

echo 📤 Uploading to AWS EC2...
scp -i "..\%KEY_FILE%" ..\ai-learning-backend.zip ubuntu@%EC2_IP%:~/
if errorlevel 1 (
    echo ❌ Upload failed - check your EC2 IP and key file
    pause
    exit /b 1
)

echo 🚀 Deploying on AWS EC2...
ssh -i "..\%KEY_FILE%" ubuntu@%EC2_IP% "bash -s" < ..\deploy-commands.sh
if errorlevel 1 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo 🧹 Cleaning up...
del ..\ai-learning-backend.zip

echo.
echo ✅ AWS deployment completed!
echo.
echo 🌐 Your backend is now running at: http://%EC2_IP%:4000
echo.
echo 📱 Update your Flutter app with this URL:
echo    http://%EC2_IP%:4000
echo.
echo 🔍 To check backend status:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "pm2 status"
echo.
echo 📋 To view logs:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "pm2 logs ai-learning-backend"
echo.
pause 