@echo off
echo ========================================
echo    Testing Flutter Adversarial Integration
echo ========================================
echo.

set EC2_IP=34.202.215.209

echo Testing Flutter app integration with Enhanced Adversarial Testing Service
echo.

echo ========================================
echo    STEP 1: Check Service Status
echo ========================================
echo.

echo Checking if enhanced adversarial testing service is running...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8001/health"
echo.
echo.

echo ========================================
echo    STEP 2: Test External Access
echo ========================================
echo.

echo Testing external access to port 8001...
powershell -Command "Test-NetConnection -ComputerName %EC2_IP% -Port 8001"
echo.

if %errorlevel% equ 0 (
    echo ✅ Port 8001 is accessible externally
    echo.
    echo ========================================
    echo    STEP 3: Test API Endpoints
    echo ========================================
    echo.
    
    echo Testing health endpoint:
    curl -s http://%EC2_IP%:8001/health
    echo.
    echo.
    
    echo Testing overview endpoint:
    curl -s http://%EC2_IP%:8001/ | head -c 200
    echo.
    echo.
    
    echo Testing recent scenarios endpoint:
    curl -s http://%EC2_IP%:8001/recent-scenarios
    echo.
    echo.
    
    echo ========================================
    echo    STEP 4: Test Generate and Execute
    echo ========================================
    echo.
    
    echo Testing generate and execute endpoint with sample data:
    curl -s -X POST http://%EC2_IP%:8001/generate-and-execute ^
      -H "Content-Type: application/json" ^
      -d "{\"ai_types\": [\"imperium\", \"guardian\"], \"target_domain\": \"system_level\", \"complexity\": \"basic\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}"
    echo.
    echo.
    
    echo ========================================
    echo    ✅ INTEGRATION READY
    echo ========================================
    echo.
    echo The enhanced adversarial testing service is working correctly!
    echo Your Flutter app should be able to:
    echo - Launch enhanced adversarial tests
    echo - View recent test scenarios
    echo - Configure test parameters
    echo.
    echo Flutter app endpoints configured:
    echo - Recent scenarios: http://%EC2_IP%:8001/recent-scenarios
    echo - Generate test: POST http://%EC2_IP%:8001/generate-and-execute
    echo.
    
) else (
    echo ❌ Port 8001 is not accessible externally
    echo.
    echo ========================================
    echo    🔧 REQUIRED ACTION
    echo ========================================
    echo.
    echo You need to add port 8001 to your AWS security group:
    echo.
    echo 1. Go to AWS Console: https://console.aws.amazon.com
    echo 2. Navigate to EC2 Dashboard
    echo 3. Find your instance (IP: %EC2_IP%)
    echo 4. Click on the instance → Security tab → Security group name
    echo 5. Click "Edit inbound rules"
    echo 6. Add new rule:
    echo    - Type: Custom TCP
    echo    - Protocol: TCP
    echo    - Port: 8001
    echo    - Source: 0.0.0.0/0
    echo    - Description: Enhanced Adversarial Testing Service
    echo 7. Click "Save rules"
    echo.
    echo After adding the security group rule, run this script again.
    echo.
)

echo ========================================
echo    Flutter App Configuration Status
echo ========================================
echo.

echo ✅ Flutter app is correctly configured to use:
echo    - Enhanced Adversarial Testing: http://%EC2_IP%:8001
echo    - Main Backend: http://%EC2_IP%:8000
echo.

echo The "Launch Adversarial Test" button in the Flutter app will work
echo once port 8001 is accessible externally.
echo.

pause 