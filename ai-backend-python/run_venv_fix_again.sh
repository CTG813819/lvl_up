#!/bin/bash

# Run Virtual Environment Fix Again
echo "🚀 Running comprehensive virtual environment fix again..."

# Run the venv fix on the EC2 instance
ssh ubuntu@your-ec2-ip << 'EOF'
cd /home/ubuntu/ai-backend-python
echo "🔧 Running comprehensive virtual environment fix..."
python3 comprehensive_venv_fix.py
EOF

echo "✅ Virtual environment fix completed!"
echo ""
echo "🧪 Next steps on EC2:"
echo "1. Test the main app: cd /home/ubuntu/ai-backend-python && python -c \"from app.main import app; print('✅ App imported successfully')\""
echo "2. If successful, start the backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" 