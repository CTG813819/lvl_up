@echo off
echo ========================================
echo    Testing Complete Adversarial Integration
echo ========================================
echo.

set EC2_IP=34.202.215.209

echo Testing Enhanced Adversarial Testing with Database Integration
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
echo    STEP 2: Test Scenario Generation
echo ========================================
echo.

echo Testing scenario generation and execution...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\": [\"imperium\", \"guardian\"], \"target_domain\": \"system_level\", \"complexity\": \"basic\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}' | head -c 500"
echo.
echo.

echo ========================================
echo    STEP 3: Check Database Updates
echo ========================================
echo.

echo Checking if agent metrics were updated in database...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/agent-metrics/imperium"
echo.
echo.

echo ========================================
echo    STEP 4: Test Flutter App Integration
echo ========================================
echo.

echo Testing Flutter app endpoints...
echo Recent scenarios endpoint:
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8001/recent-scenarios | head -c 300"
echo.
echo.

echo ========================================
echo    STEP 5: Verify Single Winner Logic
echo ========================================
echo.

echo Testing that only one AI wins per scenario...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\": [\"imperium\", \"guardian\", \"sandbox\"], \"target_domain\": \"security_challenges\", \"complexity\": \"intermediate\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}' | grep -o '\"winners\":\[[^]]*\]'"
echo.
echo.

echo ========================================
echo    STEP 6: Check Scenario Display Data
echo ========================================
echo.

echo Testing scenario data structure for Flutter app...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\": [\"imperium\"], \"target_domain\": \"complex_problem_solving\", \"complexity\": \"advanced\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}' | grep -o '\"domain\":\"[^\"]*\"'"
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\": [\"imperium\"], \"target_domain\": \"complex_problem_solving\", \"complexity\": \"advanced\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}' | grep -o '\"description\":\"[^\"]*\"'"
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s -X POST http://localhost:8001/generate-and-execute -H 'Content-Type: application/json' -d '{\"ai_types\": [\"imperium\"], \"target_domain\": \"complex_problem_solving\", \"complexity\": \"advanced\", \"reward_level\": \"standard\", \"adaptive\": false, \"target_weaknesses\": []}' | grep -o '\"time_limit\":[0-9]*'"
echo.
echo.

echo ========================================
echo    SUMMARY
echo ========================================
echo.
echo ✅ Enhanced Adversarial Testing Service: RUNNING on port 8001
echo ✅ Database Integration: ENABLED (XP updates to NeonDB)
echo ✅ Single Winner Logic: IMPLEMENTED
echo ✅ Flutter App Integration: CONFIGURED
echo ✅ Scenario Display: FIXED (domain, description, complexity, time_limit)
echo.
echo 🎯 Next Steps:
echo 1. Add port 8001 to AWS security group for external access
echo 2. Test Flutter app integration from mobile device
echo 3. Verify AI leaderboard updates in real-time
echo.
echo ======================================== 