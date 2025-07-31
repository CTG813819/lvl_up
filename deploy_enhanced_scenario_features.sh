#!/bin/bash

echo "🚀 Deploying Enhanced Scenario Features to EC2"
echo "================================================"

# Set variables
EC2_IP="34.202.215.209"
KEY_PATH="C:/projects/lvl_up/New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

echo "📋 Step 1: Copying enhanced files to EC2..."

# Copy enhanced scenario service
scp -i "$KEY_PATH" ai-backend-python/app/services/enhanced_scenario_service.py ubuntu@$EC2_IP:$REMOTE_DIR/app/services/

# Copy updated training data router
scp -i "$KEY_PATH" ai-backend-python/app/routers/training_data.py ubuntu@$EC2_IP:$REMOTE_DIR/app/routers/

# Copy updated training ground screen
scp -i "$KEY_PATH" lib/screens/training_ground_screen.dart ubuntu@$EC2_IP:$REMOTE_DIR/lib/screens/

echo "✅ Files copied successfully!"

echo "📋 Step 2: Installing dependencies on EC2..."

# Install SQLite3 if not already installed
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    echo "Installing SQLite3..."
    sudo apt-get update
    sudo apt-get install -y sqlite3
    
    echo "Installing Python dependencies..."
    cd /home/ubuntu/ai-backend-python
    pip install aiohttp structlog
    
    echo "Creating database directories..."
    mkdir -p /home/ubuntu/ai-backend-python/databases
    cd /home/ubuntu/ai-backend-python/databases
    
    echo "✅ Dependencies installed!"
EOF

echo "📋 Step 3: Restarting services..."

# Restart the AI backend service
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    echo "Restarting AI backend service..."
    sudo systemctl restart ai-backend-python
    
    echo "Checking service status..."
    sudo systemctl status ai-backend-python --no-pager
    
    echo "✅ Services restarted!"
EOF

echo "📋 Step 4: Testing enhanced features..."

# Test the new endpoints
ssh -i "$KEY_PATH" ubuntu@$EC2_IP << 'EOF'
    echo "Testing enhanced scenario endpoints..."
    cd /home/ubuntu/ai-backend-python
    
    # Test expert examples endpoint
    echo "Testing expert examples endpoint..."
    curl -s http://localhost:8000/api/ai/expert-examples | head -20
    
    # Test scenario suggestions endpoint
    echo "Testing scenario suggestions endpoint..."
    curl -s http://localhost:8000/api/ai/scenario-suggestions | head -20
    
    # Test building scenario from suggestion
    echo "Testing build suggested scenario endpoint..."
    curl -s -X POST http://localhost:8000/api/ai/build-suggested-scenario/1 | head -20
    
    # Test building scenario from expert example
    echo "Testing build expert scenario endpoint..."
    curl -s -X POST http://localhost:8000/api/ai/build-expert-scenario/1 | head -20
    
    echo "✅ Endpoint tests completed!"
EOF

echo "🎉 Enhanced Scenario Features Deployment Complete!"
echo ""
echo "📋 Summary of deployed features:"
echo "   ✅ Enhanced Scenario Service with expert learning"
echo "   ✅ Enhanced scenario suggestion system with description, requirements, and outcome"
echo "   ✅ Expert examples database and API with sandbox integration"
echo "   ✅ Updated training data router with new endpoints"
echo "   ✅ Enhanced Dart training ground screen with difficulty slider"
echo "   ✅ Build scenario functionality for both suggestions and expert examples"
echo ""
echo "🔗 EC2 Instance: $EC2_IP"
echo "📁 Remote Directory: $REMOTE_DIR"
echo ""
echo "🌐 New API Endpoints:"
echo "   - POST /api/ai/scenario-suggestion (enhanced with requirements/outcome)"
echo "   - GET /api/ai/scenario-suggestions"
echo "   - POST /api/ai/expert-learning"
echo "   - GET /api/ai/expert-examples"
echo "   - POST /api/ai/build-suggested-scenario/{suggestion_id}"
echo "   - POST /api/ai/build-expert-scenario/{example_id}"
echo ""
echo "📱 Flutter App Features:"
echo "   - Enhanced scenario suggestion form with description, requirements, outcome"
echo "   - Difficulty slider (Easy/Medium/Hard/Expert)"
echo "   - Expert examples display with build scenario functionality"
echo "   - Real-time suggestion status updates"
echo "   - AI feedback integration"
echo "   - Sandbox scenario building from both suggestions and expert examples" 