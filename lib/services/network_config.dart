import 'dart:io';

class NetworkConfig {
  // Railway Backend URL (Primary)
  static const String railwayUrl =
      'https://ai-backend-railway-production.up.railway.app';

  // AWS EC2 Backend URL - Updated to use port 8000 (where backend is actually running)
  static const String baseUrl = 'http://34.202.215.209:8000';

  // API Endpoints
  static const String apiUrl = '$baseUrl/api';

  // WebSocket URL for real-time updates - Now working on port 8000
  static const String socketUrl = 'ws://34.202.215.209:8000';

  // Working endpoint for all data
  static const String workingEndpoint = '/api/learning/data';

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

  static const String apiBaseUrl =
      'http://34.202.215.209:8000'; // <-- Set your backend base URL here

  // Get the appropriate backend URL based on platform and environment
  static String get backendUrl => railwayUrl; // Use Railway as primary

  // Get all possible backend URLs for testing - Enhanced with Railway and local options
  static List<String> get allBackendUrls => [
    railwayUrl, // Railway production (primary)
    baseUrl, // AWS production (port 8000) - fallback
    'http://34.202.215.209:8000', // AWS fallback (port 8000)
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
        results[url] = response.statusCode == 200;

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

    // Fallback to local development
    print('[NETWORK_CONFIG] ⚠️ No remote backends available, using localhost');
    return 'http://localhost:8000';
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
}
