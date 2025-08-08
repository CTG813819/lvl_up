# Deploy Token Usage Limits to EC2 Instance

## Quick Deployment

Run this command on your EC2 instance to update the token usage system:

```bash
# Download and run the update script
curl -s https://raw.githubusercontent.com/your-repo/update_token_limits_ec2.sh | bash
```

## Manual Deployment Steps

If you prefer to deploy manually, follow these steps:

### 1. SSH into your EC2 instance
```bash
ssh ubuntu@your-ec2-instance.com
```

### 2. Navigate to the backend directory
```bash
cd /home/ubuntu/ai-backend-python
```

### 3. Create backup
```bash
mkdir -p /home/ubuntu/backups/token_limits_$(date +%Y%m%d_%H%M%S)
cp app/services/token_usage_service.py /home/ubuntu/backups/token_limits_$(date +%Y%m%d_%H%M%S)/
cp app/services/anthropic_service.py /home/ubuntu/backups/token_limits_$(date +%Y%m%d_%H%M%S)/
```

### 4. Update the token usage service
Copy the updated `token_usage_service.py` file to:
```
/home/ubuntu/ai-backend-python/app/services/token_usage_service.py
```

### 5. Update the anthropic service
Copy the updated `anthropic_service.py` file to:
```
/home/ubuntu/ai-backend-python/app/services/anthropic_service.py
```

### 6. Restart the backend service
```bash
sudo systemctl restart ai-backend-python
```

### 7. Initialize token tracking
```bash
cd /home/ubuntu/ai-backend-python
python -c "import asyncio; from app.services.token_usage_service import token_usage_service; from app.core.database import init_database; asyncio.run(init_database()); asyncio.run(token_usage_service._setup_monthly_tracking()); print('Token tracking initialized')"
```

## Verification

### Check current usage
```bash
cd /home/ubuntu/ai-backend-python
python reset_token_usage.py
```

### Monitor usage in real-time
```bash
cd /home/ubuntu/ai-backend-python
python monitor_token_usage.py
```

### Reset usage for testing
```bash
cd /home/ubuntu/ai-backend-python
python reset_token_usage.py reset
```

## New Token Limits

The system now enforces these strict limits:

- **Monthly Limit**: 140,000 tokens (70% of 200,000)
- **Daily Limit**: ~4,667 tokens
- **Hourly Limit**: ~194 tokens
- **Request Limit**: 1,000 tokens per request

### Alert Thresholds
- **Warning**: 80% (112,000 tokens)
- **Critical**: 95% (133,000 tokens)
- **Emergency Shutdown**: 98% (137,200 tokens)

## What This Fixes

1. **Prevents overuse**: AIs can no longer exceed monthly limits
2. **Real-time monitoring**: Track usage as it happens
3. **Automatic blocking**: Requests are blocked before they exceed limits
4. **Emergency controls**: System shuts down at 98% usage
5. **Detailed tracking**: Log all requests with metadata

## Monitoring Commands

### Check API endpoints
```bash
curl http://localhost:4000/api/token-usage/summary
curl http://localhost:4000/api/token-usage/alerts
```

### View logs
```bash
sudo journalctl -u ai-backend-python -n 100 --no-pager
```

### Check service status
```bash
sudo systemctl status ai-backend-python
```

## Troubleshooting

### If the service won't start
```bash
# Check logs
sudo journalctl -u ai-backend-python -n 50 --no-pager

# Restart with verbose logging
sudo systemctl restart ai-backend-python
sudo journalctl -u ai-backend-python -f
```

### If token tracking isn't working
```bash
# Check database connection
cd /home/ubuntu/ai-backend-python
python -c "import asyncio; from app.core.database import init_database; asyncio.run(init_database()); print('Database connected')"

# Initialize tracking manually
python -c "import asyncio; from app.services.token_usage_service import token_usage_service; asyncio.run(token_usage_service._setup_monthly_tracking()); print('Tracking initialized')"
```

### If you need to reset everything
```bash
cd /home/ubuntu/ai-backend-python
python reset_token_usage.py reset
```

## Success Indicators

After deployment, you should see:

1. ✅ Backend service restarts without errors
2. ✅ Token tracking initializes successfully
3. ✅ Current usage shows 0 tokens (if reset)
4. ✅ Monitor script runs without errors
5. ✅ API endpoints return usage data

## Next Steps

1. **Monitor usage**: Run `python monitor_token_usage.py` to watch usage
2. **Set up alerts**: Configure monitoring for production
3. **Review limits**: Adjust limits based on your needs
4. **Test enforcement**: Try making requests to verify blocking works

The system will now prevent the AIs from exceeding the monthly Anthropic token limit and provide real-time monitoring of usage. 