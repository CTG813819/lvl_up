#!/bin/bash

# EC2 Deployment Script for LVL UP Backend
# This script helps deploy the backend to EC2 and ensure it works without the PC

echo "🚀 LVL UP Backend EC2 Deployment Script"
echo "========================================"

# Configuration
EC2_IP="44.204.184.21"
EC2_USER="ubuntu"  # Change if using different user
BACKEND_PORT="4000"
LOCAL_BACKEND_DIR="ai-backend"

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

# Check if we're in the right directory
if [ ! -d "$LOCAL_BACKEND_DIR" ]; then
    print_error "Backend directory '$LOCAL_BACKEND_DIR' not found!"
    print_status "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting EC2 deployment process..."

# Step 1: Check local backend
print_status "Step 1: Checking local backend..."
if [ -f "$LOCAL_BACKEND_DIR/package.json" ]; then
    print_success "Backend package.json found"
else
    print_error "Backend package.json not found!"
    exit 1
fi

# Step 2: Test EC2 connectivity
print_status "Step 2: Testing EC2 connectivity..."
if ping -c 1 $EC2_IP > /dev/null 2>&1; then
    print_success "EC2 instance is reachable"
else
    print_error "Cannot reach EC2 instance at $EC2_IP"
    print_warning "Please check your EC2 instance is running and accessible"
    exit 1
fi

# Step 3: Check if backend is already running on EC2
print_status "Step 3: Checking if backend is running on EC2..."
if curl -s "http://$EC2_IP:$BACKEND_PORT/health" > /dev/null 2>&1; then
    print_success "Backend is already running on EC2"
    print_status "Backend URL: http://$EC2_IP:$BACKEND_PORT"
else
    print_warning "Backend not running on EC2"
    print_status "You'll need to start the backend on your EC2 instance"
fi

# Step 4: Create deployment package
print_status "Step 4: Creating deployment package..."
DEPLOY_PACKAGE="lvl-up-backend-$(date +%Y%m%d-%H%M%S).tar.gz"

# Create tar.gz of backend directory
tar -czf "$DEPLOY_PACKAGE" -C "$LOCAL_BACKEND_DIR" .

if [ -f "$DEPLOY_PACKAGE" ]; then
    print_success "Deployment package created: $DEPLOY_PACKAGE"
else
    print_error "Failed to create deployment package"
    exit 1
fi

# Step 5: Instructions for manual deployment
echo ""
print_status "Step 5: Manual Deployment Instructions"
echo "============================================="
echo ""
print_status "To deploy to EC2, follow these steps:"
echo ""
echo "1. Upload the deployment package to EC2:"
echo "   scp $DEPLOY_PACKAGE $EC2_USER@$EC2_IP:~/"
echo ""
echo "2. SSH into your EC2 instance:"
echo "   ssh $EC2_USER@$EC2_IP"
echo ""
echo "3. Extract and setup the backend:"
echo "   cd ~"
echo "   tar -xzf $DEPLOY_PACKAGE"
echo "   cd ai-backend"
echo "   npm install"
echo "   npm start"
echo ""
echo "4. For persistent deployment, use PM2:"
echo "   npm install -g pm2"
echo "   pm2 start src/index.js --name 'lvl-up-backend'"
echo "   pm2 startup"
echo "   pm2 save"
echo ""

# Step 6: Test app connectivity
print_status "Step 6: Testing app connectivity..."
echo ""
print_status "Your Flutter app is now configured to connect to:"
echo "   Backend: http://$EC2_IP:$BACKEND_PORT"
echo ""
print_status "To test the connection:"
echo "   curl http://$EC2_IP:$BACKEND_PORT/health"
echo ""

# Step 7: Security group check
print_status "Step 7: Security Group Configuration"
echo ""
print_warning "Make sure your EC2 security group allows:"
echo "   - Inbound TCP port $BACKEND_PORT from anywhere (0.0.0.0/0)"
echo "   - Or restrict to your IP for better security"
echo ""

# Step 8: Environment variables
print_status "Step 8: Environment Variables"
echo ""
print_warning "Make sure your .env file on EC2 contains:"
echo "   - GITHUB_TOKEN"
echo "   - MONGODB_URI"
echo "   - Other required environment variables"
echo ""

print_success "Deployment script completed!"
echo ""
print_status "Next steps:"
echo "1. Deploy the backend to EC2 using the instructions above"
echo "2. Test the connection from your Android app"
echo "3. Approve proposals in the app to trigger AI improvements"
echo "4. Use the learning endpoints to nudge the AIs:"
echo "   - POST http://$EC2_IP:$BACKEND_PORT/api/learning/trigger-self-improvement/imperium"
echo "   - POST http://$EC2_IP:$BACKEND_PORT/api/learning/trigger-cross-ai-learning"
echo ""

# Cleanup
rm -f "$DEPLOY_PACKAGE"
print_status "Deployment package cleaned up" 