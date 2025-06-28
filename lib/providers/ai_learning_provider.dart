import 'dart:async';
import 'package:flutter/foundation.dart';
import '../services/ai_learning_service.dart';
import '../models/ai_proposal.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../providers/proposal_provider.dart';

/// Provider for managing AI learning state and data
class AILearningProvider extends ChangeNotifier {
  final AILearningService _learningService = AILearningService();
  
  // Learning data
  Map<String, dynamic> _learningData = {};
  Map<String, dynamic> _learningMetrics = {};
  Map<String, List<Map<String, dynamic>>> _debugLogs = {};
  
  // Stream subscriptions
  StreamSubscription<Map<String, dynamic>>? _learningUpdateSubscription;
  StreamSubscription<String>? _aiLearningEventSubscription;
  StreamSubscription<Map<String, dynamic>>? _debugOutputSubscription;
  
  // Polling timer for real-time updates
  Timer? _pollingTimer;
  
  // Getters
  Map<String, dynamic> get learningData => Map.unmodifiable(_learningData);
  Map<String, dynamic> get learningMetrics => Map.unmodifiable(_learningMetrics);
  Map<String, List<Map<String, dynamic>>> get debugLogs => Map.unmodifiable(_debugLogs);
  
  Map<String, dynamic> _aiLearningStatus = {};
  Map<String, dynamic> get aiLearningStatus => _aiLearningStatus;
  
  List<Map<String, dynamic>> _debugLog = [];
  List<Map<String, dynamic>> get debugLog => List.unmodifiable(_debugLog);
  
  Map<String, dynamic> _quotaStatus = {};
  bool _isLoading = false;
  
  // Constructor - auto-initialize
  AILearningProvider() {
    print('[AI_LEARNING_PROVIDER] 🧠 Creating AI learning provider...');
    // Initialize after a short delay to ensure the provider is fully created
    Future.delayed(const Duration(milliseconds: 100), () {
      initialize();
    });
  }
  
  /// Initialize the provider
  Future<void> initialize() async {
    print('[AI_LEARNING_PROVIDER] 🧠 Initializing AI learning provider...');
    
    // Initialize the learning service
    await _learningService.initialize();
    
    // Load initial data from backend
    await fetchAIStatus();
    await fetchDebugLog();
    await fetchLearningData();
    await fetchLearningMetrics();
    
    // Start polling for real-time updates
    startPolling();
    
    // Subscribe to learning updates
    _learningUpdateSubscription = _learningService.learningUpdateStream.listen((update) {
      print('[AI_LEARNING_PROVIDER] 📊 Learning update received: ${update['aiType']}');
      
      // Refresh data from backend
      fetchAIStatus();
      fetchDebugLog();
      fetchLearningData();
      fetchLearningMetrics();
    });
    
    // Subscribe to AI learning events
    _aiLearningEventSubscription = _learningService.aiLearningEventStream.listen((event) {
      print('[AI_LEARNING_PROVIDER] 🎯 AI learning event: $event');
      // Events are handled by the service notifications
    });
    
    // Subscribe to debug output
    _debugOutputSubscription = _learningService.debugOutputStream.listen((debugOutput) {
      print('[AI_LEARNING_PROVIDER] 🐛 Debug output: ${debugOutput['aiType']} - ${debugOutput['message']}');
      
      // Refresh debug log from backend
      fetchDebugLog();
    });
    
    print('[AI_LEARNING_PROVIDER] ✅ AI learning provider initialized');
  }
  
