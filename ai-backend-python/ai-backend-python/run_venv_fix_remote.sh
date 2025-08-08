#!/bin/bash

# Run Virtual Environment Fix on EC2
echo "🚀 Running comprehensive virtual environment fix on EC2..."

# Run the venv fix on the EC2 instance
ssh ubuntu@your-ec2-ip << 'EOF'
cd /home/ubuntu/ai-backend-python
python3 comprehensive_venv_fix.py
EOF

echo "✅ Virtual environment fix completed on EC2!"
echo ""
echo "🧪 Next steps on EC2:"
echo "1. Test database import: cd /home/ubuntu/ai-backend-python && python -c \"from app.core.database import get_session; print('✅ Database imported successfully')\""
echo "2. Test main app: python -c \"from app.main import app; print('✅ App imported successfully')\""
echo "3. Start backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" 