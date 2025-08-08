@echo off
echo 🔍 Testing Backend Connection
echo =============================

set BACKEND_IP=34.202.215.209
set BACKEND_PORT=4000

echo [INFO] Testing connection to: http://%BACKEND_IP%:%BACKEND_PORT%
echo.

REM Test basic connectivity
echo [INFO] Step 1: Testing basic connectivity...
ping -n 1 %BACKEND_IP% >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend server is reachable
) else (
    echo [ERROR] Cannot reach backend server
    pause
    exit /b 1
)

REM Test backend health endpoint
echo [INFO] Step 2: Testing backend health endpoint...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" "http://%BACKEND_IP%:%BACKEND_PORT%/health"
if %errorlevel% equ 0 (
    echo [SUCCESS] Backend health endpoint is accessible
) else (
    echo [WARNING] Backend health endpoint not accessible
    echo [INFO] The backend might not be running
)

REM Test API endpoints
echo [INFO] Step 3: Testing API endpoints...
echo [INFO] Testing proposals endpoint...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" "http://%BACKEND_IP%:%BACKEND_PORT%/api/proposals"
if %errorlevel% equ 0 (
    echo [SUCCESS] Proposals endpoint accessible
) else (
    echo [WARNING] Proposals endpoint not accessible
)

echo [INFO] Testing learning endpoint...
curl -s -o nul -w "HTTP Status: %%{http_code}\n" "http://%BACKEND_IP%:%BACKEND_PORT%/api/learning/data"
if %errorlevel% equ 0 (
    echo [SUCCESS] Learning endpoint accessible
) else (
    echo [WARNING] Learning endpoint not accessible
)

echo.
echo [INFO] Connection test completed!
echo.
echo [INFO] Your Flutter app should now connect to:
echo    Backend: http://%BACKEND_IP%:%BACKEND_PORT%
echo.
echo [INFO] If any endpoints failed, make sure:
echo    1. Your EC2 instance is running
echo    2. The backend is started on EC2
echo    3. Security group allows port %BACKEND_PORT%
echo    4. Environment variables are set on EC2
echo.

pause 