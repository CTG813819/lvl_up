@echo off
REM EC2 Deployment Script for LVL UP Backend (Windows)
REM This script helps deploy the backend to EC2 and ensure it works without the PC

echo 🚀 LVL UP Backend EC2 Deployment Script
echo ========================================

REM Configuration
set EC2_IP=44.204.184.21
set EC2_USER=ubuntu
set BACKEND_PORT=4000
set LOCAL_BACKEND_DIR=ai-backend

REM Check if we're in the right directory
if not exist "%LOCAL_BACKEND_DIR%" (
    echo [ERROR] Backend directory '%LOCAL_BACKEND_DIR%' not found!
    echo [INFO] Please run this script from the project root directory
    pause
    exit /b 1
)

echo [INFO] Starting EC2 deployment process...

REM Step 1: Check local backend
echo [INFO] Step 1: Checking local backend...
if exist "%LOCAL_BACKEND_DIR%\package.json" (
    echo [SUCCESS] Backend package.json found
) else (
    echo [ERROR] Backend package.json not found!
    pause
    exit /b 1
)

REM Step 2: Test EC2 connectivity
echo [INFO] Step 2: Testing EC2 connectivity...
ping -n 1 %EC2_IP% >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] EC2 instance is reachable
) else (
    echo [ERROR] Cannot reach EC2 instance at %EC2_IP%
    echo [WARNING] Please check your EC2 instance is running and accessible
    pause
    exit /b 1
)

REM Step 3: Check if backend is already running on EC2
echo [INFO] Step 3: Checking if backend is running on EC2...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend is already running on EC2
    echo [INFO] Backend URL: http://%EC2_IP%:%BACKEND_PORT%
) else (
    echo [WARNING] Backend not running on EC2
    echo [INFO] You'll need to start the backend on your EC2 instance
)

REM Step 4: Create deployment package
echo [INFO] Step 4: Creating deployment package...
set DEPLOY_PACKAGE=lvl-up-backend-%date:~-4,4%%date:~-10,2%%date:~-7,2%-%time:~0,2%%time:~3,2%%time:~6,2%.tar.gz
set DEPLOY_PACKAGE=%DEPLOY_PACKAGE: =0%

REM Create tar.gz of backend directory (requires tar command)
tar -czf "%DEPLOY_PACKAGE%" -C "%LOCAL_BACKEND_DIR%" .

if exist "%DEPLOY_PACKAGE%" (
    echo [SUCCESS] Deployment package created: %DEPLOY_PACKAGE%
) else (
    echo [ERROR] Failed to create deployment package
    echo [INFO] Make sure you have tar command available (Git Bash, WSL, or similar)
    pause
    exit /b 1
)

REM Step 5: Instructions for manual deployment
echo.
echo [INFO] Step 5: Manual Deployment Instructions
echo =============================================
echo.
echo [INFO] To deploy to EC2, follow these steps:
echo.
echo 1. Upload the deployment package to EC2:
echo    scp %DEPLOY_PACKAGE% %EC2_USER%@%EC2_IP%:~/
echo.
echo 2. SSH into your EC2 instance:
echo    ssh %EC2_USER%@%EC2_IP%
echo.
echo 3. Extract and setup the backend:
echo    cd ~
echo    tar -xzf %DEPLOY_PACKAGE%
echo    cd ai-backend
echo    npm install
echo    npm start
echo.
echo 4. For persistent deployment, use PM2:
echo    npm install -g pm2
echo    pm2 start src/index.js --name "lvl-up-backend"
echo    pm2 startup
echo    pm2 save
echo.

REM Step 6: Test app connectivity
echo [INFO] Step 6: Testing app connectivity...
echo.
echo [INFO] Your Flutter app is now configured to connect to:
echo    Backend: http://%EC2_IP%:%BACKEND_PORT%
echo.
echo [INFO] To test the connection:
echo    curl http://%EC2_IP%:%BACKEND_PORT%/health
echo.

REM Step 7: Security group check
echo [INFO] Step 7: Security Group Configuration
echo.
echo [WARNING] Make sure your EC2 security group allows:
echo    - Inbound TCP port %BACKEND_PORT% from anywhere (0.0.0.0/0)
echo    - Or restrict to your IP for better security
echo.

REM Step 8: Environment variables
echo [INFO] Step 8: Environment Variables
echo.
echo [WARNING] Make sure your .env file on EC2 contains:
echo    - GITHUB_TOKEN
echo    - MONGODB_URI
echo    - Other required environment variables
echo.

echo [SUCCESS] Deployment script completed!
echo.
echo [INFO] Next steps:
echo 1. Deploy the backend to EC2 using the instructions above
echo 2. Test the connection from your Android app
echo 3. Approve proposals in the app to trigger AI improvements
echo 4. Use the learning endpoints to nudge the AIs:
echo    - POST http://%EC2_IP%:%BACKEND_PORT%/api/learning/trigger-self-improvement/imperium
echo    - POST http://%EC2_IP%:%BACKEND_PORT%/api/learning/trigger-cross-ai-learning
echo.

REM Cleanup
del "%DEPLOY_PACKAGE%" >nul 2>&1
echo [INFO] Deployment package cleaned up

pause 