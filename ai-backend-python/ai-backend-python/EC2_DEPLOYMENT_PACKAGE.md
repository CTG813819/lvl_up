# EC2 Deployment Package for Autonomous Subject Learning

## 🚀 Quick Start

This package contains everything needed to deploy enhanced subject learning features to your EC2 instance, enabling AIs to learn autonomously and grow intuitively.

## 📦 Files Included

### Core Services
1. **`autonomous_subject_learning_service.py`** - Main autonomous learning service
2. **`enhanced_subject_learning_service.py`** - Enhanced subject learning with internet research
3. **`ai_learning_cycle_enhancement.py`** - AI learning cycle integration

### Database Models
4. **`sql_models.py`** - Updated SQLAlchemy models with subject fields
5. **`training_data.py`** - Training data model with subject support
6. **`oath_paper.py`** - Oath paper model with subject integration

### API Routers
7. **`oath_papers.py`** - Enhanced oath papers router with subject endpoints
8. **`training_data.py`** - Enhanced training data router with subject support

### Migration & Setup
9. **`add_subject_fields_migration.py`** - Database migration script
10. **`deploy_subject_learning_features.sh`** - Linux deployment script
11. **`deploy_to_ec2_windows.bat`** - Windows deployment script

### Documentation
12. **`ENHANCED_SUBJECT_LEARNING_FEATURES.md`** - Feature documentation
13. **`EC2_AUTONOMOUS_LEARNING_DEPLOYMENT.md`** - EC2 deployment guide
14. **`EC2_DEPLOYMENT_PACKAGE.md`** - This file

## 🛠️ Manual Deployment Steps

### Step 1: Prepare Your EC2 Instance

```bash
# Connect to your EC2 instance
ssh -i "C:\projects\lvl_up\New.pem" ubuntu@YOUR_EC2_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv -y
```

### Step 2: Set Up Project Directory

```bash
# Create project directory
mkdir -p /home/ubuntu/ai-backend-python/app/{services,models,routers}
cd /home/ubuntu/ai-backend-python

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Copy Files to EC2

From your local machine, copy the files:

```bash
# Copy core services
scp -i "C:\projects\lvl_up\New.pem" autonomous_subject_learning_service.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/services/enhanced_subject_learning_service.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/services/

# Copy models
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/models/sql_models.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/models/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/models/training_data.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/models/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/models/oath_paper.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/models/

# Copy routers
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/routers/oath_papers.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/routers/
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/app/routers/training_data.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/app/routers/

# Copy migration script
scp -i "C:\projects\lvl_up\New.pem" ai-backend-python/add_subject_fields_migration.py ubuntu@YOUR_EC2_IP:/home/ubuntu/ai-backend-python/
```

### Step 4: Install Dependencies

```bash
# On EC2 instance
cd /home/ubuntu/ai-backend-python
source venv/bin/activate

# Install required packages
pip install aiohttp schedule structlog sqlalchemy fastapi
```

### Step 5: Set Environment Variables

```bash
# Edit bashrc
nano ~/.bashrc

# Add these lines (replace with your actual API keys):
export OPENAI_API_KEY="your_actual_openai_api_key"
export ANTHROPIC_API_KEY="your_actual_anthropic_api_key"
export GOOGLE_SEARCH_API_KEY="your_actual_google_search_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_actual_search_engine_id"

# Reload environment
source ~/.bashrc
```

### Step 6: Run Database Migration

```bash
# Run migration
python add_subject_fields_migration.py
```

### Step 7: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/autonomous-learning.service
```

Add this content:

```ini
[Unit]
Description=Autonomous Subject Learning Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python autonomous_subject_learning_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 8: Start the Service

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable autonomous-learning.service
sudo systemctl start autonomous-learning.service

# Check status
sudo systemctl status autonomous-learning.service
```

### Step 9: Set Up Monitoring

