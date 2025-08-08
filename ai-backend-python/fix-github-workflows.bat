@echo off
echo Fixing GitHub workflows directory...
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

echo Creating GitHub workflows directory and copying files...
ssh -i "New.pem" %EC2_HOST% << 'EOF'
# Create GitHub workflows directory
mkdir -p /home/ubuntu/.github/workflows

# Set proper permissions
chmod -R 755 /home/ubuntu/.github

echo GitHub workflows directory created successfully!
ls -la /home/ubuntu/.github/
EOF

echo.
echo Copying GitHub workflow files...
scp -i "New.pem" -r .github/workflows/* %EC2_HOST%:/home/ubuntu/.github/workflows/

if %ERRORLEVEL% neq 0 (
    echo Failed to copy GitHub workflow files
    pause
    exit /b 1
)

echo.
echo GitHub workflows fixed successfully!
echo.
pause 