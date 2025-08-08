@echo off
echo Deploying Complete AI System to EC2...
echo.
echo This deployment includes:
echo   - GitHub Integration and Webhooks
echo   - Conquest AI - Creates new app repositories and APKs
echo   - Autonomous AI Agents (Imperium, Guardian, Sandbox, Conquest)
echo   - AI Growth System with scikit-learn
echo   - Background Services and Autonomous Cycles
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

REM Copy ALL AI System files to EC2
echo Copying Complete AI System files...
echo.

echo Core Backend Files:
scp -i "New.pem" -r ai-backend-python/main.py %EC2_HOST%:/home/ubuntu/ai-backend-python/
scp -i "New.pem" -r ai-backend-python/requirements.txt %EC2_HOST%:/home/ubuntu/ai-backend-python/
scp -i "New.pem" -r ai-backend-python/start.py %EC2_HOST%:/home/ubuntu/ai-backend-python/

echo Database Models:
scp -i "New.pem" -r ai-backend-python/app/models/sql_models.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/models/

echo AI Services:
scp -i "New.pem" -r ai-backend-python/app/services/ai_agent_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/github_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/ai_learning_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/ml_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/background_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/ai_growth_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/
scp -i "New.pem" -r ai-backend-python/app/services/conquest_ai_service.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/services/

echo API Routers:
scp -i "New.pem" -r ai-backend-python/app/routers/github_webhook.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/agents.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/conquest.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/growth.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/imperium.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/guardian.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/
scp -i "New.pem" -r ai-backend-python/app/routers/sandbox.py %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/

echo Documentation:
scp -i "New.pem" -r AI_GROWTH_SYSTEM_GUIDE.md %EC2_HOST%:/home/ubuntu/
scp -i "New.pem" -r CONQUEST_AI_README.md %EC2_HOST%:/home/ubuntu/
scp -i "New.pem" -r AUTONOMOUS_AI_SYSTEM.md %EC2_HOST%:/home/ubuntu/

echo GitHub Actions and CI/CD:
scp -i "New.pem" -r .github/workflows/ %EC2_HOST%:/home/ubuntu/.github/
scp -i "New.pem" -r deploy.sh %EC2_HOST%:/home/ubuntu/

if %ERRORLEVEL% neq 0 (
    echo Failed to copy files to EC2
    pause
    exit /b 1
)

echo Files copied successfully
echo.

REM Install dependencies and restart backend
echo Installing dependencies and restarting backend...
ssh -i "New.pem" %EC2_HOST% << 'EOF'
cd /home/ubuntu/ai-backend-python

echo Installing new dependencies...
pip install joblib>=1.3.2 scikit-learn>=1.3.0 aiohttp>=3.8.0

echo Stopping existing backend...
sudo systemctl stop ai-backend-python

echo Starting backend with Complete AI System...
sudo systemctl start ai-backend-python

echo Waiting for backend to start...
sleep 15

echo Checking backend status...
sudo systemctl status ai-backend-python --no-pager

echo Testing core endpoints...
curl -s http://localhost:4000/health | python -m json.tool
EOF

if %ERRORLEVEL% neq 0 (
    echo Failed to deploy Complete AI System
    pause
    exit /b 1
)

echo.
echo Complete AI System deployed successfully!
echo.

REM Test all AI systems
echo Testing Complete AI System...
echo.

echo Testing Health Check:
curl -s http://%EC2_IP%:4000/health | python -m json.tool

echo.
echo Testing AI Agents:
curl -s http://%EC2_IP%:4000/api/agents/status | python -m json.tool

echo.
echo Testing Conquest AI:
curl -s http://%EC2_IP%:4000/api/conquest/status | python -m json.tool

echo.
echo Testing AI Growth System:
curl -s http://%EC2_IP%:4000/api/growth/status | python -m json.tool

echo.
echo Testing GitHub Integration:
curl -s http://%EC2_IP%:4000/api/github/status | python -m json.tool

echo.
echo Complete AI System is now live and running!
echo.
echo Available endpoints:
echo.
echo Conquest AI - App Creation and APK Building:
echo   - POST http://%EC2_IP%:4000/api/conquest/create-app
echo   - GET  http://%EC2_IP%:4000/api/conquest/deployments
echo   - GET  http://%EC2_IP%:4000/api/conquest/deployment/{app_id}
echo   - POST http://%EC2_IP%:4000/api/conquest/analyze-suggestion
echo   - GET  http://%EC2_IP%:4000/api/conquest/status
echo.
echo Autonomous AI Agents:
echo   - POST http://%EC2_IP%:4000/api/agents/run/imperium
echo   - POST http://%EC2_IP%:4000/api/agents/run/guardian
echo   - POST http://%EC2_IP%:4000/api/agents/run/sandbox
echo   - POST http://%EC2_IP%:4000/api/agents/run/conquest
echo   - POST http://%EC2_IP%:4000/api/agents/run/all
echo   - GET  http://%EC2_IP%:4000/api/agents/status
echo.
echo AI Growth System (scikit-learn):
echo   - GET  http://%EC2_IP%:4000/api/growth/status
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Imperium
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Guardian
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Sandbox
echo   - GET  http://%EC2_IP%:4000/api/growth/analysis/Conquest
echo   - GET  http://%EC2_IP%:4000/api/growth/insights
echo   - POST http://%EC2_IP%:4000/api/growth/train-models
echo   - POST http://%EC2_IP%:4000/api/growth/auto-improve
echo.
echo GitHub Integration and Webhooks:
echo   - POST http://%EC2_IP%:4000/api/github/webhook
echo   - GET  http://%EC2_IP%:4000/api/github/status
echo.
echo System Monitoring:
echo   - GET  http://%EC2_IP%:4000/health
echo   - GET  http://%EC2_IP%:4000/debug
echo   - GET  http://%EC2_IP%:4000/api/app/status
echo.
echo How to use Conquest AI:
echo.
echo 1. Create a new app:
echo    curl -X POST http://%EC2_IP%:4000/api/conquest/create-app
echo    -H "Content-Type: application/json"
echo    -d "{
echo      \"name\": \"My Awesome App\",
echo      \"description\": \"A fitness tracking app with social features\",
echo      \"keywords\": [\"fitness\", \"social\", \"tracking\"],
echo      \"app_type\": \"fitness\",
echo      \"features\": [\"workout_tracking\", \"social_sharing\"]
echo    }"
echo.
echo 2. Check deployment status:
echo    curl http://%EC2_IP%:4000/api/conquest/deployments
echo.
echo 3. Analyze app suggestion:
echo    curl -X POST http://%EC2_IP%:4000/api/conquest/analyze-suggestion
echo    -H "Content-Type: application/json"
echo    -d "{
echo      \"name\": \"Game App\",
echo      \"description\": \"A puzzle game with multiplayer\",
echo      \"keywords\": [\"game\", \"puzzle\", \"multiplayer\"],
echo      \"app_type\": \"game\"
echo    }"
echo.
echo Conquest AI Capabilities:
echo   - Creates new GitHub repositories
echo   - Generates complete Flutter applications
echo   - Builds APKs automatically
echo   - Integrates with GitHub Actions
echo   - Supports multiple app types (game, social, fitness, etc.)
echo   - Analyzes app suggestions and provides recommendations
echo   - Tracks deployment status and build logs
echo.
echo See documentation files for detailed guides:
echo   - AI_GROWTH_SYSTEM_GUIDE.md
echo   - CONQUEST_AI_README.md
echo   - AUTONOMOUS_AI_SYSTEM.md
echo.
pause 