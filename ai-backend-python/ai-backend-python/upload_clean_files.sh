#!/bin/bash

# Upload Clean Files to Fix Indentation Errors
echo "📤 Uploading clean files to fix indentation errors..."

# Upload the clean files from your local project
scp ai-backend-python/app/core/database.py ubuntu@your-ec2-ip:/home/ubuntu/ai-backend-python/app/core/database.py
scp ai-backend-python/app/services/ai_learning_service.py ubuntu@your-ec2-ip:/home/ubuntu/ai-backend-python/app/services/ai_learning_service.py

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Test the main app: cd /home/ubuntu/ai-backend-python && python -c \"from app.main import app; print('✅ App imported successfully')\""
echo "2. If successful, start the backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "💡 This should fix the indentation errors in both database.py and ai_learning_service.py" 