#!/bin/bash

# Enhanced Proposal System Deployment Script
# Deploys all enhanced proposal system files to EC2 instance

EC2_HOST="34.202.215.209"
PEM_FILE="C:/projects/lvl_up/New.pem"
REMOTE_DIR="~/ai-backend-python"

echo "🚀 Deploying Enhanced Proposal System to EC2..."

# Create a temporary directory for the files
TEMP_DIR="./temp_deploy"
mkdir -p $TEMP_DIR

# Copy all the enhanced proposal system files
echo "📁 Copying enhanced proposal system files..."

# Backend files
cp ai-backend-python/app/models/proposal.py $TEMP_DIR/
cp ai-backend-python/app/models/sql_models.py $TEMP_DIR/
cp ai-backend-python/app/services/enhanced_proposal_description_service.py $TEMP_DIR/
cp ai-backend-python/app/routers/proposals.py $TEMP_DIR/
cp ai-backend-python/add_enhanced_proposal_fields_migration.py $TEMP_DIR/

# Frontend files
mkdir -p $TEMP_DIR/lib/models
mkdir -p $TEMP_DIR/lib/screens
cp lib/models/ai_proposal.dart $TEMP_DIR/lib/models/
cp lib/screens/proposal_approval_screen.dart $TEMP_DIR/lib/screens/

# Documentation
cp ENHANCED_PROPOSAL_SYSTEM_SUMMARY.md $TEMP_DIR/

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf enhanced_proposal_system.tar.gz -C $TEMP_DIR .

# Deploy to EC2
echo "☁️ Deploying to EC2 instance..."
scp -i "$PEM_FILE" enhanced_proposal_system.tar.gz ubuntu@$EC2_HOST:~/

# Extract and install on EC2
echo "🔧 Installing on EC2..."
ssh -i "$PEM_FILE" ubuntu@$EC2_HOST << 'EOF'
    cd ~/ai-backend-python
    
    # Backup existing files
    echo "💾 Backing up existing files..."
    mkdir -p backup_$(date +%Y%m%d_%H%M%S)
    cp app/models/proposal.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    cp app/models/sql_models.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    cp app/routers/proposals.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
    
    # Extract new files
    echo "📂 Extracting new files..."
    tar -xzf ~/enhanced_proposal_system.tar.gz
    
    # Install missing dependencies
    echo "📦 Installing missing dependencies..."
    pip install schedule
    
    # Run database migration
    echo "🗄️ Running database migration..."
    python add_enhanced_proposal_fields_migration.py
    
    # Restart the application
    echo "🔄 Restarting application..."
    sudo systemctl restart ai-backend-python || true
    
    # Clean up
    rm ~/enhanced_proposal_system.tar.gz
    
    echo "✅ Enhanced proposal system deployment completed!"
EOF

# Clean up local files
echo "🧹 Cleaning up local files..."
rm -rf $TEMP_DIR
rm enhanced_proposal_system.tar.gz

echo "🎉 Deployment completed successfully!"
echo "📋 Summary of deployed files:"
echo "   - Enhanced proposal models (proposal.py, sql_models.py)"
echo "   - Enhanced proposal description service"
echo "   - Updated proposals router with response functionality"
echo "   - Database migration script"
echo "   - Enhanced frontend models and screens"
echo "   - Documentation"
echo ""
echo "🔗 EC2 Instance: $EC2_HOST"
echo "📁 Remote Directory: $REMOTE_DIR" 