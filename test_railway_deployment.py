#!/usr/bin/env python3
"""
Test Railway deployment readiness
"""

import os
import asyncio
import requests
import json

# Set the database URL for Railway
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb"

def test_local_app():
    """Test if the app can start locally"""
    print("🔍 Testing local app startup...")
    
    try:
        # Set environment variable
        os.environ["DATABASE_URL"] = DATABASE_URL
        
        # Import the app
        from app.main import app
        print("✅ App import successful!")
        
        # Test if the app has the expected endpoints
        routes = [route.path for route in app.routes]
        print(f"✅ App has {len(routes)} routes")
        
        # Check for key endpoints
        key_endpoints = ["/health", "/api/health", "/api/status"]
        found_endpoints = [ep for ep in key_endpoints if any(ep in route for route in routes)]
        
        if found_endpoints:
            print(f"✅ Found key endpoints: {found_endpoints}")
            return True
        else:
            print("⚠️ Key endpoints not found in routes")
            return False
            
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def test_railway_current_status():
    """Test current Railway deployment status"""
    print("\n🔍 Testing current Railway deployment...")
    
    railway_url = "https://lvlup-production.up.railway.app"
    test_endpoints = ["/health", "/api/health", "/api/status"]
    
    working_endpoints = []
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{railway_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint}: {response.status_code}")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
    
    return working_endpoints

def create_railway_deployment_guide():
    """Create a deployment guide"""
    print("\n📋 Railway Deployment Guide")
    print("=" * 50)
    
    print("\n1. Add Environment Variables to Railway:")
    print("   • Go to Railway dashboard")
    print("   • Click on your service")
    print("   • Go to 'Variables' tab")
    print("   • Add new variable:")
    print("     Name: DATABASE_URL")
    print("     Value: postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb")
    
    print("\n2. Redeploy the Service:")
    print("   • In Railway dashboard, click 'Deploy'")
    print("   • Or push changes to your connected Git repository")
    
    print("\n3. Monitor Deployment:")
    print("   • Check the 'Deployments' tab for logs")
    print("   • Look for any startup errors")
    print("   • Verify the service is running")
    
    print("\n4. Test Endpoints:")
    print("   • Health: https://lvlup-production.up.railway.app/health")
    print("   • API Health: https://lvlup-production.up.railway.app/api/health")
    print("   • Status: https://lvlup-production.up.railway.app/api/status")

def main():
    print("🚀 Railway Deployment Readiness Test")
    print("=" * 50)
    
    # Test local app
    local_success = test_local_app()
    
    # Test current Railway status
    working_endpoints = test_railway_current_status()
    
    print(f"\n📊 Results:")
    print(f"• Local app: {'✅ Ready' if local_success else '❌ Issues'}")
    print(f"• Railway endpoints working: {len(working_endpoints)}/{3}")
    
    if local_success and len(working_endpoints) == 0:
        print("\n🎯 Status: Ready for Railway deployment!")
        print("The local app works, but Railway needs the DATABASE_URL environment variable.")
        create_railway_deployment_guide()
    elif local_success and len(working_endpoints) > 0:
        print("\n🎯 Status: Railway partially working!")
        print("Some endpoints are working, but you may need to add DATABASE_URL.")
    else:
        print("\n❌ Status: Local app has issues that need to be fixed first.")
    
    print("\n🔧 Next Steps:")
    print("1. Add DATABASE_URL to Railway environment variables")
    print("2. Redeploy your Railway service")
    print("3. Test the endpoints again")

if __name__ == "__main__":
    main() 