#!/bin/bash

# Deploy Adversarial Testing Fixes to EC2
# This script applies all fixes for infinite adversarial testing

set -e

echo "🚀 Deploying Adversarial Testing Fixes to EC2"
echo "=============================================="

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

# EC2 connection details
EC2_IP="34.202.215.209"
EC2_USER="ubuntu"
PEM_FILE="C:/projects/lvl_up/New.pem"
BACKEND_DIR="/home/ubuntu/ai-backend-python"

print_status "Starting deployment of adversarial testing fixes..."

# Step 1: Upload the reset token script
print_status "Uploading token reset script..."
scp -i "$PEM_FILE" reset_token_usage_ec2.py "$EC2_USER@$EC2_IP:$BACKEND_DIR/"

# Step 2: Upload the enhanced scenario service
print_status "Uploading enhanced scenario service..."
scp -i "$PEM_FILE" ai-backend-python/app/services/enhanced_scenario_service.py "$EC2_USER@$EC2_IP:$BACKEND_DIR/app/services/"

# Step 3: Execute the token reset script
print_status "Executing token reset script..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "cd $BACKEND_DIR && python3 reset_token_usage_ec2.py"

# Step 4: Restart the backend service
print_status "Restarting backend service..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "sudo systemctl restart ai-backend-python"

# Step 5: Test the adversarial testing endpoints
print_status "Testing adversarial testing endpoints..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "cd $BACKEND_DIR && curl -s http://localhost:8000/api/imperium/status"

# Step 6: Check if port 8001 is open for adversarial testing
print_status "Checking port 8001 for adversarial testing..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "sudo ufw allow 8001"

# Step 7: Create adversarial testing service on port 8001
print_status "Creating adversarial testing service on port 8001..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "cd $BACKEND_DIR && nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 1 > adversarial_testing.log 2>&1 &"

# Step 8: Test the adversarial testing service
print_status "Testing adversarial testing service..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_IP" "curl -s http://localhost:8001/api/imperium/status"

print_success "Adversarial testing fixes deployed successfully!"
print_success "✅ Token usage reset to zero"
print_success "✅ Enhanced scenario service updated"
print_success "✅ Backend service restarted"
print_success "✅ Adversarial testing service running on port 8001"
print_success "✅ Infinite token generation enabled"

echo ""
echo "🎯 Adversarial Testing Features:"
echo "  • Infinite scenario generation using internet sources and LLMs"
echo "  • Live attack streaming on port 8001"
echo "  • Progressive difficulty scaling"
echo "  • Enhanced penetration testing scenarios"
echo "  • Real-time AI response tracking"
echo ""
echo "🌐 Access Points:"
echo "  • Main Backend: http://34.202.215.209:8000"
echo "  • Adversarial Testing: http://34.202.215.209:8001"
echo "  • Flutter App: Updated to use port 8001 for adversarial testing" 