@echo off
echo ========================================
echo    Updating Systemd Service
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
echo UPDATING SYSTEMD SERVICE
echo ========================================
echo.

echo Creating updated systemd service configuration...
ssh -i "New.pem" %EC2_HOST% "sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=GITHUB_TOKEN=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
Environment=GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
Environment=GITHUB_USERNAME=CTG813819
Environment=AUTO_IMPROVEMENT_ENABLED=true
Environment=GROWTH_ANALYSIS_INTERVAL=3600
Environment=GROWTH_THRESHOLD=0.6
Environment=REPO_BRANCH=main
Environment=REPO_PATH=/home/ubuntu/ai-backend-python/repo
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo.
echo ========================================
echo RELOADING SYSTEMD
echo ========================================
echo.

echo Reloading systemd daemon...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl daemon-reload"

echo.
echo ========================================
echo RESTARTING BACKEND SERVICE
echo ========================================
echo.

echo Restarting backend service with GitHub environment variables...
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

echo Triggering all AI agents with GitHub integration...
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
echo Systemd service has been updated with GitHub environment variables!
echo All AI agents should now have full GitHub access.
echo.
pause 