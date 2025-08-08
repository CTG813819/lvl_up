#!/bin/bash

# Upload All Clean Service Files
echo "📤 Uploading all clean service files..."

# Upload the clean files from your local project
scp ai-backend-python/app/services/ai_learning_service.py ubuntu@your-ec2-ip:/home/ubuntu/ai-backend-python/app/services/ai_learning_service.py
scp ai-backend-python/app/services/ml_service.py ubuntu@your-ec2-ip:/home/ubuntu/ai-backend-python/app/services/ml_service.py

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Test the main app: cd /home/ubuntu/ai-backend-python && python -c \"from app.main import app; print('✅ App imported successfully')\""
echo "2. If successful, start the backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "💡 This should fix the indentation errors in both ai_learning_service.py and ml_service.py" 