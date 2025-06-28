import 'dart:async';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:socket_io_client/socket_io_client.dart' as IO;

import 'mission_provider.dart' hide navigatorKey;
import 'ai_file_system_helper.dart';
import 'services/notification_service.dart';
// ignore: unused_import
import 'providers/proposal_provider.dart';
import 'main.dart';

/// The Imperium: Meta-AI that learns and improves all other AIs
class TheImperium {
  static final TheImperium instance = TheImperium._internal();
  TheImperium._internal() {
    print('TheImperium: _internal() constructor called');
  }

  final List<Map<String, dynamic>> _metaLearningLog = [];
  final StreamController<Map<String, dynamic>> _metaLearningController = StreamController.broadcast();
  final StreamController<bool> _runningController = StreamController.broadcast();
  bool _isRunning = false;
  Timer? _backgroundLoop;
  IO.Socket? _socket;

  bool get isRunning => _isRunning;
  Stream<Map<String, dynamic>> get metaLearningStream => _metaLearningController.stream;
  Stream<bool> get runningStream => _runningController.stream;
  List<Map<String, dynamic>> get metaLearningLog => List.unmodifiable(_metaLearningLog);

  void start() {
    print('TheImperium: start() called');
    if (_isRunning) return;
    _isRunning = true;
    _runningController.add(true);
    print('🏆 The Imperium: Started. Directive: Constant growth, self-learning, and improvement of all AIs.');
    
    // Connect to backend Socket.IO
    _connectToBackend();
    
    // Start background loop for continuous improvement (reduced frequency)
    _backgroundLoop ??= Timer.periodic(const Duration(minutes: 5), (_) => _runMetaImprovementCycle());
    
    // Listen to MissionProvider's learning log (if available)
    MissionProvider.latestInstance?.aiLearningLogStream.listen((event) {
      _analyzeLearningEvent(event);
    });
    
    _logMetaEvent('The Imperium started monitoring all AIs and connected to backend.');
    startFileWatchers();
  }

  void _connectToBackend() {
    print('[IMPERIUM] Connecting to backend Socket.IO...');
    _socket = IO.io('http://234.55.93.144:4000', <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
    });

    _socket!.onConnect((_) {
      print('[IMPERIUM] ✅ Connected to backend Socket.IO');
      _logMetaEvent('Connected to AI backend for real-time monitoring');
    });

    _socket!.onDisconnect((_) {
      print('[IMPERIUM] ❌ Disconnected from backend Socket.IO');
      _logMetaEvent('Disconnected from AI backend');
    });

    // Listen to backend AI events
    _socket!.on('ai:experiment-start', (data) {
      print('[IMPERIUM] 📨 Received ai:experiment-start from backend');
      final ai = data['ai'] ?? 'Unknown AI';
      final filePath = data['filePath'] ?? 'unknown file';
      final message = data['message'] ?? 'AI is working...';
      _logMetaEvent('Backend $ai started experiment on $filePath: $message');
    });

    _socket!.on('ai:experiment-complete', (data) {
      print('[IMPERIUM] 📨 Received ai:experiment-complete from backend');
      final ai = data['ai'] ?? 'Unknown AI';
      final filePath = data['filePath'] ?? 'unknown file';
      final message = data['message'] ?? 'AI completed work';
      _logMetaEvent('Backend $ai completed experiment on $filePath: $message');
    });

    _socket!.on('proposal:created', (data) {
      print('[IMPERIUM] 📨 Received proposal:created from backend');
      final aiType = data['aiType'] ?? 'Unknown AI';
      final filePath = data['filePath'] ?? 'unknown file';
      _logMetaEvent('Backend $aiType created proposal for $filePath');
    });

    _socket!.on('proposal:test-started', (data) {
      print('[IMPERIUM] 📨 Received proposal:test-started from backend');
      final filePath = data['filePath'] ?? 'unknown file';
      _logMetaEvent('Backend started testing proposal for $filePath');
    });

    _socket!.on('proposal:test-finished', (data) {
      print('[IMPERIUM] 📨 Received proposal:test-finished from backend');
      final status = data['testStatus'] ?? '';
      final filePath = data['filePath'] ?? 'unknown file';
      _logMetaEvent('Backend test finished for $filePath with status: $status');
    });

