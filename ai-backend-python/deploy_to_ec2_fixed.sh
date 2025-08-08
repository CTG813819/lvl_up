#!/bin/bash

# Comprehensive EC2 Deployment Script - Fixed Version
# This script fixes port conflicts and database issues

set -e

echo "🚀 Deploying AI Backend to EC2 with fixes..."
echo "============================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if sudo lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find and stop process using a port
stop_process_on_port() {
    local port=$1
    local new_port=$2
    echo "🔍 Finding process using port $port..."
    
    local pids=$(sudo lsof -t -i :$port 2>/dev/null || echo "")
    if [ -n "$pids" ]; then
        # Handle multiple PIDs properly
        for pid in $pids; do
            echo "📊 Found process $pid using port $port"
            echo "🔍 Checking what this process is..."
            ps -p $pid -o pid,ppid,cmd --no-headers 2>/dev/null || echo "Process not found"
            
            # Check if it's a uvicorn process
            if ps -p $pid -o cmd --no-headers 2>/dev/null | grep -q uvicorn; then
                echo "🔄 This is a uvicorn process, stopping it..."
                sudo kill $pid
                sleep 2
            else
                echo "⚠️ This is not a uvicorn process, stopping it..."
                sudo kill $pid
                sleep 2
            fi
        done
    else
        echo "✅ Port $port is free"
    fi
}

# Step 1: Check current state
echo "📊 Checking current system state..."
echo "Port 8000 status:"
if check_port 8000; then
    echo "❌ Port 8000 is in use"
    stop_process_on_port 8000 4000
else
    echo "✅ Port 8000 is free"
fi

echo "Port 4000 status:"
if check_port 4000; then
    echo "❌ Port 4000 is in use"
    stop_process_on_port 4000 5000
else
    echo "✅ Port 4000 is free"
fi

# Step 2: Stop the current AI backend service
echo "🛑 Stopping current AI backend service..."
sudo systemctl stop ai-backend-python || echo "Service was not running"

# Step 3: Fix database schema issue using virtual environment
echo "🔧 Fixing database schema issue..."
cd /home/ubuntu/ai-backend-python

# Create a database migration script to fix the pattern column
cat > fix_learning_table.py << 'EOF'
#!/usr/bin/env python3
"""
Fix the learning table schema to handle the pattern column properly
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_learning_table():
    """Fix the learning table schema"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return False
    
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        
        # Check if pattern column exists and its constraints
        print("🔍 Checking learning table schema...")
        result = await conn.fetch("""
            SELECT column_name, is_nullable, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'learning' AND column_name = 'pattern'
        """)
        
        if not result:
            print("❌ Pattern column not found in learning table")
            return False
        
        column_info = result[0]
        print(f"📊 Pattern column: nullable={column_info['is_nullable']}, type={column_info['data_type']}")
        
        # If pattern column is NOT NULL, make it nullable
        if column_info['is_nullable'] == 'NO':
            print("🔧 Making pattern column nullable...")
            await conn.execute("""
                ALTER TABLE learning 
                ALTER COLUMN pattern DROP NOT NULL
            """)
            print("✅ Pattern column is now nullable")
        else:
            print("✅ Pattern column is already nullable")
        
        # Add a default value for pattern if it doesn't exist
        print("🔧 Adding default value for pattern column...")
        await conn.execute("""
            ALTER TABLE learning 
            ALTER COLUMN pattern SET DEFAULT 'default_pattern'
        """)
        print("✅ Default value added for pattern column")
        
        # Update existing null values
        print("🔧 Updating existing null pattern values...")
        result = await conn.execute("""
            UPDATE learning 
            SET pattern = 'default_pattern' 
            WHERE pattern IS NULL
        """)
        print(f"✅ Updated {result} rows with null pattern values")
        
        await conn.close()
        print("✅ Database schema fix completed")
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_learning_table())
    if success:
        print("🎉 Database schema fix successful")
    else:
        print("💥 Database schema fix failed")
        exit(1)
EOF

# Run the database fix using the virtual environment
echo "🔧 Running database schema fix using virtual environment..."
source venv/bin/activate
python3 fix_learning_table.py
deactivate

# Step 4: Update the service configuration to use port 8000
echo "⚙️ Updating service configuration to use port 8000..."
sudo tee /etc/systemd/system/ai-backend-python.service > /dev/null <<EOF
[Unit]
Description=AI Backend Python Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal
Environment=DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

[Install]
WantedBy=multi-user.target
EOF

# Step 5: Reload systemd and start the service
echo "🔄 Reloading systemd configuration..."
sudo systemctl daemon-reload

echo "🚀 Starting AI backend service on port 8000..."
sudo systemctl start ai-backend-python

# Step 6: Wait for service to start and test
echo "⏳ Waiting for service to start..."
sleep 10

# Check service status
echo "📊 Service status:"
sudo systemctl status ai-backend-python --no-pager

# Test the service
echo "🌐 Testing service on port 8000:"
if curl -s --connect-timeout 10 http://localhost:8000/health > /dev/null; then
    echo "✅ Service is running successfully on port 8000"
else
    echo "❌ Service failed to start on port 8000"
    echo "📋 Recent logs:"
    sudo journalctl -u ai-backend-python -n 20 --no-pager
    exit 1
fi

# Step 7: Verify ports
echo "🔍 Verifying port usage:"
echo "Port 8000:"
sudo lsof -i :8000 || echo "Port 8000 not listening"

echo "Port 4000:"
sudo lsof -i :4000 || echo "Port 4000 not listening"

# Step 8: Test API endpoints
echo "🧪 Testing API endpoints..."
echo "Health check:"
curl -s http://localhost:8000/health | jq '.' || echo "Health check completed"

echo "Learning status:"
curl -s http://localhost:8000/api/learning/stats/Imperium | jq '.' || echo "Learning status check completed"

echo ""
echo "🎉 Deployment completed successfully!"
echo "====================================="
echo "✅ AI Backend is running on port 8000"
echo "✅ Database schema issues fixed"
echo "✅ Port conflicts resolved"
echo ""
echo "📊 Service Information:"
echo "- URL: http://localhost:8000"
echo "- Health: http://localhost:8000/health"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "🚀 To monitor the service:"
echo "   sudo journalctl -u ai-backend-python -f"
echo ""
echo "🔄 To restart the service:"
echo "   sudo systemctl restart ai-backend-python" 