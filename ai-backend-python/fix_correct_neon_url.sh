#!/bin/bash

echo "🔧 Updating DATABASE_URL with correct Neon hostname..."

# Navigate to backend directory
cd ~/ai-backend-python

# Update DATABASE_URL with the correct Neon hostname
echo "📝 Updating DATABASE_URL..."
sed -i 's|DATABASE_URL=.*|DATABASE_URL="postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"|' .env

# Verify the change
echo "✅ Updated DATABASE_URL:"
grep "DATABASE_URL" .env

# Test DNS resolution for correct hostname
echo "🔍 Testing DNS resolution for correct hostname..."
nslookup ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech

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

echo "✅ Correct Neon URL setup completed!" 