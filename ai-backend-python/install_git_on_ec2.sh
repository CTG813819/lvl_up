#!/bin/bash

# Script to install git on EC2 instance for Conquest agent
echo "🔧 Installing git on EC2 instance..."

# Update package list
sudo apt update

# Install git
sudo apt install -y git

# Configure git with default settings
git config --global user.name "AI Backend"
git config --global user.email "ai-backend@example.com"

# Verify installation
if command -v git &> /dev/null; then
    echo "✅ Git installed successfully"
    git --version
else
    echo "❌ Git installation failed"
    exit 1
fi

echo "🎉 Git installation completed!" 