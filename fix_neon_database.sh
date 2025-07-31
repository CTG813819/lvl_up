#!/bin/bash

echo "🔧 Fixing Neon database setup..."

# Navigate to backend directory
cd ~/ai-backend-python

# Install asyncpg
echo "📦 Installing asyncpg..."
source venv/bin/activate
pip install asyncpg

# Fix the corrupted DATABASE_URL
echo "🔧 Fixing corrupted DATABASE_URL..."
cat > .env.temp << 'EOF'
DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-1b.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
EOF

# Replace the corrupted line
sed -i '/DATABASE_URL=/d' .env
cat .env.temp >> .env
rm .env.temp

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

echo "✅ Neon database fix completed!" 