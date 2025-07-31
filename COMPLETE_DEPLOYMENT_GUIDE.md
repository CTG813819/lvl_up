# Complete AI System Deployment Guide

## Overview

This guide will help you deploy the complete AI system to your EC2 instance. The system includes:

- **Conquest AI**: Creates new app repositories and APKs based on user suggestions
- **Autonomous AI Agents**: Imperium, Guardian, Sandbox, and Conquest agents
- **AI Growth System**: Uses scikit-learn for autonomous improvement
- **GitHub Integration**: Webhooks and repository management
- **Background Services**: Autonomous cycles and monitoring

## Prerequisites

### 1. EC2 Instance Setup
- Ubuntu 20.04+ EC2 instance running
- Security group allows SSH (port 22) and HTTP (port 4000)
- At least 2GB RAM and 20GB storage

### 2. Local Setup
- Windows machine with PowerShell
- SSH key file (`lvl_up_key.pem`) in your project directory
- Git installed locally

### 3. Environment Variables
Set your EC2 IP address:
```powershell
$env:EC2_IP="your-ec2-ip-address"
```

## Step-by-Step Deployment

### Step 1: Initial EC2 Setup (First Time Only)

If this is your first deployment, run these commands on your EC2 instance:

```bash
# Connect to EC2
ssh -i lvl_up_key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Create project directory
mkdir -p /home/ubuntu/lvl_up
cd /home/ubuntu/lvl_up

# Clone your repository (if using Git)
# git clone https://github.com/your-username/lvl_up.git .

# Or create the directory structure manually
mkdir -p ai-backend-python/app/{core,models,routers,services}
```

### Step 2: Database Setup

```bash
# Install PostgreSQL (if using NeonDB, skip this)
sudo apt install postgresql postgresql-contrib -y

# Or use SQLite for development
sudo apt install sqlite3 -y
```

### Step 3: Python Environment Setup

```bash
# Create virtual environment
cd /home/ubuntu/lvl_up/ai-backend-python
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install fastapi uvicorn sqlalchemy asyncpg structlog aiohttp scikit-learn joblib
```

### Step 4: Systemd Service Setup

Create the systemd service file:

```bash
sudo nano /etc/systemd/system/ai-backend-python.service
```

Add this content:

```ini
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lvl_up/ai-backend-python
Environment=PATH=/home/ubuntu/lvl_up/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/lvl_up/ai-backend-python/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-backend-python
sudo systemctl start ai-backend-python
```

### Step 5: Deploy Complete AI System

Now run the deployment script from your local machine:

```powershell
# Set your EC2 IP
$env:EC2_IP="your-ec2-ip-address"

# Run the deployment script
.\deploy-complete-ai-system.bat
```

### Step 6: Verify Deployment

Check that all services are running:

```bash
# Check service status
sudo systemctl status ai-backend-python

# Check logs
sudo journalctl -u ai-backend-python -f

# Test endpoints
curl http://localhost:4000/health
curl http://localhost:4000/api/conquest/status
curl http://localhost:4000/api/growth/status
```

## Testing the Complete System

### 1. Test Conquest AI - App Creation

Create a new app:

```bash
curl -X POST http://your-ec2-ip:4000/api/conquest/create-app \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fitness Tracker Pro",
    "description": "A comprehensive fitness tracking app with social features",
    "keywords": ["fitness", "social", "tracking", "workout"],
    "app_type": "fitness",
    "features": ["workout_tracking", "social_sharing", "progress_charts"]
  }'
```

### 2. Test AI Agents

Run all AI agents:

```bash
curl -X POST http://your-ec2-ip:4000/api/agents/run/all
```

### 3. Test AI Growth System

Check growth status:

```bash
curl http://your-ec2-ip:4000/api/growth/status
```

Trigger auto-improvement:

```bash
curl -X POST http://your-ec2-ip:4000/api/growth/auto-improve
```

### 4. Test GitHub Integration

Check GitHub status:

```bash
curl http://your-ec2-ip:4000/api/github/status
```

## Configuration

### Environment Variables

Set these environment variables on your EC2 instance:

```bash
# Database
export DATABASE_URL="your-database-url"

# GitHub
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPO="your-username/your-repo"

# AI Configuration
export AI_LEARNING_ENABLED="true"
export AUTONOMOUS_CYCLES_ENABLED="true"
export CONQUEST_AI_ENABLED="true"
```

### GitHub Webhook Setup

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add webhook:
   - Payload URL: `http://your-ec2-ip:4000/api/github/webhook`
   - Content type: `application/json`
   - Events: Select all events or specific ones

## Monitoring and Maintenance

### 1. View Logs

```bash
# Service logs
sudo journalctl -u ai-backend-python -f

# Application logs
tail -f /home/ubuntu/lvl_up/ai-backend-python/logs/app.log
```

### 2. Check System Status

```bash
# Health check
curl http://your-ec2-ip:4000/health

# Debug information
curl http://your-ec2-ip:4000/debug

# App status
curl http://your-ec2-ip:4000/api/app/status
```

### 3. Restart Services

```bash
# Restart backend
sudo systemctl restart ai-backend-python

# Check status
sudo systemctl status ai-backend-python
```

## Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u ai-backend-python -n 50
   
   # Check Python environment
   source /home/ubuntu/lvl_up/ai-backend-python/venv/bin/activate
   python main.py
   ```

2. **Database connection issues**
   ```bash
   # Test database connection
   python -c "from app.core.database import get_session; print('DB OK')"
   ```

3. **Port already in use**
   ```bash
   # Check what's using port 4000
   sudo netstat -tlnp | grep :4000
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

### Performance Optimization

1. **Increase system resources** if needed
2. **Monitor memory usage**: `htop`
3. **Check disk space**: `df -h`
4. **Monitor network**: `iftop`

## Security Considerations

1. **Firewall**: Configure security groups properly
2. **HTTPS**: Set up SSL/TLS for production
3. **Authentication**: Implement proper auth for production
4. **Secrets**: Use environment variables for sensitive data
5. **Updates**: Keep system and dependencies updated

## Backup and Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump your_database > backup.sql

# SQLite
cp database.db backup.db
```

### Code Backup

```bash
# Backup entire project
tar -czf lvl_up_backup_$(date +%Y%m%d).tar.gz /home/ubuntu/lvl_up/
```

## Scaling

For production scaling:

1. **Load Balancer**: Use AWS ALB
2. **Multiple Instances**: Deploy to multiple EC2 instances
3. **Database**: Use RDS or Aurora
4. **Caching**: Add Redis for caching
5. **Monitoring**: Use CloudWatch or similar

## Support

If you encounter issues:

1. Check the logs first
2. Review this documentation
3. Check the individual system guides:
   - `AI_GROWTH_SYSTEM_GUIDE.md`
   - `CONQUEST_AI_README.md`
   - `AUTONOMOUS_AI_SYSTEM.md`

## Next Steps

After successful deployment:

1. **Test all features** thoroughly
2. **Configure monitoring** and alerts
3. **Set up backups** and recovery procedures
4. **Plan for scaling** as usage grows
5. **Document any customizations** made

---

**Congratulations!** Your complete AI system is now deployed and ready to create apps, learn autonomously, and grow its capabilities. 