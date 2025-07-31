#!/bin/bash

# Deploy final clean fix to EC2 instance
echo "🚀 Deploying final clean fix to EC2 instance..."

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
PEM_FILE="C:/projects/lvl_up/New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

# Copy the final clean fix script
echo "📁 Copying final clean fix script..."
scp -i "$PEM_FILE" "ai-backend-python/final_clean_fix.sh" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# SSH into EC2 and run the fix
echo "🔧 Running final clean fix on EC2..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    echo "🔧 Making script executable..."
    chmod +x final_clean_fix.sh
    
    echo "🚀 Running final clean fix..."
    ./final_clean_fix.sh
    
    echo "✅ Final clean fix completed!"
    echo "📋 Checking final status..."
    
    # Check service status
    sudo systemctl status ai-backend-python.service --no-pager
    
    # Check process count
    echo "🔍 Process count:"
    pgrep -f uvicorn | wc -l
    
    # Check CPU usage
    echo "📊 CPU usage:"
    top -p $(pgrep -f uvicorn | tr '\n' ',' | sed 's/,$//') -b -n 1 | tail -2
    
    echo "🎉 Deployment completed successfully!"
EOF

echo "✅ Final clean fix deployed successfully!"
echo "📋 You can check the application status by SSH'ing into the EC2 instance:"
echo "   ssh -i \"$PEM_FILE\" $EC2_USER@$EC2_HOST"
echo "   cd $REMOTE_DIR && sudo systemctl status ai-backend-python.service" 