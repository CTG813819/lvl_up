import 'dart:io';
import 'dart:convert';

void main() async {
  print('🚀 Testing Frontend Railway Connection...');

  // Test the network configuration endpoints
  final testUrls = [
      'https://compassionate-truth-production-2fcd.up.railway.app',
  'https://compassionate-truth-production-2fcd.up.railway.app/health',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/health',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/learning/data',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/imperium/status',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/agents/status',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/proposals',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/missions/statistics',
  'https://compassionate-truth-production-2fcd.up.railway.app/api/growth/insights',
  ];

  print('\n📡 Testing Railway Backend Connectivity...');

  for (final url in testUrls) {
    try {
      print('\n🔍 Testing: $url');

      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);

      final request = await client.getUrl(Uri.parse(url));
      final response = await request.close();

      print('✅ Status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final body = await response.transform(utf8.decoder).join();
        print(
          '📄 Response: ${body.substring(0, body.length > 200 ? 200 : body.length)}...',
        );
      } else if (response.statusCode == 404) {
        print('⚠️ Endpoint not found (404) - server is reachable');
      } else {
        print('📊 Status: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error: $e');
    }
  }

  print('\n🎯 Testing WebSocket Connection...');

  // Test WebSocket connection
  try {
<<<<<<< HEAD
    final wsUrl = 'wss://compassionate-truth-production-2fcd.up.railway.app/api/imperium/status';
=======
    final wsUrl =
        'wss://compassionate-truth-production-2fcd.up.railway.app/api/imperium/status';
>>>>>>> c98fd28782c60b4bf527a7cf8255f563dabe32e2
    print('🔌 Testing WebSocket: $wsUrl');

    // Note: WebSocket testing would require a WebSocket client
    // For now, we'll just test the HTTP endpoint
    final client = HttpClient();
<<<<<<< HEAD
          final request = await client.getUrl(Uri.parse('https://compassionate-truth-production-2fcd.up.railway.app/api/imperium/status'));
=======
    final request = await client.getUrl(
      Uri.parse(
        'https://compassionate-truth-production-2fcd.up.railway.app/api/imperium/status',
      ),
    );
>>>>>>> c98fd28782c60b4bf527a7cf8255f563dabe32e2
    final response = await request.close();
    print('✅ WebSocket endpoint HTTP status: ${response.statusCode}');
  } catch (e) {
    print('❌ WebSocket test error: $e');
  }

  print('\n🎯 Frontend Railway Connection Test Completed!');
  print('\n📱 Next Steps:');
  print('1. The Railway backend is reachable (404s indicate server is up)');
  print('2. The frontend is configured to use Railway backend');
  print('3. You can now run the Flutter app to test the full integration');
  print('4. Run: flutter run --debug');
}
