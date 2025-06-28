#!/bin/bash

echo "🚀 Deploying AI Learning Backend to AWS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
EC2_IP=${EC2_IP:-"your-ec2-ip"}
KEY_FILE=${KEY_FILE:-"your-key.pem"}
APP_NAME="ai-learning-backend"
DEPLOYMENT_BUCKET=${DEPLOYMENT_BUCKET:-"your-deployment-bucket"}

echo -e "${YELLOW}Configuration:${NC}"
echo "EC2 IP: $EC2_IP"
echo "Key File: $KEY_FILE"
echo "App Name: $APP_NAME"
echo "Deployment Bucket: $DEPLOYMENT_BUCKET"
echo ""

# Check if required variables are set
if [ "$EC2_IP" = "your-ec2-ip" ]; then
    echo -e "${RED}❌ Please set EC2_IP environment variable${NC}"
    exit 1
fi

if [ "$KEY_FILE" = "your-key.pem" ]; then
    echo -e "${RED}❌ Please set KEY_FILE environment variable${NC}"
    exit 1
fi

# Step 1: Build the application
echo -e "${YELLOW}📦 Building application...${NC}"
npm install --production

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

# Step 2: Create deployment package
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
zip -r ai-learning-backend.zip . -x "node_modules/*" ".git/*" "*.log" "deploy-to-aws.sh" "restart-backend.bat"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Package creation failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment package created: ai-learning-backend.zip${NC}"

# Step 3: Upload to EC2
echo -e "${YELLOW}📤 Uploading to EC2...${NC}"
scp -i "$KEY_FILE" ai-learning-backend.zip ubuntu@"$EC2_IP":~/

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Upload failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Upload completed${NC}"

# Step 4: Deploy on EC2
echo -e "${YELLOW}🚀 Deploying on EC2...${NC}"
ssh -i "$KEY_FILE" ubuntu@"$EC2_IP" << 'EOF'
    echo "📦 Extracting deployment package..."
    unzip -o ai-learning-backend.zip -d ai-learning-backend-temp
    
    echo "📁 Moving to application directory..."
    rm -rf ai-learning-backend
    mv ai-learning-backend-temp ai-learning-backend
    cd ai-learning-backend
    
    echo "📦 Installing dependencies..."
    npm install --production
    
    echo "🔧 Creating environment file..."
    cat > .env << 'ENVEOF'
NODE_ENV=production
PORT=4000
MONGODB_URI=mongodb://localhost:27017/ai-learning
AWS_REGION=us-east-1
CORS_ORIGIN=*
ENABLE_CLOUDWATCH=false
LOG_LEVEL=info
ENVEOF
    
    echo "🔄 Restarting application with PM2..."
    pm2 restart ai-learning-backend || pm2 start src/index.js --name ai-learning-backend --max-memory-restart 3G
    
    echo "💾 Saving PM2 configuration..."
    pm2 save
    
    echo "🧹 Cleaning up..."
    rm -f ~/ai-learning-backend.zip
    
    echo "✅ Deployment completed!"
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 5: Clean up local files
echo -e "${YELLOW}🧹 Cleaning up local files...${NC}"
rm -f ai-learning-backend.zip

# Step 6: Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
sleep 5
curl -f "http://$EC2_IP:4000/api/health" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment verified successfully!${NC}"
    echo -e "${GREEN}🌐 Backend is running at: http://$EC2_IP:4000${NC}"
else
    echo -e "${YELLOW}⚠️  Deployment may still be starting up...${NC}"
    echo -e "${YELLOW}🔍 Check logs with: ssh -i $KEY_FILE ubuntu@$EC2_IP 'pm2 logs ai-learning-backend'${NC}"
fi

echo ""
echo -e "${GREEN}🎉 AWS deployment completed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your Flutter app backend URL to: http://$EC2_IP:4000"
echo "2. Test the connection from your mobile app"
echo "3. Monitor logs: ssh -i $KEY_FILE ubuntu@$EC2_IP 'pm2 logs ai-learning-backend'"
echo "4. Check status: ssh -i $KEY_FILE ubuntu@$EC2_IP 'pm2 status'" 