# Production Deployment Guide - AI Internet Learning System

## 🚀 Quick Start Deployment

This guide will help you deploy the AI Internet Learning System to production in minutes using our automated CI/CD pipeline.

## 📋 Prerequisites

### Required Accounts & Services
- [ ] GitHub account with repository access
- [ ] MongoDB Atlas account (or local MongoDB)
- [ ] AWS account (for hosting)
- [ ] Google Cloud account (for Play Store deployment)
- [ ] Buddy.works account (optional, for enhanced CI/CD)

### Required Environment Variables
```env
# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=username/repository_name
GITHUB_USER=your_github_username
GITHUB_EMAIL=your_github_email

# Database
MONGODB_URI=mongodb://localhost:27017/ai_learning_system
# OR for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_learning_system

# API Configuration
API_BASE_URL=https://your-api-domain.com
PORT=3000
NODE_ENV=production

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Optional: Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url

# Optional: Google Play Store
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY=your_service_account_json
GOOGLE_CLOUD_PROJECT=your_project_id
```

## 🔧 Step 1: Repository Setup

### 1.1 Create GitHub Repository
```bash
# Create a new repository on GitHub
# Name: ai-learning-system
# Description: AI Internet Learning System
# Visibility: Public (recommended) or Private
```

### 1.2 Clone and Push Code
```bash
# Clone your repository
git clone https://github.com/yourusername/ai-learning-system.git
cd ai-learning-system

# Copy all project files to the repository
# (Your current project files)

# Add and commit files
git add .
git commit -m "Initial commit: AI Internet Learning System"

# Push to GitHub
git push origin main
```

## 🔧 Step 2: GitHub Secrets Configuration

### 2.1 Access Repository Settings
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

```bash
# Required Secrets
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_learning_system
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=yourusername/ai-learning-system
GITHUB_USER=your_github_username
GITHUB_EMAIL=your_github_email

# Optional Secrets
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
API_BASE_URL=https://your-api-domain.com
```

### 2.2 Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with permissions:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org` (Full control of organizations and teams)

## 🔧 Step 3: MongoDB Setup

### 3.1 MongoDB Atlas (Recommended)
1. Create MongoDB Atlas account
2. Create new cluster
3. Create database user
4. Get connection string
5. Add to GitHub secrets

### 3.2 Local MongoDB (Alternative)
```bash
# Install MongoDB locally
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Start MongoDB
sudo systemctl start mongod
# OR
brew services start mongodb-community
```

## 🔧 Step 4: Backend Deployment

### 4.1 AWS EC2 Setup (Recommended)
```bash
# Launch EC2 instance
# Instance Type: t3.medium or larger
# OS: Ubuntu 20.04 LTS
# Security Group: Allow ports 22, 80, 443, 3000

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2

# Install MongoDB (if not using Atlas)
sudo apt-get install -y mongodb

# Clone repository
git clone https://github.com/yourusername/ai-learning-system.git
cd ai-learning-system/ai-backend

# Install dependencies
npm ci

# Create .env file
nano .env
# Add your environment variables

# Start application with PM2
pm2 start src/index.js --name "ai-learning-backend"
pm2 startup
pm2 save
```

### 4.2 Environment Variables for Backend
Create `.env` file in `ai-backend/` directory:
```env
# Server Configuration
PORT=3000
NODE_ENV=production

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_learning_system

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=yourusername/ai-learning-system
GITHUB_USER=your_github_username
GITHUB_EMAIL=your_github_email

# Security
JWT_SECRET=your_jwt_secret_key
ENCRYPTION_KEY=your_encryption_key

# Optional: Slack Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

## 🔧 Step 5: CI/CD Pipeline Activation

### 5.1 GitHub Actions
The CI/CD pipeline will automatically activate when you push to the `main` branch:

```bash
# Push a change to trigger the pipeline
git add .
git commit -m "Trigger CI/CD pipeline"
git push origin main
```

### 5.2 Monitor Pipeline
1. Go to your GitHub repository
2. Click **Actions** tab
3. Monitor the pipeline progress:
   - Backend testing and building
   - Flutter testing and APK building
   - Security scanning
   - Production deployment

### 5.3 Manual Pipeline Trigger
You can also trigger the pipeline manually:
1. Go to **Actions** → **AI Learning System CI/CD Pipeline**
2. Click **Run workflow**
3. Select environment (staging/production)
4. Click **Run workflow**

## 🔧 Step 6: Flutter App Deployment

### 6.1 Build APK Locally (Optional)
```bash
# Navigate to project root
cd ai-learning-system

