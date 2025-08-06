import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

// Add this to your Flutter app for WebSocket fallback
class WebSocketFallback {
  static const String baseUrl = 'https://lvlup-production-1a5a.up.railway.app';
  static const Duration pollInterval = Duration(seconds: 5);

  static Future<void> startPolling(Function(dynamic) onData) async {
    Timer.periodic(pollInterval, (timer) async {
      try {
        final response = await http.get(
          Uri.parse('$baseUrl/api/imperium/dashboard'),
          headers: {'Content-Type': 'application/json'},
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          onData(data);
        }
      } catch (e) {
        print('Polling error: $e');
      }
    });
  }
}
