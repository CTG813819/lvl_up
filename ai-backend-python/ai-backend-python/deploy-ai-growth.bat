@echo off
echo 🚀 Deploying AI Growth System to EC2...
echo.

REM Get EC2 IP from environment or use default
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo ❌ EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

echo 📡 Connecting to EC2 instance: %EC2_IP%
echo.

REM Copy updated files to EC2
echo 📁 Copying Complete AI System files...
echo   - AI Growth Service (NEW)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/services/ai_growth_service.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/services/
echo   - Growth Router (NEW)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/routers/growth.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/routers/
echo   - Updated Main App (with ALL features)
scp -i "lvl_up_key.pem" -r ai-backend-python/main.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/
echo   - Updated Requirements
scp -i "lvl_up_key.pem" -r ai-backend-python/requirements.txt ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/
echo   - AI Growth Documentation
scp -i "lvl_up_key.pem" -r AI_GROWTH_SYSTEM_GUIDE.md ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/
echo   - GitHub Integration (existing)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/services/github_service.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/services/
scp -i "lvl_up_key.pem" -r ai-backend-python/app/routers/github_webhook.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/routers/
echo   - AI Agent Service (existing)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/services/ai_agent_service.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/services/
scp -i "lvl_up_key.pem" -r ai-backend-python/app/routers/agents.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/routers/
echo   - Conquest AI (existing)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/routers/conquest.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/routers/
echo   - Background Service (existing)
scp -i "lvl_up_key.pem" -r ai-backend-python/app/services/background_service.py ubuntu@%EC2_IP%:/home/ubuntu/lvl_up/ai-backend-python/app/services/

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to copy files to EC2
    pause
    exit /b 1
)

echo ✅ Files copied successfully
echo.

REM Install new dependencies and restart backend
echo 🔧 Installing new dependencies and restarting backend...
ssh -i "lvl_up_key.pem" ubuntu@%EC2_IP% << 'EOF'
cd /home/ubuntu/lvl_up/ai-backend-python

echo Installing new dependencies...
pip install joblib>=1.3.2

echo Stopping existing backend...
sudo systemctl stop ai-backend-python

echo Starting backend with AI Growth System...
sudo systemctl start ai-backend-python

echo Waiting for backend to start...
sleep 10

echo Checking backend status...
sudo systemctl status ai-backend-python --no-pager

echo Testing AI Growth endpoints...
curl -s http://localhost:4000/api/growth/status | python -m json.tool
EOF

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to deploy AI Growth System
    pause
    exit /b 1
)

echo.
echo ✅ AI Growth System deployed successfully!
echo.
echo 🧪 Testing AI Growth System...
echo.

REM Test the growth endpoints
echo 📊 Testing Growth Status...
curl -s http://%EC2_IP%:4000/api/growth/status | python -m json.tool

echo.
echo 🔍 Testing Growth Analysis for Imperium...
curl -s http://%EC2_IP%:4000/api/growth/analysis/Imperium | python -m json.tool

echo.
echo 🚀 Testing Auto-Improvement...
curl -s -X POST http://%EC2_IP%:4000/api/growth/auto-improve | python -m json.tool

echo.
echo 🎉 Complete AI System is now live and running!
echo.
echo 📚 Available endpoints:
echo.
echo 🌱 AI Growth System (NEW):
echo   - GET  http://%EC2_IP%:4000/api/growth/status
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Imperium
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Guardian
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Sandbox
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Conquest
echo   - GET  http://%EC2_IP%:4000/api/growth/insights
echo   - POST http://%EC2_IP%:4000/api/growth/train-models
echo   - POST http://%EC2_IP%:4000/api/growth/auto-improve
echo.
echo 🤖 AI Agents & GitHub Integration:
echo   - POST http://%EC2_IP%:4000/api/github/webhook
echo   - GET  http://%EC2_IP%:4000/api/github/status
echo   - POST http://%EC2_IP%:4000/api/agents/run/imperium
echo   - POST http://%EC2_IP%:4000/api/agents/run/guardian
echo   - POST http://%EC2_IP%:4000/api/agents/run/sandbox
echo   - POST http://%EC2_IP%:4000/api/agents/run/conquest
echo.
echo ⚔️ Conquest AI Code Creation:
echo   - POST http://%EC2_IP%:4000/api/conquest/analyze
echo   - POST http://%EC2_IP%:4000/api/conquest/create-proposal
echo   - POST http://%EC2_IP%:4000/api/conquest/implement
echo   - GET  http://%EC2_IP%:4000/api/conquest/status
echo.
echo 📖 See AI_GROWTH_SYSTEM_GUIDE.md for detailed documentation
echo.
pause 