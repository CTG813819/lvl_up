#!/usr/bin/env python3
"""
Debug script to test notifications router import
"""

import sys
import os

# Add the ai-backend-python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

def test_notifications_import():
    """Test if notifications router can be imported"""
    try:
        print("Testing notifications router import...")
        
        # Test importing the router
        from app.routers import notifications
        print("✅ Notifications router imported successfully")
        
        # Test importing the notification service
        from app.services.notification_service import notification_service
        print("✅ Notification service imported successfully")
        
        # Test creating router instance
        router = notifications.router
        print("✅ Router instance created successfully")
        
        # List the routes
        routes = [route.path for route in router.routes]
        print(f"✅ Router has {len(routes)} routes: {routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_notifications_import()
    sys.exit(0 if success else 1) 