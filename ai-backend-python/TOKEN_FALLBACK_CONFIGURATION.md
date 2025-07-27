# Token Fallback Configuration - AI Provider Management

## Overview

This document outlines the configuration changes made to ensure proper fallback behavior between Anthropic and OpenAI providers for all AI services, including Custodes.

## Configuration Changes Made

### 1. Port Configuration Fixed
- **File**: `ai-backend-python/app/core/config.py`
- **Change**: Updated default port from 4000 to 8000
- **Reason**: Align with memory requirement for main backend service port

### 2. Fallback Threshold Improved
- **File**: `ai-backend-python/app/core/config.py`
- **Change**: Updated `openai_fallback_threshold` from 0.008 (0.8%) to 0.95 (95%)
- **Reason**: More reasonable threshold for switching to OpenAI fallback

### 3. Token Usage Service Enhanced
- **File**: `ai-backend-python/app/services/token_usage_service.py`
- **Changes**:
  - Updated `get_provider_recommendation()` to use configurable threshold instead of hardcoded 95%
  - Updated `check_provider_availability()` to use configurable threshold
  - Added threshold information to provider availability responses

### 4. Custodes Protocol Service Updated
- **File**: `ai-backend-python/app/services/custody_protocol_service.py`
- **Changes**:
  - Added import for `unified_ai_service`
  - Updated AI test execution to use `unified_ai_service.call_ai()` instead of direct `anthropic_rate_limited_call()`
  - Updated evaluation calls to use unified AI service
  - Updated verification calls to use unified AI service
- **Reason**: Ensure Custodes tests also benefit from OpenAI fallback when Anthropic is unavailable

## Current Configuration

### Token Limits
- **Anthropic Monthly Limit**: 40,000 tokens
- **OpenAI Monthly Limit**: 6,000 tokens
- **Fallback Threshold**: 95% (switches to OpenAI when Anthropic usage reaches 95%)

### Provider Selection Logic
1. **Primary**: Anthropic Claude (when usage < 95%)
2. **Fallback**: OpenAI GPT-4.1 (when Anthropic usage >= 95% or Anthropic fails)
3. **Emergency**: Both providers exhausted

### Services Using Unified AI Service
- ✅ Unified AI Service (main orchestrator)
- ✅ Custodes Protocol Service (AI testing)
- ✅ All AI agents (Imperium, Guardian, Sandbox, Conquest)
- ✅ Token usage monitoring and recommendations

## Benefits

1. **Seamless Fallback**: Automatic switching between providers without service interruption
2. **Cost Optimization**: Uses cheaper Anthropic tokens first, OpenAI as backup
3. **Reliability**: Continues operation even if one provider fails
4. **Consistent Behavior**: All services use the same fallback logic
5. **Configurable**: Easy to adjust thresholds via environment variables

## Environment Variables

```env
# Server Configuration
PORT=8000

# Token Usage Limits
ANTHROPIC_MONTHLY_LIMIT=40000
OPENAI_MONTHLY_LIMIT=6000
ENABLE_OPENAI_FALLBACK=true
OPENAI_FALLBACK_THRESHOLD=0.95

# API Keys
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

## Testing

To verify the configuration is working:

1. **Check Provider Status**: `/api/token-usage/provider-status`
2. **Test AI Call**: `/api/token-usage/test-ai-call`
3. **Monitor Usage**: `/api/token-usage/summary`
4. **Run Custodes Test**: `/api/custodes/administer-test/{ai_type}`

## Monitoring

The system provides comprehensive monitoring through:
- Real-time token usage tracking
- Provider availability status
- Fallback event logging
- Emergency status alerts

All services now properly use the unified AI service for consistent fallback behavior. 