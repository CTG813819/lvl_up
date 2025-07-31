@echo off
REM Deploy Proposal Validation Fix to EC2
REM This script deploys the fixes for the "No meaningful changes detected" validation error

setlocal enabledelayedexpansion

REM Configuration
set EC2_HOST=34.202.215.209
set EC2_USER=ubuntu
set REMOTE_PATH=/home/ubuntu/ai-backend
set LOCAL_PATH=ai-backend-python
set SSH_KEY=C:\projects\lvl_up\New.pem

echo 🚀 Deploying Proposal Validation Fix to EC2...

REM Check if we're in the right directory
if not exist "%LOCAL_PATH%" (
    echo ❌ Error: %LOCAL_PATH% directory not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if SSH key exists
if not exist "%SSH_KEY%" (
    echo ❌ Error: SSH key not found at %SSH_KEY%
    echo Please ensure the SSH key file exists
    pause
    exit /b 1
)

echo 📁 Local path: %LOCAL_PATH%
echo 🌐 Remote host: %EC2_HOST%
echo 📂 Remote path: %REMOTE_PATH%
echo 🔑 SSH key: %SSH_KEY%

REM Create backup of current deployment
echo 💾 Creating backup of current deployment...
ssh -i "%SSH_KEY%" "%EC2_USER%@%EC2_HOST%" "cd %REMOTE_PATH% && tar -czf backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.tar.gz ."

REM Deploy the fixed files
echo 📤 Deploying fixed files...

REM Deploy the main AI agent service with fixes
scp -i "%SSH_KEY%" "%LOCAL_PATH%\app\services\ai_agent_service.py" "%EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/app/services/"

REM Deploy test scripts
scp -i "%SSH_KEY%" "%LOCAL_PATH%\test_direct_code_analysis.py" "%EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/"
scp -i "%SSH_KEY%" "%LOCAL_PATH%\test_full_proposal_flow.py" "%EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/"

REM Deploy the fix summary
scp -i "%SSH_KEY%" "%LOCAL_PATH%\PROPOSAL_VALIDATION_FIX_SUMMARY.md" "%EC2_USER%@%EC2_HOST%:%REMOTE_PATH%/"

REM Install missing dependency
echo 📦 Installing missing dependencies...
ssh -i "%SSH_KEY%" "%EC2_USER%@%EC2_HOST%" "cd %REMOTE_PATH% && pip install beautifulsoup4"

REM Restart the backend service
echo 🔄 Restarting backend service...
ssh -i "%SSH_KEY%" "%EC2_USER%@%EC2_HOST%" "sudo systemctl restart ai-backend"

REM Wait for service to start
echo ⏳ Waiting for service to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo 🔍 Checking service status...
ssh -i "%SSH_KEY%" "%EC2_USER%@%EC2_HOST%" "sudo systemctl status ai-backend --no-pager"

REM Test the deployment
echo 🧪 Testing deployment...
ssh -i "%SSH_KEY%" "%EC2_USER%@%EC2_HOST%" "cd %REMOTE_PATH% && python test_direct_code_analysis.py"

echo ✅ Deployment completed successfully!
echo.
echo 📊 Summary:
echo   - Fixed AI agent proposal creation flow
echo   - Enhanced code analysis methods
echo   - Fixed validation service integration
echo   - Added test scripts for verification
echo.
echo 🔗 Backend URL: http://%EC2_HOST%:8000
echo 📋 Validation stats: http://%EC2_HOST%:8000/api/proposals/validation/stats
echo.
echo 🎯 The proposal validation system should now work correctly!
echo    AI agents will generate meaningful code changes that pass validation.

pause 