#!/usr/bin/env python3
"""
Verification script for XP display and diverse test generation fixes
"""

import asyncio
import requests
import json
from datetime import datetime

class FixVerifier:
    def __init__(self):
        self.base_url = "http://ec2-34-202-215-209.compute-1.amazonaws.com:8000"
        self.verification_results = {}
    
    async def verify_xp_display_fix(self):
        """Verify that XP display is working correctly"""
        print("🔍 Verifying XP display fix...")
        
        try:
            # Test the custody analytics endpoint
            response = requests.get(f"{self.base_url}/custody/analytics", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if XP values are being displayed correctly
                ai_metrics = data.get("data", {}).get("ai_specific_metrics", {})
                
                xp_issues_found = []
                for ai_type, metrics in ai_metrics.items():
                    xp = metrics.get("custody_xp", 0)
                    if xp == 0:
                        xp_issues_found.append(ai_type)
                
                if xp_issues_found:
                    print(f"⚠️  Found AIs with zero XP: {', '.join(xp_issues_found)}")
                    self.verification_results["xp_display"] = "partial"
                else:
                    print("✅ XP display appears to be working correctly")
                    self.verification_results["xp_display"] = "success"
                
                return True
            else:
                print(f"❌ Failed to get custody analytics: {response.status_code}")
                self.verification_results["xp_display"] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Error verifying XP display: {e}")
            self.verification_results["xp_display"] = "error"
            return False
    
    async def verify_diverse_test_generation(self):
        """Verify that diverse test generation is working"""
        print("🔍 Verifying diverse test generation...")
        
        try:
            # Test the custody test endpoint
            response = requests.post(
                f"{self.base_url}/custody/test/imperium",
                json={"test_category": "knowledge_verification"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if diverse test generation is being used
                test_content = data.get("data", {}).get("test_content", {})
                test_type = test_content.get("test_type", "")
                
                if "diverse" in test_type.lower():
                    print("✅ Diverse test generation is working")
                    self.verification_results["diverse_tests"] = "success"
                else:
                    print("⚠️  Diverse test generation may not be active")
                    self.verification_results["diverse_tests"] = "partial"
                
                return True
            else:
                print(f"❌ Failed to trigger custody test: {response.status_code}")
                self.verification_results["diverse_tests"] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Error verifying diverse test generation: {e}")
            self.verification_results["diverse_tests"] = "error"
            return False
    
    async def verify_service_status(self):
        """Verify that the service is running"""
        print("🔍 Verifying service status...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                print("✅ Service is running and responding")
                self.verification_results["service_status"] = "success"
                return True
            else:
                print(f"❌ Service returned status code: {response.status_code}")
                self.verification_results["service_status"] = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Service is not responding: {e}")
            self.verification_results["service_status"] = "error"
            return False
    
    async def check_recent_logs(self):
        """Check recent logs for diverse test generation and XP fixes"""
        print("🔍 Checking recent logs...")
        
        try:
            # This would require SSH access to check logs
            # For now, we'll just note that this check is available
            print("ℹ️  Log checking requires SSH access to EC2 instance")
            print("📝 You can check logs manually with:")
            print("   ssh -i lvl_up_key.pem ubuntu@ec2-54-147-131-199.compute-1.amazonaws.com")
            print("   sudo journalctl -u ai-backend-python -f")
            
            self.verification_results["log_check"] = "manual_required"
            return True
            
        except Exception as e:
            print(f"❌ Error checking logs: {e}")
            self.verification_results["log_check"] = "error"
            return False
    
    async def run_comprehensive_verification(self):
        """Run all verification checks"""
        print("🚀 Starting comprehensive verification...")
        print("=" * 50)
        
        # Check service status first
        await self.verify_service_status()
        print()
        
        # Check XP display
        await self.verify_xp_display_fix()
        print()
        
        # Check diverse test generation
        await self.verify_diverse_test_generation()
        print()
        
        # Check logs
        await self.check_recent_logs()
        print()
        
        # Print summary
        self.print_verification_summary()
    
    def print_verification_summary(self):
        """Print a summary of verification results"""
        print("=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        for check, result in self.verification_results.items():
            status_emoji = {
                "success": "✅",
                "partial": "⚠️",
                "failed": "❌",
                "error": "💥",
                "manual_required": "📝"
            }.get(result, "❓")
            
            check_name = check.replace("_", " ").title()
            print(f"{status_emoji} {check_name}: {result}")
        
        print()
        
        # Overall assessment
        success_count = sum(1 for result in self.verification_results.values() if result == "success")
        total_checks = len(self.verification_results)
        
        if success_count == total_checks:
            print("🎉 All checks passed! The fixes are working correctly.")
        elif success_count > total_checks / 2:
            print("⚠️  Most checks passed, but some issues remain.")
        else:
            print("❌ Multiple issues detected. Please review the fixes.")

async def main():
    verifier = FixVerifier()
    await verifier.run_comprehensive_verification()

if __name__ == "__main__":
    asyncio.run(main()) 