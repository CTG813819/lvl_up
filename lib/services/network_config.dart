import 'dart:io';
import 'package:flutter/foundation.dart';

class NetworkConfig {
  // AWS EC2 Backend URL
  static const String baseUrl = 'http://44.204.184.21:4000';
  
  // Local Development URL (uncomment for local testing)
  // static const String baseUrl = 'http://localhost:4000';
  
  // API Endpoints
  static const String apiUrl = '$baseUrl/api';
  
  // Socket.IO URL for real-time updates
  static const String socketUrl = 'http://44.204.184.21:4000';
  
  // Timeout settings
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Retry settings
  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);
  
  /// Get the appropriate backend URL based on platform and environment
  static String get backendUrl {
    if (kIsWeb) {
      // Web platform - use AWS
      return baseUrl;
    } else if (Platform.isAndroid) {
      // Android platform - check if running on emulator
      if (_isEmulator()) {
        return 'http://10.0.2.2:4000'; // Android emulator
      } else {
        // Physical device - use AWS
        return baseUrl;
      }
    } else if (Platform.isIOS) {
      // iOS platform - use localhost for simulator, AWS for device
      if (_isSimulator()) {
        return 'http://localhost:4000'; // iOS simulator
      } else {
        return baseUrl; // Physical iOS device
      }
    }
    
    // Default fallback to AWS
    return baseUrl;
  }
  
  /// Check if running on Android emulator
  static bool _isEmulator() {
    try {
      // Check for common emulator indicators
      final androidId = Platform.environment['ANDROID_ID'];
      final buildFingerprint = Platform.environment['BUILD_FINGERPRINT'];
      
      if (androidId != null && androidId.contains('generic')) {
        return true;
      }
      
      if (buildFingerprint != null && 
          (buildFingerprint.contains('generic') || 
           buildFingerprint.contains('sdk') ||
           buildFingerprint.contains('emulator'))) {
        return true;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }
  
  /// Check if running on iOS simulator
  static bool _isSimulator() {
    try {
      // Check for iOS simulator indicators
      final deviceName = Platform.environment['SIMULATOR_DEVICE_NAME'];
      return deviceName != null;
    } catch (e) {
      return false;
    }
  }
  
  /// Get all possible backend URLs for testing
  static List<String> get allBackendUrls => [
    baseUrl, // AWS
    'http://localhost:4000', // Local development
    'http://10.0.2.2:4000', // Android emulator
    'http://192.168.1.118:4000', // Local network
  ];
  
  /// Test connectivity to all backend URLs
  static Future<Map<String, bool>> testConnectivity() async {
    final results = <String, bool>{};
    
    for (final url in allBackendUrls) {
      try {
        final client = HttpClient();
        final request = await client.getUrl(Uri.parse('$url/api/health'));
        final response = await request.close();
        results[url] = response.statusCode == 200;
      } catch (e) {
        results[url] = false;
      }
    }
    
    return results;
  }
  
  /// Get the best available backend URL
  static Future<String> getBestBackendUrl() async {
    final connectivityResults = await testConnectivity();
    
    // Return the first working URL
    for (final entry in connectivityResults.entries) {
      if (entry.value) {
        return entry.key;
      }
    }
    
    // Fallback to default
    return backendUrl;
  }
} 