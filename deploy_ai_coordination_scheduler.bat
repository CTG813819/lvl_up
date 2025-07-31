@echo off
REM Deploy AI Coordination Scheduler to EC2
REM Sets up robust AI scheduling with timeout handling and Custodes testing after each AI completion

echo 🚀 Deploying AI Coordination Scheduler to EC2...

REM Configuration
set PEM_FILE=C:\projects\lvl_up\New.pem
set EC2_HOST=ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
set REMOTE_DIR=/home/ubuntu/ai-backend-python

echo 📁 Deploying from: %PEM_FILE%
echo 🌐 Deploying to: %EC2_HOST%:%REMOTE_DIR%

REM Stop any existing scheduler services
echo 🛑 Stopping existing scheduler services...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl stop guardian-custodes-scheduler || echo 'Service not found'"
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl disable guardian-custodes-scheduler || echo 'Service not found'"

REM Deploy the schedule configuration
echo 📤 Deploying AI coordination schedule configuration...
scp -i "%PEM_FILE%" "ai-backend-python\ai_coordination_schedule.json" "%EC2_HOST%:%REMOTE_DIR%/"

REM Deploy the enhanced coordination scheduler
echo 📤 Deploying AI coordination scheduler...
scp -i "%PEM_FILE%" "ai-backend-python\ai_coordination_scheduler.py" "%EC2_HOST%:%REMOTE_DIR%/"

REM Deploy the systemd service file
echo 📤 Deploying systemd service file...
scp -i "%PEM_FILE%" "ai-backend-python\ai-coordination-scheduler.service" "%EC2_HOST%:%REMOTE_DIR%/"

REM Set up the service on the server
echo 🔧 Setting up AI coordination scheduler service...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && sudo cp ai-coordination-scheduler.service /etc/systemd/system/ && sudo systemctl daemon-reload"

REM Enable and start the service
echo 🚀 Enabling and starting AI coordination scheduler...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl enable ai-coordination-scheduler && sudo systemctl start ai-coordination-scheduler"

REM Check service status
echo 📊 Checking service status...
ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo systemctl status ai-coordination-scheduler --no-pager"

REM Show AI schedules
echo ⏰ AI Schedules:
echo    Guardian: Every 3 hours (30 min timeout)
echo    Imperium: Every 2 hours (45 min timeout)
echo    Sandbox: Every 4 hours (20 min timeout)
echo    Conquest: Every 6 hours (60 min timeout)
echo    Custodes: 1 minute after each AI completion (15 min timeout)

echo ✅ AI Coordination Scheduler deployment completed!
echo 📋 Monitor the scheduler with:
echo    ssh -i "%PEM_FILE%" "%EC2_HOST%" "sudo journalctl -u ai-coordination-scheduler -f"
echo 📋 Check AI status with:
echo    ssh -i "%PEM_FILE%" "%EC2_HOST%" "cat %REMOTE_DIR%/ai_scheduler_status.json"

pause 