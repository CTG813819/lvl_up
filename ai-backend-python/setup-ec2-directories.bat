@echo off
echo Setting up EC2 directory structure...
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

echo Creating directory structure on EC2...
ssh -i "New.pem" %EC2_HOST% << 'EOF'
# Create main project directory
mkdir -p /home/ubuntu/lvl_up

# Create backend directory structure
mkdir -p /home/ubuntu/lvl_up/ai-backend-python
mkdir -p /home/ubuntu/lvl_up/ai-backend-python/app
mkdir -p /home/ubuntu/lvl_up/ai-backend-python/app/core
mkdir -p /home/ubuntu/lvl_up/ai-backend-python/app/models
mkdir -p /home/ubuntu/lvl_up/ai-backend-python/app/routers
mkdir -p /home/ubuntu/lvl_up/ai-backend-python/app/services

# Create GitHub workflows directory
mkdir -p /home/ubuntu/lvl_up/.github/workflows

# Set proper permissions
chmod -R 755 /home/ubuntu/lvl_up

echo Directory structure created successfully!
echo.
echo Created directories:
ls -la /home/ubuntu/lvl_up/
echo.
echo Backend structure:
ls -la /home/ubuntu/lvl_up/ai-backend-python/app/
EOF

if %ERRORLEVEL% neq 0 (
    echo Failed to create directory structure
    pause
    exit /b 1
)

echo.
echo Directory structure created successfully!
echo Now you can run the deployment script.
echo.
pause 