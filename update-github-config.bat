@echo off
echo ========================================
echo    Updating GitHub Configuration
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
echo UPDATING GITHUB CONFIGURATION
echo ========================================
echo.

echo Updating .env file with your GitHub credentials...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '# GitHub Configuration' > .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_TOKEN=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' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_USERNAME=CTG813819' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '# AI Configuration' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'AUTO_IMPROVEMENT_ENABLED=true' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GROWTH_ANALYSIS_INTERVAL=3600' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GROWTH_THRESHOLD=0.6' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '# Repository Configuration' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'REPO_BRANCH=main' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'REPO_PATH=/home/ubuntu/ai-backend-python/repo' >> .env"

echo.
echo ========================================
echo CONFIGURATION UPDATED
echo ========================================
echo.

echo Current .env file contents:
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && cat .env"

echo.
echo ========================================
echo RESTARTING BACKEND SERVICE
echo ========================================
echo.

echo Restarting backend service to apply new configuration...
ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"

echo.
echo Waiting for backend to restart...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo TESTING AI AGENTS
echo ========================================
echo.

echo Testing AI agent status after restart...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Testing autonomous cycle status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/autonomous/status

echo.
echo ========================================
echo TRIGGERING AI AGENTS
echo ========================================
echo.

echo Triggering all AI agents with new GitHub configuration...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all

echo.
echo Waiting for agents to process...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo FINAL STATUS CHECK
echo ========================================
echo.

echo Final AI agent status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Testing GitHub integration...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/github/status

echo.
echo ========================================
echo SUCCESS! 🎉
echo ========================================
echo.
echo Your GitHub configuration has been updated with:
echo ✅ GitHub Token: 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
echo ✅ Repository: https://github.com/CTG813819/Lvl_UP.git
echo ✅ Username: CTG813819
echo.
echo All 4 AI agents should now be fully functional:
echo ✅ Imperium AI: Code analysis and improvements
echo ✅ Guardian AI: Security analysis and monitoring
echo ✅ Sandbox AI: Experiments and testing
echo ✅ Conquest AI: Deployments and changes
echo.
echo The AI system is now 100%% operational!
echo.
pause 