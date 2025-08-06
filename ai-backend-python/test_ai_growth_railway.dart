import 'dart:io';
import 'dart:convert';

void main() async {
  print('🔍 Testing AI Growth Analytics -> Railway Connection...\n');
  
  const railwayUrl = 'https://compassionate-truth-production-2fcd.up.railway.app';
  
  // Test the endpoints that AI Growth Analytics Provider uses
  final aiGrowthEndpoints = [
    '/api/imperium/dashboard',  // AI status endpoint
    '/api/imperium/agents',     // Agents data endpoint
    '/api/learning/data',       // Learning data endpoint
    '/api/learning/metrics',    // Learning metrics endpoint
  ];
  
  int workingEndpoints = 0;
  
  for (final endpoint in aiGrowthEndpoints) {
    try {
      print('Testing: $railwayUrl$endpoint');
      
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);
      
      final request = await client.getUrl(Uri.parse('$railwayUrl$endpoint'));
      final response = await request.close();
      
      if (response.statusCode == 200) {
        workingEndpoints++;
        final body = await response.transform(utf8.decoder).join();
        try {
          final data = json.decode(body);
          print('✅ ${endpoint}: ${response.statusCode}');
          print('📄 Response keys: ${data.keys.toList()}');
        } catch (e) {
          print('✅ ${endpoint}: ${response.statusCode}');
          print('📄 Response: ${body.substring(0, 100)}...');
        }
      } else {
        print('⚠️ ${endpoint}: ${response.statusCode}');
      }
      
      print('');
    } catch (e) {
      print('❌ ${endpoint}: Error - $e\n');
    }
  }
  
  print('🎯 AI Growth Analytics Connection Test Results:');
  print('• Working endpoints: $workingEndpoints/${aiGrowthEndpoints.length}');
  
  if (workingEndpoints == aiGrowthEndpoints.length) {
    print('\n✅ All AI Growth Analytics endpoints are working!');
    print('The AI Dashboard should now display data from Railway.');
  } else if (workingEndpoints > 0) {
    print('\n⚠️ Some AI Growth Analytics endpoints are working.');
    print('The AI Dashboard may show partial data.');
  } else {
    print('\n❌ No AI Growth Analytics endpoints are working.');
    print('Check Railway deployment and endpoint configuration.');
  }
  
  print('\n📱 To test the AI Dashboard:');
  print('1. Run: flutter run');
  print('2. Navigate to AI Growth Analytics screen');
  print('3. Check if data is loading from Railway');
} 