@echo off
echo 🚀 EC2 Backend Fixes Runner
echo ================================

echo.
echo Step 1: SSH into EC2 instance...
echo Run this command in your terminal:
echo ssh -i "C:/projects/lvl_up/New.pem" ubuntu@34.202.215.209
echo.
pause

echo.
echo Step 2: Once connected to EC2, run these commands:
echo.
echo # Run cleanup script
echo chmod +x /home/ubuntu/cleanup_ec2.sh
echo /home/ubuntu/cleanup_ec2.sh
echo.
echo # Navigate to backend and run fixes
echo cd /home/ubuntu/ai-backend-python
echo python3 fix_backend_issues.py
echo.
echo # Install dependencies
echo pip3 install -r requirements.txt
echo.
echo # Restart backend
echo sudo systemctl restart ai-backend-python
echo # OR if no service:
echo python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause

echo.
echo Step 3: Test the fixes
echo.
echo # Test conquest progress logs
echo curl http://34.202.215.209:4000/api/conquest/progress-logs
echo.
echo # Test proposals endpoint
echo curl http://34.202.215.209:4000/api/proposals?limit=5
echo.
pause

echo.
echo ✅ Fixes completed! Your backend should now be working properly.
echo.
echo Expected results:
echo - Conquest AI: 3 sample apps with progress logs
echo - Imperium AI: 3 sample proposals  
echo - AI Learning: Every 20 minutes instead of 1 hour
echo - Disk space: Freed up 3-4GB
echo.
pause 