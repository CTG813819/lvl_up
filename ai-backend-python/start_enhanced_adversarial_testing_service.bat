@echo off
REM Start Enhanced Adversarial Testing Service on Port 8001
REM This script starts the enhanced adversarial testing service as a standalone service

echo 🚀 Starting Enhanced Adversarial Testing Service on Port 8001...
echo =================================================================

REM Navigate to the backend directory
cd /d "%~dp0"

REM Check if port 8001 is already in use
netstat -an | findstr :8001 >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8001 is already in use. Stopping existing service...
    taskkill /f /im python.exe 2>nul
    timeout /t 2 /nobreak >nul
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%~dp0
set DATABASE_URL=postgresql://neon_user:neon_password@ep-cool-forest-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

REM Start the enhanced adversarial testing service
echo 🔧 Starting enhanced adversarial testing service...
start /b python standalone_enhanced_adversarial_testing.py

REM Wait a moment for the service to start
timeout /t 5 /nobreak >nul

REM Check if the service is running
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Enhanced Adversarial Testing Service is running on port 8001
    echo 🌐 Health check: http://localhost:8001/health
    echo 📊 Overview: http://localhost:8001/
    echo 🔗 API endpoint: http://localhost:8001/generate-and-execute
) else (
    echo ❌ Failed to start Enhanced Adversarial Testing Service
    exit /b 1
)

echo =================================================================
echo 🎯 Service is ready for enhanced adversarial testing!
echo =================================================================

pause 