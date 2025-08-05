@echo off
echo ========================================
echo    AI Activity Trigger & Test Script
echo ========================================
echo.

REM Get EC2 IP from environment or use default
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
echo 1. Checking Current AI Status
echo ========================================
echo Current AI agent status:
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo ========================================
echo 2. Triggering Manual AI Agent Run
echo ========================================
echo Triggering all AI agents manually...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run-all

echo.
echo Waiting 10 seconds for agents to process...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo 3. Checking AI Status After Manual Run
echo ========================================
echo AI agent status after manual run:
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo ========================================
echo 4. Triggering Individual AI Agents
echo ========================================
echo Triggering Imperium AI...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run/Imperium

echo.
echo Triggering Guardian AI...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run/Guardian

echo.
echo Triggering Sandbox AI...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run/Sandbox

echo.
echo Triggering Conquest AI...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run/Conquest

echo.
echo ========================================
echo 5. Starting Autonomous Mode
echo ========================================
echo Starting autonomous AI cycle...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/autonomous/start

echo.
echo Waiting 15 seconds for autonomous cycle...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo 6. Checking Autonomous Status
echo ========================================
echo Autonomous cycle status:
curl -s http://%EC2_IP%:4000/api/agents/autonomous/status

echo.
echo ========================================
echo 7. Checking Recent Activity
echo ========================================
echo Recent learning data:
curl -s http://%EC2_IP%:4000/api/learning/data

echo.
echo Recent proposals:
curl -s http://%EC2_IP%:4000/api/proposals/

echo.
echo ========================================
echo 8. Checking Backend Logs for Activity
echo ========================================
echo Recent backend logs showing AI activity:
ssh -i "New.pem" %EC2_HOST% "sudo journalctl -u ai-backend-python --no-pager -n 20 | grep -E '(agent|cycle|proposal|learning)'"

echo.
echo ========================================
echo 9. Testing AI Growth System
echo ========================================
echo Triggering AI growth analysis...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/growth/auto-improve

echo.
echo ========================================
echo 10. Final Status Check
echo ========================================
echo Final AI agent status:
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo ========================================
echo TROUBLESHOOTING GUIDE
echo ========================================
echo.
echo If AI agents still aren't working:
echo.
echo 1. Check backend logs for errors:
echo    ssh -i "New.pem" %EC2_HOST% "sudo journalctl -u ai-backend-python --no-pager -n 100"
echo.
echo 2. Check if background service is running:
echo    ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python"
echo.
echo 3. Restart the backend service:
echo    ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"
echo.
echo 4. Check database connection:
echo    ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python -c \"from app.core.database import get_session; print('Testing database connection...')\""
echo.
echo 5. Check environment variables:
echo    ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && env | grep -E '(DATABASE|GITHUB|AI)'"
echo.
echo 6. Check if GitHub tokens are configured:
echo    ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && find . -name '*.env*' -exec cat {} \\;"
echo.
pause 