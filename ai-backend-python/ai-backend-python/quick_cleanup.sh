#!/bin/bash
echo "🧹 Quick Disk Cleanup"
echo "===================="

echo "💾 Initial disk usage:"
df -h

echo -e "\n🗑️  Removing old backup files..."
rm -rf enhanced_learning_deployment_20250706_*.tar.gz

echo -e "\n🗑️  Removing old directories..."
rm -rf ai-backend test lib flutter android-sdk

echo -e "\n🗑️  Removing old scripts..."
rm -f fix_*.py test_*.py setup_*.py deploy_*.py comprehensive_*.py debug_*.py restart_*.py check_*.py

echo -e "\n📦 Clearing package cache..."
sudo apt-get clean
sudo apt-get autoremove -y

echo -e "\n🐍 Clearing pip cache..."
pip cache purge

echo -e "\n📋 Clearing old logs..."
sudo find /var/log -name "*.log" -mtime +3 -delete
sudo journalctl --vacuum-time=3d

echo -e "\n🗂️  Clearing temp files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

echo -e "\n💾 Final disk usage:"
df -h

echo -e "\n�� Cleanup complete!" 