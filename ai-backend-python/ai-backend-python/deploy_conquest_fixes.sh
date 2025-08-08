#!/bin/bash

# Deploy Conquest AI fixes to EC2 instance
echo "🚀 Deploying Conquest AI fixes to EC2 instance..."

# Set variables
EC2_HOST="your-ec2-instance-ip"
EC2_USER="ubuntu"
BACKEND_DIR="/home/ubuntu/ai-backend-python"
FRONTEND_DIR="/home/ubuntu/lvl_up"

# Deploy backend fixes
echo "📦 Deploying backend fixes..."
scp -i ~/.ssh/your-key.pem ai-backend-python/app/services/conquest_ai_service.py $EC2_USER@$EC2_HOST:$BACKEND_DIR/app/services/

# Deploy frontend fixes
echo "📱 Deploying frontend fixes..."
scp -i ~/.ssh/your-key.pem lib/screens/conquest_apps_screen.dart $EC2_USER@$EC2_HOST:$FRONTEND_DIR/lib/screens/
scp -i ~/.ssh/your-key.pem lib/mission_provider.dart $EC2_USER@$EC2_HOST:$FRONTEND_DIR/lib/
scp -i ~/.ssh/your-key.pem lib/services/conquest_ai_service.dart $EC2_USER@$EC2_HOST:$FRONTEND_DIR/lib/services/

# Restart backend services
echo "🔄 Restarting backend services..."
ssh -i ~/.ssh/your-key.pem $EC2_USER@$EC2_HOST << 'EOF'
cd /home/ubuntu/ai-backend-python
sudo systemctl restart ai-backend-python
echo "✅ Backend restarted"
EOF

# Build and deploy frontend
echo "🔨 Building frontend..."
ssh -i ~/.ssh/your-key.pem $EC2_USER@$EC2_HOST << 'EOF'
cd /home/ubuntu/lvl_up
flutter clean
flutter pub get
flutter build apk --release
echo "✅ Frontend built"
EOF

echo "🎉 Deployment completed!"
echo "📋 Summary of fixes:"
echo "   - Removed filter text from Conquest AI statistics"
echo "   - Fixed GitHub progress integration for app completion status"
echo "   - Reduced notification and refresh frequency to prevent spam"
echo "   - Fixed unused variable warning" 