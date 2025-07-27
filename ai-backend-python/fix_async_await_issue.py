#!/usr/bin/env python3
"""
Fix async/await issue in custody protocol service
"""

import os
import shutil
from datetime import datetime

def fix_async_await_issue():
    """Fix the async/await issue in custody_protocol_service.py"""
    
    print("🔧 Fixing Async/Await Issue")
    print("=" * 30)
    
    # File paths
    service_file = "app/services/custody_protocol_service.py"
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{service_file}.backup{timestamp}"
    
    if os.path.exists(service_file):
        shutil.copy2(service_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    else:
        print(f"❌ Service file not found: {service_file}")
        return False
    
    # Read the file
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Fix the get_custody_analytics method to be async
    old_method = '''    def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get custody protocol analytics for a specific AI or all AIs.
        
        Args:
            ai_type: Optional AI type to filter by
            
        Returns:
            Analytics dictionary
        """
        try:
            if ai_type:
                # Filter tests for specific AI
                ai_tests = [t for t in self.test_history if t["ai_type"] == ai_type]
                passed_tests = len([t for t in ai_tests if t.get("passed", False)])
                failed_tests = len(ai_tests) - passed_tests
                average_score = sum(t.get("score", 0) for t in ai_tests) / len(ai_tests) if ai_tests else 0
            else:
                # All tests
                passed_tests = len([t for t in self.test_history if t.get("passed", False)])
                failed_tests = len(self.test_history) - passed_tests
                average_score = sum(t.get("score", 0) for t in self.test_history) / len(self.test_history) if self.test_history else 0
            
            analytics = {
                "recent_tests": self.test_history[-10:] if self.test_history else [],
                "ai_performance": self.ai_performance,
                "average_score": round(average_score, 2),
                "failed_tests": failed_tests,
                "passed_tests": passed_tests,
                "total_tests": len(self.test_history),
            }
            return analytics
        except Exception as e:
            logger.error(f"Error getting custody analytics: {e}")
            return {
                "recent_tests": [],
                "ai_performance": {},
                "average_score": 0,
                "failed_tests": 0,
                "passed_tests": 0,
                "total_tests": 0,
            }'''
    
    new_method = '''    async def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get custody protocol analytics for a specific AI or all AIs.
        
        Args:
            ai_type: Optional AI type to filter by
            
        Returns:
            Analytics dictionary
        """
        try:
            if ai_type:
                # Filter tests for specific AI
                ai_tests = [t for t in self.test_history if t["ai_type"] == ai_type]
                passed_tests = len([t for t in ai_tests if t.get("passed", False)])
                failed_tests = len(ai_tests) - passed_tests
                average_score = sum(t.get("score", 0) for t in ai_tests) / len(ai_tests) if ai_tests else 0
            else:
                # All tests
                passed_tests = len([t for t in self.test_history if t.get("passed", False)])
                failed_tests = len(self.test_history) - passed_tests
                average_score = sum(t.get("score", 0) for t in self.test_history) / len(self.test_history) if self.test_history else 0
            
            analytics = {
                "recent_tests": self.test_history[-10:] if self.test_history else [],
                "ai_performance": self.ai_performance,
                "average_score": round(average_score, 2),
                "failed_tests": failed_tests,
                "passed_tests": passed_tests,
                "total_tests": len(self.test_history),
            }
            return analytics
        except Exception as e:
            logger.error(f"Error getting custody analytics: {e}")
            return {
                "recent_tests": [],
                "ai_performance": {},
                "average_score": 0,
                "failed_tests": 0,
                "passed_tests": 0,
                "total_tests": 0,
            }'''
    
    # Replace the method
    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✅ Fixed get_custody_analytics method to be async")
    else:
        print("⚠️ Method not found, checking for other patterns...")
        
        # Alternative fix - look for the method definition
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if 'def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:' in line:
                # Make it async
                fixed_lines.append('    async def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:')
                print("✅ Fixed method definition to be async")
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
    
    # Write the fixed content
    with open(service_file, 'w') as f:
        f.write(content)
    
    print("✅ Async/await issue fixed")
    
    # Restart the service
    print("🔄 Restarting backend service...")
    os.system("sudo systemctl restart ai-backend-python.service")
    
    # Wait a moment and check status
    import time
    time.sleep(10)
    
    result = os.system("sudo systemctl is-active ai-backend-python.service")
    if result == 0:
        print("✅ Backend service restarted successfully")
    else:
        print("⚠️ Service may not be running, checking logs...")
        os.system("sudo journalctl -u ai-backend-python.service --no-pager -n 10")
    
    return True

if __name__ == "__main__":
    fix_async_await_issue()
    print("\n🎉 Async/await issue fixed!") 