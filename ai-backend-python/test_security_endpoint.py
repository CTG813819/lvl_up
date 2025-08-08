#!/usr/bin/env python3
"""
Test script to check the security endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_security_endpoint():
    """Test the security endpoint"""
    base_url = "https://compassionate-truth-production-2fcd.up.railway.app"
    
    print(f"🔍 Testing security endpoint at {base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{base_url}/api/security/cryptographic-status")
            
            print(f"✅ Security Cryptographic Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   Error: {response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Security endpoint error: {str(e)}")
    
    print("=" * 80)
    print("✅ Security endpoint testing completed!")

if __name__ == "__main__":
    asyncio.run(test_security_endpoint())
