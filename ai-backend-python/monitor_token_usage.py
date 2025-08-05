#!/usr/bin/env python3
"""
Token Usage Monitor
Real-time monitoring of Anthropic token usage with alerts
"""

import asyncio
import time
import json
from datetime import datetime
from app.services.token_usage_service import token_usage_service, WARNING_THRESHOLD, CRITICAL_THRESHOLD, EMERGENCY_SHUTDOWN_THRESHOLD
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
        print(f"⚠️  Warning threshold: {WARNING_THRESHOLD}%")
        print(f"🚨 Critical threshold: {CRITICAL_THRESHOLD}%")
        print(f"🛑 Emergency threshold: {EMERGENCY_SHUTDOWN_THRESHOLD}%")
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
                    if usage_percentage < WARNING_THRESHOLD:
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