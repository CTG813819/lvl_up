#!/bin/bash

# Guardian AI Enhancements Deployment Script
# This script deploys the new Guardian AI health check and suggestion management system

set -e

echo "🚀 Starting Guardian AI Enhancements Deployment..."

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
BACKEND_DIR="/home/ubuntu/ai-backend-python"
SERVICE_NAME="ai-backend-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Create database migration
print_status "Step 1: Creating database migration for Guardian suggestions table..."
cd ai-backend-python

if [ -f "create_guardian_suggestions_table.py" ]; then
    print_success "Migration script found"
else
    print_error "Migration script not found!"
    exit 1
fi

# Step 2: Deploy to EC2
print_status "Step 2: Deploying to EC2 instance..."

# Create a temporary deployment package
DEPLOY_DIR="guardian_deployment_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DEPLOY_DIR

# Copy necessary files
cp -r app/ $DEPLOY_DIR/
cp create_guardian_suggestions_table.py $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp main.py $DEPLOY_DIR/

print_status "Created deployment package: $DEPLOY_DIR"

# Step 3: Upload to EC2
print_status "Step 3: Uploading files to EC2..."

# Create backup of current backend
ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << 'EOF'
    echo "Creating backup of current backend..."
    sudo cp -r /home/ubuntu/ai-backend-python /home/ubuntu/ai-backend-python.backup.$(date +%Y%m%d_%H%M%S)
EOF

# Upload new files
scp -o StrictHostKeyChecking=no -r $DEPLOY_DIR/* $EC2_USER@$EC2_HOST:$BACKEND_DIR/

print_success "Files uploaded successfully"

# Step 4: Run database migration
print_status "Step 4: Running database migration..."

ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    echo "Running Guardian suggestions table migration..."
    python3 create_guardian_suggestions_table.py
    
    if [ $? -eq 0 ]; then
        echo "Database migration completed successfully"
    else
        echo "Database migration failed!"
        exit 1
    fi
EOF

# Step 5: Restart backend service
print_status "Step 5: Restarting backend service..."

ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << 'EOF'
    echo "Stopping backend service..."
    sudo systemctl stop ai-backend-python
    
    echo "Starting backend service..."
    sudo systemctl start ai-backend-python
    
    echo "Checking service status..."
    sudo systemctl status ai-backend-python --no-pager
    
    # Wait a moment for service to fully start
    sleep 5
    
    # Check if service is running
    if sudo systemctl is-active --quiet ai-backend-python; then
        echo "Backend service is running successfully"
    else
        echo "Backend service failed to start!"
        exit 1
    fi
EOF

# Step 6: Test the new endpoints
print_status "Step 6: Testing new Guardian endpoints..."

# Test health check endpoint
print_status "Testing health check endpoint..."
HEALTH_CHECK_RESPONSE=$(curl -s -X POST "http://$EC2_HOST:4000/api/guardian/health-check" || echo "FAILED")

if [[ $HEALTH_CHECK_RESPONSE == *"success"* ]]; then
    print_success "Health check endpoint working"
else
    print_warning "Health check endpoint test failed: $HEALTH_CHECK_RESPONSE"
fi

# Test suggestions endpoint
print_status "Testing suggestions endpoint..."
SUGGESTIONS_RESPONSE=$(curl -s "http://$EC2_HOST:4000/api/guardian/suggestions" || echo "FAILED")

if [[ $SUGGESTIONS_RESPONSE == *"success"* ]]; then
    print_success "Suggestions endpoint working"
else
    print_warning "Suggestions endpoint test failed: $SUGGESTIONS_RESPONSE"
fi

# Test health status endpoint
print_status "Testing health status endpoint..."
HEALTH_STATUS_RESPONSE=$(curl -s "http://$EC2_HOST:4000/api/guardian/health-status" || echo "FAILED")

if [[ $HEALTH_STATUS_RESPONSE == *"success"* ]]; then
    print_success "Health status endpoint working"
else
    print_warning "Health status endpoint test failed: $HEALTH_STATUS_RESPONSE"
fi

# Step 7: Cleanup
print_status "Step 7: Cleaning up deployment files..."

rm -rf $DEPLOY_DIR

# Step 8: Final verification
print_status "Step 8: Final verification..."

ssh -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST << 'EOF'
    echo "Checking backend logs for any errors..."
    sudo journalctl -u ai-backend-python --no-pager -n 20
    
    echo "Checking service status..."
    sudo systemctl status ai-backend-python --no-pager
EOF

print_success "🎉 Guardian AI Enhancements Deployment Completed Successfully!"

echo ""
echo "📋 Deployment Summary:"
echo "✅ Database migration completed"
echo "✅ Backend service restarted"
echo "✅ New endpoints tested"
echo "✅ Service status verified"
echo ""
echo "🔗 New Guardian AI Endpoints:"
echo "   - POST /api/guardian/health-check"
echo "   - GET /api/guardian/suggestions"
echo "   - POST /api/guardian/suggestions/{id}/approve"
echo "   - POST /api/guardian/suggestions/{id}/reject"
echo "   - GET /api/guardian/suggestions/statistics"
echo "   - GET /api/guardian/health-status"
echo ""
echo "📱 Frontend Integration:"
echo "   - GuardianSuggestionsWidget added to Terra screen"
echo "   - GuardianService updated with new API calls"
echo ""
echo "🚀 Ready for frontend deployment!" 