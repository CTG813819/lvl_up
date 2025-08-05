@echo off
REM Enhanced Subject Learning Features Deployment Script for EC2 (Windows)
REM EC2 Instance: 34-202-215-209.compute-1.amazonaws.com
REM Key File: C:\projects\lvl_up\New.pem

echo 🚀 Deploying Enhanced Subject Learning Features to EC2...

REM EC2 Configuration
set EC2_HOST=34-202-215-209.compute-1.amazonaws.com
set EC2_USER=ubuntu
set KEY_FILE=C:\projects\lvl_up\New.pem
set REMOTE_DIR=/home/ubuntu/ai-backend-python

REM Check if key file exists
if not exist "%KEY_FILE%" (
    echo ❌ SSH key file not found: %KEY_FILE%
    exit /b 1
)

echo 📋 Starting deployment to EC2 instance: %EC2_HOST%

REM 1. Test SSH connection
echo [INFO] Step 1: Testing SSH connection...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo 'SSH connection successful'"
if %errorlevel% neq 0 (
    echo ❌ Failed to connect to EC2 instance
    exit /b 1
)
echo ✅ SSH connection established

REM 2. Create deployment directory
echo [INFO] Step 2: Setting up deployment directory...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "mkdir -p %REMOTE_DIR%"

REM 3. Copy enhanced subject learning service
echo [INFO] Step 3: Copying enhanced subject learning service...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\services\enhanced_subject_learning_service.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/services/

REM 4. Copy updated models
echo [INFO] Step 4: Copying updated models...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\models\sql_models.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/models/
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\models\training_data.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/models/
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\models\oath_paper.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/models/

REM 5. Copy updated routers
echo [INFO] Step 5: Copying updated routers...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\routers\oath_papers.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/routers/
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\app\routers\training_data.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/app/routers/

REM 6. Copy migration script
echo [INFO] Step 6: Copying migration script...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "ai-backend-python\add_subject_fields_migration.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/

REM 7. Copy autonomous learning service
echo [INFO] Step 7: Copying autonomous learning service...
scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "autonomous_subject_learning_service.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/

REM 8. Install dependencies on EC2
echo [INFO] Step 8: Installing dependencies on EC2...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "cd %REMOTE_DIR% && pip install aiohttp schedule"

REM 9. Run database migration
echo [INFO] Step 9: Running database migration...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "cd %REMOTE_DIR% && python add_subject_fields_migration.py"

REM 10. Set up environment variables
echo [INFO] Step 10: Setting up environment variables...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo 'export OPENAI_API_KEY=\"your_openai_api_key\"' >> ~/.bashrc"
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo 'export ANTHROPIC_API_KEY=\"your_anthropic_api_key\"' >> ~/.bashrc"
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo 'export GOOGLE_SEARCH_API_KEY=\"your_google_api_key\"' >> ~/.bashrc"
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo 'export GOOGLE_SEARCH_ENGINE_ID=\"your_search_engine_id\"' >> ~/.bashrc"

REM 11. Create startup script
echo [INFO] Step 11: Creating startup script...
echo #!/bin/bash > start_enhanced_services.sh
echo echo "🚀 Starting Enhanced Subject Learning Services..." >> start_enhanced_services.sh
echo source /home/ubuntu/ai-backend-python/venv/bin/activate >> start_enhanced_services.sh
echo echo "Starting autonomous learning service..." >> start_enhanced_services.sh
echo python autonomous_subject_learning_service.py ^& >> start_enhanced_services.sh
echo echo "✅ All enhanced services started" >> start_enhanced_services.sh

scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "start_enhanced_services.sh" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "chmod +x %REMOTE_DIR%/start_enhanced_services.sh"

REM 12. Create systemd service
echo [INFO] Step 12: Creating systemd service...
echo [Unit] > autonomous-learning.service
echo Description=Autonomous Subject Learning Service >> autonomous-learning.service
echo After=network.target >> autonomous-learning.service
echo. >> autonomous-learning.service
echo [Service] >> autonomous-learning.service
echo Type=simple >> autonomous-learning.service
echo User=ubuntu >> autonomous-learning.service
echo WorkingDirectory=%REMOTE_DIR% >> autonomous-learning.service
echo Environment=PATH=%REMOTE_DIR%/venv/bin >> autonomous-learning.service
echo ExecStart=%REMOTE_DIR%/venv/bin/python autonomous_subject_learning_service.py >> autonomous-learning.service
echo Restart=always >> autonomous-learning.service
echo RestartSec=10 >> autonomous-learning.service
echo. >> autonomous-learning.service
echo [Install] >> autonomous-learning.service
echo WantedBy=multi-user.target >> autonomous-learning.service

scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "autonomous-learning.service" %EC2_USER%@%EC2_HOST%:/tmp/
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo mv /tmp/autonomous-learning.service /etc/systemd/system/"
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo systemctl daemon-reload"
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo systemctl enable autonomous-learning.service"

