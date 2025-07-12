#!/bin/bash

# Deployment script to clean up pending proposals and restart the service
# Run this on the EC2 instance

echo "Starting cleanup and deployment process..."

# Navigate to the project directory
cd /home/ubuntu/ai-backend-python

# Stop the current service
echo "Stopping current service..."
sudo systemctl stop ai-backend-python

# Run the direct cleanup script to remove all pending proposals
echo "Cleaning up pending proposals backlog using direct SQL..."
python scripts/direct_db_cleanup.py

# Wait a moment for cleanup to complete
sleep 5

# Verify cleanup worked
echo "Verifying cleanup..."
python -c "
import asyncio
import sys
sys.path.append('.')
from app.core.database import init_database
from sqlalchemy import text
import app.core.database as database_module

async def verify():
    await init_database()
    async with database_module.SessionLocal() as db:
        count_sql = text('SELECT COUNT(*) FROM proposals WHERE status = \\'pending\\'')
        result = await db.execute(count_sql)
        count = result.scalar()
        print(f'Remaining pending proposals: {count}')
        if count > 0:
            print('WARNING: Cleanup may not have worked completely!')
        else:
            print('SUCCESS: All pending proposals cleaned up!')

asyncio.run(verify())
"

# Start the service again
echo "Starting service with new configuration..."
sudo systemctl start ai-backend-python

# Check service status
echo "Checking service status..."
sudo systemctl status ai-backend-python

# Show recent logs
echo "Recent logs:"
sudo journalctl -u ai-backend-python -n 20 --no-pager

echo "Deployment complete! The service should now be running with:"
echo "- Cleaned up pending proposals backlog"
echo "- Increased limit to 40 pending proposals"
echo "- Automatic cleanup mechanism to prevent future backlogs" 