import 'dart:io';
import 'dart:convert';

void main() async {
  print('🔍 Testing Railway Port Configuration...\n');

  // Test different port configurations
  final testUrls = [
    'https://lvlup-production-1a5a.up.railway.app:8080',
    'https://lvlup-production-1a5a.up.railway.app',
    'http://lvlup-production-1a5a.up.railway.app:8080',
    'http://lvlup-production-1a5a.up.railway.app',
  ];

  for (final url in testUrls) {
    try {
      print('Testing: $url/health');

      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);

      final request = await client.getUrl(Uri.parse('$url/health'));
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
      }

      print('');
    } catch (e) {
      print('❌ Error: $e\n');
    }
  }

  print('🎯 Railway Port Analysis:');
  print('• Railway typically uses port 443 (HTTPS) or 80 (HTTP)');
  print('• Port 8080 is usually for local development');
  print('• If Railway is running on 8080, it might be misconfigured');
  print('\n📋 Next Steps:');
  print('1. Check Railway dashboard for the correct URL');
  print('2. Verify the service is deployed and running');
  print('3. Check if there are any port configuration issues');
}
