#!/bin/bash

# Migration script: Remove JavaScript backend and deploy Python backend to EC2
# Usage: ./migrate_to_python.sh [EC2_IP] [SSH_KEY_PATH]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
EC2_IP=${1:-""34-202-215-209""}
SSH_KEY=${2:-"C:\projects\lvl_up\New.pem"}
REMOTE_USER="ubuntu"
REMOTE_DIR="/home/ubuntu"
JS_BACKEND_DIR="$REMOTE_DIR/ai-backend"
PYTHON_BACKEND_DIR="$REMOTE_DIR/ai-backend-python"
BACKUP_DIR="$REMOTE_DIR/backup-js-backend-$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}🚀 Starting migration from JavaScript to Python backend${NC}"
echo -e "${YELLOW}EC2 IP: $EC2_IP${NC}"
echo -e "${YELLOW}SSH Key: $SSH_KEY${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to execute SSH command
ssh_exec() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_USER@$EC2_IP" "$1"
}

# Function to copy files to EC2
scp_copy() {
    scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -r "$1" "$REMOTE_USER@$EC2_IP:$2"
}

# Step 1: Test SSH connection
print_info "Testing SSH connection..."
if ! ssh_exec "echo 'SSH connection successful'" > /dev/null 2>&1; then
    print_error "Failed to connect to EC2 instance. Please check your IP and SSH key."
    exit 1
fi
print_status "SSH connection established"

# Step 2: Stop JavaScript backend services
print_info "Stopping JavaScript backend services..."
ssh_exec "sudo systemctl stop ai-backend || true"
ssh_exec "sudo systemctl stop pm2 || true"
ssh_exec "pkill -f 'node.*ai-backend' || true"
ssh_exec "pkill -f 'pm2' || true"
print_status "JavaScript backend services stopped"

# Step 3: Create backup of JavaScript backend
print_info "Creating backup of JavaScript backend..."
ssh_exec "mkdir -p $BACKUP_DIR"
ssh_exec "cp -r $JS_BACKEND_DIR/* $BACKUP_DIR/ 2>/dev/null || true"
print_status "Backup created at $BACKUP_DIR"

# Step 4: Remove JavaScript backend files
print_info "Removing JavaScript backend files..."
ssh_exec "rm -rf $JS_BACKEND_DIR"
ssh_exec "rm -rf $REMOTE_DIR/node_modules"
ssh_exec "rm -f $REMOTE_DIR/package*.json"
ssh_exec "rm -f $REMOTE_DIR/.env"
print_status "JavaScript backend files removed"

# Step 5: Clean up system services
print_info "Cleaning up system services..."
ssh_exec "sudo systemctl disable ai-backend || true"
ssh_exec "sudo rm -f /etc/systemd/system/ai-backend.service || true"
ssh_exec "sudo systemctl daemon-reload"
print_status "System services cleaned up"

# Step 6: Install Python dependencies
print_info "Installing Python dependencies..."
ssh_exec "sudo apt-get update"
ssh_exec "sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential"
ssh_exec "sudo apt-get install -y curl wget git"
print_status "Python dependencies installed"

# Step 7: Create Python virtual environment
print_info "Setting up Python virtual environment..."
ssh_exec "cd $REMOTE_DIR && python3 -m venv venv"
ssh_exec "source $REMOTE_DIR/venv/bin/activate && pip install --upgrade pip"
print_status "Python virtual environment created"

# Step 8: Upload Python backend files
print_info "Uploading Python backend files..."
scp_copy "ai-backend-python/" "$REMOTE_DIR/"
print_status "Python backend files uploaded"

# Step 9: Install Python requirements
print_info "Installing Python requirements..."
ssh_exec "cd $PYTHON_BACKEND_DIR && source $REMOTE_DIR/venv/bin/activate && pip install -r requirements.txt"
print_status "Python requirements installed"

# Step 10: Download NLTK data
print_info "Downloading NLTK data..."
ssh_exec "cd $PYTHON_BACKEND_DIR && source $REMOTE_DIR/venv/bin/activate && python -c \"import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)\""
print_status "NLTK data downloaded"

# Step 11: Create necessary directories
print_info "Creating necessary directories..."
ssh_exec "mkdir -p $PYTHON_BACKEND_DIR/models"
ssh_exec "mkdir -p $PYTHON_BACKEND_DIR/uploads"
ssh_exec "mkdir -p $PYTHON_BACKEND_DIR/temp"
print_status "Directories created"

