import 'dart:async';
import 'package:flutter/foundation.dart';
import '../services/ai_learning_service.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/network_config.dart';
import 'package:flutter/widgets.dart';
import '../services/network_config.dart';

// Provider for managing AI learning state and data
class AILearningProvider extends ChangeNotifier {
  final AILearningService _learningService = AILearningService();

  // Connection state tracking
  static bool _isBackendAvailable = false;
  static int _consecutiveFailures = 0;
  static const int _maxFailures = 999; // Always try real mode

  // Public getter for backend availability
  static bool get isBackendAvailable => _isBackendAvailable;

  // Learning data
  Map<String, dynamic> _learningData = {};
  Map<String, dynamic> _learningMetrics = {};
  Map<String, List<Map<String, dynamic>>> _debugLogs = {};

  // Enhanced learning data
  List<Map<String, dynamic>> _recentLearning = [];
  List<Map<String, dynamic>> _weeklyTrends = [];
  List<Map<String, dynamic>> _topPatterns = [];
  int _totalPatterns = 0;
  String _lastUpdated = '';
  double _learningProgress = 0.0;
  int _totalApplied = 0;
  double _averageSuccessRate = 0.0;

  // Stream subscriptions
  StreamSubscription<Map<String, dynamic>>? _learningUpdateSubscription;
  StreamSubscription<String>? _aiLearningEventSubscription;
  StreamSubscription<Map<String, dynamic>>? _debugOutputSubscription;

  // Polling timer for real-time updates
  Timer? _pollingTimer;

  // Getters
  Map<String, dynamic> get learningData => Map.unmodifiable(_learningData);
  Map<String, dynamic> get learningMetrics =>
      Map.unmodifiable(_learningMetrics);
  Map<String, List<Map<String, dynamic>>> get debugLogs =>
      Map.unmodifiable(_debugLogs);

  // Enhanced learning getters
  List<Map<String, dynamic>> get recentLearning =>
      List.unmodifiable(_recentLearning);
  List<Map<String, dynamic>> get weeklyTrends =>
      List.unmodifiable(_weeklyTrends);
  List<Map<String, dynamic>> get topPatterns => List.unmodifiable(_topPatterns);
  int get totalPatterns => _totalPatterns;
  String get lastUpdated => _lastUpdated;
  double get learningProgress => _learningProgress;
  int get totalApplied => _totalApplied;
  double get averageSuccessRate => _averageSuccessRate;

  Map<String, dynamic> _aiLearningStatus = {};
  Map<String, dynamic> get aiLearningStatus => _aiLearningStatus;

  List<Map<String, dynamic>> _debugLog = [];
  List<Map<String, dynamic>> get debugLog => List.unmodifiable(_debugLog);

  Map<String, dynamic> _quotaStatus = {};
  bool _isLoading = false;

