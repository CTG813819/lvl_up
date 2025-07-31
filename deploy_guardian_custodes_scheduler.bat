@echo off
REM Deploy Guardian-Custodes Scheduler to EC2
REM Sets up Guardian to run every 3 hours and Custodes to test Guardian after completion

echo 🚀 Deploying Guardian-Custodes Scheduler to EC2...

REM Configuration
set PEM_FILE=C:\projects\lvl_up\New.pem
set EC2_HOST=ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
set REMOTE_DIR=/home/ubuntu/ai-backend-python

echo 📁 Deploying from: %PEM_FILE%
echo 🌐 Deploying to: %EC2_HOST%:%REMOTE_DIR%

REM Deploy the schedule configuration
echo 📤 Deploying schedule configuration...
scp -i "%PEM_FILE%" "ai-backend-python\guardian_custodes_schedule.json" "%EC2_HOST%:%REMOTE_DIR%/"

REM Deploy the enhanced scheduler
echo 📤 Deploying enhanced scheduler...
scp -i "%PEM_FILE%" "ai-backend-python\guardian_scheduler_enhanced.py" "%EC2_HOST%:%REMOTE_DIR%/"

REM Deploy the systemd service file
echo 📤 Deploying systemd service file...
scp -i "%PEM_FILE%" "ai-backend-python\guardian-custodes-scheduler.service" "%EC2_HOST%:%REMOTE_DIR%/"

REM Set up the service on the server
echo 🔧 Setting up Guardian-Custodes scheduler service...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && sudo cp guardian-custodes-scheduler.service /etc/systemd/system/ && sudo systemctl daemon-reload"

REM Enable and start the service
echo 🚀 Enabling and starting Guardian-Custodes scheduler...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl enable guardian-custodes-scheduler && sudo systemctl start guardian-custodes-scheduler"

REM Check service status
echo 📊 Checking service status...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl status guardian-custodes-scheduler --no-pager"

REM Show next scheduled runs
echo ⏰ Next scheduled runs:
echo    Guardian: Every 3 hours
echo    Custodes: 2 minutes after Guardian completion

echo ✅ Guardian-Custodes Scheduler deployment completed!
echo 📋 Monitor the scheduler with:
echo    ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo journalctl -u guardian-custodes-scheduler -f"

pause 