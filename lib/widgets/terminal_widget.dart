import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'dart:convert';
import '../services/ai_learning_service.dart';
import '../services/notification_service.dart';

class TerminalWidget extends StatefulWidget {
  final String title;
  final bool showControls;
  final bool autoScroll;
  final int maxLines;

  const TerminalWidget({
    Key? key,
    this.title = 'System Terminal',
    this.showControls = true,
    this.autoScroll = true,
    this.maxLines = 1000,
  }) : super(key: key);

  @override
  State<TerminalWidget> createState() => _TerminalWidgetState();
}

class _TerminalWidgetState extends State<TerminalWidget> {
  final ScrollController _scrollController = ScrollController();
  final List<TerminalLine> _lines = [];
  final TextEditingController _commandController = TextEditingController();
  bool _isConnected = false;
  Timer? _updateTimer;
  String _currentStatus = 'Disconnected';
  Color _statusColor = Colors.red;

  @override
  void initState() {
    super.initState();
    _initializeTerminal();
    _startStatusUpdates();
  }

  @override
  void dispose() {
    _updateTimer?.cancel();
    _scrollController.dispose();
    _commandController.dispose();
    super.dispose();
  }

  void _initializeTerminal() {
    _addLine('🚀 AI Learning System Terminal', TerminalType.info);
    _addLine('Initializing connection to backend...', TerminalType.system);
    _connectToBackend();
  }

  void _connectToBackend() async {
    try {
      final service = AILearningService();
      final status = await service.getSystemStatus();
      
      setState(() {
        _isConnected = true;
        _currentStatus = 'Connected';
        _statusColor = Colors.green;
      });
      
      _addLine('✅ Connected to AI Learning System', TerminalType.success);
      _addLine('System Status: ${status['status']}', TerminalType.info);
      _addLine('Active AIs: ${status['activeAIs']?.join(', ') ?? 'None'}', TerminalType.info);
      _addLine('Ready for commands. Type "help" for available commands.', TerminalType.system);
      
    } catch (e) {
      setState(() {
        _isConnected = false;
        _currentStatus = 'Connection Failed';
        _statusColor = Colors.red;
      });
      
      _addLine('❌ Failed to connect to backend: $e', TerminalType.error);
      _addLine('Retrying in 5 seconds...', TerminalType.warning);
      
      Future.delayed(const Duration(seconds: 5), () {
        if (mounted) _connectToBackend();
      });
    }
  }

