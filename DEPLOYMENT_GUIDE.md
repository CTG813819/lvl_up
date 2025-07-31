# EC2 Deployment Guide

This guide will help you deploy the fixed files to your EC2 instance to resolve the import error and get the custody tests working.

## Quick Deployment

### Option 1: Use the Batch Script (Windows)
```bash
# Run the deployment script
deploy_to_ec2.bat
```

### Option 2: Manual Deployment

If the batch script doesn't work, you can run these commands manually:

#### 1. Transfer the Fixed Files
```bash
# Transfer main.py (fixed import)
scp -i "C:\projects\lvl_up\New.pem" "app/main.py" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/main.py"

# Transfer custody_protocol_service.py (fixed database initialization)
scp -i "C:\projects\lvl_up\New.pem" "app/services/custody_protocol_service.py" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/app/services/custody_protocol_service.py"

# Transfer create_tables.py (database setup)
scp -i "C:\projects\lvl_up\New.pem" "create_tables.py" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/create_tables.py"
```

#### 2. Setup Database on EC2
```bash
# SSH into EC2 and run database setup
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "cd /home/ubuntu/ai-backend-python && python3 create_tables.py"
```

#### 3. Restart the Backend Service
```bash
# Restart the service
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "sudo systemctl restart ultimate_start"

# Check service status
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "sudo systemctl status ultimate_start"
```

#### 4. Monitor the Logs
```bash
# Watch the logs in real-time
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "sudo journalctl -u ultimate_start -f"
```

## What Was Fixed

### 1. Import Error in main.py
- **Problem**: `ModuleNotFoundError: No module named 'app.routers.optimized_router'`
- **Solution**: Changed import from `optimized_router` to `optimized_services`

### 2. Database Initialization in Custody Service
- **Problem**: `Database not initialized. Call init_database() first.`
- **Solution**: Added database initialization to custody service startup

### 3. Missing Database Tables
- **Problem**: `internet_knowledge` table doesn't exist
- **Solution**: Created `create_tables.py` script to set up all required tables

### 4. Method Name Issues
- **Problem**: `'AILearningService' object has no attribute 'get_learning_log'`
- **Solution**: Fixed method calls to use correct method names

## Expected Results

After deployment, you should see:

1. ✅ **Backend starts successfully** - No more import errors
2. ✅ **Database connects properly** - PostgreSQL connection established
3. ✅ **Custody tests activate** - Background service runs custody testing cycle
4. ✅ **Olympic tests activate** - Background service runs olympic testing cycle
5. ✅ **Collaborative tests activate** - Background service runs collaborative testing cycle

## Verification Commands

### Check if Backend is Running
```bash
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "sudo systemctl status ultimate_start"
```

### Check Recent Logs
```bash
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "sudo journalctl -u ultimate_start --since '5 minutes ago'"
```

### Test Custody Service
```bash
ssh -i "C:\projects\lvl_up\New.pem" "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com" "cd /home/ubuntu/ai-backend-python && python3 test_custody_service.py"
```

## Troubleshooting

### If Service Still Fails to Start
1. Check the logs: `sudo journalctl -u ultimate_start -f`
2. Verify database connection: `python3 -c "from app.core.database import init_database; import asyncio; asyncio.run(init_database())"`
3. Check file permissions: `ls -la /home/ubuntu/ai-backend-python/app/main.py`

### If Tests Are Not Running
1. Check background service logs: `sudo journalctl -u ultimate_start | grep "custody\|olympic\|collaborative"`
2. Verify database tables exist: `python3 -c "from app.core.database import get_db; print('Database tables exist')"`

## Files Modified

1. **app/main.py** - Fixed import error
2. **app/services/custody_protocol_service.py** - Added database initialization
3. **create_tables.py** - Database setup script
4. **test_custody_service.py** - Test script for verification 