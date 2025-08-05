# Manual Migration Guide: JavaScript to Python Backend

This guide provides step-by-step instructions to manually migrate from your JavaScript backend to the new Python backend with scikit-learn integration.

## Prerequisites

- SSH access to your EC2 instance
- Your EC2 IP address
- SSH private key file
- Basic knowledge of Linux commands

## Step 1: Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## Step 2: Stop JavaScript Backend Services

```bash
# Stop systemd services
sudo systemctl stop ai-backend
sudo systemctl stop pm2

# Kill any running Node.js processes
pkill -f 'node.*ai-backend'
pkill -f 'pm2'
```

## Step 3: Create Backup

```bash
# Create backup directory with timestamp
BACKUP_DIR="/home/ubuntu/backup-js-backend-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Copy JavaScript backend files
cp -r /home/ubuntu/ai-backend/* $BACKUP_DIR/
echo "Backup created at: $BACKUP_DIR"
```

## Step 4: Remove JavaScript Files

```bash
# Remove JavaScript backend directory
rm -rf /home/ubuntu/ai-backend

# Remove Node.js related files
rm -rf /home/ubuntu/node_modules
rm -f /home/ubuntu/package*.json
rm -f /home/ubuntu/.env

# Clean up system services
sudo systemctl disable ai-backend
sudo rm -f /etc/systemd/system/ai-backend.service
sudo systemctl daemon-reload
```

## Step 5: Install Python Dependencies

```bash
# Update package list
sudo apt-get update

# Install Python and build tools
sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential
sudo apt-get install -y curl wget git
```

## Step 6: Create Python Virtual Environment

```bash
cd /home/ubuntu
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

## Step 7: Upload Python Backend Files

From your local machine, upload the Python backend files:

```bash
# From your local machine
scp -i your-key.pem -r ai-backend-python/ ubuntu@your-ec2-ip:/home/ubuntu/
```

## Step 8: Install Python Requirements

```bash
# On EC2 instance
cd /home/ubuntu/ai-backend-python
source /home/ubuntu/venv/bin/activate
pip install -r requirements.txt
```

## Step 9: Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"
```

## Step 10: Create Directories

```bash
mkdir -p models
mkdir -p uploads
mkdir -p temp
```

## Step 11: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add the following content (replace with your actual values):

```env
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=ai_backend_python

# Server
PORT=4000
HOST=0.0.0.0
DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_repo_here

# AWS
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# AI Learning
LEARNING_ENABLED=true
LEARNING_INTERVAL=300
MAX_LEARNING_HISTORY=1000

# Proposal settings
MAX_PROPOSAL_LENGTH=10000
PROPOSAL_TIMEOUT=300
```

## Step 12: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/ai-backend-python.service
```

Add the following content:

```ini
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/venv/bin
ExecStart=/home/ubuntu/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Step 13: Enable and Start Service

```bash
# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python

# Start the service
sudo systemctl start ai-backend-python

# Check status
sudo systemctl status ai-backend-python
```

## Step 14: Configure Firewall

```bash
# Allow port 4000
sudo ufw allow 4000/tcp
```

## Step 15: Test the Backend

```bash
# Test health endpoint
curl http://localhost:4000/health

# Test from external
curl http://your-ec2-ip:4000/health
```

## Step 16: View Logs

```bash
# View service logs
sudo journalctl -u ai-backend-python -f

# View recent logs
sudo journalctl -u ai-backend-python --since "1 hour ago"
```

## Step 17: Verify Migration

```bash
# Check if service is running
sudo systemctl is-active ai-backend-python

# Check if port is listening
netstat -tlnp | grep :4000

# Test API endpoints
curl http://localhost:4000/api/health
curl http://localhost:4000/debug
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status ai-backend-python

# View detailed logs
sudo journalctl -u ai-backend-python -n 50

# Check if Python dependencies are installed
source /home/ubuntu/venv/bin/activate
python -c "import fastapi, uvicorn, motor"
```

### Port Already in Use

```bash
# Check what's using port 4000
sudo netstat -tlnp | grep :4000

# Kill process if needed
sudo pkill -f uvicorn
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/ai-backend-python

# Fix permissions
chmod +x /home/ubuntu/ai-backend-python/start.py
```

### Database Connection Issues

```bash
# Check MongoDB status
sudo systemctl status mongod

# Test MongoDB connection
mongo --eval "db.runCommand('ping')"
```

## Rollback Instructions

If you need to rollback to the JavaScript backend:

```bash
# Stop Python backend
sudo systemctl stop ai-backend-python
sudo systemctl disable ai-backend-python

# Remove Python backend
rm -rf /home/ubuntu/ai-backend-python

# Restore JavaScript backend
cp -r /home/ubuntu/backup-js-backend-YYYYMMDD_HHMMSS /home/ubuntu/ai-backend

# Reinstall Node.js dependencies
cd /home/ubuntu/ai-backend
npm install

# Restart JavaScript backend
sudo systemctl start ai-backend
```

## Post-Migration Tasks

1. **Update Frontend Configuration**: Update your frontend to point to the new Python backend
2. **Test All Features**: Verify all functionality works with the new backend
3. **Monitor Performance**: Check logs and performance metrics
4. **Train ML Models**: Run initial ML model training with existing data
5. **Update Documentation**: Update any documentation referencing the old backend

## Support

If you encounter issues during migration:

1. Check the logs: `sudo journalctl -u ai-backend-python -f`
2. Verify configuration: Check the `.env` file
3. Test connectivity: Ensure all services are running
4. Review this guide: Double-check all steps were completed

## Migration Complete!

Your JavaScript backend has been successfully migrated to Python with scikit-learn integration. The new backend provides:

- ✅ Advanced machine learning capabilities
- ✅ Better performance with FastAPI
- ✅ Improved type safety with Pydantic
- ✅ Enhanced logging and monitoring
- ✅ Continuous learning from user feedback 