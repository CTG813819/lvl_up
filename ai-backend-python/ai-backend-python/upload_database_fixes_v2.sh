#!/bin/bash

# Upload Database Fix Scripts v2
echo "📤 Uploading database fix scripts v2..."

# Upload the fix scripts
scp direct_database_fix.py ubuntu@your-ec2-ip:/home/ubuntu/
scp recreate_database_py.py ubuntu@your-ec2-ip:/home/ubuntu/

echo "✅ Upload complete!"
echo ""
echo "🚀 Next steps on EC2:"
echo "1. Try the direct fix first: python3 direct_database_fix.py"
echo "2. If that doesn't work, recreate the file: python3 recreate_database_py.py"
echo "3. Then run the venv fix again: python3 comprehensive_venv_fix.py"
echo "4. Test the main app: cd /home/ubuntu/ai-backend-python && python -c \"from app.main import app; print('✅ App imported successfully')\""
echo ""
echo "💡 The recreate_database_py.py script completely recreates the database.py file"
echo "   with the correct content, which should definitely fix the indentation error." 