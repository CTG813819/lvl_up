#!/bin/bash

# Setup Autonomous Learning System on EC2
# Run this script on the EC2 instance after files have been transferred

set -e

echo "🚀 Setting up Autonomous Subject Learning System on EC2..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Navigate to project directory
cd ~/ai-backend-python

print_status "Step 1: Activating virtual environment..."
source venv/bin/activate

print_status "Step 2: Installing required dependencies..."
pip install aiohttp schedule structlog

print_status "Step 3: Running database migration..."
python add_subject_fields_migration.py

print_status "Step 4: Setting up environment variables..."
# Check if environment variables are already set
if ! grep -q "OPENAI_API_KEY" ~/.bashrc; then
    echo 'export OPENAI_API_KEY="your_openai_api_key"' >> ~/.bashrc
    echo 'export ANTHROPIC_API_KEY="your_anthropic_api_key"' >> ~/.bashrc
    echo 'export GOOGLE_SEARCH_API_KEY="your_google_search_api_key"' >> ~/.bashrc
    echo 'export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"' >> ~/.bashrc
    print_warning "Please update API keys in ~/.bashrc with your actual keys"
else
    print_success "Environment variables already configured"
fi

print_status "Step 5: Creating systemd service..."
cat > /tmp/autonomous-learning.service << 'EOF'
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
EOF

sudo mv /tmp/autonomous-learning.service /etc/systemd/system/
sudo systemctl daemon-reload

print_status "Step 6: Creating monitoring script..."
cat > monitor_enhanced_learning.py << 'EOF'
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

print_status "Step 7: Setting up monitoring cron job..."
echo "*/30 * * * * cd /home/ubuntu/ai-backend-python && python monitor_enhanced_learning.py >> /var/log/enhanced-learning.log 2>&1" | crontab -

print_status "Step 8: Enabling and starting autonomous learning service..."
sudo systemctl enable autonomous-learning.service
sudo systemctl start autonomous-learning.service

print_status "Step 9: Testing the service..."
sleep 5
if sudo systemctl is-active --quiet autonomous-learning.service; then
    print_success "Autonomous learning service is running!"
else
    print_error "Service failed to start. Check logs with: sudo journalctl -u autonomous-learning.service -f"
fi

print_status "Step 10: Testing monitoring script..."
python monitor_enhanced_learning.py

echo ""
print_success "🎉 Autonomous Subject Learning System Setup Complete!"
echo ""
echo "📋 System Status:"
echo "  ✅ Autonomous Learning Service: $(sudo systemctl is-active autonomous-learning.service)"
echo "  ✅ Monitoring: Every 30 minutes"
echo "  ✅ Database Migration: Complete"
echo "  ✅ Dependencies: Installed"
echo ""
echo "🔧 Management Commands:"
echo "  📊 Check Status: sudo systemctl status autonomous-learning.service"
echo "  📝 View Logs: sudo journalctl -u autonomous-learning.service -f"
echo "  🔄 Restart: sudo systemctl restart autonomous-learning.service"
echo "  📈 Monitor: python monitor_enhanced_learning.py"
echo "  📋 Learning Logs: tail -f /var/log/enhanced-learning.log"
echo ""
echo "🎯 What's Happening Now:"
echo "  🤖 AIs will learn autonomously every 2 hours"
echo "  🌅 Daily learning cycles at 5:00 AM, 12:00 PM, 5:00 PM"
echo "  📚 Subjects: Machine Learning, Cybersecurity, Web Dev, Trading, etc."
echo "  🔄 Cross-AI knowledge sharing enabled"
echo "  📈 Intuitive growth and leveling system active"
echo ""
print_warning "⚠️  IMPORTANT: Update your API keys in ~/.bashrc before the first learning cycle!"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY" 
echo "   - GOOGLE_SEARCH_API_KEY"
echo "   - GOOGLE_SEARCH_ENGINE_ID"
echo ""
print_success "🚀 Your AIs are now ready to learn autonomously and grow intuitively!" 