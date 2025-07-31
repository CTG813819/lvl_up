# EC2 Database Column Fix Instructions

## Issue Description
The EC2 instance is experiencing database errors because the `ai_learning_summary` column is missing from the `proposals` table. The application code expects this column to exist, but it wasn't created during the initial database setup.

## Error Details
```
ProgrammingError: column proposals.ai_learning_summary does not exist
```

## Solution Steps

### Step 1: Connect to EC2 Instance
```bash
scp -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/
```

### Step 2: Navigate to the Project Directory
```bash
cd /home/ubuntu/ai-backend-python
```

### Step 3: Activate the Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Run the Database Fix Script
```bash
python fix_ai_learning_summary_column.py
```

### Step 5: Verify the Fix
```bash
python check_and_fix_db.py
```

### Step 6: Restart the Application
```bash
# Stop the current process
sudo systemctl stop your-app-service

# Or if running manually, stop the uvicorn process
pkill -f uvicorn

# Start the application again
sudo systemctl start your-app-service

# Or if running manually
uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1
```

## Alternative Solutions

### Option 1: Use the Comprehensive Migration Script
If the simple fix doesn't work, run the full migration:
```bash
python add_ai_learning_summary_migration.py
```

### Option 2: Manual Database Fix
Connect to the database directly and run:
```sql
ALTER TABLE proposals ADD COLUMN ai_learning_summary TEXT;
```

### Option 3: Check Database Schema
To see all current columns in the proposals table:
```bash
python check_db_schema.py
```

## Verification Steps

1. **Check Application Logs**: Monitor the application logs to ensure no more column errors
2. **Test API Endpoints**: Verify that proposal-related endpoints work correctly
3. **Database Query**: Confirm the column exists by querying the database

## Prevention
To prevent this issue in the future:
1. Always run database migrations before deploying new code
2. Use Alembic migrations for schema changes
3. Test database schema compatibility in staging environments

## Troubleshooting

### If the script fails:
1. Check database connection settings
2. Verify database permissions
3. Check if the proposals table exists
4. Review application logs for additional errors

### If the application still fails:
1. Check if there are other missing columns
2. Verify the database URL configuration
3. Ensure all required tables exist
4. Check for any pending migrations

## Files Created/Modified
- `fix_ai_learning_summary_column.py` - Quick fix script
- `EC2_DATABASE_FIX_INSTRUCTIONS.md` - This instruction file

## Expected Outcome
After running the fix script, the application should:
- No longer show `ai_learning_summary` column errors
- Successfully query the proposals table
- Resume normal operation without database-related crashes 