#!/bin/bash

# Database Initialization Deployment Script
# This script should be run once to set up the database tables

set -e

echo "🚀 Starting Database Initialization on EC2"

# Navigate to project directory
cd /home/ubuntu/ai-backend-python

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:/home/ubuntu/ai-backend-python"

# Run database initialization
echo "🗄️ Initializing database tables..."
python3 create_tables.py

# Verify tables were created
echo "🔍 Verifying database tables..."
python3 scripts/create_token_usage_tables.py --verify

echo "✅ Database initialization completed successfully!"
echo "📋 All tables including token_usage tables are now ready"

# Show table status
echo "📊 Database table status:"
python3 -c "
import asyncio
import sys
sys.path.append('/home/ubuntu/ai-backend-python')
from app.core.database import init_database
from sqlalchemy import text

async def check_tables():
    await init_database()
    from app.core.database import engine
    async with engine.begin() as conn:
        result = await conn.execute(text(\"\"\"
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('token_usage', 'token_usage_logs', 'proposals', 'learning', 'oath_papers')
            ORDER BY table_name
        \"\"\"))
        tables = result.fetchall()
        for table in tables:
            print(f'✅ {table[0]} table exists')

asyncio.run(check_tables())
"

echo "🎉 Database initialization deployment completed!" 