  void _stopAutonomousPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
    print(
      '[AI_LEARNING_PROVIDER] 🛑 Autonomous polling stopped due to AI operations not allowed',
    );
  }

  void _startAutonomousPolling() {
    if (_pollingTimer != null) return; // Already polling
    _pollingTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      // Always run in mock mode, otherwise check operational hours
      // Always allow operations now that chaos/warp is removed
      await _fetchAIStatus();
      await _fetchLearningData();
      await _fetchLearningMetrics();
      // Check backend connectivity and update status
      final healthy = await checkBackendConnectivity();
      if (healthy && !_isBackendAvailable) {
        print(
          '[AI_LEARNING_PROVIDER] ✅ Backend healthy again, updating status.',
        );
        _isBackendAvailable = true;
        notifyListeners();
        // Immediately fetch real data
        await _fetchAIStatus();
        await _fetchLearningData();
        await _fetchLearningMetrics();
      }
    });
    print(
      '[AI_LEARNING_PROVIDER] 🔄 Started autonomous polling for real-time updates (every 30 seconds)',
    );
  }

  AILearningProvider() {
    // Start automatically - don't wait for user interaction
    print(
      '[AI_LEARNING_PROVIDER] 🧠 AI Learning Provider created - starting autonomous operation',
    );
    // Initialize immediately
    WidgetsBinding.instance.addPostFrameCallback((_) {
      initialize();
    });
  }

  void initialize() async {
    print('[AI_LEARNING_PROVIDER] 🧠 Initializing AI learning provider...');

    // Initialize the learning service
    await _learningService.initialize();

    // Always start autonomous operation - don't depend on ChaosWarpProvider
    _fetchAIStatus();
    _fetchLearningData();
    _fetchLearningMetrics();
    _startAutonomousPolling();

    // Subscribe to learning updates
    _learningUpdateSubscription = _learningService.learningUpdateStream.listen((
      update,
    ) {
      print(
        '[AI_LEARNING_PROVIDER] 📊 Learning update received: ${update['aiType']}',
      );

      // Refresh data from backend
      _fetchAIStatus();
      _fetchLearningData();
      _fetchLearningMetrics();
    });

    // Subscribe to AI learning events
    _aiLearningEventSubscription = _learningService.aiLearningEventStream
        .listen((event) {
          print('[AI_LEARNING_PROVIDER] 🎯 AI learning event: $event');
          // Events are handled by the service notifications
        });

    // Subscribe to debug output
    _debugOutputSubscription = _learningService.debugOutputStream.listen((
      debugOutput,
    ) {
      print(
        '[AI_LEARNING_PROVIDER] 🐛 Debug output: ${debugOutput['aiType']} - ${debugOutput['message']}',
      );

      // Refresh debug log from backend
      fetchDebugLog();
    });

    print(
      '[AI_LEARNING_PROVIDER] ✅ AI learning provider initialized and running autonomously',
    );
  }

  // Fetch AI status from backend (public wrapper)
  Future<void> fetchAIStatus() async {
    // Always allow operations now that chaos/warp is removed
    await _fetchAIStatus();
  }

  // Fetch learning data from backend (public wrapper)
  Future<void> fetchLearningData() async {
    try {
      final response = await http.get(
        Uri.parse('${NetworkConfig.apiBaseUrl}/api/learning/data'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print(
          '[AI_LEARNING_PROVIDER] 📊 Learning data fetched: ${data.toString()}',
        );

        if (data['status'] == 'success') {
          _learningData = data['learning_stats'] ?? {};
          _recentLearning = List<Map<String, dynamic>>.from(
            data['recent_learning'] ?? [],
          );
          _weeklyTrends = List<Map<String, dynamic>>.from(
            data['weekly_trends'] ?? [],
          );
          _topPatterns = List<Map<String, dynamic>>.from(
            data['top_patterns'] ?? [],
          );
          _totalPatterns = data['total_patterns'] ?? 0;
          _lastUpdated =
              data['last_updated'] ?? DateTime.now().toIso8601String();

          // Update learning progress
          _learningProgress =
              _learningData['learning_progress']?.toDouble() ?? 0.0;
          _totalApplied = _learningData['total_applied'] ?? 0;
          _averageSuccessRate =
              _learningData['average_success_rate']?.toDouble() ?? 0.0;

          print(
            '[AI_LEARNING_PROVIDER] ✅ Learning data updated: $_totalPatterns patterns, $_learningProgress% progress',
          );
        } else {
          print(
            '[AI_LEARNING_PROVIDER] ⚠️ Learning data status: ${data['status']}',
          );
        }
      } else {
        print(
          '[AI_LEARNING_PROVIDER] ❌ Failed to fetch learning data: ${response.statusCode}',
        );
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching learning data: $e');
    }

    notifyListeners();
  }

  // Fetch learning metrics from backend (public wrapper)
  Future<void> fetchLearningMetrics() async {
    // Always allow operations now that chaos/warp is removed
    await _fetchLearningMetrics();
  }

  // Fetch AI status from backend
  Future<void> _fetchAIStatus() async {
    // Skip health check here since it's handled by the polling timer
    try {
      print(
        '[AI_LEARNING_PROVIDER] 🔄 Fetching AI status from ${NetworkConfig.backendUrl}/api/imperium/dashboard',
      );

      // Add timeout for Android network requests
      final response = await http
          .get(
            Uri.parse('${NetworkConfig.backendUrl}/api/imperium/dashboard'),
            headers: {
              'Content-Type': 'application/json',
              'User-Agent': 'LVL_UP_Flutter_App',
            },
          )
          .timeout(NetworkConfig.requestTimeout);

      print(
        '[AI_LEARNING_PROVIDER] 📡 AI status response: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final newStatus = jsonDecode(response.body);
        print('[AI_LEARNING_PROVIDER] 📊 Received AI status: $newStatus');
        _handleBackendSuccess(); // Mark backend as available

        if (!mapEquals(_aiLearningStatus, newStatus)) {
          _aiLearningStatus = newStatus;
          print(
            '[AI_LEARNING_PROVIDER] 🔄 AI status updated: $_aiLearningStatus',
          );
          notifyListeners();
        }
      } else {
        print(
          '[AI_LEARNING_PROVIDER] ❌ AI status failed: ${response.statusCode} - ${response.body}',
        );
        _handleBackendFailure('HTTP ${response.statusCode}');
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching AI status: $e');
      _handleBackendFailure(e.toString());
      // Don't throw error, just log it to prevent app crashes
    }
  }

  // Fetch learning data from backend
  Future<void> _fetchLearningData() async {
    // Always use real data - no mock mode
    try {
      print('Requesting: ${NetworkConfig.backendUrl}/api/imperium/agents');
      final response = await http
          .get(
            Uri.parse('${NetworkConfig.backendUrl}/api/imperium/agents'),
            headers: {
              'Content-Type': 'application/json',
              'User-Agent': 'LVL_UP_Flutter_App',
            },
          )
          .timeout(NetworkConfig.requestTimeout);

      print(
        '[AI_LEARNING_PROVIDER] 📡 Learning data response: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final newData = jsonDecode(response.body);
        print(
          '[AI_LEARNING_PROVIDER] 📊 Received learning data keys: ${newData.keys.toList()}',
        );
        if (!mapEquals(_learningData, newData)) {
          _learningData = newData;
          print('[AI_LEARNING_PROVIDER] 🔄 Learning data updated');
          notifyListeners();
        }
      } else {
        print(
          '[AI_LEARNING_PROVIDER] ❌ Learning data failed: ${response.statusCode} - ${response.body}',
        );
        // Use empty data instead of mock data
        _learningData = {};
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching learning data: $e');
      // Use empty data instead of mock data
      _learningData = {};
      notifyListeners();
    }
  }

  // Fetch learning metrics from backend
  Future<void> _fetchLearningMetrics() async {
    // Always use real data - no mock mode
    try {
      print(
        '[AI_LEARNING_PROVIDER] 🔄 Fetching learning metrics from ${NetworkConfig.backendUrl}/api/imperium/dashboard',
      );

      final response = await http
          .get(
            Uri.parse('${NetworkConfig.backendUrl}/api/imperium/dashboard'),
            headers: {
              'Content-Type': 'application/json',
              'User-Agent': 'LVL_UP_Flutter_App',
            },
          )
          .timeout(NetworkConfig.requestTimeout);

      print(
        '[AI_LEARNING_PROVIDER] 📡 Learning metrics response: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final newMetrics = jsonDecode(response.body);
        print(
          '[AI_LEARNING_PROVIDER] 📊 Received learning metrics keys: ${newMetrics.keys.toList()}',
        );
        if (!mapEquals(_learningMetrics, newMetrics)) {
          _learningMetrics = newMetrics;
          print('[AI_LEARNING_PROVIDER] 🔄 Learning metrics updated');
          notifyListeners();
        }
      } else {
        print(
          '[AI_LEARNING_PROVIDER] ❌ Learning metrics failed: ${response.statusCode} - ${response.body}',
        );
        // Use empty metrics instead of mock data
        _learningMetrics = {};
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching learning metrics: $e');
      // Use empty metrics instead of mock data
      _learningMetrics = {};
      notifyListeners();
    }
  }

  // Reset learning state for an AI
  Future<bool> resetLearningState(String aiType) async {
    // Always use real data - no mock mode
    try {
      print('[AI_LEARNING_PROVIDER] 🔄 Resetting learning state for $aiType');

      final response = await http.post(
        Uri.parse('${NetworkConfig.backendUrl}/api/proposals'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({}),
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        print(
          '[AI_LEARNING_PROVIDER] ✅ Learning state reset for $aiType: ${result['message']}',
        );

        // Refresh AI status
        await _fetchAIStatus();

        return true;
      } else {
        print(
          '[AI_LEARNING_PROVIDER] ❌ Failed to reset learning state: ${response.statusCode}',
        );
        return false;
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error resetting learning state: $e');
      return false;
    }
  }

  // Fetch debug log from backend
  Future<void> fetchDebugLog() async {
    try {
      final response = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/learning/data'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _debugLog = List<Map<String, dynamic>>.from(data['logs'] ?? []);
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] Error fetching debug log: $e');
    }
  }

  // Get recent debug entries (last 20)
  List<Map<String, dynamic>> getRecentDebugEntries() {
    return _debugLog.take(20).toList();
  }

  // Get debug entries for a specific AI
  List<Map<String, dynamic>> getDebugEntriesForAI(String aiType) {
    return _debugLog
        .where(
          (entry) =>
              entry['message']?.toString().contains(aiType.toUpperCase()) ==
              true,
        )
        .toList();
  }

  // Check if an AI is currently learning
  bool isAILearning(String aiType) {
    return _aiLearningStatus[aiType]?['isLearning'] == true;
  }

  // Get learning state summary
  Map<String, bool> getLearningStateSummary() {
    final summary = <String, bool>{};
    for (final aiType in ['Imperium', 'Sandbox', 'Guardian']) {
      summary[aiType] = isAILearning(aiType);
    }
    return summary;
  }

  // Learn from a proposal approval/rejection
  Future<void> learnFromProposal(
    dynamic proposal,
    String action,
    String? feedbackReason,
  ) async {
    print('[AI_LEARNING_PROVIDER] 🧠 Learning from proposal: $action');

    try {
      await _learningService.learnFromProposal(
        proposal,
        action,
        feedbackReason,
      );

      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning from proposal completed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error learning from proposal: $e');
    }
  }

  // Learn from backend test results
  Future<void> learnFromBackendTestResult(
    String aiType,
    Map<String, dynamic> testData,
  ) async {
    print(
      '[AI_LEARNING_PROVIDER] 🧪 Learning from backend test result: $aiType',
    );

    try {
      await _learningService.learnFromBackendTestResult(aiType, testData);

      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print(
        '[AI_LEARNING_PROVIDER] ✅ Learning from backend test result completed',
      );
    } catch (e) {
      print(
        '[AI_LEARNING_PROVIDER] ❌ Error learning from backend test result: $e',
      );
    }
  }

  // Learn from local test results
  Future<void> learnFromTestResult(
    String aiType,
    String testType,
    String result,
    String details,
  ) async {
    print(
      '[AI_LEARNING_PROVIDER] 🧪 Learning from test result: $aiType - $testType = $result',
    );

    try {
      await _learningService.learnFromTestResult(
        aiType,
        testType,
        result,
        details,
      );

      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning from test result completed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error learning from test result: $e');
    }
  }

  // Get learning data for a specific AI
  Map<String, dynamic> getLearningDataForAI(String aiType) {
    final data = _learningData[aiType] ?? {};
    final capabilities = <String>[];
    final recentLearning = <String>[];

    // Extract capabilities from learning data
    if (data['capabilities'] != null) {
      capabilities.addAll(List<String>.from(data['capabilities']));
    }

    // Extract recent learning from experiments and suggestions
    if (data['experiments'] != null) {
      final experiments = List<Map<String, dynamic>>.from(data['experiments']);
      for (final experiment in experiments.take(3)) {
        final focus = experiment['focus'] ?? 'unknown';
        final description = experiment['description'] ?? '';
        recentLearning.add(
          'Experiment: $focus - ${description.substring(0, description.length > 50 ? 50 : description.length)}...',
        );
      }
    }

    if (data['suggestions'] != null) {
      final suggestions = List<Map<String, dynamic>>.from(data['suggestions']);
      for (final suggestion in suggestions.take(2)) {
        final issue = suggestion['issue'] ?? 'unknown';
        recentLearning.add('Suggestion: $issue');
      }
    }

    return {
      'capabilities': capabilities,
      'recentLearning': recentLearning,
      'isLearning': isAILearning(aiType),
    };
  }

  // Get all AI learning data for display
  Map<String, Map<String, dynamic>> getAllAILearningData() {
    final result = <String, Map<String, dynamic>>{};
    for (final aiType in ['Imperium', 'Sandbox', 'Guardian']) {
      result[aiType] = getLearningDataForAI(aiType);
    }
    return result;
  }

  // Get learning metrics for a specific AI
  Map<String, dynamic> getLearningMetricsForAI(String aiType) {
    return _learningMetrics[aiType] ?? {};
  }

  // Get debug log for a specific AI
  List<Map<String, dynamic>> getDebugLogForAI(String aiType) {
    return _debugLogs[aiType] ?? [];
  }

  // Get learning summary for dashboard
  Map<String, dynamic> getLearningSummary() {
    final summary = <String, dynamic>{
      'totalAIs': _learningData.length,
      'totalLessons': 0,
      'totalProposals': 0,
      'totalBackendTests': 0,
      'averageLearningScore': 0,
      'totalDebugEntries': 0,
    };

    int totalLessons = 0;
    int totalProposals = 0;
    int totalBackendTests = 0;
    int totalLearningScore = 0;
    int totalDebugEntries = 0;

    for (final aiType in _learningData.keys) {
      final data = _learningData[aiType]!;
      totalLessons += (data['lessons'] as List).length;
      totalProposals += (data['userFeedback'] as List).length;
      totalBackendTests += (data['backendTestResults'] as List).length;
      totalLearningScore += data['learningScore'] as int;
      totalDebugEntries += (data['debugLog'] as List).length;
    }

    summary['totalLessons'] = totalLessons;
    summary['totalProposals'] = totalProposals;
    summary['totalBackendTests'] = totalBackendTests;
    summary['totalDebugEntries'] = totalDebugEntries;
    summary['averageLearningScore'] =
        _learningData.isEmpty
            ? 0
            : (totalLearningScore / _learningData.length).round();

    return summary;
  }

  // Get AI performance comparison
  Map<String, dynamic> getAIPerformanceComparison() {
    final comparison = <String, dynamic>{};

    for (final aiType in _learningData.keys) {
      final metrics = _learningMetrics[aiType] ?? {};
      comparison[aiType] = {
        'learningScore': metrics['learningScore'] ?? 0,
        'successRate': metrics['successRate'] ?? 0,
        'appliedLearning': metrics['appliedLearning'] ?? 0,
        'backendTestSuccessRate': metrics['backendTestSuccessRate'] ?? 0,
        'totalProposals': metrics['totalProposals'] ?? 0,
        'backendTests': metrics['backendTests'] ?? 0,
      };
    }

    return comparison;
  }

  // Get learning trends (last 10 entries per AI)
  Map<String, List<Map<String, dynamic>>> getLearningTrends() {
    final trends = <String, List<Map<String, dynamic>>>{};

    for (final aiType in _learningData.keys) {
      final data = _learningData[aiType]!;
      final userFeedback = data['userFeedback'] as List;
      final backendTests = data['backendTestResults'] as List;

      // Combine and sort by timestamp
      final allEntries = <Map<String, dynamic>>[];
      allEntries.addAll(userFeedback.cast<Map<String, dynamic>>());
      allEntries.addAll(backendTests.cast<Map<String, dynamic>>());

      allEntries.sort((a, b) => b['timestamp'].compareTo(a['timestamp']));

      trends[aiType] = allEntries.take(10).toList();
    }

    return trends;
  }

  // Clear all learning data
  Future<void> clearLearningData() async {
    print('[AI_LEARNING_PROVIDER] 🗑️ Clearing all learning data...');

    try {
      await _learningService.clearLearningData();

      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning data cleared');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error clearing learning data: $e');
    }
  }

  // Refresh learning data
  Future<void> refreshLearningData() async {
    print('[AI_LEARNING_PROVIDER] 🔄 Refreshing learning data...');

    try {
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning data refreshed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error refreshing learning data: $e');
    }
  }

  // Simulate learning for testing
  Future<void> simulateLearning() async {
    print('[AI_LEARNING_PROVIDER] 🧪 Simulating learning events...');

    try {
      // Simulate proposal learning
      await learnFromTestResult(
        'Imperium',
        'compilation',
        'fail',
        'Syntax error in generated code',
      );
      await learnFromTestResult(
        'Sandbox',
        'dependency',
        'pass',
        'All dependencies resolved successfully',
      );
      await learnFromTestResult(
        'Guardian',
        'null_safety',
        'fail',
        'Null safety violation detected',
      );

      // Simulate backend test learning
      await learnFromBackendTestResult('Imperium', {
        'testType': 'compilation_test',
        'result': 'fail',
        'details': 'Generated code contains syntax errors',
        'filePath': 'lib/main.dart',
        'function': 'main',
      });

      await learnFromBackendTestResult('Sandbox', {
        'testType': 'dependency_test',
        'result': 'pass',
        'details': 'All package dependencies are compatible',
        'filePath': 'pubspec.yaml',
        'function': 'dependencies',
      });

      print('[AI_LEARNING_PROVIDER] ✅ Learning simulation completed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error simulating learning: $e');
    }
  }

  Map<String, dynamic> get quotaStatus => Map.unmodifiable(_quotaStatus);
  bool get isLoading => _isLoading;

  Future<void> fetchQuotaStatus() async {
    try {
      final response = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/proposals'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _quotaStatus = Map<String, dynamic>.from(data);
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] Error fetching quota status: $e');
    }
  }

  // Trigger comprehensive AI learning cycle
  Future<void> triggerLearningCycle(
    String aiType,
    String proposalId,
    String result,
  ) async {
    print('[AI_LEARNING_PROVIDER] 🎯 Triggering learning cycle for $aiType');

    try {
      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning cycle triggered successfully');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error triggering learning cycle: $e');
      rethrow;
    }
  }

  // Get learning cycle statistics
  Future<Map<String, dynamic>> getLearningCycleStats({
    String? aiType,
    int days = 30,
  }) async {
    print('[AI_LEARNING_PROVIDER] 📊 Getting learning cycle stats');

    try {
      final response = await _learningService.getLearningCycleStats(
        aiType: aiType,
        days: days,
      );
      return response;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error getting learning cycle stats: $e');
      return {};
    }
  }

  // Get GitHub repository status
  Future<Map<String, dynamic>> getGitHubStatus() async {
    print('[AI_LEARNING_PROVIDER] 🔗 Getting GitHub status');

    try {
      final response = await _learningService.getGitHubStatus();
      return response;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error getting GitHub status: $e');
      return {};
    }
  }

  // Merge AI learning pull request
  Future<bool> mergeLearningPR(String prUrl) async {
    print('[AI_LEARNING_PROVIDER] 🔄 Merging learning PR: $prUrl');

    try {
      final response = await _learningService.mergeLearningPR(prUrl);
      return response['success'] ?? false;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error merging learning PR: $e');
      return false;
    }
  }

  // Get internet learning status
  Future<Map<String, dynamic>> getInternetLearningStatus({
    String? aiType,
  }) async {
    print('[AI_LEARNING_PROVIDER] 🌐 Getting internet learning status');

    try {
      final response = await _learningService.getInternetLearningStatus(
        aiType: aiType,
      );
      return response;
    } catch (e) {
      print(
        '[AI_LEARNING_PROVIDER] ❌ Error getting internet learning status: $e',
      );
      return {};
    }
  }

  // Learn from oath paper with enhanced capabilities
  Future<void> learnFromOathPaper(Map<String, dynamic> oathPaper) async {
    print(
      '[AI_LEARNING_PROVIDER] 🧠 Learning from oath paper: ${oathPaper['subject']}',
    );

    try {
      // Use the enhanced learning service
      await _learningService.learnFromOathPaper(oathPaper);

      // Refresh data from backend
      await _fetchAIStatus();
      await _fetchLearningData();
      await _fetchLearningMetrics();

      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Oath paper learning completed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error learning from oath paper: $e');
      rethrow;
    }
  }

  // Get learning progress for oath papers
  Map<String, dynamic> getOathPaperLearningProgress() {
    final oathPapers = _learningData['oathPapers'] ?? [];
    final totalPapers = oathPapers.length;
    final totalKeywords = oathPapers.fold<int>(
      0,
      (sum, paper) => sum + (paper['keywords']?.length ?? 0),
    );
    final totalSearches = oathPapers.fold<int>(
      0,
      (sum, paper) => sum + (paper['searchResults']?.length ?? 0),
    );

    return {
      'totalOathPapers': totalPapers,
      'totalKeywordsExtracted': totalKeywords,
      'totalInternetSearches': totalSearches,
      'averageKeywordsPerPaper':
          totalPapers > 0 ? totalKeywords / totalPapers : 0,
      'averageSearchesPerPaper':
          totalPapers > 0 ? totalSearches / totalPapers : 0,
    };
  }

  // Get recent oath paper learning activities
  List<Map<String, dynamic>> getRecentOathPaperLearning() {
    final oathPapers = _learningData['oathPapers'] ?? [];
    return oathPapers
        .take(5)
        .map(
          (paper) => {
            'subject': paper['subject'],
            'keywords': paper['keywords'] ?? [],
            'targetAI': paper['targetAI'],
            'timestamp': paper['timestamp'],
            'searchResults': paper['searchResults']?.length ?? 0,
          },
        )
        .toList();
  }

  // Check backend connectivity
  static Future<bool> checkBackendConnectivity() async {
    final url = '${NetworkConfig.backendUrl}/api/imperium/agents';
    print('[AI_LEARNING_PROVIDER] Checking backend health at: $url');
    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'LVL_UP_Flutter_App',
        },
      );
      print(
        '[AI_LEARNING_PROVIDER] Health check response: ${response.statusCode} ${response.body}',
      );
      return response.statusCode == 200;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] Health check exception: $e');
      return false;
    }
  }

  // Handle successful backend connection
  void _handleBackendSuccess() {
    _consecutiveFailures = 0;
    _isBackendAvailable = true;

    print('[AI_LEARNING_PROVIDER] ✅ Backend available - connection restored');
    _showNotification(
      '✅ Backend Connected',
      'Successfully connected to backend - AI learning data will come from backend',
      channelId: 'ai_processes',
    );
  }

  // Handle backend connection failure
  void _handleBackendFailure(String error) {
    _consecutiveFailures++;
    print(
      '[AI_LEARNING_PROVIDER] ❌ Backend failure #$_consecutiveFailures: $error',
    );

    if (_consecutiveFailures >= _maxFailures) {
      print(
        '[AI_LEARNING_PROVIDER] 🔄 Too many failures - backend unavailable',
      );
      _isBackendAvailable = false;
      _showNotification(
        '❌ Backend Unavailable',
        'Backend connection failed - will retry automatically',
        channelId: 'ai_processes',
      );
    }
  }

  // Show notification (placeholder - implement as needed)
  void _showNotification(String title, String body, {String? channelId}) {
    print('[AI_LEARNING_PROVIDER] 🔔 $title: $body');
    // TODO: Implement notification system if needed
  }

  // Manual retry connection (public method)
  Future<void> retryConnection() async {
    print('[AI_LEARNING_PROVIDER] 🔄 Manual retry requested');

    // Reset failure count for manual retry
    _consecutiveFailures = 0;

    // Always allow operations now that chaos/warp is removed
    print(
      '[AI_LEARNING_PROVIDER] ✅ Attempting connection (no operational hours restrictions)',
    );

    // Test backend connectivity
    final isHealthy = await checkBackendConnectivity();
    if (isHealthy) {
      print(
        '[AI_LEARNING_PROVIDER] ✅ Backend is healthy - connection restored',
      );
      _isBackendAvailable = true;

      // Fetch fresh data from backend
      await _fetchAIStatus();
      await _fetchLearningData();
      await _fetchLearningMetrics();

      _showNotification(
        '✅ Connection Restored',
        'Successfully connected to backend',
        channelId: 'ai_processes',
      );
    } else {
      print('[AI_LEARNING_PROVIDER] ❌ Backend still unavailable');
      _showNotification(
        '❌ Connection Failed',
        'Backend is still unavailable - will retry automatically',
        channelId: 'ai_processes',
      );
    }

    notifyListeners();
  }

  // Force switch to real mode (for testing)
  void forceRealMode() {
    print('[AI_LEARNING_PROVIDER] 🔧 Force switching to real mode');
    _consecutiveFailures = 0;
    _isBackendAvailable = true;
    notifyListeners();

    _showNotification(
      '🔧 Forced Real Mode',
      'Manually switched to real mode for testing',
      channelId: 'ai_processes',
    );
  }

  // Force switch to mock mode (for testing) - REMOVED
  void forceMockMode() {
    print(
      '[AI_LEARNING_PROVIDER] 🔧 Mock mode disabled - always using real mode',
    );
    _showNotification(
      '🔧 Mock Mode Disabled',
      'Mock mode has been removed - always using real backend data',
      channelId: 'ai_processes',
    );
  }

  void updateFromWebSocket(Map<String, dynamic> data) {
    // Example: update level and progress from backend data
    if (data.containsKey('level')) {
      // _level = data['level']; / Assuming _level is a member variable
    }
    if (data.containsKey('progress')) {
      // _progress = data['progress']; / Assuming _progress is a member variable
    }
    notifyListeners();
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    _learningUpdateSubscription?.cancel();
    _aiLearningEventSubscription?.cancel();
    _debugOutputSubscription?.cancel();
    super.dispose();
  }

  // Get current connection status for debugging and UI
  Map<String, dynamic> getConnectionStatus() {
    return {
      'mode': 'Real', // Always real mode now
      'backendAvailable': _isBackendAvailable,
      'consecutiveFailures': _consecutiveFailures,
      'backendUrl': NetworkConfig.backendUrl,
      'operationalHours': true, // Always true now that chaos/warp is removed
    };
  }
}
