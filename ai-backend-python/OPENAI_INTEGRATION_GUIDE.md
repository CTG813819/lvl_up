# OpenAI Integration with Token Usage System

## Overview

This integration adds OpenAI as a fallback AI provider when Anthropic tokens are exhausted. The system intelligently manages token usage across both providers to ensure continuous AI operation while staying within budget limits.

## Key Features

### 🎯 **Intelligent Provider Selection**
- **Primary**: Anthropic Claude (140,000 tokens/month - 70% of 200k limit)
- **Fallback**: OpenAI GPT-4.1 (9,000 tokens/month - 30% of 30k limit)
- **Threshold**: Switches to OpenAI when Anthropic usage reaches 95%

### 📊 **Token Usage Tracking**
- Real-time monitoring of both Anthropic and OpenAI usage
- Monthly limits enforced per AI agent
- Global usage tracking across all AIs
- Emergency shutdown when limits are exceeded

### 🔄 **Automatic Fallback**
- Seamless switching between providers
- No interruption to AI operations
- Intelligent error handling and retry logic

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
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
```

### Token Limits Breakdown

| Provider | Monthly Limit | Percentage | Usage |
|----------|---------------|------------|-------|
| Anthropic | 140,000 tokens | 70% of 200k | Primary provider |
| OpenAI | 9,000 tokens | 30% of 30k | Fallback provider |

## Architecture

### Service Components

1. **TokenUsageService** - Core token tracking and limit enforcement
2. **OpenAIService** - OpenAI API integration with rate limiting
3. **UnifiedAIService** - Intelligent provider selection
4. **AnthropicService** - Updated with OpenAI fallback

### Provider Selection Logic

```python
# Simplified logic flow
if anthropic_usage_percentage < 95:
    use_anthropic()
elif openai_usage_percentage < 100:
    use_openai()
else:
    raise_exception("Both providers exhausted")
```

## API Endpoints

### Token Usage Monitoring

```bash
# Get overall token usage summary
GET /api/token-usage/summary

# Get usage for specific AI
GET /api/token-usage/ai/{ai_name}

# Get provider status for all AIs
GET /api/token-usage/provider-status

# Get provider status for specific AI
GET /api/token-usage/provider-status/{ai_name}

# Get emergency status
GET /api/token-usage/emergency-status

# Get usage alerts
GET /api/token-usage/alerts
```

### Testing and Management

```bash
# Test AI call with provider selection
POST /api/token-usage/test-ai-call
{
  "ai_name": "imperium",
  "prompt": "Hello, this is a test",
  "preferred_provider": "openai"  # optional
}

# Reset token usage for AI
POST /api/token-usage/reset/{ai_name}

# Get usage history
GET /api/token-usage/history/{ai_name}?months=6
```

## Usage Examples

### Python Code

```python
from app.services.unified_ai_service import unified_ai_service

# Call AI with automatic provider selection
response, provider_info = await unified_ai_service.call_ai(
    prompt="Analyze this code for security vulnerabilities",
    ai_name="guardian"
)

print(f"Provider used: {provider_info['provider']}")
print(f"Reason: {provider_info['reason']}")
print(f"Response: {response}")
```

### API Testing

```bash
# Test provider status
curl http://localhost:4000/api/token-usage/provider-status

# Test AI call
curl -X POST http://localhost:4000/api/token-usage/test-ai-call \
  -H "Content-Type: application/json" \
  -d '{
    "ai_name": "imperium",
    "prompt": "Generate a Flutter widget for user authentication"
  }'
```

## Monitoring and Alerts

### Key Metrics

- **Anthropic Usage**: Percentage of 140k monthly limit
- **OpenAI Usage**: Percentage of 9k monthly limit
- **Provider Recommendations**: Which provider to use for each AI
- **Emergency Status**: System-wide usage and shutdown conditions

### Alert Thresholds

- **Warning**: 80% of Anthropic limit
- **Critical**: 95% of Anthropic limit (triggers OpenAI fallback)
- **Emergency**: 98% of Anthropic limit (potential shutdown)

### Monitoring Dashboard

```bash
# Quick status check
curl http://localhost:4000/api/token-usage/summary | jq '.'

