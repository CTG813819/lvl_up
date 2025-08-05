@echo off
echo Starting deployment to EC2 instance...

REM Set variables
set EC2_HOST=ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
set KEY_FILE=C:\projects\lvl_up\New.pem
set REMOTE_DIR=/home/ubuntu/ai-backend-python

echo Transferring fixed files to EC2...

REM Transfer main.py
echo Transferring app/main.py...
scp -i "%KEY_FILE%" "app/main.py" "%EC2_HOST%:%REMOTE_DIR%/app/main.py"
if %ERRORLEVEL% neq 0 (
    echo Failed to transfer app/main.py
    exit /b 1
)
echo Successfully transferred app/main.py

REM Transfer custody_protocol_service.py
echo Transferring app/services/custody_protocol_service.py...
scp -i "%KEY_FILE%" "app/services/custody_protocol_service.py" "%EC2_HOST%:%REMOTE_DIR%/app/services/custody_protocol_service.py"
if %ERRORLEVEL% neq 0 (
    echo Failed to transfer app/services/custody_protocol_service.py
    exit /b 1
)
echo Successfully transferred app/services/custody_protocol_service.py

REM Transfer create_tables.py
echo Transferring create_tables.py...
scp -i "%KEY_FILE%" "create_tables.py" "%EC2_HOST%:%REMOTE_DIR%/create_tables.py"
if %ERRORLEVEL% neq 0 (
    echo Failed to transfer create_tables.py
    exit /b 1
)
echo Successfully transferred create_tables.py

echo Running database setup on EC2...
ssh -i "%KEY_FILE%" "%EC2_HOST%" "cd %REMOTE_DIR% && python3 create_tables.py"

echo Restarting the backend service on EC2...
ssh -i "%KEY_FILE%" "%EC2_HOST%" "sudo systemctl restart ultimate_start"

echo Waiting for service to start...
timeout /t 10 /nobreak > nul

echo Checking service status...
ssh -i "%KEY_FILE%" "%EC2_HOST%" "sudo systemctl status ultimate_start"

echo Deployment completed!
echo.
echo To check the logs, run:
echo ssh -i "%KEY_FILE%" "%EC2_HOST%" "sudo journalctl -u ultimate_start -f" 