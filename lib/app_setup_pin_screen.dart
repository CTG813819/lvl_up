import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'services/rolling_password_service.dart';

class AppSetupPinScreen extends StatefulWidget {
  const AppSetupPinScreen({super.key});

  @override
  _AppSetupPinScreenState createState() => _AppSetupPinScreenState();
}

class _AppSetupPinScreenState extends State<AppSetupPinScreen> {
  String enteredPin = '';
  String confirmPin = '';
  bool isConfirming = false;
  String errorMessage = '';
  bool isLoading = false;
  final pinController = TextEditingController();

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
  void dispose() {
    pinController.dispose();
    super.dispose();
  }

  Future<void> _savePin(String pin) async {
    setState(() {
      isLoading = true;
    });

    try {
      // Initialize rolling password with backend
      final result = await RollingPasswordService.initializePassword(pin);
      
      if (result['success'] == true) {
        // Also save locally as backup
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('app_pin', pin);
        
        if (mounted) {
          Navigator.of(context).pushReplacementNamed('/home');
        }
      } else {
        setState(() {
          errorMessage = result['message'] ?? 'Failed to initialize password';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Failed to connect to backend: $e';
        isLoading = false;
      });
    }
  }

  void _handlePinComplete(String value) {
    if (!isConfirming) {
      setState(() {
        enteredPin = value;
        isConfirming = true;
        pinController.clear();
        errorMessage = '';
      });
    } else {
      setState(() {
        confirmPin = value;
      });
      if (enteredPin == confirmPin) {
        _savePin(confirmPin);
      } else {
        setState(() {
          errorMessage = 'PINs do not match';
          isConfirming = false;
          enteredPin = '';
          confirmPin = '';
          pinController.clear();
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final focusedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.purple,
        border: Border.all(color: Colors.purple),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final submittedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.purple,
        border: Border.all(color: Colors.purple),
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
        child: Container(
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.purple.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.flash_on, color: Colors.purple, size: 60),
              const SizedBox(height: 16),
              Text(
                'Set a PIN for LVL UP',
                style: TextStyle(
                  fontSize: 22,
                  color: Colors.purple,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                isConfirming
                    ? 'Please enter the PIN again to confirm'
                    : 'Enter a 6-digit PIN to secure your app',
                style: const TextStyle(fontSize: 16, color: Colors.white70),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              SizedBox(
                height: 80, // Fixed height for Pinput
                child: Pinput(
                  controller: pinController,
                  length: 6,
                  defaultPinTheme: defaultPinTheme,
                  focusedPinTheme: focusedPinTheme,
                  submittedPinTheme: submittedPinTheme,
                  errorPinTheme: errorMessage.isNotEmpty ? errorPinTheme : null,
                  obscureText: true,
                  keyboardType: TextInputType.number,
                  enabled: !isLoading,
                  onChanged: (value) {
                    setState(() {
                      errorMessage = '';
                    });
                  },
                  onCompleted: _handlePinComplete,
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
              if (isLoading) ...[
                const SizedBox(height: 16),
                const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.purple),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Connecting to backend...',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
              ],
              const SizedBox(height: 32),
              if (!isConfirming && !isLoading)
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop(false); // Return cancelled
                  },
                  child: const Text(
                    'Cancel',
                    style: TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
