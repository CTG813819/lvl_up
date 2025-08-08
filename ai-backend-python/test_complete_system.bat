@echo off
echo ========================================
echo    Complete System Test
echo ========================================
echo.

set EC2_IP=34.202.215.209

echo Testing all system components after restart
echo.

echo ========================================
echo    STEP 1: Check Service Status
echo ========================================
echo.

echo Checking if main service is running...
ssh -i "New.pem" ubuntu@%EC2_IP% "netstat -tlnp | grep 8000"
echo.

echo ========================================
echo    STEP 2: Test Live Analytics (Fixed)
echo ========================================
echo.

echo Testing live analytics with null safety fix...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/live-analytics | head -c 400"
echo.
echo.

echo ========================================
echo    STEP 3: Test AI Leaderboard
echo ========================================
echo.

echo Testing AI leaderboard with XP and adversarial wins...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/api/agent-metrics/leaderboard | head -c 400"
echo.
echo.

echo ========================================
echo    STEP 4: Test Recent Tests
echo ========================================
echo.

echo Testing recent tests from database...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/recent-tests | head -c 400"
echo.
echo.

echo ========================================
echo    STEP 5: Test AI Response (Critical)
echo ========================================
echo.

echo Testing if AIs respond to custody tests...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8000/custody/test/imperium | head -c 500"
echo.
echo.

echo ========================================
echo    STEP 6: Test Adversarial Testing
echo ========================================
echo.

echo Testing adversarial testing on port 8001...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8001/recent-scenarios | head -c 300"
echo.
echo.

echo ========================================
echo    STEP 7: Test Olympic History
echo ========================================
echo.

echo Testing Olympic history from database...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/olympics/history | head -c 200"
echo.
echo.

echo ========================================
echo    STEP 8: Check Service Logs
echo ========================================
echo.

echo Checking recent service logs...
ssh -i "New.pem" ubuntu@%EC2_IP% "tail -10 /home/ubuntu/ai-backend-python/main.log"
echo.
echo.

echo ========================================
echo    SUMMARY
echo ========================================
echo.
echo 🎯 System Status Check:
echo ✅ Main Service: Should be running on port 8000
echo ✅ Live Analytics: Should work with null safety fix
echo ✅ AI Leaderboard: Should show XP and adversarial wins
echo ✅ Recent Tests: Should load from Neon database
echo ❌ AI Response: Critical - AIs need to respond to tests
echo ✅ Adversarial Testing: Should work on port 8001
echo ✅ Olympic History: Should load from database
echo.
echo 🔧 Key Issues to Address:
echo 1. AI Service Connectivity (unified_ai_service_shared)
echo 2. AI Response Generation (ai_response and evaluation)
echo 3. Live Analytics Slice Error (if still occurring)
echo.
echo ======================================== 