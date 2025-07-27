#!/bin/bash

echo "🚀 Deploying comprehensive frontend-backend integration check to EC2..."

# Copy the comprehensive check script to EC2
echo "📤 Copying comprehensive check script to EC2..."
scp -i "lvl_up_key.pem" comprehensive_frontend_backend_check.py ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

# SSH into EC2 and run the comprehensive check
echo "🔍 Running comprehensive frontend-backend integration check on EC2..."
ssh -i "lvl_up_key.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com << 'EOF'

cd /home/ubuntu/ai-backend-python

echo "🔧 Fixing database issues first..."

# Check SQLAlchemy version and fix _static_cache_key issues
echo "📊 Checking SQLAlchemy version..."
python3 -c "import sqlalchemy; print(f'Current SQLAlchemy version: {sqlalchemy.__version__}')"

# Fix SQLAlchemy compatibility issues
echo "🔧 Fixing SQLAlchemy compatibility..."
pip3 install --upgrade "sqlalchemy>=2.0.0" --force-reinstall

# Check if there are any database schema issues
echo "🗄️ Checking database schema..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app.database import engine
    print('✅ Database engine import successful')
except Exception as e:
    print(f'❌ Database engine import error: {e}')
    if '_static_cache_key' in str(e):
        print('🔧 Detected _static_cache_key error - attempting fix...')
        import subprocess
        subprocess.run(['pip3', 'install', 'sqlalchemy==1.4.46', '--force-reinstall'])
        print('✅ SQLAlchemy downgraded to 1.4.46')
"

# Restart the backend service to apply fixes
echo "🔄 Restarting backend service..."
sudo systemctl restart ultimate_start

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check if service is running
echo "🔍 Checking service status..."
sudo systemctl status ultimate_start --no-pager

# Run the comprehensive frontend-backend check
echo "🎯 Running comprehensive frontend-backend integration check..."
python3 comprehensive_frontend_backend_check.py

# Display the results
echo "📄 Integration check results:"
if [ -f "frontend_backend_integration_report.json" ]; then
    cat frontend_backend_integration_report.json
else
    echo "❌ No integration report generated"
fi

# Check specific issues mentioned in logs
echo "🔍 Checking specific issues from logs..."

# Check proposals endpoint specifically
echo "📋 Testing proposals endpoint..."
curl -s http://localhost:8000/api/proposals/ | head -20

# Check custody endpoint specifically  
echo "🛡️ Testing custody endpoint..."
curl -s http://localhost:8000/api/custody/ | head -20

# Check database errors
echo "🗄️ Checking for database errors in logs..."
sudo journalctl -u ultimate_start --since "5 minutes ago" | grep -i "error\|exception" | tail -10

EOF

echo "✅ Comprehensive check completed on EC2"
echo "📄 Check the output above for integration status and any issues found" 