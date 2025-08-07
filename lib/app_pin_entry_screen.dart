import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'app_setup_pin_screen.dart';
import 'services/rolling_password_service.dart';

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
  late AnimationController _lightningAnimationController;
  late AnimationController _pulseAnimationController;

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
    _lightningAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    _pulseAnimationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Start the pulse animation
    _pulseAnimationController.repeat(reverse: true);
    _checkPinSetup();
  }

  @override
  void dispose() {
    pinController.dispose();
    _lightningAnimationController.dispose();
    _pulseAnimationController.dispose();
    super.dispose();
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
      // Try to authenticate with the rolling password system
      final authResult = await RollingPasswordService.verifyPassword(pin);

      if (authResult['success'] == true) {
        // Store the new password if provided
        if (authResult['next_password'] != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('app_pin', authResult['next_password']);
        }
        return true;
      }

      // Fallback to local storage for backward compatibility
      final prefs = await SharedPreferences.getInstance();
      final savedPin = prefs.getString('app_pin');
      return savedPin == pin;
    } catch (e) {
      print('[APP_PIN_ENTRY] ❌ Error verifying pin: $e');
      // Fallback to local storage on error
      final prefs = await SharedPreferences.getInstance();
      final savedPin = prefs.getString('app_pin');
      return savedPin == pin;
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

  void _showNewPasswordDialog(BuildContext context, String newPassword) {
    showDialog(
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
                'Password Reset Successful',
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
              Text(
                'Your new password is:',
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
              Text(
                'Please remember this password. You can use it to access the app.',
                style: TextStyle(color: Colors.white70, fontSize: 12),
                textAlign: TextAlign.center,
              ),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                // Clear the PIN input and show the new password
                pinController.clear();
                setState(() {
                  enteredPin = '';
                  errorMessage = '';
                });
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
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
              AnimatedBuilder(
                animation: _pulseAnimationController,
                builder: (context, child) {
                  return Transform.scale(
                    scale: 1.0 + (_pulseAnimationController.value * 0.3),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.yellow.withOpacity(
                          0.2 + (_pulseAnimationController.value * 0.3),
                        ),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: Colors.yellow.withOpacity(
                            0.5 + (_pulseAnimationController.value * 0.5),
                          ),
                          width: 2 + (_pulseAnimationController.value * 2),
                        ),
                      ),
                      child: Icon(
                        Icons.flash_on,
                        size: 80,
                        color: Colors.yellow.withOpacity(
                          0.8 + (_pulseAnimationController.value * 0.2),
                        ),
                      ),
                    ),
                  );
                },
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
                'Enter PIN to access the app',
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
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.security, color: Colors.purple, size: 16),
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
                    SizedBox(
                      height: 80, // Fixed height for Pinput
                      child: Pinput(
                        controller: pinController,
                        length: 6,
                        defaultPinTheme: defaultPinTheme,
                        focusedPinTheme: focusedPinTheme,
                        submittedPinTheme: submittedPinTheme,
                        errorPinTheme:
                            errorMessage.isNotEmpty ? errorPinTheme : null,
                        obscureText: true,
                        keyboardType: TextInputType.number,
                        onChanged: (value) {
                          setState(() {
                            enteredPin = value;
                            errorMessage = '';
                          });
                        },
                        onCompleted: (value) async {
                          if (value.length == 6) {
                            final isValid = await _verifyPin(value);
                            if (isValid && mounted) {
                              widget.onPinEntered(value, context);
                            } else if (mounted) {
                              setState(() {
                                errorMessage = 'Invalid PIN';
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
                        onPressed: () async {
                          if (enteredPin.length == 6) {
                            final isValid = await _verifyPin(enteredPin);
                            if (isValid && mounted) {
                              widget.onPinEntered(enteredPin, context);
                            } else if (mounted) {
                              setState(() {
                                errorMessage = 'Invalid PIN';
                              });
                              pinController.clear();
                            }
                          } else if (mounted) {
                            setState(() {
                              errorMessage = 'PIN must be 6 digits';
                            });
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          backgroundColor: Colors.yellow,
                          foregroundColor: Colors.black,
                        ),
                        child: const Text(
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
