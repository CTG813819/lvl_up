# Token Usage Limits and Monitoring

## Overview

The AI backend now implements strict token usage limits to prevent overuse of Anthropic API tokens and ensure cost control. The system enforces multiple levels of limits and provides real-time monitoring.

## Limits Configuration

### Global Limits
- **Monthly Limit**: 200,000 tokens (enforced at 140,000 = 70%)
- **Daily Limit**: ~4,667 tokens (monthly / 30 days)
- **Hourly Limit**: ~194 tokens (daily / 24 hours)
- **Request Limit**: 1,000 tokens per request

### Thresholds
- **Warning**: 80% of enforced limit (112,000 tokens)
- **Critical**: 95% of enforced limit (133,000 tokens)
- **Emergency Shutdown**: 98% of enforced limit (137,200 tokens)

## Enforcement System

### 1. Pre-Request Validation
Before any Anthropic API call, the system:
1. Estimates token usage for the request
2. Checks if the request would exceed limits
3. Validates against multiple thresholds (monthly, daily, hourly)
4. Blocks requests that would exceed limits

### 2. Real-Time Tracking
- All token usage is logged with detailed metadata
- Usage is tracked per AI type and globally
- Failed requests are also logged for monitoring

### 3. Emergency Controls
- **Emergency Shutdown**: Blocks all requests at 98% usage
- **Critical Level**: Sends alerts and restricts large requests
- **Warning Level**: Sends alerts and monitors closely

## Monitoring Tools

### 1. Real-Time Monitor
```bash
python monitor_token_usage.py
```
- Checks usage every 60 seconds
- Sends alerts at warning/critical/emergency levels
- Logs alerts to `token_usage_alerts.json`

### 2. Usage Status
```bash
python reset_token_usage.py
```
- Shows current usage for all AI types
- Displays emergency status
- Shows remaining tokens

### 3. Reset Usage (Testing)
```bash
python reset_token_usage.py reset
```
- Resets all token usage to zero
- Useful for testing and development

## API Endpoints

### Token Usage Status
- `GET /api/token-usage/monthly` - All AI usage
- `GET /api/token-usage/monthly/{ai_type}` - Specific AI usage
- `GET /api/token-usage/alerts` - Current alerts
- `GET /api/token-usage/summary` - Usage summary
- `GET /api/token-usage/limits` - Current limits

### Emergency Status
- `GET /api/token-usage/status/{ai_type}` - AI-specific status

## Implementation Details

### Token Estimation
The system estimates token usage using:
- Input tokens: `len(prompt.split()) * 1.3` (30% buffer)
- Output tokens: `max_tokens` parameter
- Total: `input_tokens + output_tokens`

### Rate Limiting
- **Per-minute**: 42 requests (85% of 50 limit)
- **Per-day**: 3,400 requests (85% of 4,000 limit)
- **Per-request**: 17,000 tokens (85% of 20,000 limit)

### Database Tables
- `token_usage`: Monthly tracking per AI type
- `token_usage_logs`: Detailed request logs

## Alert System

### Alert Levels
1. **Warning (80%)**: Monitor closely
2. **Critical (95%)**: Restrict large requests
3. **Emergency (98%)**: Block all requests

### Alert Actions
- Console output with detailed information
- JSON log file (`token_usage_alerts.json`)
- Status updates via API endpoints

## Cost Control Features

### 1. Strict Enforcement
- No requests allowed if limits would be exceeded
- Pre-validation of all requests
- Multiple threshold checks

### 2. Usage Tracking
- Detailed logging of all requests
- Failed request tracking
- Per-AI type monitoring

### 3. Emergency Controls
- Automatic shutdown at 98% usage
- Critical level restrictions
- Warning level monitoring

## Troubleshooting

### Common Issues

1. **"Token limit reached" errors**
   - Check current usage: `python reset_token_usage.py`
   - Reset if needed: `python reset_token_usage.py reset`
   - Monitor usage: `python monitor_token_usage.py`

2. **High usage alerts**
   - Review recent requests in logs
   - Check which AI types are using most tokens
   - Consider reducing request frequency

3. **Database connection issues**
   - Ensure database is running
   - Check token usage tables exist
   - Verify database permissions

### Debug Commands

```bash
# Check current usage
python reset_token_usage.py

# Reset usage for testing
python reset_token_usage.py reset

# Monitor usage in real-time
python monitor_token_usage.py

# Check API endpoints
curl http://localhost:4000/api/token-usage/summary
```

## Best Practices

### 1. Regular Monitoring
- Run the monitor script in production
- Check usage daily
- Set up alerts for critical levels

### 2. Testing
- Reset usage before testing
- Monitor usage during tests
- Use smaller requests for testing

### 3. Production
- Keep monitor running
- Set up automated alerts
- Regular usage reviews

## Configuration

### Environment Variables
```bash
# Token limits (in token_usage_service.py)
GLOBAL_MONTHLY_LIMIT = 200_000
ENFORCED_GLOBAL_LIMIT = 140_000  # 70%
WARNING_THRESHOLD = 80.0
CRITICAL_THRESHOLD = 95.0
EMERGENCY_SHUTDOWN_THRESHOLD = 98.0
```

### Monitoring Settings
```python
# In monitor_token_usage.py
check_interval = 60  # seconds
```

## Future Enhancements

### Planned Features
1. **Web Dashboard**: Real-time usage visualization
2. **Email Alerts**: Automated email notifications
3. **Usage Analytics**: Detailed usage patterns
4. **Cost Prediction**: Estimate monthly costs
5. **Dynamic Limits**: Adjust limits based on usage

### Integration Points
1. **Slack Notifications**: Send alerts to Slack
2. **Grafana Dashboards**: Visual monitoring
3. **Prometheus Metrics**: Metrics collection
4. **Webhook Alerts**: Custom alert endpoints 