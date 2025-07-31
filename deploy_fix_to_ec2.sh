#!/bin/bash

# Deploy database fix to EC2 instance
# This script copies the fix files and runs the database migration

set -e  # Exit on any error

# Configuration
EC2_HOST="ec2-34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
PEM_FILE="C:/projects/lvl_up/New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

echo "🚀 Deploying database fix to EC2 instance..."

# Step 1: Copy the fix script to EC2
echo "📁 Copying fix script to EC2..."
scp -i "$PEM_FILE" "ai-backend-python/fix_ai_learning_summary_column.py" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# Step 2: Copy the instructions
echo "📄 Copying instructions to EC2..."
scp -i "$PEM_FILE" "EC2_DATABASE_FIX_INSTRUCTIONS.md" "$EC2_USER@$EC2_HOST:$REMOTE_DIR/"

# Step 3: SSH into EC2 and run the fix
echo "🔧 Running database fix on EC2..."
ssh -i "$PEM_FILE" "$EC2_USER@$EC2_HOST" << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    echo "📂 Current directory: $(pwd)"
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
    
    echo "🔧 Running database fix script..."
    python fix_ai_learning_summary_column.py
    
    echo "✅ Verifying the fix..."
    python check_and_fix_db.py
    
    echo "🔄 Restarting the application..."
    # Stop any running uvicorn processes
    pkill -f uvicorn || true
    
    # Start the application with the correct parameters
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio --workers 1 > app.log 2>&1 &
    
    echo "🎉 Database fix completed and application restarted!"
    echo "📋 Check the logs with: tail -f app.log"
EOF

echo "✅ Deployment completed successfully!"
echo "📋 You can check the application status by SSH'ing into the EC2 instance:"
echo "   ssh -i \"$PEM_FILE\" $EC2_USER@$EC2_HOST"
echo "   cd $REMOTE_DIR && tail -f app.log" 