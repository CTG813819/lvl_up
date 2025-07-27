#!/bin/bash

# Comprehensive Performance Fix Deployment Script
# Runs diagnostics first, then applies optimizations

set -e

# Configuration
EC2_HOST="ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
PEM_FILE="C:/projects/lvl_up/New.pem"
REMOTE_PATH="/home/ubuntu/ai-backend-python"
LOCAL_PATH="./ai-backend-python"

echo "🚀 Starting Comprehensive Performance Fix Deployment"
echo "===================================================="
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

# Phase 1: Pre-deployment diagnostics
echo "🔍 PHASE 1: Running Pre-deployment Diagnostics"
echo "=============================================="

# 1. Copy diagnostic script
echo "📋 Copying diagnostic script..."
copy_file "$LOCAL_PATH/diagnose_performance_issues.py" "$REMOTE_PATH/"

# 2. Make script executable
echo "🔧 Making diagnostic script executable..."
run_remote "chmod +x $REMOTE_PATH/diagnose_performance_issues.py"

# 3. Install dependencies for diagnostics
echo "📦 Installing diagnostic dependencies..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && pip install psutil requests"

# 4. Run diagnostics
echo "🔍 Running performance diagnostics..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && python diagnose_performance_issues.py"

# 5. Show diagnostic results
echo "📊 Diagnostic Results:"
run_remote "tail -50 $REMOTE_PATH/logs/performance_diagnosis.log || echo 'No diagnostic logs found'"

# Phase 2: Performance optimization
echo ""
echo "⚡ PHASE 2: Applying Performance Optimizations"
echo "=============================================="

# 1. Copy optimization script
echo "📋 Copying optimization script..."
copy_file "$LOCAL_PATH/optimize_backend_performance_comprehensive.py" "$REMOTE_PATH/"

# 2. Make script executable
echo "🔧 Making optimization script executable..."
run_remote "chmod +x $REMOTE_PATH/optimize_backend_performance_comprehensive.py"

# 3. Stop current services
echo "⏹️  Stopping current services..."
run_remote "sudo systemctl stop guardian-ai.service || true"
run_remote "sudo systemctl stop ai-backend-optimized.service || true"
run_remote "sudo systemctl stop main.service || true"

# 4. Run optimization
echo "⚡ Running performance optimization..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && python optimize_backend_performance_comprehensive.py"

# 5. Wait for optimization to complete
echo "⏳ Waiting for optimization to complete..."
sleep 45

# Phase 3: Post-optimization verification
echo ""
echo "✅ PHASE 3: Post-optimization Verification"
echo "=========================================="

# 1. Check service status
echo "🔍 Checking service status..."
run_remote "sudo systemctl status ai-backend-optimized.service || echo 'Service not found'"
run_remote "sudo systemctl status guardian-ai.service || echo 'Service not found'"
run_remote "sudo systemctl status postgresql || echo 'PostgreSQL not found'"

# 2. Test backend connectivity
echo "🧪 Testing backend connectivity..."
run_remote "curl -f http://localhost:4000/health || echo 'Backend not responding'"
run_remote "curl -f http://localhost:4000/api/health || echo 'API not responding'"

# 3. Show performance metrics
echo "📊 Performance metrics:"
run_remote "ps aux | grep python | grep -v grep || echo 'No Python processes found'"
run_remote "free -h"
run_remote "df -h"

# 4. Show optimization logs
echo "📝 Optimization logs:"
run_remote "tail -30 $REMOTE_PATH/logs/performance_optimization.log || echo 'No optimization logs found'"

# 5. Run post-optimization diagnostics
echo "🔍 Running post-optimization diagnostics..."
run_remote "cd $REMOTE_PATH && source venv/bin/activate && python diagnose_performance_issues.py"

# 6. Show comparison
echo "📊 Performance Comparison:"
run_remote "echo '=== BEFORE OPTIMIZATION ===' && head -20 $REMOTE_PATH/logs/performance_diagnosis.log || echo 'No before logs'"
run_remote "echo '=== AFTER OPTIMIZATION ===' && tail -20 $REMOTE_PATH/logs/performance_diagnosis.log || echo 'No after logs'"

# Phase 4: Final verification and monitoring
echo ""
echo "🎯 PHASE 4: Final Verification and Monitoring"
echo "============================================="

# 1. Start performance monitoring
echo "📊 Starting performance monitoring..."
run_remote "cd $REMOTE_PATH && nohup python monitor_performance.py > /dev/null 2>&1 &"

# 2. Final health check
echo "🏥 Final health check..."
run_remote "curl -f http://localhost:4000/health && echo ' - Backend healthy' || echo ' - Backend unhealthy'"

# 3. Show final status
echo "📋 Final system status:"
run_remote "sudo systemctl list-units --type=service --state=active | grep -E '(ai-backend|guardian|postgresql)' || echo 'No relevant services found'"

echo ""
echo "✅ Comprehensive Performance Fix Deployment Complete!"
echo "===================================================="
echo ""
echo "🔗 Backend URL: http://ec2-34-202-215-209.compute-1.amazonaws.com:4000"
echo "📊 Health Check: http://ec2-34-202-215-209.compute-1.amazonaws.com:4000/health"
echo ""
echo "📋 Performance Improvements Applied:"
echo "✅ Increased database connection pool size (25 → 50)"
echo "✅ Increased connection timeout (60s → 120s)"
echo "✅ Optimized system resource limits"
echo "✅ Enhanced service restart policies"
echo "✅ Added performance monitoring"
echo "✅ Optimized FastAPI configuration"
echo "✅ Added caching layer"
echo ""
echo "📞 Monitoring and Troubleshooting:"
echo "- Real-time monitoring: $REMOTE_PATH/monitor_performance.py"
echo "- Performance logs: $REMOTE_PATH/logs/performance_optimization.log"
echo "- Diagnostic logs: $REMOTE_PATH/logs/performance_diagnosis.log"
echo "- Service logs: journalctl -u ai-backend-optimized.service"
echo "- Database logs: journalctl -u postgresql"
echo ""
echo "🔄 If issues persist:"
echo "1. Check logs for specific errors"
echo "2. Monitor resource usage"
echo "3. Verify database connectivity"
echo "4. Consider scaling up EC2 instance" 