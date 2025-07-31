#!/usr/bin/env python3
"""
Fix Custody Protocol Service Initialize Method as Class Method
=============================================================

This script fixes the initialize method to be a class method instead of an instance method.
"""

import os
import sys

def fix_initialize_as_class_method():
    """Fix the initialize method to be a class method"""
    try:
        print("🔧 Fixing initialize method as class method...")
        
        custody_file = "app/services/custody_protocol_service.py"
        if not os.path.exists(custody_file):
            print(f"❌ {custody_file} not found")
            return False
        
        # Create a backup
        backup_file = custody_file + ".backup7"
        with open(custody_file, 'r') as f:
            content = f.read()
        
        with open(backup_file, 'w') as f:
            f.write(content)
        print(f"✅ Backup created: {backup_file}")
        
        # Replace the instance method with a class method
        old_method = '''    def initialize(self):
        """Initialize the custody protocol service"""
        try:
            logger.info("Initializing Custody Protocol Service")
            # Initialize any required components
            self.test_results = {}
            self.test_history = []
            logger.info("Custody Protocol Service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Custody Protocol Service: {str(e)}")
            return False'''
        
        new_method = '''    @classmethod
    async def initialize(cls):
        """Initialize the custody protocol service"""
        try:
            logger.info("Initializing Custody Protocol Service")
            # Create and return an instance
            instance = cls()
            instance.test_results = {}
            instance.test_history = []
            logger.info("Custody Protocol Service initialized successfully")
            return instance
        except Exception as e:
            logger.error(f"Error initializing Custody Protocol Service: {str(e)}")
            return None'''
        
        # Replace the method
        content = content.replace(old_method, new_method)
        
        # Write the updated content
        with open(custody_file, 'w') as f:
            f.write(content)
        
        print("✅ Initialize method fixed as class method")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing initialize method: {str(e)}")
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
    print("🔧 Fixing Initialize Method as Class Method")
    print("=" * 45)
    
    # Fix the initialize method
    if fix_initialize_as_class_method():
        print("✅ Method fixed")
        
        # Restart the service
        if restart_backend_service():
            print("✅ Backend service restarted")
            print("\n🎉 Initialize method fixed successfully!")
            print("The custody protocol service now has the correct class method.")
        else:
            print("❌ Failed to restart backend service")
    else:
        print("❌ Failed to fix initialize method")

if __name__ == "__main__":
    main() 