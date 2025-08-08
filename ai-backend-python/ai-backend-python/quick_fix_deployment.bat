@echo off
REM Quick Fix Deployment - Fix SQLAlchemy metadata error
REM Deploy corrected sql_models.py to EC2 instance

echo 🔧 Quick Fix: Deploying corrected SQL models...
echo.

REM Set variables
set EC2_HOST=34.202.215.209
set PEM_FILE=C:\projects\lvl_up\New.pem
set REMOTE_DIR=~/ai-backend-python

echo 📁 Deploying corrected sql_models.py...
scp -i "%PEM_FILE%" ai-backend-python\app\models\sql_models.py ubuntu@%EC2_HOST%:%REMOTE_DIR%/app/models/

echo ✅ SQL models file deployed!
echo.

echo 🔄 Restarting application...
ssh -i "%PEM_FILE%" ubuntu@%EC2_HOST% "sudo systemctl restart ai-backend-python"

echo ✅ Application restarted!
echo.

echo 🎉 Quick fix deployment completed!
echo 📋 Fixed: SQLAlchemy metadata reserved word error
echo.
pause 