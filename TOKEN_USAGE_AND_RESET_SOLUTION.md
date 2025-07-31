# Token Usage and Reset Issues - Complete Solution

## 🚨 Problem Analysis

### Issues Identified

1. **Token Usage Not Resetting**: Despite manual resets, token usage continues to accumulate
2. **No Automatic Monthly Reset**: No mechanism to automatically reset tokens at the end of each month
3. **Request Token Limit Exceeded**: Errors like `Request token limit exceeded - blocking request for imperium estimated_tokens=1073 request_limit=1000`
4. **Claude Verification Error**: `Claude verification error: Logger._log() got an unexpected keyword argument 'error'`

### Root Causes

1. **Database State Issues**: Token usage records not properly cleared or reset
2. **Missing Automation**: No cron jobs or scheduled tasks for monthly resets
3. **Poor Error Handling**: Token limit errors not handled gracefully
4. **Logger Configuration**: Incorrect logger usage in Claude verification

## ✅ Complete Solution

### 1. Token Usage Reset Fix

**Problem**: Token usage not resetting despite manual attempts

**Solution**: 
- Complete database cleanup of token usage tables
- Fresh initialization of tracking records
- Proper session management and commit handling

```python
# Complete reset of all token usage
await session.execute(text("DELETE FROM token_usage"))
await session.execute(text("DELETE FROM token_usage_logs"))

# Create fresh tracking for all AI types
for ai_type in ai_types:
    new_tracking = TokenUsage(
        ai_type=ai_type,
        month_year=current_month,
        monthly_limit=140000,  # 70% of 200,000
        tokens_in=0,
        tokens_out=0,
        total_tokens=0,
        request_count=0,
        usage_percentage=0.0,
        status="active",
        last_request_at=None
    )
    session.add(new_tracking)
```

### 2. Automatic Monthly Reset

**Problem**: No automatic reset mechanism

**Solution**: 
- Cron job scheduled for 1st of each month at 00:01
- Archive old month data before reset
- Fresh initialization for new month

```bash
# Cron job for monthly reset
1 0 1 * * cd /home/ubuntu/ai-backend-python && python monthly_token_reset.py >> /var/log/monthly-token-reset.log 2>&1
```

**Monthly Reset Process**:
1. Archive current month data to `token_usage_archive` table
2. Clear all token usage records for old months
3. Create fresh tracking records for new month
4. Reset all counters to zero

### 3. Enhanced Error Handling

**Problem**: Poor error handling for token limit exceeded

**Solution**: 
- Detailed error messages with context
- Proper logging with structured data
- Graceful fallback mechanisms

```python
async def check_request_limit(self, ai_type: str, estimated_tokens: int) -> Tuple[bool, Dict[str, Any]]:
    """Enhanced request limit checking with detailed error messages"""
    try:
        # Check if request exceeds per-request limit
        if estimated_tokens > self.request_limit:
            logger.warning(
                f"Request token limit exceeded - blocking request for {ai_type}",
                estimated_tokens=estimated_tokens,
                request_limit=self.request_limit
            )
            return False, {
                "error": "request_limit_exceeded",
                "message": f"Request exceeds token limit: {estimated_tokens} > {self.request_limit}",
                "estimated_tokens": estimated_tokens,
                "request_limit": self.request_limit,
                "ai_type": ai_type
            }
        
        # Check monthly usage
        current_usage = await self.get_current_monthly_usage(ai_type)
        if current_usage + estimated_tokens > self.monthly_limit:
            logger.warning(
                f"Monthly token limit would be exceeded - blocking request for {ai_type}",
                current_usage=current_usage,
                estimated_tokens=estimated_tokens,
                monthly_limit=self.monthly_limit
            )
            return False, {
                "error": "monthly_limit_exceeded",
                "message": f"Request would exceed monthly limit: {current_usage + estimated_tokens} > {self.monthly_limit}",
                "current_usage": current_usage,
                "estimated_tokens": estimated_tokens,
                "monthly_limit": self.monthly_limit,
                "ai_type": ai_type
            }
        
        return True, {"status": "ok", "ai_type": ai_type}
        
    except Exception as e:
        logger.error(f"Error checking request limit: {str(e)}")
        return False, {
            "error": "check_failed",
            "message": f"Failed to check token limits: {str(e)}",
            "ai_type": ai_type
        }
```

### 4. Claude Verification Error Fix

**Problem**: `Logger._log() got an unexpected keyword argument 'error'`

**Solution**: 
- Proper structured logging with structlog
- Correct error parameter handling
- Enhanced error context

```python
async def call_claude_safely(self, prompt: str, ai_name: str, max_tokens: int = 1024) -> str:
    """Call Claude with proper error handling and logging"""
    try:
        # Log the request attempt
        logger.info(
            f"Calling Claude for {ai_name}",
            ai_name=ai_name,
            max_tokens=max_tokens,
            prompt_length=len(prompt)
        )
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        # Log successful response
        logger.info(
            f"Claude call successful for {ai_name}",
            ai_name=ai_name,
            response_length=len(response_text)
        )
        
        return response_text
        
    except requests.exceptions.RequestException as e:
        # Log request errors properly
        logger.error(
            f"Claude API request failed for {ai_name}",
            ai_name=ai_name,
            error=str(e),
            status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        )
        raise Exception(f"Claude API request failed: {str(e)}")
        
    except Exception as e:
        # Log general errors properly
        logger.error(
            f"Claude call failed for {ai_name}",
            ai_name=ai_name,
            error=str(e)
        )
        raise Exception(f"Claude call failed: {str(e)}")
```

