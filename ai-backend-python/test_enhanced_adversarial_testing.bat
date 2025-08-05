@echo off
echo ========================================
echo    Testing Enhanced Adversarial Testing
echo ========================================
echo.

set EC2_IP=34.202.215.209

echo Testing Enhanced Adversarial Testing Service on %EC2_IP%:8001
echo.

echo 1. Testing Health Endpoint...
curl -s http://%EC2_IP%:8001/health
echo.
echo.

echo 2. Testing Overview Endpoint...
curl -s http://%EC2_IP%:8001/ | head -c 300
echo.
echo.

echo 3. Testing Recent Scenarios Endpoint...
curl -s http://%EC2_IP%:8001/recent-scenarios
echo.
echo.

echo 4. Testing Domains Endpoint...
curl -s http://%EC2_IP%:8001/domains
echo.
echo.

echo 5. Testing Complexities Endpoint...
curl -s http://%EC2_IP%:8001/complexities
echo.
echo.

echo 6. Testing Reward Levels Endpoint...
curl -s http://%EC2_IP%:8001/reward-levels
echo.
echo.

echo ========================================
echo    Testing Complete
echo ========================================
echo.

echo If you see JSON responses above, the service is working correctly!
echo If you see connection errors, make sure port 8001 is open in AWS security group.
echo.

pause 