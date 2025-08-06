#!/usr/bin/env python3
"""
Fix Custody Protocol Service Initialize Method
==============================================

This script adds the missing initialize method to the custody protocol service.
"""

import os
import sys

def add_initialize_method():
    """Add the missing initialize method to custody protocol service"""
    try:
        print("🔧 Adding initialize method to custody protocol service...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup
        backup_file = custody_file + ".backup6"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Add the initialize method after the __init__ method
        lines = content.split('\n')
        new_lines = []
        init_found = False
        
        for line in lines:
            new_lines.append(line)
            
            # Look for the end of __init__ method
            if '__init__(self):' in line:
                init_found = True
            elif init_found and line.strip() == '':
                # Add initialize method after __init__
                new_lines.append('    ')
                new_lines.append('    def initialize(self):')
                new_lines.append('        """Initialize the custody protocol service"""')
                new_lines.append('        try:')
                new_lines.append('            logger.info("Initializing Custody Protocol Service")')
                new_lines.append('            # Initialize any required components')
                new_lines.append('            self.test_results = {}')
                new_lines.append('            self.test_history = []')
                new_lines.append('            logger.info("Custody Protocol Service initialized successfully")')
                new_lines.append('            return True')
                new_lines.append('        except Exception as e:')
                new_lines.append('            logger.error(f"Error initializing Custody Protocol Service: {str(e)}")')
                new_lines.append('            return False')
                new_lines.append('')
                init_found = False
        
        # Write the updated content
        with open(custody_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Initialize method added to custody protocol service")
        return True
        
    except Exception as e:
        print(f"❌ Error adding initialize method: {str(e)}")
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
    print("🔧 Adding Initialize Method to Custody Protocol Service")
    print("=" * 50)
    
    # Add the initialize method
    if add_initialize_method():
        print("✅ Method added")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Initialize method added successfully!")
            print("The custody protocol service now has the required initialize method.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to add initialize method")

if __name__ == "__main__":
    main() 