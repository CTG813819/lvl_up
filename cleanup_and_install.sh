#!/bin/bash

# Cleanup and Light AI Dependencies Installation Script
# This script frees up disk space and installs lighter AI dependencies

echo "🧹 Cleaning up disk space..."

# Navigate to the backend directory
cd /home/ubuntu/ai-backend-python

# Clean up package cache
echo "📦 Cleaning package cache..."
sudo apt clean
sudo apt autoremove -y

# Clean up pip cache
echo "📦 Cleaning pip cache..."
pip cache purge

# Clean up old logs
echo "📋 Cleaning old logs..."
sudo journalctl --vacuum-time=7d

# Clean up temporary files
echo "🗂️ Cleaning temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Check disk space
echo "💾 Checking disk space..."
df -h

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install lighter AI dependencies (CPU-only versions)
echo "📦 Installing lighter AI/ML dependencies..."
pip install openai anthropic

# Install transformers without torch (we'll use CPU version)
echo "📦 Installing transformers..."
pip install transformers

# Install CPU-only torch (much smaller)
echo "📦 Installing CPU-only PyTorch..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
echo "📦 Installing other dependencies..."
pip install scikit-learn numpy pandas pytest aiohttp

# Verify installation
echo "✅ Verifying installation..."
python -c "import openai, anthropic, transformers, torch; print('✅ All AI dependencies installed successfully!')"

echo ""
echo "🎉 Cleanup and installation complete!"
echo ""
echo "📋 Installed packages:"
echo "  ✅ openai - OpenAI API client"
echo "  ✅ anthropic - Anthropic Claude API client"
echo "  ✅ transformers - Hugging Face transformers library (CPU)"
echo "  ✅ torch - PyTorch (CPU-only, much smaller)"
echo "  ✅ scikit-learn - Machine learning library"
echo "  ✅ numpy - Numerical computing"
echo "  ✅ pandas - Data manipulation"
echo "  ✅ pytest - Testing framework"
echo "  ✅ aiohttp - Async HTTP client"
echo ""
echo "💾 Disk space freed up and lighter dependencies installed!"
echo ""
echo "🔧 Next steps:"
echo "  1. Set OPENAI_API_KEY in .env for GPT-4 code generation"
echo "  2. Set ANTHROPIC_API_KEY in .env for Claude code generation"
echo "  3. Run the deployment scripts to enable AI features"
echo ""
echo "📊 Monitor logs with: sudo journalctl -u ai-backend-python -f" 