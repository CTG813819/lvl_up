#!/bin/bash

# Enhanced Sandbox AI Deployment Script for EC2
# This script deploys the enhanced backend with AI-powered sandbox capabilities

echo "🚀 Deploying Enhanced Sandbox AI with Advanced Code Generation..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment and install enhanced AI/ML dependencies for sandbox AI
echo "📦 Installing enhanced AI/ML dependencies for sandbox AI..."
source venv/bin/activate
pip install transformers torch openai anthropic scikit-learn numpy pandas pytest

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

# Sandbox AI Configuration
SANDBOX_AI_ENABLED=true
SANDBOX_AI_MODEL_PATH=./models/sandbox-ai/
SANDBOX_AI_EXPERIMENT_MODE=true
EOF
fi

# Restart the backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Check if service is running
echo "✅ Checking service status..."
sudo systemctl status ai-backend-python --no-pager

# Test the enhanced sandbox AI endpoints
echo "🧪 Testing enhanced sandbox AI endpoints..."
sleep 5  # Wait for service to start

# Test sandbox AI capabilities
echo "Testing sandbox AI capabilities..."
curl -X GET http://localhost:4000/api/agents/sandbox/ai-capabilities

# Test AI code generation
echo "Testing AI code generation..."
curl -X POST http://localhost:4000/api/agents/sandbox/test-ai-code-generation \
  -H "Content-Type: application/json" \
  -d '{
    "feature_name": "SandboxAIWidget",
    "complexity": "medium",
    "description": "A widget with AI-powered sandbox capabilities"
  }'

# Test AI experiments
echo "Testing AI experiments..."
curl -X POST http://localhost:4000/api/agents/sandbox/run-ai-experiments \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_type": "code_generation",
    "parameters": {
      "complexity": "medium",
      "language": "dart",
      "framework": "flutter"
    }
  }'

# Test code quality analysis
echo "Testing code quality analysis..."
curl -X POST http://localhost:4000/api/agents/sandbox/analyze-code-quality \
  -H "Content-Type: application/json" \
  -d '{
    "code": "class SandboxWidget extends StatelessWidget { @override Widget build(BuildContext context) { return Container(); } }",
    "language": "dart",
    "framework": "flutter"
  }'

# Test sandbox agent status
echo "Testing sandbox agent status..."
curl -X GET http://localhost:4000/api/agents/status

echo ""
echo "🎉 Enhanced Sandbox AI deployment complete!"
echo ""
echo "📋 What's new in Sandbox AI:"
echo "  ✅ Advanced AI code generation (OpenAI GPT-4, Anthropic Claude)"
echo "  ✅ Local transformer model support"
echo "  ✅ Complexity-based code generation"
echo "  ✅ AI-powered experiments and testing"
echo "  ✅ Code quality analysis"
echo "  ✅ Feature detection and assessment"
echo "  ✅ Continuous learning integration"
echo "  ✅ Fallback template generation"
echo ""
echo "🔧 To enable full AI capabilities:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Add local models to models/code-generation-model/"
echo ""
echo "📊 Monitor sandbox AI logs with: sudo journalctl -u ai-backend-python -f"
echo ""
echo "🧪 Test endpoints:"
echo "  - GET /api/agents/sandbox/ai-capabilities"
echo "  - POST /api/agents/sandbox/test-ai-code-generation"
echo "  - POST /api/agents/sandbox/run-ai-experiments"
echo "  - POST /api/agents/sandbox/analyze-code-quality"
echo "  - GET /api/agents/status (enhanced with AI info)"
echo "  - POST /api/agents/run/sandbox (enhanced sandbox agent)" 