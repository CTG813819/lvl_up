#!/bin/bash

# Deploy testing service fix for NoneType error
echo "🔧 Deploying testing service fix for NoneType error..."

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

# Apply the fix to both main and guardian deployment
echo "🔧 Applying testing service fix..."

# Fix main testing service
sed -i 's/ai_type = proposal_data.get('\''ai_type'\'', '\'''\'').lower()/ai_type = (proposal_data.get('\''ai_type'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/app/services/testing_service.py
sed -i 's/improvement_type = proposal_data.get('\''improvement_type'\'', '\'''\'').lower()/improvement_type = (proposal_data.get('\''improvement_type'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/app/services/testing_service.py
sed -i 's/file_path = proposal_data.get('\''file_path'\'', '\'''\'').lower()/file_path = (proposal_data.get('\''file_path'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/app/services/testing_service.py

# Fix guardian deployment testing service
sed -i 's/ai_type = proposal_data.get('\''ai_type'\'', '\'''\'').lower()/ai_type = (proposal_data.get('\''ai_type'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/services/testing_service.py
sed -i 's/improvement_type = proposal_data.get('\''improvement_type'\'', '\'''\'').lower()/improvement_type = (proposal_data.get('\''improvement_type'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/services/testing_service.py
sed -i 's/file_path = proposal_data.get('\''file_path'\'', '\'''\'').lower()/file_path = (proposal_data.get('\''file_path'\'') or '\'''\'').lower()/g' /home/ubuntu/ai-backend-python/guardian_deployment_20250607_175440/app/services/testing_service.py

echo "✅ Testing service fix applied"

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

echo "🎉 Testing service fix deployed successfully!"
echo "📝 The NoneType error in live testing should now be resolved."
echo "📊 Monitor the logs to verify the fix is working:"
echo "   sudo journalctl -u uvicorn -f" 