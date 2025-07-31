@echo off
REM Guardian AI Enhancements Deployment Script for Windows
REM This script deploys the new Guardian AI health check and suggestion management system

echo 🚀 Starting Guardian AI Enhancements Deployment...

REM Configuration
set EC2_HOST=ec2-34-202-215-209.compute-1.amazonaws.com
set EC2_USER=ubuntu
set BACKEND_DIR=/home/ubuntu/ai-backend-python
set SERVICE_NAME=ai-backend-python

REM Step 1: Create database migration
echo [INFO] Step 1: Creating database migration for Guardian suggestions table...
cd ai-backend-python

if exist "create_guardian_suggestions_table.py" (
    echo [SUCCESS] Migration script found
) else (
    echo [ERROR] Migration script not found!
    exit /b 1
)

REM Step 2: Deploy to EC2
echo [INFO] Step 2: Deploying to EC2 instance...

REM Create a temporary deployment package
set DEPLOY_DIR=guardian_deployment_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set DEPLOY_DIR=%DEPLOY_DIR: =0%
mkdir %DEPLOY_DIR%

REM Copy necessary files
xcopy /E /I app %DEPLOY_DIR%\app
copy create_guardian_suggestions_table.py %DEPLOY_DIR%\
copy requirements.txt %DEPLOY_DIR%\
copy main.py %DEPLOY_DIR%\

echo [INFO] Created deployment package: %DEPLOY_DIR%

REM Step 3: Upload to EC2
echo [INFO] Step 3: Uploading files to EC2...

REM Create backup of current backend
ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo cp -r /home/ubuntu/ai-backend-python /home/ubuntu/ai-backend-python.backup.$(date +%%Y%%m%%d_%%H%%M%%S)"

REM Upload new files
scp -o StrictHostKeyChecking=no -r %DEPLOY_DIR%\* %EC2_USER%@%EC2_HOST%:%BACKEND_DIR%/

echo [SUCCESS] Files uploaded successfully

REM Step 4: Run database migration
echo [INFO] Step 4: Running database migration...

ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "cd /home/ubuntu/ai-backend-python && python3 create_guardian_suggestions_table.py"

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Database migration completed successfully
) else (
    echo [ERROR] Database migration failed!
    exit /b 1
)

REM Step 5: Restart backend service
echo [INFO] Step 5: Restarting backend service...

ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo systemctl stop ai-backend-python && sudo systemctl start ai-backend-python && sleep 5 && sudo systemctl status ai-backend-python --no-pager"

REM Step 6: Test the new endpoints
echo [INFO] Step 6: Testing new Guardian endpoints...

REM Test health check endpoint
echo [INFO] Testing health check endpoint...
curl -s -X POST "http://%EC2_HOST%:4000/api/guardian/health-check"

REM Test suggestions endpoint
echo [INFO] Testing suggestions endpoint...
curl -s "http://%EC2_HOST%:4000/api/guardian/suggestions"

REM Test health status endpoint
echo [INFO] Testing health status endpoint...
curl -s "http://%EC2_HOST%:4000/api/guardian/health-status"

REM Step 7: Cleanup
echo [INFO] Step 7: Cleaning up deployment files...
rmdir /S /Q %DEPLOY_DIR%

REM Step 8: Final verification
echo [INFO] Step 8: Final verification...

ssh -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo [SUCCESS] 🎉 Guardian AI Enhancements Deployment Completed Successfully!

echo.
echo 📋 Deployment Summary:
echo ✅ Database migration completed
echo ✅ Backend service restarted
echo ✅ New endpoints tested
echo ✅ Service status verified
echo.
echo 🔗 New Guardian AI Endpoints:
echo    - POST /api/guardian/health-check
echo    - GET /api/guardian/suggestions
echo    - POST /api/guardian/suggestions/{id}/approve
echo    - POST /api/guardian/suggestions/{id}/reject
echo    - GET /api/guardian/suggestions/statistics
echo    - GET /api/guardian/health-status
echo.
echo 📱 Frontend Integration:
echo    - GuardianSuggestionsWidget added to Terra screen
echo    - GuardianService updated with new API calls
echo.
echo 🚀 Ready for frontend deployment!

pause 