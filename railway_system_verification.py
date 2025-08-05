#!/usr/bin/env python3
"""
Railway System Verification Script
Checks if enhanced, training, and project warmaster features are working
"""

import requests
import json
import time
from datetime import datetime
import sys

class RailwaySystemVerifier:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.results = {}
        
    def test_endpoint(self, endpoint, method="GET", data=None):
        """Test an endpoint and return results"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None,
                'error': None
            }
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def verify_enhanced_system(self):
        """Verify enhanced ML learning system"""
        print("🔍 Verifying Enhanced ML Learning System...")
        
        endpoints = [
            "/api/enhanced-learning/health",
            "/api/enhanced-learning/training-analytics",
            "/api/enhanced-learning/model-performance",
            "/api/enhanced-learning/learning-insights"
        ]
        
        enhanced_results = {}
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            enhanced_results[endpoint] = result
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {endpoint}: {result['status_code']}")
        
        self.results['enhanced_system'] = enhanced_results
        return any(r['success'] for r in enhanced_results.values())
    
    def verify_training_system(self):
        """Verify training system"""
        print("🎯 Verifying Training System...")
        
        endpoints = [
            "/api/enhanced-learning/health",
            "/api/enhanced-learning/training-analytics",
            "/api/enhanced-learning/force-retrain"
        ]
        
        training_results = {}
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            training_results[endpoint] = result
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {endpoint}: {result['status_code']}")
        
        self.results['training_system'] = training_results
        return any(r['success'] for r in training_results.values())
    
    def verify_project_warmaster(self):
        """Verify project warmaster system"""
        print("⚔️ Verifying Project Warmaster System...")
        
        endpoints = [
            "/api/project-warmaster/status",
            "/api/project-warmaster/health",
            "/api/project-warmaster/live-data"
        ]
        
        warmaster_results = {}
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            warmaster_results[endpoint] = result
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {endpoint}: {result['status_code']}")
        
        self.results['project_warmaster'] = warmaster_results
        return any(r['success'] for r in warmaster_results.values())
    
    def verify_basic_system(self):
        """Verify basic system health"""
        print("🏥 Verifying Basic System Health...")
        
        endpoints = [
            "/health",
            "/api/health",
            "/api/status"
        ]
        
        basic_results = {}
        for endpoint in endpoints:
            result = self.test_endpoint(endpoint)
            basic_results[endpoint] = result
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {endpoint}: {result['status_code']}")
        
        self.results['basic_system'] = basic_results
        return any(r['success'] for r in basic_results.values())
    
    def generate_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "="*60)
        print("📊 RAILWAY SYSTEM VERIFICATION REPORT")
        print("="*60)
        
        # Basic system status
        basic_working = self.verify_basic_system()
        print(f"\n🏥 Basic System: {'✅ WORKING' if basic_working else '❌ NOT WORKING'}")
        
        # Enhanced system status
        enhanced_working = self.verify_enhanced_system()
        print(f"🧠 Enhanced System: {'✅ WORKING' if enhanced_working else '❌ NOT WORKING'}")
        
        # Training system status
        training_working = self.verify_training_system()
        print(f"🎯 Training System: {'✅ WORKING' if training_working else '❌ NOT WORKING'}")
        
        # Project warmaster status
        warmaster_working = self.verify_project_warmaster()
        print(f"⚔️ Project Warmaster: {'✅ WORKING' if warmaster_working else '❌ NOT WORKING'}")
        
        # Overall status
        overall_working = basic_working and (enhanced_working or training_working or warmaster_working)
        print(f"\n🎯 Overall Status: {'✅ ALL SYSTEMS OPERATIONAL' if overall_working else '⚠️ PARTIAL FUNCTIONALITY'}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for system, results in self.results.items():
            print(f"\n{system.upper().replace('_', ' ')}:")
            for endpoint, result in results.items():
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {endpoint}")
                if result['data'] and isinstance(result['data'], dict):
                    if 'healthy' in result['data']:
                        print(f"    Health: {'✅' if result['data']['healthy'] else '❌'}")
                    if 'models_loaded' in result['data']:
                        print(f"    Models Loaded: {result['data']['models_loaded']}")
                    if 'scheduler_running' in result['data']:
                        print(f"    Scheduler: {'✅' if result['data']['scheduler_running'] else '❌'}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if not basic_working:
            print("  ❌ Fix basic system connectivity first")
        if not enhanced_working:
            print("  🔧 Check enhanced learning service configuration")
        if not training_working:
            print("  🔧 Verify training scheduler and ML models")
        if not warmaster_working:
            print("  🔧 Check project warmaster service status")
        
        if overall_working:
            print("  ✅ All systems are operational!")
        
        return overall_working

def main():
    if len(sys.argv) != 2:
        print("Usage: python railway_system_verification.py <railway-app-url>")
        print("Example: python railway_system_verification.py https://your-app.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1]
    print(f"🔍 Verifying Railway system at: {base_url}")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verifier = RailwaySystemVerifier(base_url)
    success = verifier.generate_report()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 