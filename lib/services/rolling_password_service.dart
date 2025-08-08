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
      print(
        '[ROLLING_PASSWORD_SERVICE] 🔐 Attempting to verify password with backend...',
      );

      final url = Uri.parse('$baseUrl/api/auth/login');

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'user_id': 'app_user', 'password': password}),
          )
          .timeout(Duration(seconds: 10)); // Add timeout for faster response

      print(
        '[ROLLING_PASSWORD_SERVICE] 📡 Backend response status: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        print('[ROLLING_PASSWORD_SERVICE] 📊 Backend response data: $data');

        if (data['success'] == true) {
          // Update session token
          if (data['session_token'] != null) {
            final prefs = await SharedPreferences.getInstance();
            await prefs.setString('session_token', data['session_token']);
            print('[ROLLING_PASSWORD_SERVICE] 🔑 Session token updated');
          }

          final nextPassword = data['next_password'];
          print(
            '[ROLLING_PASSWORD_SERVICE] 🔄 Next password from backend: $nextPassword',
          );

          return {
            'success': true,
            'message': 'Password verified successfully',
            'next_password': nextPassword,
            'password_expires_at': data['password_expires_at'],
            'time_until_expiry': data['time_until_expiry'],
          };
        } else {
          print(
            '[ROLLING_PASSWORD_SERVICE] ❌ Backend verification failed: ${data['error']}',
          );

          // Check if this is an expired password scenario
          if (data['error'] == 'invalid_password' ||
              data['error'] == 'expired_password') {
            // Try local storage as fallback for expired passwords
            final prefs = await SharedPreferences.getInstance();
            final savedPassword = prefs.getString('app_pin');

            if (savedPassword == password) {
              print(
                '[ROLLING_PASSWORD_SERVICE] ✅ Expired password accepted locally',
              );

              // Attempt to fetch the current/new password from backend
              String? newPassword;
              try {
                // First try to get current password
                final currentRes = await http
                    .get(
                      Uri.parse('$baseUrl/api/auth/current-password'),
                      headers: {'Content-Type': 'application/json'},
                    )
                    .timeout(const Duration(seconds: 10));
                if (currentRes.statusCode == 200) {
                  final cur =
                      jsonDecode(currentRes.body) as Map<String, dynamic>;
                  newPassword = cur['current_password'] as String?;
                }

                // If not available, force rotation then fetch again
                if (newPassword == null) {
                  await http
                      .post(
                        Uri.parse('$baseUrl/api/auth/force-rotation'),
                        headers: {'Content-Type': 'application/json'},
                      )
                      .timeout(const Duration(seconds: 10));

                  final currentRes2 = await http
                      .get(
                        Uri.parse('$baseUrl/api/auth/current-password'),
                        headers: {'Content-Type': 'application/json'},
                      )
                      .timeout(const Duration(seconds: 10));
                  if (currentRes2.statusCode == 200) {
                    final cur2 =
                        jsonDecode(currentRes2.body) as Map<String, dynamic>;
                    newPassword = cur2['current_password'] as String?;
                  }
                }
              } catch (e) {
                print(
                  '[ROLLING_PASSWORD_SERVICE] ❌ Error fetching new password after expiry: $e',
                );
              }

              if (newPassword != null && newPassword.isNotEmpty) {
                await prefs.setString('app_pin', newPassword);
                print(
                  '[ROLLING_PASSWORD_SERVICE] ✅ Retrieved new backend password after expiry',
                );

                // Optionally, get expiry/status info
                String? passwordExpiresAt;
                String? timeUntilExpiry;
                try {
                  final statusRes = await http
                      .get(
                        Uri.parse('$baseUrl/api/auth/current-password-status'),
                        headers: {'Content-Type': 'application/json'},
                      )
                      .timeout(const Duration(seconds: 10));
                  if (statusRes.statusCode == 200) {
                    final st =
                        jsonDecode(statusRes.body) as Map<String, dynamic>;
                    passwordExpiresAt = st['expires_at'] as String?;
                    timeUntilExpiry = st['time_until_expiry'] as String?;
                  }
                } catch (_) {}

                return {
                  'success': true,
                  'message':
                      'Password verified (expired but rotated by backend)',
                  'next_password': newPassword,
                  'password_expires_at': passwordExpiresAt,
                  'time_until_expiry': timeUntilExpiry,
                };
              }

              // Backend did not provide a new one right now
              return {
                'success': true,
                'message': 'Password verified (expired but accepted locally)',
                'next_password': null,
                'password_expires_at':
                    DateTime.now().add(Duration(hours: 1)).toIso8601String(),
                'time_until_expiry': '1 hour',
              };
            }
          }

          return {
            'success': false,
            'message': 'Invalid password',
            'error': data['error'],
            'attempts_remaining': data['attempts_remaining'],
          };
        }
      } else {
        print(
          '[ROLLING_PASSWORD_SERVICE] ❌ Backend HTTP error: ${response.statusCode}',
        );
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
        // Accept password locally but don't generate new one
        // Backend will provide new password on next successful verification
        print('[ROLLING_PASSWORD_SERVICE] ✅ Offline verification successful');

        return {
          'success': true,
          'message': 'Password verified (offline mode)',
          'next_password': null,
          'password_expires_at':
              DateTime.now().add(Duration(hours: 1)).toIso8601String(),
          'time_until_expiry': '1 hour',
        };
      }

      print('[ROLLING_PASSWORD_SERVICE] ❌ Offline verification failed');
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
        // Force rotation then fetch current password from backend
        await http
            .post(
              Uri.parse('$baseUrl/api/auth/force-rotation'),
              headers: {'Content-Type': 'application/json'},
            )
            .timeout(const Duration(seconds: 10));

        final currentRes = await http
            .get(
              Uri.parse('$baseUrl/api/auth/current-password'),
              headers: {'Content-Type': 'application/json'},
            )
            .timeout(const Duration(seconds: 10));

        if (currentRes.statusCode == 200) {
          final cur = jsonDecode(currentRes.body) as Map<String, dynamic>;
          final newPassword = cur['current_password'] as String?;
          if (newPassword != null && newPassword.isNotEmpty) {
            final prefs = await SharedPreferences.getInstance();
            await prefs.setString('app_pin', newPassword);

            // Optionally fetch expiry/status info
            String? passwordExpiresAt;
            String? timeUntilExpiry;
            try {
              final statusRes = await http
                  .get(
                    Uri.parse('$baseUrl/api/auth/current-password-status'),
                    headers: {'Content-Type': 'application/json'},
                  )
                  .timeout(const Duration(seconds: 10));
              if (statusRes.statusCode == 200) {
                final st = jsonDecode(statusRes.body) as Map<String, dynamic>;
                passwordExpiresAt = st['expires_at'] as String?;
                timeUntilExpiry = st['time_until_expiry'] as String?;
              }
            } catch (_) {}

            return {
              'success': true,
              'message': 'Admin recovery successful. New password generated.',
              'new_password': newPassword,
              'next_password': newPassword,
              'password_expires_at': passwordExpiresAt,
              'time_until_expiry': timeUntilExpiry,
            };
          }
        }

        return {
          'success': false,
          'message': 'Admin recovery failed - could not obtain new password',
          'error': 'Rotation or fetch failed',
        };
      } catch (e) {
        // Emergency fallback - return error
        return {
          'success': false,
          'message': 'Admin recovery failed - system error',
          'error': e.toString(),
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
