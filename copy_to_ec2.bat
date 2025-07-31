@echo off
echo Copying deployment script to EC2 instance...
echo.

REM Set the PEM file path and EC2 IP
set PEM_FILE=C:\projects\lvl_up\New.pem
set EC2_IP=34-202-215-209
set REMOTE_USER=ubuntu
set REMOTE_PATH=/home/ubuntu/

echo PEM File: %PEM_FILE%
echo EC2 IP: %EC2_IP%
echo Remote User: %REMOTE_USER%
echo Remote Path: %REMOTE_PATH%
echo.

REM Test SSH connection first
echo Testing SSH connection...
ssh -i "%PEM_FILE%" %REMOTE_USER%@%EC2_IP% "echo 'SSH connection successful'"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SSH connection failed
    echo Please check:
    echo 1. The PEM file exists and has correct permissions
    echo 2. The EC2 IP address is correct
    echo 3. The EC2 instance is running
    echo 4. Your security group allows SSH access
    pause
    exit /b 1
)

echo SSH connection successful!
echo.

REM Copy the deployment script
echo Copying deploy_to_ec2.sh to EC2...
scp -i "%PEM_FILE%" deploy_to_ec2.sh %REMOTE_USER%@%EC2_IP%:%REMOTE_PATH%
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: SCP copy failed
    pause
    exit /b 1
)

echo.
echo SUCCESS: Deployment script copied to EC2!
echo.
echo Next steps:
echo 1. SSH to your EC2 instance: ssh -i "%PEM_FILE%" %REMOTE_USER%@%EC2_IP%
echo 2. Navigate to backend: cd /home/ubuntu/ai-backend-python
echo 3. Run deployment: bash /home/ubuntu/deploy_to_ec2.sh
echo.
pause 