import requests
import time
import json
import socket
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComprehensiveSystemTest:
    def __init__(self):
        self.backend_ip = '34.202.215.209'
        self.ports = [4000, 8000]
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': 0,
            'tests': {},
            'recommendations': [],
            'errors': []
        }
        
        # All endpoints to test
        self.endpoints = {
            'imperium': [
                '/api/imperium/agents',
                '/api/imperium/status', 
                '/api/imperium/dashboard',
                '/api/imperium/trusted-sources',
                '/api/imperium/internet-learning/topics',
                '/api/imperium/persistence/learning-analytics',
                '/api/imperium/growth',
                '/api/imperium/proposals',
                '/api/imperium/monitoring',
                '/api/imperium/issues',
                '/api/imperium/health',
            ],
            'core': [
                '/api/health',
                '/api/status',
                '/api/config',
                '/api/info',
                '/api/version',
            ],
            'learning': [
                '/api/learning/data',
                '/api/learning/metrics',
                '/api/learning/status',
                '/api/learning/insights',
            ],
            'proposals': [
                '/api/proposals',
                '/api/proposals/ai-status',
                '/api/proposals/status',
            ],
            'oath_papers': [
                '/api/oath-papers',
                '/api/oath-papers/ai-insights',
                '/api/oath-papers/learn',
                '/api/oath-papers/categories',
            ],
            'conquest': [
                '/api/conquest/build-failure',
                '/api/conquest/status',
                '/api/conquest/analytics',
            ],
            'websocket': [
                '/ws',
                '/ws/imperium/learning-analytics',
                '/api/notifications/ws',
                '/socket.io/',
            ]
        }

    def test_port_connectivity(self):
        """Test if ports are open and accessible"""
        print("🔌 Testing port connectivity...")
        port_results = {}
        
        for port in self.ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((self.backend_ip, port))
                sock.close()
                
                if result == 0:
                    port_results[port] = {'status': 'open', 'score': 100}
                    print(f"  ✅ Port {port} is open")
                else:
                    port_results[port] = {'status': 'closed', 'score': 0}
                    print(f"  ❌ Port {port} is closed")
            except Exception as e:
                port_results[port] = {'status': 'error', 'score': 0, 'error': str(e)}
                print(f"  ❌ Port {port} error: {e}")
        
        self.results['tests']['port_connectivity'] = port_results
        return port_results

    def test_http_endpoints(self, port):
        """Test all HTTP endpoints on a specific port"""
        print(f"\n🌐 Testing HTTP endpoints on port {port}...")
        endpoint_results = {}
        total_tests = 0
        successful_tests = 0
        
        for category, endpoints in self.endpoints.items():
            if category == 'websocket':
                continue  # Skip WebSocket endpoints for HTTP test
                
            category_results = {}
            for endpoint in endpoints:
                total_tests += 1
                url = f'http://{self.backend_ip}:{port}{endpoint}'
                
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        successful_tests += 1
                        category_results[endpoint] = {
                            'status': 'success',
                            'score': 100,
                            'response_time': round(response_time, 3),
                            'data_size': len(response.text),
                            'content_type': response.headers.get('content-type', 'unknown')
                        }
                        print(f"  ✅ {endpoint} [200] - {response_time:.3f}s")
                    else:
                        category_results[endpoint] = {
                            'status': 'failed',
                            'score': 0,
                            'status_code': response.status_code,
                            'response_time': round(response_time, 3)
                        }
                        print(f"  ❌ {endpoint} [{response.status_code}]")
                        
                except Exception as e:
                    category_results[endpoint] = {
                        'status': 'error',
                        'score': 0,
                        'error': str(e)
                    }
                    print(f"  ❌ {endpoint} [error: {e}]")
            
            endpoint_results[category] = category_results
        
        # Calculate overall score for this port
        port_score = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        endpoint_results['overall_score'] = round(port_score, 2)
        
        return endpoint_results

    def test_websocket_endpoints(self, port):
        """Test WebSocket endpoints"""
        print(f"\n🔌 Testing WebSocket endpoints on port {port}...")
        ws_results = {}
        successful_tests = 0
        total_tests = len(self.endpoints['websocket'])
        
        try:
            import websocket
            for endpoint in self.endpoints['websocket']:
                ws_url = f'ws://{self.backend_ip}:{port}{endpoint}'
                
                try:
                    start_time = time.time()
                    ws = websocket.create_connection(ws_url, timeout=5)
                    response_time = time.time() - start_time
                    ws.close()
                    
                    ws_results[endpoint] = {
                        'status': 'success',
                        'score': 100,
                        'response_time': round(response_time, 3)
                    }
                    successful_tests += 1
                    print(f"  ✅ {endpoint} [WebSocket OK] - {response_time:.3f}s")
                    
                except Exception as e:
                    ws_results[endpoint] = {
                        'status': 'failed',
                        'score': 0,
                        'error': str(e)
                    }
                    print(f"  ❌ {endpoint} [WebSocket error: {e}]")
                    
        except ImportError:
            print("  ⚠️ websocket-client not installed, skipping WebSocket tests")
            for endpoint in self.endpoints['websocket']:
                ws_results[endpoint] = {
                    'status': 'skipped',
                    'score': 0,
                    'error': 'websocket-client not installed'
                }
        
        ws_results['overall_score'] = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        return ws_results

    def test_ai_systems(self, port):
        """Test AI-specific systems and data"""
        print(f"\n🤖 Testing AI systems on port {port}...")
        ai_results = {}
        
        # Test AI agents
        try:
            response = requests.get(f'http://{self.backend_ip}:{port}/api/imperium/agents', timeout=5)
            if response.status_code == 200:
                data = response.json()
                ai_results['agents'] = {
                    'status': 'success',
                    'score': 100,
                    'agent_count': len(data.get('agents', [])),
                    'data_keys': list(data.keys())
                }
                print(f"  ✅ AI Agents: {len(data.get('agents', []))} agents found")
            else:
                ai_results['agents'] = {'status': 'failed', 'score': 0, 'status_code': response.status_code}
                print(f"  ❌ AI Agents: HTTP {response.status_code}")
        except Exception as e:
            ai_results['agents'] = {'status': 'error', 'score': 0, 'error': str(e)}
            print(f"  ❌ AI Agents: {e}")
        
        # Test learning analytics
        try:
            response = requests.get(f'http://{self.backend_ip}:{port}/api/imperium/persistence/learning-analytics', timeout=5)
            if response.status_code == 200:
                data = response.json()
                ai_results['learning_analytics'] = {
                    'status': 'success',
                    'score': 100,
                    'data_keys': list(data.keys()),
                    'data_size': len(str(data))
                }
                print(f"  ✅ Learning Analytics: {len(data.keys())} data keys")
            else:
                ai_results['learning_analytics'] = {'status': 'failed', 'score': 0, 'status_code': response.status_code}
                print(f"  ❌ Learning Analytics: HTTP {response.status_code}")
        except Exception as e:
            ai_results['learning_analytics'] = {'status': 'error', 'score': 0, 'error': str(e)}
            print(f"  ❌ Learning Analytics: {e}")
        
        # Test dashboard
        try:
            response = requests.get(f'http://{self.backend_ip}:{port}/api/imperium/dashboard', timeout=5)
            if response.status_code == 200:
                data = response.json()
                ai_results['dashboard'] = {
                    'status': 'success',
                    'score': 100,
                    'data_keys': list(data.keys()),
                    'has_metrics': 'metrics' in str(data).lower()
                }
                print(f"  ✅ Dashboard: {len(data.keys())} data keys")
            else:
                ai_results['dashboard'] = {'status': 'failed', 'score': 0, 'status_code': response.status_code}
                print(f"  ❌ Dashboard: HTTP {response.status_code}")
        except Exception as e:
            ai_results['dashboard'] = {'status': 'error', 'score': 0, 'error': str(e)}
            print(f"  ❌ Dashboard: {e}")
        
        # Calculate AI systems score
        scores = [result['score'] for result in ai_results.values()]
        ai_results['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        return ai_results

    def test_data_quality(self, port):
        """Test data quality and consistency"""
        print(f"\n📊 Testing data quality on port {port}...")
        data_results = {}
        
        # Test data consistency across endpoints
        endpoints_to_test = [
            '/api/imperium/agents',
            '/api/imperium/status',
            '/api/imperium/dashboard'
        ]
        
        data_samples = {}
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f'http://{self.backend_ip}:{port}{endpoint}', timeout=5)
                if response.status_code == 200:
                    data_samples[endpoint] = response.json()
            except:
                pass
        
        # Check for common data patterns
        if data_samples:
            # Check for timestamp consistency
            timestamps = []
            for data in data_samples.values():
                if isinstance(data, dict) and 'timestamp' in data:
                    timestamps.append(data['timestamp'])
            
            if timestamps:
                data_results['timestamp_consistency'] = {
                    'status': 'success',
                    'score': 100,
                    'timestamp_count': len(timestamps)
                }
                print(f"  ✅ Timestamp consistency: {len(timestamps)} timestamps found")
            else:
                data_results['timestamp_consistency'] = {'status': 'warning', 'score': 50, 'note': 'No timestamps found'}
                print(f"  ⚠️ Timestamp consistency: No timestamps found")
            
            # Check data structure
            data_results['structure_quality'] = {
                'status': 'success',
                'score': 100,
                'endpoints_tested': len(data_samples)
            }
            print(f"  ✅ Data structure quality: {len(data_samples)} endpoints tested")
        else:
            data_results['structure_quality'] = {'status': 'failed', 'score': 0, 'note': 'No data retrieved'}
            print(f"  ❌ Data structure quality: No data retrieved")
        
        # Calculate data quality score
        scores = [result['score'] for result in data_results.values()]
        data_results['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        return data_results

    def test_performance(self, port):
        """Test performance metrics"""
        print(f"\n⚡ Testing performance on port {port}...")
        perf_results = {}
        
        # Test response times for key endpoints
        key_endpoints = [
            '/api/imperium/agents',
            '/api/imperium/status',
            '/api/imperium/dashboard'
        ]
        
        response_times = []
        for endpoint in key_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f'http://{self.backend_ip}:{port}{endpoint}', timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    print(f"  ✅ {endpoint}: {response_time:.3f}s")
                else:
                    print(f"  ❌ {endpoint}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {endpoint}: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Score based on response time (faster = better)
            if avg_time < 0.5:
                score = 100
            elif avg_time < 1.0:
                score = 80
            elif avg_time < 2.0:
                score = 60
            else:
                score = 40
            
            perf_results['response_times'] = {
                'status': 'success',
                'score': score,
                'average_time': round(avg_time, 3),
                'max_time': round(max_time, 3),
                'min_time': round(min_time, 3),
                'endpoints_tested': len(response_times)
            }
        else:
            perf_results['response_times'] = {'status': 'failed', 'score': 0, 'note': 'No successful responses'}
        
        # Calculate performance score
        scores = [result['score'] for result in perf_results.values()]
        perf_results['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        return perf_results

    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check port connectivity
        port_results = self.results['tests'].get('port_connectivity', {})
        for port, result in port_results.items():
            if result['status'] != 'open':
                recommendations.append(f"🔌 Fix port {port} connectivity - currently {result['status']}")
        
        # Check endpoint availability
        for port in self.ports:
            if port in self.results['tests'].get('http_endpoints', {}):
                endpoint_results = self.results['tests']['http_endpoints'][port]
                overall_score = endpoint_results.get('overall_score', 0)
                if overall_score < 50:
                    recommendations.append(f"🌐 Improve endpoint availability on port {port} - score: {overall_score}%")
        
        # Check WebSocket support
        for port in self.ports:
            if port in self.results['tests'].get('websocket_endpoints', {}):
                ws_results = self.results['tests']['websocket_endpoints'][port]
                overall_score = ws_results.get('overall_score', 0)
                if overall_score < 50:
                    recommendations.append(f"🔌 Enable WebSocket support on port {port} - score: {overall_score}%")
        
        # Check AI systems
        for port in self.ports:
            if port in self.results['tests'].get('ai_systems', {}):
                ai_results = self.results['tests']['ai_systems'][port]
                overall_score = ai_results.get('overall_score', 0)
                if overall_score < 80:
                    recommendations.append(f"🤖 Improve AI systems on port {port} - score: {overall_score}%")
        
        # Check data quality
        for port in self.ports:
            if port in self.results['tests'].get('data_quality', {}):
                data_results = self.results['tests']['data_quality'][port]
                overall_score = data_results.get('overall_score', 0)
                if overall_score < 80:
                    recommendations.append(f"📊 Improve data quality on port {port} - score: {overall_score}%")
        
        # Check performance
        for port in self.ports:
            if port in self.results['tests'].get('performance', {}):
                perf_results = self.results['tests']['performance'][port]
                overall_score = perf_results.get('overall_score', 0)
                if overall_score < 70:
                    recommendations.append(f"⚡ Optimize performance on port {port} - score: {overall_score}%")
        
        return recommendations

    def calculate_overall_score(self):
        """Calculate overall system score"""
        all_scores = []
        
        for test_category, test_results in self.results['tests'].items():
            if isinstance(test_results, dict):
                for port, results in test_results.items():
                    if isinstance(results, dict) and 'overall_score' in results:
                        all_scores.append(results['overall_score'])
                    elif isinstance(results, dict) and 'score' in results:
                        all_scores.append(results['score'])
        
        if all_scores:
            self.results['overall_score'] = sum(all_scores) / len(all_scores)
        else:
            self.results['overall_score'] = 0

    def run_all_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive System Test...")
        print("=" * 60)
        
        # Test port connectivity
        self.results['tests']['port_connectivity'] = self.test_port_connectivity()
        
        # Test each port
        for port in self.ports:
            if self.results['tests']['port_connectivity'].get(port, {}).get('status') == 'open':
                print(f"\n🔧 Testing port {port}...")
                
                # HTTP endpoints
                self.results['tests']['http_endpoints'] = self.results['tests'].get('http_endpoints', {})
                self.results['tests']['http_endpoints'][port] = self.test_http_endpoints(port)
                
                # WebSocket endpoints
                self.results['tests']['websocket_endpoints'] = self.results['tests'].get('websocket_endpoints', {})
                self.results['tests']['websocket_endpoints'][port] = self.test_websocket_endpoints(port)
                
                # AI systems
                self.results['tests']['ai_systems'] = self.results['tests'].get('ai_systems', {})
                self.results['tests']['ai_systems'][port] = self.test_ai_systems(port)
                
                # Data quality
                self.results['tests']['data_quality'] = self.results['tests'].get('data_quality', {})
                self.results['tests']['data_quality'][port] = self.test_data_quality(port)
                
                # Performance
                self.results['tests']['performance'] = self.results['tests'].get('performance', {})
                self.results['tests']['performance'][port] = self.test_performance(port)
        
        # Generate recommendations
        self.results['recommendations'] = self.generate_recommendations()
        
        # Calculate overall score
        self.calculate_overall_score()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return self.results

    def print_summary(self):
        """Print a comprehensive summary"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        overall_score = self.results['overall_score']
        print(f"📊 Overall System Score: {overall_score:.1f}%")
        
        if overall_score >= 90:
            print("🏆 Status: EXCELLENT - System is performing optimally")
        elif overall_score >= 80:
            print("✅ Status: GOOD - System is working well with minor issues")
        elif overall_score >= 70:
            print("⚠️ Status: FAIR - System has some issues that need attention")
        elif overall_score >= 50:
            print("❌ Status: POOR - System has significant issues")
        else:
            print("🚨 Status: CRITICAL - System has major issues requiring immediate attention")
        
        print(f"\n📅 Test completed: {self.results['timestamp']}")
        
        # Port summary
        print(f"\n🔌 Port Status:")
        for port, result in self.results['tests'].get('port_connectivity', {}).items():
            status_emoji = "✅" if result['status'] == 'open' else "❌"
            print(f"  {status_emoji} Port {port}: {result['status']}")
        
        # Endpoint summary
        print(f"\n🌐 Endpoint Summary:")
        for port in self.ports:
            if port in self.results['tests'].get('http_endpoints', {}):
                score = self.results['tests']['http_endpoints'][port].get('overall_score', 0)
                print(f"  📡 Port {port} HTTP endpoints: {score:.1f}%")
        
        # WebSocket summary
        print(f"\n🔌 WebSocket Summary:")
        for port in self.ports:
            if port in self.results['tests'].get('websocket_endpoints', {}):
                score = self.results['tests']['websocket_endpoints'][port].get('overall_score', 0)
                print(f"  🔌 Port {port} WebSocket: {score:.1f}%")
        
        # AI systems summary
        print(f"\n🤖 AI Systems Summary:")
        for port in self.ports:
            if port in self.results['tests'].get('ai_systems', {}):
                score = self.results['tests']['ai_systems'][port].get('overall_score', 0)
                print(f"  🧠 Port {port} AI systems: {score:.1f}%")
        
        # Performance summary
        print(f"\n⚡ Performance Summary:")
        for port in self.ports:
            if port in self.results['tests'].get('performance', {}):
                score = self.results['tests']['performance'][port].get('overall_score', 0)
                print(f"  ⚡ Port {port} performance: {score:.1f}%")
        
        # Recommendations
        if self.results['recommendations']:
            print(f"\n🔧 Recommendations:")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")
        else:
            print(f"\n✅ No recommendations - system is performing well!")
        
        print(f"\n📄 Detailed results saved to: comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

def main():
    tester = ComprehensiveSystemTest()
    results = tester.run_all_tests()
    tester.print_summary()

if __name__ == '__main__':
    main() 