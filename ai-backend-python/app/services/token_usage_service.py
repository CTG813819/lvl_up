"""
Token Usage Service - Monthly token monitoring for AI agents with rate limiting
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from ..core.database import get_session
from ..core.config import settings
from ..models.sql_models import TokenUsage, TokenUsageLog

logger = structlog.get_logger()

# Global Anthropic monthly limit (all AIs combined) - use config values
GLOBAL_MONTHLY_LIMIT = settings.anthropic_monthly_limit
ENFORCED_GLOBAL_LIMIT = int(GLOBAL_MONTHLY_LIMIT * 0.7)  # 70% of monthly limit

# OpenAI monthly limit - use config values
OPENAI_MONTHLY_LIMIT = settings.openai_monthly_limit

# Warning thresholds (percentage of enforced global limit)
WARNING_THRESHOLD = 80.0  # 80% of enforced limit
CRITICAL_THRESHOLD = 95.0  # 95% of enforced limit

# Enhanced rate limiting with daily and hourly distribution
DAILY_LIMIT = int(ENFORCED_GLOBAL_LIMIT / 30)  # Daily limit (monthly / 30 days)
HOURLY_LIMIT = int(DAILY_LIMIT / 24)  # Hourly limit
REQUEST_LIMIT = 1000  # Max tokens per request

# Rate limiting intervals
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
DAILY_WINDOW = 86400  # 24 hours in seconds

# Emergency shutdown threshold
EMERGENCY_SHUTDOWN_THRESHOLD = 98.0  # 98% of enforced limit

# Usage distribution settings - Different limits for Anthropic and OpenAI
ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE = 15.0  # Max 15% of monthly limit per day (increased from 8%)
ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE = 2.0  # Max 2% of monthly limit per hour (increased from 0.5%)
OPENAI_MAX_DAILY_USAGE_PERCENTAGE = 12.0  # Max 12% of monthly limit per day (more generous)
OPENAI_MAX_HOURLY_USAGE_PERCENTAGE = 1.0  # Max 1% of monthly limit per hour (more generous)
MIN_DAILY_USAGE_PERCENTAGE = 2.0  # Min 2% of monthly limit per day (to ensure usage)

# AI coordination settings
AI_COOLDOWN_PERIOD = 60  # 1 minute between AI requests (reduced from 5 minutes)
MAX_CONCURRENT_AI_REQUESTS = 5  # Max 5 AIs can make requests simultaneously (increased from 2)


class TokenUsageService:
    """Service to track and monitor monthly token usage for AI agents with rate limiting"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenUsageService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._last_ai_request = {}  # Track last request time per AI
            self._active_requests = 0  # Track concurrent requests
            self._daily_usage_cache = {}  # Cache daily usage
            self._hourly_usage_cache = {}  # Cache hourly usage
    
    @classmethod
    async def initialize(cls):
        """Initialize the token usage service"""
        instance = cls()
        await instance._setup_monthly_tracking()
        logger.info("Token Usage Service initialized with rate limiting")
        return instance
    
    async def _setup_monthly_tracking(self):
        """Setup monthly tracking for all AI types"""
        try:
            # Initialize database if not already initialized
            try:
                from ..core.database import init_database
                await init_database()
            except Exception as e:
                logger.error(f"Error setting up monthly tracking: {str(e)}")
                return
            
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
            logger.error(f"Error setting up monthly tracking: {str(e)}")
            # Don't fail initialization if tables don't exist yet
    
    async def _get_daily_usage(self, current_date: str) -> int:
        """Get actual daily usage for a specific date"""
        try:
            async with get_session() as session:
                # Compare string date to string date using to_char
                stmt = select(func.sum(TokenUsageLog.total_tokens)).where(
                    and_(
                        TokenUsageLog.month_year == current_date[:7],  # YYYY-MM
                        func.to_char(TokenUsageLog.created_at, 'YYYY-MM-DD') == current_date
                    )
                )
                result = await session.execute(stmt)
                daily_usage = result.scalar() or 0
                return daily_usage
        except Exception as e:
            logger.error(f"Error getting daily usage: {str(e)}")
            return 0
    
    async def _get_hourly_usage(self, current_hour: str) -> int:
        """Get actual hourly usage for a specific hour"""
        try:
            async with get_session() as session:
                # Compare string hour to string hour using to_char
                stmt = select(func.sum(TokenUsageLog.total_tokens)).where(
                    and_(
                        TokenUsageLog.month_year == current_hour[:7],  # YYYY-MM
                        func.to_char(TokenUsageLog.created_at, 'YYYY-MM-DD-HH24') == current_hour
                    )
                )
                result = await session.execute(stmt)
                hourly_usage = result.scalar() or 0
                return hourly_usage
        except Exception as e:
            logger.error(f"Error getting hourly usage: {str(e)}")
            return 0
    
    async def _check_rate_limits(self, ai_type: str, estimated_tokens: int, provider: str = "anthropic") -> Tuple[bool, Dict[str, Any]]:
        """Check rate limits before allowing request with different limits for different providers"""
        try:
            now = datetime.utcnow()
            current_date = now.strftime("%Y-%m-%d")
            current_hour = now.strftime("%Y-%m-%d-%H")
            
            # Check AI cooldown period
            last_request = self._last_ai_request.get(ai_type)
            if last_request and (now - last_request).total_seconds() < AI_COOLDOWN_PERIOD:
                return False, {
                    "error": "AI cooldown period not met",
                    "ai_type": ai_type,
                    "cooldown_remaining": AI_COOLDOWN_PERIOD - (now - last_request).total_seconds()
                }
            
            # Check concurrent requests limit
            if self._active_requests >= MAX_CONCURRENT_AI_REQUESTS:
                return False, {
                    "error": "Too many concurrent AI requests",
                    "active_requests": self._active_requests,
                    "max_concurrent": MAX_CONCURRENT_AI_REQUESTS
                }
            
            # Get actual daily and hourly usage
            daily_usage = await self._get_daily_usage(current_date)
            hourly_usage = await self._get_hourly_usage(current_hour)
            
            # Calculate limits based on provider
            if provider.lower() == "openai":
                daily_limit = int(OPENAI_MONTHLY_LIMIT * (OPENAI_MAX_DAILY_USAGE_PERCENTAGE / 100))
                hourly_limit = int(OPENAI_MONTHLY_LIMIT * (OPENAI_MAX_HOURLY_USAGE_PERCENTAGE / 100))
            else:  # anthropic
                daily_limit = int(ENFORCED_GLOBAL_LIMIT * (ANTHROPIC_MAX_DAILY_USAGE_PERCENTAGE / 100))
                hourly_limit = int(ENFORCED_GLOBAL_LIMIT * (ANTHROPIC_MAX_HOURLY_USAGE_PERCENTAGE / 100))
            
            # Check daily limit
            if daily_usage + estimated_tokens > daily_limit:
                return False, {
                    "error": "Daily usage limit exceeded",
                    "daily_usage": daily_usage,
                    "daily_limit": daily_limit,
                    "estimated_tokens": estimated_tokens,
                    "provider": provider
                }
            
            # Check hourly limit
            if hourly_usage + estimated_tokens > hourly_limit:
                return False, {
                    "error": "Hourly usage limit exceeded",
                    "hourly_usage": hourly_usage,
                    "hourly_limit": hourly_limit,
                    "estimated_tokens": estimated_tokens
                }
            
            # Check minimum daily usage (ensure some usage each day)
            days_in_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - now.replace(day=1)
            min_daily_usage = int(ENFORCED_GLOBAL_LIMIT * (MIN_DAILY_USAGE_PERCENTAGE / 100))
            
            # If we're in the last week of the month and haven't used enough, allow more usage
            if now.day > 23 and daily_usage < min_daily_usage:
                logger.info(f"Allowing increased usage for {ai_type} - catching up on daily minimum")
            
            return True, {
                "daily_usage": daily_usage,
                "hourly_usage": hourly_usage,
                "daily_limit": daily_limit,
                "hourly_limit": hourly_limit,
                "estimated_tokens": estimated_tokens
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limits: {str(e)}")
            return False, {"error": str(e)}
    
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
        """Record token usage for an AI agent (enforcing global cap with rate limiting)"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            total_tokens = tokens_in + tokens_out
            
            # Update request tracking
            self._last_ai_request[ai_type] = datetime.utcnow()
            self._active_requests = max(0, self._active_requests - 1)
            
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
            logger.error(f"Error recording token usage: {str(e)} ai_type={ai_type}")
            return False
    
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
            logger.error(f"Error getting monthly usage: {str(e)} ai_type={ai_type}")
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
            logger.error(f"Error getting all monthly usage: {str(e)}")
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
            logger.error(f"Error getting usage alerts: {str(e)}")
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
            logger.error(f"Error resetting monthly usage: {str(e)} ai_type={ai_type}")
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
            logger.error(f"Error getting usage history: {str(e)} ai_type={ai_type}")
            return []
    
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
            logger.error(f"Error checking usage limit: {str(e)} ai_type={ai_type}")
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

    async def enforce_strict_limits(self, ai_type: str, estimated_tokens: int, provider: str = "anthropic") -> Tuple[bool, Dict[str, Any]]:
        """Enforce strict limits before allowing any AI request with rate limiting"""
        try:
            # Check rate limits first (daily/hourly/cooldown)
            rate_limit_ok, rate_limit_info = await self._check_rate_limits(ai_type, estimated_tokens, provider)
            
            if not rate_limit_ok:
                logger.warning(
                    f"Rate limit exceeded - blocking request for {ai_type} - {rate_limit_info.get('error')} - estimated_tokens={estimated_tokens}"
                )
                return False, rate_limit_info
            
            # Check if we can make the request (monthly limits)
            can_make_request, usage_info = await self.check_usage_limit(ai_type)
            
            if not can_make_request:
                logger.warning(
                    f"Token limit reached - blocking request for {ai_type} - usage_percentage={usage_info.get('usage_percentage', 0)} - estimated_tokens={estimated_tokens}"
                )
                return False, usage_info
            
            # Check if this specific request would exceed limits
            if estimated_tokens > REQUEST_LIMIT:
                logger.warning(
                    f"Request too large - blocking request for {ai_type} - estimated_tokens={estimated_tokens} - limit={REQUEST_LIMIT}"
                )
                return False, {
                    "error": f"Request too large ({estimated_tokens} tokens > {REQUEST_LIMIT} limit)",
                    "estimated_tokens": estimated_tokens,
                    "request_limit": REQUEST_LIMIT
                }
            
            # Check if this request would push us over the limit
            current_tokens = usage_info.get("global_total_tokens", 0)
            if current_tokens + estimated_tokens > ENFORCED_GLOBAL_LIMIT:
                logger.warning(
                    f"Request would exceed monthly limit - blocking request for {ai_type} current_tokens={current_tokens} estimated_tokens={estimated_tokens} limit={ENFORCED_GLOBAL_LIMIT}"
                )
                return False, {
                    **usage_info,
                    "error": f"Request would exceed monthly limit: {current_tokens + estimated_tokens} > {ENFORCED_GLOBAL_LIMIT}"
                }
            
            # Increment active requests counter
            self._active_requests += 1
            
            # Combine rate limit info with usage info
            combined_info = {**usage_info, **rate_limit_info}
            
            return True, combined_info
            
        except Exception as e:
            logger.error(f"Error enforcing strict limits: {str(e)} ai_type={ai_type}")
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
                
                # Calculate daily and hourly estimates
                daily_usage = global_total_tokens / 30  # Rough daily estimate
                hourly_usage = global_total_tokens / (30 * 24)  # Rough hourly estimate
                
                return {
                    "global_total_tokens": global_total_tokens,
                    "global_usage_percentage": global_usage_percentage,
                    "enforced_global_limit": ENFORCED_GLOBAL_LIMIT,
                    "daily_usage_estimate": daily_usage,
                    "hourly_usage_estimate": hourly_usage,
                    "emergency_shutdown": global_usage_percentage >= EMERGENCY_SHUTDOWN_THRESHOLD,
                    "status": "critical" if global_usage_percentage >= CRITICAL_THRESHOLD else "warning" if global_usage_percentage >= WARNING_THRESHOLD else "normal"
                }
                
        except Exception as e:
            logger.error(f"Error getting emergency status: {str(e)}")
            return {
                "error": str(e),
                "status": "unknown"
            }
    
    async def get_provider_recommendation(self, ai_name: str) -> Dict[str, Any]:
        """Get recommendation for which AI provider to use (Anthropic vs OpenAI)"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            # Get Anthropic usage for this AI
            anthropic_usage = await self.get_monthly_usage(ai_name, current_month)
            anthropic_percentage = anthropic_usage.get("usage_percentage", 0) if anthropic_usage else 0
            
            # Get OpenAI usage for this AI
            openai_ai_name = f"{ai_name}_openai"
            openai_usage = await self.get_monthly_usage(openai_ai_name, current_month)
            openai_percentage = openai_usage.get("usage_percentage", 0) if openai_usage else 0
            
            # Calculate OpenAI percentage against OpenAI limit
            openai_total_tokens = openai_usage.get("total_tokens", 0) if openai_usage else 0
            openai_usage_percentage = (openai_total_tokens / OPENAI_MONTHLY_LIMIT) * 100
            
            # Check if Anthropic is rate limited (cooldown period)
            estimated_tokens = 1000  # Default estimate for checking rate limits
            rate_limit_ok, rate_limit_info = await self._check_rate_limits(ai_name, estimated_tokens)
            
            # Check if Anthropic is actually reachable (quick connectivity test)
            anthropic_reachable = await self._check_anthropic_connectivity()
            
            # Determine recommendation using configurable threshold
            anthropic_threshold = settings.openai_fallback_threshold * 100  # Convert to percentage
            
            # Log the current state for debugging
            logger.info(f"Provider recommendation for {ai_name}:", 
                       anthropic_percentage=anthropic_percentage,
                       openai_usage_percentage=openai_usage_percentage,
                       anthropic_threshold=anthropic_threshold,
                       rate_limit_ok=rate_limit_ok,
                       anthropic_reachable=anthropic_reachable)
            
            # If Anthropic is not reachable or rate limited, try OpenAI
            if not anthropic_reachable:
                if openai_usage_percentage < 100:  # OpenAI available as fallback
                    recommendation = "openai"
                    reason = "anthropic_unreachable_openai_available"
                else:  # Both unreachable and exhausted
                    recommendation = "none"
                    reason = "anthropic_unreachable_openai_exhausted"
            elif not rate_limit_ok:
                if openai_usage_percentage < 100:  # OpenAI available as fallback
                    recommendation = "openai"
                    reason = "anthropic_rate_limited_openai_available"
                else:  # Both rate limited and exhausted
                    recommendation = "none"
                    reason = "anthropic_rate_limited_openai_exhausted"
            elif anthropic_percentage < anthropic_threshold:  # Anthropic available
                recommendation = "anthropic"
                reason = "anthropic_available"
            elif openai_usage_percentage < 100:  # OpenAI available as fallback
                recommendation = "openai"
                reason = "anthropic_exhausted_openai_available"
            else:  # Both exhausted
                recommendation = "none"
                reason = "both_exhausted"
            
            return {
                "recommendation": recommendation,
                "reason": reason,
                "anthropic": {
                    "usage_percentage": anthropic_percentage,
                    "total_tokens": anthropic_usage.get("total_tokens", 0) if anthropic_usage else 0,
                    "available": anthropic_percentage < 95 and rate_limit_ok and anthropic_reachable
                },
                "openai": {
                    "usage_percentage": openai_usage_percentage,
                    "total_tokens": openai_total_tokens,
                    "available": openai_usage_percentage < 100
                },
                "rate_limit_info": rate_limit_info if not rate_limit_ok else None,
                "anthropic_reachable": anthropic_reachable
            }
            
        except Exception as e:
            logger.error(f"Error getting provider recommendation: {str(e)} ai_name={ai_name}")
            return {
                "recommendation": "anthropic",  # Default to Anthropic on error
                "reason": "error_fallback",
                "error": str(e)
            }
    
    async def check_provider_availability(self, ai_name: str, provider: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if a specific provider is available for an AI"""
        try:
            if provider == "anthropic":
                usage = await self.get_monthly_usage(ai_name)
                if not usage:
                    return True, {"reason": "no_usage_data"}
                
                usage_percentage = usage.get("usage_percentage", 0)
                anthropic_threshold = settings.openai_fallback_threshold * 100  # Convert to percentage
                return usage_percentage < anthropic_threshold, {
                    "usage_percentage": usage_percentage,
                    "total_tokens": usage.get("total_tokens", 0),
                    "threshold": anthropic_threshold
                }
            
            elif provider == "openai":
                openai_ai_name = f"{ai_name}_openai"
                usage = await self.get_monthly_usage(openai_ai_name)
                if not usage:
                    return True, {"reason": "no_usage_data"}
                
                total_tokens = usage.get("total_tokens", 0)
                usage_percentage = (total_tokens / OPENAI_MONTHLY_LIMIT) * 100
                return usage_percentage < 100, {
                    "usage_percentage": usage_percentage,
                    "total_tokens": total_tokens
                }
            
            else:
                return False, {"error": f"Unknown provider: {provider}"}
                
        except Exception as e:
            logger.error(f"Error checking provider availability: {str(e)} ai_name={ai_name} provider={provider}")
            return False, {"error": str(e)}
    
    async def get_usage_distribution_stats(self) -> Dict[str, Any]:
        """Get detailed usage distribution statistics"""
        try:
            now = datetime.utcnow()
            current_month = now.strftime("%Y-%m")
            current_date = now.strftime("%Y-%m-%d")
            
            async with get_session() as session:
                # Get all usage for the current month
                stmt_all = select(TokenUsageLog).where(
                    TokenUsageLog.month_year == current_month
                )
                
                result_all = await session.execute(stmt_all)
                all_logs = result_all.scalars().all()
                
                # Process daily usage manually
                daily_usage = {}
                hourly_usage = {}
                
                for log in all_logs:
                    if log.created_at:
                        # Daily usage
                        day_key = log.created_at.strftime("%Y-%m-%d")
                        daily_usage[day_key] = daily_usage.get(day_key, 0) + (log.total_tokens or 0)
                        
                        # Hourly usage for today
                        if day_key == current_date:
                            hour_key = log.created_at.strftime("%Y-%m-%d %H:00")
                            hourly_usage[hour_key] = hourly_usage.get(hour_key, 0) + (log.total_tokens or 0)
                
                daily_usage_data = [
                    {"date": day, "tokens": tokens} 
                    for day, tokens in daily_usage.items()
                ]
                
                hourly_usage_data = [
                    {"hour": hour, "tokens": tokens} 
                    for hour, tokens in hourly_usage.items()
                ]
                
                # Calculate distribution statistics
                total_monthly_tokens = sum(item["tokens"] for item in daily_usage_data)
                days_with_usage = len(daily_usage_data)
                avg_daily_usage = total_monthly_tokens / max(days_with_usage, 1)
                
                # Calculate usage spread
                if daily_usage_data:
                    max_daily_usage = max(item["tokens"] for item in daily_usage_data)
                    min_daily_usage = min(item["tokens"] for item in daily_usage_data)
                    usage_spread = (max_daily_usage - min_daily_usage) / max(max_daily_usage, 1) * 100
                else:
                    usage_spread = 0
                
                # Calculate hourly distribution for today
                total_hourly_tokens = sum(item["tokens"] for item in hourly_usage_data)
                hours_with_usage = len(hourly_usage_data)
                avg_hourly_usage = total_hourly_tokens / max(hours_with_usage, 1)
                
                return {
                    "monthly_distribution": {
                        "total_tokens": total_monthly_tokens,
                        "days_with_usage": days_with_usage,
                        "avg_daily_usage": avg_daily_usage,
                        "max_daily_usage": max_daily_usage if daily_usage_data else 0,
                        "min_daily_usage": min_daily_usage if daily_usage_data else 0,
                        "usage_spread_percentage": usage_spread,
                        "daily_usage_data": daily_usage_data
                    },
                    "daily_distribution": {
                        "total_tokens": total_hourly_tokens,
                        "hours_with_usage": hours_with_usage,
                        "avg_hourly_usage": avg_hourly_usage,
                        "hourly_usage_data": hourly_usage_data
                    },
                    "rate_limiting_status": {
                        "max_daily_percentage": MAX_DAILY_USAGE_PERCENTAGE,
                        "max_hourly_percentage": MAX_HOURLY_USAGE_PERCENTAGE,
                        "min_daily_percentage": MIN_DAILY_USAGE_PERCENTAGE,
                        "ai_cooldown_period": AI_COOLDOWN_PERIOD,
                        "max_concurrent_requests": MAX_CONCURRENT_AI_REQUESTS,
                        "active_requests": self._active_requests,
                        "last_ai_requests": {
                            ai: last_request.isoformat() if last_request else None
                            for ai, last_request in self._last_ai_request.items()
                        }
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting usage distribution stats: {str(e)}")
            return {
                "error": str(e),
                "monthly_distribution": {},
                "daily_distribution": {},
                "rate_limiting_status": {}
            }

    async def _check_anthropic_connectivity(self) -> bool:
        """Check if Anthropic API is reachable with a quick connectivity test"""
        try:
            import os
            import requests
            
            # Check if API key is available
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("Anthropic API key not found")
                return False
            
            # For now, assume connectivity if API key exists
            # The actual connectivity test can be expensive and slow
            logger.info("Anthropic API key found, assuming connectivity")
            return True
            
        except Exception as e:
            logger.warning(f"Anthropic API connectivity check failed: {str(e)}")
            return False

    async def reset_all_usage_for_testing(self) -> bool:
        """Reset all usage data for testing purposes"""
        try:
            current_month = datetime.utcnow().strftime("%Y-%m")
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            async with get_session() as session:
                for ai_type in ai_types:
                    # Reset main AI usage
                    stmt = select(TokenUsage).where(
                        and_(
                            TokenUsage.ai_type == ai_type,
                            TokenUsage.month_year == current_month
                        )
                    )
                    result = await session.execute(stmt)
                    usage = result.scalar_one_or_none()
                    
                    if usage:
                        usage.total_tokens = 0
                        usage.usage_percentage = 0.0
                        usage.last_updated = datetime.utcnow()
                    
                    # Reset OpenAI usage
                    openai_ai_name = f"{ai_type}_openai"
                    stmt_openai = select(TokenUsage).where(
                        and_(
                            TokenUsage.ai_type == openai_ai_name,
                            TokenUsage.month_year == current_month
                        )
                    )
                    result_openai = await session.execute(stmt_openai)
                    usage_openai = result_openai.scalar_one_or_none()
                    
                    if usage_openai:
                        usage_openai.total_tokens = 0
                        usage_openai.usage_percentage = 0.0
                        usage_openai.last_updated = datetime.utcnow()
                
                await session.commit()
                logger.info("Reset all usage data for testing")
                return True
                
        except Exception as e:
            logger.error(f"Error resetting usage data: {str(e)}")
            return False


# Global instance
token_usage_service = TokenUsageService() 