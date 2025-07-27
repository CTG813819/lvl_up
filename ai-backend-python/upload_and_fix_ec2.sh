#!/bin/bash

# Upload and Fix EC2 Backend Issues Script
# This script uploads the fix files to EC2 and runs them

echo "🚀 Upload and Fix EC2 Backend Issues"
echo "===================================="

# Configuration
EC2_USER="ubuntu"
EC2_IP="your-ec2-ip-here"  # Replace with your actual EC2 IP
EC2_KEY="your-key.pem"     # Replace with your actual key file path
REMOTE_DIR="~/ai-backend-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "EC2 User: $EC2_USER"
echo "EC2 IP: $EC2_IP"
echo "Remote Directory: $REMOTE_DIR"
echo ""

# Check if key file exists
if [ ! -f "$EC2_KEY" ]; then
    echo -e "${RED}❌ Key file not found: $EC2_KEY${NC}"
    echo "Please update the EC2_KEY variable in this script with your actual key file path"
    exit 1
fi

# Check if fix script exists
if [ ! -f "fix_backend_issues.py" ]; then
    echo -e "${RED}❌ fix_backend_issues.py not found in current directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📤 Uploading files to EC2...${NC}"

# Upload the fix script
scp -i "$EC2_KEY" fix_backend_issues.py "$EC2_USER@$EC2_IP:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ fix_backend_issues.py uploaded successfully${NC}"
else
    echo -e "${RED}❌ Failed to upload fix_backend_issues.py${NC}"
    exit 1
fi

# Upload the test script if it exists
if [ -f "test_backend_fixes.py" ]; then
    scp -i "$EC2_KEY" test_backend_fixes.py "$EC2_USER@$EC2_IP:$REMOTE_DIR/"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ test_backend_fixes.py uploaded successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to upload test_backend_fixes.py (continuing anyway)${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}🔧 Running fixes on EC2...${NC}"

# SSH into EC2 and run the fixes
ssh -i "$EC2_KEY" "$EC2_USER@$EC2_IP" << 'EOF'
cd ~/ai-backend-python

echo "🔧 Running backend fixes..."
python fix_backend_issues.py

if [ $? -eq 0 ]; then
    echo "✅ Fixes applied successfully!"
    
    echo ""
    echo "🔄 Restarting backend service..."
    sudo systemctl restart ai-backend-python
    
    echo ""
    echo "📊 Checking backend status..."
    sudo systemctl status ai-backend-python --no-pager
    
    echo ""
    echo "🧪 Running tests..."
    if [ -f "test_backend_fixes.py" ]; then
        python test_backend_fixes.py
    else
        echo "⚠️  Test script not found, skipping tests"
    fi
    
    echo ""
    echo "📋 Next steps:"
    echo "1. Monitor logs: sudo journalctl -u ai-backend-python -f"
    echo "2. Check health endpoint: curl http://localhost:8000/health"
    echo "3. Test OpenAI integration: python test_simple_openai.py"
    
else
    echo "❌ Fixes failed. Please check the errors above."
fi
EOF

echo ""
echo -e "${GREEN}🎉 Upload and fix process completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Manual steps if needed:${NC}"
echo "1. SSH into EC2: ssh -i $EC2_KEY $EC2_USER@$EC2_IP"
echo "2. Navigate to: cd ~/ai-backend-python"
echo "3. Run fixes manually: python fix_backend_issues.py"
echo "4. Restart backend: sudo systemctl restart ai-backend-python"
echo "5. Monitor logs: sudo journalctl -u ai-backend-python -f" 