  /// Start polling for real-time updates
  void startPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      fetchAIStatus();
      fetchDebugLog();
      fetchLearningData();
      fetchLearningMetrics();
    });
    print('[AI_LEARNING_PROVIDER] 🔄 Started polling for real-time updates (every 10 seconds)');
  }
  
  /// Stop polling
  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
    print('[AI_LEARNING_PROVIDER] ⏹️ Stopped polling');
  }
  
  /// Fetch AI status from backend
  Future<void> fetchAIStatus() async {
    try {
      print('[AI_LEARNING_PROVIDER] 🔄 Fetching AI status from ${ProposalProvider.backendUrl}/api/proposals/ai-status');
      
      // Add timeout for Android network requests
      final response = await http.get(
        Uri.parse('${ProposalProvider.backendUrl}/api/proposals/ai-status'),
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'LVL_UP_Flutter_App',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('[AI_LEARNING_PROVIDER] 📡 AI status response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final newStatus = jsonDecode(response.body);
        print('[AI_LEARNING_PROVIDER] 📊 Received AI status: $newStatus');
        if (!mapEquals(_aiLearningStatus, newStatus)) {
          _aiLearningStatus = newStatus;
          print('[AI_LEARNING_PROVIDER] 🔄 AI status updated: $_aiLearningStatus');
          notifyListeners();
        }
      } else {
        print('[AI_LEARNING_PROVIDER] ❌ AI status failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching AI status: $e');
      // Don't throw error, just log it to prevent app crashes
    }
  }
  
  /// Fetch learning data from backend
  Future<void> fetchLearningData() async {
    try {
      print('[AI_LEARNING_PROVIDER] 🔄 Fetching learning data from ${ProposalProvider.backendUrl}/api/learning/data');
      
      final response = await http.get(
        Uri.parse('${ProposalProvider.backendUrl}/api/learning/data'),
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'LVL_UP_Flutter_App',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('[AI_LEARNING_PROVIDER] 📡 Learning data response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final newData = jsonDecode(response.body);
        print('[AI_LEARNING_PROVIDER] 📊 Received learning data keys: ${newData.keys.toList()}');
        if (!mapEquals(_learningData, newData)) {
          _learningData = newData;
          print('[AI_LEARNING_PROVIDER] 🔄 Learning data updated');
          notifyListeners();
        }
      } else {
        print('[AI_LEARNING_PROVIDER] ❌ Learning data failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching learning data: $e');
    }
  }
  
  /// Fetch learning metrics from backend
  Future<void> fetchLearningMetrics() async {
    try {
      print('[AI_LEARNING_PROVIDER] 🔄 Fetching learning metrics from ${ProposalProvider.backendUrl}/api/learning/metrics');
      
      final response = await http.get(
        Uri.parse('${ProposalProvider.backendUrl}/api/learning/metrics'),
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'LVL_UP_Flutter_App',
        },
      ).timeout(const Duration(seconds: 15));
      
      print('[AI_LEARNING_PROVIDER] 📡 Learning metrics response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final newMetrics = jsonDecode(response.body);
        print('[AI_LEARNING_PROVIDER] 📊 Received learning metrics keys: ${newMetrics.keys.toList()}');
        if (!mapEquals(_learningMetrics, newMetrics)) {
          _learningMetrics = newMetrics;
          print('[AI_LEARNING_PROVIDER] 🔄 Learning metrics updated');
          notifyListeners();
        }
      } else {
        print('[AI_LEARNING_PROVIDER] ❌ Learning metrics failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error fetching learning metrics: $e');
    }
  }
  
  /// Reset learning state for an AI
  Future<bool> resetLearningState(String aiType) async {
    try {
      print('[AI_LEARNING_PROVIDER] 🔄 Resetting learning state for $aiType');
      
      final response = await http.post(
        Uri.parse('${ProposalProvider.backendUrl}/api/proposals/reset-learning/$aiType'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({}),
      );
      
      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        print('[AI_LEARNING_PROVIDER] ✅ Learning state reset for $aiType: ${result['message']}');
        
        // Refresh AI status
        await fetchAIStatus();
        
        return true;
      } else {
        print('[AI_LEARNING_PROVIDER] ❌ Failed to reset learning state: ${response.statusCode}');
        return false;
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error resetting learning state: $e');
      return false;
    }
  }
  
  /// Fetch debug log from backend
  Future<void> fetchDebugLog() async {
    try {
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/learning/debug-log'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _debugLog = List<Map<String, dynamic>>.from(data['logs'] ?? []);
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] Error fetching debug log: $e');
    }
  }
  
  /// Get recent debug entries (last 20)
  List<Map<String, dynamic>> getRecentDebugEntries() {
    return _debugLog.take(20).toList();
  }
  
  /// Get debug entries for a specific AI
  List<Map<String, dynamic>> getDebugEntriesForAI(String aiType) {
    return _debugLog.where((entry) => 
      entry['message']?.toString().contains(aiType.toUpperCase()) == true
    ).toList();
  }
  
  /// Check if an AI is currently learning
  bool isAILearning(String aiType) {
    return _aiLearningStatus[aiType]?['isLearning'] == true;
  }
  
  /// Get learning state summary
  Map<String, bool> getLearningStateSummary() {
    final summary = <String, bool>{};
    for (final aiType in ['Imperium', 'Sandbox', 'Guardian']) {
      summary[aiType] = isAILearning(aiType);
    }
    return summary;
  }
  
  /// Learn from a proposal approval/rejection
  Future<void> learnFromProposal(dynamic proposal, String action, String? feedbackReason) async {
    print('[AI_LEARNING_PROVIDER] 🧠 Learning from proposal: $action');
    
    try {
      await _learningService.learnFromProposal(proposal, action, feedbackReason);
      
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
  
  /// Learn from backend test results
  Future<void> learnFromBackendTestResult(String aiType, Map<String, dynamic> testData) async {
    print('[AI_LEARNING_PROVIDER] 🧪 Learning from backend test result: $aiType');
    
    try {
      await _learningService.learnFromBackendTestResult(aiType, testData);
      
      // Refresh data
      _learningData = _learningService.getAllLearningData();
      _learningMetrics = _learningService.getLearningMetrics();
      _debugLogs = _learningService.getAllDebugLogs();
      
      notifyListeners();
      print('[AI_LEARNING_PROVIDER] ✅ Learning from backend test result completed');
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error learning from backend test result: $e');
    }
  }
  
  /// Learn from local test results
  Future<void> learnFromTestResult(String aiType, String testType, String result, String details) async {
    print('[AI_LEARNING_PROVIDER] 🧪 Learning from test result: $aiType - $testType = $result');
    
    try {
      await _learningService.learnFromTestResult(aiType, testType, result, details);
      
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
  
  /// Get learning data for a specific AI
  Map<String, dynamic> getLearningDataForAI(String aiType) {
    return _learningData[aiType] ?? {};
  }
  
  /// Get learning metrics for a specific AI
  Map<String, dynamic> getLearningMetricsForAI(String aiType) {
    return _learningMetrics[aiType] ?? {};
  }
  
  /// Get debug log for a specific AI
  List<Map<String, dynamic>> getDebugLogForAI(String aiType) {
    return _debugLogs[aiType] ?? [];
  }
  
  /// Get learning summary for dashboard
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
    summary['averageLearningScore'] = _learningData.isEmpty ? 0 : 
        (totalLearningScore / _learningData.length).round();
    
    return summary;
  }
  
  /// Get AI performance comparison
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
  
  /// Get learning trends (last 10 entries per AI)
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
  
  /// Clear all learning data
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
  
  /// Refresh learning data
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
  
  /// Simulate learning for testing
  Future<void> simulateLearning() async {
    print('[AI_LEARNING_PROVIDER] 🧪 Simulating learning events...');
    
    try {
      // Simulate proposal learning
      await learnFromTestResult('Imperium', 'compilation', 'fail', 'Syntax error in generated code');
      await learnFromTestResult('Sandbox', 'dependency', 'pass', 'All dependencies resolved successfully');
      await learnFromTestResult('Guardian', 'null_safety', 'fail', 'Null safety violation detected');
      
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
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/proposals/quotas'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _quotaStatus = Map<String, dynamic>.from(data);
        notifyListeners();
      }
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] Error fetching quota status: $e');
    }
  }
  
  /// Trigger comprehensive AI learning cycle
  Future<void> triggerLearningCycle(String aiType, String proposalId, String result) async {
    print('[AI_LEARNING_PROVIDER] 🎯 Triggering learning cycle for $aiType');
    
    try {
      final response = await _learningService.triggerLearningCycle(aiType, proposalId, result);
      
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
  
  /// Get learning cycle statistics
  Future<Map<String, dynamic>> getLearningCycleStats({String? aiType, int days = 30}) async {
    print('[AI_LEARNING_PROVIDER] 📊 Getting learning cycle stats');
    
    try {
      final response = await _learningService.getLearningCycleStats(aiType: aiType, days: days);
      return response;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error getting learning cycle stats: $e');
      return {};
    }
  }
  
  /// Get GitHub repository status
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
  
  /// Merge AI learning pull request
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
  
  /// Get internet learning status
  Future<Map<String, dynamic>> getInternetLearningStatus({String? aiType}) async {
    print('[AI_LEARNING_PROVIDER] 🌐 Getting internet learning status');
    
    try {
      final response = await _learningService.getInternetLearningStatus(aiType: aiType);
      return response;
    } catch (e) {
      print('[AI_LEARNING_PROVIDER] ❌ Error getting internet learning status: $e');
      return {};
    }
  }
  
  @override
  void dispose() {
    _pollingTimer?.cancel();
    _learningUpdateSubscription?.cancel();
    _aiLearningEventSubscription?.cancel();
    _debugOutputSubscription?.cancel();
    super.dispose();
  }
} 