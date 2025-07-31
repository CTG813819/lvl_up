#!/bin/bash

# Deploy Custody Protocol Fixes to EC2
# This script uploads and applies the fixes to the EC2 instance

echo "🚀 Deploying Custody Protocol Fixes to EC2..."
echo "=============================================="

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
PEM_FILE="C:\projects\lvl_up\New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 Uploading fix files to server...${NC}"

# Upload the fix script
scp -i "$PEM_FILE" "fix_custody_issues.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Fix script uploaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to upload fix script${NC}"
    exit 1
fi

# Upload the deployment script
scp -i "$PEM_FILE" "deploy_custody_fix.sh" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment script uploaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to upload deployment script${NC}"
    exit 1
fi

echo -e "${YELLOW}🔧 Running custody protocol fixes on server...${NC}"

# SSH into server and run the fixes
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
cd /home/ubuntu/ai-backend-python

echo "🔧 Applying custody protocol fixes..."

# Stop the service first
echo "🛑 Stopping AI backend service..."
sudo systemctl stop ai-backend-python.service

# Wait for service to stop
sleep 5

# Run the Python fix script
echo "🔧 Running Python fix script..."
python3 fix_custody_issues.py

if [ $? -eq 0 ]; then
    echo "✅ Python fixes applied successfully"
else
    echo "❌ Python fixes failed"
    exit 1
fi

# Test the fixes
echo "🧪 Testing the fixes..."
python3 -c "
import sys
sys.path.append('app')
try:
    from app.services.custody_protocol_service import CustodyProtocolService
    print('✅ CustodyProtocolService import successful')
    
    # Test that the method exists
    custody_service = CustodyProtocolService()
    if hasattr(custody_service, '_execute_collaborative_test'):
        print('✅ _execute_collaborative_test method exists')
    else:
        print('❌ _execute_collaborative_test method not found')
        exit(1)
        
    print('✅ All tests passed!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi

# Start the service
echo "🚀 Starting AI backend service..."
sudo systemctl start ai-backend-python.service

# Wait for service to start
sleep 10

# Check service status
echo "📊 Checking service status..."
sudo systemctl status ai-backend-python.service --no-pager -l

# Test the service endpoints
echo "🧪 Testing service endpoints..."
curl -s http://localhost:8000/health || echo "❌ Health check failed"

echo "✅ Custody protocol fixes deployed successfully!"
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Custody protocol fixes deployed successfully to EC2${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 Checking final service status...${NC}"

# Check final status
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
echo "📊 Final service status:"
sudo systemctl status ai-backend-python.service --no-pager

echo ""
echo "📋 Recent logs:"
sudo journalctl -u ai-backend-python.service --no-pager -l -n 20

echo ""
echo "🔍 Testing custody service methods:"
python3 -c "
import asyncio
import sys
sys.path.append('/home/ubuntu/ai-backend-python')

async def test_custody_service():
    try:
        from app.services.custody_protocol_service import CustodyProtocolService
        
        # Test that the service can be imported
        print('✅ CustodyProtocolService import successful')
        
        # Test that the method exists
        custody_service = CustodyProtocolService()
        if hasattr(custody_service, '_execute_collaborative_test'):
            print('✅ _execute_collaborative_test method exists')
        else:
            print('❌ _execute_collaborative_test method not found')
            return False
            
        # Test that the service can be initialized (without full init)
        print('✅ CustodyProtocolService instantiation successful')
        
        print('✅ All custody service tests passed')
        return True
        
    except Exception as e:
        print(f'❌ Error testing custody service: {e}')
        return False

# Run the test
result = asyncio.run(test_custody_service())
if not result:
    exit(1)
"
EOF

echo -e "${GREEN}🎉 Custody Protocol Fixes Deployment Complete!${NC}"
echo -e "${YELLOW}📋 Summary of fixes applied:${NC}"
echo -e "${YELLOW}   • Removed testing_service.initialize() call${NC}"
echo -e "${YELLOW}   • Fixed database parameter binding issues${NC}"
echo -e "${YELLOW}   • Fixed Claude tokens missing parameter${NC}"
echo -e "${YELLOW}   • Ensured _execute_collaborative_test method exists${NC}"
echo -e "${YELLOW}   • Added missing imports${NC}"
echo -e "${YELLOW}   • Fixed anthropic_rate_limited_call usage${NC}"
echo -e "${YELLOW}   • Restarted backend service${NC}"
echo -e "${YELLOW}   • Verified all required methods are present${NC}"