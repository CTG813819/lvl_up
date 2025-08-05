# AWS Deployment Guide for LVL UP AI Learning Backend

## 🚀 Quick Start

### Prerequisites
- AWS EC2 instance running Ubuntu
- Key pair file: `New.pem` (place in project root)
- EC2 IP Address: `44.204.184.21`

### 1. Place Your Key File
Place your `New.pem` file in the project root directory (same level as this README).

### 2. Deploy Backend
Run the deployment script:
```bash
deploy-to-aws-simple.bat
```

### 3. Update Flutter App
The Flutter app is already configured to use the new AWS backend at:
```
http://44.204.184.21:4000
```

## 📋 Manual Deployment Steps

If the automated script fails, follow these manual steps:

### 1. Build Backend
```bash
cd ai-backend
npm install --production
```

### 2. Create Deployment Package
```bash
# On Windows
powershell -Command "Compress-Archive -Path * -DestinationPath ..\ai-learning-backend.zip -Force"

# On Linux/Mac
zip -r ../ai-learning-backend.zip .
```

### 3. Upload to EC2
```bash
scp -i "New.pem" ai-learning-backend.zip ubuntu@44.204.184.21:~/
```

### 4. Deploy on EC2
```bash
ssh -i "New.pem" ubuntu@44.204.184.21
```

Then run these commands on the EC2 instance:
```bash
# Stop existing service
pm2 stop ai-learning-backend || true
pm2 delete ai-learning-backend || true

# Extract new version
unzip -o ai-learning-backend.zip -d /home/ubuntu/ai-learning-backend
cd /home/ubuntu/ai-learning-backend

# Install dependencies
npm install --production

# Start with memory optimization
pm2 start src/index.js --name ai-learning-backend --node-args="--max-old-space-size=4096"

# Save PM2 configuration
pm2 save

# Check status
pm2 status
pm2 logs ai-learning-backend
```

## 🔧 Configuration

### Backend Configuration
The backend is configured to run on port 4000 with:
- Memory limit: 4GB
- Auto-restart on failure
- Log rotation
- Health monitoring

### Flutter Configuration
The Flutter app is configured in `lib/services/network_config.dart`:
```dart
static const String baseUrl = 'http://44.204.184.21:4000';
```

## 📊 Monitoring

### Check Backend Status
```bash
ssh -i "New.pem" ubuntu@44.204.184.21 "pm2 status"
```

### View Logs
```bash
ssh -i "New.pem" ubuntu@44.204.184.21 "pm2 logs ai-learning-backend"
```

### Memory Usage
```bash
ssh -i "New.pem" ubuntu@44.204.184.21 "pm2 monit"
```

### Health Check
```bash
curl http://44.204.184.21:4000/api/health
```

## 🛠️ Troubleshooting

### Connection Issues
1. Check EC2 security group allows port 4000
2. Verify key file permissions: `chmod 400 New.pem`
3. Check instance status in AWS Console

### Memory Issues
If you see "JavaScript heap out of memory":
```bash
ssh -i "New.pem" ubuntu@44.204.184.21
pm2 restart ai-learning-backend
```

### Service Not Starting
```bash
ssh -i "New.pem" ubuntu@44.204.184.21
cd /home/ubuntu/ai-learning-backend
node src/index.js
```

## 🔄 Updating

To update the backend:
1. Make your changes locally
2. Run `deploy-to-aws-simple.bat` again
3. The script will automatically stop, update, and restart the service

## 📱 Testing

### Test Backend
```bash
curl http://44.204.184.21:4000/api/health
```

### Test Flutter App
1. Build and run your Flutter app
2. Check the AI Learning Dashboard
3. Test AI triggers and learning functionality

## 🔐 Security

- Keep your `New.pem` file secure
- Don't commit it to version control
- Consider using AWS Systems Manager for secure access
- Regularly update your EC2 instance

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review PM2 logs for error details
3. Verify network connectivity
4. Check AWS Console for instance status 