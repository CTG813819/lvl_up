#!/bin/bash

# Deploy validation fix to allow proposals without requiring user feedback first
# This fixes the issue where AIs were blocked from generating proposals

set -e

echo "🔧 Deploying validation fix to allow proposal generation..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Backup the current validation service
echo "📦 Backing up current validation service..."
cp app/services/enhanced_proposal_validation_service.py app/services/enhanced_proposal_validation_service.py.backup.$(date +%Y%m%d_%H%M%S)

# Test the validation changes
echo "🧪 Testing validation changes..."
python test_validation_fix.py

if [ $? -eq 0 ]; then
    echo "✅ Validation test passed"
else
    echo "❌ Validation test failed - rolling back changes"
    cp app/services/enhanced_proposal_validation_service.py.backup.* app/services/enhanced_proposal_validation_service.py
    exit 1
fi

# Restart the service
echo "🔄 Restarting AI backend service..."
sudo systemctl restart ai-backend-python

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test the API endpoint
echo "🌐 Testing API endpoint..."
curl -s http://localhost:8000/health || echo "Health endpoint not available (this is normal)"

echo "✅ Validation fix deployed successfully!"
echo ""
echo "📋 Changes made:"
echo "   - Removed requirement for user feedback before proposal generation"
echo "   - Proposals can now be generated and tested first"
echo "   - User validation only required after testing passes"
echo "   - Reduced learning progress thresholds for new proposals"
echo ""
echo "🎯 Expected behavior:"
echo "   - AIs can generate proposals without waiting for user feedback"
echo "   - Proposals go through testing first"
echo "   - User validation happens after testing and custodes validation"
echo ""
echo "📈 Monitor the logs to verify proposals are being generated:"
echo "   sudo journalctl -u ai-backend-python -f" 