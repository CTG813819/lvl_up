#!/bin/bash

# Deploy Token Usage Limits to EC2 Instance
# Run this script on your EC2 instance

set -e

echo "🚀 Deploying Token Usage Limits to EC2 Instance"
echo "================================================"

# Configuration
BACKEND_DIR="/home/ubuntu/ai-backend-python"
BACKUP_DIR="/home/ubuntu/backups/token_limits_$(date +%Y%m%d_%H%M%S)"

# Step 1: Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
cp $BACKEND_DIR/app/services/token_usage_service.py $BACKUP_DIR/
cp $BACKEND_DIR/app/services/anthropic_service.py $BACKUP_DIR/
echo "✅ Backup created at $BACKUP_DIR"

# Step 2: Update token usage service with new limits
echo "🔧 Updating token usage service..."
cat > $BACKEND_DIR/app/services/token_usage_service.py << 'EOF'
"""
Token Usage Service - Monthly token monitoring for AI agents
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from ..core.database import get_session
from ..models.sql_models import TokenUsage, TokenUsageLog

logger = structlog.get_logger()

# Global Anthropic monthly limit (all AIs combined)
GLOBAL_MONTHLY_LIMIT = 200_000
ENFORCED_GLOBAL_LIMIT = int(GLOBAL_MONTHLY_LIMIT * 0.7)  # 70% of 200,000 = 140,000

# Warning thresholds (percentage of enforced global limit)
WARNING_THRESHOLD = 80.0  # 80% of enforced limit
CRITICAL_THRESHOLD = 95.0  # 95% of enforced limit

# Additional strict limits
DAILY_LIMIT = int(ENFORCED_GLOBAL_LIMIT / 30)  # Daily limit (monthly / 30 days)
HOURLY_LIMIT = int(DAILY_LIMIT / 24)  # Hourly limit
REQUEST_LIMIT = 1000  # Max tokens per request

# Emergency shutdown threshold
EMERGENCY_SHUTDOWN_THRESHOLD = 98.0  # 98% of enforced limit


class TokenUsageService:
    """Service to track and monitor monthly token usage for AI agents (global shared cap)"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenUsageService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the token usage service"""
        instance = cls()
        await instance._setup_monthly_tracking()
        logger.info("Token Usage Service initialized")
        return instance
    
    async def _setup_monthly_tracking(self):
        """Setup monthly tracking for all AI types"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            # Define AI types manually since we can't access enum values
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            async with get_session() as session:
                for ai_type in ai_types:
                    try:
                        # Check if tracking exists for current month
                        stmt = select(TokenUsage).where(
                            and_(
                                TokenUsage.ai_type == ai_type,
                                TokenUsage.month_year == current_month
                            )
                        )
                        result = await session.execute(stmt)
                        existing = result.scalar_one_or_none()
                        
                        if not existing:
                            # Create new monthly tracking
                            new_tracking = TokenUsage(
                                ai_type=ai_type,
                                month_year=current_month,
                                monthly_limit=ENFORCED_GLOBAL_LIMIT,
                                status="active"
                            )
                            session.add(new_tracking)
                            await session.commit()
                            logger.info(f"Created monthly tracking for {ai_type} - {current_month}")
                    except Exception as e:
                        logger.warning(f"Could not setup tracking for {ai_type}: {e}")
                        # Continue with other AI types even if one fails
                        continue
                        
        except Exception as e:
            logger.error("Error setting up monthly tracking", error=str(e))
            # Don't fail initialization if tables don't exist yet
    
    async def record_token_usage(
        self, 
        ai_type: str, 
        tokens_in: int, 
        tokens_out: int, 
        request_id: Optional[str] = None,
        model_used: Optional[str] = None,
        request_type: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """Record token usage for an AI agent (enforcing global cap)"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            total_tokens = tokens_in + tokens_out
            
            async with get_session() as session:
                # Get or create monthly tracking for this AI
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year == current_month
                    )
                )
                result = await session.execute(stmt)
                tracking = result.scalar_one_or_none()
                
                if not tracking:
                    tracking = TokenUsage(
                        ai_type=ai_type,
                        month_year=current_month,
                        monthly_limit=ENFORCED_GLOBAL_LIMIT,
                        status="active"
                    )
                    session.add(tracking)
                
                # Update tracking for this AI (handle None values)
                tracking.tokens_in = (tracking.tokens_in or 0) + tokens_in
                tracking.tokens_out = (tracking.tokens_out or 0) + tokens_out
                tracking.total_tokens = (tracking.total_tokens or 0) + total_tokens
                tracking.request_count = (tracking.request_count or 0) + 1
                tracking.last_request_at = datetime.utcnow()
                
                # Calculate global usage for all AIs
                stmt_all = select(func.sum(TokenUsage.total_tokens)).where(TokenUsage.month_year == current_month)
                result_all = await session.execute(stmt_all)
                global_total_tokens = result_all.scalar() or 0
                global_usage_percentage = (global_total_tokens / ENFORCED_GLOBAL_LIMIT) * 100
                
                # Update status for this AI based on global usage
                if global_usage_percentage >= 100:
                    tracking.status = "limit_reached"
                elif global_usage_percentage >= CRITICAL_THRESHOLD:
                    tracking.status = "critical"
                elif global_usage_percentage >= WARNING_THRESHOLD:
                    tracking.status = "warning"
                else:
                    tracking.status = "active"
                tracking.usage_percentage = global_usage_percentage
                
                # Create detailed log entry
                log_entry = TokenUsageLog(
                    ai_type=ai_type,
                    month_year=current_month,
                    request_id=request_id,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    total_tokens=total_tokens,
                    model_used=model_used,
                    request_type=request_type,
                    success=success,
                    error_message=error_message
                )
                session.add(log_entry)
                
                await session.commit()
                
                # Log warning if approaching limits
                if global_usage_percentage >= WARNING_THRESHOLD:
                    logger.warning(
                        f"Global token usage warning: {global_usage_percentage:.1f}% of shared monthly limit",
                        usage_percentage=global_usage_percentage,
                        total_tokens=global_total_tokens,
                        enforced_global_limit=ENFORCED_GLOBAL_LIMIT
                    )
                
                return True
                
        except Exception as e:
            logger.error("Error recording token usage", error=str(e), ai_type=ai_type)
            return False
    
    async def check_usage_limit(self, ai_type: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if any AI can make more requests based on the global monthly limit"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            current_day = datetime.utcnow().strftime("%Y-%m-%d")
            current_hour = datetime.utcnow().strftime("%Y-%m-%d-%H")
            
            async with get_session() as session:
                # Check monthly global usage
                stmt_all = select(func.sum(TokenUsage.total_tokens)).where(TokenUsage.month_year == current_month)
                result_all = await session.execute(stmt_all)
                global_total_tokens = result_all.scalar() or 0
                global_usage_percentage = (global_total_tokens / ENFORCED_GLOBAL_LIMIT) * 100
                
                # Check daily usage (approximate)
                daily_usage = global_total_tokens / 30  # Rough daily estimate
                daily_usage_percentage = (daily_usage / DAILY_LIMIT) * 100
                
                # Check hourly usage (approximate)
                hourly_usage = global_total_tokens / (30 * 24)  # Rough hourly estimate
                hourly_usage_percentage = (hourly_usage / HOURLY_LIMIT) * 100
                
                # Determine if request can be made
                can_make_request = (
                    global_usage_percentage < EMERGENCY_SHUTDOWN_THRESHOLD and
                    daily_usage_percentage < 100 and
                    hourly_usage_percentage < 100
                )
                
                # Determine status
                if global_usage_percentage >= EMERGENCY_SHUTDOWN_THRESHOLD:
                    status = "emergency_shutdown"
                elif global_usage_percentage >= CRITICAL_THRESHOLD:
                    status = "critical"
                elif global_usage_percentage >= WARNING_THRESHOLD:
                    status = "warning"
                else:
                    status = "active"
                
                return can_make_request, {
                    "ai_type": ai_type,
                    "global_total_tokens": global_total_tokens,
                    "enforced_global_limit": ENFORCED_GLOBAL_LIMIT,
                    "usage_percentage": global_usage_percentage,
                    "daily_usage_percentage": daily_usage_percentage,
                    "hourly_usage_percentage": hourly_usage_percentage,
                    "status": status,
                    "remaining_tokens": ENFORCED_GLOBAL_LIMIT - global_total_tokens,
                    "limits": {
                        "monthly_limit": ENFORCED_GLOBAL_LIMIT,
                        "daily_limit": DAILY_LIMIT,
                        "hourly_limit": HOURLY_LIMIT,
                        "request_limit": REQUEST_LIMIT
                    }
                }
        except Exception as e:
            logger.error("Error checking usage limit", error=str(e), ai_type=ai_type)
            # If tables don't exist, allow requests but log the issue
            if "relation \"token_usage\" does not exist" in str(e):
                logger.warning("Token usage tables not found - allowing requests", ai_type=ai_type)
                return True, {
                    "ai_type": ai_type,
                    "global_total_tokens": 0,
                    "enforced_global_limit": ENFORCED_GLOBAL_LIMIT,
                    "usage_percentage": 0.0,
                    "status": "active",
                    "remaining_tokens": ENFORCED_GLOBAL_LIMIT,
                    "warning": "Token usage tracking not available"
                }
            return False, {"error": str(e)}

    async def enforce_strict_limits(self, ai_type: str, estimated_tokens: int) -> Tuple[bool, Dict[str, Any]]:
        """Enforce strict limits before allowing any Anthropic request"""
        try:
            # Check if we can make the request
            can_make_request, usage_info = await self.check_usage_limit(ai_type)
            
            if not can_make_request:
                logger.warning(
                    f"Token limit reached - blocking request for {ai_type}",
                    usage_percentage=usage_info.get("usage_percentage", 0),
                    estimated_tokens=estimated_tokens
                )
                return False, usage_info
            
            # Check if this specific request would exceed limits
            if estimated_tokens > REQUEST_LIMIT:
                logger.warning(
                    f"Request token limit exceeded - blocking request for {ai_type}",
                    estimated_tokens=estimated_tokens,
                    request_limit=REQUEST_LIMIT
                )
                return False, {
                    **usage_info,
                    "error": f"Request exceeds token limit: {estimated_tokens} > {REQUEST_LIMIT}"
                }
            
            # Check if this request would push us over the limit
            current_tokens = usage_info.get("global_total_tokens", 0)
            if current_tokens + estimated_tokens > ENFORCED_GLOBAL_LIMIT:
                logger.warning(
                    f"Request would exceed monthly limit - blocking request for {ai_type}",
                    current_tokens=current_tokens,
                    estimated_tokens=estimated_tokens,
                    limit=ENFORCED_GLOBAL_LIMIT
                )
                return False, {
                    **usage_info,
                    "error": f"Request would exceed monthly limit: {current_tokens + estimated_tokens} > {ENFORCED_GLOBAL_LIMIT}"
                }
            
            return True, usage_info
            
        except Exception as e:
            logger.error("Error enforcing strict limits", error=str(e), ai_type=ai_type)
            return False, {"error": str(e)}

    async def get_emergency_status(self) -> Dict[str, Any]:
        """Get emergency status for token usage monitoring"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt_all = select(func.sum(TokenUsage.total_tokens)).where(TokenUsage.month_year == current_month)
                result_all = await session.execute(stmt_all)
                global_total_tokens = result_all.scalar() or 0
                global_usage_percentage = (global_total_tokens / ENFORCED_GLOBAL_LIMIT) * 100
                
                return {
                    "emergency_shutdown": global_usage_percentage >= EMERGENCY_SHUTDOWN_THRESHOLD,
                    "critical_level": global_usage_percentage >= CRITICAL_THRESHOLD,
                    "warning_level": global_usage_percentage >= WARNING_THRESHOLD,
                    "usage_percentage": global_usage_percentage,
                    "total_tokens": global_total_tokens,
                    "remaining_tokens": ENFORCED_GLOBAL_LIMIT - global_total_tokens,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error("Error getting emergency status", error=str(e))
            return {
                "emergency_shutdown": False,
                "critical_level": False,
                "warning_level": False,
                "usage_percentage": 0.0,
                "error": str(e)
            }

    async def get_monthly_usage(self, ai_type: str, month_year: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get monthly usage for an AI agent"""
        try:
            if not month_year:
                month_year = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year == month_year
                    )
                )
                result = await session.execute(stmt)
                tracking = result.scalar_one_or_none()
                
                if tracking:
                    return {
                        "ai_type": tracking.ai_type,
                        "month_year": tracking.month_year,
                        "tokens_in": tracking.tokens_in,
                        "tokens_out": tracking.tokens_out,
                        "total_tokens": tracking.total_tokens,
                        "request_count": tracking.request_count,
                        "monthly_limit": tracking.monthly_limit,
                        "usage_percentage": tracking.usage_percentage,
                        "status": tracking.status,
                        "last_request_at": tracking.last_request_at.isoformat() if tracking.last_request_at else None,
                        "created_at": tracking.created_at.isoformat(),
                        "updated_at": tracking.updated_at.isoformat()
                    }
                return None
                
        except Exception as e:
            logger.error("Error getting monthly usage", error=str(e), ai_type=ai_type)
            return None
    
    async def get_all_monthly_usage(self, month_year: Optional[str] = None) -> Dict[str, Any]:
        """Get monthly usage for all AI agents"""
        try:
            if not month_year:
                month_year = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt = select(TokenUsage).where(TokenUsage.month_year == month_year)
                result = await session.execute(stmt)
                trackings = result.scalars().all()
                
                usage_data = {}
                total_tokens = 0
                total_requests = 0
                
                for tracking in trackings:
                    usage_data[tracking.ai_type] = {
                        "tokens_in": tracking.tokens_in,
                        "tokens_out": tracking.tokens_out,
                        "total_tokens": tracking.total_tokens,
                        "request_count": tracking.request_count,
                        "monthly_limit": tracking.monthly_limit,
                        "usage_percentage": tracking.usage_percentage,
                        "status": tracking.status,
                        "last_request_at": tracking.last_request_at.isoformat() if tracking.last_request_at else None
                    }
                    total_tokens += tracking.total_tokens
                    total_requests += tracking.request_count
                
                return {
                    "month_year": month_year,
                    "ai_usage": usage_data,
                    "summary": {
                        "total_tokens": total_tokens,
                        "total_requests": total_requests,
                        "ai_count": len(usage_data)
                    }
                }
                
        except Exception as e:
            logger.error("Error getting all monthly usage", error=str(e))
            return {"month_year": month_year, "ai_usage": {}, "summary": {}}
    
    async def get_usage_alerts(self) -> List[Dict[str, Any]]:
        """Get alerts for AI agents approaching or exceeding limits"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.month_year == current_month,
                        TokenUsage.usage_percentage >= WARNING_THRESHOLD
                    )
                )
                result = await session.execute(stmt)
                warnings = result.scalars().all()
                
                alerts = []
                for warning in warnings:
                    alert_level = "critical" if warning.usage_percentage >= CRITICAL_THRESHOLD else "warning"
                    alerts.append({
                        "ai_type": warning.ai_type,
                        "usage_percentage": warning.usage_percentage,
                        "total_tokens": warning.total_tokens,
                        "monthly_limit": warning.monthly_limit,
                        "alert_level": alert_level,
                        "remaining_tokens": warning.monthly_limit - warning.total_tokens,
                        "last_request_at": warning.last_request_at.isoformat() if warning.last_request_at else None
                    })
                
                return alerts
                
        except Exception as e:
            logger.error("Error getting usage alerts", error=str(e))
            return []
    
    async def reset_monthly_usage(self, ai_type: str, month_year: Optional[str] = None) -> bool:
        """Reset monthly usage for an AI agent (for testing or limit reset)"""
        try:
            if not month_year:
                month_year = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year == month_year
                    )
                )
                result = await session.execute(stmt)
                tracking = result.scalar_one_or_none()
                
                if tracking:
                    tracking.tokens_in = 0
                    tracking.tokens_out = 0
                    tracking.total_tokens = 0
                    tracking.request_count = 0
                    tracking.usage_percentage = 0.0
                    tracking.status = "active"
                    tracking.last_request_at = None
                    
                    await session.commit()
                    logger.info(f"Reset monthly usage for {ai_type} - {month_year}")
                    return True
                else:
                    logger.warning(f"No tracking found for {ai_type} - {month_year}")
                    return False
                    
        except Exception as e:
            logger.error("Error resetting monthly usage", error=str(e), ai_type=ai_type)
            return False
    
    async def get_usage_history(self, ai_type: str, months: int = 6) -> List[Dict[str, Any]]:
        """Get usage history for an AI agent over multiple months"""
        try:
            async with get_session() as session:
                # Get current month and calculate start month
                current_month = datetime.utcnow()
                start_month = current_month - timedelta(days=30 * months)
                
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year >= start_month.strftime("%Y-%m")
                    )
                ).order_by(TokenUsage.month_year.desc())
                
                result = await session.execute(stmt)
                trackings = result.scalars().all()
                
                history = []
                for tracking in trackings:
                    history.append({
                        "month_year": tracking.month_year,
                        "tokens_in": tracking.tokens_in,
                        "tokens_out": tracking.tokens_out,
                        "total_tokens": tracking.total_tokens,
                        "request_count": tracking.request_count,
                        "usage_percentage": tracking.usage_percentage,
                        "status": tracking.status
                    })
                
                return history
                
        except Exception as e:
            logger.error("Error getting usage history", error=str(e), ai_type=ai_type)
            return []


# Global instance
token_usage_service = TokenUsageService()
EOF

# Step 3: Update anthropic service with strict enforcement
echo "🔧 Updating anthropic service..."
cat > $BACKEND_DIR/app/services/anthropic_service.py << 'EOF'
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import asyncio
import time
import json
from collections import defaultdict
from typing import Optional, Dict, Any

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# Import token usage service
from .token_usage_service import token_usage_service


def call_claude(prompt, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

# Anthropic Opus 4 limits (with 15% buffer)
MAX_REQUESTS_PER_MIN = 42  # 50 * 0.85
MAX_TOKENS_PER_REQUEST = 17000  # 20,000 * 0.85
MAX_REQUESTS_PER_DAY = 3400  # 4,000 * 0.85
AI_NAMES = ["imperium", "guardian", "sandbox", "conquest"]

# Track requests per AI
_request_counts_minute = defaultdict(list)  # {ai_name: [timestamps]}
_request_counts_day = defaultdict(list)     # {ai_name: [timestamps]}
_rate_limiter_lock = asyncio.Lock()

async def anthropic_rate_limited_call(prompt, ai_name, model="claude-3-5-sonnet-20241022", max_tokens=1024):
    """Async wrapper for call_claude with per-AI and global rate limiting."""
    if ai_name not in AI_NAMES:
        ai_name = "imperium"  # fallback
    
    # Estimate tokens for this request
    estimated_input_tokens = len(prompt.split()) * 1.3  # Rough estimate with 30% buffer
    estimated_total_tokens = estimated_input_tokens + max_tokens
    
    # Check monthly usage limits first with strict enforcement
    can_make_request, usage_info = await token_usage_service.enforce_strict_limits(ai_name, int(estimated_total_tokens))
    if not can_make_request:
        error_msg = f"Token limit reached for {ai_name}. Usage: {usage_info.get('usage_percentage', 0):.1f}%"
        if 'error' in usage_info:
            error_msg += f" - {usage_info['error']}"
        raise Exception(error_msg)
    
    now = time.time()
    async with _rate_limiter_lock:
        # Clean up old timestamps
        _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
        _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
        # Enforce per-minute and per-day limits
        while (len(_request_counts_minute[ai_name]) >= MAX_REQUESTS_PER_MIN or
               len(_request_counts_day[ai_name]) >= MAX_REQUESTS_PER_DAY):
            await asyncio.sleep(1)
            now = time.time()
            _request_counts_minute[ai_name] = [t for t in _request_counts_minute[ai_name] if now - t < 60]
            _request_counts_day[ai_name] = [t for t in _request_counts_day[ai_name] if now - t < 86400]
        # Register this request
        _request_counts_minute[ai_name].append(now)
        _request_counts_day[ai_name].append(now)
    
    # Enforce token limit
    if max_tokens > MAX_TOKENS_PER_REQUEST:
        max_tokens = MAX_TOKENS_PER_REQUEST
    
    try:
        # Call Claude and capture response
        response = await _call_claude_with_tracking(prompt, model, max_tokens, ai_name)
        return response
    except Exception as e:
        # Record failed request
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=int(estimated_input_tokens),
            tokens_out=0,
            model_used=model,
            request_type="HTTP",
            success=False,
            error_message=str(e)
        )
        raise e

async def _call_claude_with_tracking(prompt, model, max_tokens, ai_name):
    """Call Claude with token usage tracking"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        response_data = response.json()
        response_text = response_data["content"][0]["text"]
        
        # Extract token usage from response headers or estimate
        tokens_in = 0
        tokens_out = 0
        request_id = None
        
        # Try to get token usage from response headers
        if "x-request-id" in response.headers:
            request_id = response.headers["x-request-id"]
        
        # Try to get usage from response body if available
        if "usage" in response_data:
            usage = response_data["usage"]
            tokens_in = usage.get("input_tokens", 0)
            tokens_out = usage.get("output_tokens", 0)
        else:
            # Estimate token usage if not provided
            tokens_in = len(prompt.split())  # Rough estimate
            tokens_out = len(response_text.split())  # Rough estimate
        
        # Record token usage
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            request_id=request_id,
            model_used=model,
            request_type="HTTP",
            success=True
        )
        
        return response_text
        
    except requests.exceptions.RequestException as e:
        # Record failed request
        await token_usage_service.record_token_usage(
            ai_type=ai_name,
            tokens_in=len(prompt.split()),  # Approximate input tokens
            tokens_out=0,
            model_used=model,
            request_type="HTTP",
            success=False,
            error_message=str(e)
        )
        raise e
