@echo off
echo ========================================
echo    Fixing Port 8001 Access
echo ========================================
echo.

echo Current Status:
echo ✅ Enhanced Adversarial Testing Service is running on EC2 (port 8001)
echo ✅ Service is responding locally
echo ❌ Port 8001 is not accessible externally (security group issue)
echo.

echo ========================================
echo    STEP 1: Add Security Group Rule
echo ========================================
echo.

echo To fix this, you need to add port 8001 to your AWS security group:
echo.
echo 1. Go to AWS Console: https://console.aws.amazon.com
echo 2. Navigate to EC2 Dashboard
echo 3. Find your instance (IP: 34.202.215.209)
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

echo ========================================
echo    STEP 2: Test Connection
echo ========================================
echo.

echo After adding the security group rule, press any key to test the connection...
pause

echo.
echo Testing connection to enhanced adversarial testing service...
echo.

echo 1. Testing Health Endpoint:
curl -s http://34.202.215.209:8001/health
echo.
echo.

echo 2. Testing Overview Endpoint:
curl -s http://34.202.215.209:8001/ | head -c 200
echo.
echo.

echo 3. Testing Recent Scenarios Endpoint:
curl -s http://34.202.215.209:8001/recent-scenarios
echo.
echo.

echo ========================================
echo    STEP 3: Test Flutter App Integration
echo ========================================
echo.

echo If you see JSON responses above, the service is working correctly!
echo.
echo Your Flutter app should now be able to:
echo - Launch enhanced adversarial tests
echo - View recent test scenarios
echo - Configure test parameters
echo.

echo ========================================
echo    Available Endpoints
echo ========================================
echo.

echo Enhanced Adversarial Testing Service (Port 8001):
echo - Health Check: http://34.202.215.209:8001/health
echo - Overview: http://34.202.215.209:8001/
echo - Generate Test: POST http://34.202.215.209:8001/generate-and-execute
echo - Recent Scenarios: http://34.202.215.209:8001/recent-scenarios
echo - Available Domains: http://34.202.215.209:8001/domains
echo - Available Complexities: http://34.202.215.209:8001/complexities
echo - Available Reward Levels: http://34.202.215.209:8001/reward-levels
echo.

echo Main Backend Service (Port 8000):
echo - Health Check: http://34.202.215.209:8000/api/health
echo - API Documentation: http://34.202.215.209:8000/docs
echo.

pause 