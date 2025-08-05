#!/bin/bash

# Upload Clean Database.py
echo "📤 Uploading clean database.py file..."

# Upload the clean database.py file from your local project
scp ai-backend-python/app/core/database.py ubuntu@your-ec2-ip:/home/ubuntu/ai-backend-python/app/core/database.py

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Test the database import: cd /home/ubuntu/ai-backend-python && python -c \"from app.core.database import get_session; print('✅ Database imported successfully')\""
echo "2. Test the main app: python -c \"from app.main import app; print('✅ App imported successfully')\""
echo "3. If both work, start the backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "💡 This should fix the indentation error since you're uploading the original, clean file." 