EOF

# Step 4: Create monitoring script
echo "📤 Creating monitoring script..."
cat > $BACKEND_DIR/monitor_token_usage.py << 'EOF'
#!/usr/bin/env python3
"""
Token Usage Monitor
Real-time monitoring of Anthropic token usage with alerts
"""

import asyncio
import time
import json
from datetime import datetime
from app.services.token_usage_service import token_usage_service
from app.core.database import init_database

class TokenUsageMonitor:
    def __init__(self):
        self.check_interval = 60  # Check every 60 seconds
        self.alert_sent = False
        self.critical_alert_sent = False
        self.emergency_alert_sent = False
    
    async def initialize(self):
        """Initialize the monitor"""
        await init_database()
        await token_usage_service._setup_monthly_tracking()
        print("✅ Token usage monitor initialized")
    
    async def check_usage(self):
        """Check current token usage"""
        try:
            # Get emergency status
            emergency_status = await token_usage_service.get_emergency_status()
            
            # Get all monthly usage
            all_usage = await token_usage_service.get_all_monthly_usage()
            
            # Get alerts
            alerts = await token_usage_service.get_usage_alerts()
            
            return {
                "emergency_status": emergency_status,
                "all_usage": all_usage,
                "alerts": alerts,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error checking usage: {e}")
            return None
    
    async def send_alert(self, level: str, message: str, data: dict):
        """Send an alert (placeholder for actual alert system)"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        alert = {
            "level": level,
            "message": message,
            "data": data,
            "timestamp": timestamp
        }
        
        print(f"\n🚨 {level.upper()} ALERT: {message}")
        print(f"📊 Usage: {data.get('usage_percentage', 0):.1f}%")
        print(f"🔢 Total Tokens: {data.get('total_tokens', 0):,}")
        print(f"⏰ Time: {timestamp}")
        print("-" * 50)
        
        # Save alert to file
        with open("token_usage_alerts.json", "a") as f:
            f.write(json.dumps(alert) + "\n")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("🔍 Starting token usage monitor...")
        print(f"📊 Monitoring interval: {self.check_interval} seconds")
        print(f"⚠️  Warning threshold: {token_usage_service.WARNING_THRESHOLD}%")
        print(f"🚨 Critical threshold: {token_usage_service.CRITICAL_THRESHOLD}%")
        print(f"🛑 Emergency threshold: {token_usage_service.EMERGENCY_SHUTDOWN_THRESHOLD}%")
        print("=" * 60)
        
        while True:
            try:
                usage_data = await self.check_usage()
                
                if usage_data:
                    emergency_status = usage_data["emergency_status"]
                    usage_percentage = emergency_status.get("usage_percentage", 0)
                    
                    # Emergency shutdown alert
                    if emergency_status.get("emergency_shutdown") and not self.emergency_alert_sent:
                        await self.send_alert(
                            "EMERGENCY",
                            "EMERGENCY SHUTDOWN: Token usage has reached emergency threshold!",
                            emergency_status
                        )
                        self.emergency_alert_sent = True
                    
                    # Critical alert
                    elif emergency_status.get("critical_level") and not self.critical_alert_sent:
                        await self.send_alert(
                            "CRITICAL",
                            "CRITICAL: Token usage has reached critical threshold!",
                            emergency_status
                        )
                        self.critical_alert_sent = True
                    
                    # Warning alert
                    elif emergency_status.get("warning_level") and not self.alert_sent:
                        await self.send_alert(
                            "WARNING",
                            "WARNING: Token usage is approaching critical levels!",
                            emergency_status
                        )
                        self.alert_sent = True
                    
                    # Reset alerts if usage drops
                    if usage_percentage < token_usage_service.WARNING_THRESHOLD:
                        self.alert_sent = False
                        self.critical_alert_sent = False
                        self.emergency_alert_sent = False
                    
                    # Print status every 10 minutes
                    if int(time.time()) % 600 == 0:
                        print(f"📊 Status: {usage_percentage:.1f}% used ({emergency_status.get('total_tokens', 0):,} tokens)")
                
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitor stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                await asyncio.sleep(self.check_interval)

async def main():
    """Main function"""
    monitor = TokenUsageMonitor()
    await monitor.initialize()
    await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Step 5: Create reset script
echo "📤 Creating reset script..."
cat > $BACKEND_DIR/reset_token_usage.py << 'EOF'
#!/usr/bin/env python3
"""
Reset Token Usage
Reset token usage for testing and development
"""

import asyncio
from app.services.token_usage_service import token_usage_service
from app.core.database import init_database

async def reset_all_token_usage():
    """Reset token usage for all AI types"""
    try:
        await init_database()
        await token_usage_service._setup_monthly_tracking()
        
        # Reset for all AI types
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        for ai_type in ai_types:
            success = await token_usage_service.reset_monthly_usage(ai_type)
            if success:
                print(f"✅ Reset token usage for {ai_type}")
            else:
                print(f"❌ Failed to reset token usage for {ai_type}")
        
        print("\n🎉 Token usage reset completed!")
        
        # Show current status
        all_usage = await token_usage_service.get_all_monthly_usage()
        print(f"\n📊 Current usage summary:")
        print(f"Total tokens: {all_usage.get('summary', {}).get('total_tokens', 0)}")
        print(f"Total requests: {all_usage.get('summary', {}).get('total_requests', 0)}")
        
    except Exception as e:
        print(f"❌ Error resetting token usage: {e}")

async def show_current_usage():
    """Show current token usage"""
    try:
        await init_database()
        
        all_usage = await token_usage_service.get_all_monthly_usage()
        emergency_status = await token_usage_service.get_emergency_status()
        
        print("📊 Current Token Usage:")
        print("=" * 40)
        
        for ai_type, usage in all_usage.get("ai_usage", {}).items():
            print(f"{ai_type.upper()}:")
            print(f"  Tokens: {usage.get('total_tokens', 0):,}")
            print(f"  Requests: {usage.get('request_count', 0)}")
            print(f"  Usage: {usage.get('usage_percentage', 0):.1f}%")
            print(f"  Status: {usage.get('status', 'unknown')}")
            print()
        
        print("🚨 Emergency Status:")
        print(f"  Emergency Shutdown: {emergency_status.get('emergency_shutdown', False)}")
        print(f"  Critical Level: {emergency_status.get('critical_level', False)}")
        print(f"  Warning Level: {emergency_status.get('warning_level', False)}")
        print(f"  Usage Percentage: {emergency_status.get('usage_percentage', 0):.1f}%")
        print(f"  Total Tokens: {emergency_status.get('total_tokens', 0):,}")
        print(f"  Remaining Tokens: {emergency_status.get('remaining_tokens', 0):,}")
        
    except Exception as e:
        print(f"❌ Error showing usage: {e}")

async def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        await reset_all_token_usage()
    else:
        await show_current_usage()

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Step 6: Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x $BACKEND_DIR/monitor_token_usage.py
chmod +x $BACKEND_DIR/reset_token_usage.py
echo "✅ Scripts made executable"

# Step 7: Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ai-backend-python
echo "✅ Backend service restarted"

# Step 8: Initialize token usage tracking
echo "🔧 Initializing token usage tracking..."
cd $BACKEND_DIR
python -c "import asyncio; from app.services.token_usage_service import token_usage_service; from app.core.database import init_database; asyncio.run(init_database()); asyncio.run(token_usage_service._setup_monthly_tracking()); print('Token tracking initialized')"
echo "✅ Token usage tracking initialized"

# Step 9: Show current status
echo "📊 Current token usage status..."
python reset_token_usage.py

echo ""
echo "🎯 Token Usage Limits Deployed Successfully!"
echo "============================================="
echo ""
echo "📊 To monitor usage in real-time:"
echo "   cd $BACKEND_DIR"
echo "   python monitor_token_usage.py"
echo ""
echo "📋 To check current usage:"
echo "   cd $BACKEND_DIR"
echo "   python reset_token_usage.py"
echo ""
echo "🔄 To reset usage (for testing):"
echo "   cd $BACKEND_DIR"
echo "   python reset_token_usage.py reset"
echo ""
echo "🚨 The system will now enforce strict token limits:"
echo "   - Monthly limit: 140,000 tokens (70% of 200,000)"
echo "   - Warning at 80% (112,000 tokens)"
echo "   - Critical at 95% (133,000 tokens)"
echo "   - Emergency shutdown at 98% (137,200 tokens)"
echo ""
echo "✅ Deployment complete!" 