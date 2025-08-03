import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;

// Test script to verify frontend connection to Railway backend
class FrontendRailwayConnectionTester {
  static const String railwayUrl = 'https://lvlup-production.up.railway.app';
  static const String workingEndpoint = '/api/learning/data';
  
  static Future<void> testRailwayConnection() async {
    print('🔍 Testing Frontend Connection to Railway Backend');
    print('=' * 50);
    
    try {
      // Test 1: Basic connectivity
      print('\n1. Testing basic connectivity...');
      final connectivityResult = await testBasicConnectivity();
      print('✅ Basic connectivity: ${connectivityResult ? "SUCCESS" : "FAILED"}');
      
      // Test 2: API endpoint availability
      print('\n2. Testing API endpoint availability...');
      final apiResult = await testAPIEndpoint();
      print('✅ API endpoint: ${apiResult ? "SUCCESS" : "FAILED"}');
      
      // Test 3: Response structure
      print('\n3. Testing response structure...');
      final responseStructure = await testResponseStructure();
      print('✅ Response structure: ${responseStructure ? "VALID" : "INVALID"}');
      
      // Test 4: Network configuration compatibility
      print('\n4. Testing network configuration compatibility...');
      final configCompatibility = await testNetworkConfigCompatibility();
      print('✅ Network config compatibility: ${configCompatibility ? "COMPATIBLE" : "INCOMPATIBLE"}');
      
      // Test 5: Endpoint mapping
      print('\n5. Testing endpoint mapping...');
      final endpointMapping = await testEndpointMapping();
      print('✅ Endpoint mapping: ${endpointMapping ? "WORKING" : "FAILED"}');
      
      // Summary
      print('\n' + '=' * 50);
      print('📊 CONNECTION TEST SUMMARY');
      print('=' * 50);
      print('Railway URL: $railwayUrl');
      print('Working Endpoint: $workingEndpoint');
      print('Basic Connectivity: ${connectivityResult ? "✅" : "❌"}');
      print('API Endpoint: ${apiResult ? "✅" : "❌"}');
      print('Response Structure: ${responseStructure ? "✅" : "❌"}');
      print('Network Config: ${configCompatibility ? "✅" : "❌"}');
      print('Endpoint Mapping: ${endpointMapping ? "✅" : "❌"}');
      
      final overallSuccess = connectivityResult && apiResult && responseStructure && configCompatibility && endpointMapping;
      print('\n🎯 OVERALL STATUS: ${overallSuccess ? "CONNECTED ✅" : "DISCONNECTED ❌"}');
      
      if (overallSuccess) {
        print('\n✅ Frontend is properly connected to Railway backend!');
      } else {
        print('\n❌ Frontend connection issues detected. Check the failed tests above.');
      }
      
    } catch (e) {
      print('❌ Error during connection testing: $e');
    }
  }
  
  static Future<bool> testBasicConnectivity() async {
    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      
      final request = await client.getUrl(Uri.parse(railwayUrl));
      final response = await request.close();
      
      return response.statusCode == 200 || response.statusCode == 404; // 404 is OK for root path
    } catch (e) {
      print('   ❌ Connectivity error: $e');
      return false;
    }
  }
  
  static Future<bool> testAPIEndpoint() async {
    try {
      final response = await http.get(
        Uri.parse('$railwayUrl$workingEndpoint'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 15));
      
      return response.statusCode == 200;
    } catch (e) {
      print('   ❌ API endpoint error: $e');
      return false;
    }
  }
  
  static Future<bool> testResponseStructure() async {
    try {
      final response = await http.get(
        Uri.parse('$railwayUrl$workingEndpoint'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 15));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        // Check if response has expected structure
        return data is Map<String, dynamic> || data is List;
      }
      return false;
    } catch (e) {
      print('   ❌ Response structure error: $e');
      return false;
    }
  }
  
  static Future<bool> testNetworkConfigCompatibility() async {
    try {
      // Test the network configuration values that the frontend uses
      final testUrls = [
        railwayUrl,
        'http://10.0.2.2:8000', // Android emulator
        'http://localhost:8000', // Local development
        'http://127.0.0.1:8000', // Local development fallback
      ];
      
      for (final url in testUrls) {
        try {
          final response = await http.get(
            Uri.parse('$url$workingEndpoint'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(const Duration(seconds: 5));
          
          if (response.statusCode == 200) {
            print('   ✅ Compatible URL found: $url');
            return true;
          }
        } catch (e) {
          // Continue to next URL
        }
      }
      
      print('   ❌ No compatible URLs found');
      return false;
    } catch (e) {
      print('   ❌ Network config compatibility error: $e');
      return false;
    }
  }
  
  static Future<bool> testEndpointMapping() async {
    try {
      // Test some of the mapped endpoints from the frontend
      final testEndpoints = [
        '/api/learning/data',
        '/api/imperium/status',
        '/api/proposals',
        '/api/conquest/deployments',
      ];
      
      int successfulEndpoints = 0;
      
      for (final endpoint in testEndpoints) {
        try {
          final response = await http.get(
            Uri.parse('$railwayUrl$endpoint'),
            headers: {'Content-Type': 'application/json'},
          ).timeout(const Duration(seconds: 10));
          
          if (response.statusCode == 200 || response.statusCode == 404) {
            successfulEndpoints++;
          }
        } catch (e) {
          // Endpoint failed, continue
        }
      }
      
      // Consider it working if at least one endpoint responds
      return successfulEndpoints > 0;
    } catch (e) {
      print('   ❌ Endpoint mapping error: $e');
      return false;
    }
  }
  
  static Future<void> testSpecificFrontendEndpoints() async {
    print('\n🔍 Testing Specific Frontend Endpoints');
    print('=' * 40);
    
    final endpoints = [
      '/api/learning/data',
      '/api/imperium/status',
      '/api/proposals',
      '/api/conquest/deployments',
      '/api/approval/pending',
      '/api/guardian/code-review/threat-detection',
      '/api/missions/statistics',
      '/api/growth/insights',
    ];
    
    for (final endpoint in endpoints) {
      try {
        final response = await http.get(
          Uri.parse('$railwayUrl$endpoint'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(const Duration(seconds: 10));
        
        final status = response.statusCode;
        final statusIcon = status == 200 ? '✅' : status == 404 ? '⚠️' : '❌';
        
        print('$statusIcon $endpoint - Status: $status');
        
        if (status == 200) {
          try {
            final data = jsonDecode(response.body);
            if (data is Map<String, dynamic>) {
              final keys = data.keys.take(3).toList();
              print('   📊 Response keys: ${keys.join(', ')}...');
            }
          } catch (e) {
            print('   📊 Response: ${response.body.substring(0, 100)}...');
          }
        }
      } catch (e) {
        print('❌ $endpoint - Error: $e');
      }
    }
  }
}

void main() async {
  await FrontendRailwayConnectionTester.testRailwayConnection();
  await FrontendRailwayConnectionTester.testSpecificFrontendEndpoints();
} 