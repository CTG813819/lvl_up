@echo off
echo Checking EC2 directory structure...
echo.

REM Get EC2 IP from environment or use default
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

REM Convert IP to EC2 hostname format
set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo Checking existing directory structure...
ssh -i "New.pem" %EC2_HOST% << 'EOF'
echo Current directory structure:
echo.
echo /home/ubuntu/ contents:
ls -la /home/ubuntu/
echo.
echo /home/ubuntu/ai-backend-python/ contents:
ls -la /home/ubuntu/ai-backend-python/
echo.
echo /home/ubuntu/ai-backend-python/app/ contents:
ls -la /home/ubuntu/ai-backend-python/app/
echo.
echo /home/ubuntu/ai-backend-python/app/services/ contents:
ls -la /home/ubuntu/ai-backend-python/app/services/
echo.
echo /home/ubuntu/ai-backend-python/app/routers/ contents:
ls -la /home/ubuntu/ai-backend-python/app/routers/
echo.
echo /home/ubuntu/ai-backend-python/app/models/ contents:
ls -la /home/ubuntu/ai-backend-python/app/models/
EOF

echo.
echo Directory structure check completed!
pause 