#!/usr/bin/env python3
"""
Simplified EC2 Backend Test Script
Uses only standard library modules to avoid dependency issues
"""

import urllib.request
import urllib.error
import json
import time
import socket
from datetime import datetime

class SimpleEC2BackendTester:
    def __init__(self):
        self.base_url_8000 = "http://34.202.215.209:8000"
        self.base_url_4000 = "http://34.202.215.209:4000"
        self.dashboard_url = "http://34.202.215.209:8501"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }

    def test_http_endpoints(self):
        """Test all HTTP endpoints"""
        print("\n🌐 Testing HTTP Endpoints...")
        
        endpoints_8000 = [
            "/api/imperium/persistence/learning-analytics",
            "/api/health",
            "/api/imperium/growth",
            "/api/imperium/proposals",
            "/api/imperium/monitoring",
            "/api/imperium/issues",
            "/api/proposals/ai-status",
            "/api/learning/data",
            "/api/oath-papers/ai-insights",
            "/api/oath-papers/learn",
            "/api/oath-papers/categories",
        ]
        
        endpoints_4000 = [
            "/api/imperium/persistence/learning-analytics",
            "/api/health",
            "/api/imperium/growth",
            "/api/imperium/proposals",
            "/api/imperium/monitoring",
            "/api/imperium/issues",
            "/api/proposals/ai-status",
            "/api/learning/data",
            "/api/oath-papers/ai-insights",
            "/api/oath-papers/learn",
            "/api/oath-papers/categories",
        ]
        
        # Test port 8000 endpoints
        print(f"\n📡 Testing Port 8000 Endpoints:")
        for endpoint in endpoints_8000:
            url = f"{self.base_url_8000}{endpoint}"
            self._test_endpoint(url, f"8000_{endpoint.replace('/', '_')}")
        
        # Test port 4000 endpoints
        print(f"\n📡 Testing Port 4000 Endpoints:")
        for endpoint in endpoints_4000:
            url = f"{self.base_url_4000}{endpoint}"
            self._test_endpoint(url, f"4000_{endpoint.replace('/', '_')}")

    def _test_endpoint(self, url, test_name):
        """Test a single HTTP endpoint"""
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'EC2-Backend-Tester/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.status
                content_type = response.headers.get('content-type', 'unknown')
                
                if status == 200:
                    try:
                        data = response.read().decode('utf-8')
                        json_data = json.loads(data)
                        print(f"✅ {url} - Status: {status}, Type: {content_type}, Data: {len(data)} chars")
                        
                        # Special check for growth endpoint
                        if "growth" in url:
                            self._analyze_growth_data(json_data, test_name)
                            
                    except Exception as e:
                        print(f"⚠️ {url} - Status: {status}, Type: {content_type}, JSON Error: {e}")
                else:
                    print(f"❌ {url} - Status: {status}, Type: {content_type}")
                
                self.results["tests"][test_name] = {
                    "url": url,
                    "status": status,
                    "content_type": content_type,
                    "success": status == 200
                }
                
        except urllib.error.HTTPError as e:
            print(f"❌ {url} - HTTP Error: {e.code} - {e.reason}")
            self.results["tests"][test_name] = {
                "url": url,
                "status": e.code,
                "error": f"HTTP Error: {e.reason}",
                "success": False
            }
        except urllib.error.URLError as e:
            print(f"❌ {url} - URL Error: {e.reason}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": f"URL Error: {e.reason}",
                "success": False
            }
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": str(e),
                "success": False
            }

    def _analyze_growth_data(self, data, test_name):
        """Analyze growth data structure"""
        print(f"🔍 Analyzing growth data for {test_name}:")
        
        if isinstance(data, dict):
            print(f"   📊 Data is a dictionary with keys: {list(data.keys())}")
            if 'data' in data and isinstance(data['data'], list):
                print(f"   📈 Found 'data' array with {len(data['data'])} items")
                if data['data']:
                    first_item = data['data'][0]
                    print(f"   📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    if isinstance(first_item, dict) and 'start_time' not in first_item:
                        print(f"   ⚠️ WARNING: Missing 'start_time' field in growth data!")
            else:
                print(f"   ⚠️ No 'data' array found in response")
        elif isinstance(data, list):
            print(f"   📈 Data is a list with {len(data)} items")
            if data:
                first_item = data[0]
                print(f"   📋 First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                if isinstance(first_item, dict) and 'start_time' not in first_item:
                    print(f"   ⚠️ WARNING: Missing 'start_time' field in growth data!")
        else:
            print(f"   ❓ Unexpected data type: {type(data)}")

    def test_websocket_endpoints(self):
        """Test WebSocket endpoints using socket connections"""
        print("\n🔌 Testing WebSocket Endpoints...")
        
        ws_endpoints = [
            ("34.202.215.209", 8000, "/ws"),
            ("34.202.215.209", 8000, "/ws/imperium/learning-analytics"),
            ("34.202.215.209", 8000, "/api/notifications/ws"),
            ("34.202.215.209", 4000, "/ws"),
            ("34.202.215.209", 4000, "/api/notifications/ws"),
        ]
        
        for host, port, path in ws_endpoints:
            self._test_websocket_socket(host, port, path)

    def _test_websocket_socket(self, host, port, path):
        """Test WebSocket using raw socket connection"""
        test_name = f"ws_{host}_{port}_{path.replace('/', '_')}"
        url = f"ws://{host}:{port}{path}"
        
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            
            # Send HTTP upgrade request
            upgrade_request = f"""GET {path} HTTP/1.1\r
Host: {host}:{port}\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r
Sec-WebSocket-Version: 13\r
\r
"""
            sock.send(upgrade_request.encode())
            
            # Read response
            response = sock.recv(1024).decode()
            
            if "101 Switching Protocols" in response:
                print(f"✅ {url} - WebSocket upgrade successful")
                self.results["tests"][test_name] = {
                    "url": url,
                    "success": True,
                    "connected": True
                }
            else:
                print(f"❌ {url} - WebSocket upgrade failed: {response.split()[0] if response else 'No response'}")
                self.results["tests"][test_name] = {
                    "url": url,
                    "error": f"Upgrade failed: {response.split()[0] if response else 'No response'}",
                    "success": False
                }
            
            sock.close()
            
        except socket.timeout:
            print(f"❌ {url} - Connection timeout")
            self.results["tests"][test_name] = {
                "url": url,
                "error": "Connection timeout",
                "success": False
            }
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            self.results["tests"][test_name] = {
                "url": url,
                "error": str(e),
                "success": False
            }

    def test_dashboard(self):
        """Test Streamlit dashboard"""
        print("\n📊 Testing Streamlit Dashboard...")
        
        try:
            req = urllib.request.Request(self.dashboard_url)
            req.add_header('User-Agent', 'EC2-Backend-Tester/1.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    print(f"✅ Dashboard accessible at {self.dashboard_url}")
                    self.results["tests"]["dashboard"] = {
                        "url": self.dashboard_url,
                        "status": response.status,
                        "success": True
                    }
                else:
                    print(f"❌ Dashboard returned status {response.status}")
                    self.results["tests"]["dashboard"] = {
                        "url": self.dashboard_url,
                        "status": response.status,
                        "success": False
                    }
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            self.results["tests"]["dashboard"] = {
                "url": self.dashboard_url,
                "error": str(e),
                "success": False
            }

    def test_backend_services(self):
        """Test if backend services are running"""
        print("\n🔧 Testing Backend Services...")
        
        # Test if ports are open
        ports_to_test = [8000, 4000, 8501]
        
        for port in ports_to_test:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex(('34.202.215.209', port))
                sock.close()
                
                if result == 0:
                    print(f"✅ Port {port} is open and accepting connections")
                    self.results["tests"][f"port_{port}"] = {
                        "port": port,
                        "status": "open",
                        "success": True
                    }
                else:
                    print(f"❌ Port {port} is closed or not accessible")
                    self.results["tests"][f"port_{port}"] = {
                        "port": port,
                        "status": "closed",
                        "success": False
                    }
            except Exception as e:
                print(f"❌ Error testing port {port}: {e}")
                self.results["tests"][f"port_{port}"] = {
                    "port": port,
                    "error": str(e),
                    "success": False
                }

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.results["tests"])
        successful_tests = sum(1 for test in self.results["tests"].values() if test.get("success", False))
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        print(f"\n📋 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_tests - successful_tests}")
        print(f"   Success Rate: {self.results['summary']['success_rate']:.1f}%")

    def save_results(self):
        """Save test results to file"""
        filename = f"ec2_backend_test_results_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive EC2 Backend Test...")
        print(f"⏰ Test started at: {datetime.now().isoformat()}")
        
        self.test_backend_services()
        self.test_http_endpoints()
        self.test_websocket_endpoints()
        self.test_dashboard()
        
        self.generate_summary()
        self.save_results()
        
        print(f"\n✅ Test completed at: {datetime.now().isoformat()}")

def main():
    tester = SimpleEC2BackendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 