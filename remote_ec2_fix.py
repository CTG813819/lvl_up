import requests
import time
import json
from datetime import datetime

class RemoteEC2Fix:
    def __init__(self):
        self.backend_ip = '34.202.215.209'
        self.ports = [4000, 8000]
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': [],
            'errors': [],
            'tests_after': {}
        }

    def make_request(self, port, endpoint, method='GET', data=None, timeout=10):
        """Make HTTP request with error handling"""
        url = f'http://{self.backend_ip}:{port}{endpoint}'
        try:
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, timeout=timeout)
            else:
                return None, f"Unsupported method: {method}"
            
            return response, None
        except Exception as e:
            return None, str(e)

    def test_endpoint(self, port, endpoint):
        """Test if an endpoint is working"""
        response, error = self.make_request(port, endpoint)
        if error:
            return False, error
        return response.status_code == 200, response.status_code

    def fix_database_initialization(self):
        """Attempt to initialize database via HTTP requests"""
        print("🔧 Attempting database initialization...")
        
        init_payloads = [
            {"action": "init_database", "force": True},
            {"command": "init_database", "force": True},
            {"operation": "init_database", "force": True},
            {"method": "init_database", "force": True},
            {"task": "init_database", "force": True},
            {"init": True, "database": True, "force": True},
            {"initialize": True, "database": True, "force": True},
            {"setup": "database", "force": True},
            {"db_init": True, "force": True},
            {"database": "init", "force": True},
            {"trigger": "database_init", "force": True},
            {"fix": "database", "force": True},
        ]
        
        init_endpoints = [
            '/api/init',
            '/api/database/init',
            '/api/setup',
            '/api/imperium/init',
            '/api/admin/init',
            '/api/system/init',
            '/api/fix/database',
            '/api/trigger/init',
            '/api/command/init',
            '/api/operation/init',
        ]
        
        for payload in init_payloads:
            for endpoint in init_endpoints:
                for port in self.ports:
                    response, error = self.make_request(port, endpoint, 'POST', payload)
                    if response and response.status_code in [200, 201, 202]:
                        print(f"  ✅ Database initialization triggered via {endpoint} on port {port}")
                        self.results['fixes_applied'].append(f"Database init via {endpoint} on port {port}")
                        return True
                    elif response and response.status_code == 404:
                        continue  # Try next endpoint
                    elif error:
                        continue  # Try next endpoint
        
        print("  ⚠️ Could not initialize database via HTTP - may need SSH access")
        self.results['errors'].append("Database initialization failed via HTTP")
        return False

    def fix_missing_endpoints(self):
        """Attempt to add missing endpoints via HTTP requests"""
        print("🔧 Attempting to add missing endpoints...")
        
        missing_endpoints = [
            '/api/health',
            '/api/status',
            '/api/imperium/health',
            '/api/proposals',
            '/api/proposals/ai-status',
            '/api/learning/data',
            '/api/learning/metrics',
            '/api/oath-papers',
            '/api/oath-papers/ai-insights',
            '/api/conquest/build-failure',
        ]
        
        endpoint_payloads = [
            {"endpoint": endpoint, "method": "GET", "enabled": True, "create": True}
            for endpoint in missing_endpoints
        ]
        
        admin_endpoints = [
            '/api/admin/endpoints',
            '/api/config/endpoints',
            '/api/setup/endpoints',
            '/api/system/endpoints',
            '/api/fix/endpoints',
            '/api/create/endpoints',
        ]
        
        endpoints_added = 0
        for payload in endpoint_payloads:
            for admin_endpoint in admin_endpoints:
                for port in self.ports:
                    response, error = self.make_request(port, admin_endpoint, 'POST', payload)
                    if response and response.status_code in [200, 201, 202]:
                        print(f"  ✅ Added endpoint: {payload['endpoint']} via {admin_endpoint} on port {port}")
                        endpoints_added += 1
                        self.results['fixes_applied'].append(f"Added {payload['endpoint']} via {admin_endpoint} on port {port}")
                        break
                if response and response.status_code in [200, 201, 202]:
                    break
        
        print(f"  📊 Endpoints added: {endpoints_added}")
        return endpoints_added

    def fix_websocket_support(self):
        """Attempt to enable WebSocket support via HTTP requests"""
        print("🔧 Attempting to enable WebSocket support...")
        
        websocket_endpoints = [
            '/ws',
            '/ws/imperium/learning-analytics',
            '/api/notifications/ws',
            '/socket.io/',
        ]
        
        ws_payloads = [
            {"websocket": endpoint, "enabled": True, "upgrade": True, "create": True}
            for endpoint in websocket_endpoints
        ]
        
        ws_admin_endpoints = [
            '/api/admin/websocket',
            '/api/config/websocket',
            '/api/setup/websocket',
            '/api/system/websocket',
            '/api/fix/websocket',
            '/api/enable/websocket',
        ]
        
        ws_added = 0
        for payload in ws_payloads:
            for ws_admin in ws_admin_endpoints:
                for port in self.ports:
                    response, error = self.make_request(port, ws_admin, 'POST', payload)
                    if response and response.status_code in [200, 201, 202]:
                        print(f"  ✅ Added WebSocket: {payload['websocket']} via {ws_admin} on port {port}")
                        ws_added += 1
                        self.results['fixes_applied'].append(f"Added WebSocket {payload['websocket']} via {ws_admin} on port {port}")
                        break
                if response and response.status_code in [200, 201, 202]:
                    break
        
        print(f"  📊 WebSocket endpoints added: {ws_added}")
        return ws_added

    def restart_services(self):
        """Attempt to restart services via HTTP requests"""
        print("🔧 Attempting to restart services...")
        
        restart_payloads = [
            {"action": "restart", "force": True},
            {"command": "restart", "force": True},
            {"operation": "restart", "force": True},
            {"restart": True, "force": True},
            {"reload": True, "force": True},
            {"refresh": True, "force": True},
            {"reboot": True, "force": True},
        ]
        
        restart_endpoints = [
            '/api/admin/restart',
            '/api/system/restart',
            '/api/service/restart',
            '/api/restart',
            '/api/reload',
            '/api/refresh',
            '/api/reboot',
        ]
        
        for payload in restart_payloads:
            for restart_endpoint in restart_endpoints:
                for port in self.ports:
                    response, error = self.make_request(port, restart_endpoint, 'POST', payload, timeout=15)
                    if response and response.status_code in [200, 201, 202]:
                        print(f"  ✅ Service restart triggered via {restart_endpoint} on port {port}")
                        self.results['fixes_applied'].append(f"Service restart via {restart_endpoint} on port {port}")
                        return True
                    elif response and response.status_code == 404:
                        continue
                    elif error:
                        continue
        
        print("  ⚠️ Could not restart services via HTTP - may need SSH access")
        self.results['errors'].append("Service restart failed via HTTP")
        return False

    def test_fixes(self):
        """Test if fixes were successful"""
        print("\n🧪 Testing fixes...")
        time.sleep(5)  # Wait for changes to take effect
        
        test_results = {}
        
        for port in self.ports:
            port_results = {}
            
            # Test key endpoints
            key_endpoints = [
                '/api/health',
                '/api/status',
                '/api/imperium/health',
                '/api/proposals',
                '/api/learning/data',
            ]
            
            working_endpoints = 0
            for endpoint in key_endpoints:
                is_working, status = self.test_endpoint(port, endpoint)
                if is_working:
                    working_endpoints += 1
                    print(f"  ✅ Port {port} {endpoint} [200]")
                else:
                    print(f"  ❌ Port {port} {endpoint} [{status}]")
            
            port_results['working_endpoints'] = working_endpoints
            port_results['total_endpoints'] = len(key_endpoints)
            port_results['success_rate'] = (working_endpoints / len(key_endpoints) * 100) if key_endpoints else 0
            
            test_results[port] = port_results
        
        self.results['tests_after'] = test_results
        return test_results

    def run_fixes(self):
        """Run all fixes"""
        print("🚀 Starting Remote EC2 Fix...")
        print("=" * 50)
        
        # Step 1: Fix database
        db_fixed = self.fix_database_initialization()
        
        # Step 2: Add missing endpoints
        endpoints_added = self.fix_missing_endpoints()
        
        # Step 3: Enable WebSocket support
        ws_added = self.fix_websocket_support()
        
        # Step 4: Restart services
        services_restarted = self.restart_services()
        
        # Step 5: Test fixes
        test_results = self.test_fixes()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"remote_ec2_fix_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 50)
        print("🎯 REMOTE EC2 FIX SUMMARY")
        print("=" * 50)
        print(f"📊 Database initialized: {'✅' if db_fixed else '❌'}")
        print(f"📊 Endpoints added: {endpoints_added}")
        print(f"📊 WebSocket endpoints added: {ws_added}")
        print(f"📊 Services restarted: {'✅' if services_restarted else '❌'}")
        
        print(f"\n🧪 Test Results After Fixes:")
        for port, results in test_results.items():
            success_rate = results['success_rate']
            print(f"  📡 Port {port}: {results['working_endpoints']}/{results['total_endpoints']} endpoints working ({success_rate:.1f}%)")
        
        if self.results['errors']:
            print(f"\n❌ Errors encountered:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        if self.results['fixes_applied']:
            print(f"\n✅ Fixes applied:")
            for fix in self.results['fixes_applied']:
                print(f"  • {fix}")
        
        print(f"\n📄 Results saved to: {filename}")
        
        # Recommendations
        print(f"\n🔄 Next steps:")
        if db_fixed and endpoints_added > 0:
            print("  1. ✅ Remote fixes applied successfully!")
            print("  2. Test your Flutter app with the updated endpoints")
            print("  3. Run the comprehensive test again to verify improvements")
        else:
            print("  1. ⚠️ Some fixes require SSH access")
            print("  2. SSH into your EC2 instance and run the bash fix script")
            print("  3. Or use your EC2 console to access the instance")
        
        return self.results

def main():
    fixer = RemoteEC2Fix()
    results = fixer.run_fixes()

if __name__ == '__main__':
    main() 