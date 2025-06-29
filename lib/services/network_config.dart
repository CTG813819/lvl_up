import 'dart:io';
import 'package:flutter/foundation.dart';

class NetworkConfig {
  // AWS EC2 Backend URL (for production)
  static const String baseUrl = 'http://44.204.184.21:4000';
  
  // Local Development Backend URL (for development)
  static const String localBaseUrl = 'http://192.168.1.118:4000';
  
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
  static String get backendUrl => baseUrl;
  
  /// Get all possible backend URLs for testing
  static List<String> get allBackendUrls => [
    'http://10.0.2.2:4000', // Android emulator
    'http://192.168.1.118:4000', // Local network
    'http://localhost:4000', // Local development
    'http://127.0.0.1:4000', // Local development
    baseUrl, // AWS (for production)
  ];
  
  /// Test connectivity to all backend URLs
  static Future<Map<String, bool>> testConnectivity() async {
    final results = <String, bool>{};
    
    for (final url in allBackendUrls) {
      try {
        final client = HttpClient();
        client.connectionTimeout = const Duration(seconds: 5);
        // Try to connect to the base URL instead of a specific endpoint
        final request = await client.getUrl(Uri.parse(url));
        final response = await request.close();
        results[url] = response.statusCode < 500; // Accept any non-server error
        client.close();
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
        print('[NETWORK] Using backend: ${entry.key}');
        return entry.key;
      }
    }
    
    // Fallback to default
    print('[NETWORK] No working backend found, using default: $backendUrl');
    return backendUrl;
  }
  
  /// Get a working backend URL with retry logic
  static Future<String> getWorkingBackendUrl() async {
    for (int i = 0; i < maxRetries; i++) {
      try {
        final url = await getBestBackendUrl();
        final client = HttpClient();
        client.connectionTimeout = const Duration(seconds: 10);
        // Try to connect to the base URL instead of a specific endpoint
        final request = await client.getUrl(Uri.parse(url));
        final response = await request.close();
        client.close();
        
        if (response.statusCode < 500) { // Accept any non-server error
          return url;
        }
      } catch (e) {
        print('[NETWORK] Retry $i failed: $e');
        if (i < maxRetries - 1) {
          await Future.delayed(retryDelay);
        }
      }
    }
    
    return backendUrl;
  }
} 