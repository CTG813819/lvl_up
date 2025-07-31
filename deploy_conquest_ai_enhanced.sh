#!/bin/bash

# Enhanced Conquest AI Deployment Script for EC2
# This script deploys the enhanced backend with AI-powered conquest capabilities

echo "🚀 Deploying Enhanced Conquest AI with Advanced Code Generation..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment and install enhanced AI/ML dependencies for conquest AI
echo "📦 Installing enhanced AI/ML dependencies for conquest AI..."
source venv/bin/activate
pip install transformers torch openai anthropic scikit-learn numpy pandas

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

# Conquest AI Configuration
CONQUEST_AI_ENABLED=true
CONQUEST_AI_MODEL_PATH=./models/conquest-ai/
CONQUEST_AI_LEARNING_RATE=0.001
EOF
fi

# Restart the backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Check if service is running
echo "✅ Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test the enhanced conquest AI endpoints
echo "🧪 Testing enhanced conquest AI endpoints..."
sleep 5  # Wait for service to start

# Test AI code generation
echo "Testing AI code generation..."
curl -X POST http://localhost:4000/api/conquest/test-ai-code-generation \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "ConquestAIWidget",
    "complexity": "medium",
    "description": "A widget with AI-powered conquest capabilities"
  }'

# Test complexity analysis
echo "Testing complexity analysis..."
curl -X POST http://localhost:4000/api/conquest/analyze-code-complexity \
  -H "Content-Type: application/json" \
  -d '{
    "code": "class ConquestWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); } }",
    "language": "dart"
  }'

# Test enhanced app creation
echo "Testing enhanced app creation..."
curl -X POST http://localhost:4000/api/conquest/create-app \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ConquestAIApp",
    "description": "An AI-powered conquest application",
    "keywords": ["ai", "conquest", "flutter"],
    "features": ["ai_integration", "conquest_analytics", "smart_deployment"]
  }'

echo ""
echo "🎉 Enhanced Conquest AI deployment complete!"
echo ""
echo "📋 What's new in Conquest AI:"
echo "  ✅ Advanced AI code generation (OpenAI GPT-4, Anthropic Claude)"
echo "  ✅ Local transformer model support"
echo "  ✅ Complexity-based code generation"
echo "  ✅ AI-enhanced pubspec.yaml generation"
echo "  ✅ Intelligent screen and service generation"
echo "  ✅ Fallback template generation"
echo "  ✅ Continuous learning integration"
echo ""
echo "🔧 To enable full AI capabilities:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Add local models to models/code-generation-model/"
echo ""
echo "📊 Monitor conquest AI logs with: sudo journalctl -u ai-backend-python -f"
echo ""
echo "🧪 Test endpoints:"
echo "  - POST /api/conquest/test-ai-code-generation"
echo "  - POST /api/conquest/analyze-code-complexity"
echo "  - POST /api/conquest/create-app (enhanced)"
echo "  - GET /api/conquest/ (overview with AI capabilities)" 