# Get Flutter dependencies
flutter pub get

# Build APK
flutter build apk --release

# Build App Bundle (for Play Store)
flutter build appbundle --release
```

### 6.2 Google Play Store Deployment
1. Create Google Play Console account
2. Create new app
3. Upload APK/AAB file
4. Configure app details
5. Submit for review

### 6.3 Automated Play Store Deployment
Add to GitHub secrets:
```bash
GOOGLE_PLAY_SERVICE_ACCOUNT_KEY=your_service_account_json
GOOGLE_CLOUD_PROJECT=your_project_id
```

## 🔧 Step 7: Domain & SSL Setup

### 7.1 Domain Configuration
```bash
# Point your domain to your server IP
# A record: your-domain.com → your-server-ip
# CNAME: www.your-domain.com → your-domain.com
```

### 7.2 SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7.3 Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔧 Step 8: Monitoring & Maintenance

### 8.1 System Monitoring
```bash
# Check application status
pm2 status
pm2 logs ai-learning-backend

# Monitor system resources
htop
df -h
free -h

# Check MongoDB status
sudo systemctl status mongod
```

### 8.2 Automated Backups
```bash
# Create backup script
nano /home/ubuntu/backup.sh

#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --uri="your_mongodb_uri" --out="$BACKUP_DIR/mongodb_$DATE"

# Backup application files
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" /home/ubuntu/ai-learning-system

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -mtime +7 -delete

# Add to crontab
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh
```

### 8.3 Log Rotation
```bash
# Configure log rotation for PM2
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

## 🔧 Step 9: Testing Production Deployment

### 9.1 API Testing
```bash
# Test backend API
curl https://your-domain.com/api/health
curl https://your-domain.com/api/proposals/status

# Test AI learning system
curl -X POST https://your-domain.com/api/proposals/trigger-learning \
  -H "Content-Type: application/json" \
  -d '{"aiType": "Imperium", "proposalId": "test", "result": "passed"}'
```

### 9.2 Mobile App Testing
1. Install APK on test device
2. Test all features:
   - AI Learning Dashboard
   - Terminal Interface
   - Approval Workflow
   - Notifications

### 9.3 CI/CD Pipeline Testing
1. Make a small change to code
2. Push to GitHub
3. Monitor pipeline execution
4. Verify deployment

## 🔧 Step 10: Performance Optimization

### 10.1 Database Optimization
```javascript
// Add indexes to MongoDB collections
db.proposals.createIndex({ "aiType": 1, "createdAt": -1 })
db.learningCycles.createIndex({ "aiType": 1, "status": 1 })
db.approvals.createIndex({ "status": 1, "createdAt": -1 })
```

### 10.2 Caching
```bash
# Install Redis
sudo apt-get install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set maxmemory and maxmemory-policy

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 10.3 Load Balancing
```bash
# Install HAProxy
sudo apt-get install haproxy

# Configure load balancer
sudo nano /etc/haproxy/haproxy.cfg
# Add backend servers and load balancing rules
```

## 🚨 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check connection string
echo $MONGODB_URI

# Test connection
mongo "your_mongodb_uri"
```

#### 2. GitHub Integration Issues
```bash
# Verify GitHub token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Check repository access
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO
```

#### 3. PM2 Process Issues
```bash
# Restart application
pm2 restart ai-learning-backend

# Check logs
pm2 logs ai-learning-backend --lines 100

# Reset PM2
pm2 delete all
pm2 start src/index.js --name "ai-learning-backend"
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

## 📞 Support

### Getting Help
- **Documentation**: Check `SYSTEM_SUMMARY.md` for system overview
- **Issues**: Create GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact support@ai-learning-system.com

### Emergency Contacts
- **System Admin**: admin@your-domain.com
- **DevOps**: devops@your-domain.com
- **Security**: security@your-domain.com

---

## ✅ Deployment Checklist

- [ ] GitHub repository created and configured
- [ ] Environment variables set in GitHub secrets
- [ ] MongoDB database configured and accessible
- [ ] Backend deployed and running on server
- [ ] Domain configured and SSL certificate installed
- [ ] CI/CD pipeline tested and working
- [ ] Mobile app built and tested
- [ ] Monitoring and backup systems configured
- [ ] Performance optimization completed
- [ ] Security audit performed

**🎉 Congratulations! Your AI Internet Learning System is now deployed to production!**

The system will automatically:
- Monitor AI learning activities
- Generate and apply code improvements
- Create GitHub pull requests
- Build and deploy APK updates
- Provide real-time analytics and monitoring

Your autonomous development system is ready to continuously improve your applications! 