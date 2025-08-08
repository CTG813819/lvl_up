#!/usr/bin/env python3
"""
Test script to verify frontend proposal status handling
"""

import requests
import json

def test_backend_proposal_status():
    """Test what the backend returns for proposals"""
    print("🧪 Testing Backend Proposal Status")
    print("=" * 50)
    
    # Test the main proposals endpoint (should return only test-passed + test_status=passed)
    try:
        response = requests.get("http://34.202.215.209:8000/api/proposals")
        print(f"✅ Backend response status: {response.status_code}")
        
        if response.status_code == 200:
            proposals = response.json()
            print(f"📋 Found {len(proposals)} proposals")
            
            if proposals:
                print("\n📊 Proposal Status Breakdown:")
                status_counts = {}
                for prop in proposals:
                    status = prop.get('status', 'unknown')
                    test_status = prop.get('test_status', 'unknown')
                    status_counts[f"{status}+{test_status}"] = status_counts.get(f"{status}+{test_status}", 0) + 1
                
                for status_combo, count in status_counts.items():
                    print(f"  {status_combo}: {count}")
                
                # Show first few proposals
                print("\n🔍 Sample Proposals:")
                for i, prop in enumerate(proposals[:3]):
                    print(f"  Proposal {i+1}:")
                    print(f"    ID: {prop.get('id')}")
                    print(f"    Status: {prop.get('status')}")
                    print(f"    Test Status: {prop.get('test_status')}")
                    print(f"    AI Type: {prop.get('ai_type')}")
                    print()
            else:
                print("📭 No proposals returned (this is expected with stricter filtering)")
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing backend: {e}")

def test_admin_proposal_status():
    """Test admin endpoint to see all proposals"""
    print("\n👨‍💼 Testing Admin Proposal Access")
    print("=" * 50)
    
    try:
        response = requests.get("http://34.202.215.209:8000/api/proposals/all")
        print(f"✅ Admin response status: {response.status_code}")
        
        if response.status_code == 200:
            proposals = response.json()
            print(f"📋 Found {len(proposals)} total proposals (admin view)")
            
            if proposals:
                print("\n📊 Admin Status Breakdown:")
                status_counts = {}
                for prop in proposals:
                    status = prop.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
                
                # Show test-passed proposals
                test_passed = [p for p in proposals if p.get('status') == 'test-passed' and p.get('test_status') == 'passed']
                print(f"\n✅ User-ready proposals (test-passed + test_status=passed): {len(test_passed)}")
                
                if test_passed:
                    print("🔍 Sample User-Ready Proposals:")
                    for i, prop in enumerate(test_passed[:2]):
                        print(f"  User-Ready Proposal {i+1}:")
                        print(f"    ID: {prop.get('id')}")
                        print(f"    Status: {prop.get('status')}")
                        print(f"    Test Status: {prop.get('test_status')}")
                        print(f"    AI Type: {prop.get('ai_type')}")
                        print()
            else:
                print("📭 No proposals in admin view")
        else:
            print(f"❌ Admin endpoint error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing admin endpoint: {e}")

if __name__ == "__main__":
    test_backend_proposal_status()
    test_admin_proposal_status()
    
    print("\n" + "=" * 50)
    print("🎯 Expected Results:")
    print("✅ Backend /api/proposals should return 0 proposals (stricter filtering)")
    print("✅ Admin /api/proposals/all should show test-passed proposals")
    print("✅ Frontend should now correctly map test-passed to ProposalStatus.testPassed")
    print("=" * 50) 