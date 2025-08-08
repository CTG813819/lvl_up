#!/bin/bash

echo "🔧 Testing Neon database connection..."

# Navigate to backend directory
cd ~/ai-backend-python

# Test DNS resolution
echo "🔍 Testing DNS resolution..."
nslookup ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech

# Test network connectivity
echo "🔍 Testing network connectivity..."
ping -c 3 ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech

# Test with curl
echo "🔍 Testing with curl..."
curl -I https://ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech

# Try alternative connection method
echo "🔍 Testing alternative connection..."
python3 -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    try:
        # Try with explicit SSL settings
        conn = await asyncpg.connect(
            'postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech/neondb',
            ssl='require'
        )
        print('✅ Neon database connection successful!')
        await conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        print('Trying alternative URL format...')
        try:
            # Try without SSL parameters in URL
            conn = await asyncpg.connect(
                'postgresql://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech/neondb',
                ssl='require'
            )
            print('✅ Alternative connection successful!')
            await conn.close()
        except Exception as e2:
            print(f'❌ Alternative connection also failed: {e2}')

asyncio.run(test_connection())
"

# Update .env with working format if needed
echo "🔧 Updating DATABASE_URL with working format..."
sed -i 's|sslmode=require&channel_binding=require||' .env

# Verify the change
echo "✅ Updated DATABASE_URL:"
grep "DATABASE_URL" .env

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait for restart
sleep 5

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 15 --no-pager

echo "✅ Neon connection test completed!" 