@echo off
setlocal

:: =============================================================================
:: Quick and Dirty Deployment Script for AI Backend (PowerShell + Scorch)
:: =============================================================================
:: This script will:
:: 1. Package the local ai-backend-python directory using PowerShell.
:: 2. Upload it to the EC2 instance.
:: 3. Rename the old directory, create a new one, and unpack the code.
:: 4. Create/activate a Python venv, install requirements, and restart the remote service.
:: =============================================================================

:: --- Configuration ---
set "EC2_IP=34.202.215.209"
set "EC2_USER=ubuntu"
set "PEM_KEY=New.pem"
set "REMOTE_DIR=/home/ubuntu/ai-backend-python"
set "LOCAL_DIR=ai-backend-python"
set "ARCHIVE_NAME=ai-backend-deployment.zip"
set "PM2_PROCESS_NAME=ai-backend-python"

:: --- Script Start ---
echo [DEPLOY] Starting deployment to %EC2_IP%...

:: 1. Create a compressed archive of the local backend directory
echo [DEPLOY] 1/4 - Creating deployment archive...
powershell -Command "Compress-Archive -Path %LOCAL_DIR%\* -DestinationPath %ARCHIVE_NAME% -Force"
if %errorlevel% neq 0 (
  echo [DEPLOY] ERROR: Failed to create archive.
  goto :eof
)
echo [DEPLOY] Archive created successfully: %ARCHIVE_NAME%

:: 2. Upload the archive to the EC2 instance
echo [DEPLOY] 2/4 - Uploading archive to EC2...
scp -i "%PEM_KEY%" %ARCHIVE_NAME% %EC2_USER%@%EC2_IP%:/tmp/
if %errorlevel% neq 0 (
  echo [DEPLOY] ERROR: Failed to upload archive.
  goto :eof
)
echo [DEPLOY] Archive uploaded successfully.

:: 3. Execute remote commands for deployment
echo [DEPLOY] 3/4 - Deploying on EC2 (this may take a moment)...
ssh -i "%PEM_KEY%" %EC2_USER%@%EC2_IP% "mv %REMOTE_DIR% %REMOTE_DIR%-old-$(date +%%s) 2>/dev/null || true && mkdir -p %REMOTE_DIR% && unzip -o /tmp/%ARCHIVE_NAME% -d %REMOTE_DIR%/ && cd %REMOTE_DIR% && if [ ! -d venv ]; then python3 -m venv venv; fi && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate && sudo systemctl restart ai-backend-python.service"
if %errorlevel% neq 0 (
  echo [DEPLOY] ERROR: Remote deployment commands failed.
  echo [DEPLOY] Please check the EC2 instance manually.
  goto :eof
)

:: 4. Clean up local archive
echo [DEPLOY] 4/4 - Cleaning up...
del %ARCHIVE_NAME%
echo [DEPLOY] Local archive deleted.

echo [DEPLOY] =============================================================================
echo [DEPLOY] Deployment Complete!
echo [DEPLOY] =============================================================================

endlocal 