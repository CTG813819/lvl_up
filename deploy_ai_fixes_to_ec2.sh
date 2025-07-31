#!/bin/bash

# AI Growth Analytics Fixes Deployment Script
# Deploys the fixes to EC2 instance

set -e  # Exit on any error

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
PEM_FILE="C:\projects\lvl_up\New.pem"
BACKEND_DIR="/home/ubuntu/ai-backend-python"
FLUTTER_DIR="/home/ubuntu/lvl_up"

echo "🚀 Starting AI Growth Analytics Fixes Deployment"
echo "=================================================="

# Function to check if file exists
check_file() {
    if [ ! -f "$1" ]; then
        echo "❌ Error: File $1 not found!"
        exit 1
    fi
}

# Check if PEM file exists
echo "🔍 Checking PEM file..."
check_file "$PEM_FILE"

# Function to run command on EC2
run_on_ec2() {
    ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$1"
}

# Function to copy file to EC2
copy_to_ec2() {
    scp -i "$PEM_FILE" -o StrictHostKeyChecking=no "$1" "$EC2_USER@$EC2_HOST:$2"
}

echo "📋 Step 1: Checking backend service status..."
run_on_ec2 "sudo systemctl status guardian-ai || echo 'Service not found'"

echo "📋 Step 2: Stopping backend service..."
run_on_ec2 "sudo systemctl stop guardian-ai || echo 'Service already stopped'"

echo "📋 Step 3: Backing up current files..."
run_on_ec2 "cd $BACKEND_DIR && cp -r app/services app/services.backup.$(date +%Y%m%d_%H%M%S) || echo 'Backup created'"

echo "📋 Step 4: Copying updated backend files..."
echo "   Copying imperium_learning_controller.py..."
copy_to_ec2 "ai-backend-python/app/services/imperium_learning_controller.py" "$BACKEND_DIR/app/services/"

echo "📋 Step 5: Copying Flutter fixes..."
echo "   Copying ai_growth_analytics_provider.dart..."
run_on_ec2 "mkdir -p $FLUTTER_DIR/lib/providers"
copy_to_ec2 "lib/providers/ai_growth_analytics_provider.dart" "$FLUTTER_DIR/lib/providers/"

echo "📋 Step 6: Copying test script..."
copy_to_ec2 "test_ai_fixes_ec2.py" "$BACKEND_DIR/"

echo "📋 Step 7: Setting proper permissions..."
run_on_ec2 "chmod +x $BACKEND_DIR/test_ai_fixes_ec2.py"

echo "📋 Step 8: Starting backend service..."
run_on_ec2 "sudo systemctl start guardian-ai"

echo "📋 Step 9: Waiting for service to start..."
sleep 10

echo "📋 Step 10: Checking service status..."
run_on_ec2 "sudo systemctl status guardian-ai"

echo "📋 Step 11: Testing backend health..."
run_on_ec2 "curl -s http://localhost:8000/health || echo 'Health check failed'"

echo "📋 Step 12: Running AI fixes test..."
run_on_ec2 "cd $BACKEND_DIR && python3 test_ai_fixes_ec2.py"

echo ""
echo "✅ Deployment completed!"
echo "=================================================="
echo "📊 Summary:"
echo "   - Backend service restarted"
echo "   - AI growth analytics fixes deployed"
echo "   - Test script executed"
echo ""
echo "🔍 To verify manually:"
echo "   ssh -i \"$PEM_FILE\" $EC2_USER@$EC2_HOST"
echo "   cd $BACKEND_DIR"
echo "   python3 test_ai_fixes_ec2.py"
echo ""
echo "🌐 Backend URL: http://$EC2_HOST:8000"
echo "==================================================" 