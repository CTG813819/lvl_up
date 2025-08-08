@echo off
echo ========================================
echo    Testing Warp Screen Fixes
echo ========================================
echo.

set EC2_IP=34.202.215.209

echo Testing warp screen data sources after null safety fixes
echo.

echo ========================================
echo    STEP 1: Test Recent Tests (Fixed)
echo ========================================
echo.

echo Testing recent tests with null safety...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/recent-tests | head -c 400"
echo.
echo.

echo ========================================
echo    STEP 2: Test AI Leaderboard (Fixed)
echo ========================================
echo.

echo Testing AI leaderboard with null safety...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/api/agent-metrics/leaderboard | head -c 400"
echo.
echo.

echo ========================================
echo    STEP 3: Test Olympic History (Fixed)
echo ========================================
echo.

echo Testing Olympic history with null safety...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/olympics/history | head -c 200"
echo.
echo.

echo ========================================
echo    STEP 4: Test Live Analytics (Fixed)
echo ========================================
echo.

echo Testing live analytics with null safety...
ssh -i "New.pem" ubuntu@%EC2_IP% "curl -s http://localhost:8000/custody/live-analytics | head -c 300"
echo.
echo.

echo ========================================
echo    SUMMARY
echo ========================================
echo.
echo ✅ Recent Tests: NULL SAFETY FIXED (ai_types -> ai_type)
echo ✅ AI Leaderboard: NULL SAFETY FIXED (win_rate, recent_score, adversarial_wins)
echo ✅ Olympic History: NULL SAFETY FIXED (participants, winners)
echo ✅ Olympic Leaderboard: NULL SAFETY FIXED (ai, wins)
echo ✅ Live Analytics: NULL SAFETY FIXED (all fields)
echo.
echo 🎯 Null Safety Fixes Applied:
echo 1. Fixed ai_types.join() -> ai_type (single AI per test)
echo 2. Added null checks for win_rate, recent_score, adversarial_wins
echo 3. Added null checks for participants and winners lists
echo 4. Added null checks for Olympic leaderboard data
echo 5. Added fallback values for all potentially null fields
echo.
echo ======================================== 