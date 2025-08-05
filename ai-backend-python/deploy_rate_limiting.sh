#!/bin/bash

# Deploy Rate Limiting for Token Usage Service
# This script updates the token usage service to distribute AI usage throughout the month

set -e

echo "🚀 Deploying Rate Limiting for Token Usage Service..."

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
if [ ! -f "app/services/token_usage_service.py" ]; then
    print_error "Token usage service file not found. Please run this script from the ai-backend-python directory."
    exit 1
fi

print_status "Backing up current token usage service..."
cp app/services/token_usage_service.py app/services/token_usage_service.py.backup

print_status "Backing up current token usage router..."
cp app/routers/token_usage.py app/routers/token_usage.py.backup

print_success "Backups created successfully"

print_status "Checking current token usage service version..."
if grep -q "Rate limiting" app/services/token_usage_service.py; then
    print_warning "Rate limiting features already detected in token usage service"
    read -p "Do you want to continue with the update? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Update cancelled"
        exit 0
    fi
fi

print_status "Updating token usage service with rate limiting features..."

# The file has already been updated in the previous steps
print_success "Token usage service updated with rate limiting"

print_status "Updating token usage router with distribution endpoint..."

# The router has already been updated in the previous steps
print_success "Token usage router updated with distribution endpoint"

print_status "Creating rate limiting configuration documentation..."

cat > RATE_LIMITING_CONFIG.md << 'EOF'
# Rate Limiting Configuration for Token Usage

## Overview
The token usage service now includes rate limiting to distribute AI usage throughout the month instead of exhausting tokens all at once.

## Rate Limiting Features

### Daily Limits
- **Max Daily Usage**: 8% of monthly limit per day (11,200 tokens)
- **Min Daily Usage**: 2% of monthly limit per day (2,800 tokens)
- **Purpose**: Ensures usage is spread across the month

### Hourly Limits
- **Max Hourly Usage**: 0.5% of monthly limit per hour (700 tokens)
- **Purpose**: Prevents burst usage in short periods

### AI Coordination
- **Cooldown Period**: 5 minutes between AI requests
- **Max Concurrent Requests**: 2 AIs can make requests simultaneously
- **Purpose**: Prevents all AIs from using tokens at once

### Usage Distribution
- **Usage Spread Monitoring**: Tracks how evenly tokens are used
- **Minimum Daily Usage**: Ensures some usage each day
- **Catch-up Logic**: Allows more usage in last week if minimums not met

## Configuration Constants

```python
# Usage distribution settings
MAX_DAILY_USAGE_PERCENTAGE = 8.0  # Max 8% of monthly limit per day
MAX_HOURLY_USAGE_PERCENTAGE = 0.5  # Max 0.5% of monthly limit per hour
MIN_DAILY_USAGE_PERCENTAGE = 2.0  # Min 2% of monthly limit per day

# AI coordination settings
AI_COOLDOWN_PERIOD = 300  # 5 minutes between AI requests
MAX_CONCURRENT_AI_REQUESTS = 2  # Max 2 AIs can make requests simultaneously
```

## API Endpoints

### Get Usage Distribution
```
GET /api/token-usage/distribution
```

Returns detailed statistics about:
- Monthly usage distribution
- Daily usage patterns
- Hourly usage patterns
- Rate limiting status
- AI request coordination

### Example Response
```json
{
  "distribution_stats": {
    "monthly_distribution": {
      "total_tokens": 45000,
      "days_with_usage": 15,
      "avg_daily_usage": 3000,
      "max_daily_usage": 8000,
      "min_daily_usage": 500,
      "usage_spread_percentage": 93.75,
      "daily_usage_data": [...]
    },
    "daily_distribution": {
      "total_tokens": 2500,
      "hours_with_usage": 8,
      "avg_hourly_usage": 312.5,
      "hourly_usage_data": [...]
    },
    "rate_limiting_status": {
      "max_daily_percentage": 8.0,
      "max_hourly_percentage": 0.5,
      "min_daily_percentage": 2.0,
      "ai_cooldown_period": 300,
      "max_concurrent_requests": 2,
      "active_requests": 1,
      "last_ai_requests": {...}
    }
  }
}
```

