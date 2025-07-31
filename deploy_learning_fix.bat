@echo off
REM Deploy Learning Model Fix to EC2
REM This script deploys the fix for the 'context' keyword argument error in the Learning model

echo 🚀 Deploying Learning Model Fix to EC2...

REM Configuration
set PEM_FILE=C:\projects\lvl_up\New.pem
set EC2_HOST=ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
set REMOTE_DIR=/home/ubuntu/ai-backend-python

echo 📁 Deploying from: %PEM_FILE%
echo 🌐 Deploying to: %EC2_HOST%:%REMOTE_DIR%

REM Create a backup of the current ai_learning_service.py on the server
echo 💾 Creating backup of current ai_learning_service.py...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "cp %REMOTE_DIR%/app/services/ai_learning_service.py %REMOTE_DIR%/app/services/ai_learning_service.py.backup.$(date +%%Y%%m%%d_%%H%%M%%S)"

REM Deploy the fixed ai_learning_service.py
echo 📤 Deploying fixed ai_learning_service.py...
scp -i "%PEM_FILE%" "ai-backend-python\app\services\ai_learning_service.py" "%EC2_HOST%:%REMOTE_DIR%/app/services/"

REM Deploy the test script
echo 📤 Deploying test script...
scp -i "%PEM_FILE%" "ai-backend-python\test_learning_fix.py" "%EC2_HOST%:%REMOTE_DIR%/"

REM Test the fix on the server
echo 🧪 Testing the fix on the server...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && python test_learning_fix.py"

REM Restart the application if it's running
echo 🔄 Restarting the application...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && sudo systemctl restart lvl_up_backend || echo 'Service not found, manual restart may be needed'"

echo ✅ Deployment completed!
echo 📋 Check the logs to verify the fix is working:
echo    ssh -i "%PEM_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && tail -f logs/app.log"

pause 