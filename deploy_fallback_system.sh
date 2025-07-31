#!/bin/bash

echo "🚀 Deploying Fallback System to EC2..."

EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
PEM_FILE="C:\projects\lvl_up\New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 Copying modified files to server...${NC}"

scp -i "$PEM_FILE" "ai-backend-python/app/services/enhanced_test_generator_fixed.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/app/services/enhanced_test_generator_fixed.py"
scp -i "$PEM_FILE" "ai-backend-python/app/services/custody_protocol_service_fixed.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/app/services/custody_protocol_service_fixed.py"

echo -e "${GREEN}✅ Files copied successfully${NC}"

echo -e "${YELLOW}🔧 Updating service files on server...${NC}"

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
cd /home/ubuntu/ai-backend-python

echo "🔄 Backing up original files..."
cp app/services/enhanced_test_generator.py app/services/enhanced_test_generator.py.backup
cp app/services/custody_protocol_service.py app/services/custody_protocol_service.py.backup

echo "📝 Updating enhanced test generator..."
cp app/services/enhanced_test_generator_fixed.py app/services/enhanced_test_generator.py

echo "📝 Updating custody protocol service..."
cp app/services/custody_protocol_service_fixed.py app/services/custody_protocol_service.py

echo "🔧 Updating imports in main application..."
sed -i 's/from app.services.enhanced_test_generator import EnhancedTestGenerator/from app.services.enhanced_test_generator_fixed import EnhancedTestGenerator/g' app/main.py

echo "🔧 Updating background service to use fallback system..."
sed -i 's/from app.services.custody_protocol_service import CustodyProtocolService/from app.services.custody_protocol_service_fixed import CustodyProtocolService/g' app/services/background_service.py

echo "✅ Files updated successfully"
EOF

echo -e "${GREEN}✅ Service files updated${NC}"

echo -e "${YELLOW}🔄 Restarting AI backend service...${NC}"

ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
sudo systemctl stop ai-backend-python.service
sleep 5
sudo systemctl start ai-backend-python.service
sleep 10

echo "📊 Checking service status..."
sudo systemctl status ai-backend-python.service --no-pager -l

echo "📋 Recent logs..."
sudo journalctl -u ai-backend-python.service --no-pager -l -n 20
EOF

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}📋 The fallback system is now active and will:${NC}"
echo -e "${YELLOW}   • Use Claude when tokens are available${NC}"
echo -e "${YELLOW}   • Automatically fallback to custodes system when Claude is unavailable${NC}"
echo -e "${YELLOW}   • Execute custody, Olympic, and collaborative tests independently${NC}"
echo -e "${YELLOW}   • Not depend on GitHub API for test generation${NC}"

echo -e "${GREEN}🎉 Fallback system deployment complete!${NC}"