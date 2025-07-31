import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'setup_pin_screen.dart';

class EntryPinScreen extends StatefulWidget {
  final Function(String, BuildContext) onPinEntered;
  final String title;
  final bool isViewing;

  const EntryPinScreen({
    required this.onPinEntered,
    required this.title,
    this.isViewing = false,
    super.key,
  });

  @override
  _EntryPinScreenState createState() => _EntryPinScreenState();
}

class _EntryPinScreenState extends State<EntryPinScreen> {
  String enteredPin = '';
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
  void initState() {
    super.initState();
    _checkPinSetup();
  }

  @override
  void dispose() {
    pinController.dispose();
    super.dispose();
  }

  Future<void> _checkPinSetup() async {
    final prefs = await SharedPreferences.getInstance();
    final savedPin = prefs.getString('entry_pin');
    if (savedPin == null) {
      if (mounted) {
        final result = await Navigator.of(
          context,
        ).push(MaterialPageRoute(builder: (context) => const SetupPinScreen()));
        if (result != true && mounted) {
          Navigator.of(context).pop(); // Go back if setup was cancelled
        }
      }
    }
  }

  Future<bool> _verifyPin(String pin) async {
    final prefs = await SharedPreferences.getInstance();
    final savedPin = prefs.getString('entry_pin');
    return savedPin == pin;
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
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  widget.title,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.purple,
                  ),
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
              ],
            ),
          ),
        ),
      ),
    );
  }
}
