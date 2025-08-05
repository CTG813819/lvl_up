#!/usr/bin/env python3
"""
Test script to verify stricter proposal filtering and notification system
"""

import asyncio
import sys
import os
import requests
import json
from datetime import datetime

# Add the ai-backend-python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-backend-python'))

def test_proposal_filtering():
    """Test that only test-passed AND test_status=passed proposals are returned to users"""
    print("🧪 Testing stricter proposal filtering...")
    
    try:
        # Test the main proposals endpoint (should only return test-passed + test_status=passed)
        response = requests.get("http://localhost:8000/api/proposals/")
        
        if response.status_code == 200:
            data = response.json()
            proposals = data.get("data", []) if isinstance(data, dict) else data
            
            print(f"✅ Got {len(proposals)} proposals from main endpoint")
            
            # Check that all proposals have the correct status
            for proposal in proposals:
                status = proposal.get("status")
                test_status = proposal.get("test_status")
                
                if status != "test-passed" or test_status != "passed":
                    print(f"❌ Found proposal with incorrect status: {status}, test_status: {test_status}")
                    return False
                else:
                    print(f"✅ Proposal {proposal.get('id', 'unknown')} has correct status: {status}, test_status: {test_status}")
            
            print("✅ All proposals have correct status (test-passed + test_status=passed)")
            return True
        else:
            print(f"❌ Failed to get proposals: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing proposal filtering: {str(e)}")
        return False

def test_notifications():
    """Test that notifications are working"""
    print("\n🔔 Testing notification system...")
    
    try:
        # Test getting notifications
        response = requests.get("http://localhost:8000/api/notifications/")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get("data", {}).get("notifications", [])
            
            print(f"✅ Got {len(notifications)} notifications")
            
            # Check for live testing notifications
            live_testing_notifications = [
                n for n in notifications 
                if n.get("type") in ["live_testing", "live_testing_success", "live_testing_failure", "live_testing_error"]
            ]
            
            print(f"✅ Found {len(live_testing_notifications)} live testing notifications")
            
            # Check for proposal ready notifications
            proposal_ready_notifications = [
                n for n in notifications 
                if n.get("type") == "proposal_ready"
            ]
            
            print(f"✅ Found {len(proposal_ready_notifications)} proposal ready notifications")
            
            # Check for AI learning notifications
            learning_notifications = [
                n for n in notifications 
                if n.get("type") == "ai_learning"
            ]
            
            print(f"✅ Found {len(learning_notifications)} AI learning notifications")
            
            return True
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing notifications: {str(e)}")
        return False

def test_notification_stats():
    """Test notification statistics"""
    print("\n📊 Testing notification statistics...")
    
    try:
        response = requests.get("http://localhost:8000/api/notifications/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {})
            
            print(f"✅ Total notifications: {stats.get('total_notifications', 0)}")
            print(f"✅ Unread notifications: {stats.get('unread_notifications', 0)}")
            print(f"✅ Read notifications: {stats.get('read_notifications', 0)}")
            
            by_type = stats.get("by_type", {})
            print(f"✅ Notifications by type: {by_type}")
            
            by_priority = stats.get("by_priority", {})
            print(f"✅ Notifications by priority: {by_priority}")
            
            return True
        else:
            print(f"❌ Failed to get notification stats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing notification stats: {str(e)}")
        return False

def test_admin_proposals():
    """Test that admin can see all proposals including failed ones"""
    print("\n👨‍💼 Testing admin proposal access...")
    
    try:
        # Test the /all endpoint (admin access)
        response = requests.get("http://localhost:8000/api/proposals/all")
        
        if response.status_code == 200:
            data = response.json()
            proposals = data.get("data", []) if isinstance(data, dict) else data
            
            print(f"✅ Admin can see {len(proposals)} total proposals")
            
            # Count by status
            status_counts = {}
            for proposal in proposals:
                status = proposal.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"✅ Proposals by status: {status_counts}")
            
            # Check that we can see failed proposals in admin view
            failed_proposals = [p for p in proposals if p.get("status") in ["test-failed", "failed"]]
            print(f"✅ Found {len(failed_proposals)} failed proposals in admin view")
            
            return True
        else:
            print(f"❌ Failed to get admin proposals: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing admin proposals: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Stricter Proposals and Notifications System")
    print("=" * 60)
    
    tests = [
        ("Proposal Filtering", test_proposal_filtering),
        ("Notifications", test_notifications),
        ("Notification Stats", test_notification_stats),
        ("Admin Proposals", test_admin_proposals),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The stricter filtering and notification system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 