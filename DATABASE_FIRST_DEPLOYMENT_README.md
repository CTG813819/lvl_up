# Database-First Migration Deployment Guide

## 🚀 Quick Start

### Prerequisites
- EC2 instance running Ubuntu
- Python virtual environment activated
- All files transferred to `/home/ubuntu/ai-backend-python/`

### Step 1: Navigate to the Project Directory
```bash
cd /home/ubuntu/ai-backend-python/
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 3: Make the Deployment Script Executable
```bash
chmod +x deploy_database_first.sh
```

### Step 4: Run the Complete Deployment
```bash
./deploy_database_first.sh
```

## 📋 What the Deployment Script Does

1. **Installs Dependencies** - Updates all Python packages
2. **Runs Migration** - Migrates existing data to database-first approach
3. **Executes Refactoring** - Runs complete backend refactoring
4. **Tests API Endpoints** - Verifies new endpoints are working
5. **Generates Reports** - Creates migration documentation
6. **Validates Files** - Checks all required files are present

## 🔧 Manual Steps (if needed)

### Run Migration Only
```bash
python migrate_all_metrics_to_db.py
```

### Run Complete Refactoring Only
```bash
python refactor_to_database_first.py
```

### Test the Backend
```bash
python main.py
```

## 🌐 New API Endpoints

After deployment, these new endpoints will be available:

- `GET /api/agent-metrics/` - Overview of all agents
- `GET /api/agent-metrics/{agent_type}` - Specific agent metrics
- `GET /api/agent-metrics/{agent_type}/custody` - Custody metrics
- `PUT /api/agent-metrics/{agent_type}` - Update agent metrics
- `POST /api/agent-metrics/{agent_type}/custody-test` - Record test result
- `POST /api/agent-metrics/bulk-update` - Bulk update metrics
- `DELETE /api/agent-metrics/{agent_type}/reset` - Reset agent metrics
- `GET /api/agent-metrics/analytics/summary` - Analytics summary

## 📊 Database Changes

- **Before**: In-memory storage for agent metrics
- **After**: NeonDB as single source of truth
- **Benefits**: 
  - Persistent data storage
  - Real-time updates
  - Transaction safety
  - Better performance with connection pooling

## 🔍 Troubleshooting

### If Migration Fails
1. Check database connection in `.env` file
2. Ensure all dependencies are installed
3. Verify virtual environment is activated

### If API Endpoints Don't Work
1. Check if main.py includes the agent_metrics router
2. Verify the backend server is running
3. Check logs for any errors

### If Files Are Missing
1. Re-transfer files using SCP
2. Check file permissions
3. Verify file paths are correct

## 📚 Documentation

- `DATABASE_FIRST_MIGRATION_GUIDE.md` - Complete technical guide
- `migration_report_*.json` - Detailed migration results
- `deploy_database_first.sh` - Deployment script with comments

## 🎯 Success Indicators

✅ All files transferred successfully  
✅ Migration script runs without errors  
✅ Refactoring completes successfully  
✅ API endpoints respond correctly  
✅ Database contains all agent metrics  
✅ No in-memory storage dependencies  

## 🚀 Next Steps

1. **Start the Backend**: `python main.py`
2. **Test Frontend Integration**: Update frontend to use new endpoints
3. **Monitor Performance**: Watch for any performance issues
4. **Update Documentation**: Document any frontend changes needed

---

**Note**: This migration is irreversible. All agent metrics are now stored in the database as the single source of truth. 