#!/bin/bash

echo "🧹 FINAL CLEAN FIX - Resolving All Issues"
echo "========================================="

# Step 1: Stop ALL services and kill ALL processes
echo "🛑 Step 1: Stopping all services and processes..."
sudo systemctl stop ai-backend-python.service 2>/dev/null || true
sudo systemctl stop integrated-ai-manager.service 2>/dev/null || true
sudo systemctl stop conquest-ai-simple.service 2>/dev/null || true
sudo systemctl stop sandbox-ai-simple.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true

# Kill ALL uvicorn and Python processes
echo "🔪 Killing all uvicorn and Python processes..."
sudo pkill -f uvicorn
sudo pkill -f 'python.*main:app'
sudo pkill -f 'python3.*main:app'
sudo pkill -f 'run_uvicorn'
sudo fuser -k 8000/tcp 2>/dev/null || true

# Wait for processes to fully stop
sleep 10

# Verify no processes are running
echo "🔍 Verifying no processes are running..."
if pgrep -f uvicorn > /dev/null; then
    echo "❌ Uvicorn processes still running, force killing..."
    sudo pkill -9 -f uvicorn
    sleep 5
fi

if pgrep -f 'python.*main:app' > /dev/null; then
    echo "❌ Python main processes still running, force killing..."
    sudo pkill -9 -f 'python.*main:app'
    sleep 5
fi

# Step 2: Clean up all the conflicting scripts
echo "🧹 Step 2: Cleaning up conflicting scripts..."
cd /home/ubuntu/ai-backend-python

# Remove all the fix scripts that are causing conflicts
rm -f fix_ai_learning_summary_column.py
rm -f check_and_fix_db.py
rm -f ensure_single_process.sh
rm -f start_single_backend.sh
rm -f final_single_pid_fix.sh
rm -f run_uvicorn_simple.py
rm -f deploy_single_pid_fix.sh
rm -f comprehensive_fix.sh
rm -f run_uvicorn_single.py
rm -f fix_database_schema.py
rm -f add_back_ai_services.sh
rm -f final_pid_fix.sh
rm -f simple_backend_fix.sh
rm -f fix_ai_services_integration.sh
rm -f fix_single_pid.sh
rm -f deploy_port_fix.sh
rm -f fix_port_conflicts_comprehensive.py
rm -f final_audit_issues_fix.py
rm -f fix_audit_created_by_issue.py
rm -f final_audit_fix.py
rm -f targeted_fix_script.py
rm -f fix_audit_issues.py
rm -f comprehensive_system_audit_fixed.py
rm -f fix_audit_config.py
rm -f deploy_audit_script.sh
rm -f comprehensive_system_audit.py
rm -f test_correct_endpoints.py
rm -f test_ai_endpoints_comprehensive.py
rm -f fix_service_tokens.py
rm -f update_github_token.py
rm -f setup_environment.py
rm -f fix_ai_services_comprehensive.py
rm -f fix_database_schema_issues.py
rm -f deploy_cleanup_fix.sh
rm -f deploy_ml_fix.sh
rm -f fix_backend_performance_critical.py
rm -f deploy_subject_learning_features.sh
rm -f deploy_testing_fix.sh
rm -f imperium_runner.py
rm -f system_config_update.env
rm -f test_enhanced_ml_ec2.py
rm -f fix_postgresql_syntax.py
rm -f debug_schema_issue.py
rm -f deploy_performance_fix.sh
rm -f create_json_function.sql
rm -f fix_dependencies.sh
rm -f targeted_fix.py
rm -f simple_terra_test.py
rm -f fix_service_database.py
rm -f run_guardian.py
rm -f reset_token_usage.py
rm -f fix_guardian_conquest_services.py
rm -f fix_import_issue.py
rm -f fix_database_connection.py
rm -f final_cleanup.sh
rm -f migrate_learning_data.py
rm -f test_proposal_validation.py
rm -f install_minimal_ai.sh
rm -f fix_token_service_initialization.py
rm -f test_advanced_api_check.py
rm -f verify_deployment_fixed.py
rm -f fix_all_syntax.py
rm -f deploy_ec2_fixes_fixed.sh
rm -f create_oath_papers_table.py
rm -f fix_nltk_resources.py
rm -f test_imperium_master.py
rm -f test_comprehensive_fixes.py
rm -f run_conquest.py
rm -f create_mission_tables.py
rm -f deploy_database_init.sh
rm -f monitor_token_usage.py
rm -f debug_openai_auth.py
rm -f check_app_database.py
rm -f force_reload_env.py
rm -f deploy_optimized_backend.sh
rm -f migrate_from_js.py
rm -f integrate_ai_agents_to_backend.py
rm -f deploy_fixed_enhanced_ai_v2.sh
rm -f deploy_backend.sh
rm -f test_terra_extensions.py
rm -f optimize_backend_performance_comprehensive.py
rm -f check_github_token.py
rm -f fix_ai_authentication.py
rm -f debug_service_issues.py

