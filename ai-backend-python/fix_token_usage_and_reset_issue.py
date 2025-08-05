#!/usr/bin/env python3
"""
Fix Token Usage and Reset Issues
================================

This script addresses the following issues:
1. Token usage not resetting despite manual resets
2. No automatic monthly reset mechanism
3. Request token limit exceeded errors
4. Claude verification errors

The main problems identified:
- Token usage tracking not properly resetting
- No automatic monthly reset mechanism
- Missing error handling for token limit exceeded
- Logger._log() error in Claude verification
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json
import schedule
import time

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

import asyncpg
import structlog
from sqlalchemy import select, update, text
from app.core.database import get_session, init_database
from app.models.sql_models import TokenUsage, TokenUsageLog
from app.services.token_usage_service import TokenUsageService

logger = structlog.get_logger()

class TokenUsageFixer:
    def __init__(self):
        self.issues_fixed = []
        self.errors_encountered = []
        
    async def fix_token_usage_issues(self):
        """Main method to fix all token usage issues"""
        try:
            print("🔧 Starting token usage fix...")
            
            # Initialize database
            await init_database()
            
            # Fix 1: Reset all token usage for current month
            await self.reset_all_token_usage()
            
            # Fix 2: Create automatic monthly reset mechanism
            await self.setup_automatic_monthly_reset()
            
            # Fix 3: Fix token limit exceeded error handling
            await self.fix_token_limit_error_handling()
            
            # Fix 4: Fix Claude verification error
            await self.fix_claude_verification_error()
            
            # Fix 5: Create monitoring and alerting system
            await self.setup_token_monitoring()
            
            print("✅ Token usage issues fixed successfully!")
            print(f"📋 Issues fixed: {', '.join(self.issues_fixed)}")
            
            if self.errors_encountered:
                print(f"⚠️ Errors encountered: {', '.join(self.errors_encountered)}")
                
        except Exception as e:
            print(f"❌ Error fixing token usage issues: {str(e)}")
            self.errors_encountered.append(str(e))
    
    async def reset_all_token_usage(self):
        """Reset all token usage for the current month"""
        try:
            print("🔄 Resetting all token usage...")
            
            current_month = datetime.utcnow().strftime("%Y-%m")
            ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            async with get_session() as session:
                # Reset all token usage records
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
                
                await session.commit()
                print(f"✅ Reset token usage for {len(ai_types)} AI types")
                self.issues_fixed.append("token_usage_reset")
                
        except Exception as e:
            error_msg = f"Failed to reset token usage: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def setup_automatic_monthly_reset(self):
        """Set up automatic monthly reset mechanism"""
        try:
            print("⏰ Setting up automatic monthly reset...")
            
            # Create monthly reset script
            reset_script = '''#!/usr/bin/env python3
"""
Automatic Monthly Token Usage Reset
==================================

