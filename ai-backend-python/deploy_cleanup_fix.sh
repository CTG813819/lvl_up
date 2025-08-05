#!/bin/bash

echo "Deploying cleanup fix to EC2 instance..."

# Stop the service
echo "Stopping ai-backend-python service..."
sudo systemctl stop ai-backend-python

# Apply the fix to the proposals.py file
echo "Applying cleanup fix..."
sudo sed -i 's/proposal.user_feedback = "Automatically expired due to age"/proposal.user_feedback = "expired"/g' /home/ubuntu/ai-backend-python/app/routers/proposals.py

# Verify the fix was applied
echo "Verifying fix..."
if grep -q 'proposal.user_feedback = "expired"' /home/ubuntu/ai-backend-python/app/routers/proposals.py; then
    echo "✅ Fix applied successfully"
else
    echo "❌ Fix not found - manual intervention required"
    exit 1
fi

# Start the service
echo "Starting ai-backend-python service..."
sudo systemctl start ai-backend-python

# Check service status
echo "Checking service status..."
sudo systemctl status ai-backend-python --no-pager

echo "Deployment complete! The service should now handle cleanup without the string length error." 