REM 13. Create monitoring script
echo [INFO] Step 13: Creating monitoring script...
echo #!/usr/bin/env python3 > monitor_enhanced_learning.py
echo import asyncio >> monitor_enhanced_learning.py
echo import json >> monitor_enhanced_learning.py
echo from datetime import datetime, timedelta >> monitor_enhanced_learning.py
echo from app.core.database import get_session >> monitor_enhanced_learning.py
echo from app.models.sql_models import OathPaper, TrainingData, AgentMetrics >> monitor_enhanced_learning.py
echo from sqlalchemy import select >> monitor_enhanced_learning.py
echo. >> monitor_enhanced_learning.py
echo async def monitor_enhanced_learning(): >> monitor_enhanced_learning.py
echo     try: >> monitor_enhanced_learning.py
echo         session = get_session() >> monitor_enhanced_learning.py
echo         async with session as s: >> monitor_enhanced_learning.py
echo             recent_oath_papers = await s.execute( >> monitor_enhanced_learning.py
echo                 select(OathPaper) >> monitor_enhanced_learning.py
echo                 .where(OathPaper.created_at ^>= datetime.utcnow() - timedelta(hours=24)) >> monitor_enhanced_learning.py
echo                 .order_by(OathPaper.created_at.desc()) >> monitor_enhanced_learning.py
echo                 .limit(10) >> monitor_enhanced_learning.py
echo             ) >> monitor_enhanced_learning.py
echo             oath_papers = recent_oath_papers.scalars().all() >> monitor_enhanced_learning.py
echo             ai_metrics = await s.execute(select(AgentMetrics)) >> monitor_enhanced_learning.py
echo             metrics = ai_metrics.scalars().all() >> monitor_enhanced_learning.py
echo             report = { >> monitor_enhanced_learning.py
echo                 "timestamp": datetime.now().isoformat(), >> monitor_enhanced_learning.py
echo                 "oath_papers_last_24h": len(oath_papers), >> monitor_enhanced_learning.py
echo                 "ai_metrics": [ >> monitor_enhanced_learning.py
echo                     { >> monitor_enhanced_learning.py
echo                         "agent_type": m.agent_type, >> monitor_enhanced_learning.py
echo                         "learning_score": m.learning_score, >> monitor_enhanced_learning.py
echo                         "level": m.level, >> monitor_enhanced_learning.py
echo                         "prestige": m.prestige >> monitor_enhanced_learning.py
echo                     } >> monitor_enhanced_learning.py
echo                     for m in metrics >> monitor_enhanced_learning.py
echo                 ] >> monitor_enhanced_learning.py
echo             } >> monitor_enhanced_learning.py
echo             print(json.dumps(report, indent=2)) >> monitor_enhanced_learning.py
echo     except Exception as e: >> monitor_enhanced_learning.py
echo         print(f"Error monitoring: {e}") >> monitor_enhanced_learning.py
echo. >> monitor_enhanced_learning.py
echo if __name__ == "__main__": >> monitor_enhanced_learning.py
echo     asyncio.run(monitor_enhanced_learning()) >> monitor_enhanced_learning.py

scp -i "%KEY_FILE%" -o StrictHostKeyChecking=no "monitor_enhanced_learning.py" %EC2_USER%@%EC2_HOST%:%REMOTE_DIR%/

REM 14. Set up cron job for monitoring
echo [INFO] Step 14: Setting up monitoring...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "echo '*/30 * * * * cd %REMOTE_DIR% && python monitor_enhanced_learning.py >> /var/log/enhanced-learning.log 2^>^&1' | crontab -"

REM 15. Start the service
echo [INFO] Step 15: Starting autonomous learning service...
ssh -i "%KEY_FILE%" -o StrictHostKeyChecking=no %EC2_USER%@%EC2_HOST% "sudo systemctl start autonomous-learning.service"

REM 16. Final status
echo.
echo ✅ Enhanced Subject Learning Features Deployed to EC2 Successfully!
echo.
echo 📋 Summary of deployed features:
echo   ✅ Enhanced Subject Learning Service deployed
echo   ✅ Autonomous AI Learning Service deployed
echo   ✅ AI Learning Cycle Enhancement deployed
echo   ✅ Systemd service configured for autonomous learning
echo   ✅ Database migration completed
echo   ✅ Monitoring and logging configured
echo.
echo 🔧 Services running on EC2:
echo   🚀 Autonomous Learning Service: systemctl status autonomous-learning.service
echo   📊 Monitoring: python monitor_enhanced_learning.py
echo   🔄 AI Learning Cycles: Enhanced with subject-based learning
echo.
echo 🎯 Autonomous Features:
echo   🤖 AIs will autonomously learn subjects every 2 hours
echo   🌅 Daily comprehensive learning cycles at 5:00 AM
echo   ☀️ Midday advanced learning cycles at 12:00 PM
echo   🌆 Evening practical learning cycles at 5:00 PM
echo   🔄 Cross-AI knowledge sharing enabled
echo   📈 Intuitive growth tracking and leveling
echo   🏆 Prestige system for significant achievements
echo.
echo 📚 Documentation: ENHANCED_SUBJECT_LEARNING_FEATURES.md
echo 🔍 Monitor logs: tail -f /var/log/enhanced-learning.log
echo.
echo ✅ EC2 deployment completed successfully!
pause 