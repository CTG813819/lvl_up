# 🚀 Backend Deployment & Fix Guide

## 📋 Current Status

✅ **Files Uploaded to EC2:**
- `ai-backend` directory uploaded to `~/ai-backend`
- `fix_async_generator_direct.py` uploaded to `~/`
- `ec2_backend_fix.sh` uploaded to `~/`

## 🔧 Next Steps on EC2

### Step 1: SSH to EC2 Instance
```bash
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com
```

### Step 2: Navigate to Backend Directory
```bash
cd ~/ai-backend-python
```

### Step 3: Run the Fix Script
```bash
# Option A: Python script (recommended)
python3 ~/fix_async_generator_direct.py

# Option B: Bash script (alternative)
chmod +x ~/ec2_backend_fix.sh
~/ec2_backend_fix.sh
```

## 🔍 What the Fix Script Does

1. **Installs Git** - Resolves `[Errno 2] No such file or directory: 'git'`
2. **Sets up Git Repository** - Initializes git repo for experiments
3. **Creates Repository Config** - Adds configuration for auto-push and issues
4. **Fixes Async Generator** - Resolves `'async_generator' object has no attribute 'close'`
5. **Creates Environment Config** - Sets up proper environment variables
6. **Restarts Backend Service** - Applies all changes

## 📝 Manual Configuration After Fix

### 1. Update Repository URL
```bash
nano repository_config.json
```
Change:
```json
{
  "repository": {
    "url": "https://github.com/CTG813819/Lvl_UP.git",
    "branch": "main",
    "remote": "origin"
  },
  "experiments": {
    "default_repository": "https://github.com/CTG813819/Lvl_UP.git",
    "auto_push": true,
    "create_issues": true
  }
}
```

### 2. Update Environment Configuration
```bash
nano .env.fixed
```
Update with your actual values:
```bash
# Environment configuration for AI Backend
GIT_ENABLED=true
REPOSITORY_URL=https://github.com/CTG813819/Lvl_UP.git
AUTO_PUSH_ENABLED=true
CREATE_ISSUES_ENABLED=true

# Database configuration (update with your actual DB URL)
DATABASE_URL=postgresql://username:password@localhost/dbname

# AI Learning configuration
LEARNING_ENABLED=true
LEARNING_CYCLE_INTERVAL=300
MAX_LEARNING_CYCLES=100

# Experiment configuration
EXPERIMENT_REPOSITORY_URL=https://github.com/CTG813819/Lvl_UP.git
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true
```

### 3. Apply Environment Configuration
```bash
cp .env.fixed .env
```

## 🔍 Verify the Fix

### Check Service Status
```bash
sudo systemctl status ai-backend-python --no-pager
```

### Monitor Logs
```bash
journalctl -u ai-backend-python -f
```

### Check for Errors
Look for these issues to be resolved:
- ❌ `'async_generator' object has no attribute 'close'` → ✅ Should be gone
- ❌ `[Errno 2] No such file or directory: 'git'` → ✅ Should be gone  
- ❌ `No repository URL found for experiment` → ✅ Should be gone

## 🧪 Test the Backend

### Test API Endpoints
```bash
# Test basic connectivity
curl http://localhost:8000/api/imperium/agents

# Test proposals endpoint
curl http://localhost:8000/api/proposals

# Test learning endpoints
curl http://localhost:8000/api/imperium/learning-analytics
```

### Test from Flutter App
1. Open your Flutter app
2. Check if backend connectivity is working
3. Verify that proposals are loading
4. Test the apply functionality

## 🔧 Troubleshooting

### If Git Still Not Found
```bash
sudo apt update
sudo apt install -y git
git config --global user.name "AI Backend"
git config --global user.email "ai-backend@example.com"
```

### If Async Generator Error Persists
```bash
# Check the fixed service file
cat app/services/ai_learning_service_fixed.py

# Restart the service
sudo systemctl restart ai-backend-python
```

### If Service Won't Start
```bash
# Check service logs
journalctl -u ai-backend-python -n 50 --no-pager

# Check if Python dependencies are installed
cd ~/ai-backend-python
pip3 install -r requirements.txt
```

## 📊 Expected Results

After successful deployment:

✅ **Backend Issues Resolved:**
- No more async generator errors
- Git properly installed and configured
- Repository URLs properly configured
- Learning cycles working properly

✅ **App Functionality:**
- Real-time updates working
- Proposals loading correctly
- Apply functionality working
- AI learning cycles running

✅ **Monitoring:**
- Clean logs without errors
- Regular learning cycles
- Successful proposal generation

## 🚨 Emergency Rollback

If something goes wrong:
```bash
# Stop the service
sudo systemctl stop ai-backend-python

# Restore original files
cd ~/ai-backend-python
cp app/services/ai_learning_service.py.backup app/services/ai_learning_service.py

# Restart service
sudo systemctl start ai-backend-python
```

## 📞 Support

If you encounter issues:
1. Check the logs: `journalctl -u ai-backend-python -f`
2. Verify service status: `sudo systemctl status ai-backend-python`
3. Test API endpoints: `curl http://localhost:8000/api/imperium/agents`

The fix should resolve all the backend issues identified in the logs and get your AI learning system working properly! 