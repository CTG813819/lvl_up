# EC2 Deployment Guide - LVL UP Backend

## Overview
This guide helps you deploy your LVL UP backend to AWS EC2 so your Android app can work without needing your PC running.

## ✅ What's Already Done

Your Flutter app has been updated to prioritize the EC2 backend:
- **Network Configuration**: Updated to use `http://44.204.184.21:4000` as primary backend
- **Socket.IO**: Configured to connect to EC2
- **AI Endpoints**: All AI endpoints point to EC2
- **Loading Screen**: Tests connectivity to EC2 before launching

## 🚀 Quick Deployment Steps

### 1. Test Current EC2 Connection
Run the test script to see if your EC2 backend is already running:
```bash
test-ec2-connection.bat
```

### 2. Deploy Backend to EC2
If the backend isn't running, use the deployment script:
```bash
deploy-to-ec2.bat
```

### 3. Manual EC2 Setup (if needed)

#### SSH into your EC2 instance:
```bash
ssh ubuntu@44.204.184.21
```

#### Install Node.js and npm:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Clone or upload your backend:
```bash
# Option 1: Clone from GitHub
git clone https://github.com/CTG813819/Lvl_UP.git
cd Lvl_UP/ai-backend

# Option 2: Upload via SCP (if you have the files locally)
# scp -r ai-backend/ ubuntu@44.204.184.21:~/
```

#### Install dependencies and start:
```bash
npm install
npm start
```

#### For persistent deployment (recommended):
```bash
npm install -g pm2
pm2 start src/index.js --name "lvl-up-backend"
pm2 startup
pm2 save
```

## 🔧 EC2 Configuration

### Security Group Settings
Make sure your EC2 security group allows:
- **Inbound TCP port 4000** from anywhere (0.0.0.0/0)
- **SSH port 22** from your IP

### Environment Variables
Create a `.env` file on EC2 with:
```env
GITHUB_TOKEN=your_github_token
MONGODB_URI=mongodb+srv://canicegonzague:***@lvlup.j2m9fir.mongodb.net/?retryWrites=true&w=majority&appName=LvlUp
NODE_ENV=production
PORT=4000
```

## 📱 App Configuration

Your Flutter app is now configured to:
- **Primary Backend**: `http://44.204.184.21:4000` (EC2)
- **Fallback URLs**: Local network, emulator, localhost
- **Automatic Detection**: Tests connectivity and uses best available backend

## 🧪 Testing the Setup

### 1. Test Backend Health
```bash
curl http://44.204.184.21:4000/health
```

### 2. Test AI Endpoints
```bash
curl http://44.204.184.21:4000/api/imperium/health
curl http://44.204.184.21:4000/api/guardian/health
curl http://44.204.184.21:4000/api/sandbox/health
```

### 3. Test Learning Endpoints
```bash
curl http://44.204.184.21:4000/api/learning/data
```

### 4. Test from Android App
- Install the updated app on your Android device
- The app should automatically connect to EC2
- Check the logs for successful connection

## 🎯 Using the AI Learning System

Once deployed, you can:

### 1. Approve Proposals
- Use the app's proposal approval interface
- Or approve directly in the backend

### 2. Trigger AI Self-Improvement
```bash
curl -X POST http://44.204.184.21:4000/api/learning/trigger-self-improvement/imperium
curl -X POST http://44.204.184.21:4000/api/learning/trigger-self-improvement/guardian
curl -X POST http://44.204.184.21:4000/api/learning/trigger-self-improvement/sandbox
```

### 3. Trigger Cross-AI Learning
```bash
curl -X POST http://44.204.184.21:4000/api/learning/trigger-cross-ai-learning
```

## 🔍 Monitoring

### Check Backend Status
```bash
# If using PM2
pm2 status
pm2 logs lvl-up-backend

# If running directly
# Check the terminal where you started npm start
```

### Check App Logs
- Use `flutter logs` to see app connection attempts
- Look for successful backend connections

## 🛠️ Troubleshooting

### Backend Not Accessible
1. **Check EC2 instance**: Make sure it's running
2. **Check security group**: Port 4000 must be open
3. **Check backend process**: `pm2 status` or `ps aux | grep node`
4. **Check logs**: `pm2 logs` or backend terminal

### App Can't Connect
1. **Check network**: Make sure device has internet
2. **Check backend URL**: Verify `44.204.184.21:4000` is correct
3. **Check app logs**: Look for connection errors
4. **Test manually**: Try `curl` from device (if possible)

### AI Endpoints Not Working
1. **Check backend logs**: Look for AI service errors
2. **Check environment variables**: Make sure GitHub token is set
3. **Check MongoDB connection**: Verify database connectivity
4. **Restart backend**: `pm2 restart lvl-up-backend`

## 📊 Expected Behavior

### When Working Correctly:
- ✅ App connects to EC2 backend automatically
- ✅ 96 pending proposals are loaded
- ✅ AI learning endpoints respond
- ✅ Socket.IO connects for real-time updates
- ✅ Proposals can be approved and processed
- ✅ AIs can improve code and push to Git

### Log Messages to Look For:
```
[NETWORK] ✅ Using backend: http://44.204.184.21:4000
[PROPOSAL_PROVIDER] ✅ Connected to backend
[AI-AUTO] Found 96 pending proposals that need user approval
```

## 🎉 Success Indicators

Your setup is working when:
1. **App launches** without connection errors
2. **Proposals load** from the backend
3. **AI endpoints respond** to requests
4. **Learning system** can trigger improvements
5. **Git integration** works for code pushes

## 📞 Next Steps

1. **Deploy backend** to EC2 using the scripts
2. **Test connectivity** from your Android device
3. **Approve some proposals** to see the AIs in action
4. **Trigger learning** to see cross-AI knowledge sharing
5. **Monitor the system** as it improves your app

---

**Your app will now work completely independently without needing your PC!** 🚀 