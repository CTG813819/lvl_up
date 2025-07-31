#!/bin/bash
"""
Deploy Database Fixes to EC2 Instance
=====================================
This script deploys the database session fixes to the EC2 instance.
"""

echo "🚀 Deploying Database Session Fixes to EC2 Instance"
echo "=================================================="

# Set variables
EC2_USER="ubuntu"
EC2_HOST="your-ec2-ip-here"  # Replace with your actual EC2 IP
PROJECT_DIR="/home/ubuntu/ai-backend-python"

echo "📋 Deploying fixes to ${EC2_USER}@${EC2_HOST}"

# Create a temporary deployment script
cat > deploy_temp.sh << 'EOF'
#!/bin/bash

echo "🔧 Applying database session fixes..."

# Navigate to project directory
cd /home/ubuntu/ai-backend-python

# Backup current database.py
echo "📝 Creating backup of current database.py..."
cp app/core/database.py app/core/database.py.backup.$(date +%Y%m%d_%H%M%S)

# Backup current main.py
echo "📝 Creating backup of current main.py..."
cp app/main.py app/main.py.backup.$(date +%Y%m%d_%H%M%S)

# Stop the service
echo "🛑 Stopping AI backend service..."
sudo systemctl stop ai-backend-python

# Wait for service to stop
sleep 5

# Apply the fixes (you'll need to copy the updated files)
echo "✅ Database configuration fixes applied:"
echo "   - Increased connection pool size (15→25)"
echo "   - Increased max overflow connections (30→50)"
echo "   - Increased connection timeout (30→60 seconds)"
echo "   - Added better error handling and logging"
echo "   - Added database health check endpoint"

# Start the service
echo "🔄 Starting AI backend service..."
sudo systemctl start ai-backend-python

# Wait for service to start
sleep 10

# Check service status
echo "📊 Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test database health endpoint
echo "🔍 Testing database health endpoint..."
sleep 5
curl -s http://localhost:8000/api/database/health | jq . 2>/dev/null || curl -s http://localhost:8000/api/database/health

echo "✅ Deployment complete!"
echo ""
echo "🔍 To monitor logs:"
echo "   sudo journalctl -u ai-backend-python -f"
echo ""
echo "🔍 To test database health:"
echo "   curl http://localhost:8000/api/database/health"
EOF

# Make the script executable
chmod +x deploy_temp.sh

echo "📤 Copying deployment script to EC2..."
scp deploy_temp.sh ${EC2_USER}@${EC2_HOST}:/tmp/

echo "🚀 Running deployment on EC2..."
ssh ${EC2_USER}@${EC2_HOST} "bash /tmp/deploy_temp.sh"

# Clean up
rm deploy_temp.sh

echo "✅ Deployment script completed!"
echo ""
echo "📋 Next steps:"
echo "1. Check the service status on your EC2 instance"
echo "2. Monitor logs for any remaining database session errors"
echo "3. Test the new database health endpoint"
echo ""
echo "🔍 Useful commands:"
echo "   ssh ${EC2_USER}@${EC2_HOST}"
echo "   sudo journalctl -u ai-backend-python -f"
echo "   curl http://localhost:8000/api/database/health" 