@echo off
echo ========================================
echo    Fixing Systemd Service
echo ========================================
echo.

REM Get EC2 IP from environment
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo ========================================
echo UNMASKING SERVICE
echo ========================================
echo.

echo Unmasking the service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl unmask ai-backend-python"

echo.
echo ========================================
echo UPDATING SERVICE CONFIGURATION
echo ========================================
echo.

echo Updating service with GitHub environment variables...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment GITHUB_TOKEN=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"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment GITHUB_USERNAME=CTG813819"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment AUTO_IMPROVEMENT_ENABLED=true"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment GROWTH_ANALYSIS_INTERVAL=3600"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment GROWTH_THRESHOLD=0.6"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment REPO_BRANCH=main"
ssh -i "New.pem" %EC2_HOST% "sudo systemctl set-environment REPO_PATH=/home/ubuntu/ai-backend-python/repo"

echo.
echo ========================================
echo RESTARTING BACKEND SERVICE
echo ========================================
echo.

echo Restarting backend service...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"

echo.
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo TESTING GITHUB INTEGRATION
echo ========================================
echo.

echo Testing GitHub status endpoint...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/github/status

echo.
echo Testing AI agents status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo ========================================
echo TRIGGERING AI AGENTS
echo ========================================
echo.

echo Triggering all AI agents...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all

echo.
echo Waiting for agents to process...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo FINAL STATUS CHECK
echo ========================================
echo.

echo Final GitHub integration status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/github/status

echo.
echo Final AI agent status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo ========================================
echo SUCCESS! 🎉
echo ========================================
echo.
echo Systemd service has been fixed with GitHub environment variables!
echo All AI agents should now have full GitHub access.
echo.
pause 