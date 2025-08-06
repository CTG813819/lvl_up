import 'dart:io';
import 'dart:convert';

void main() async {
  print('🔍 Testing Flutter -> Railway Connection...\n');

  const railwayUrl = 'https://compassionate-truth-production-2fcd.up.railway.app';

  // Test the exact endpoints your Flutter app uses
  final flutterEndpoints = [
    '/api/imperium/status', // From audit_results_screen.dart
    '/api/guardian/code-review/threat-detection', // From audit_results_screen.dart
    '/api/learning/data', // From audit_results_screen.dart
    '/health', // Basic health check
    '/api/health', // API health check
  ];

  int workingEndpoints = 0;

  for (final endpoint in flutterEndpoints) {
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
          print('📄 Response: ${data.toString().substring(0, 100)}...');
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

  print('🎯 Connection Test Results:');
  print('• Working endpoints: $workingEndpoints/${flutterEndpoints.length}');

  if (workingEndpoints == flutterEndpoints.length) {
    print(
      '\n✅ Railway backend is working! Your Flutter app should connect automatically.',
    );
    print('\n📱 To test your Flutter app:');
    print('1. Run: flutter run');
    print('2. Navigate to the Audit Results screen');
    print('3. The app should fetch data from Railway automatically');
  } else if (workingEndpoints > 0) {
    print('\n⚠️ Railway backend is partially working.');
    print('Some endpoints work, but others need fixing.');
  } else {
    print('\n❌ Railway backend is not working yet.');
    print('You need to fix the Railway deployment first.');
    print('\n🔧 Next steps:');
    print('1. Go to Railway dashboard');
    print('2. Check deployment logs for errors');
    print('3. Force a redeploy');
    print('4. Verify DATABASE_URL environment variable is set');
  }
}
