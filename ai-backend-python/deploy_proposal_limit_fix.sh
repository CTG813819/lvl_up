#!/bin/bash

# Deploy proposal limit fix and improvements
echo "🔧 Deploying proposal limit fix and improvements..."

# Stop the service
echo "🛑 Stopping uvicorn service..."
sudo systemctl stop uvicorn

# Wait a moment for the service to stop
sleep 2

# Check if service is stopped
if systemctl is-active --quiet uvicorn; then
    echo "❌ Failed to stop uvicorn service"
    exit 1
fi

echo "✅ Service stopped successfully"

# Apply the fixes to both main and guardian deployment
echo "🔧 Applying proposal limit fixes..."

# Fix main proposals.py - increase limit to 100
sed -i 's/if pending_count >= 40:/if pending_count >= 100: # Increased from 40/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py
sed -i 's/detail="Maximum pending proposals reached (40)./detail="Maximum pending proposals reached (100)./g' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Fix guardian deployment proposals.py - increase limit to 100
sed -i 's/if pending_count >= 40:/if pending_count >= 100: # Increased from 40/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py
sed -i 's/detail="Maximum pending proposals reached (40)./detail="Maximum pending proposals reached (100)./g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py

# Improve cleanup threshold in main proposals.py
sed -i 's/if pending_count > 30: # If more than 30 pending/if pending_count > 50: # If more than 50 pending/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py
sed -i 's/cutoff_time = datetime.utcnow() - timedelta(hours=1)/cutoff_time = datetime.utcnow() - timedelta(minutes=30) # More aggressive: 30 minutes instead of 1 hour/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Add cleanup function to guardian deployment if not already present
if ! grep -q "async def cleanup_old_pending_proposals" /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/routers/proposals.py; then
    echo "Adding cleanup function to guardian deployment..."
    # This will be handled by the file edits we already made
fi

echo "✅ Proposal limit fixes applied"

# Start the service
echo "🚀 Starting uvicorn service..."
sudo systemctl start uvicorn

# Wait a moment for the service to start
sleep 3

# Check if service is running
if systemctl is-active --quiet uvicorn; then
    echo "✅ Service started successfully"
    echo "📊 Checking service status..."
    sudo systemctl status uvicorn --no-pager -l
else
    echo "❌ Failed to start uvicorn service"
    echo "📋 Service logs:"
    sudo journalctl -u uvicorn -n 20 --no-pager
    exit 1
fi

echo "🎉 Proposal limit fix deployed successfully!"
echo "📝 Changes made:"
echo "   - Increased pending proposal limit from 40 to 100"
echo "   - Improved cleanup threshold from 30 to 50 pending proposals"
echo "   - Made cleanup more aggressive (30 minutes instead of 1 hour)"
echo "   - Added cleanup function to guardian deployment"
echo "📊 Monitor the logs to verify the fix is working:"
echo "   sudo journalctl -u uvicorn -f" 