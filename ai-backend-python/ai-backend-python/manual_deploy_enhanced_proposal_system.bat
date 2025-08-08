@echo off
REM Manual Deployment Script for Enhanced Proposal System
REM Deploy files to EC2 instance step by step

echo 🚀 Manual Deployment of Enhanced Proposal System
echo.

REM Set variables
set EC2_HOST=34.202.215.209
set PEM_FILE=C:\projects\lvl_up\New.pem
set REMOTE_DIR=~/ai-backend-python

echo 📋 Files to be deployed:
echo    - Enhanced proposal models (proposal.py, sql_models.py)
echo    - Enhanced proposal description service
echo    - Updated proposals router with response functionality
echo    - Database migration script
echo    - Enhanced frontend models and screens
echo    - Documentation
echo.

echo 🔗 EC2 Instance: %EC2_HOST%
echo 📁 Remote Directory: %REMOTE_DIR%
echo.

REM Step 1: Copy backend files
echo 📁 Step 1: Copying backend files...
scp -i "%PEM_FILE%" ai-backend-python\app\models\proposal.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/app/models/
scp -i "%PEM_FILE%" ai-backend-python\app\models\sql_models.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/app/models/
scp -i "%PEM_FILE%" ai-backend-python\app\services\enhanced_proposal_description_service.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/app/services/
scp -i "%PEM_FILE%" ai-backend-python\app\routers\proposals.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/app/routers/
scp -i "%PEM_FILE%" ai-backend-python\add_enhanced_proposal_fields_migration.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/

echo ✅ Backend files copied successfully!
echo.

REM Step 2: Copy frontend files
echo 📱 Step 2: Copying frontend files...
scp -i "%PEM_FILE%" lib\models\ai_proposal.dart ubuntu@%EC2_HOST%:%REMOTE_DIR%/lib/models/
scp -i "%PEM_FILE%" lib\screens\proposal_approval_screen.dart ubuntu@%EC2_HOST%:%REMOTE_DIR%/lib/screens/

echo ✅ Frontend files copied successfully!
echo.

REM Step 3: Copy documentation
echo 📚 Step 3: Copying documentation...
scp -i "%PEM_FILE%" ENHANCED_PROPOSAL_SYSTEM_SUMMARY.md ubuntu@%EC2_HOST%:%REMOTE_DIR%/

echo ✅ Documentation copied successfully!
echo.

REM Step 4: Install dependencies and run migration
echo 🔧 Step 4: Installing dependencies and running migration...
ssh -i "%PEM_FILE%" ubuntu@%EC2_HOST% "cd %REMOTE_DIR% && pip install schedule && python add_enhanced_proposal_fields_migration.py"

echo ✅ Dependencies installed and migration completed!
echo.

REM Step 5: Restart application
echo 🔄 Step 5: Restarting application...
ssh -i "%PEM_FILE%" ubuntu@%EC2_HOST% "sudo systemctl restart ai-backend-python"

echo ✅ Application restarted!
echo.

echo 🎉 Manual deployment completed successfully!
echo.
echo 📋 Summary:
echo    - All enhanced proposal system files deployed
echo    - Database migration completed
echo    - Application restarted
echo    - Missing dependencies installed
echo.
echo 🔗 EC2 Instance: %EC2_HOST%
echo 📁 Remote Directory: %REMOTE_DIR%
echo.
pause 