# Replace PC Backend with AWS - Step by Step

## 🎯 Goal
Deploy your AI Learning backend to AWS so it works without your PC connection.

## 📋 Prerequisites
- AWS account (free tier available)
- Credit card for billing (~$30-65/month)
- 30 minutes setup time

## 🚀 Quick Setup (5 Steps)

### Step 1: Create AWS EC2 Instance

1. **Go to AWS Console**: https://console.aws.amazon.com
2. **Launch EC2 Instance**:
   - Instance Type: `t3.medium` (2 vCPU, 4GB RAM)
   - AMI: Ubuntu Server 22.04 LTS
   - Storage: 20GB GP3 SSD
   - Security Group: Allow ports 22, 80, 443, 4000
   - Key Pair: Create new and download `.pem` file

3. **Note Your EC2 IP**: Copy the Public IPv4 address (e.g., `3.250.123.45`)

### Step 2: Setup EC2 Instance

1. **Connect to EC2**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Run Setup Script**:
   ```bash
   # Copy setup script to EC2
   scp -i your-key.pem setup-ec2.sh ubuntu@your-ec2-ip:~/
   
   # Run setup on EC2
   ssh -i your-key.pem ubuntu@your-ec2-ip "chmod +x setup-ec2.sh && ./setup-ec2.sh"
   ```

### Step 3: Deploy Backend

1. **Update Deployment Script**:
   - Open `deploy-to-aws-simple.bat`
   - Replace `your-ec2-ip-here` with your actual EC2 IP
   - Replace `your-key-file.pem` with your key file name

2. **Run Deployment**:
   ```bash
   # Windows
   deploy-to-aws-simple.bat
   
   # Or manually:
   cd ai-backend
   npm install --production
   # Then follow the deployment steps
   ```

### Step 4: Update Flutter App

1. **Update Network Config**:
   ```dart
   // lib/services/network_config.dart
   static const String _awsBackendUrl = 'http://your-ec2-ip:4000';
   ```

2. **Test Connection**:
   ```bash
   # Test from browser
   http://your-ec2-ip:4000/api/health
   ```

### Step 5: Verify Everything Works

1. **Check Backend Status**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip "pm2 status"
   ```

2. **View Logs**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip "pm2 logs ai-learning-backend"
   ```

3. **Test from Flutter App**:
   - Run your Flutter app
   - Check if it connects to AWS backend
   - Test AI Learning features

## 🔧 Manual Setup (If Scripts Don't Work)

### On EC2 Instance:
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Deploy Backend:
```bash
# Upload your code
scp -i your-key.pem -r ai-backend/ ubuntu@your-ec2-ip:~/

# On EC2
cd ai-learning-backend
npm install --production

# Create .env file
cat > .env << EOF
NODE_ENV=production
PORT=4000
MONGODB_URI=mongodb://localhost:27017/ai-learning
CORS_ORIGIN=*
EOF

# Start with PM2
pm2 start src/index.js --name ai-learning-backend
pm2 startup
pm2 save
```

## 💰 Cost Breakdown

### Monthly AWS Costs:
- **EC2 t3.medium**: ~$30/month
- **Data Transfer**: ~$10/month
- **Total**: ~$40/month

### Cost Optimization:
- Use Spot Instances for development (~$15/month)
- Implement auto-scaling
- Monitor usage with CloudWatch

## 🔍 Troubleshooting

### Connection Issues:
```bash
# Check if backend is running
ssh -i your-key.pem ubuntu@your-ec2-ip "pm2 status"

# Check logs
ssh -i your-key.pem ubuntu@your-ec2-ip "pm2 logs ai-learning-backend"

# Check MongoDB
ssh -i your-key.pem ubuntu@your-ec2-ip "sudo systemctl status mongod"

# Test API endpoint
curl http://your-ec2-ip:4000/api/health
```

### Security Group Issues:
- Ensure port 4000 is open in AWS Security Group
- Check if your IP is allowed for SSH (port 22)

### Memory Issues:
```bash
# Check memory usage
ssh -i your-key.pem ubuntu@your-ec2-ip "free -h"

# Restart with more memory
ssh -i your-key.pem ubuntu@your-ec2-ip "pm2 restart ai-learning-backend --max-memory-restart 3G"
```

## ✅ Success Checklist

- [ ] EC2 instance created and running
- [ ] Backend deployed and accessible
- [ ] Flutter app updated with AWS URL
- [ ] AI Learning features working
- [ ] No PC connection required
- [ ] App works on any device, anywhere

## 🎉 Benefits After Migration

- ✅ **No PC dependency** - Backend runs 24/7 on AWS
- ✅ **Global accessibility** - Works from anywhere
- ✅ **Better reliability** - 99.9% uptime SLA
- ✅ **Scalability** - Auto-scaling capabilities
- ✅ **Professional monitoring** - CloudWatch integration
- ✅ **Cost-effective** - Pay only for what you use

## 📞 Support

If you encounter issues:
1. Check AWS CloudWatch logs
2. Review PM2 logs on EC2
3. Test API endpoints manually
4. Verify security group settings
5. Check MongoDB status

Your backend will now run independently on AWS without needing your PC! 