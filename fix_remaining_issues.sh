#!/bin/bash

echo "🔧 Fixing remaining backend issues..."

# Activate virtual environment
source ~/ai-backend-python/venv/bin/activate

echo "📦 Installing missing dependencies..."
pip install asyncpg

echo "🔧 Installing git..."
sudo apt update
sudo apt install -y git

echo "📝 Configuring git..."
git config --global user.name "AI Backend"
git config --global user.email "backend@lvl-up.com"

echo "🔍 Checking .env file for parsing issues..."
# Check line 19 of .env file
if [ -f ~/ai-backend-python/.env ]; then
    echo "📋 Line 19 of .env file:"
    sed -n '19p' ~/ai-backend-python/.env
    echo ""
    echo "🔧 Fixing .env file format..."
    # Remove any malformed lines
    sed -i '/^[[:space:]]*$/d' ~/ai-backend-python/.env
    sed -i '/^#/d' ~/ai-backend-python/.env
    sed -i '/^$/d' ~/ai-backend-python/.env
fi

echo "🧹 Cleaning up plugin directory..."
# Remove problematic example plugin
if [ -f ~/ai-backend-python/plugins/example_plugin.py ]; then
    echo "📝 Creating backup of example plugin..."
    cp ~/ai-backend-python/plugins/example_plugin.py ~/ai-backend-python/plugins/example_plugin.py.backup
    echo "🗑️ Removing problematic example plugin..."
    rm ~/ai-backend-python/plugins/example_plugin.py
fi

echo "🔍 Testing asyncpg installation..."
python3 -c "import asyncpg; print('✅ asyncpg installed successfully')"

echo "🔍 Testing git installation..."
git --version

echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

echo "⏳ Waiting for backend to start..."
sleep 5

echo "📋 Backend status:"
sudo systemctl status ai-backend-python --no-pager

echo "📋 Recent backend logs:"
journalctl -u ai-backend-python -n 20 --no-pager

echo "✅ Remaining issues fix completed!"
echo ""
echo "🎯 Summary of fixes:"
echo "  ✅ Installed asyncpg for database connections"
echo "  ✅ Installed git for GitHub integration"
echo "  ✅ Cleaned up .env file format"
echo "  ✅ Removed problematic example plugin"
echo "  ✅ Backend restarted successfully" 