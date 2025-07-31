#!/bin/bash
# Deploy the fixed automatic custodes service to EC2

echo "🚀 Deploying fixed automatic custodes service..."

# Configuration
EC2_HOST="ubuntu@ec2-54-147-131-201.compute-1.amazonaws.com"
REMOTE_DIR="/home/ubuntu/ai-backend-python"
LOCAL_FILES=(
    "run_automatic_custodes_simple.py"
    "ai-backend-python/test_custody_endpoints.py"
)

# Copy the fixed files to EC2
echo "📁 Copying fixed files to EC2..."
for file in "${LOCAL_FILES[@]}"; do
    echo "   Copying $file..."
    scp -i ~/.ssh/aws-key.pem "$file" "$EC2_HOST:$REMOTE_DIR/"
done

# SSH into EC2 and restart the automatic custodes service
echo "🔧 Restarting automatic custodes service..."
ssh -i ~/.ssh/aws-key.pem "$EC2_HOST" << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    # Stop the current automatic custodes service
    echo "Stopping current automatic custodes service..."
    sudo systemctl stop automatic-custodes.service
    
    # Test the custody endpoints first
    echo "Testing custody endpoints..."
    python3 test_custody_endpoints.py
    
    # Start the fixed automatic custodes service
    echo "Starting fixed automatic custodes service..."
    sudo systemctl start automatic-custodes.service
    
    # Check service status
    echo "Checking service status..."
    sudo systemctl status automatic-custodes.service
    
    # Show recent logs
    echo "Recent logs:"
    sudo journalctl -u automatic-custodes.service -n 20 --no-pager
EOF

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Monitor the automatic custodes service logs:"
echo "   ssh -i ~/.ssh/aws-key.pem $EC2_HOST"
echo "   sudo journalctl -u automatic-custodes.service -f"
echo ""
echo "2. Check custody analytics:"
echo "   curl http://localhost:8000/api/custody/analytics"
echo ""
echo "3. Force test an AI manually:"
echo "   curl -X POST http://localhost:8000/api/custody/test/imperium/force" 