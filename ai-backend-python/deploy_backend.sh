#!/bin/bash

set -e

# 1. Pull latest code
echo "=== [1/6] Pulling latest code from git ==="
# git pull

# 2. Activate Python virtual environment
echo "=== [2/6] Activating Python virtual environment ==="
source venv/bin/activate

# 3. Install/update Python dependencies
echo "=== [3/6] Installing/updating Python dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

# 4. Download NLTK data (if needed)
echo "=== [4/6] Downloading NLTK data (if needed) ==="
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# 5. Run backend audit script
echo "=== [5/6] Running backend audit script ==="
python /home/ubuntu/ai-backend-python/../test/test_backend_comprehensive_check.py || true

# 6. Restart backend service
echo "=== [6/6] Restarting backend service ==="
sudo systemctl restart ai-backend-python.service

echo "=== Deployment complete! ===" 