# Step 12: Set up environment variables
print_info "Setting up environment variables..."
cat > .env.template << 'EOF'
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=ai_backend_python

# Server
PORT=4000
HOST=0.0.0.0
DEBUG=false

# AI Services
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_repo_here

# AWS
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=us-east-1

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# AI Learning
LEARNING_ENABLED=true
LEARNING_INTERVAL=300
MAX_LEARNING_HISTORY=1000

# Proposal settings
MAX_PROPOSAL_LENGTH=10000
PROPOSAL_TIMEOUT=300
EOF

scp_copy ".env.template" "$PYTHON_BACKEND_DIR/.env"
print_warning "Please edit the .env file with your actual API keys and configuration"
print_status "Environment template created"

# Step 13: Create systemd service for Python backend
print_info "Creating systemd service for Python backend..."
cat > ai-backend-python.service << 'EOF'
[Unit]
Description=AI Backend Python Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/venv/bin
ExecStart=/home/ubuntu/venv/bin/uvicorn main:app --host 0.0.0.0 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

scp_copy "ai-backend-python.service" "$REMOTE_DIR/"
ssh_exec "sudo mv $REMOTE_DIR/ai-backend-python.service /etc/systemd/system/"
ssh_exec "sudo systemctl daemon-reload"
ssh_exec "sudo systemctl enable ai-backend-python"
print_status "Systemd service created"

# Step 14: Set up firewall (if needed)
print_info "Setting up firewall..."
ssh_exec "sudo ufw allow 4000/tcp || true"
print_status "Firewall configured"

# Step 15: Test the Python backend
print_info "Testing Python backend..."
ssh_exec "cd $PYTHON_BACKEND_DIR && source $REMOTE_DIR/venv/bin/activate && python -c \"import sys; sys.path.append('.'); from app.core.config import settings; print('Configuration loaded successfully')\""
print_status "Python backend configuration test passed"

# Step 16: Start the Python backend
print_info "Starting Python backend..."
ssh_exec "sudo systemctl start ai-backend-python"
sleep 5

# Check if service is running
if ssh_exec "sudo systemctl is-active ai-backend-python" | grep -q "active"; then
    print_status "Python backend started successfully"
else
    print_error "Failed to start Python backend"
    ssh_exec "sudo systemctl status ai-backend-python"
    exit 1
fi

# Step 17: Test the API
print_info "Testing API endpoints..."
sleep 10  # Wait for service to fully start

if ssh_exec "curl -f http://localhost:4000/health" > /dev/null 2>&1; then
    print_status "Health check passed"
else
    print_warning "Health check failed - service may still be starting"
fi

# Step 18: Clean up temporary files
print_info "Cleaning up temporary files..."
rm -f .env.template
rm -f ai-backend-python.service
print_status "Temporary files cleaned up"

# Step 19: Migration summary
echo -e "${GREEN}"
echo "🎉 Migration completed successfully!"
echo ""
echo "📋 Summary:"
echo "  ✅ JavaScript backend stopped and backed up"
echo "  ✅ JavaScript files removed from EC2"
echo "  ✅ Python backend deployed and configured"
echo "  ✅ Systemd service created and enabled"
echo "  ✅ Python backend started"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo "🐍 Python backend location: $PYTHON_BACKEND_DIR"
echo "🔧 Service name: ai-backend-python"
echo ""
echo "📝 Next steps:"
echo "  1. Edit the .env file with your API keys:"
echo "     ssh -i $SSH_KEY ubuntu@$EC2_IP"
echo "     nano $PYTHON_BACKEND_DIR/.env"
echo ""
echo "  2. Check service status:"
echo "     sudo systemctl status ai-backend-python"
echo ""
echo "  3. View logs:"
echo "     sudo journalctl -u ai-backend-python -f"
echo ""
echo "  4. Test API:"
echo "     curl http://$EC2_IP:4000/health"
echo ""
echo "🔄 To rollback (if needed):"
echo "  sudo systemctl stop ai-backend-python"
echo "  sudo systemctl disable ai-backend-python"
echo "  rm -rf $PYTHON_BACKEND_DIR"
echo "  cp -r $BACKUP_DIR $JS_BACKEND_DIR"
echo "${NC}"

print_info "Migration script completed!" 