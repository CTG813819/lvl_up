@echo off
echo ========================================
echo Deploying Mission System to EC2 Backend
echo ========================================

set EC2_IP=ec2-34-202-215-209.compute-1.amazonaws.com
set PEM_FILE=C:\projects\lvl_up\New.pem
set BACKEND_DIR=~/ai-backend-python

echo.
echo 1. Uploading updated database configuration...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\app\core\database.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/app/core/

echo.
echo 2. Uploading mission models...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\app\models\sql_models.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/app/models/

echo.
echo 3. Uploading updated Guardian AI service...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\app\services\guardian_ai_service.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/app/services/

echo.
echo 4. Uploading missions router...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\app\routers\missions.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/app/routers/

echo.
echo 5. Uploading updated main app...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\main.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/

echo.
echo 6. Uploading mission tables migration script...
scp -i "%PEM_FILE%" "C:\projects\lvl_up\ai-backend-python\create_mission_tables.py" ubuntu@%EC2_IP%:%BACKEND_DIR%/

echo.
echo 7. Running mission tables migration...
ssh -i "%PEM_FILE%" ubuntu@%EC2_IP% "cd %BACKEND_DIR% && source venv/bin/activate && python3 create_mission_tables.py"

echo.
echo 8. Restarting backend service...
ssh -i "%PEM_FILE%" ubuntu@%EC2_IP% "sudo systemctl restart ai-backend-python"

echo.
echo 9. Checking service status...
ssh -i "%PEM_FILE%" ubuntu@%EC2_IP% "sudo systemctl status ai-backend-python --no-pager"

echo.
echo 10. Testing mission endpoints...
echo Testing mission sync endpoint...
curl -X POST http://%EC2_IP%:4000/api/missions/sync -H "Content-Type: application/json" -d "[]"

echo.
echo Testing mission statistics endpoint...
curl -X GET http://%EC2_IP%:4000/api/missions/statistics

echo.
echo Testing mission health check endpoint...
curl -X POST http://%EC2_IP%:4000/api/missions/health-check

echo.
echo Testing Guardian AI health check with missions...
curl -X POST http://%EC2_IP%:4000/api/guardian/health-check

echo.
echo ========================================
echo Mission System Deployment Complete!
echo ========================================
echo.
echo Backend endpoints available:
echo - POST /api/missions/sync - Sync missions from frontend
echo - GET  /api/missions/statistics - Get mission statistics
echo - POST /api/missions/health-check - Run mission health check
echo - GET  /api/missions/ - Get missions with filtering
echo - GET  /api/missions/{id} - Get specific mission
echo.
echo Guardian AI now includes mission health checks!
echo.
pause 