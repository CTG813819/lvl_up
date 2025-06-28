import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Tally extends StatefulWidget {
  const Tally({super.key});

  @override
  State<Tally> createState() => _TallyState();
}

class _TallyState extends State<Tally> {
  int _counter = 0;
  static const String _counterKey = 'counter_value';

  @override
  void initState() {
    super.initState();
    _loadCounter();
  }

  // Load counter value from SharedPreferences
  Future<void> _loadCounter() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _counter = prefs.getInt(_counterKey) ?? 0;
    });
  }

  // Save counter value to SharedPreferences
  Future<void> _saveCounter() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_counterKey, _counter);
  }

  String _toRomanNumeral(int number) {
    if (number <= 0) return '0';
    const List<String> romanSymbols = [
      'M',
      'CM',
      'D',
      'CD',
      'C',
      'XC',
      'L',
      'XL',
      'X',
      'IX',
      'V',
      'IV',
      'I',
    ];
    const List<int> values = [
      1000,
      900,
      500,
      400,
      100,
      90,
      50,
      40,
      10,
      9,
      5,
      4,
      1,
    ];

    String result = '';
    int num = number;

    for (int i = 0; i < romanSymbols.length; i++) {
      while (num >= values[i]) {
        result += romanSymbols[i];
        num -= values[i];
      }
    }
    return result;
  }

  void _incrementCounter() {
    setState(() {
      _counter++;
      _saveCounter(); // Save the new counter value
    });
  }

  void _decrementCounter() {
    setState(() {
      if (_counter > 0) _counter--;
      _saveCounter(); // Save the new counter value
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _toRomanNumeral(_counter),
              style: const TextStyle(
                color: Color.fromARGB(255, 247, 0, 0),
                fontSize: 150,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _incrementCounter,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                  ),
                  child: const Text('+1'),
                ),
                const SizedBox(width: 20),
                ElevatedButton(
                  onPressed: _decrementCounter,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black,
                  ),
                  child: const Text('-1'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
