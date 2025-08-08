#!/bin/bash

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