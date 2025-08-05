#!/bin/bash

# Disk Space Check and Cleanup Recommendations Script

echo "💾 Checking disk space and providing cleanup recommendations..."

# Check disk space
echo "📊 Current disk usage:"
df -h

echo ""
echo "📦 Checking largest directories:"
du -h --max-depth=1 /home/ubuntu/ai-backend-python/ 2>/dev/null | sort -hr | head -10

echo ""
echo "🗂️ Checking system directories:"
du -h --max-depth=1 /var/log/ 2>/dev/null | sort -hr | head -5
du -h --max-depth=1 /tmp/ 2>/dev/null | sort -hr | head -5

echo ""
echo "🧹 Cleanup recommendations:"
echo "1. Run: sudo apt clean && sudo apt autoremove -y"
echo "2. Run: sudo journalctl --vacuum-time=7d"
echo "3. Run: sudo rm -rf /tmp/* /var/tmp/*"
echo "4. Run: pip cache purge (in virtual environment)"
echo "5. Consider removing old log files in /var/log/"
echo ""
echo "💡 For minimal AI installation:"
echo "   - Use CPU-only PyTorch (saves ~2GB)"
echo "   - Install only essential packages"
echo "   - Skip heavy ML models initially"
echo ""
echo "🚀 To install minimal AI dependencies:"
echo "   chmod +x install_minimal_ai.sh"
echo "   ./install_minimal_ai.sh"
echo ""
echo "🧹 To cleanup and install:"
echo "   chmod +x cleanup_and_install.sh"
echo "   ./cleanup_and_install.sh" 