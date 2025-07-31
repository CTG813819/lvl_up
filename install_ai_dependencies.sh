#!/bin/bash

# Install AI Dependencies Script
# This script installs AI/ML dependencies using the virtual environment

echo "🚀 Installing AI/ML Dependencies..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install AI/ML dependencies
echo "📦 Installing AI/ML dependencies..."
pip install transformers torch openai anthropic scikit-learn numpy pandas pytest aiohttp

# Verify installation
echo "✅ Verifying installation..."
python -c "import transformers, torch, openai, anthropic; print('✅ All AI dependencies installed successfully!')"

echo ""
echo "🎉 AI dependencies installation complete!"
echo ""
echo "📋 Installed packages:"
echo "  ✅ transformers - Hugging Face transformers library"
echo "  ✅ torch - PyTorch for deep learning"
echo "  ✅ openai - OpenAI API client"
echo "  ✅ anthropic - Anthropic Claude API client"
echo "  ✅ scikit-learn - Machine learning library"
echo "  ✅ numpy - Numerical computing"
echo "  ✅ pandas - Data manipulation"
echo "  ✅ pytest - Testing framework"
echo "  ✅ aiohttp - Async HTTP client"
echo ""
echo "🔧 Next steps:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Run the deployment scripts to enable AI features"
echo ""
echo "📊 Monitor logs with: sudo journalctl -u ai-backend-python -f" 