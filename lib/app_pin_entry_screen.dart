import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app_setup_pin_screen.dart';
import 'services/rolling_password_service.dart';
import 'dart:async'; // Added for Timer

class AppPinEntryScreen extends StatefulWidget {
  final Function(String, BuildContext) onPinEntered;
  final String title;

  const AppPinEntryScreen({
    required this.onPinEntered,
    required this.title,
    super.key,
  });

  @override
  _AppPinEntryScreenState createState() => _AppPinEntryScreenState();
}

class _AppPinEntryScreenState extends State<AppPinEntryScreen>
    with TickerProviderStateMixin {
  String enteredPin = '';
  String errorMessage = '';
  final pinController = TextEditingController();
  late AnimationController _pulseAnimationController;

  // Timer variables
  Timer? _passwordTimer;
  String _timeUntilExpiry = '';
  String _timeUntilNextPassword = '';

  // Loading state
  bool isLoading = false;

  final defaultPinTheme = PinTheme(
    width: 56,
    height: 56,
    textStyle: const TextStyle(fontSize: 20, color: Colors.black),
    decoration: BoxDecoration(
      color: Colors.white,
      border: Border.all(color: Colors.white),
      borderRadius: BorderRadius.circular(8),
    ),
  );

  @override
  void initState() {
    super.initState();
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Start the pulse animation
    _pulseAnimationController.repeat(reverse: true);
    _checkPinSetup();
    _startPasswordTimer();
  }

  @override
  void dispose() {
    pinController.dispose();
    _pulseAnimationController.dispose();
    _passwordTimer?.cancel();
    super.dispose();
  }

  void _startPasswordTimer() {
    // Update timer every second
    _passwordTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      _updatePasswordTimers();
    });
  }

  void _updatePasswordTimers() async {
    try {
      // Check if widget is still mounted before proceeding
      if (!mounted) return;

      // Get password status from backend
      final status = await RollingPasswordService.getPasswordStatus();
      if (status['success'] == true) {
        final timeUntilExpiry = status['status']?['time_until_expiry'];

        if (timeUntilExpiry != null && mounted) {
          setState(() {
            _timeUntilExpiry = timeUntilExpiry;
            // Don't show next password timing - it should only be generated after login
            _timeUntilNextPassword = '';
          });
        }
      }
    } catch (e) {
      print('[APP_PIN_ENTRY] ❌ Error updating password timers: $e');
    }
  }

  Future<void> _checkPinSetup() async {
    try {
      // Try to get current password status from backend
      final passwordStatus = await RollingPasswordService.getPasswordStatus();

      if (passwordStatus['success'] == true) {
        // Backend has a password, use rolling password system
        print('[APP_PIN_ENTRY] ✅ Using rolling password system');
        return;
      }
    } catch (e) {
      print(
        '[APP_PIN_ENTRY] ⚠️ Rolling password system not available, using local storage: $e',
      );
    }

    // Fallback to local storage check
    final prefs = await SharedPreferences.getInstance();
    final savedPin = prefs.getString('app_pin');
    if (savedPin == null) {
      if (mounted) {
        final result = await Navigator.of(context).push(
          MaterialPageRoute(builder: (context) => const AppSetupPinScreen()),
        );
        if (result != true && mounted) {
          Navigator.of(context).pop(); // Go back if setup was cancelled
        }
      }
    }
  }

  Future<bool> _verifyPin(String pin) async {
    try {
      setState(() {
        isLoading = true;
        errorMessage = '';
      });

      print('[APP_PIN_ENTRY] 🔐 Verifying password: $pin');

      // Try rolling password authentication first
      final authResult = await RollingPasswordService.verifyPassword(pin);

      print('[APP_PIN_ENTRY] 🔍 Auth result: $authResult');

      if (authResult['success'] == true) {
        // Check if we have a next password to show
        final nextPassword = authResult['next_password'];

        if (nextPassword != null && nextPassword.isNotEmpty) {
          print('[APP_PIN_ENTRY] 🔄 New password received: $nextPassword');

          // Store the new password locally
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('app_pin', nextPassword);

          // Show new password dialog and wait for user to continue
          if (mounted) {
            await _showNewPasswordDialog(context, nextPassword);
          }
          return true;
        } else {
          print('[APP_PIN_ENTRY] ✅ No new password, proceeding normally');
          // No new password, proceed normally
          widget.onPinEntered(pin, context);
          return true;
        }
      } else {
        print(
          '[APP_PIN_ENTRY] ❌ Rolling password failed, trying local storage',
        );

        // Try local storage as fallback
        final prefs = await SharedPreferences.getInstance();
        final savedPin = prefs.getString('app_pin');

        if (savedPin == pin) {
          print('[APP_PIN_ENTRY] ✅ Local storage verification successful');

          // Accept password locally but don't generate new one
          // Backend will provide new password on next successful verification
          print('[APP_PIN_ENTRY] 🔄 Password accepted locally');

          // Continue to app without showing new password dialog
          // since we don't have a new password from backend
          return true;
        } else {
          print('[APP_PIN_ENTRY] ❌ Invalid password');
          setState(() {
            errorMessage = authResult['message'] ?? 'Invalid password';
          });
          return false;
        }
      }
    } catch (e) {
      print('[APP_PIN_ENTRY] ❌ Error verifying password: $e');
      setState(() {
        errorMessage = 'Authentication error: $e';
      });
      return false;
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  Future<Map<String, dynamic>> _getPasswordStatus() async {
    try {
      final status = await RollingPasswordService.getPasswordStatus();
      return {
        'is_rolling': status['success'] == true,
        'last_rotation': status['status']?['last_rotation'],
        'next_rotation': status['status']?['next_rotation'],
      };
    } catch (e) {
      print('[APP_PIN_ENTRY] ❌ Error getting password status: $e');
      return {
        'is_rolling': false,
        'last_rotation': null,
        'next_rotation': null,
      };
    }
  }

  void _showAdminRecoveryDialog(BuildContext context) {
    String adminPassword = '';
    String adminPhrase = '';
    bool isLoading = false;
    String errorMessage = '';

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: Colors.grey[900],
              title: Row(
                children: [
                  Icon(Icons.admin_panel_settings, color: Colors.purple),
                  const SizedBox(width: 8),
                  Text(
                    'Admin Recovery',
                    style: TextStyle(
                      color: Colors.purple,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Enter admin credentials to reset password',
                    style: TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.blue.withOpacity(0.5)),
                    ),
                    child: Text(
                      '💡 Tip: You can also try your last known password if you remember it.',
                      style: TextStyle(color: Colors.blue[300], fontSize: 10),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    onChanged: (value) => adminPassword = value,
                    decoration: InputDecoration(
                      labelText: 'Admin Password',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.grey[600]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.purple),
                      ),
                    ),
                    style: TextStyle(color: Colors.white),
                    obscureText: true,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    onChanged: (value) => adminPhrase = value,
                    decoration: InputDecoration(
                      labelText: 'Admin Phrase',
                      labelStyle: TextStyle(color: Colors.white70),
                      border: OutlineInputBorder(),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.grey[600]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(color: Colors.purple),
                      ),
                    ),
                    style: TextStyle(color: Colors.white),
                  ),
                  if (errorMessage.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      errorMessage,
                      style: TextStyle(color: Colors.red, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ],
                  if (isLoading) ...[
                    const SizedBox(height: 16),
                    CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
                    ),
                  ],
                ],
              ),
              actions: [
                TextButton(
                  onPressed:
                      isLoading ? null : () => Navigator.of(context).pop(),
                  child: Text(
                    'Cancel',
                    style: TextStyle(color: Colors.white70),
                  ),
                ),
                ElevatedButton(
                  onPressed:
                      isLoading
                          ? null
                          : () async {
                            setState(() {
                              isLoading = true;
                              errorMessage = '';
                            });

                            try {
                              final result =
                                  await RollingPasswordService.adminPasswordRecovery(
                                    adminPassword,
                                    adminPhrase,
                                  );

                              if (result['success'] == true) {
                                Navigator.of(context).pop();
                                // Show success message with new password
                                _showNewPasswordDialog(
                                  context,
                                  result['new_password'],
                                );
                              } else {
                                setState(() {
                                  errorMessage =
                                      result['message'] ?? 'Recovery failed';
                                  isLoading = false;
                                });
                              }
                            } catch (e) {
                              setState(() {
                                errorMessage = 'Error: $e';
                                isLoading = false;
                              });
                            }
                          },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple,
                    foregroundColor: Colors.white,
                  ),
                  child: Text('Recover'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showNewPasswordDialog(
    BuildContext context,
    String newPassword,
  ) async {
    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green),
              const SizedBox(width: 8),
              Text(
                'Login Successful!',
                style: TextStyle(
                  color: Colors.green,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: Column(
                  children: [
                    Icon(Icons.security, color: Colors.green, size: 20),
                    const SizedBox(height: 8),
                    Text(
                      'Your password has been rotated for security.',
                      style: TextStyle(color: Colors.green, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Your new password for next login is:',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 16),
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green),
                ),
                child: Text(
                  newPassword,
                  style: TextStyle(
                    color: Colors.green,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange),
                ),
                child: Column(
                  children: [
                    Icon(Icons.warning_amber, color: Colors.orange, size: 20),
                    const SizedBox(height: 8),
                    Text(
                      '⚠️ Remember this password! You will need it for your next login.',
                      style: TextStyle(color: Colors.orange, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Continue to the main app with the new password
                print(
                  '[APP_PIN_ENTRY] 🚀 Continuing to app with new password: $newPassword',
                );
                widget.onPinEntered(newPassword, context);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
              ),
              child: Text('Continue to App'),
            ),
          ],
        );
      },
    );
  }

  void _showCurrentPasswordDialog(
    BuildContext context,
    String currentPassword,
  ) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.lock, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                'Rolling Password System',
                style: TextStyle(
                  color: Colors.blue,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Your current password to log in:',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 16),
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue),
                ),
                child: Text(
                  currentPassword,
                  style: TextStyle(
                    color: Colors.blue,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange),
                ),
                child: Column(
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange, size: 20),
                    const SizedBox(height: 8),
                    Text(
                      'After successful login, you will receive a new password for next time.',
                      style: TextStyle(color: Colors.orange, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.purple),
                ),
                child: Column(
                  children: [
                    Icon(Icons.timer, color: Colors.purple, size: 20),
                    const SizedBox(height: 8),
                    Text(
                      'Password expires in: $_timeUntilExpiry',
                      style: TextStyle(
                        color: Colors.purple,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'If you miss the login window, use admin recovery.',
                      style: TextStyle(color: Colors.purple, fontSize: 12),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: Text('OK'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final focusedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.yellow,
        border: Border.all(color: Colors.yellow),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final submittedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.yellow,
        border: Border.all(color: Colors.yellow),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final errorPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.red,
        border: Border.all(color: Colors.red),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.yellow.withOpacity(0.2),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Colors.yellow.withOpacity(0.5),
                    width: 2,
                  ),
                ),
                child: Icon(
                  Icons.flash_on,
                  size: 80,
                  color: Colors.yellow.withOpacity(0.8),
                ),
              ),
              const SizedBox(height: 40),
              Text(
                'LVL UP',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.yellow,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Enter password to access the app',
                style: TextStyle(fontSize: 16, color: Colors.grey[400]),
              ),
              const SizedBox(height: 8),
              FutureBuilder<Map<String, dynamic>>(
                future: _getPasswordStatus(),
                builder: (context, snapshot) {
                  if (snapshot.hasData &&
                      snapshot.data!['is_rolling'] == true) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.purple.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                          color: Colors.purple.withOpacity(0.5),
                        ),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.security,
                                color: Colors.purple,
                                size: 16,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Rolling Password Active',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.purple[300],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Column(
                                children: [
                                  Icon(
                                    Icons.timer,
                                    color: Colors.red[300],
                                    size: 16,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    'Expires in:',
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: Colors.red[300],
                                    ),
                                  ),
                                  Text(
                                    _timeUntilExpiry.isNotEmpty
                                        ? _timeUntilExpiry
                                        : '--:--',
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.red[300],
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }
                  return const SizedBox.shrink();
                },
              ),
              const SizedBox(height: 40),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.yellow),
                      ),
                      child: TextField(
                        controller: pinController,
                        obscureText: true,
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.black,
                          fontFamily: 'monospace',
                        ),
                        decoration: InputDecoration(
                          hintText: 'Enter password',
                          hintStyle: TextStyle(color: Colors.grey[600]),
                          border: InputBorder.none,
                          contentPadding: EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 16,
                          ),
                        ),
                        onChanged: (value) {
                          setState(() {
                            enteredPin = value;
                            errorMessage = '';
                          });
                        },
                        onSubmitted: (value) async {
                          if (value.isNotEmpty) {
                            final isValid = await _verifyPin(value);
                            if (isValid && mounted) {
                              // Don't call widget.onPinEntered here if we're showing the new password dialog
                              // The dialog will handle the navigation
                              if (!mounted) return;

                              // Check if we have a next password to show
                              final prefs =
                                  await SharedPreferences.getInstance();
                              final nextPassword = prefs.getString('app_pin');
                              if (nextPassword != value) {
                                // We have a new password, the dialog will handle navigation
                                return;
                              }

                              // No new password, proceed normally
                              widget.onPinEntered(value, context);
                            } else if (mounted) {
                              setState(() {
                                errorMessage = 'Invalid password';
                              });
                              pinController.clear();
                            }
                          }
                        },
                      ),
                    ),
                    if (errorMessage.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      Text(
                        errorMessage,
                        style: const TextStyle(color: Colors.red, fontSize: 16),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    const SizedBox(height: 32),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed:
                            isLoading
                                ? null
                                : () async {
                                  if (enteredPin.isNotEmpty) {
                                    setState(() {
                                      isLoading = true;
                                      errorMessage = '';
                                    });

                                    try {
                                      final isValid = await _verifyPin(
                                        enteredPin,
                                      );
                                      if (isValid && mounted) {
                                        widget.onPinEntered(
                                          enteredPin,
                                          context,
                                        );
                                      } else if (mounted) {
                                        setState(() {
                                          errorMessage = 'Invalid PIN';
                                        });
                                        pinController.clear();
                                      }
                                    } finally {
                                      if (mounted) {
                                        setState(() {
                                          isLoading = false;
                                        });
                                      }
                                    }
                                  } else if (mounted) {
                                    setState(() {
                                      errorMessage = 'Please enter a PIN';
                                    });
                                  }
                                },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          backgroundColor:
                              isLoading ? Colors.grey : Colors.yellow,
                          foregroundColor: Colors.black,
                        ),
                        child:
                            isLoading
                                ? Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                        valueColor:
                                            AlwaysStoppedAnimation<Color>(
                                              Colors.black,
                                            ),
                                      ),
                                    ),
                                    const SizedBox(width: 12),
                                    const Text(
                                      'Verifying...',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                )
                                : const Text(
                                  'Continue',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: () => _showAdminRecoveryDialog(context),
                      child: Text(
                        'Forgot Password?',
                        style: TextStyle(color: Colors.grey[400], fontSize: 14),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
