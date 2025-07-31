#!/bin/bash

# Minimal AI Dependencies Installation Script
# This script installs only the essential AI dependencies to save disk space

echo "🚀 Installing Minimal AI Dependencies..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install only essential AI dependencies
echo "📦 Installing essential AI dependencies..."
pip install openai anthropic

# Install minimal transformers (without heavy dependencies)
echo "📦 Installing minimal transformers..."
pip install transformers --no-deps
pip install tokenizers safetensors

# Install CPU-only torch (much smaller)
echo "📦 Installing CPU-only PyTorch..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install other essential dependencies
echo "📦 Installing other essential dependencies..."
pip install scikit-learn numpy pandas aiohttp

# Verify installation
echo "✅ Verifying installation..."
python -c "import openai, anthropic, transformers, torch; print('✅ Essential AI dependencies installed successfully!')"

echo ""
echo "🎉 Minimal AI dependencies installation complete!"
echo ""
echo "📋 Installed packages:"
echo "  ✅ openai - OpenAI API client"
echo "  ✅ anthropic - Anthropic Claude API client"
echo "  ✅ transformers - Hugging Face transformers library (minimal)"
echo "  ✅ torch - PyTorch (CPU-only)"
echo "  ✅ scikit-learn - Machine learning library"
echo "  ✅ numpy - Numerical computing"
echo "  ✅ pandas - Data manipulation"
echo "  ✅ aiohttp - Async HTTP client"
echo ""
echo "💾 Minimal installation to save disk space!"
echo ""
echo "🔧 Next steps:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Run the deployment scripts to enable AI features"
echo ""
echo "📊 Monitor logs with: sudo journalctl -u ai-backend-python -f" 