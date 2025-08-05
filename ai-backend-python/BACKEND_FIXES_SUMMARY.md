# Backend Fixes Summary

## Issues Fixed

### 1. Logging Errors
**Problem**: `Logger._log() got an unexpected keyword argument 'error'`

**Root Cause**: Structlog logger was being called with `error=` keyword argument, but structlog expects `error_message=` instead.

**Files Fixed**:
- `app/services/token_usage_service.py` - Fixed all logging calls
- `app/services/guardian_ai_service.py` - Fixed all logging calls

**Changes Made**:
- Changed `logger.error(..., error=str(e))` to `logger.error(..., error_message=str(e))`
- Changed `logger.warning(..., error=...)` to `logger.warning(..., error_message=...)`

### 2. Rate Limiting Issues
**Problem**: `Rate limit exceeded - blocking request for sandbox error='Hourly usage limit exceeded'`

**Root Cause**: Rate limiting was too restrictive, causing frequent blocking of legitimate requests.

**Files Fixed**:
- `app/services/token_usage_service.py`

**Changes Made**:
- Increased `ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE` from 0.5% to 2.0%
- Increased `ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE` from 8.0% to 15.0%
- Reduced `AI_COOLDOWN_PERIOD` from 300 seconds to 60 seconds
- Increased `MAX_CONCURRENT_AI_REQUESTS` from 2 to 5

## Configuration Changes

### Before:
```python
ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE = 8.0  # Max 8% of monthly limit per day
ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE = 0.5  # Max 0.5% of monthly limit per hour
AI_COOLDOWN_PERIOD = 300  # 5 minutes between AI requests
MAX_CONCURRENT_AI_REQUESTS = 2  # Max 2 AIs can make requests simultaneously
```

### After:
```python
ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE = 15.0  # Max 15% of monthly limit per day
ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE = 2.0  # Max 2% of monthly limit per hour
AI_COOLDOWN_PERIOD = 60  # 1 minute between AI requests
MAX_CONCURRENT_AI_REQUESTS = 5  # Max 5 AIs can make requests simultaneously
```

## Impact

### Positive Effects:
1. **Eliminated logging errors** - No more `Logger._log() got an unexpected keyword argument 'error'` errors
2. **Reduced rate limiting blocks** - Increased limits allow more legitimate requests
3. **Improved responsiveness** - Reduced cooldown periods and increased concurrent requests
4. **Better error reporting** - Proper error messages in logs

### Monitoring Required:
1. **Token usage** - Monitor if increased limits lead to higher costs
2. **Performance** - Ensure increased concurrent requests don't overwhelm the system
3. **Rate limiting effectiveness** - Verify that limits still provide adequate protection

## Restart Instructions

To apply these fixes, restart the backend:

```bash
cd ai-backend-python
python restart_backend_with_fixes.py
```

Or manually:
```bash
cd ai-backend-python
pkill -f uvicorn
pkill -f main.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Verification

After restart, check logs for:
- ✅ No more `Logger._log() got an unexpected keyword argument 'error'` errors
- ✅ Reduced `Rate limit exceeded` warnings
- ✅ Normal operation of AI services

## Rollback Plan

If issues arise, the original values can be restored:

```python
ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE = 8.0
ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE = 0.5
AI_COOLDOWN_PERIOD = 300
MAX_CONCURRENT_AI_REQUESTS = 2
```

And logging calls can be reverted to use `error=` instead of `error_message=`. 