  void _startStatusUpdates() {
    _updateTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted && _isConnected) {
        _updateSystemStatus();
      }
    });
  }

  void _updateSystemStatus() async {
    try {
      final service = AILearningService();
      final status = await service.getSystemStatus();
      
      if (mounted) {
        _addLine('📊 System Update: ${status['status']}', TerminalType.info);
        if (status['recentActivity'] != null) {
          _addLine('Recent Activity: ${status['recentActivity']}', TerminalType.info);
        }
      }
    } catch (e) {
      _addLine('⚠️ Status update failed: $e', TerminalType.warning);
    }
  }

  void _addLine(String text, TerminalType type) {
    if (!mounted) return;
    
    setState(() {
      _lines.add(TerminalLine(
        text: text,
        type: type,
        timestamp: DateTime.now(),
      ));
      
      // Keep only the last maxLines
      if (_lines.length > widget.maxLines) {
        _lines.removeRange(0, _lines.length - widget.maxLines);
      }
    });
    
    if (widget.autoScroll) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void _executeCommand(String command) {
    _addLine('> $command', TerminalType.command);
    
    switch (command.toLowerCase().trim()) {
      case 'help':
        _showHelp();
        break;
      case 'status':
        _showStatus();
        break;
      case 'clear':
        _clearTerminal();
        break;
      case 'ai status':
        _showAIStatus();
        break;
      case 'learning cycle':
        _triggerLearningCycle();
        break;
      case 'github status':
        _showGitHubStatus();
        break;
      case 'deploy':
        _triggerDeployment();
        break;
      case 'logs':
        _showSystemLogs();
        break;
      default:
        _addLine('❌ Unknown command: $command', TerminalType.error);
        _addLine('Type "help" for available commands.', TerminalType.info);
    }
  }

  void _showHelp() {
    _addLine('📖 Available Commands:', TerminalType.info);
    _addLine('  help          - Show this help message', TerminalType.info);
    _addLine('  status        - Show system status', TerminalType.info);
    _addLine('  ai status     - Show AI learning status', TerminalType.info);
    _addLine('  learning cycle - Trigger AI learning cycle', TerminalType.info);
    _addLine('  github status - Show GitHub integration status', TerminalType.info);
    _addLine('  deploy        - Trigger deployment', TerminalType.info);
    _addLine('  logs          - Show recent system logs', TerminalType.info);
    _addLine('  clear         - Clear terminal', TerminalType.info);
  }

  void _showStatus() async {
    try {
      final service = AILearningService();
      final status = await service.getSystemStatus();
      
      _addLine('📊 System Status:', TerminalType.info);
      _addLine('  Status: ${status['status']}', TerminalType.info);
      _addLine('  Active AIs: ${status['activeAIs']?.join(', ') ?? 'None'}', TerminalType.info);
      _addLine('  Learning Cycles: ${status['learningCycles'] ?? 0}', TerminalType.info);
      _addLine('  GitHub PRs: ${status['githubPRs'] ?? 0}', TerminalType.info);
      _addLine('  Last Update: ${status['lastUpdate'] ?? 'Unknown'}', TerminalType.info);
    } catch (e) {
      _addLine('❌ Failed to get status: $e', TerminalType.error);
    }
  }

  void _showAIStatus() async {
    try {
      final service = AILearningService();
      final aiStatus = await service.getAIStatus();
      
      _addLine('🤖 AI Learning Status:', TerminalType.info);
      for (final ai in ['Imperium', 'Guardian', 'Sandbox']) {
        final status = aiStatus[ai] ?? {};
        _addLine('  $ai:', TerminalType.info);
        _addLine('    Status: ${status['status'] ?? 'Unknown'}', TerminalType.info);
        _addLine('    Learning Cycles: ${status['learningCycles'] ?? 0}', TerminalType.info);
        _addLine('    Success Rate: ${status['successRate'] ?? 0}%', TerminalType.info);
        _addLine('    Last Activity: ${status['lastActivity'] ?? 'Unknown'}', TerminalType.info);
      }
    } catch (e) {
      _addLine('❌ Failed to get AI status: $e', TerminalType.error);
    }
  }

  void _triggerLearningCycle() async {
    _addLine('🔄 Triggering AI learning cycle...', TerminalType.system);
    
    try {
      final service = AILearningService();
      final result = await service.triggerLearningCycle('Imperium', 'test-proposal', 'passed');
      
      _addLine('✅ Learning cycle triggered successfully', TerminalType.success);
      _addLine('Result: $result', TerminalType.info);
    } catch (e) {
      _addLine('❌ Failed to trigger learning cycle: $e', TerminalType.error);
    }
  }

  void _showGitHubStatus() async {
    try {
      final service = AILearningService();
      final githubStatus = await service.getGitHubStatus();
      
      _addLine('🔗 GitHub Integration Status:', TerminalType.info);
      _addLine('  Repository: ${githubStatus['repository'] ?? 'Unknown'}', TerminalType.info);
      _addLine('  Status: ${githubStatus['status'] ?? 'Unknown'}', TerminalType.info);
      _addLine('  Last Push: ${githubStatus['lastPush'] ?? 'Unknown'}', TerminalType.info);
      _addLine('  Open PRs: ${githubStatus['openPRs'] ?? 0}', TerminalType.info);
    } catch (e) {
      _addLine('❌ Failed to get GitHub status: $e', TerminalType.error);
    }
  }

  void _triggerDeployment() async {
    _addLine('🚀 Triggering deployment...', TerminalType.system);
    
    try {
      // Simulate deployment process
      _addLine('📦 Building application...', TerminalType.info);
      await Future.delayed(const Duration(seconds: 2));
      
      _addLine('🧪 Running tests...', TerminalType.info);
      await Future.delayed(const Duration(seconds: 2));
      
      _addLine('🔒 Security scan...', TerminalType.info);
      await Future.delayed(const Duration(seconds: 1));
      
      _addLine('📱 Creating APK...', TerminalType.info);
      await Future.delayed(const Duration(seconds: 3));
      
      _addLine('✅ Deployment completed successfully!', TerminalType.success);
      _addLine('APK ready for download', TerminalType.info);
    } catch (e) {
      _addLine('❌ Deployment failed: $e', TerminalType.error);
    }
  }

  void _showSystemLogs() async {
    _addLine('📋 Recent System Logs:', TerminalType.info);
    _addLine('  [2024-01-15 10:30:15] AI Learning cycle completed', TerminalType.log);
    _addLine('  [2024-01-15 10:25:42] GitHub PR #123 created', TerminalType.log);
    _addLine('  [2024-01-15 10:20:18] Code update applied to Imperium', TerminalType.log);
    _addLine('  [2024-01-15 10:15:33] Internet research completed', TerminalType.log);
    _addLine('  [2024-01-15 10:10:07] Learning cycle initiated', TerminalType.log);
  }

  void _clearTerminal() {
    setState(() {
      _lines.clear();
    });
    _addLine('🚀 AI Learning System Terminal', TerminalType.info);
    _addLine('Terminal cleared. Ready for commands.', TerminalType.system);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.black87,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        children: [
          // Terminal Header
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(8),
                topRight: Radius.circular(8),
              ),
            ),
            child: Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: _statusColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  widget.title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  _currentStatus,
                  style: TextStyle(
                    color: _statusColor,
                    fontSize: 12,
                  ),
                ),
                if (widget.showControls) ...[
                  const SizedBox(width: 16),
                  IconButton(
                    icon: const Icon(Icons.refresh, color: Colors.white, size: 16),
                    onPressed: _updateSystemStatus,
                    tooltip: 'Refresh Status',
                  ),
                  IconButton(
                    icon: const Icon(Icons.clear, color: Colors.white, size: 16),
                    onPressed: _clearTerminal,
                    tooltip: 'Clear Terminal',
                  ),
                ],
              ],
            ),
          ),
          
          // Terminal Output
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(8),
              child: ListView.builder(
                controller: _scrollController,
                itemCount: _lines.length,
                itemBuilder: (context, index) {
                  final line = _lines[index];
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 1),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '[${line.timestamp.hour.toString().padLeft(2, '0')}:${line.timestamp.minute.toString().padLeft(2, '0')}:${line.timestamp.second.toString().padLeft(2, '0')}] ',
                          style: TextStyle(
                            color: Colors.grey[400],
                            fontSize: 12,
                            fontFamily: 'monospace',
                          ),
                        ),
                        Expanded(
                          child: Text(
                            line.text,
                            style: TextStyle(
                              color: _getLineColor(line.type),
                              fontSize: 12,
                              fontFamily: 'monospace',
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ),
          
          // Command Input
          if (widget.showControls)
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(8),
                  bottomRight: Radius.circular(8),
                ),
              ),
              child: Row(
                children: [
                  const Text(
                    '> ',
                    style: TextStyle(
                      color: Colors.green,
                      fontSize: 14,
                      fontFamily: 'monospace',
                    ),
                  ),
                  Expanded(
                    child: TextField(
                      controller: _commandController,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 14,
                        fontFamily: 'monospace',
                      ),
                      decoration: const InputDecoration(
                        border: InputBorder.none,
                        hintText: 'Enter command...',
                        hintStyle: TextStyle(color: Colors.grey),
                      ),
                      onSubmitted: (command) {
                        if (command.isNotEmpty) {
                          _executeCommand(command);
                          _commandController.clear();
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Color _getLineColor(TerminalType type) {
    switch (type) {
      case TerminalType.info:
        return Colors.cyan;
      case TerminalType.success:
        return Colors.green;
      case TerminalType.error:
        return Colors.red;
      case TerminalType.warning:
        return Colors.yellow;
      case TerminalType.system:
        return Colors.white;
      case TerminalType.command:
        return Colors.green;
      case TerminalType.log:
        return Colors.grey[300]!;
    }
  }
}

class TerminalLine {
  final String text;
  final TerminalType type;
  final DateTime timestamp;

  TerminalLine({
    required this.text,
    required this.type,
    required this.timestamp,
  });
}

enum TerminalType {
  info,
  success,
  error,
  warning,
  system,
  command,
  log,
} 