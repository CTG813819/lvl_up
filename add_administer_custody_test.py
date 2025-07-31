#!/usr/bin/env python3
"""
Add Administer Custody Test Method
==================================

This script adds the missing administer_custody_test method to the custody protocol service.
"""

import os
import sys

def add_administer_custody_test_method():
    """Add the missing administer_custody_test method"""
    try:
        print("🔧 Adding administer_custody_test method...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup
        backup_file = custody_file + ".backup8"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Add the administer_custody_test method before the last method
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Look for the last method (clear_test_results)
            if 'def clear_test_results(self, ai_type: Optional[str] = None):' in line:
                # Add the administer_custody_test method before this
                new_lines.insert(i, '')
                new_lines.insert(i, '    async def administer_custody_test(self, ai_type: str, test_category: Optional[TestCategory] = None) -> Dict[str, Any]:')
                new_lines.insert(i, '        """')
                new_lines.insert(i, '        Administer a custody protocol test for the specified AI type.')
                new_lines.insert(i, '        ')
                new_lines.insert(i, '        Args:')
                new_lines.insert(i, '            ai_type: Type of AI to test')
                new_lines.insert(i, '            test_category: Optional test category')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '        Returns:')
                new_lines.insert(i, '            Test results dictionary')
                new_lines.insert(i, '        """')
                new_lines.insert(i, '        try:')
                new_lines.insert(i, '            logger.info(f"Administering custody test for {ai_type}")')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Determine test category if not provided')
                new_lines.insert(i, '            if test_category is None:')
                new_lines.insert(i, '                test_category = TestCategory.KNOWLEDGE_VERIFICATION')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Execute the test')
                new_lines.insert(i, '            result = await self.execute_custody_test(ai_type, "comprehensive")')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            # Add test category to result')
                new_lines.insert(i, '            result["test_category"] = test_category.value')
                new_lines.insert(i, '            result["ai_type"] = ai_type')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '            logger.info(f"Custody test administered for {ai_type}: {result.get(\'passed\', False)}")')
                new_lines.insert(i, '            return result')
                new_lines.insert(i, '            ')
                new_lines.insert(i, '        except Exception as e:')
                new_lines.insert(i, '            logger.error(f"Error administering custody test for {ai_type}: {str(e)}")')
                new_lines.insert(i, '            return {')
                new_lines.insert(i, '                "passed": False,')
                new_lines.insert(i, '                "score": 0,')
                new_lines.insert(i, '                "error": str(e),')
                new_lines.insert(i, '                "ai_type": ai_type,')
                new_lines.insert(i, '                "test_category": test_category.value if test_category else "unknown"')
                new_lines.insert(i, '            }')
                break
        
        # Write the updated content
        with open(custody_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ administer_custody_test method added")
        return True
        
    except Exception as e:
        print(f"❌ Error adding administer_custody_test method: {str(e)}")
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
    print("🔧 Adding Administer Custody Test Method")
    print("=" * 40)
    
    # Add the administer_custody_test method
    if add_administer_custody_test_method():
        print("✅ Method added")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Administer custody test method added successfully!")
            print("The custody protocol service now has all required methods.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to add administer_custody_test method")

if __name__ == "__main__":
    main() 