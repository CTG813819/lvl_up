import 'dart:io';

class NetworkConfig {
  // Railway Backend URL (Primary) - Updated to use Railway deployment
  static const String railwayUrl = 'https://lvlup-production.up.railway.app';

  // API Endpoints
  static const String apiUrl = '$railwayUrl/api';

  // WebSocket URL for real-time updates
  static const String socketUrl = 'wss://lvlup-production.up.railway.app';

  // Working endpoint for all data - Updated to use a more reliable endpoint
  static const String workingEndpoint = '/health';

  // FIX: Improved timeout settings for better reliability
  static const Duration connectionTimeout = Duration(
    seconds: 15,
  ); // Reduced from 30
  static const Duration receiveTimeout = Duration(
    seconds: 20,
  ); // Reduced from 30

  // Retry settings
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);

  static const String apiBaseUrl = railwayUrl; // Use Railway as base URL

  // Get the appropriate backend URL based on platform and environment
  static String get backendUrl => railwayUrl; // Use Railway as primary

  // Get all possible backend URLs for testing - Railway and local options only
  static List<String> get allBackendUrls => [
    railwayUrl, // Railway production (primary)
    'http://10.0.2.2:8000', // Android emulator
    'http://localhost:8000', // Local development
    'http://127.0.0.1:8000', // Local development fallback
    'http://192.168.1.118:8000', // Local network
  ];

  // FIX: Test connectivity to all backend URLs with better error handling
  static Future<Map<String, bool>> testConnectivity() async {
    final results = <String, bool>{};

    for (final url in allBackendUrls) {
      try {
        final client = HttpClient();
        client.connectionTimeout = const Duration(
          seconds: 5,
        ); // Shorter timeout for testing
        client.idleTimeout = const Duration(seconds: 10); // Add idle timeout

        // Test the working endpoint instead of health
        final request = await client.getUrl(Uri.parse('$url$workingEndpoint'));
        final response = await request.close();

        // Consider both 200 and 404 as "reachable" (404 means server is up)
        results[url] = response.statusCode == 200 || response.statusCode == 404;

        print('[NETWORK_CONFIG] ✅ $url is reachable (${response.statusCode})');
      } catch (e) {
        results[url] = false;
        print('[NETWORK_CONFIG] ❌ $url is not reachable: $e');
      }
    }

    return results;
  }

  // Get the best available backend URL
  static Future<String> getBestBackendUrl() async {
    final connectivityResults = await testConnectivity();

    // Return the first working URL
    for (final entry in connectivityResults.entries) {
      if (entry.value) {
        print('[NETWORK_CONFIG] 🎯 Using backend: ${entry.key}');
        return entry.key;
      }
    }

    // Fallback to Railway even if it's not responding properly
    print('[NETWORK_CONFIG] ⚠️ No local backends available, using Railway');
    return railwayUrl;
  }

  // Get the working endpoint URL for any backend
  static String getWorkingEndpointUrl(String baseUrl) {
    return '$baseUrl$workingEndpoint';
  }

  // Check if we're running in development mode
  static bool get isDevelopmentMode {
    return const bool.fromEnvironment('dart.vm.product') == false;
  }

  // FIX: Get appropriate timeout based on environment with better defaults
  static Duration get requestTimeout {
    return isDevelopmentMode
        ? const Duration(seconds: 30) // Reduced from 60 for development
        : const Duration(seconds: 20); // Reduced from 30 for production
  }

  // FIX: Get timeout for specific operations with better defaults
  static Duration get timeoutForAgentsData =>
      const Duration(seconds: 20); // Reduced from 45
  static Duration get timeoutForGrowthData =>
      const Duration(seconds: 20); // Reduced from 45
  static Duration get timeoutForRecentActivity =>
      const Duration(seconds: 20); // Reduced from 45
  static Duration get timeoutForLearningInsights =>
      const Duration(seconds: 20); // Reduced from 45

  // NEW: Check if Railway backend is properly deployed
  static Future<bool> isRailwayProperlyDeployed() async {
    try {
      final client = HttpClient();
      client.connectionTimeout = const Duration(seconds: 10);

      // Test multiple endpoints to see if any work
      final testEndpoints = ['/health', '/api/health', '/api/imperium/status'];

      for (final endpoint in testEndpoints) {
        try {
          final request = await client.getUrl(
            Uri.parse('$railwayUrl$endpoint'),
          );
          final response = await request.close();

          if (response.statusCode == 200) {
            print('[NETWORK_CONFIG] ✅ Railway backend is properly deployed');
            return true;
          }
        } catch (e) {
          // Continue to next endpoint
        }
      }

      print(
        '[NETWORK_CONFIG] ⚠️ Railway backend is reachable but endpoints not working',
      );
      return false;
    } catch (e) {
      print('[NETWORK_CONFIG] ❌ Railway backend is not reachable: $e');
      return false;
    }
  }

  // NEW: Get deployment status message
  static Future<String> getDeploymentStatus() async {
    final isDeployed = await isRailwayProperlyDeployed();

    if (isDeployed) {
      return 'Railway backend is properly deployed and accessible';
    } else {
      return 'Railway backend is reachable but endpoints are not working. Check Railway deployment configuration.';
    }
  }

  // NEW: Get working endpoints for Flutter app
  static List<String> get workingEndpoints => [
    '/api/imperium/status', // ✅ Working
    '/api/learning/data', // ✅ Working
    '/health', // ✅ Working
    '/api/health', // ✅ Working
    '/api/project-horus/status', // ✅ Project Horus status
    '/api/project-horus/chaos/repository', // ✅ Chaos code repository
    '/api/project-warmaster/status', // ✅ Project Berserk status
    '/api/project-warmaster/brain-visualization', // ✅ Brain visualization data
  ];

  // NEW: Get endpoints that need attention
  static List<String> get needsAttentionEndpoints => [
    '/api/guardian/code-review/threat-detection', // ⚠️ Returns 404
  ];
}
