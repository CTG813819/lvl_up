import 'package:flutter/material.dart';
import '../widgets/terminal_widget.dart';

class TerminalScreen extends StatefulWidget {
  const TerminalScreen({Key? key}) : super(key: key);

  @override
  State<TerminalScreen> createState() => _TerminalScreenState();
}

class _TerminalScreenState extends State<TerminalScreen> {
  bool _isFullScreen = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: _isFullScreen ? null : AppBar(
        title: const Text(
          'AI Learning Terminal',
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.grey[900],
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: Icon(_isFullScreen ? Icons.fullscreen_exit : Icons.fullscreen),
            onPressed: () {
              setState(() {
                _isFullScreen = !_isFullScreen;
              });
            },
            tooltip: _isFullScreen ? 'Exit Full Screen' : 'Full Screen',
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _showTerminalSettings,
            tooltip: 'Terminal Settings',
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(8.0),
          child: Column(
            children: [
              // Quick Actions Bar
              if (!_isFullScreen)
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.grey[900],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      _buildQuickActionButton(
                        'Status',
                        Icons.info,
                        () => _sendCommand('status'),
                      ),
                      const SizedBox(width: 8),
                      _buildQuickActionButton(
                        'AI Status',
                        Icons.smart_toy,
                        () => _sendCommand('ai status'),
                      ),
                      const SizedBox(width: 8),
                      _buildQuickActionButton(
                        'GitHub',
                        Icons.link,
                        () => _sendCommand('github status'),
                      ),
                      const SizedBox(width: 8),
                      _buildQuickActionButton(
                        'Deploy',
                        Icons.rocket_launch,
                        () => _sendCommand('deploy'),
                      ),
                      const SizedBox(width: 8),
                      _buildQuickActionButton(
                        'Clear',
                        Icons.clear,
                        () => _sendCommand('clear'),
                      ),
                      const Spacer(),
                      _buildQuickActionButton(
                        'Help',
                        Icons.help,
                        () => _sendCommand('help'),
                      ),
                    ],
                  ),
                ),
              
              const SizedBox(height: 8),
              
              // Terminal Widget
              Expanded(
                child: TerminalWidget(
                  title: 'AI Learning System Terminal',
                  showControls: true,
                  autoScroll: true,
                  maxLines: 2000,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionButton(String label, IconData icon, VoidCallback onPressed) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.grey[800],
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(6),
        ),
      ),
    );
  }

  void _sendCommand(String command) {
    // This would be implemented to send commands to the terminal
    // For now, we'll show a snackbar
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Command sent: $command'),
        duration: const Duration(seconds: 1),
        backgroundColor: Colors.grey[800],
      ),
    );
  }

  void _showTerminalSettings() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.grey[900],
        title: const Text(
          'Terminal Settings',
          style: TextStyle(color: Colors.white),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildSettingSwitch(
              'Auto-scroll',
              'Automatically scroll to latest output',
              true,
              (value) {
                // Handle auto-scroll setting
              },
            ),
            _buildSettingSwitch(
              'Show timestamps',
              'Display timestamps for each line',
              true,
              (value) {
                // Handle timestamp setting
              },
            ),
            _buildSettingSwitch(
              'Sound notifications',
              'Play sound for important events',
              false,
              (value) {
                // Handle sound setting
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // Apply settings
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }

  Widget _buildSettingSwitch(String title, String subtitle, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: Colors.grey[400],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: Colors.green,
          ),
        ],
      ),
    );
  }
} 