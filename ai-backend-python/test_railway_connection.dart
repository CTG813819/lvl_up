import 'dart:io';
import 'dart:convert';

void main() async {
  print('🔍 Testing Railway Backend Connection (ai-backend-python)...\n');
  
  const railwayUrl = 'https://compassionate-truth-production-2fcd.up.railway.app';
  
  // Test endpoints that should be available based on app/main.py
  final endpoints = [
    '/health',  // Basic health check
    '/api/health',  // API health check
    '/api/status',  // Status endpoint
    '/api/agents/status',  // Agents status
    '/api/database/health',  // Database health
    '/api/oath-papers/learn',  // Oath papers
    '/api/config',  // Config endpoint
    '/api/info',  // Info endpoint
    '/api/version',  // Version endpoint
  ];
  
  for (final endpoint in endpoints) {
    try {
      print('Testing: $railwayUrl$endpoint');
      
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      
      final request = await client.getUrl(Uri.parse('$railwayUrl$endpoint'));
      final response = await request.close();
      
      print('✅ Status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final body = await response.transform(utf8.decoder).join();
        try {
          final data = json.decode(body);
          print('📄 Response: ${data.toString().substring(0, 100)}...');
        } catch (e) {
          print('📄 Response: ${body.substring(0, 100)}...');
        }
      } else if (response.statusCode == 404) {
        print('⚠️ Endpoint not found (404) - server is reachable but endpoint missing');
      } else {
        print('📊 Status: ${response.statusCode}');
      }
      
      print('');
    } catch (e) {
      print('❌ Error: $e\n');
    }
  }
  
  print('🎯 Railway Backend Test Complete!');
  print('\n📋 Analysis:');
  print('• If all endpoints return 404: Railway deployment issue');
  print('• If some endpoints work: Configuration issue');
  print('• If connection errors: Railway service not running');
  print('\n🔧 Next Steps:');
  print('1. Check Railway dashboard for deployment status');
  print('2. Verify environment variables (DATABASE_URL, etc.)');
  print('3. Check Railway logs for startup errors');
  print('4. Ensure the service is running and healthy');
}
