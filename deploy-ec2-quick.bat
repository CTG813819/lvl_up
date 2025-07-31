@echo off
echo 🚀 Quick EC2 Deployment
echo ======================

set EC2_IP=44.204.184.21
set KEY_FILE=New.pem

echo [INFO] Deploying to EC2: %EC2_IP%
echo [INFO] Using key file: %KEY_FILE%
echo.

REM Check if key file exists
if not exist "%KEY_FILE%" (
    echo ❌ Key file %KEY_FILE% not found
    echo Please place your New.pem file in the project root directory
    pause
    exit /b 1
)

echo 📦 Building backend...
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

echo 📤 Uploading to EC2...
scp -i "..\%KEY_FILE%" ..\ai-learning-backend.zip ubuntu@%EC2_IP%:~/
if errorlevel 1 (
    echo ❌ Upload failed
    pause
    exit /b 1
)

echo 🚀 Deploying on EC2...
ssh -i "..\%KEY_FILE%" ubuntu@%EC2_IP% "bash -s" << 'EOF'
cd /home/ubuntu
unzip -o ai-learning-backend.zip -d ai-learning-backend
cd ai-learning-backend
npm install --production
pm2 stop ai-learning-backend || true
pm2 delete ai-learning-backend || true
pm2 start src/index.js --name ai-learning-backend --node-args="--max-old-space-size=4096"
pm2 save
pm2 status
EOF

if errorlevel 1 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo 🧹 Cleaning up...
del ..\ai-learning-backend.zip

echo.
echo ✅ EC2 deployment completed!
echo.
echo 🌐 Backend is running at: http://%EC2_IP%:4000
echo.
echo 🔍 To check status:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "pm2 status"
echo.
echo 📋 To view logs:
echo    ssh -i %KEY_FILE% ubuntu@%EC2_IP% "pm2 logs ai-learning-backend"
echo.

pause 