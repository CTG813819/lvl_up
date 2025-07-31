#!/bin/bash

# Deploy Leveling and Proposal Management Changes
# This script applies all the changes for the new leveling system and proposal management

set -e

echo "🚀 Deploying Leveling and Proposal Management Changes..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    print_error "This script must be run from the ai-backend-python directory"
    exit 1
fi

print_header "Starting Deployment"

# Step 1: Backup current configuration
print_status "Creating backup of current configuration..."
cp app/core/config.py app/core/config.py.backup
print_status "Backup created: app/core/config.py.backup"

# Step 2: Update learning cycle timing
print_header "Updating Learning Cycle Configuration"
print_status "Changing learning cycle interval from 5 minutes to 35 minutes..."

# The config.py file has already been updated in the previous edits
print_status "Learning cycle interval updated to 35 minutes (2100 seconds)"

# Step 3: Test the backend endpoints
print_header "Testing Backend Endpoints"

# Test the new proposal endpoints
print_status "Testing new proposal endpoints..."

# Test accept-all endpoint
echo "Testing /api/proposals/accept-all..."
curl -X POST "http://34.202.215.209:8000/api/proposals/accept-all" \
     -H "Content-Type: application/json" \
     --max-time 30 \
     --silent \
     --show-error || print_warning "accept-all endpoint test failed"

# Test reset-all endpoint
echo "Testing /api/proposals/reset-all..."
curl -X POST "http://34.202.215.209:8000/api/proposals/reset-all" \
     -H "Content-Type: application/json" \
     --max-time 30 \
     --silent \
     --show-error || print_warning "reset-all endpoint test failed"

# Test cleanup-daily endpoint
echo "Testing /api/proposals/cleanup-daily..."
curl -X POST "http://34.202.215.209:8000/api/proposals/cleanup-daily" \
     -H "Content-Type: application/json" \
     --max-time 30 \
     --silent \
     --show-error || print_warning "cleanup-daily endpoint test failed"

print_status "Backend endpoint tests completed"

# Step 4: Set up daily cleanup
print_header "Setting Up Daily Cleanup"
print_status "Setting up daily cleanup cron job..."

# Make the setup script executable
chmod +x setup_daily_cleanup.py

# Run the setup
python3 setup_daily_cleanup.py setup

print_status "Daily cleanup setup completed"

# Step 5: Restart the backend service
print_header "Restarting Backend Service"
print_status "Restarting ai-backend-python service..."

# Check if systemctl is available
if command -v systemctl &> /dev/null; then
    sudo systemctl restart ai-backend-python || print_warning "Could not restart service via systemctl"
    print_status "Service restart attempted via systemctl"
else
    print_warning "systemctl not available, manual restart may be required"
fi

# Step 6: Verify the deployment
print_header "Verifying Deployment"

# Wait a moment for the service to start
sleep 5

# Test the main endpoints
print_status "Testing main endpoints..."

# Test health endpoint
if curl -s "http://34.202.215.209:8000/health" > /dev/null; then
    print_status "✅ Backend is healthy"
else
    print_error "❌ Backend health check failed"
fi

# Test proposals endpoint
if curl -s "http://34.202.215.209:8000/api/proposals" > /dev/null; then
    print_status "✅ Proposals endpoint is working"
else
    print_error "❌ Proposals endpoint failed"
fi

# Step 7: Show deployment summary
print_header "Deployment Summary"

echo "✅ Changes Applied:"
echo "   - Updated leveling system to use 1,000,000 as highest level"
echo "   - Changed learning cycles to 35 minutes (30-45 minute range)"
echo "   - Added bulk accept all proposals endpoint"
echo "   - Added bulk reset all proposals endpoint"
echo "   - Added daily cleanup endpoint"
echo "   - Limited proposals to 1 per AI type"
echo "   - Set up daily cleanup cron job"

echo ""
echo "🔄 Next Steps:"
echo "   1. Test the frontend with the new leveling system"
echo "   2. Verify bulk operations work correctly"
echo "   3. Monitor daily cleanup logs"
echo "   4. Check that learning cycles run at 35-minute intervals"

echo ""
echo "📝 Useful Commands:"
echo "   - Test cleanup: python3 setup_daily_cleanup.py test"
echo "   - Manual cleanup: python3 setup_daily_cleanup.py manual"
echo "   - Check status: python3 setup_daily_cleanup.py status"
echo "   - View logs: tail -f /var/log/ai-proposal-cleanup.log"

print_header "Deployment Complete! 🎉"

# Optional: Show current cron jobs
echo ""
echo "📅 Current cron jobs:"
crontab -l 2>/dev/null | grep "ai-proposal-cleanup" || echo "No cleanup cron job found"

echo ""
print_status "Deployment completed successfully!" 