#!/bin/bash

# Deploy OpenAI Integration with Token Usage System
# This script sets up OpenAI as a fallback when Anthropic tokens are exhausted

set -e

echo "🚀 Deploying OpenAI Integration with Token Usage System"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    print_error "Please run this script from the ai-backend-python directory"
    exit 1
fi

print_status "Starting OpenAI integration deployment..."

# Step 1: Install OpenAI dependency
print_status "Installing OpenAI dependency..."
pip install openai

# Step 2: Check if .env file exists and add OpenAI configuration
print_status "Checking environment configuration..."

if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating one..."
    touch .env
fi

# Add OpenAI configuration to .env if not already present
if ! grep -q "OPENAI_API_KEY" .env; then
    print_status "Adding OpenAI configuration to .env..."
    cat >> .env << EOF

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1
OPENAI_MAX_TOKENS=1024
OPENAI_TEMPERATURE=0.7

# Token Usage Limits
ANTHROPIC_MONTHLY_LIMIT=140000
OPENAI_MONTHLY_LIMIT=9000
ENABLE_OPENAI_FALLBACK=true
OPENAI_FALLBACK_THRESHOLD=0.95
EOF
    print_success "OpenAI configuration added to .env"
else
    print_status "OpenAI configuration already exists in .env"
fi

# Step 3: Initialize token usage service
print_status "Initializing token usage service..."
python -c "
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from app.services.token_usage_service import token_usage_service
from app.core.database import init_database

async def init():
    await init_database()
    await token_usage_service._setup_monthly_tracking()
    print('Token usage service initialized successfully')

asyncio.run(init())
"

# Step 4: Test the integration
print_status "Testing OpenAI integration..."
python test_openai_integration.py

# Step 5: Restart the backend service
print_status "Restarting backend service..."
sudo systemctl restart ai-backend-python

# Step 6: Wait for service to start
print_status "Waiting for service to start..."
sleep 5

# Step 7: Check service status
print_status "Checking service status..."
if sudo systemctl is-active --quiet ai-backend-python; then
    print_success "Backend service is running"
else
    print_error "Backend service failed to start"
    sudo systemctl status ai-backend-python
    exit 1
fi

# Step 8: Test API endpoints
print_status "Testing API endpoints..."

# Test token usage summary
echo "Testing token usage summary endpoint..."
curl -s http://localhost:4000/api/token-usage/summary | jq '.' || echo "Token usage summary endpoint test failed"

# Test provider status
echo "Testing provider status endpoint..."
curl -s http://localhost:4000/api/token-usage/provider-status | jq '.' || echo "Provider status endpoint test failed"

# Test emergency status
echo "Testing emergency status endpoint..."
curl -s http://localhost:4000/api/token-usage/emergency-status | jq '.' || echo "Emergency status endpoint test failed"

print_success "OpenAI Integration Deployment Complete!"
echo ""
echo "📋 Summary:"
echo "✅ OpenAI dependency installed"
echo "✅ Environment configuration updated"
echo "✅ Token usage service initialized"
echo "✅ Backend service restarted"
echo "✅ API endpoints tested"
echo ""
echo "🔧 Configuration:"
echo "   - Anthropic Monthly Limit: 140,000 tokens (70% of 200k)"
echo "   - OpenAI Monthly Limit: 9,000 tokens (30% of 30k)"
echo "   - OpenAI Fallback Threshold: 95% of Anthropic usage"
echo "   - AIs will use OpenAI when Anthropic tokens are exhausted"
echo ""
echo "📊 Monitoring:"
echo "   - Token usage: http://localhost:4000/api/token-usage/summary"
echo "   - Provider status: http://localhost:4000/api/token-usage/provider-status"
echo "   - Emergency status: http://localhost:4000/api/token-usage/emergency-status"
echo ""
echo "🧪 Testing:"
echo "   - Run: python test_openai_integration.py"
echo "   - Test AI call: curl -X POST http://localhost:4000/api/token-usage/test-ai-call"
echo ""
print_warning "⚠️  Remember to set your OPENAI_API_KEY in the .env file!" 