#!/bin/bash

echo "🔧 Direct database URL fix..."

# Navigate to backend directory
cd ~/ai-backend-python

# Show current DATABASE_URL
echo "📝 Current DATABASE_URL:"
grep "DATABASE_URL" .env

# Directly replace the DATABASE_URL with the correct one
echo "🔧 Replacing DATABASE_URL..."
sed -i 's|DATABASE_URL=.*|DATABASE_URL="postgresql://ai_user:ai_password@localhost:5432/ai_backend"|' .env

# Verify the change
echo "✅ New DATABASE_URL:"
grep "DATABASE_URL" .env

# Test database connection
echo "🔍 Testing database connection..."
PGPASSWORD=ai_password psql -h localhost -U ai_user -d ai_backend -c "SELECT version();" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed. Checking PostgreSQL status..."
    sudo systemctl status postgresql --no-pager
fi

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait for restart
sleep 5

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 10 --no-pager

echo "✅ Database fix completed!" 