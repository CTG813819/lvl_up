#!/bin/bash

echo "🧹 Starting targeted EC2 cleanup..."

# Remove specific backup directories
echo "🗂️ Removing backup directories..."
rm -rf /home/ubuntu/ai-backend-python-backup
rm -rf /home/ubuntu/ai-backend-python-backup-2
rm -rf /home/ubuntu/ai-backend-python-old
rm -rf /home/ubuntu/ai-backend-python-old-1751788936
rm -rf /home/ubuntu/ai-backend-python-old-1751789025
rm -rf /home/ubuntu/ai-backend-python-old-1751791008
rm -rf /home/ubuntu/ai-backend-python-old-1751792255

# Remove old deployment directories
echo "🚀 Removing old deployment directories..."
rm -rf /home/ubuntu/imperium_deployment
rm -rf /home/ubuntu/imperium_deployment_final
rm -rf /home/ubuntu/imperium_deployment_fixed
rm -f /home/ubuntu/imperium_deployment.tar.gz
rm -f /home/ubuntu/imperium_deployment_final.tar.gz
rm -f /home/ubuntu/imperium_deployment_fixed.tar.gz

# Remove old backup JS backend
echo "🔧 Removing old JS backend backup..."
rm -rf /home/ubuntu/backup-js-backend-20250704_231537
rm -rf /home/ubuntu/backup-js-backend-20250704_232854

# Remove old AI backend
echo "🤖 Removing old AI backend..."
rm -rf /home/ubuntu/ai-learning-backend

# Remove old zip files
echo "📦 Removing old zip files..."
rm -f /home/ubuntu/ai-backend-python-fixed.zip
rm -f /home/ubuntu/ai-backend-python-updated.zip

# Remove old Flutter files
echo "🎨 Removing old Flutter files..."
rm -f /home/ubuntu/flutter_linux_3.32.5-stable.tar.xz
rm -f /home/ubuntu/flutter_linux_latest.tar.xz

# Remove old scripts
echo "📜 Removing old scripts..."
rm -f /home/ubuntu/deploy.sh
rm -f /home/ubuntu/ec2_comprehensive_enhancement.sh
rm -f /home/ubuntu/ec2_comprehensive_testing.sh
rm -f /home/ubuntu/start-backend.sh

# Remove test directories
echo "🧪 Removing test directories..."
rm -rf /home/ubuntu/test_flutter_app

# Remove old virtual environment
echo "🐍 Removing old virtual environment..."
rm -rf /home/ubuntu/venv

# Remove NLTK data (can be re-downloaded if needed)
echo "📚 Removing NLTK data..."
rm -rf /home/ubuntu/nltk_data

# Remove old Flutter directory (keeping only current one)
echo "🎨 Removing old Flutter directory..."
rm -rf /home/ubuntu/flutter

# Remove old Lvl_UP directory
echo "📱 Removing old Lvl_UP directory..."
rm -rf /home/ubuntu/Lvl_UP

# Remove old documentation files
echo "📖 Removing old documentation..."
rm -f /home/ubuntu/AI_GROWTH_SYSTEM_GUIDE.md
rm -f /home/ubuntu/AUTONOMOUS_AI_SYSTEM.md
rm -f /home/ubuntu/CONQUEST_AI_README.md

echo "✅ Targeted cleanup completed!"
echo "📊 Current disk usage:"
df -h /
echo ""
echo "💾 Space freed up successfully!" 