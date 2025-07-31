#!/bin/bash

echo "🔧 Setting up local PostgreSQL database..."

# Update package list
sudo apt update

# Install PostgreSQL
echo "📦 Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL service
echo "🚀 Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
echo "🗄️  Creating database and user..."
sudo -u postgres psql << EOF
CREATE DATABASE ai_backend;
CREATE USER ai_user WITH PASSWORD 'ai_password';
GRANT ALL PRIVILEGES ON DATABASE ai_backend TO ai_user;
ALTER USER ai_user CREATEDB;
\q
EOF

# Update .env file with local database URL
echo "📝 Updating .env file..."
cd ~/ai-backend-python
sed -i 's|DATABASE_URL="postgresql://your_actual_username:your_actual_password@your_db_host:5432/your_db_name"|DATABASE_URL="postgresql://ai_user:ai_password@localhost:5432/ai_backend"|' .env

echo "✅ Database setup completed!"
echo "📊 PostgreSQL status:"
sudo systemctl status postgresql --no-pager

echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python

echo "📋 Check backend logs:"
journalctl -u ai-backend-python -n 20 --no-pager 