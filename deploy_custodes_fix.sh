#!/bin/bash
<<<<<<< HEAD

# Deploy Custodes and Timeout Fix
# This script runs the fixed version of the custodes and timeout fix

set -e

echo "🚀 Deploying Custodes and Timeout Fix..."
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "fix_custodes_and_timeouts_fixed.py" ]; then
    echo "❌ Error: fix_custodes_and_timeouts_fixed.py not found in current directory"
    echo "Please run this script from the ai-backend-python directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed"
    exit 1
fi

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️ Warning: Backend does not appear to be running on port 8000"
    echo "The fix script will attempt to start it if needed"
fi

# Run the fixed script
echo "🔧 Running Custodes and Timeout Fix..."
python3 fix_custodes_and_timeouts_fixed.py

# Check if the script completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Custodes and Timeout Fix completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Check the test results above"
    echo "2. If a service was created, you can enable it with:"
    echo "   systemctl --user enable custodes-scheduler.service"
    echo "   systemctl --user start custodes-scheduler.service"
    echo "3. Monitor the scheduler with:"
    echo "   journalctl --user -u custodes-scheduler.service -f"
    echo "4. Or run the scheduler manually with:"
    echo "   python3 custodes_scheduler.py"
else
    echo ""
    echo "❌ Custodes and Timeout Fix failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi 
=======
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
>>>>>>> d1b3e6353067c4166fd183c12c225678794528f5
