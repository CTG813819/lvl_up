#!/bin/bash

echo "🔧 Fixing Neon database URL format..."

# Navigate to backend directory
cd ~/ai-backend-python

# Fix the DATABASE_URL format for asyncpg
echo "🔧 Updating DATABASE_URL format..."
sed -i 's|postgresql+asyncpg://|postgresql://|' .env

# Verify the fix
echo "✅ Fixed DATABASE_URL:"
grep "DATABASE_URL" .env

# Test database connection
echo "🔍 Testing Neon database connection..."
python3 -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        print('✅ Neon database connection successful!')
        await conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')

asyncio.run(test_connection())
"

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait for restart
sleep 5

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 15 --no-pager

echo "✅ Neon database URL fix completed!" 