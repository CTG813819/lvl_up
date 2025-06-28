@echo off
echo 🚀 AI Internet Learning System - GitHub Setup
echo =============================================
echo.

echo 📋 Checking current setup...
if not exist ".env" (
    echo ❌ .env file not found
    echo.
    echo 📝 Creating .env template...
    echo # OpenAI Configuration > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo. >> .env
    echo # MongoDB Configuration >> .env
    echo MONGODB_URI=mongodb://localhost:27017/lvl_up >> .env
    echo. >> .env
    echo # GitHub Configuration (REQUIRED for AI learning system) >> .env
    echo GITHUB_TOKEN=your_github_token_here >> .env
    echo GITHUB_REPO=your_github_username/your_repository_name >> .env
    echo GITHUB_USER=your_github_username >> .env
    echo GITHUB_EMAIL=your_github_email@example.com >> .env
    echo. >> .env
    echo # Server Configuration >> .env
    echo PORT=4000 >> .env
    echo NODE_ENV=production >> .env
    echo CORS_ORIGIN=* >> .env
    echo. >> .env
    echo # Logging >> .env
    echo LOG_LEVEL=info >> .env
    
    echo ✅ .env file created!
    echo.
    echo 🔧 Please edit the .env file with your actual GitHub credentials:
    echo    1. Get your GitHub token from: https://github.com/settings/tokens
    echo    2. Update GITHUB_TOKEN, GITHUB_REPO, GITHUB_USER, and GITHUB_EMAIL
    echo    3. Save the file and run this script again
    echo.
    pause
    exit /b
) else (
    echo ✅ .env file found
)

echo.
echo 🧪 Testing GitHub integration...
node test-github-integration.js

echo.
echo 📚 For detailed setup instructions, see: GITHUB_SETUP_GUIDE.md
echo.
pause 