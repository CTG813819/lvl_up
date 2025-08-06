import 'dart:convert';
import 'package:http/http.dart' as http;

// Test script to verify Warmaster and Warp screens can connect to Railway backend
void main() async {
  print('🧪 Testing Warmaster and Warp Railway Backend Connectivity...\n');

  const railwayUrl = 'https://compassionate-truth-production-2fcd.up.railway.app';

  // Test endpoints used by Warmaster/Project Berserk screen
  final warmasterEndpoints = [
    '/api/project-warmaster/status',
    '/api/offline-chaos/status',
    '/api/offline-chaos/stealth-assimilation',
    '/api/offline-chaos/generate-chaos-code',
    '/api/offline-chaos/legion-directive/create',
    '/api/project-warmaster/build-chaos-repository',
    '/api/project-warmaster/create-self-extension',
  ];

  // Test endpoints used by Warp screen
  final warpEndpoints = [
    '/api/agent-metrics/leaderboard',
    '/custody/recent-tests',
    '/api/adversarial/recent-scenarios',
    '/api/adversarial/health',
    '/api/adversarial/generate-and-execute',
    '/api/adversarial/activate',
  ];

  print('🔍 Testing Warmaster/Project Berserk endpoints:');
  for (final endpoint in warmasterEndpoints) {
    await testEndpoint('$railwayUrl$endpoint', 'Warmaster');
  }

  print('\n🔍 Testing Warp/Enhanced Adversarial endpoints:');
  for (final endpoint in warpEndpoints) {
    await testEndpoint('$railwayUrl$endpoint', 'Warp');
  }

  print('\n✅ Warmaster and Warp Railway connectivity test completed!');
}

Future<void> testEndpoint(String url, String screen) async {
  try {
    print('  Testing: $url');

    final response = await http
        .get(Uri.parse(url), headers: {'Content-Type': 'application/json'})
        .timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      print('    ✅ $screen: $url - Status: ${response.statusCode}');
    } else if (response.statusCode == 404) {
      print(
        '    ⚠️ $screen: $url - Status: ${response.statusCode} (Endpoint not found)',
      );
    } else {
      print('    ❌ $screen: $url - Status: ${response.statusCode}');
    }
  } catch (e) {
    print('    ❌ $screen: $url - Error: $e');
  }
}
