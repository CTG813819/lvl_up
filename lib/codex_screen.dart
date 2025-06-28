import 'package:flutter/material.dart';
import 'widgets/ai_learning_dashboard.dart';
import './home_page.dart';

class CodexScreen extends StatelessWidget {
  const CodexScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (context) => const Homepage()),
              (route) => false,
            );
          },
        ),
        title: const Text('The Codex'),
      ),
      body: const AILearningDashboard(),
    );
  }
} 