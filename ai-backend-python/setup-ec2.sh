#!/bin/bash

echo "🚀 Setting up EC2 instance for AI Learning Backend..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js 18.x
echo "📦 Installing Node.js 18.x..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
echo "📦 Installing PM2..."
sudo npm install -g pm2

# Install MongoDB
echo "📦 Installing MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start and enable MongoDB
echo "🔧 Starting MongoDB..."
sudo systemctl start mongod
sudo systemctl enable mongod

# Install nginx for reverse proxy (optional)
echo "📦 Installing nginx..."
sudo apt-get install -y nginx

# Configure nginx
echo "🔧 Configuring nginx..."
sudo tee /etc/nginx/sites-available/ai-learning-backend << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/ai-learning-backend /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /home/ubuntu/ai-learning-backend
cd /home/ubuntu/ai-learning-backend

# Set up PM2 startup
echo "🔧 Setting up PM2 startup..."
pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u ubuntu --hp /home/ubuntu

echo "✅ EC2 setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy your backend using the deployment script"
echo "2. Update your Flutter app with this EC2 IP"
echo "3. Test the connection"
echo ""
echo "🔍 Useful commands:"
echo "- Check PM2 status: pm2 status"
echo "- View logs: pm2 logs ai-learning-backend"
echo "- Restart app: pm2 restart ai-learning-backend"
echo "- Check MongoDB: sudo systemctl status mongod" 