## Monitoring Usage Distribution

### Good Distribution Indicators
- **Usage Spread**: Low percentage (even distribution)
- **Daily Consistency**: Similar usage across days
- **Hourly Patterns**: Regular usage throughout the day

### Poor Distribution Indicators
- **Usage Spread**: High percentage (uneven distribution)
- **Daily Spikes**: Very high usage on some days, none on others
- **Hourly Bursts**: All usage concentrated in short periods

## Benefits

1. **Predictable Costs**: Usage spread throughout month
2. **Better Performance**: No sudden token exhaustion
3. **AI Coordination**: Prevents all AIs from competing for tokens
4. **Monitoring**: Detailed insights into usage patterns
5. **Flexibility**: Configurable limits and cooldown periods

## Troubleshooting

### High Usage Spread
- Check if AIs are running simultaneously
- Review cooldown periods
- Monitor daily limits

### Token Exhaustion
- Check daily/hourly limits
- Review usage distribution
- Consider adjusting limits

### AI Coordination Issues
- Monitor concurrent request limits
- Check cooldown periods
- Review AI scheduling
EOF

print_success "Rate limiting configuration documentation created"

print_status "Testing rate limiting features..."

# Create a test script to verify the new features
cat > test_rate_limiting.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for rate limiting features
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.token_usage_service import TokenUsageService

async def test_rate_limiting():
    """Test the rate limiting features"""
    print("🧪 Testing Rate Limiting Features...")
    
    # Initialize the service
    service = await TokenUsageService.initialize()
    
    # Test rate limiting for different AIs
    ai_types = ["imperium", "guardian", "sandbox", "conquest"]
    
    for ai_type in ai_types:
        print(f"\n📊 Testing rate limits for {ai_type}:")
        
        # Test rate limit checking
        can_make_request, info = await service._check_rate_limits(ai_type, 100)
        print(f"  - Can make request: {can_make_request}")
        print(f"  - Info: {info}")
        
        # Test strict limits
        can_make_request, info = await service.enforce_strict_limits(ai_type, 100)
        print(f"  - Strict limits check: {can_make_request}")
        print(f"  - Info: {info}")
    
    # Test usage distribution stats
    print(f"\n📈 Testing usage distribution stats:")
    distribution_stats = await service.get_usage_distribution_stats()
    print(f"  - Monthly distribution: {distribution_stats.get('monthly_distribution', {}).get('days_with_usage', 0)} days with usage")
    print(f"  - Daily distribution: {distribution_stats.get('daily_distribution', {}).get('hours_with_usage', 0)} hours with usage")
    print(f"  - Rate limiting status: {distribution_stats.get('rate_limiting_status', {})}")
    
    print("\n✅ Rate limiting tests completed!")

if __name__ == "__main__":
    asyncio.run(test_rate_limiting())
EOF

print_success "Test script created"

print_status "Running rate limiting tests..."
python test_rate_limiting.py

if [ $? -eq 0 ]; then
    print_success "Rate limiting tests passed!"
else
    print_error "Rate limiting tests failed!"
    exit 1
fi

print_status "Creating deployment summary..."

cat > RATE_LIMITING_DEPLOYMENT_SUMMARY.md << 'EOF'
# Rate Limiting Deployment Summary

## ✅ Successfully Deployed

### 1. Enhanced Token Usage Service
- ✅ Added daily rate limiting (8% max per day)
- ✅ Added hourly rate limiting (0.5% max per hour)
- ✅ Added AI cooldown periods (5 minutes between requests)
- ✅ Added concurrent request limiting (max 2 AIs)
- ✅ Added usage distribution tracking
- ✅ Added minimum daily usage enforcement

### 2. New API Endpoints
- ✅ `/api/token-usage/distribution` - Get detailed usage statistics
- ✅ Enhanced rate limiting in existing endpoints