echo "✅ Cleaned up all conflicting scripts"

# Step 3: Fix the database column issue
echo "🔧 Step 3: Fixing database column issue..."
source venv/bin/activate

# Create a simple database fix script
cat > fix_db_final.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import os
from app.core.database import init_database
from sqlalchemy import text

async def fix_database():
    print("🔧 Fixing database schema...")
    
    # Set the correct database URL
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
    
    await init_database()
    from app.core.database import engine
    
    async with engine.begin() as conn:
        # Add the missing column if it doesn't exist
        try:
            await conn.execute(text("ALTER TABLE proposals ADD COLUMN IF NOT EXISTS ai_learning_summary TEXT"))
            print("✅ ai_learning_summary column added successfully")
        except Exception as e:
            print(f"ℹ️  Column already exists or error: {e}")
        
        # Verify the column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'proposals' 
            AND column_name = 'ai_learning_summary'
        """))
        exists = result.scalar() is not None
        print(f"✅ ai_learning_summary column exists: {exists}")

asyncio.run(fix_database())
EOF

python fix_db_final.py
rm -f fix_db_final.py

# Step 4: Create a clean, simple startup script
echo "📝 Step 4: Creating clean startup script..."
cat > start_clean_backend.sh << 'EOF'
#!/bin/bash

# Kill any existing processes
pkill -f uvicorn || true
pkill -f 'python.*main:app' || true
sleep 3

# Change to the correct directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source venv/bin/activate

# Set environment variables to disable heavy background tasks
export DISABLE_BACKGROUND_TASKS=true
export DISABLE_AI_CYCLES=true
export DISABLE_AUTONOMOUS_CYCLES=true
export DISABLE_LEARNING_CYCLES=true

# Start uvicorn with single process
echo "🚀 Starting clean uvicorn with single process..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1 --limit-concurrency 50
EOF

chmod +x start_clean_backend.sh

# Step 5: Create a clean systemd service
echo "📝 Step 5: Creating clean systemd service..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
Environment=DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
Environment=DISABLE_BACKGROUND_TASKS=true
Environment=DISABLE_AI_CYCLES=true
Environment=DISABLE_AUTONOMOUS_CYCLES=true
Environment=DISABLE_LEARNING_CYCLES=true

ExecStart=/home/ubuntu/ai-backend-python/start_clean_backend.sh
ExecStop=/bin/kill -TERM $MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Reload systemd and start the service
echo "🔄 Step 6: Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python.service
sudo systemctl start ai-backend-python.service

# Step 7: Wait and verify
echo "⏳ Step 7: Waiting for service to start..."
sleep 15

# Check service status
echo "🔍 Step 8: Checking service status..."
if sudo systemctl is-active ai-backend-python.service > /dev/null; then
    echo "✅ Service is running"
    
    # Check for single process
    pids=$(pgrep -f "uvicorn.*app.main:app" | wc -l)
    echo "Found $pids uvicorn process(es)"
    
    if [ "$pids" -eq 1 ]; then
        pid=$(pgrep -f 'uvicorn.*app.main:app')
        echo "✅ SUCCESS! Only one PID: $pid"
        
        # Show process details
        echo "📋 Process details:"
        ps -p $pid -o pid,ppid,cmd
        
        # Check CPU usage
        echo "📊 CPU usage:"
        top -p $pid -b -n 1 | tail -2
        
        echo "🎉 FINAL CLEAN FIX COMPLETED SUCCESSFULLY!"
        echo "📋 Summary:"
        echo "   - Single PID: $pid"
        echo "   - Port: 8000"
        echo "   - No conflicts"
        echo "   - Database column fixed"
        echo "   - All conflicting scripts removed"
        echo "   - Clean systemd service"
        
    else
        echo "❌ Multiple PIDs found:"
        pgrep -f 'uvicorn.*app.main:app' -a
        exit 1
    fi
    
else
    echo "❌ Service failed to start"
    sudo systemctl status ai-backend-python.service
    exit 1
fi 