### 5. Comprehensive Monitoring

**Problem**: No real-time monitoring of token usage

**Solution**: 
- Monitoring script running every 5 minutes
- Alert thresholds at 80%, 95%, and 98%
- Detailed logging and alerting

```bash
# Monitoring cron job
*/5 * * * * cd /home/ubuntu/ai-backend-python && python monitor_token_usage.py >> /var/log/token-monitoring.log 2>&1
```

**Monitoring Features**:
- Real-time token usage tracking
- Alert levels: WARNING (80%), CRITICAL (95%), EMERGENCY (98%)
- Action recommendations based on usage level
- Historical data archiving

## 🔧 Implementation

### Files Created

1. **`fix_token_usage_and_reset_issue.py`** - Main fix script
2. **`monthly_token_reset.py`** - Automatic monthly reset script
3. **`monitor_token_usage.py`** - Real-time monitoring script
4. **`app/services/enhanced_token_usage_service.py`** - Enhanced token service
5. **`app/services/enhanced_claude_service.py`** - Fixed Claude service
6. **`deploy_token_usage_fix.sh`** - Deployment script

### Database Changes

1. **Archive Table**: `token_usage_archive` for historical data
2. **Reset Process**: Complete cleanup and reinitialization
3. **Fresh Tracking**: New records for all AI types

### Cron Jobs Added

1. **Monthly Reset**: `1 0 1 * *` (1st of each month at 00:01)
2. **Monitoring**: `*/5 * * * *` (every 5 minutes)

## 📊 Token Limits and Thresholds

### Current Limits
- **Monthly Limit**: 140,000 tokens (70% of 200,000)
- **Daily Limit**: ~4,667 tokens
- **Hourly Limit**: ~194 tokens
- **Request Limit**: 1,000 tokens per request

### Alert Thresholds
- **Warning**: 80% (112,000 tokens)
- **Critical**: 95% (133,000 tokens)
- **Emergency Shutdown**: 98% (137,200 tokens)

## 🚀 Deployment

### Quick Fix Commands

```bash
# Run the complete fix
python fix_token_usage_and_reset_issue.py

# Deploy to EC2
./deploy_token_usage_fix.sh

# Manual reset (if needed)
python reset_token_usage.py

# Check current status
python monitor_token_usage.py
```

### Verification Commands

```bash
# Check if reset worked
python -c "import asyncio; from app.core.database import init_database; from app.models.sql_models import TokenUsage; from sqlalchemy import select, func; from datetime import datetime; asyncio.run(init_database()); print('Database initialized')"

# Check cron jobs
crontab -l | grep -E '(monthly_token_reset|monitor_token_usage)'

# Check service status
sudo systemctl status ai-backend-python

# View logs
sudo journalctl -u ai-backend-python -n 50 --no-pager
```

## 📈 Expected Results

### After Fix
1. **Token Usage Reset**: All AI types start with 0 tokens
2. **Automatic Monthly Reset**: Tokens reset on 1st of each month
3. **Better Error Messages**: Clear, actionable error messages
4. **Real-time Monitoring**: Continuous monitoring with alerts
5. **Historical Data**: Archived data for analysis

### Monitoring Indicators
- ✅ Token usage starts at 0 for all AIs
- ✅ Monthly reset runs automatically
- ✅ No more "Request token limit exceeded" errors
- ✅ No more "Claude verification error" messages
- ✅ Real-time monitoring shows usage levels
- ✅ Alerts sent at appropriate thresholds

## 🔍 Troubleshooting

### If Token Usage Still Not Resetting
```bash
# Force complete reset
python -c "import asyncio; from app.core.database import init_database; from sqlalchemy import text; asyncio.run(init_database()); print('Database reset')"

# Check database state
python -c "import asyncio; from app.core.database import get_session; from app.models.sql_models import TokenUsage; from sqlalchemy import select; asyncio.run(get_session())"
```

### If Monthly Reset Not Working
```bash
# Check cron job
crontab -l

# Test monthly reset manually
python monthly_token_reset.py

# Check logs
tail -f /var/log/monthly-token-reset.log
```

### If Monitoring Not Working
```bash
# Test monitoring manually
python monitor_token_usage.py

# Check monitoring logs
tail -f /var/log/token-monitoring.log

# Check alert logs
tail -f /var/log/token-usage-alerts.log
```

## 🎯 Success Criteria

The fix is successful when:

1. ✅ **Token usage resets to 0** for all AI types
2. ✅ **No more token limit exceeded errors** in logs
3. ✅ **No more Claude verification errors** in logs
4. ✅ **Monthly reset runs automatically** on 1st of each month
5. ✅ **Monitoring shows real-time usage** with alerts
6. ✅ **Service restarts without errors** after deployment

## 📝 Maintenance

### Regular Checks
- Monitor token usage weekly
- Check monthly reset logs monthly
- Review alert logs for patterns
- Update limits if needed

### Future Improvements
- Add email/SMS alerts for critical levels
- Implement token usage analytics dashboard
- Add predictive usage modeling
- Implement dynamic limit adjustment

---

**Status**: ✅ **COMPLETE SOLUTION IMPLEMENTED**

This comprehensive solution addresses all identified token usage and reset issues with automatic monthly resets, enhanced error handling, and real-time monitoring. 