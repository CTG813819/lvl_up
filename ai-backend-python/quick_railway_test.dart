import 'dart:io';
import 'dart:convert';

void main() async {
  const railwayUrl = 'https://lvlup-production.up.railway.app';
  
  print('🔍 Quick Railway Backend Connection Test');
  print('=' * 40);
  print('Testing URL: $railwayUrl');
  print('');
  
  try {
    // Test 1: Basic connectivity
    print('1. Testing basic connectivity...');
    final client = HttpClient();
    client.connectionTimeout = const Duration(seconds: 10);
    
    final request = await client.getUrl(Uri.parse(railwayUrl));
    final response = await request.close();
    
    print('   Status Code: ${response.statusCode}');
    print('   ✅ Basic connectivity: ${response.statusCode == 200 || response.statusCode == 404 ? "SUCCESS" : "FAILED"}');
    
    // Test 2: API endpoints
    print('\n2. Testing API endpoints...');
    final endpoints = [
      '/api/learning/data',
      '/api/imperium/status',
      '/api/proposals',
      '/api/conquest/deployments',
      '/health',
      '/',
    ];
    
    for (final endpoint in endpoints) {
      try {
        final apiRequest = await client.getUrl(Uri.parse('$railwayUrl$endpoint'));
        final apiResponse = await apiRequest.close();
        
        final status = apiResponse.statusCode;
        final statusIcon = status == 200 ? '✅' : status == 404 ? '⚠️' : '❌';
        
        print('   $statusIcon $endpoint - Status: $status');
        
        if (status == 200) {
          final responseBody = await apiResponse.transform(utf8.decoder).join();
          if (responseBody.length > 100) {
            print('      📊 Response: ${responseBody.substring(0, 100)}...');
          } else {
            print('      📊 Response: $responseBody');
          }
        }
      } catch (e) {
        print('   ❌ $endpoint - Error: $e');
      }
    }
    
    // Test 3: Check if backend is running
    print('\n3. Checking backend status...');
    try {
      final healthRequest = await client.getUrl(Uri.parse('$railwayUrl/health'));
      final healthResponse = await healthRequest.close();
      
      if (healthResponse.statusCode == 200) {
        print('   ✅ Backend health check: SUCCESS');
      } else {
        print('   ⚠️ Backend health check: Status ${healthResponse.statusCode}');
      }
    } catch (e) {
      print('   ❌ Backend health check failed: $e');
    }
    
    print('\n' + '=' * 40);
    print('📊 SUMMARY');
    print('=' * 40);
    print('Railway URL: $railwayUrl');
    print('Basic Connectivity: ✅');
    print('Backend Status: Check individual endpoints above');
    
  } catch (e) {
    print('❌ Error during testing: $e');
  }
} 