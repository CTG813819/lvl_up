@echo off
REM Training Ground Server Startup Script for Windows
REM This script starts the training ground server on port 8002

echo 🚀 Starting Training Ground Server on port 8002...

REM Navigate to the backend directory
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables
set TRAINING_GROUND_PORT=8002
set TRAINING_GROUND_HOST=0.0.0.0
set ENVIRONMENT=production

REM Start the training ground server
echo Starting training ground server...
start /B python training_ground_server.py

echo ✅ Training Ground Server started on port 8002

REM Wait a moment for the server to start
timeout /t 3 /nobreak > nul

REM Check if the server is running
curl -s http://localhost:8002/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Training Ground Server is healthy and running
) else (
    echo ❌ Training Ground Server failed to start properly
    exit /b 1
) 