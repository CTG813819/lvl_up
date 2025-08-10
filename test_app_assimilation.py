#!/usr/bin/env python3
"""
Test script for app assimilation service
Verifies that the assimilation process completes fully without getting stuck
"""

import asyncio
import json
import tempfile
import os
from datetime import datetime

async def test_app_assimilation():
    """Test the app assimilation process"""
    print("🧪 Testing App Assimilation Service...")
    
    try:
        # Import the service
        from app.services.app_assimilation_service import AppAssimilationService
        
        # Create service instance
        service = AppAssimilationService()
        print("✅ Service instance created")
        
        # Create a mock app analysis
        mock_analysis = {
            "file_type": "apk",
            "file_path": "/tmp/test.apk",
            "file_size": 1024 * 1024,  # 1MB
            "package_info": {
                "package_name": "com.test.app",
                "version_name": "1.0.0",
                "version_code": "1"
            },
            "security_analysis": {
                "encryption_used": False,
                "obfuscation_detected": False,
                "native_code_present": False,
                "sensitive_permissions": ["CAMERA", "LOCATION"],
                "vulnerability_score": 0.3,
                "chaos_integration_difficulty": "medium"
            },
            "chaos_integration_points": [
                {"type": "activity", "name": "MainActivity", "complexity": 1.0},
                {"type": "service", "name": "BackgroundService", "complexity": 1.5}
            ],
            "services": ["BackgroundService", "DataSyncService"],
            "permissions": ["INTERNET", "CAMERA", "LOCATION"]
        }
        
        print("📱 Mock analysis created")
        
        # Test assimilation
        print("🚀 Starting app assimilation...")
        start_time = datetime.now()
        
        result = await service.assimilate_app(mock_analysis, "test_user_123")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Assimilation completed in {duration:.2f} seconds")
        print(f"📊 Result: {json.dumps(result, indent=2, default=str)}")
        
        # Check if assimilation completed successfully
        app_id = result.get("app_id")
        if app_id:
            # Get the final status
            app_data = service.assimilated_apps.get(app_id)
            if app_data:
                progress = app_data.get("real_time_monitoring", {}).get("integration_progress", 0)
                chaos_status = app_data.get("chaos_integration_status", "unknown")
                synthetic_status = app_data.get("synthetic_code_status", "unknown")
                
                print(f"📈 Final Progress: {progress}%")
                print(f"🔮 Chaos Status: {chaos_status}")
                print(f"⚡ Synthetic Status: {synthetic_status}")
                
                if progress >= 100 and chaos_status in ["completed", "completed_fallback"]:
                    print("✅ App assimilation completed successfully!")
                    return True
                else:
                    print("❌ App assimilation did not complete properly")
                    return False
            else:
                print("❌ Could not retrieve app data after assimilation")
                return False
        else:
            print("❌ No app ID returned from assimilation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 APP ASSIMILATION SERVICE TEST")
    print("=" * 60)
    
    success = await test_app_assimilation()
    
    print("=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - App assimilation working correctly!")
    else:
        print("💥 TESTS FAILED - App assimilation has issues!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
