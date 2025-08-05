#!/bin/bash

echo "🚀 Setting up AI Backend Environment Configuration on EC2"
echo "=================================================="

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
source /home/ubuntu/venv/bin/activate

# Run the environment setup script
echo "📝 Creating environment configuration..."
python setup_environment.py

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p models
mkdir -p uploads
mkdir -p temp
mkdir -p logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 600 .env
chmod 755 models uploads temp logs

echo "✅ Environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update GitHub configuration (if needed):"
echo "   python setup_environment.py --update-github"
echo ""
echo "2. Restart the service:"
echo "   sudo systemctl restart ai-backend-python"
echo ""
echo "3. Check service status:"
echo "   sudo systemctl status ai-backend-python"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u ai-backend-python -f" 