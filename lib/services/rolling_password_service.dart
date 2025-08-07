import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class RollingPasswordService {
  static const String baseUrl =
      'https://compassionate-truth-production-2fcd.up.railway.app'; // Railway backend URL
  static const String adminPassword = '813819';
  static const String adminPhrase = 'there are no wolves on fenris';

  /// Initialize rolling password system with initial password
  static Future<Map<String, dynamic>> initializePassword(
    String initialPassword,
  ) async {
    try {
      final url = Uri.parse('$baseUrl/api/auth/login');

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': 'app_user', 'password': initialPassword}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;

        // Save session token locally
        if (data['session_token'] != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('session_token', data['session_token']);
        }

        return {
          'success': true,
          'message': 'Password initialized successfully',
          'next_password': data['next_password'],
          'password_expires_at': data['password_expires_at'],
        };
      } else {
        return {
          'success': false,
          'message': 'Failed to initialize password',
          'error': 'HTTP ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to connect to backend',
        'error': e.toString(),
      };
    }
  }

  /// Get current password from backend
  static Future<String?> getCurrentPassword() async {
    try {
      final url = Uri.parse('$baseUrl/api/auth/current-password');

      final response = await http.get(
        url,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return data['current_password'];
      }
      return null;
    } catch (e) {
      print('[ROLLING_PASSWORD_SERVICE] ❌ Error getting current password: $e');
      return null;
    }
  }

  /// Verify current password with backend
  static Future<Map<String, dynamic>> verifyPassword(String password) async {
    try {
      final url = Uri.parse('$baseUrl/api/auth/login');

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_id': 'app_user', 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;

        if (data['success'] == true) {
          // Update session token
          if (data['session_token'] != null) {
            final prefs = await SharedPreferences.getInstance();
            await prefs.setString('session_token', data['session_token']);
          }

          return {
            'success': true,
            'message': 'Password verified successfully',
            'next_password': data['next_password'],
            'password_expires_at': data['password_expires_at'],
            'time_until_expiry': data['time_until_expiry'],
          };
        } else {
          return {
            'success': false,
            'message': 'Invalid password',
            'error': data['error'],
            'attempts_remaining': data['attempts_remaining'],
          };
        }
      } else {
        return {
          'success': false,
          'message': 'Failed to verify password',
          'error': 'HTTP ${response.statusCode}',
        };
      }
    } catch (e) {
      print('[ROLLING_PASSWORD_SERVICE] ❌ Backend not available: $e');
      
      // Fallback: check against local storage
      final prefs = await SharedPreferences.getInstance();
      final savedPassword = prefs.getString('app_pin');
      
      if (savedPassword == password) {
        // Generate a new password for next time
        final newPassword = _generateNewPassword();
        await prefs.setString('app_pin', newPassword);
        
        return {
          'success': true,
          'message': 'Password verified (offline mode)',
          'next_password': newPassword,
          'password_expires_at': DateTime.now().add(Duration(hours: 1)).toIso8601String(),
          'time_until_expiry': '1 hour',
        };
      }
      
      return {
        'success': false,
        'message': 'Failed to connect to backend',
        'error': e.toString(),
      };
    }
  }

  /// Admin password recovery - works locally
  static Future<Map<String, dynamic>> adminPasswordRecovery(
    String password,
    String phrase,
  ) async {
    // Check if admin credentials are correct
    if (password == adminPassword &&
        phrase.toLowerCase().trim() == adminPhrase) {
      try {
        // Generate a new rolling password
        final newPassword = _generateNewPassword();

        // Initialize the new password with backend
        final result = await initializePassword(newPassword);

        if (result['success'] == true) {
          // Save the new password locally as backup
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('app_pin', newPassword);

          return {
            'success': true,
            'message': 'Admin recovery successful. New password generated.',
            'new_password': newPassword,
            'next_password': result['next_password'],
            'password_expires_at': result['password_expires_at'],
          };
        } else {
          // If backend fails, create a local password for emergency access
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('app_pin', newPassword);
          
          return {
            'success': true,
            'message': 'Admin recovery successful (offline mode). New password generated.',
            'new_password': newPassword,
            'password_expires_at': DateTime.now().add(Duration(hours: 1)).toIso8601String(),
            'time_until_expiry': '1 hour',
          };
        }
      } catch (e) {
        // Emergency fallback - create local password
        final newPassword = _generateNewPassword();
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('app_pin', newPassword);
        
        return {
          'success': true,
          'message': 'Admin recovery successful (emergency mode). New password generated.',
          'new_password': newPassword,
          'password_expires_at': DateTime.now().add(Duration(hours: 1)).toIso8601String(),
          'time_until_expiry': '1 hour',
        };
      }
    } else {
      return {
        'success': false,
        'message': 'Invalid admin credentials',
        'error': 'Incorrect password or phrase',
      };
    }
  }

  /// Generate a new password locally
  static String _generateNewPassword() {
    final random = DateTime.now().millisecondsSinceEpoch;
    final base = random.toString();
    final password = base.substring(base.length - 6);
    return password.padLeft(6, '0');
  }

  /// Get current password status from backend
  static Future<Map<String, dynamic>> getPasswordStatus() async {
    try {
      final url = Uri.parse('$baseUrl/api/auth/current-password-status');

      final response = await http.get(
        url,
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return {'success': true, 'status': data};
      } else {
        return {
          'success': false,
          'message': 'Failed to get password status',
          'error': 'HTTP ${response.statusCode}',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'message': 'Failed to connect to backend',
        'error': e.toString(),
      };
    }
  }

  /// Get session token from local storage
  static Future<String?> getSessionToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('session_token');
  }

  /// Clear session token from local storage
  static Future<void> clearSessionToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('session_token');
  }
}
