@echo off
REM Deploy Proposal Improvements to EC2 (Fixed for Virtual Environment)
REM This script deploys the enhanced proposal system to the EC2 instance

echo 🚀 Deploying Proposal Improvements to EC2
echo ==========================================

REM Configuration
set EC2_HOST=ec2-34-202-215-209.compute-1.amazonaws.com
set EC2_USER=ubuntu
set SSH_KEY=C:\projects\lvl_up\New.pem
set REMOTE_PATH=/home/ubuntu/ai-backend-python
set LOCAL_PATH=ai-backend-python

REM Step 1: Check SSH key
echo [INFO] Step 1: Checking SSH key...
if exist "%SSH_KEY%" (
    echo [SUCCESS] SSH key found: %SSH_KEY%
) else (
    echo [ERROR] SSH key not found: %SSH_KEY%
    exit /b 1
)

REM Step 2: Test EC2 connectivity
echo [INFO] Step 2: Testing EC2 connectivity...
ssh -i "%SSH_KEY%" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "%EC2_USER%@%EC2_HOST%" "echo 'Connection successful'" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] EC2 connection successful
) else (
    echo [ERROR] Cannot connect to EC2 instance
    echo [WARNING] Please check your EC2 instance is running and accessible
    exit /b 1
)

REM Step 3: Create deployment package
echo [INFO] Step 3: Creating deployment package...
set DEPLOY_PACKAGE=proposal_improvements_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.tar.gz
set DEPLOY_PACKAGE=%DEPLOY_PACKAGE: =0%

REM Create tar.gz of the specific files we need to deploy
tar -czf "%DEPLOY_PACKAGE%" -C "%LOCAL_PATH%" app/services/proposal_validation_service.py app/routers/proposals.py test_proposal_validation.py PROPOSAL_IMPROVEMENTS_SUMMARY.md

if exist "%DEPLOY_PACKAGE%" (
    echo [SUCCESS] Deployment package created: %DEPLOY_PACKAGE%
) else (
    echo [ERROR] Failed to create deployment package
    exit /b 1
)

REM Step 4: Upload to EC2
echo [INFO] Step 4: Uploading to EC2...
scp -i "%SSH_KEY%" -o StrictHostKeyChecking=no "%DEPLOY_PACKAGE%" "%EC2_USER%@%EC2_HOST%:~/"

if %errorlevel% equ 0 (
    echo [SUCCESS] Deployment package uploaded to EC2
) else (
    echo [ERROR] Failed to upload deployment package
    exit /b 1
)

REM Step 5: Deploy on EC2 (Fixed for virtual environment)
echo [INFO] Step 5: Deploying on EC2...
ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no "%EC2_USER%@%EC2_HOST%" "echo '🔧 Deploying proposal improvements on EC2...' && cd /home/ubuntu/ai-backend-python && tar -xzf ~/proposal_improvements_*.tar.gz && echo '🐍 Activating virtual environment...' && source venv/bin/activate && echo '📦 Installing dependencies in virtual environment...' && pip install scikit-learn pandas numpy joblib requests && echo '🧪 Testing proposal validation service...' && python test_proposal_validation.py && echo '🔄 Restarting backend service...' && sudo systemctl restart ai-backend-python && sleep 10 && echo '📊 Checking service status...' && sudo systemctl status ai-backend-python --no-pager && echo '🔍 Testing new endpoints...' && curl -s http://localhost:8000/api/proposals/validation/stats && echo '✅ Deployment completed on EC2'"

if %errorlevel% equ 0 (
    echo [SUCCESS] Deployment completed successfully on EC2
) else (
    echo [ERROR] Deployment failed on EC2
    exit /b 1
)

REM Step 6: Test the deployment
echo [INFO] Step 6: Testing the deployment...
ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no "%EC2_USER%@%EC2_HOST%" "echo '🧪 Testing deployment...' && curl -s http://localhost:8000/api/health && curl -s http://localhost:8000/api/proposals/validation/stats && curl -s http://localhost:8000/api/proposals/ && echo '✅ All tests completed'"

REM Step 7: Generate deployment report
echo [INFO] Step 7: Generating deployment report...
(
echo Proposal Improvements Deployment Report
echo =====================================
echo.
echo Deployment Date: %date% %time%
echo EC2 Instance: %EC2_HOST%
echo Deployment Package: %DEPLOY_PACKAGE%
echo.
echo Deployed Components:
echo - Enhanced Proposal Validation Service
echo - Improved Proposal Descriptions
echo - AI Learning Integration
echo - Duplicate Detection System
echo - Confidence Threshold Validation
echo - Improvement Potential Assessment
echo.
echo New Features:
echo 1. Enhanced frontend descriptions with AI-specific explanations
echo 2. Backend validation to prevent redundant proposals
echo 3. AI learning requirements before new proposals
echo 4. Confidence threshold validation (60%% minimum)
echo 5. Improvement potential assessment
echo 6. Duplicate detection with 85%% similarity threshold
echo 7. Proposal limits (2 pending per AI, 10 daily per AI)
echo 8. Learning interval requirements (2 hours minimum)
echo.
echo API Endpoints:
echo - GET /api/proposals/validation/stats - Get validation statistics
echo - POST /api/proposals/ - Enhanced with validation
echo - All existing proposal endpoints remain functional
echo.
echo Validation Process:
echo 1. Duplicate Check - Compares with existing proposals
echo 2. Learning Status - Verifies AI has learned from feedback
echo 3. Proposal Limits - Ensures limits are not exceeded
echo 4. Confidence Check - Validates minimum confidence threshold
echo 5. Improvement Assessment - Evaluates potential impact
echo.
echo Configuration:
echo - Similarity Threshold: 85%%
echo - Minimum Learning Interval: 2 hours
echo - Max Pending per AI: 2
echo - Daily Limit per AI: 10
echo - Minimum Confidence: 60%%
echo.
echo Deployment Status: ✅ SUCCESS
) > proposal_improvements_deployment_report.txt

echo [SUCCESS] Deployment report saved to proposal_improvements_deployment_report.txt

REM Cleanup
del "%DEPLOY_PACKAGE%" 2>nul
echo [INFO] Deployment package cleaned up

echo.
echo [SUCCESS] Proposal improvements deployment completed!
echo.
echo [INFO] Next steps:
echo 1. Test the enhanced proposal descriptions in your Flutter app
echo 2. Monitor proposal validation through the new stats endpoint
echo 3. Check that AIs are learning and waiting appropriately
echo 4. Verify that redundant proposals are being filtered out
echo.
echo [INFO] Test endpoints:
echo   - http://%EC2_HOST%:8000/api/proposals/validation/stats
echo   - http://%EC2_HOST%:8000/api/proposals/
echo   - http://%EC2_HOST%:8000/api/health
echo.
pause 