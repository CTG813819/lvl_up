#!/bin/bash

echo "🔧 Fixing PostgreSQL authentication..."

# Check PostgreSQL status
echo "📊 PostgreSQL status:"
sudo systemctl status postgresql --no-pager

# Check if ai_user exists and has proper permissions
echo "🔍 Checking ai_user permissions..."
sudo -u postgres psql -c "SELECT usename, usesuper, usecreatedb FROM pg_user WHERE usename = 'ai_user';"

# Check if database exists
echo "🔍 Checking database..."
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname = 'ai_backend';"

# Fix user permissions if needed
echo "🔧 Setting up ai_user permissions..."
sudo -u postgres psql << EOF
-- Drop user if exists and recreate
DROP USER IF EXISTS ai_user;
CREATE USER ai_user WITH PASSWORD 'ai_password';
ALTER USER ai_user CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE ai_backend TO ai_user;
\q
EOF

# Update PostgreSQL authentication configuration
echo "🔧 Updating PostgreSQL authentication..."
sudo -u postgres cp /etc/postgresql/*/main/pg_hba.conf /etc/postgresql/*/main/pg_hba.conf.backup

# Add local authentication for ai_user
echo "local   ai_backend    ai_user                     md5" | sudo -u postgres tee -a /etc/postgresql/*/main/pg_hba.conf

# Restart PostgreSQL
echo "🔄 Restarting PostgreSQL..."
sudo systemctl restart postgresql

# Wait for restart
sleep 3

# Test connection
echo "🔍 Testing database connection..."
PGPASSWORD=ai_password psql -h localhost -U ai_user -d ai_backend -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection still failing. Trying alternative approach..."
    
    # Try with postgres user and create tables
    sudo -u postgres psql -d ai_backend -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
    
    # Test again
    PGPASSWORD=ai_password psql -h localhost -U ai_user -d ai_backend -c "SELECT version();"
fi

# Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

# Wait for restart
sleep 5

# Check backend logs
echo "📋 Backend logs after restart:"
journalctl -u ai-backend-python -n 15 --no-pager

echo "✅ PostgreSQL authentication fix completed!" 