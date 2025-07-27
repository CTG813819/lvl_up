#!/usr/bin/env python3
"""
Fix custody protocol service indentation error
"""

import os
import shutil
from datetime import datetime

def fix_custody_indentation():
    """Fix the indentation error in custody_protocol_service.py"""
    
    print("🔧 Fixing Custody Protocol Indentation")
    print("=" * 40)
    
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
    
    # Fix the malformed method
    # Find the problematic section and replace it
    problematic_section = '''    def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str,
Any]:

    def clear_test_results(self, ai_type: Optional[str] = None):'''
    
    fixed_section = '''    def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get custody protocol analytics for a specific AI or all AIs.
        
        Args:
            ai_type: Optional AI type to filter by
            
        Returns:
            Analytics dictionary
        """
        try:
            analytics = {
                "recent_tests": [],
                "ai_performance": {},
                "average_score": 0,
                "failed_tests": 0,
                "passed_tests": 0,
                "total_tests": len(self.test_history),
            }
            return analytics
        except Exception as e:
            print(f"Error getting custody analytics: {e}")
            return {
                "recent_tests": [],
                "ai_performance": {},
                "average_score": 0,
                "failed_tests": 0,
                "passed_tests": 0,
                "total_tests": 0,
            }

    def clear_test_results(self, ai_type: Optional[str] = None):'''
    
    # Replace the problematic section
    if problematic_section in content:
        content = content.replace(problematic_section, fixed_section)
        print("✅ Fixed indentation error")
    else:
        print("⚠️ Problematic section not found, checking for other issues...")
        
        # Alternative fix - look for the specific line with the error
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip() == 'analytics = {' and i > 0:
                # Check if previous line is malformed
                if 'def get_custody_analytics' in lines[i-1] and '-> Dict[str,' in lines[i-1]:
                    # Fix the method definition
                    fixed_lines.append('    def get_custody_analytics(self, ai_type: Optional[str] = None) -> Dict[str, Any]:')
                    fixed_lines.append('        """')
                    fixed_lines.append('        Get custody protocol analytics for a specific AI or all AIs.')
                    fixed_lines.append('        ')
                    fixed_lines.append('        Args:')
                    fixed_lines.append('            ai_type: Optional AI type to filter by')
                    fixed_lines.append('            ')
                    fixed_lines.append('        Returns:')
                    fixed_lines.append('            Analytics dictionary')
                    fixed_lines.append('        """')
                    fixed_lines.append('        try:')
                    fixed_lines.append('            analytics = {')
                    print("✅ Fixed method definition")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
    
    # Write the fixed content
    with open(service_file, 'w') as f:
        f.write(content)
    
    print("✅ Indentation fixed")
    
    # Restart the service
    print("🔄 Restarting backend service...")
    os.system("sudo systemctl restart ai-backend-python.service")
    
    # Wait a moment and check status
    import time
    time.sleep(5)
    
    result = os.system("sudo systemctl is-active ai-backend-python.service")
    if result == 0:
        print("✅ Backend service restarted successfully")
    else:
        print("⚠️ Service may not be running, checking logs...")
        os.system("sudo journalctl -u ai-backend-python.service --no-pager -n 10")
    
    return True

if __name__ == "__main__":
    fix_custody_indentation()
    print("\n🎉 Custody protocol indentation fixed!") 