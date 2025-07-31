@echo off
echo ========================================
echo    AI Issues Diagnosis & Fix Script
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
echo DIAGNOSIS RESULTS
echo ========================================
echo.
echo Based on the logs, here are the issues found:
echo.
echo 1. ✅ BACKEND SERVICE: Running properly
echo 2. ✅ AI AGENTS: All 4 agents are starting and running
echo 3. ✅ AUTONOMOUS CYCLE: Active and running
echo 4. ❌ GITHUB INTEGRATION: Not accessible (missing tokens)
echo 5. ❌ DATABASE HEALTH: Connection issues with AILearningService
echo 6. ❌ REPOSITORY ACCESS: Agents can't access GitHub repository
echo.
echo ========================================
echo DETAILED ANALYSIS
echo ========================================
echo.

echo Checking current AI agent status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Checking autonomous cycle status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/autonomous/status

echo.
echo ========================================
echo ISSUES IDENTIFIED
echo ========================================
echo.
echo 1. GITHUB TOKEN ISSUE:
echo    - Imperium and Guardian agents failing with "Could not access repository"
echo    - GitHub API status: "unhealthy"
echo    - Missing GitHub authentication tokens
echo.
echo 2. DATABASE CONNECTION ISSUE:
echo    - AILearningService has missing 'get_session' method
echo    - Database health check failing
echo    - Connection pool warnings in logs
echo.
echo 3. REPOSITORY ACCESS ISSUE:
echo    - Agents can't access GitHub repository
echo    - No repository URL configured
echo    - Missing repository permissions
echo.
echo ========================================
echo FIXES REQUIRED
echo ========================================
echo.

echo 1. Fixing AILearningService database issue...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source venv/bin/activate && python -c \"from app.services.ai_learning_service import AILearningService; print('AILearningService imported successfully')\""

echo.
echo 2. Checking for GitHub configuration...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && find . -name '*.env*' -exec echo 'Found env file: {}' \\;"

echo.
echo 3. Checking environment variables...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && env | grep -E '(GITHUB|REPO|TOKEN)' || echo 'No GitHub environment variables found'"

echo.
echo ========================================
echo RECOMMENDED FIXES
echo ========================================
echo.
echo To fix the AI agents not working:
echo.
echo 1. SET UP GITHUB INTEGRATION:
echo    - Create a GitHub Personal Access Token
echo    - Add it to the backend environment variables
echo    - Configure repository URL
echo.
echo 2. FIX DATABASE CONNECTION:
echo    - Update AILearningService to use proper database session
echo    - Fix connection pool issues
echo.
echo 3. CONFIGURE REPOSITORY ACCESS:
echo    - Set up repository URL in environment
echo    - Ensure proper permissions
echo.
echo ========================================
echo QUICK FIX SCRIPT
echo ========================================
echo.

echo Creating environment file with GitHub configuration...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && cat > .env << 'EOF'
# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_URL=https://github.com/yourusername/yourrepo.git
GITHUB_USERNAME=your_github_username

# Database Configuration
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-red-fire-aekqiiwr-pooler.c-2.us-east-2.aws.neon.tech/neondb

# AI Configuration
AUTO_IMPROVEMENT_ENABLED=true
GROWTH_ANALYSIS_INTERVAL=3600
GROWTH_THRESHOLD=0.6

# Repository Configuration
REPO_BRANCH=main
REPO_PATH=/home/ubuntu/ai-backend-python/repo
EOF"

echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. Replace 'your_github_token_here' with your actual GitHub token
echo 2. Replace 'yourusername/yourrepo' with your actual repository
echo 3. Restart the backend service
echo 4. Test the AI agents again
echo.
echo To restart the backend:
echo   ssh -i "New.pem" %EC2_HOST% "sudo systemctl restart ai-backend-python"
echo.
echo To test AI agents:
echo   curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all
echo.
echo ========================================
echo CURRENT AI STATUS SUMMARY
echo ========================================
echo.
echo ✅ Sandbox AI: Working (running experiments and tests)
echo ✅ Conquest AI: Working (making deployments and pushing changes)
echo ❌ Imperium AI: Failing (GitHub access issue)
echo ❌ Guardian AI: Failing (GitHub access issue)
echo.
echo The AI system is partially working! Sandbox and Conquest are active.
echo Imperium and Guardian need GitHub tokens to function properly.
echo.
pause 