@echo off
echo ========================================
echo    GitHub Configuration Fix
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
echo CURRENT STATUS
echo ========================================
echo.
echo ✅ Sandbox AI: Working (running experiments)
echo ✅ Conquest AI: Working (making deployments)
echo ❌ Imperium AI: Failing (needs GitHub token)
echo ❌ Guardian AI: Failing (needs GitHub token)
echo.

echo ========================================
echo CREATING GITHUB CONFIGURATION
echo ========================================
echo.

echo Creating .env file with GitHub configuration...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '# GitHub Configuration' > .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_TOKEN=your_github_token_here' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_REPO_URL=https://github.com/yourusername/yourrepo.git' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GITHUB_USERNAME=your_github_username' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo '# AI Configuration' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'AUTO_IMPROVEMENT_ENABLED=true' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GROWTH_ANALYSIS_INTERVAL=3600' >> .env"
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && echo 'GROWTH_THRESHOLD=0.6' >> .env"

echo.
echo ========================================
echo CONFIGURATION CREATED
echo ========================================
echo.

echo Current .env file contents:
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && cat .env"

echo.
echo ========================================
echo NEXT STEPS TO COMPLETE SETUP
echo ========================================
echo.
echo 1. EDIT THE .ENV FILE:
echo    ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && nano .env"
echo.
echo 2. REPLACE THESE VALUES:
echo    - your_github_token_here → Your actual GitHub Personal Access Token
echo    - yourusername/yourrepo → Your actual GitHub repository URL
echo    - your_github_username → Your GitHub username
echo.
echo 3. RESTART THE BACKEND:
echo    ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"
echo.
echo 4. TEST THE AI AGENTS:
echo    curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all
echo.
echo ========================================
echo HOW TO GET GITHUB TOKEN
echo ========================================
echo.
echo 1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
echo 2. Click "Generate new token (classic)"
echo 3. Give it a name like "AI Backend Token"
echo 4. Select scopes: repo, workflow, admin:org
echo 5. Copy the token and replace 'your_github_token_here' in the .env file
echo.
echo ========================================
echo CURRENT AI ACTIVITY
echo ========================================
echo.

echo Testing current AI status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Testing recent activity...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/learning/data

echo.
echo ========================================
echo SUMMARY
echo ========================================
echo.
echo The AI system is PARTIALLY WORKING:
echo.
echo ✅ WORKING AGENTS:
echo    - Sandbox AI: Running experiments and tests
echo    - Conquest AI: Making deployments and pushing changes
echo.
echo ❌ NEEDS GITHUB TOKEN:
echo    - Imperium AI: Code analysis and improvements
echo    - Guardian AI: Security analysis and monitoring
echo.
echo Once you add the GitHub token, ALL 4 AI agents will be fully functional!
echo.
pause 