#!/usr/bin/env python3
"""
Add Custody Analytics Method
============================

This script adds the missing get_custody_analytics method to the custody protocol service.
"""

import os
import sys

def add_custody_analytics_method():
    """Add the missing get_custody_analytics method"""
    try:
        print("🔧 Adding get_custody_analytics method...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup
        backup_file = custody_file + ".backup9"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Add the get_custody_analytics method before the last method
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Look for the clear_test_results method
            if 'def clear_test_results(self, ai_type: Optional[str] = None):' in line:
                # Add the get_custody_analytics method before this
                new_lines.insert(i, '')
                new_lines.insert(i, '    def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:')
                new_lines.insert(i, '        """')
                new_lines.insert(i, '        Get custody protocol analytics for a specific AI or all AIs.')
                new_lines.insert(i, '        ')
                new_lines.insert(i, '        Args:')
                new_lines.insert(i, '            ai_type: Optional AI type to filter by')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '        Returns:')
                new_lines.insert(i, '            Analytics dictionary')
                new_lines.insert(i, '        """')
                new_lines.insert(i, '        try:')
                new_lines.insert(i, '            analytics = {')
                new_lines.insert(i, '                "total_tests": len(self.test_history),')
                new_lines.insert(i, '                "passed_tests": 0,')
                new_lines.insert(i, '                "failed_tests": 0,')
                new_lines.insert(i, '                "average_score": 0,')
                new_lines.insert(i, '                "ai_performance": {},')
                new_lines.insert(i, '                "recent_tests": [],')
                new_lines.insert(i, '                "test_categories": {}')
                new_lines.insert(i, '            }')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            if not self.test_history:')
                new_lines.insert(i, '                return analytics')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Filter by AI type if specified')
                new_lines.insert(i, '            tests = self.test_history')
                new_lines.insert(i, '            if ai_type:')
                new_lines.insert(i, '                tests = [test for test in self.test_history if test.get("ai_type") == ai_type]')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            if not tests:')
                new_lines.insert(i, '                return analytics')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Calculate analytics')
                new_lines.insert(i, '            passed_count = sum(1 for test in tests if test.get("result", {}).get("passed", False))')
                new_lines.insert(i, '            total_count = len(tests)')
                new_lines.insert(i, '            scores = [test.get("result", {}).get("score", 0) for test in tests]')
                new_lines.insert(i, '            avg_score = sum(scores) / len(scores) if scores else 0')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            analytics.update({')
                new_lines.insert(i, '                "total_tests": total_count,')
                new_lines.insert(i, '                "passed_tests": passed_count,')
                new_lines.insert(i, '                "failed_tests": total_count - passed_count,')
                new_lines.insert(i, '                "average_score": round(avg_score, 2),')
                new_lines.insert(i, '                "pass_rate": round((passed_count / total_count) * 100, 2) if total_count > 0 else 0')
                new_lines.insert(i, '            })')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Get recent tests (last 10)')
                new_lines.insert(i, '            recent_tests = sorted(tests, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]')
                new_lines.insert(i, '            analytics["recent_tests"] = recent_tests')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Get AI performance breakdown')
                new_lines.insert(i, '            ai_performance = {}')
                new_lines.insert(i, '            for test in tests:')
                new_lines.insert(i, '                ai = test.get("ai_type", "unknown")')
                new_lines.insert(i, '                if ai not in ai_performance:')
                new_lines.insert(i, '                    ai_performance[ai] = {"total": 0, "passed": 0, "score": 0}')
                new_lines.insert(i, '                ai_performance[ai]["total"] += 1')
                new_lines.insert(i, '                if test.get("result", {}).get("passed", False):')
                new_lines.insert(i, '                    ai_performance[ai]["passed"] += 1')
                new_lines.insert(i, '                ai_performance[ai]["score"] += test.get("result", {}).get("score", 0)')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Calculate averages for each AI')
                new_lines.insert(i, '            for ai in ai_performance:')
                new_lines.insert(i, '                if ai_performance[ai]["total"] > 0:')
                new_lines.insert(i, '                    ai_performance[ai]["average_score"] = round(ai_performance[ai]["score"] / ai_performance[ai]["total"], 2)')
                new_lines.insert(i, '                    ai_performance[ai]["pass_rate"] = round((ai_performance[ai]["passed"] / ai_performance[ai]["total"]) * 100, 2)')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            analytics["ai_performance"] = ai_performance')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            return analytics')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '        except Exception as e:')
                new_lines.insert(i, '            logger.error(f"Error getting custody analytics: {str(e)}")')
                new_lines.insert(i, '            return {')
                new_lines.insert(i, '                "error": str(e),')
                new_lines.insert(i, '                "total_tests": 0,')
                new_lines.insert(i, '                "passed_tests": 0,')
                new_lines.insert(i, '                "failed_tests": 0,')
                new_lines.insert(i, '                "average_score": 0')
                new_lines.insert(i, '            }')
                break
        
        # Write the updated content
        with open(custody_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ get_custody_analytics method added")
        return True
        
    except Exception as e:
        print(f"❌ Error adding get_custody_analytics method: {str(e)}")
        return False

def restart_backend_service():
    """Restart the backend service"""
    try:
        print("🔄 Restarting backend service...")
        os.system("sudo systemctl restart ai-backend-python.service")
        return True
    except Exception as e:
        print(f"❌ Error restarting service: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔧 Adding Custody Analytics Method")
    print("=" * 35)
    
    # Add the get_custody_analytics method
    if add_custody_analytics_method():
        print("✅ Method added")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Custody analytics method added successfully!")
            print("The custody protocol service now has all required methods.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to add get_custody_analytics method")

if __name__ == "__main__":
    main() 