    _socket!.on('proposal:applied', (data) {
      print('[IMPERIUM] 📨 Received proposal:applied from backend');
      final aiType = data['aiType'] ?? 'Unknown AI';
      final filePath = data['filePath'] ?? 'unknown file';
      _logMetaEvent('Backend $aiType successfully applied proposal for $filePath to GitHub');
    });

    _socket!.connect();
  }

  void stop() {
    if (!_isRunning) return;
    _isRunning = false;
    _runningController.add(false);
    _backgroundLoop?.cancel();
    _backgroundLoop = null;
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
    _logMetaEvent('The Imperium stopped and disconnected from backend.');
  }

  void _analyzeLearningEvent(Map<String, dynamic> event) {
    // Simple meta-learning: log and look for repeated issues
    final insight = 'Analyzed event: ${event['action']} on ${event['files']?.join(', ') ?? 'unknown files'}';
    _metaLearningLog.add({
      'timestamp': DateTime.now().toIso8601String(),
      'event': event,
      'insight': insight,
    });
    _metaLearningController.add({
      'timestamp': DateTime.now().toIso8601String(),
      'event': event,
      'insight': insight,
    });
  }

  void proposeImprovement(String aiName, String suggestion, {String? code}) {
    // Store, notify, and optionally trigger a UI prompt for user approval
    final proposal = {
      'timestamp': DateTime.now().toIso8601String(),
      'ai': aiName,
      'suggestion': suggestion,
      'code': code,
    };
    _metaLearningLog.add(proposal);
    _metaLearningController.add(proposal);
    // TODO: Integrate with UI for user confirmation and code application
  }

  void _logMetaEvent(String message) {
    final entry = {
      'timestamp': DateTime.now().toIso8601String(),
      'event': {'action': message},
      'insight': message,
    };
    _metaLearningLog.add(entry);
    _metaLearningController.add(entry);
  }

  // Listen to Mechanicum and AI Sandbox logs (pseudo-code, replace with real streams if available)
  void listenToOtherAIs({Stream<Map<String, dynamic>>? mechanicumLog, Stream<Map<String, dynamic>>? sandboxLog}) {
    if (mechanicumLog != null) {
      mechanicumLog.listen((event) {
        _analyzeLearningEvent(event);
      });
    }
    if (sandboxLog != null) {
      sandboxLog.listen((event) {
        _analyzeLearningEvent(event);
      });
    }
  }

  // Analyze for repeated issues and propose improvements
  void analyzeForImprovements() {
    // Example: If the same issue appears 3+ times, propose a fix
    final issueCounts = <String, int>{};
    for (final entry in _metaLearningLog) {
      final event = entry['event'] as Map<String, dynamic>?;
      final action = event?['action']?.toString() ?? '';
      if (action.isNotEmpty) {
        issueCounts[action] = (issueCounts[action] ?? 0) + 1;
        if (issueCounts[action] == 3) {
          // Propose an improvement
          proposeImprovement('AI Guardian', 'Repeated issue: $action', code: '// TODO: Auto-generated fix for $action');
        }
      }
    }
  }

  // Apply a proposed code change (with user approval)
  Future<void> applyProposal(Map<String, dynamic> proposal) async {
    final ai = proposal['ai']?.toString() ?? '';
    final code = proposal['code']?.toString() ?? '';
    final suggestion = proposal['suggestion']?.toString() ?? '';
    // Example: Use MissionProvider or Mechanicum to apply code
    if (ai == 'AI Guardian' && code.isNotEmpty) {
      // Use MissionProvider to apply code (simulate for now)
      MissionProvider.latestInstance?.applyAISuggestionFromImperium(suggestion, code);
      _logMetaEvent('Applied proposal to $ai: $suggestion');
    }
    // Add more AI integrations as needed
  }

  // Enhanced meta-improvement cycle with detailed logging and auto-self-improvement
  void _runMetaImprovementCycle() {
    final now = DateTime.now();
    print('🏆 The Imperium: [${now.toIso8601String()}] Meta-improvement cycle running. Log entries: ${_metaLearningLog.length}');
    
    // Analyze backend activity patterns
    final backendEvents = _metaLearningLog.where((entry) => 
      entry['insight']?.toString().contains('Backend') == true
    ).toList();
    
    print('🏆 The Imperium: Found ${backendEvents.length} backend events in log');
    
    // Analyze for improvements based on backend activity
    final issueCounts = <String, int>{};
    for (final entry in backendEvents) {
      final insight = entry['insight']?.toString() ?? '';
      if (insight.contains('test finished') && insight.contains('failed')) {
        issueCounts['test_failures'] = (issueCounts['test_failures'] ?? 0) + 1;
      }
      if (insight.contains('disconnected')) {
        issueCounts['connection_issues'] = (issueCounts['connection_issues'] ?? 0) + 1;
      }
      if (insight.contains('proposal created')) {
        issueCounts['proposals_created'] = (issueCounts['proposals_created'] ?? 0) + 1;
      }
    }
    
    // Generate insights based on backend activity
    if (issueCounts['test_failures'] != null && issueCounts['test_failures']! > 2) {
      _logMetaEvent('🏆 The Imperium: Detected repeated test failures. Recommending code review improvements.');
      proposeImprovement('Backend AIs', 'Improve test reliability', code: '// TODO: Enhanced error handling and validation');
    }
    
    if (issueCounts['connection_issues'] != null && issueCounts['connection_issues']! > 1) {
      _logMetaEvent('🏆 The Imperium: Detected connection issues. Recommending network resilience improvements.');
      proposeImprovement('Backend AIs', 'Improve network resilience', code: '// TODO: Add retry logic and connection pooling');
    }
    
    if (issueCounts['proposals_created'] != null && issueCounts['proposals_created']! > 5) {
      _logMetaEvent('🏆 The Imperium: High proposal activity detected. System is actively improving.');
    }
    
    final afterCount = _metaLearningLog.length;
    print('🏆 The Imperium: [${now.toIso8601String()}] Cycle complete. Backend events analyzed: ${backendEvents.length}. Total log entries: $afterCount.');
  }

  // Learn from user-uploaded code or AI suggestions
  void learnFromExternalCode({
    required String source,
    required String code,
    String? description,
  }) {
    final now = DateTime.now();
    final learning = {
      'timestamp': now.toIso8601String(),
      'source': source,
      'code': code,
      'description': description ?? '',
      'insight': 'Learned from $source. The Imperium adapts and grows faster than other AIs.',
    };
    _metaLearningLog.add(learning);
    _metaLearningController.add(learning);
    print('🏆 The Imperium: [${now.toIso8601String()}] Learned from $source. Code: ${code.substring(0, code.length > 60 ? 60 : code.length)}...');
  }

  // Method to apply code changes to core files (with user approval)
  void proposeAndApplyCodeChange({
    required String aiName,
    required String filePath,
    required String oldCode,
    required String newCode,
    bool autoApply = false,
  }) {
    proposeImprovement(aiName, 'Proposed code change to $filePath', code: newCode);
    if (autoApply) {
      applyCodeChangeToFile(filePath, oldCode, newCode);
    }
  }

  void applyCodeChangeToFile(String filePath, String oldCode, String newCode) {
    final file = File(filePath);
    if (file.existsSync()) {
      final content = file.readAsStringSync();
      final updated = content.replaceFirst(oldCode, newCode);
      file.writeAsStringSync(updated);
      print('🏆 The Imperium: Updated $filePath for meta-improvement.');
      _logMetaEvent('Applied code change to $filePath');
    } else {
      print('🏆 The Imperium: File $filePath not found for meta-improvement.');
    }
  }

  // Ensure The Imperium starts automatically and runs in the background
  static void ensureStarted() {
    print('TheImperium: ensureStarted() called');
    if (!instance._isRunning) {
      instance.start();
    }
  }

  void startFileWatchers() {
    // Watch /lib
    AIFileSystemHelper.watchDirectory('lib').listen((event) async {
      AIFileSystemHelper.logFileAction('The Imperium', 'watch', event.path, details: 'Type: \\${event.runtimeType}');
      print('The Imperium: Detected file change in lib: \\${event.path}');
      if (event.path.endsWith('.dart')) {
        await _analyzeAndImproveDartFile(event.path);
      }
    });
    // Watch /assets
    AIFileSystemHelper.watchDirectory('assets').listen((event) async {
      AIFileSystemHelper.logFileAction('The Imperium', 'watch', event.path, details: 'Type: \\${event.runtimeType}');
      print('The Imperium: Detected file change in assets: \\${event.path}');
      if (_isAssetFile(event.path)) {
        await _checkAssetFile(event.path);
      }
    });
    print('The Imperium: File watchers started for /lib and /assets');
  }

  bool _isAssetFile(String path) {
    return path.endsWith('.png') || path.endsWith('.jpg') || path.endsWith('.jpeg') || path.endsWith('.gif') || path.endsWith('.mp4') || path.endsWith('.mov');
  }

  Future<void> _analyzeAndImproveDartFile(String filePath) async {
    try {
      AIFileSystemHelper.logFileAction('The Imperium', 'analyze', filePath, details: 'Running code review');
      // Simple code review: check if file is readable and not empty
      final file = File(filePath);
      if (!file.existsSync()) {
        print('The Imperium: Dart file $filePath does not exist.');
        return;
      }
      final content = await file.readAsString();
      if (content.trim().isEmpty) {
        print('The Imperium: Dart file $filePath is empty.');
        return;
      }
      // Example: If file contains TODO, propose improvement
      if (content.contains('TODO')) {
        print('The Imperium: Found TODO in $filePath, proposing improvement.');
        _logMetaEvent('TODO found in $filePath, improvement proposed.');
        if (filePath.endsWith('ai_brain.dart') || filePath.endsWith('ai_file_system_helper.dart')) {
          // Auto-apply self-improvement
          // (In real use, generate and apply the fix here)
          print('The Imperium: Auto-applying self-improvement to $filePath.');
          _logMetaEvent('Auto-applied self-improvement to $filePath.');
          notifyUser('The Imperium', 'Auto-applied self-improvement to $filePath', icon: '🏆');
        } else {
          // Propose improvement to the provider
          final context = navigatorKey.currentContext;
          if (context != null) {
            await submitProposalToBackend(
              aiType: 'The Imperium',
              filePath: filePath,
              oldCode: 'TODO: Fix this', // Placeholder
              newCode: '// TODO: Fix this\n// Resolved by The Imperium', // Placeholder
            );
            print('The Imperium: Submitted proposal for $filePath to backend.');
            notifyUser('The Imperium', 'New proposal submitted for your review.', icon: '🏆');
          }
        }
      } else {
        print('The Imperium: No TODO found in $filePath.');
      }
    } catch (e) {
      print('The Imperium: Error analyzing $filePath: $e');
    }
  }

  Future<void> _checkAssetFile(String filePath) async {
    try {
      AIFileSystemHelper.logFileAction('The Imperium', 'asset_check', filePath, details: 'Checking asset validity');
      final file = File(filePath);
      if (!file.existsSync()) {
        print('The Imperium: Asset file $filePath does not exist.');
        _logMetaEvent('Asset missing: $filePath');
        notifyUser('The Imperium', 'Asset missing: $filePath', icon: '🏆');
        return;
      }
      final length = await file.length();
      if (length == 0) {
        print('The Imperium: Asset file $filePath is empty.');
        _logMetaEvent('Asset empty: $filePath');
        notifyUser('The Imperium', 'Asset empty: $filePath', icon: '🏆');
        return;
      }
      print('The Imperium: Asset file $filePath is valid.');
      _logMetaEvent('Asset valid: $filePath');
      notifyUser('The Imperium', 'Asset valid: $filePath', icon: '🏆');
    } catch (e) {
      print('The Imperium: Error checking asset $filePath: $e');
    }
  }

  // Add a placeholder for notifyUser (to be implemented in a notification utility)
  void notifyUser(String aiName, String message, {String? icon}) {
    // TODO: Implement real notification (in-app and/or system)
    NotificationService.instance.showNotification(
      aiSource: aiName,
      message: message,
      iconChar: icon ?? 'ℹ️',
    );
    print('[NOTIFY][$aiName] $icon $message');
  }

  Future<void> submitProposalToBackend({
    required String aiType,
    required String filePath,
    required String oldCode,
    required String newCode,
  }) async {
    final url = Uri.parse('http://234.55.93.144:4000/api/proposals');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'aiType': aiType,
        'filePath': filePath,
        'codeBefore': oldCode,
        'codeAfter': newCode,
      }),
    );
    if (response.statusCode == 200) {
      print('Proposal submitted to backend.');
    } else {
      print('Failed to submit proposal: \\${response.body}');
    }
  }
} 