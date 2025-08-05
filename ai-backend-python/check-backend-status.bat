@echo off
echo ========================================
echo    AI Backend Status & Logs Checker
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
echo 1. Checking Backend Service Status
echo ========================================
ssh -i "New.pem" %EC2_HOST% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo ========================================
echo 2. Checking Recent Backend Logs
echo ========================================
ssh -i "New.pem" %EC2_HOST% "sudo journalctl -u ai-backend-python --no-pager -n 50"

echo.
echo ========================================
echo 3. Checking Backend Health
echo ========================================
echo Testing backend health endpoint...
curl -s http://%EC2_IP%:4000/health

echo.
echo ========================================
echo 4. Checking AI Agent Status
echo ========================================
echo Testing AI agents status...
curl -s http://%EC2_IP%:4000/api/agents/status

echo.
echo ========================================
echo 5. Checking Autonomous Cycle Status
echo ========================================
echo Testing autonomous cycle status...
curl -s http://%EC2_IP%:4000/api/agents/autonomous/status

echo.
echo ========================================
echo 6. Checking AI Growth System
echo ========================================
echo Testing AI growth system...
curl -s http://%EC2_IP%:4000/api/growth/status

echo.
echo ========================================
echo 7. Checking Learning Data
echo ========================================
echo Testing learning data...
curl -s http://%EC2_IP%:4000/api/learning/data

echo.
echo ========================================
echo 8. Checking Recent Proposals
echo ========================================
echo Testing recent proposals...
curl -s http://%EC2_IP%:4000/api/proposals/

echo.
echo ========================================
echo 9. Checking Database Connection
echo ========================================
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python -c \"from app.core.database import get_session; import asyncio; async def test(): session = get_session(); print('Database connection test completed'); await session.close(); asyncio.run(test())\""

echo.
echo ========================================
echo 10. Checking Background Service Logs
echo ========================================
ssh -i "New.pem" %EC2_HOST% "sudo journalctl -u ai-backend-python --no-pager -n 100 | grep -E '(background|autonomous|cycle|agent)'"

echo.
echo ========================================
echo 11. Checking System Resources
echo ========================================
ssh -i "New.pem" %EC2_HOST% "echo 'CPU Usage:'; top -bn1 | grep 'Cpu(s)' | awk '{print \$2}' | cut -d'%' -f1; echo 'Memory Usage:'; free -m | awk 'NR==2{printf \"%.2f%%\", \$3*100/\$2}'; echo 'Disk Usage:'; df -h / | awk 'NR==2{print \$5}'"

echo.
echo ========================================
echo 12. Checking Process List
echo ========================================
ssh -i "New.pem" %EC2_HOST% "ps aux | grep -E '(uvicorn|python|ai-backend)' | grep -v grep"

echo.
echo ========================================
echo 13. Checking Network Connections
echo ========================================
ssh -i "New.pem" %EC2_HOST% "netstat -tlnp | grep :4000"

echo.
echo ========================================
echo 14. Manual AI Agent Test
echo ========================================
echo Testing manual AI agent run...
curl -X POST -H "Content-Type: application/json" -d "{}" http://%EC2_IP%:4000/api/agents/run-all

echo.
echo ========================================
echo 15. Checking GitHub Integration
echo ========================================
echo Testing GitHub status...
curl -s http://%EC2_IP%:4000/api/github/status

echo.
echo ========================================
echo 16. Checking Conquest AI Status
echo ========================================
echo Testing Conquest AI status...
curl -s http://%EC2_IP%:4000/api/conquest/api/conquest/status

echo.
echo ========================================
echo DIAGNOSIS SUMMARY
echo ========================================
echo.
echo If the AI agents aren't doing anything, check:
echo 1. Backend service status (should be 'active (running)')
echo 2. Recent logs for errors or warnings
echo 3. Autonomous cycle status (should be 'true')
echo 4. Database connection (should not show errors)
echo 5. System resources (CPU/Memory usage)
echo 6. Network connectivity (port 4000 should be listening)
echo.
echo Common issues:
echo - Backend service not running
echo - Database connection failures
echo - Missing environment variables
echo - GitHub token issues
echo - System resource constraints
echo - Network connectivity problems
echo.
pause 