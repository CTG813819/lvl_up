@echo off
REM Proposal Cleanup System - EC2 Deployment Script (Batch)
REM =======================================================
REM This script automates the deployment of the cleanup system to your EC2 instance

setlocal enabledelayedexpansion

REM Configuration
set PEM_PATH=C:\projects\lvl_up\New.pem
set EC2_HOST=ec2-34-202-215-209.compute-1.amazonaws.com
set EC2_USER=ubuntu
set REMOTE_PATH=/home/ubuntu/ai-backend-python

echo ==========================================
echo   PROPOSAL CLEANUP SYSTEM DEPLOYMENT
echo ==========================================
echo.

REM Check if PEM file exists
if not exist "%PEM_PATH%" (
    echo [ERROR] PEM file not found at: %PEM_PATH%
    echo Please update the PEM_PATH variable or ensure the file exists
    pause
    exit /b 1
)
echo [SUCCESS] PEM file found: %PEM_PATH%

REM Check if required files exist
set REQUIRED_FILES=cleanup_all_pending_proposals.py deploy_cleanup.sh DEPLOYMENT_GUIDE.md
for %%f in (%REQUIRED_FILES%) do (
    if not exist "%%f" (
        echo [ERROR] Required file not found: %%f
        echo Please ensure all required files are in the current directory
        pause
        exit /b 1
    )
)
echo [SUCCESS] All required files found

REM Test EC2 connection
echo [INFO] Testing connection to EC2...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "echo 'Connection successful'"
if errorlevel 1 (
    echo [ERROR] Cannot connect to EC2. Please check your credentials and network connection.
    pause
    exit /b 1
)
echo [SUCCESS] EC2 connection test successful

REM Deploy files
echo [INFO] Starting deployment to EC2...
for %%f in (%REQUIRED_FILES%) do (
    echo [INFO] Deploying %%f...
    scp -i "%PEM_PATH%" %%f %EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/
    if errorlevel 1 (
        echo [ERROR] Failed to deploy %%f
        pause
        exit /b 1
    )
    echo [SUCCESS] Successfully deployed %%f
)

REM Setup permissions on EC2
echo [INFO] Setting up permissions on EC2...
ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST% "cd %REMOTE_PATH% && chmod +x deploy_cleanup.sh"
if errorlevel 1 (
    echo [WARNING] Permission setup failed, but files were deployed.
    echo [WARNING] You may need to manually set permissions on EC2.
) else (
    echo [SUCCESS] Successfully set permissions on EC2
)

echo.
echo ==========================================
echo   DEPLOYMENT COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo [INFO] Next steps:
echo 1. SSH into your EC2 instance:
echo    ssh -i "%PEM_PATH%" %EC2_USER%@%EC2_HOST%
echo.
echo 2. Navigate to the backend directory:
echo    cd %REMOTE_PATH%
echo.
echo 3. Run the cleanup system:
echo    ./deploy_cleanup.sh --verify-only     # Check current state
echo    ./deploy_cleanup.sh --conservative    # Safe cleanup
echo    ./deploy_cleanup.sh --aggressive      # Remove everything
echo.
echo 4. For help and options:
echo    ./deploy_cleanup.sh --help
echo.
echo [INFO] See DEPLOYMENT_GUIDE.md for detailed instructions
echo.
pause 