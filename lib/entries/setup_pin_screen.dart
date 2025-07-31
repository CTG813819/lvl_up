import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SetupPinScreen extends StatefulWidget {
  const SetupPinScreen({super.key});

  @override
  _SetupPinScreenState createState() => _SetupPinScreenState();
}

class _SetupPinScreenState extends State<SetupPinScreen> {
  String enteredPin = '';
  String confirmPin = '';
  bool isConfirming = false;
  String errorMessage = '';
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
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('entry_pin', pin);
  }

  void _handlePinComplete(String value) {
    if (!isConfirming) {
      setState(() {
        enteredPin = value;
        isConfirming = true;
        pinController.clear();
      });
    } else {
      setState(() {
        confirmPin = value;
      });
      if (enteredPin == confirmPin) {
        _savePin(confirmPin).then((_) {
          if (mounted) {
            Navigator.of(context).pop(true); // Return success
          }
        });
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
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    isConfirming ? 'Confirm PIN' : 'Set Up PIN',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.purple,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    isConfirming
                        ? 'Please enter the PIN again to confirm'
                        : 'Enter a 6-digit PIN to secure your entries',
                    style: const TextStyle(fontSize: 16, color: Colors.purple),
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
                      errorPinTheme:
                          errorMessage.isNotEmpty ? errorPinTheme : null,
                      obscureText: true,
                      keyboardType: TextInputType.number,
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
                  const SizedBox(height: 32),
                  if (!isConfirming)
                    TextButton(
                      onPressed: () {
                        Navigator.of(context).pop(false); // Return cancelled
                      },
                      child: const Text(
                        'Cancel',
                        style: TextStyle(color: Colors.purple, fontSize: 16),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