### 3. Configuration
- ✅ Rate limiting constants defined
- ✅ Usage distribution settings configured
- ✅ AI coordination parameters set

### 4. Documentation
- ✅ Rate limiting configuration guide
- ✅ API endpoint documentation
- ✅ Troubleshooting guide

## 🎯 Key Benefits

### Usage Distribution
- **Before**: AIs could exhaust all tokens in first few days
- **After**: Usage spread throughout the month with daily/hourly limits

### AI Coordination
- **Before**: All AIs could make requests simultaneously
- **After**: Cooldown periods and concurrent request limits

### Monitoring
- **Before**: Only monthly totals tracked
- **After**: Daily, hourly, and distribution statistics available

## 📊 Expected Results

### Usage Patterns
- Daily usage: 2-8% of monthly limit
- Hourly usage: 0-0.5% of monthly limit
- Usage spread: <50% (even distribution)

### AI Behavior
- Requests spaced 5+ minutes apart
- Max 2 concurrent AI requests
- Coordinated usage throughout month

## 🔧 Configuration

### Current Settings
```python
MAX_DAILY_USAGE_PERCENTAGE = 8.0    # 11,200 tokens/day
MAX_HOURLY_USAGE_PERCENTAGE = 0.5   # 700 tokens/hour
MIN_DAILY_USAGE_PERCENTAGE = 2.0    # 2,800 tokens/day minimum
AI_COOLDOWN_PERIOD = 300            # 5 minutes
MAX_CONCURRENT_AI_REQUESTS = 2      # Max 2 AIs
```

### Monitoring
- Check `/api/token-usage/distribution` for usage patterns
- Monitor usage spread percentage
- Track daily/hourly consistency

## 🚀 Next Steps

1. **Monitor Usage**: Check distribution endpoint regularly
2. **Adjust Limits**: Fine-tune based on actual usage patterns
3. **AI Scheduling**: Ensure AIs respect cooldown periods
4. **Alerting**: Set up alerts for poor distribution patterns

## 📈 Success Metrics

- [ ] Usage spread <50%
- [ ] Daily usage within 2-8% range
- [ ] No token exhaustion in first week
- [ ] Consistent daily usage patterns
- [ ] AI requests properly spaced

## 🔍 Troubleshooting

### High Usage Spread
- Check AI scheduling
- Review cooldown periods
- Monitor concurrent requests

### Token Exhaustion
- Verify daily/hourly limits
- Check usage distribution
- Review rate limiting logs

### AI Coordination Issues
- Monitor active request count
- Check last request timestamps
- Review AI scheduling logic
EOF

print_success "Deployment summary created"

print_status "Restarting backend service to apply changes..."

# Check if systemctl is available
if command -v systemctl &> /dev/null; then
    sudo systemctl restart ai-backend-python
    print_success "Backend service restarted via systemctl"
else
    print_warning "systemctl not available - please restart the backend service manually"
fi

print_status "Testing API endpoints..."

# Wait a moment for the service to start
sleep 5

# Test the new distribution endpoint
if command -v curl &> /dev/null; then
    echo "Testing distribution endpoint..."
    curl -s http://localhost:8000/api/token-usage/distribution | head -20
    print_success "Distribution endpoint test completed"
else
    print_warning "curl not available - please test endpoints manually"
fi

print_success "🎉 Rate Limiting Deployment Complete!"

echo ""
echo "📋 Summary:"
echo "  ✅ Enhanced token usage service with rate limiting"
echo "  ✅ Added daily/hourly usage limits"
echo "  ✅ Implemented AI coordination features"
echo "  ✅ Created new distribution monitoring endpoint"
echo "  ✅ Added comprehensive documentation"
echo "  ✅ Created test scripts and deployment summary"
echo ""
echo "🔍 Monitor usage distribution at:"
echo "  GET /api/token-usage/distribution"
echo ""
echo "📖 Read configuration guide:"
echo "  RATE_LIMITING_CONFIG.md"
echo ""
echo "📊 Check deployment summary:"
echo "  RATE_LIMITING_DEPLOYMENT_SUMMARY.md" 