# Provider status
curl http://localhost:4000/api/token-usage/provider-status | jq '.'

# Emergency status
curl http://localhost:4000/api/token-usage/emergency-status | jq '.'
```

## Deployment

### Quick Setup

```bash
# Run the deployment script
chmod +x deploy_openai_integration.sh
./deploy_openai_integration.sh
```

### Manual Setup

```bash
# 1. Install OpenAI dependency
pip install openai

# 2. Update .env file with OpenAI configuration
# (see Configuration section above)

# 3. Initialize token usage service
python -c "
import asyncio
from app.services.token_usage_service import token_usage_service
from app.core.database import init_database

async def init():
    await init_database()
    await token_usage_service._setup_monthly_tracking()
    print('Token usage service initialized')

asyncio.run(init())
"

# 4. Restart backend service
sudo systemctl restart ai-backend-python

# 5. Test integration
python test_openai_integration.py
```

## Testing

### Run Integration Tests

```bash
python test_openai_integration.py
```

### Test Individual Components

```python
# Test provider recommendation
from app.services.token_usage_service import token_usage_service
recommendation = await token_usage_service.get_provider_recommendation("imperium")
print(recommendation)

# Test OpenAI service directly
from app.services.openai_service import openai_service
should_use, reason = await openai_service.should_use_openai("imperium")
print(f"Should use OpenAI: {should_use}")
print(f"Reason: {reason}")
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```
   Error: OPENAI_API_KEY environment variable not set
   Solution: Add your OpenAI API key to .env file
   ```

2. **Token Limits Exceeded**
   ```
   Error: Token limit reached for imperium
   Solution: Check usage and consider resetting or increasing limits
   ```

3. **Provider Not Available**
   ```
   Error: OpenAI not available for imperium: both_exhausted
   Solution: Both providers have reached their limits
   ```

### Debug Commands

```bash
# Check service status
sudo systemctl status ai-backend-python

# View logs
sudo journalctl -u ai-backend-python -n 100 --no-pager

# Test API endpoints
curl http://localhost:4000/api/token-usage/summary

# Check database tables
python -c "
from app.core.database import get_session
from app.models.sql_models import TokenUsage
import asyncio

async def check_tables():
    async with get_session() as session:
        result = await session.execute('SELECT COUNT(*) FROM token_usage')
        print(f'Token usage records: {result.scalar()}')

asyncio.run(check_tables())
"
```

## Performance Considerations

### Rate Limiting

- **Anthropic**: 42 requests/minute, 3,400 requests/day
- **OpenAI**: 42 requests/minute, 3,400 requests/day
- **Token Limits**: 17,000 tokens per request (both providers)

### Optimization Tips

1. **Batch Requests**: Group multiple AI calls when possible
2. **Cache Responses**: Store common AI responses to reduce token usage
3. **Monitor Usage**: Regularly check usage to avoid hitting limits
4. **Provider Selection**: Use preferred_provider parameter for specific needs

## Security

### API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Rotate keys regularly
- Use least privilege access

### Rate Limiting

- Built-in rate limiting prevents API abuse
- Automatic retry logic handles temporary failures
- Circuit breaker pattern prevents cascading failures

## Future Enhancements

### Planned Features

1. **Dynamic Limits**: Adjust limits based on usage patterns
2. **Cost Optimization**: Choose providers based on cost per token
3. **Advanced Analytics**: Detailed usage analytics and reporting
4. **Multi-Provider Support**: Add support for additional AI providers

### Monitoring Improvements

1. **Real-time Dashboards**: Web-based monitoring interface
2. **Alert Notifications**: Email/SMS alerts for limit approaching
3. **Usage Forecasting**: Predict usage patterns and adjust limits
4. **Cost Tracking**: Track costs per provider and AI agent

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the logs: `sudo journalctl -u ai-backend-python -n 100`
3. Test the integration: `python test_openai_integration.py`
4. Check API endpoints: `curl http://localhost:4000/api/token-usage/summary`

---

**Last Updated**: 2025-01-08
**Version**: 1.0.0
**Status**: Production Ready ✅ 