#!/bin/bash

# Deploy Comprehensive System Analysis to EC2
# This script transfers the analysis script to EC2 and runs it

# Configuration
PEM_FILE="C:/projects/lvl_up/New.pem"
EC2_HOST="ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
REMOTE_DIR="/home/ubuntu/ai-backend-python"
LOCAL_SCRIPT="comprehensive_system_analysis.py"
REMOTE_SCRIPT="comprehensive_system_analysis.py"

echo "🚀 Deploying Comprehensive System Analysis to EC2..."
echo "📁 PEM File: $PEM_FILE"
echo "🌐 EC2 Host: $EC2_HOST"
echo "📂 Remote Directory: $REMOTE_DIR"

# Check if PEM file exists
if [ ! -f "$PEM_FILE" ]; then
    echo "❌ Error: PEM file not found at $PEM_FILE"
    exit 1
fi

# Check if local script exists
if [ ! -f "$LOCAL_SCRIPT" ]; then
    echo "❌ Error: Analysis script not found: $LOCAL_SCRIPT"
    exit 1
fi

echo "📤 Transferring analysis script to EC2..."

# Transfer the analysis script to EC2
scp -i "$PEM_FILE" "$LOCAL_SCRIPT" "$EC2_HOST:$REMOTE_DIR/"

if [ $? -eq 0 ]; then
    echo "✅ Script transferred successfully"
else
    echo "❌ Failed to transfer script"
    exit 1
fi

echo "🔧 Setting up environment on EC2..."

# SSH into EC2 and run the analysis
ssh -i "$PEM_FILE" "$EC2_HOST" << 'EOF'
    cd /home/ubuntu/ai-backend-python
    
    echo "📋 Current directory: $(pwd)"
    echo "📁 Directory contents:"
    ls -la
    
    echo "🐍 Checking Python version..."
    python3 --version
    
    echo "📦 Installing required packages..."
    pip3 install ast pathlib typing datetime importlib inspect
    
    echo "🔍 Running comprehensive system analysis..."
    python3 comprehensive_system_analysis.py
    
    echo "📄 Analysis complete! Checking for report file..."
    ls -la *.json
    
    echo "📊 Analysis results:"
    if [ -f "comprehensive_system_analysis_report.json" ]; then
        echo "✅ Report generated successfully"
        echo "📋 Report size: $(du -h comprehensive_system_analysis_report.json | cut -f1)"
        echo "📄 First 500 characters of report:"
        head -c 500 comprehensive_system_analysis_report.json
        echo ""
    else
        echo "❌ Report file not found"
    fi
EOF

echo "✅ Deployment and analysis completed!"
echo "📋 Check the EC2 instance for the analysis report" 