#!/bin/bash
# Install testing dependencies on EC2 instance

echo "🔧 Installing testing dependencies on EC2..."

# Update package list
sudo apt-get update

# Install Python testing tools
echo "📦 Installing Python testing tools..."
sudo apt-get install -y python3-pip
pip3 install flake8

# Install Node.js (if not already installed)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Dart (if not already installed)
echo "📦 Installing Dart..."
sudo apt-get install -y apt-transport-https
wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'wget -qO- https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
sudo apt-get update
sudo apt-get install -y dart

# Verify installations
echo "✅ Verifying installations..."
python3 -m flake8 --version
node --version
dart --version

echo "🎉 Testing dependencies installed successfully!" 