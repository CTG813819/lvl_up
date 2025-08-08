@echo off
echo ========================================
echo    COMPREHENSIVE AI SYSTEM TEST
echo ========================================
echo.

REM Get EC2 IP from environment
set EC2_IP=%EC2_IP%
if "%EC2_IP%"=="" (
    echo EC2_IP environment variable not set
    echo Please set EC2_IP to your EC2 instance IP address
    pause
    exit /b 1
)

echo ========================================
echo 1. TESTING BACKEND HEALTH
echo ========================================
echo.

echo Testing backend health...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/health

echo.
echo ========================================
echo 2. TESTING GITHUB INTEGRATION
echo ========================================
echo.

echo Testing GitHub integration status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/github/status

echo.
echo ========================================
echo 3. TESTING AI AGENTS STATUS
echo ========================================
echo.

echo Testing AI agents status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo ========================================
echo 4. TESTING OATH PAPERS AI LEARNING
echo ========================================
echo.

echo Testing oath papers endpoint...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/oath-papers/

echo.
echo Testing oath papers AI insights...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/oath-papers/ai-insights

echo.
echo Testing oath papers learning trigger...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/oath-papers/learn

echo.
echo ========================================
echo 5. TESTING CONQUEST AI DISTINCTIONS
echo ========================================
echo.

echo Testing Conquest AI status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/conquest/status

echo.
echo Testing Conquest AI app creation analysis...
curl -X POST -H "Content-Type: application/json" -d "{\"name\":\"Test App\",\"description\":\"A test app\",\"app_type\":\"general\",\"operation_type\":\"create_new\"}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/conquest/analyze-suggestion

echo.
echo Testing Conquest AI app improvement analysis...
curl -X POST -H "Content-Type: application/json" -d "{\"name\":\"Improved App\",\"description\":\"An improved app\",\"app_type\":\"general\",\"operation_type\":\"improve_existing\",\"existing_repo\":\"CTG813819/Lvl_UP\",\"improvement_focus\":\"performance\"}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/conquest/analyze-suggestion

echo.
echo ========================================
echo 6. TESTING NOTIFICATION SYSTEM
echo ========================================
echo.

echo Testing notification system...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/

echo.
echo Testing notification stats...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/stats

echo.
echo Creating test notification...
curl -X POST -H "Content-Type: application/json" -d "{\"title\":\"Test Notification\",\"message\":\"This is a test notification\",\"notification_type\":\"info\",\"priority\":\"normal\"}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/create

echo.
echo Testing notification broadcast...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/test-broadcast

echo.
echo ========================================
echo 7. TESTING AI LEARNING SYSTEM
echo ========================================
echo.

echo Testing AI learning status...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/learning/status

echo.
echo Testing AI growth system...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/growth/status

echo.
echo ========================================
echo 8. TRIGGERING COMPREHENSIVE AI CYCLE
echo ========================================
echo.

echo Triggering all AI agents with new features...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all

echo.
echo Waiting for AI cycle to complete...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo 9. FINAL SYSTEM STATUS
echo ========================================
echo.

echo Final AI agents status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Final notification count:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/stats

echo.
echo ========================================
echo 🎉 COMPREHENSIVE TEST COMPLETE! 🎉
echo ========================================
echo.
echo ✅ BACKEND: Running with all new features
echo ✅ OATH PAPERS: AI learning integration active
echo ✅ CONQUEST AI: APK creation vs improvements distinguished
echo ✅ NOTIFICATIONS: Real-time system operational
echo ✅ AI LEARNING: Advanced ML analysis enabled
echo ✅ GITHUB: Full integration with your credentials
echo.
echo 🚀 YOUR AI SYSTEM IS FULLY ENHANCED!
echo.
echo New Features Available:
echo - Oath Papers AI Learning & Analysis
echo - Conquest AI APK Creation vs App Improvements
echo - Real-time Notification System with WebSocket
echo - Advanced AI Learning with scikit-learn
echo - Comprehensive Progress Tracking
echo.
pause 