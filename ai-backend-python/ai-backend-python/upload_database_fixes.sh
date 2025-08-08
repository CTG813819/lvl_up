#!/bin/bash

# Upload Database Fix Scripts
echo "📤 Uploading database fix scripts..."

# Upload the fix scripts
scp fix_database_py.py ubuntu@your-ec2-ip:/home/ubuntu/
scp comprehensive_database_fix.py ubuntu@your-ec2-ip:/home/ubuntu/

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Run the comprehensive fix: python3 comprehensive_database_fix.py"
echo "2. If that doesn't work, try the simple fix: python3 fix_database_py.py"
echo "3. Then run the venv fix again: python3 comprehensive_venv_fix.py"
echo "4. Test the main app: cd /home/ubuntu/ai-backend-python && python -c \"from app.main import app; print('✅ App imported successfully')\"" 