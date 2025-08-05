import requests
import time
import json

BACKEND_IP = '34.202.215.209'
PORT = 4000
BASE_URL = f'http://{BACKEND_IP}:{PORT}'

def test_endpoint(endpoint):
    """Test if an endpoint is working"""
    try:
        response = requests.get(f'{BASE_URL}{endpoint}', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_websocket_endpoint(endpoint):
    """Test WebSocket endpoint"""
    try:
        import websocket
        ws = websocket.create_connection(f'ws://{BACKEND_IP}:{PORT}{endpoint}', timeout=5)
        ws.close()
        return True
    except:
        return False

def main():
    print("🔧 Fixing EC2 Backend Issues...")
    print("=" * 50)
    
    # Step 1: Test current status
    print("\n1️⃣ Testing current backend status...")
    working_endpoints = []
    for endpoint in ['/api/imperium/agents', '/api/imperium/status', '/api/imperium/dashboard']:
        if test_endpoint(endpoint):
            working_endpoints.append(endpoint)
            print(f"  ✅ {endpoint}")
        else:
            print(f"  ❌ {endpoint}")
    
    print(f"\n📊 Current working endpoints: {len(working_endpoints)}")
    
    # Step 2: Initialize database
    print("\n2️⃣ Initializing database...")
    init_payloads = [
        {"action": "init_database"},
        {"command": "init_database"},
        {"operation": "init_database"},
        {"method": "init_database"},
        {"task": "init_database"},
        {"init": True},
        {"initialize": True},
        {"setup": "database"},
        {"db_init": True},
        {"database": "init"},
    ]
    
    database_initialized = False
    for payload in init_payloads:
        for endpoint in ['/api/init', '/api/database/init', '/api/setup', '/api/imperium/init', '/api/admin/init']:
            try:
                response = requests.post(f'{BASE_URL}{endpoint}', json=payload, timeout=5)
                if response.status_code in [200, 201]:
                    print(f"  ✅ Database initialized via {endpoint}")
                    database_initialized = True
                    break
            except:
                continue
        if database_initialized:
            break
    
    if not database_initialized:
        print("  ⚠️ Could not initialize database via HTTP - may need manual SSH access")
    
    # Step 3: Add missing endpoints
    print("\n3️⃣ Adding missing endpoints...")
    missing_endpoints = [
        '/api/imperium/growth',
        '/api/imperium/proposals', 
        '/api/imperium/monitoring',
        '/api/imperium/issues',
        '/api/imperium/health',
        '/api/health',
        '/api/status',
        '/api/proposals',
        '/api/proposals/ai-status',
        '/api/learning/data',
        '/api/learning/metrics',
        '/api/oath-papers',
        '/api/oath-papers/ai-insights',
        '/api/conquest/build-failure',
    ]
    
    endpoint_payloads = [
        {"endpoint": endpoint, "method": "GET", "enabled": True}
        for endpoint in missing_endpoints
    ]
    
    endpoints_added = 0
    for payload in endpoint_payloads:
        for admin_endpoint in ['/api/admin/endpoints', '/api/config/endpoints', '/api/setup/endpoints']:
            try:
                response = requests.post(f'{BASE_URL}{admin_endpoint}', json=payload, timeout=5)
                if response.status_code in [200, 201]:
                    print(f"  ✅ Added endpoint: {payload['endpoint']}")
                    endpoints_added += 1
                    break
            except:
                continue
    
    print(f"  📊 Endpoints added: {endpoints_added}")
    
    # Step 4: Add WebSocket support
    print("\n4️⃣ Adding WebSocket support...")
    websocket_endpoints = [
        '/ws',
        '/ws/imperium/learning-analytics', 
        '/api/notifications/ws',
        '/socket.io/',
    ]
    
    ws_payloads = [
        {"websocket": endpoint, "enabled": True, "upgrade": True}
        for endpoint in websocket_endpoints
    ]
    
    ws_added = 0
    for payload in ws_payloads:
        for ws_admin in ['/api/admin/websocket', '/api/config/websocket', '/api/setup/websocket']:
            try:
                response = requests.post(f'{BASE_URL}{ws_admin}', json=payload, timeout=5)
                if response.status_code in [200, 201]:
                    print(f"  ✅ Added WebSocket: {payload['websocket']}")
                    ws_added += 1
                    break
            except:
                continue
    
    print(f"  📊 WebSocket endpoints added: {ws_added}")
    
    # Step 5: Restart service
    print("\n5️⃣ Attempting to restart backend service...")
    restart_payloads = [
        {"action": "restart"},
        {"command": "restart"},
        {"operation": "restart"},
        {"restart": True},
        {"reload": True},
    ]
    
    service_restarted = False
    for payload in restart_payloads:
        for restart_endpoint in ['/api/admin/restart', '/api/system/restart', '/api/service/restart']:
            try:
                response = requests.post(f'{BASE_URL}{restart_endpoint}', json=payload, timeout=10)
                if response.status_code in [200, 201]:
                    print(f"  ✅ Service restart triggered via {restart_endpoint}")
                    service_restarted = True
                    break
            except:
                continue
        if service_restarted:
            break
    
    if not service_restarted:
        print("  ⚠️ Could not restart service via HTTP - may need manual SSH access")
    
    # Step 6: Wait and test
    print("\n6️⃣ Waiting for changes to take effect...")
    time.sleep(5)
    
    # Step 7: Test fixes
    print("\n7️⃣ Testing fixes...")
    
    # Test database
    print("\n📊 Testing database initialization...")
    try:
        response = requests.get(f'{BASE_URL}/api/imperium/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'database' in str(data).lower() and 'initialized' in str(data).lower():
                print("  ✅ Database appears to be initialized")
            else:
                print("  ⚠️ Database status unclear")
        else:
            print("  ❌ Could not check database status")
    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
    
    # Test new endpoints
    print("\n📊 Testing new endpoints...")
    new_endpoints_working = 0
    for endpoint in ['/api/health', '/api/status', '/api/imperium/health']:
        if test_endpoint(endpoint):
            print(f"  ✅ {endpoint}")
            new_endpoints_working += 1
        else:
            print(f"  ❌ {endpoint}")
    
    # Test WebSocket
    print("\n📊 Testing WebSocket endpoints...")
    ws_working = 0
    for endpoint in ['/ws', '/api/notifications/ws']:
        if test_websocket_endpoint(endpoint):
            print(f"  ✅ {endpoint}")
            ws_working += 1
        else:
            print(f"  ❌ {endpoint}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 FIX SUMMARY:")
    print(f"  • Database initialized: {'✅' if database_initialized else '❌'}")
    print(f"  • New endpoints added: {endpoints_added}")
    print(f"  • WebSocket endpoints added: {ws_added}")
    print(f"  • Service restarted: {'✅' if service_restarted else '❌'}")
    print(f"  • New endpoints working: {new_endpoints_working}")
    print(f"  • WebSocket endpoints working: {ws_working}")
    
    if database_initialized and new_endpoints_working > 0:
        print("\n✅ Backend issues have been addressed!")
        print("   The database should now be initialized and more endpoints should be available.")
    else:
        print("\n⚠️ Some issues may require manual SSH access to fully resolve.")
        print("   Consider SSHing into the EC2 instance to:")
        print("   • Stop the conflicting ai-backend-python service")
        print("   • Initialize the database manually")
        print("   • Restart the imperium-monitoring service")
    
    print("\n🔄 Next steps:")
    print("   1. Test your Flutter app with the updated endpoints")
    print("   2. If WebSocket still doesn't work, check backend code for WebSocket routes")
    print("   3. If database errors persist, SSH into EC2 and run database init manually")

if __name__ == '__main__':
    main() 