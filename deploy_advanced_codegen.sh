#!/bin/bash

# Advanced Code Generation Deployment Script for EC2
# This script deploys the enhanced backend with AI-powered code generation

echo "🚀 Deploying Advanced Code Generation Backend..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment and install new dependencies
echo "📦 Installing new AI/ML dependencies..."
source venv/bin/activate
pip install transformers torch openai anthropic

# Set up environment variables for AI models (if you have API keys)
# Uncomment and set your API keys if you have them:
# export OPENAI_API_KEY="your-openai-key"
# export ANTHROPIC_API_KEY="your-anthropic-key"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# AI Model API Keys (uncomment and set if you have them)
# OPENAI_API_KEY=your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Backend Configuration
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-secret-key-here
EOF
fi

# Restart the backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Check if service is running
echo "✅ Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test the new code generation endpoint
echo "🧪 Testing code generation..."
sleep 5  # Wait for service to start

# Test with a simple extension
curl -X POST http://localhost:4000/api/terra/extensions \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "TestAdvancedWidget",
    "menu_title": "Advanced Test",
    "icon_name": "Icons.code",
    "description": "A complex widget with state management and API integration"
  }'

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 What's new:"
echo "  ✅ Advanced AI code generation (OpenAI GPT-4, Anthropic Claude)"
echo "  ✅ Local transformer model support"
echo "  ✅ Complexity-based code generation"
echo "  ✅ Fallback template generation"
echo ""
echo "🔧 To enable full AI capabilities:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Add local models to models/code-generation-model/"
echo ""
echo "📊 Monitor logs with: sudo journalctl -u ai-backend-python -f" 