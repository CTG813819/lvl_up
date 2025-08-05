#!/bin/bash

echo "🔧 Setting up local database as temporary solution..."

# Navigate to backend directory
cd ~/ai-backend-python

# Install PostgreSQL if not already installed
echo "📦 Checking PostgreSQL installation..."
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
echo "🚀 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
echo "🗄️  Creating database and user..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ai_backend;
DROP USER IF EXISTS ai_user;
CREATE DATABASE ai_backend;
CREATE USER ai_user WITH PASSWORD 'ai_password';
GRANT ALL PRIVILEGES ON DATABASE ai_backend TO ai_user;
ALTER USER ai_user CREATEDB;
\q
EOF

# Update .env with local database
echo "📝 Updating .env with local database..."
sed -i 's|DATABASE_URL=.*|DATABASE_URL="postgresql://ai_user:ai_password@localhost:5432/ai_backend"|' .env

# Verify the change
echo "✅ Updated DATABASE_URL:"
grep "DATABASE_URL" .env

# Test database connection
echo "🔍 Testing local database connection..."
PGPASSWORD=ai_password psql -h localhost -U ai_user -d ai_backend -c "SELECT version();"

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait for restart
sleep 5

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 15 --no-pager

echo "✅ Local database setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Test the endpoints to verify they work"
echo "2. Check your Neon database status"
echo "3. Update DATABASE_URL when Neon is working" 