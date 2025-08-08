@echo off
REM Test EC2 Backend Connection
REM This script tests if your EC2 backend is accessible

echo 🔍 Testing EC2 Backend Connection
echo =================================

set EC2_IP=34.202.215.209
set BACKEND_PORT=4000

echo [INFO] Testing connection to: http://%EC2_IP%:%BACKEND_PORT%

REM Test basic connectivity
echo [INFO] Step 1: Testing basic connectivity...
ping -n 1 %EC2_IP% >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] EC2 instance is reachable
) else (
    echo [ERROR] Cannot reach EC2 instance
    pause
    exit /b 1
)

REM Test backend health endpoint
echo [INFO] Step 2: Testing backend health endpoint...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend health endpoint is accessible
) else (
    echo [WARNING] Backend health endpoint not accessible
    echo [INFO] The backend might not be running on EC2
)

REM Test AI endpoints
echo [INFO] Step 3: Testing AI endpoints...
echo [INFO] Testing Imperium AI endpoint...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/api/imperium/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Imperium AI endpoint accessible
) else (
    echo [WARNING] Imperium AI endpoint not accessible
)

echo [INFO] Testing Guardian AI endpoint...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/api/guardian/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Guardian AI endpoint accessible
) else (
    echo [WARNING] Guardian AI endpoint not accessible
)

echo [INFO] Testing Sandbox AI endpoint...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/api/sandbox/health" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Sandbox AI endpoint accessible
) else (
    echo [WARNING] Sandbox AI endpoint not accessible
)

REM Test learning endpoints
echo [INFO] Step 4: Testing learning endpoints...
echo [INFO] Testing learning data endpoint...
curl -s "http://%EC2_IP%:%BACKEND_PORT%/api/learning/data" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Learning data endpoint accessible
) else (
    echo [WARNING] Learning data endpoint not accessible
)

echo.
echo [INFO] Connection test completed!
echo.
echo [INFO] Your Flutter app should now connect to:
echo    Backend: http://%EC2_IP%:%BACKEND_PORT%
echo.
echo [INFO] If any endpoints failed, make sure:
echo    1. Your EC2 instance is running
echo    2. The backend is started on EC2
echo    3. Security group allows port %BACKEND_PORT%
echo    4. Environment variables are set on EC2
echo.

pause 