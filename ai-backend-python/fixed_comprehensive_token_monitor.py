#!/usr/bin/env python3
"""
Fixed Comprehensive Token Usage Monitor
======================================

Monitors both Anthropic and OpenAI token usage with alerts and recommendations.
This version properly initializes the database.
"""

import asyncio
import time
from datetime import datetime, timedelta
import json
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import init_database
from app.services.token_usage_service import token_usage_service
from app.services.openai_service import openai_service

async def monitor_token_usage():
    """Monitor token usage for all AIs"""
    
    print("🔍 Starting comprehensive token usage monitoring...")
    print("=" * 60)
    
    # Initialize database and services
    print("📊 Initializing database and services...")
    await init_database()
    await token_usage_service.initialize()
    print("✅ Database and services initialized")
    
    ai_names = ["imperium", "guardian", "sandbox", "conquest"]
    
    while True:
        try:
            print(f"\n📊 Token Usage Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            total_anthropic_usage = 0
            total_openai_usage = 0
            
            for ai_name in ai_names:
                # Get Anthropic usage
                anthropic_usage = await token_usage_service.get_monthly_usage(ai_name)
                anthropic_percentage = anthropic_usage.get("usage_percentage", 0) if anthropic_usage else 0
                anthropic_tokens = anthropic_usage.get("total_tokens", 0) if anthropic_usage else 0
                total_anthropic_usage += anthropic_tokens
                
                # Get OpenAI usage
                openai_usage = await openai_service._get_openai_usage(ai_name)
                openai_tokens = openai_usage.get("total_tokens", 0)
                openai_percentage = (openai_tokens / 9000) * 100  # OpenAI limit
                total_openai_usage += openai_tokens
                
                # Status indicators
                anthropic_status = "🟢" if anthropic_percentage < 80 else "🟡" if anthropic_percentage < 95 else "🔴"
                openai_status = "🟢" if openai_percentage < 80 else "🟡" if openai_percentage < 100 else "🔴"
                
                print(f"{ai_name.upper():<12} | Anthropic: {anthropic_status} {anthropic_percentage:5.1f}% ({anthropic_tokens:>6,} tokens)")
                print(f"{'':<12} | OpenAI:   {openai_status} {openai_percentage:5.1f}% ({openai_tokens:>6,} tokens)")
                
                # Check fallback availability
                should_use_openai, reason = await openai_service.should_use_openai(ai_name)
                fallback_status = "✅ Available" if should_use_openai else "❌ Not available"
                print(f"{'':<12} | Fallback: {fallback_status} ({reason.get('reason', 'unknown')})")
                print()
            
            # Global summary
            print("🌍 GLOBAL SUMMARY")
            print("-" * 60)
            total_anthropic_percentage = (total_anthropic_usage / 140000) * 100
            total_openai_percentage = (total_openai_usage / 9000) * 100
            
            print(f"Total Anthropic Usage: {total_anthropic_percentage:5.1f}% ({total_anthropic_usage:,} / 140,000 tokens)")
            print(f"Total OpenAI Usage:   {total_openai_percentage:5.1f}% ({total_openai_usage:,} / 9,000 tokens)")
            
            # Recommendations
            print("\n💡 RECOMMENDATIONS")
            print("-" * 60)
            
            if total_anthropic_percentage > 90:
                print("⚠️  Anthropic usage is high - consider reducing usage or increasing limits")
            elif total_anthropic_percentage > 80:
                print("📊 Anthropic usage is moderate - monitor closely")
            else:
                print("✅ Anthropic usage is healthy")
            
            if total_openai_percentage > 90:
                print("⚠️  OpenAI usage is high - fallback capacity limited")
            elif total_openai_percentage > 80:
                print("📊 OpenAI usage is moderate - monitor fallback capacity")
            else:
                print("✅ OpenAI fallback capacity is healthy")
            
            # Wait before next check
            print("\n⏳ Waiting 60 seconds before next check...")
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Error in monitoring: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(monitor_token_usage()) 