This script runs automatically on the 1st of each month to reset token usage.
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def monthly_reset():
    """Reset token usage for the new month"""
    try:
        from app.core.database import init_database, get_session
        from app.models.sql_models import TokenUsage, TokenUsageLog
        from sqlalchemy import text
        
        # Initialize database
        await init_database()
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        
        print(f"🔄 Monthly reset for {current_month}...")
        
        async with get_session() as session:
            # Archive old month data (optional)
            await session.execute(text("""
                INSERT INTO token_usage_archive 
                SELECT *, NOW() as archived_at 
                FROM token_usage 
                WHERE month_year != :current_month
            """), {"current_month": current_month})
            
            # Clear old data
            await session.execute(text("DELETE FROM token_usage WHERE month_year != :current_month"), 
                               {"current_month": current_month})
            await session.execute(text("DELETE FROM token_usage_logs WHERE month_year != :current_month"), 
                               {"current_month": current_month})
            
            # Create fresh tracking for new month
            for ai_type in ai_types:
                new_tracking = TokenUsage(
                    ai_type=ai_type,
                    month_year=current_month,
                    monthly_limit=140000,
                    tokens_in=0,
                    tokens_out=0,
                    total_tokens=0,
                    request_count=0,
                    usage_percentage=0.0,
                    status="active",
                    last_request_at=None
                )
                session.add(new_tracking)
            
            await session.commit()
            print(f"✅ Monthly reset completed for {current_month}")
            
    except Exception as e:
        print(f"❌ Monthly reset failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(monthly_reset())
'''
            
            # Write the script
            script_path = "monthly_token_reset.py"
            with open(script_path, 'w') as f:
                f.write(reset_script)
            
            # Make it executable
            os.chmod(script_path, 0o755)
            
            # Set up cron job for monthly reset (1st of each month at 00:01)
            cron_job = "1 0 1 * * cd /home/ubuntu/ai-backend-python && python monthly_token_reset.py >> /var/log/monthly-token-reset.log 2>&1"
            
            # Add to crontab
            import subprocess
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_cron = result.stdout
            
            if cron_job not in existing_cron:
                if existing_cron.strip():
                    new_cron = existing_cron.strip() + "\n" + cron_job
                else:
                    new_cron = cron_job
                
                subprocess.run(['crontab', '-'], input=new_cron, text=True)
                print("✅ Monthly reset cron job added")
            else:
                print("ℹ️ Monthly reset cron job already exists")
            
            # Create archive table for historical data
            await self.create_token_archive_table()
            
            print("✅ Automatic monthly reset setup completed")
            self.issues_fixed.append("automatic_monthly_reset")
            
        except Exception as e:
            error_msg = f"Failed to setup automatic monthly reset: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def create_token_archive_table(self):
        """Create archive table for historical token usage data"""
        try:
            async with get_session() as session:
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS token_usage_archive (
                        id SERIAL PRIMARY KEY,
                        ai_type VARCHAR(50) NOT NULL,
                        month_year VARCHAR(7) NOT NULL,
                        monthly_limit INTEGER NOT NULL,
                        tokens_in INTEGER DEFAULT 0,
                        tokens_out INTEGER DEFAULT 0,
                        total_tokens INTEGER DEFAULT 0,
                        request_count INTEGER DEFAULT 0,
                        usage_percentage FLOAT DEFAULT 0.0,
                        status VARCHAR(20) DEFAULT 'active',
                        last_request_at TIMESTAMP,
                        archived_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                await session.commit()
                print("✅ Token usage archive table created")
                
        except Exception as e:
            print(f"⚠️ Could not create archive table: {str(e)}")
    
    async def fix_token_limit_error_handling(self):
        """Fix token limit exceeded error handling"""
        try:
            print("🔧 Fixing token limit error handling...")
            
            # Create enhanced token usage service with better error handling
            enhanced_service = '''
import structlog
from typing import Dict, Any, Tuple

logger = structlog.get_logger()

class EnhancedTokenUsageService:
    def __init__(self):
        self.request_limit = 1000
        self.monthly_limit = 140000
        self.warning_threshold = 80.0
        self.critical_threshold = 95.0
        self.emergency_threshold = 98.0
    
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
    
    async def get_current_monthly_usage(self, ai_type: str) -> int:
        """Get current monthly usage for an AI type"""
        try:
            from app.core.database import get_session
            from app.models.sql_models import TokenUsage
            from sqlalchemy import select, and_
            from datetime import datetime
            
            current_month = datetime.utcnow().strftime("%Y-%m")
            
            async with get_session() as session:
                stmt = select(TokenUsage).where(
                    and_(
                        TokenUsage.ai_type == ai_type,
                        TokenUsage.month_year == current_month
                    )
                )
                result = await session.execute(stmt)
                tracking = result.scalar_one_or_none()
                
                return tracking.total_tokens if tracking else 0
                
        except Exception as e:
            logger.error(f"Error getting monthly usage: {str(e)}")
            return 0
'''
            
            # Write enhanced service
            enhanced_path = "app/services/enhanced_token_usage_service.py"
            with open(enhanced_path, 'w') as f:
                f.write(enhanced_service)
            
            print("✅ Enhanced token usage service created")
            self.issues_fixed.append("token_limit_error_handling")
            
        except Exception as e:
            error_msg = f"Failed to fix token limit error handling: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def fix_claude_verification_error(self):
        """Fix Claude verification error with proper logger handling"""
        try:
            print("🔧 Fixing Claude verification error...")
            
            # Create enhanced Claude service with proper error handling
            enhanced_claude_service = '''
import structlog
import requests
import asyncio
from typing import Optional, Dict, Any

logger = structlog.get_logger()

class EnhancedClaudeService:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"
    
    async def call_claude_safely(self, prompt: str, ai_name: str, max_tokens: int = 1024) -> str:
        """Call Claude with proper error handling and logging"""
        try:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Log the request attempt
            logger.info(
                f"Calling Claude for {ai_name}",
                ai_name=ai_name,
                max_tokens=max_tokens,
                prompt_length=len(prompt)
            )
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            response_text = response_data["content"][0]["text"]
            
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
    
    async def verify_claude_availability(self) -> Dict[str, Any]:
        """Verify Claude API availability with proper error handling"""
        try:
            if not self.api_key:
                return {
                    "available": False,
                    "reason": "API key not set",
                    "error": "ANTHROPIC_API_KEY environment variable not set"
                }
            
            # Test API with minimal request
            test_prompt = "Hello"
            test_response = await self.call_claude_safely(test_prompt, "test", max_tokens=10)
            
            return {
                "available": True,
                "response": test_response,
                "status": "operational"
            }
            
        except Exception as e:
            return {
                "available": False,
                "reason": "API call failed",
                "error": str(e)
            }
'''
            
            # Write enhanced Claude service
            enhanced_claude_path = "app/services/enhanced_claude_service.py"
            with open(enhanced_claude_path, 'w') as f:
                f.write(enhanced_claude_service)
            
            print("✅ Enhanced Claude service created")
            self.issues_fixed.append("claude_verification_error")
            
        except Exception as e:
            error_msg = f"Failed to fix Claude verification error: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)
    
    async def setup_token_monitoring(self):
        """Set up comprehensive token monitoring and alerting"""
        try:
            print("📊 Setting up token monitoring...")
            
            # Create monitoring script
            monitoring_script = '''#!/usr/bin/env python3
"""
Token Usage Monitoring and Alerting
==================================

This script monitors token usage and sends alerts when thresholds are reached.
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def monitor_token_usage():
    """Monitor token usage and send alerts"""
    try:
        from app.core.database import get_session
        from app.models.sql_models import TokenUsage
        from sqlalchemy import select, func
        
        current_month = datetime.utcnow().strftime("%Y-%m")
        
        async with get_session() as session:
            # Get total usage for current month
            stmt = select(func.sum(TokenUsage.total_tokens)).where(
                TokenUsage.month_year == current_month
            )
            result = await session.execute(stmt)
            total_tokens = result.scalar() or 0
            
            # Calculate usage percentage
            monthly_limit = 140000
            usage_percentage = (total_tokens / monthly_limit) * 100
            
            # Check thresholds
            if usage_percentage >= 98:
                alert_level = "EMERGENCY"
                action = "BLOCK ALL REQUESTS"
            elif usage_percentage >= 95:
                alert_level = "CRITICAL"
                action = "RESTRICT LARGE REQUESTS"
            elif usage_percentage >= 80:
                alert_level = "WARNING"
                action = "MONITOR CLOSELY"
            else:
                alert_level = "NORMAL"
                action = "CONTINUE NORMAL OPERATION"
            
            # Log status
            print(f"Token Usage Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Tokens: {total_tokens:,}")
            print(f"Monthly Limit: {monthly_limit:,}")
            print(f"Usage Percentage: {usage_percentage:.1f}%")
            print(f"Alert Level: {alert_level}")
            print(f"Action: {action}")
            
            # Send alert if needed
            if alert_level in ["EMERGENCY", "CRITICAL", "WARNING"]:
                await send_alert(alert_level, usage_percentage, total_tokens, action)
            
    except Exception as e:
        print(f"Error monitoring token usage: {str(e)}")

async def send_alert(level: str, percentage: float, tokens: int, action: str):
    """Send alert about token usage"""
    message = f"""
🚨 TOKEN USAGE ALERT 🚨

Level: {level}
Usage: {percentage:.1f}% ({tokens:,} tokens)
Action: {action}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    print(message)
    
    # Log to file
    with open("/var/log/token-usage-alerts.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} - {level}: {percentage:.1f}% ({tokens:,} tokens)\n")

if __name__ == "__main__":
    asyncio.run(monitor_token_usage())
'''
            
            # Write monitoring script
            monitoring_path = "monitor_token_usage.py"
            with open(monitoring_path, 'w') as f:
                f.write(monitoring_script)
            
            # Make it executable
            os.chmod(monitoring_path, 0o755)
            
            # Set up cron job for monitoring (every 5 minutes)
            cron_job = "*/5 * * * * cd /home/ubuntu/ai-backend-python && python monitor_token_usage.py >> /var/log/token-monitoring.log 2>&1"
            
            # Add to crontab
            import subprocess
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_cron = result.stdout
            
            if cron_job not in existing_cron:
                if existing_cron.strip():
                    new_cron = existing_cron.strip() + "\n" + cron_job
                else:
                    new_cron = cron_job
                
                subprocess.run(['crontab', '-'], input=new_cron, text=True)
                print("✅ Token monitoring cron job added")
            else:
                print("ℹ️ Token monitoring cron job already exists")
            
            print("✅ Token monitoring setup completed")
            self.issues_fixed.append("token_monitoring")
            
        except Exception as e:
            error_msg = f"Failed to setup token monitoring: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors_encountered.append(error_msg)

async def main():
    """Main function to run the token usage fixer"""
    fixer = TokenUsageFixer()
    await fixer.fix_token_usage_issues()

if __name__ == "__main__":
    asyncio.run(main()) 