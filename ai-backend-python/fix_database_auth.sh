#!/bin/bash

echo "🔧 Fixing database authentication issues..."

# Check current .env file
echo "📝 Checking current DATABASE_URL..."
cd ~/ai-backend-python
grep "DATABASE_URL" .env

# Fix the DATABASE_URL to use the correct local database
echo "🔧 Updating DATABASE_URL..."
sed -i 's|DATABASE_URL="postgresql://your_actual_username:your_actual_password@your_db_host:5432/your_db_name"|DATABASE_URL="postgresql://ai_user:ai_password@localhost:5432/ai_backend"|' .env

# Also fix any remaining username references
sed -i 's|postgresql://username:password@localhost:5432/dbname|postgresql://ai_user:ai_password@localhost:5432/ai_backend|' .env

# Verify the change
echo "✅ Updated DATABASE_URL:"
grep "DATABASE_URL" .env

# Test database connection with password
echo "🔍 Testing database connection..."
PGPASSWORD=ai_password psql -h localhost -U ai_user -d ai_backend -c "SELECT version();"

# Restart the backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait a moment for restart
sleep 3

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 20 --no-pager

echo "✅ Database authentication fix completed!" 