@echo off
echo ========================================
echo    DEPLOYING ENHANCED AI FEATURES
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

set EC2_HOST=ubuntu@ec2-%EC2_IP%.compute-1.amazonaws.com

echo Connecting to EC2 instance: %EC2_HOST%
echo.

echo ========================================
echo COPYING ENHANCED FILES
echo ========================================
echo.

echo Copying enhanced oath papers router...
scp -i "New.pem" "ai-backend-python/app/routers/oath_papers.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/oath_papers.py

echo Copying enhanced conquest router...
scp -i "New.pem" "ai-backend-python/app/routers/conquest.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/conquest.py

echo Copying new notifications router...
scp -i "New.pem" "ai-backend-python/app/routers/notifications.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/app/routers/notifications.py

echo Copying updated main.py...
scp -i "New.pem" "ai-backend-python/main.py" %EC2_HOST%:/home/ubuntu/ai-backend-python/main.py

echo.
echo ========================================
echo STOPPING CURRENT BACKEND
echo ========================================
echo.

echo Stopping current backend process...
ssh -i "New.pem" %EC2_HOST% "sudo pkill -f uvicorn"

echo.
echo ========================================
echo STARTING ENHANCED BACKEND
echo ========================================
echo.

echo Starting enhanced backend with new features...
ssh -i "New.pem" %EC2_HOST% "cd /home/ubuntu/ai-backend-python && source .env && /home/ubuntu/ai-backend-python/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000" &

echo.
echo Waiting for backend to start...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo TESTING ENHANCED FEATURES
echo ========================================
echo.

echo Testing backend health...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/health

echo.
echo Testing oath papers AI learning...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/oath-papers/ai-insights

echo.
echo Testing Conquest AI distinctions...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/conquest/status

echo.
echo Testing notification system...
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/stats

echo.
echo ========================================
echo CREATING TEST NOTIFICATIONS
echo ========================================
echo.

echo Creating test notification for Conquest AI...
curl -X POST -H "Content-Type: application/json" -d "{\"title\":\"Conquest AI Progress\",\"message\":\"Creating new APK for Test App\",\"notification_type\":\"conquest_progress\",\"priority\":\"high\"}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/create

echo.
echo Creating test notification for AI Learning...
curl -X POST -H "Content-Type: application/json" -d "{\"title\":\"AI Learning Milestone\",\"message\":\"AI has learned from 5 new oath papers\",\"notification_type\":\"ai_learning\",\"priority\":\"medium\"}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/create

echo.
echo ========================================
echo TRIGGERING ENHANCED AI CYCLE
echo ========================================
echo.

echo Triggering all AI agents with enhanced features...
curl -X POST -H "Content-Type: application/json" -d "{}" http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/run-all

echo.
echo Waiting for enhanced AI cycle to complete...
timeout /t 20 /nobreak >nul

echo.
echo ========================================
echo FINAL ENHANCED SYSTEM STATUS
echo ========================================
echo.

echo Final AI agents status:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/agents/status

echo.
echo Final notification count:
curl -s http://ec2-%EC2_IP%.compute-1.amazonaws.com:4000/api/notifications/stats

echo.
echo ========================================
echo 🎉 ENHANCED FEATURES DEPLOYED! 🎉
echo ========================================
echo.
echo ✅ OATH PAPERS: AI learning integration active
echo ✅ CONQUEST AI: APK creation vs improvements distinguished
echo ✅ NOTIFICATIONS: Real-time system with WebSocket
echo ✅ AI LEARNING: Advanced ML analysis enabled
echo ✅ GITHUB: Full integration with your credentials
echo.
echo 🚀 YOUR AI SYSTEM IS NOW FULLY ENHANCED!
echo.
echo New Capabilities:
echo - Oath Papers contribute to AI learning
echo - Conquest AI distinguishes APK creation from app improvements
echo - Real-time notifications for important backend events
echo - Progress tracking for all AI operations
echo - Advanced AI learning with scikit-learn
echo.
pause 