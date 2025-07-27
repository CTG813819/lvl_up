#!/bin/bash

# Performance Optimization Deployment Script
# Deploys comprehensive performance fixes to EC2 instance

set -e

# Configuration
EC2_HOST="ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
PEM_FILE="C:/projects/lvl_up/New.pem"
REMOTE_PATH="/home/ubuntu/ai-backend-python"
LOCAL_PATH="./ai-backend-python"

echo "🚀 Starting Performance Optimization Deployment"
echo "================================================"
echo "EC2 Host: $EC2_HOST"
echo "Remote Path: $REMOTE_PATH"
echo "Local Path: $LOCAL_PATH"
echo ""

# Function to run remote command
run_remote() {
    echo "🔧 Running: $1"
    ssh -i "$PEM_FILE" "$EC2_HOST" "$1"
}

# Function to copy file
copy_file() {
    echo "📁 Copying: $1 -> $2"
    scp -i "$PEM_FILE" "$1" "$EC2_HOST:$2"
}

# 1. Create logs directory on remote
echo "📂 Creating remote directories..."
run_remote "mkdir -p $REMOTE_PATH/logs"
run_remote "mkdir -p $REMOTE_PATH/cache"

# 2. Copy optimization script
echo "📋 Copying optimization script..."
copy_file "$LOCAL_PATH/optimize_backend_performance_comprehensive.py" "$REMOTE_PATH/"

# 3. Make script executable
echo "🔧 Making script executable..."
run_remote "chmod +x $REMOTE_PATH/optimize_backend_performance_comprehensive.py"

# 4. Install required dependencies
echo "📦 Installing dependencies..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && pip install psutil"

# 5. Stop current services
echo "⏹️  Stopping current services..."
run_remote "sudo systemctl stop guardian-ai.service || true"
run_remote "sudo systemctl stop ai-backend-optimized.service || true"
run_remote "sudo systemctl stop main.service || true"

# 6. Run optimization script
echo "⚡ Running performance optimization..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && python optimize_backend_performance_comprehensive.py"

# 7. Wait for optimization to complete
echo "⏳ Waiting for optimization to complete..."
sleep 30

# 8. Check service status
echo "🔍 Checking service status..."
run_remote "sudo systemctl status ai-backend-optimized.service || echo 'Service not found'"
run_remote "sudo systemctl status guardian-ai.service || echo 'Service not found'"
run_remote "sudo systemctl status postgresql || echo 'PostgreSQL not found'"

# 9. Test backend connectivity
echo "🧪 Testing backend connectivity..."
run_remote "curl -f http://localhost:4000/health || echo 'Backend not responding'"
run_remote "curl -f http://localhost:4000/api/health || echo 'API not responding'"

# 10. Show performance metrics
echo "📊 Performance metrics:"
run_remote "ps aux | grep python | grep -v grep || echo 'No Python processes found'"
run_remote "free -h"
run_remote "df -h"

# 11. Show recent logs
echo "📝 Recent logs:"
run_remote "tail -20 $REMOTE_PATH/logs/performance_optimization.log || echo 'No optimization logs found'"
run_remote "journalctl -u ai-backend-optimized.service --no-pager -n 20 || echo 'No service logs found'"

echo ""
echo "✅ Performance Optimization Deployment Complete!"
echo "================================================"
echo ""
echo "🔗 Backend URL: http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"
echo "📊 Health Check: http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/health"
echo ""
echo "📋 Next Steps:"
echo "1. Test the backend endpoints"
echo "2. Monitor performance metrics"
echo "3. Check logs for any issues"
echo "4. Verify database connectivity"
echo ""
echo "📞 If issues persist, check:"
echo "- Service logs: journalctl -u ai-backend-optimized.service"
echo "- Performance logs: $REMOTE_PATH/logs/performance_optimization.log"
echo "- Database logs: journalctl -u postgresql" 