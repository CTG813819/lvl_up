#!/bin/bash

echo "🚀 DEPLOYING GUNICORN WORKER FAILURE FIX"
echo "========================================="

# Step 1: Upload the fix scripts to EC2
echo "📤 Step 1: Uploading fix scripts to EC2..."

# Upload the fix scripts
scp -i "C:\projects\lvl_up\New.pem" \
    fix_gunicorn_worker_failure.sh \
    fix_database_connections.py \
    ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com:/home/ubuntu/ai-backend-python/

echo "✅ Scripts uploaded successfully"

# Step 2: Execute the fix on EC2
echo "🔧 Step 2: Executing fix on EC2..."

ssh -i "C:\projects\lvl_up\New.pem" ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com << 'EOF'

cd /home/ubuntu/ai-backend-python

echo "🔧 Running Gunicorn worker failure fix..."
chmod +x fix_gunicorn_worker_failure.sh
./fix_gunicorn_worker_failure.sh

echo "🔧 Running database connection fix..."
python3 fix_database_connections.py

echo "📋 Checking final status..."
sudo systemctl status ai-backend-python.service --no-pager

echo "📋 Recent logs:"
sudo journalctl -u ai-backend-python -n 10 --no-pager

echo "🏥 Testing health endpoint..."
curl -s http://localhost:8000/api/health || echo "Health endpoint not responding"

echo "📊 Process check:"
ps aux | grep -E "(uvicorn|python.*main)" | grep -v grep

EOF

echo "✅ Fix deployment completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Check the output above for any errors"
echo "   2. If successful, your server should be running on port 8000"
echo "   3. Test the health endpoint: http://ec2-34-202-215-209.compute-1.amazonaws.com:8000/api/health"
echo "   4. Monitor logs with: ssh -i 'C:\projects\lvl_up\New.pem' ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com 'sudo journalctl -u ai-backend-python -f'" 