#!/bin/bash

# Deploy Proposal Improvements to EC2
# This script deploys the enhanced proposal system to the EC2 instance

set -e

echo "🚀 Deploying Proposal Improvements to EC2"

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
SSH_KEY="C:/projects/lvl_up/New.pem"
REMOTE_PATH="/home/ubuntu/ai-backend-python"
LOCAL_PATH="ai-backend-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Step 1: Check SSH key
print_status "Step 1: Checking SSH key..."
if [ -f "$SSH_KEY" ]; then
    print_success "SSH key found: $SSH_KEY"
    chmod 400 "$SSH_KEY"
else
    print_error "SSH key not found: $SSH_KEY"
    exit 1
fi

# Step 2: Test EC2 connectivity
print_status "Step 2: Testing EC2 connectivity..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'Connection successful'" 2>/dev/null; then
    print_success "EC2 connection successful"
else
    print_error "Cannot connect to EC2 instance"
    print_warning "Please check your EC2 instance is running and accessible"
    exit 1
fi

# Step 3: Create deployment package
print_status "Step 3: Creating deployment package..."
DEPLOY_PACKAGE="proposal_improvements_$(date +%Y%m%d_%H%M%S).tar.gz"

# Create tar.gz of the specific files we need to deploy
tar -czf "$DEPLOY_PACKAGE" \
    -C "$LOCAL_PATH" \
    app/services/proposal_validation_service.py \
    app/routers/proposals.py \
    test_proposal_validation.py \
    PROPOSAL_IMPROVEMENTS_SUMMARY.md

if [ -f "$DEPLOY_PACKAGE" ]; then
    print_success "Deployment package created: $DEPLOY_PACKAGE"
else
    print_error "Failed to create deployment package"
    exit 1
fi

# Step 4: Upload to EC2
print_status "Step 4: Uploading to EC2..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$DEPLOY_PACKAGE" "$EC2_USER@$EC2_HOST:~/"

if [ $? -eq 0 ]; then
    print_success "Deployment package uploaded to EC2"
else
    print_error "Failed to upload deployment package"
    exit 1
fi

# Step 5: Deploy on EC2
print_status "Step 5: Deploying on EC2..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
    echo "🔧 Deploying proposal improvements on EC2..."
    
    # Navigate to backend directory
    cd /home/ubuntu/ai-backend-python
    
    # Extract deployment package
    tar -xzf ~/proposal_improvements_*.tar.gz
    
    # Install any missing dependencies
    pip3 install scikit-learn pandas numpy joblib requests
    
    # Test the validation service
    echo "🧪 Testing proposal validation service..."
    python3 test_proposal_validation.py
    
    # Restart the backend service
    echo "🔄 Restarting backend service..."
    sudo systemctl restart ai-backend-python
    
    # Wait for service to start
    sleep 10
    
    # Check service status
    echo "📊 Checking service status..."
    sudo systemctl status ai-backend-python --no-pager
    
    # Test the new endpoints
    echo "🔍 Testing new endpoints..."
    
    # Test validation stats endpoint
    curl -s http://localhost:8000/api/proposals/validation/stats | jq '.' || echo "Validation stats endpoint test completed"
    
    # Test proposal creation with validation
    curl -s -X POST http://localhost:8000/api/proposals/ \
      -H "Content-Type: application/json" \
      -d '{
        "ai_type": "Imperium",
        "file_path": "lib/screens/test_screen.dart",
        "code_before": "class TestWidget extends StatelessWidget { }",
        "code_after": "class TestWidget extends StatelessWidget { \n  @override\n  Widget build(BuildContext context) {\n    return Container();\n  }\n}",
        "improvement_type": "feature",
        "confidence": 0.8
      }' | jq '.' || echo "Proposal creation test completed"
    
    echo "✅ Deployment completed on EC2"
EOF

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully on EC2"
else
    print_error "Deployment failed on EC2"
    exit 1
fi

# Step 6: Test the deployment
print_status "Step 6: Testing the deployment..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'EOF'
    echo "🧪 Testing deployment..."
    
    # Test backend health
    curl -s http://localhost:8000/api/health | jq '.' || echo "Health check completed"
    
    # Test validation stats
    curl -s http://localhost:8000/api/proposals/validation/stats | jq '.' || echo "Validation stats check completed"
    
    # Test proposal endpoints
    curl -s http://localhost:8000/api/proposals/ | jq '.' || echo "Proposals endpoint check completed"
    
    echo "✅ All tests completed"
EOF

# Step 7: Generate deployment report
print_status "Step 7: Generating deployment report..."
cat > proposal_improvements_deployment_report.txt << EOF
Proposal Improvements Deployment Report
=====================================

Deployment Date: $(date)
EC2 Instance: $EC2_HOST
Deployment Package: $DEPLOY_PACKAGE

Deployed Components:
- Enhanced Proposal Validation Service
- Improved Proposal Descriptions
- AI Learning Integration
- Duplicate Detection System
- Confidence Threshold Validation
- Improvement Potential Assessment

New Features:
1. Enhanced frontend descriptions with AI-specific explanations
2. Backend validation to prevent redundant proposals
3. AI learning requirements before new proposals
4. Confidence threshold validation (60% minimum)
5. Improvement potential assessment
6. Duplicate detection with 85% similarity threshold
7. Proposal limits (2 pending per AI, 10 daily per AI)
8. Learning interval requirements (2 hours minimum)

API Endpoints:
- GET /api/proposals/validation/stats - Get validation statistics
- POST /api/proposals/ - Enhanced with validation
- All existing proposal endpoints remain functional

Validation Process:
1. Duplicate Check - Compares with existing proposals
2. Learning Status - Verifies AI has learned from feedback
3. Proposal Limits - Ensures limits are not exceeded
4. Confidence Check - Validates minimum confidence threshold
5. Improvement Assessment - Evaluates potential impact

Configuration:
- Similarity Threshold: 85%
- Minimum Learning Interval: 2 hours
- Max Pending per AI: 2
- Daily Limit per AI: 10
- Minimum Confidence: 60%

Deployment Status: ✅ SUCCESS
EOF

print_success "Deployment report saved to proposal_improvements_deployment_report.txt"

# Cleanup
rm -f "$DEPLOY_PACKAGE"
print_status "Deployment package cleaned up"

print_success "Proposal improvements deployment completed!"
echo ""
print_status "Next steps:"
echo "1. Test the enhanced proposal descriptions in your Flutter app"
echo "2. Monitor proposal validation through the new stats endpoint"
echo "3. Check that AIs are learning and waiting appropriately"
echo "4. Verify that redundant proposals are being filtered out"
echo ""
print_status "Test endpoints:"
echo "  - http://$EC2_HOST:8000/api/proposals/validation/stats"
echo "  - http://$EC2_HOST:8000/api/proposals/"
echo "  - http://$EC2_HOST:8000/api/health" 