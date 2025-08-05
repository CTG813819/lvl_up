#!/bin/bash

# Upload Comprehensive Virtual Environment Fix
echo "📤 Uploading comprehensive virtual environment fix..."

# Upload the fix script
scp comprehensive_venv_fix.py ubuntu@your-ec2-ip:/home/ubuntu/

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Run the fix: python3 comprehensive_venv_fix.py"
echo "2. Activate the new environment: source /home/ubuntu/ai-backend-python/activate_venv.sh"
echo "3. Start the backend: cd /home/ubuntu/ai-backend-python && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" 