```bash
# Create monitoring script
cat > /home/ubuntu/ai-backend-python/monitor_enhanced_learning.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import json
from datetime import datetime, timedelta
from app.core.database import get_session
from app.models.sql_models import OathPaper, TrainingData, AgentMetrics
from sqlalchemy import select

async def monitor_enhanced_learning():
    try:
        session = get_session()
        async with session as s:
            recent_oath_papers = await s.execute(
                select(OathPaper)
                .where(OathPaper.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(OathPaper.created_at.desc())
                .limit(10)
            )
            oath_papers = recent_oath_papers.scalars().all()
            
            ai_metrics = await s.execute(select(AgentMetrics))
            metrics = ai_metrics.scalars().all()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "oath_papers_last_24h": len(oath_papers),
                "ai_metrics": [
                    {
                        "agent_type": m.agent_type,
                        "learning_score": m.learning_score,
                        "level": m.level,
                        "prestige": m.prestige
                    }
                    for m in metrics
                ]
            }
            print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"Error monitoring: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_enhanced_learning())
EOF

# Set up cron job for monitoring
echo "*/30 * * * * cd /home/ubuntu/ai-backend-python && python monitor_enhanced_learning.py >> /var/log/enhanced-learning.log 2>&1" | crontab -
```

## 🎯 What This Enables

### 🤖 Autonomous AI Learning
- **Every 2 Hours**: AIs automatically learn 3 new subjects
- **Daily Cycles**: Comprehensive learning at 5:00 AM, 12:00 PM, 5:00 PM
- **Subject-Specific**: Each AI learns subjects relevant to their domain
- **Intuitive Growth**: AIs level up and gain prestige automatically

### 📚 Enhanced Learning Capabilities
- **Internet Research**: Real-time knowledge gathering
- **AI Synthesis**: OpenAI and Anthropic enhance knowledge
- **Code Examples**: Practical implementations
- **Best Practices**: Industry standards and pitfalls
- **Learning Paths**: Structured progression

### 🔄 Cross-AI Collaboration
- **Knowledge Sharing**: Subjects shared across all AIs
- **Relevance Scoring**: Each AI gets relevant knowledge
- **Collaborative Growth**: AIs learn from each other

## 📊 Monitoring Commands

```bash
# Check service status
sudo systemctl status autonomous-learning.service

# View real-time logs
sudo journalctl -u autonomous-learning.service -f

# Check learning progress
cd /home/ubuntu/ai-backend-python
python monitor_enhanced_learning.py

# View enhanced learning logs
tail -f /var/log/enhanced-learning.log
```

## 🔧 Troubleshooting

### Service Issues
```bash
# Check logs
sudo journalctl -u autonomous-learning.service -n 50

# Restart service
sudo systemctl restart autonomous-learning.service

# Check dependencies
pip list | grep -E "(aiohttp|schedule|structlog)"
```

### API Key Issues
```bash
# Test environment variables
env | grep -E "(OPENAI|ANTHROPIC|GOOGLE)"

# Reload environment
source ~/.bashrc
```

### Database Issues
```bash
# Test database connection
python -c "from app.core.database import get_session; print('DB OK')"

# Run migration check
python add_subject_fields_migration.py --check
```

## 🎉 Success Indicators

After successful deployment, you should see:

1. **Service Running**: `systemctl status autonomous-learning.service` shows "active (running)"
2. **Learning Activity**: Logs show learning cycles every 2 hours
3. **AI Growth**: Monitoring shows increasing learning scores and levels
4. **Knowledge Accumulation**: Growing number of oath papers and training data

## 📞 Support

If you encounter issues:

1. **Check Logs**: `sudo journalctl -u autonomous-learning.service -f`
2. **Verify API Keys**: Ensure all environment variables are set
3. **Test Connectivity**: Verify internet access and API endpoints
4. **Check Dependencies**: Ensure all Python packages are installed

The AIs will now learn autonomously and grow intuitively, continuously expanding their knowledge base! 🚀 