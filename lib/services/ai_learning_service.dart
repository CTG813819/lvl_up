import 'dart:convert';
import 'dart:async';
import 'dart:math' as math;
import 'package:shared_preferences/shared_preferences.dart';
import '../services/notification_service.dart';
import 'package:dio/dio.dart';
import 'network_config.dart';

// In-App AI Learning Service
// Handles AI learning within the Flutter app based on user interactions, test results, and backend feedback
class AILearningService {
  static final AILearningService _instance = AILearningService._internal();
  factory AILearningService() => _instance;
  AILearningService._internal();

  static const String _learningStorageKey = 'ai_learning_data';

  // Learning data structure
  Map<String, dynamic> _learningData = {
    'Imperium': {
      'lessons': [],
      'successPatterns': [],
      'failurePatterns': [],
      'testResults': [],
      'userFeedback': [],
      'backendTestResults': [],
      'learningScore': 0,
      'lastUpdated': null,
      'debugLog': [],
    },
    'Sandbox': {
      'lessons': [],
      'successPatterns': [],
      'failurePatterns': [],
      'testResults': [],
      'userFeedback': [],
      'backendTestResults': [],
      'learningScore': 0,
      'lastUpdated': null,
      'debugLog': [],
    },
    'Guardian': {
      'lessons': [],
      'successPatterns': [],
      'failurePatterns': [],
      'testResults': [],
      'userFeedback': [],
      'backendTestResults': [],
      'learningScore': 0,
      'lastUpdated': null,
      'debugLog': [],
    },
  };

  // Stream controllers for real-time updates
  final StreamController<Map<String, dynamic>> _learningUpdateController =
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<String> _aiLearningEventController =
      StreamController<String>.broadcast();
  final StreamController<Map<String, dynamic>> _debugOutputController =
      StreamController<Map<String, dynamic>>.broadcast();

  // HTTP client for API calls
  final Dio _dio = Dio(
    BaseOptions(
      baseUrl: NetworkConfig.backendUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );

  Stream<Map<String, dynamic>> get learningUpdateStream =>
      _learningUpdateController.stream;
  Stream<String> get aiLearningEventStream => _aiLearningEventController.stream;
  Stream<Map<String, dynamic>> get debugOutputStream =>
      _debugOutputController.stream;

  // Initialize the learning service
  Future<void> initialize() async {
    print(
      '[AI_LEARNING_SERVICE] 🧠 Initializing in-app AI learning service...',
    );
    await _loadLearningData();
    await _calculateLearningScores();
    print('[AI_LEARNING_SERVICE] ✅ AI learning service initialized');
  }

  // Load learning data from local storage
  Future<void> _loadLearningData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final learningJson = prefs.getString(_learningStorageKey);

      if (learningJson != null) {
        final loadedData = jsonDecode(learningJson) as Map<String, dynamic>;
        _learningData = Map<String, dynamic>.from(loadedData);
        print('[AI_LEARNING_SERVICE] 📚 Loaded existing learning data');
      } else {
        print(
          '[AI_LEARNING_SERVICE] 📚 No existing learning data found, using defaults',
        );
      }
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error loading learning data: $e');
    }
  }

  // Save learning data to local storage
  Future<void> _saveLearningData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final learningJson = jsonEncode(_learningData);
      await prefs.setString(_learningStorageKey, learningJson);
      print('[AI_LEARNING_SERVICE] 💾 Learning data saved');
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error saving learning data: $e');
    }
  }

  // Learn from a proposal approval/rejection
  Future<void> learnFromProposal(
    dynamic proposal,
    String action,
    String? feedbackReason,
  ) async {
    print(
      '[AI_LEARNING_SERVICE] 🧠 Learning from proposal ${proposal.id} - Action: $action',
    );

    final aiType = proposal.aiType;
    final now = DateTime.now();

    // Create learning entry
    final learningEntry = {
      'timestamp': now.toIso8601String(),
      'proposalId': proposal.id,
      'action': action, // 'approved', 'rejected', 'test-failed'
      'feedbackReason': feedbackReason,
      'filePath': proposal.filePath,
      'improvementType':
          'general', // Default since AIProposal doesn't have this field
      'codeBefore': proposal.oldCode,
      'codeAfter': proposal.newCode,
      'source': 'user_interaction',
    };

    // Add to AI's learning data
    if (_learningData.containsKey(aiType)) {
      _learningData[aiType]!['userFeedback'].add(learningEntry);

      // Keep only last 50 entries to prevent memory issues
      if (_learningData[aiType]!['userFeedback'].length > 50) {
        _learningData[aiType]!['userFeedback'] =
            _learningData[aiType]!['userFeedback'].take(50).toList();
      }

      // Extract patterns based on action
      if (action == 'approved') {
        _extractSuccessPatterns(aiType, learningEntry);
      } else if (action == 'rejected' || action == 'test-failed') {
        _extractFailurePatterns(aiType, learningEntry);
      }

      // Update last updated timestamp
      _learningData[aiType]!['lastUpdated'] = now.toIso8601String();

      // Add debug log entry
      _addDebugLog(
        aiType,
        'Learned from $action: ${feedbackReason != null ? (feedbackReason!.length > 50 ? '${feedbackReason!.substring(0, 50)}...' : feedbackReason!) : 'No feedback'}',
      );

      // Save and notify
      await _saveLearningData();
      await _calculateLearningScores();
      _notifyLearningUpdate(aiType, learningEntry);

      // Show notification
      _showLearningNotification(aiType, action, feedbackReason);

      print('[AI_LEARNING_SERVICE] ✅ ${aiType} learned from $action action');
    }
  }

  // Learn from backend test results
  Future<void> learnFromBackendTestResult(
    String aiType,
    Map<String, dynamic> testData,
  ) async {
    print(
      '[AI_LEARNING_SERVICE] 🧪 Learning from backend test result - $aiType',
    );

    final testEntry = {
      'timestamp': DateTime.now().toIso8601String(),
      'testType': testData['testType'] ?? 'unknown',
      'result': testData['result'] ?? 'unknown',
      'details': testData['details'] ?? '',
      'filePath': testData['filePath'] ?? 'unknown',
      'function': testData['function'] ?? 'unknown',
      'reasoning': testData['reasoning'] ?? '',
      'source': 'backend_test',
    };

    if (_learningData.containsKey(aiType)) {
      _learningData[aiType]!['backendTestResults'].add(testEntry);

      // Keep only last 30 backend test results
      if (_learningData[aiType]!['backendTestResults'].length > 30) {
        _learningData[aiType]!['backendTestResults'] =
            _learningData[aiType]!['backendTestResults'].take(30).toList();
      }

      // Extract lessons from test results
      if (testEntry['result'] == 'fail') {
        _extractBackendTestFailureLessons(aiType, testEntry);
      } else if (testEntry['result'] == 'pass') {
        _extractBackendTestSuccessPatterns(aiType, testEntry);
      }

      // Add debug log entry
      _addDebugLog(
        aiType,
        'Backend test ${testEntry['result']}: ${testEntry['testType']} - ${testEntry['details'].length > 50 ? '${testEntry['details'].substring(0, 50)}...' : testEntry['details']}',
      );

      await _saveLearningData();
      await _calculateLearningScores();
      _notifyLearningUpdate(aiType, testEntry);

      // Show notification
      _showBackendTestNotification(aiType, testEntry);

      print(
        '[AI_LEARNING_SERVICE] ✅ ${aiType} learned from backend test result',
      );
    }
  }

  // Learn from test results (local)
  Future<void> learnFromTestResult(
    String aiType,
    String testType,
    String result,
    String details,
  ) async {
    print(
      '[AI_LEARNING_SERVICE] 🧪 Learning from test result - $aiType: $testType = $result',
    );

    final testEntry = {
      'timestamp': DateTime.now().toIso8601String(),
      'testType': testType,
      'result': result, // 'pass', 'fail'
      'details': details,
      'source': 'local_test',
    };

    if (_learningData.containsKey(aiType)) {
      _learningData[aiType]!['testResults'].add(testEntry);

      // Keep only last 30 test results
      if (_learningData[aiType]!['testResults'].length > 30) {
        _learningData[aiType]!['testResults'] =
            _learningData[aiType]!['testResults'].take(30).toList();
      }

      // Extract lessons from test failures
      if (result == 'fail') {
        _extractTestFailureLessons(aiType, testEntry);
      }

      // Add debug log entry
      _addDebugLog(
        aiType,
        'Local test $result: $testType - ${details.length > 50 ? '${details.substring(0, 50)}...' : details}',
      );

      await _saveLearningData();
      await _calculateLearningScores();
      _notifyLearningUpdate(aiType, testEntry);

      // Show notification
      _showTestNotification(aiType, testType, result, details);

      print('[AI_LEARNING_SERVICE] ✅ ${aiType} learned from test result');
    }
  }

  // Extract success patterns from approved proposals
  void _extractSuccessPatterns(
    String aiType,
    Map<String, dynamic> learningEntry,
  ) {
    final patterns = _learningData[aiType]!['successPatterns'] as List;

    // Extract file type pattern
    final fileExt = learningEntry['filePath'].toString().split('.').last;
    final filePattern = 'successful_${fileExt}_changes';

    // Extract improvement type pattern
    final improvementType = learningEntry['improvementType'] ?? 'general';
    final improvementPattern = 'successful_${improvementType}_improvements';

    // Add patterns if they don't exist
    if (!patterns.any((p) => p['pattern'] == filePattern)) {
      patterns.add({
        'pattern': filePattern,
        'count': 1,
        'lastSeen': learningEntry['timestamp'],
      });
    } else {
      final existing = patterns.firstWhere((p) => p['pattern'] == filePattern);
      existing['count'] = (existing['count'] as int) + 1;
      existing['lastSeen'] = learningEntry['timestamp'];
    }

    if (!patterns.any((p) => p['pattern'] == improvementPattern)) {
      patterns.add({
        'pattern': improvementPattern,
        'count': 1,
        'lastSeen': learningEntry['timestamp'],
      });
    } else {
      final existing = patterns.firstWhere(
        (p) => p['pattern'] == improvementPattern,
      );
      existing['count'] = (existing['count'] as int) + 1;
      existing['lastSeen'] = learningEntry['timestamp'];
    }
  }

  // Extract failure patterns from rejected proposals
  void _extractFailurePatterns(
    String aiType,
    Map<String, dynamic> learningEntry,
  ) {
    final patterns = _learningData[aiType]!['failurePatterns'] as List;
    final feedback =
        learningEntry['feedbackReason']?.toString().toLowerCase() ?? '';

    // Extract common failure patterns
    List<String> failurePatterns = [];

    if (feedback.contains('compilation error') ||
        feedback.contains('syntax error')) {
      failurePatterns.add('compilation_errors');
    }
    if (feedback.contains('test failed') || feedback.contains('test failure')) {
      failurePatterns.add('test_failures');
    }
    if (feedback.contains('dependency') || feedback.contains('import')) {
      failurePatterns.add('dependency_issues');
    }
    if (feedback.contains('null safety') || feedback.contains('null check')) {
      failurePatterns.add('null_safety_issues');
    }
    if (feedback.contains('performance') || feedback.contains('slow')) {
      failurePatterns.add('performance_issues');
    }

    // Add patterns
    for (final pattern in failurePatterns) {
      if (!patterns.any((p) => p['pattern'] == pattern)) {
        patterns.add({
          'pattern': pattern,
          'count': 1,
          'lastSeen': learningEntry['timestamp'],
          'examples': [
            feedback.substring(
              0,
              feedback.length > 100 ? 100 : feedback.length,
            ),
          ],
        });
      } else {
        final existing = patterns.firstWhere((p) => p['pattern'] == pattern);
        existing['count'] = (existing['count'] as int) + 1;
        existing['lastSeen'] = learningEntry['timestamp'];
        if (existing['examples'] is List) {
          existing['examples'].add(
            feedback.substring(
              0,
              feedback.length > 100 ? 100 : feedback.length,
            ),
          );
          if (existing['examples'].length > 5) {
            existing['examples'] = existing['examples'].take(5).toList();
          }
        }
      }
    }
  }

  // Extract lessons from test failures
  void _extractTestFailureLessons(
    String aiType,
    Map<String, dynamic> testEntry,
  ) {
    final lessons = _learningData[aiType]!['lessons'] as List;
    final details = testEntry['details'].toString().toLowerCase();

    String lesson = '';
    if (details.contains('flutter_test') || details.contains('dart pub')) {
      lesson = 'Use "flutter pub" instead of "dart pub" for package management';
    } else if (details.contains('version solving failed')) {
      lesson = 'Check dependency compatibility before suggesting changes';
    } else if (details.contains('compilation error')) {
      lesson = 'Verify code compiles before suggesting changes';
    } else if (details.contains('null safety')) {
      lesson = 'Consider null safety when modifying Dart code';
    } else {
      lesson = 'Test thoroughly before suggesting changes';
    }

    // Add lesson if it doesn't exist
    if (!lessons.any((l) => l['lesson'] == lesson)) {
      lessons.add({
        'lesson': lesson,
        'learnedAt': testEntry['timestamp'],
        'source': 'test_failure',
        'count': 1,
      });
    } else {
      final existing = lessons.firstWhere((l) => l['lesson'] == lesson);
      existing['count'] = (existing['count'] as int) + 1;
    }
  }

  // Extract lessons from backend test failures
  void _extractBackendTestFailureLessons(
    String aiType,
    Map<String, dynamic> testEntry,
  ) {
    final lessons = _learningData[aiType]!['lessons'] as List;
    final details = testEntry['details'].toString().toLowerCase();
    final testType = testEntry['testType'].toString().toLowerCase();

    String lesson = '';
    if (testType.contains('compilation') || details.contains('syntax error')) {
      lesson = 'Ensure generated code compiles correctly before submission';
    } else if (testType.contains('dependency') ||
        details.contains('version solving')) {
      lesson = 'Verify package dependencies are compatible and available';
    } else if (testType.contains('null_safety') ||
        details.contains('null check')) {
      lesson = 'Handle null safety properly in all code changes';
    } else if (testType.contains('performance') || details.contains('slow')) {
      lesson = 'Consider performance implications of code changes';
    } else if (testType.contains('security') ||
        details.contains('vulnerability')) {
      lesson = 'Ensure code changes don\'t introduce security vulnerabilities';
    } else {
      lesson = 'Test all changes thoroughly before proposing them';
    }

    // Add lesson if it doesn't exist
    if (!lessons.any((l) => l['lesson'] == lesson)) {
      lessons.add({
        'lesson': lesson,
        'learnedAt': testEntry['timestamp'],
        'source': 'backend_test_failure',
        'count': 1,
      });
    } else {
      final existing = lessons.firstWhere((l) => l['lesson'] == lesson);
      existing['count'] = (existing['count'] as int) + 1;
    }
  }

  // Extract success patterns from backend test successes
  void _extractBackendTestSuccessPatterns(
    String aiType,
    Map<String, dynamic> testEntry,
  ) {
    final patterns = _learningData[aiType]!['successPatterns'] as List;
    final testType = testEntry['testType'].toString();

    final successPattern = 'backend_test_success_${testType}';

    if (!patterns.any((p) => p['pattern'] == successPattern)) {
      patterns.add({
        'pattern': successPattern,
        'count': 1,
        'lastSeen': testEntry['timestamp'],
      });
    } else {
      final existing = patterns.firstWhere(
        (p) => p['pattern'] == successPattern,
      );
      existing['count'] = (existing['count'] as int) + 1;
      existing['lastSeen'] = testEntry['timestamp'];
    }
  }

  // Add debug log entry
  void _addDebugLog(String aiType, String message) {
    final debugLog = _learningData[aiType]!['debugLog'] as List;
    final logEntry = {
      'timestamp': DateTime.now().toIso8601String(),
      'message': message,
    };

    debugLog.add(logEntry);

    // Keep only last 100 debug entries
    if (debugLog.length > 100) {
      debugLog.removeRange(0, debugLog.length - 100);
    }

    // Emit debug output
    _debugOutputController.add({
      'aiType': aiType,
      'timestamp': logEntry['timestamp'],
      'message': message,
    });
  }

  // Show learning notification
  void _showLearningNotification(
    String aiType,
    String action,
    String? feedbackReason,
  ) {
    String body;
    if (action == 'approved') {
      body =
          'Proposal sent AI is learning: ${feedbackReason != null ? (feedbackReason!.length > 50 ? '${feedbackReason!.substring(0, 50)}...' : feedbackReason!) : 'Good work!'}';
    } else if (action == 'rejected') {
      body =
          'Learned to avoid: ${feedbackReason != null ? (feedbackReason!.length > 50 ? '${feedbackReason!.substring(0, 50)}...' : feedbackReason!) : 'User rejection'}';
    } else {
      body =
          'Learned from failure: ${feedbackReason != null ? (feedbackReason!.length > 50 ? '${feedbackReason!.substring(0, 50)}...' : feedbackReason!) : 'Test failed'}';
    }

    NotificationService.instance.showNotification(
      aiSource: aiType,
      message: body,
      iconChar: action == 'approved' ? '✅' : '❌',
    );
  }

  // Show test notification
  void _showTestNotification(
    String aiType,
    String testType,
    String result,
    String details,
  ) {
    final body =
        '$testType test: ${details.length > 50 ? '${details.substring(0, 50)}...' : details}';

    NotificationService.instance.showNotification(
      aiSource: aiType,
      message: body,
      iconChar: result == 'pass' ? '✅' : '❌',
    );
  }

  // Show backend test notification
  void _showBackendTestNotification(
    String aiType,
    Map<String, dynamic> testEntry,
  ) {
    final result = testEntry['result'];
    final testType = testEntry['testType'];
    final details = testEntry['details'];

    final body =
        '$testType: ${details.length > 50 ? '${details.substring(0, 50)}...' : details}';

    NotificationService.instance.showNotification(
      aiSource: aiType,
      message: body,
      iconChar: result == 'pass' ? '✅' : '❌',
    );
  }

  // Calculate learning scores for all AIs
  Future<void> _calculateLearningScores() async {
    for (final aiType in _learningData.keys) {
      final data = _learningData[aiType]!;
      int score = 0;

      // Base score from lessons learned
      score += (data['lessons'] as List).length * 5;

      // Score from avoiding failure patterns
      final recentFailures =
          (data['userFeedback'] as List)
              .where(
                (f) =>
                    f['action'] == 'rejected' || f['action'] == 'test-failed',
              )
              .take(10)
              .length;
      score += math.max(0, 50 - (recentFailures * 5));

      // Score from success patterns
      score += (data['successPatterns'] as List).length * 3;

      // Score from backend test results
      final backendTests = (data['backendTestResults'] as List);
      final backendSuccessRate =
          backendTests.isEmpty
              ? 0
              : backendTests.where((t) => t['result'] == 'pass').length /
                  backendTests.length;
      score += (backendSuccessRate * 20).round();

      // Cap score at 100
      data['learningScore'] = math.min(score, 100);
    }

    await _saveLearningData();
  }

  // Get learning data for a specific AI
  Map<String, dynamic> getLearningData(String aiType) {
    return _learningData[aiType] ?? {};
  }

  // Get all learning data
  Map<String, dynamic> getAllLearningData() {
    return Map.unmodifiable(_learningData);
  }

  // Get learning metrics for dashboard
  Map<String, dynamic> getLearningMetrics() {
    final metrics = <String, dynamic>{};

    for (final aiType in _learningData.keys) {
      final data = _learningData[aiType]!;
      metrics[aiType] = {
        'totalProposals': (data['userFeedback'] as List).length,
        'learningEntries': (data['lessons'] as List).length,
        'learningScore': data['learningScore'],
        'successRate': _calculateSuccessRate(data),
        'appliedLearning': _calculateAppliedLearning(data),
        'failedProposals':
            (data['userFeedback'] as List)
                .where(
                  (f) =>
                      f['action'] == 'rejected' || f['action'] == 'test-failed',
                )
                .length,
        'passedProposals':
            (data['userFeedback'] as List)
                .where((f) => f['action'] == 'approved')
                .length,
        'backendTests': (data['backendTestResults'] as List).length,
        'backendTestSuccessRate': _calculateBackendTestSuccessRate(data),
      };
    }

    return metrics;
  }

  // Calculate success rate
  int _calculateSuccessRate(Map<String, dynamic> data) {
    final feedback = data['userFeedback'] as List;
    if (feedback.isEmpty) return 0;

    final approved = feedback.where((f) => f['action'] == 'approved').length;
    return ((approved / feedback.length) * 100).round();
  }

  // Calculate applied learning percentage
  int _calculateAppliedLearning(Map<String, dynamic> data) {
    final lessons = data['lessons'] as List;
    final recentFeedback = (data['userFeedback'] as List).take(10);

    if (lessons.isEmpty || recentFeedback.isEmpty) return 0;

    int appliedCount = 0;
    for (final lesson in lessons.take(5)) {
      final lessonText = lesson['lesson'].toString().toLowerCase();
      final avoidsMistake = recentFeedback.every((feedback) {
        final feedbackText =
            feedback['feedbackReason']?.toString().toLowerCase() ?? '';
        return !feedbackText.contains(lessonText.split(' ').take(3).join(' '));
      });
      if (avoidsMistake) appliedCount++;
    }

    return ((appliedCount / math.min(lessons.length, 5)) * 100).round();
  }

  // Calculate backend test success rate
  int _calculateBackendTestSuccessRate(Map<String, dynamic> data) {
    final backendTests = data['backendTestResults'] as List;
    if (backendTests.isEmpty) return 0;

    final passed = backendTests.where((t) => t['result'] == 'pass').length;
    return ((passed / backendTests.length) * 100).round();
  }

  // Get debug log for a specific AI
  List<Map<String, dynamic>> getDebugLog(String aiType) {
    return List<Map<String, dynamic>>.from(
      _learningData[aiType]?['debugLog'] ?? [],
    );
  }

  // Get all debug logs
  Map<String, List<Map<String, dynamic>>> getAllDebugLogs() {
    final debugLogs = <String, List<Map<String, dynamic>>>{};
    for (final aiType in _learningData.keys) {
      debugLogs[aiType] = getDebugLog(aiType);
    }
    return debugLogs;
  }

  // Notify listeners of learning updates
  void _notifyLearningUpdate(
    String aiType,
    Map<String, dynamic> learningEntry,
  ) {
    _learningUpdateController.add({
      'aiType': aiType,
      'learningEntry': learningEntry,
      'timestamp': DateTime.now().toIso8601String(),
    });

    _aiLearningEventController.add(
      '$aiType learned from ${learningEntry['action'] ?? 'interaction'}',
    );
  }

  // Clear all learning data (for testing/reset)
  Future<void> clearLearningData() async {
    _learningData = {
      'Imperium': {
        'lessons': [],
        'successPatterns': [],
        'failurePatterns': [],
        'testResults': [],
        'userFeedback': [],
        'backendTestResults': [],
        'learningScore': 0,
        'lastUpdated': null,
        'debugLog': [],
      },
      'Sandbox': {
        'lessons': [],
        'successPatterns': [],
        'failurePatterns': [],
        'testResults': [],
        'userFeedback': [],
        'backendTestResults': [],
        'learningScore': 0,
        'lastUpdated': null,
        'debugLog': [],
      },
      'Guardian': {
        'lessons': [],
        'successPatterns': [],
        'failurePatterns': [],
        'testResults': [],
        'userFeedback': [],
        'backendTestResults': [],
        'learningScore': 0,
        'lastUpdated': null,
        'debugLog': [],
      },
    };

    await _saveLearningData();
    _learningUpdateController.add({'reset': true});
    print('[AI_LEARNING_SERVICE] 🗑️ Learning data cleared');
  }

  // Dispose resources
  void dispose() {
    _learningUpdateController.close();
    _aiLearningEventController.close();
    _debugOutputController.close();
  }

  // Trigger comprehensive AI learning cycle
  Future<Map<String, dynamic>> triggerLearningCycle(
    String aiType,
    String proposalId,
    String result,
  ) async {
    try {
      final response = await _dio.post(
        '/api/proposals',
        data: {'aiType': aiType, 'proposalId': proposalId, 'result': result},
      );

      return response.data;
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error triggering learning cycle: $e');
      rethrow;
    }
  }

  // Get learning cycle statistics
  Future<Map<String, dynamic>> getLearningCycleStats({
    String? aiType,
    int days = 30,
  }) async {
    try {
      final queryParams = <String, dynamic>{'days': days};
      if (aiType != null) queryParams['aiType'] = aiType;

      final response = await _dio.get(
        '/api/proposals',
        queryParameters: queryParams,
      );
      return response.data;
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error getting learning cycle stats: $e');
      return {};
    }
  }

  // Get GitHub repository status
  Future<Map<String, dynamic>> getGitHubStatus() async {
    try {
      final response = await _dio.get('/api/proposals');
      return response.data;
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error getting GitHub status: $e');
      return {};
    }
  }

  // Merge AI learning pull request
  Future<Map<String, dynamic>> mergeLearningPR(String prUrl) async {
    try {
      final response = await _dio.post(
        '/api/proposals',
        data: {'prUrl': prUrl},
      );

      return response.data;
    } catch (e) {
      print('[AI_LEARNING_SERVICE] ❌ Error merging learning PR: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // Get internet learning status
  Future<Map<String, dynamic>> getInternetLearningStatus({
    String? aiType,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (aiType != null) queryParams['aiType'] = aiType;

      final response = await _dio.get(
        '/api/proposals',
        queryParameters: queryParams,
      );
      return response.data;
    } catch (e) {
      print(
        '[AI_LEARNING_SERVICE] ❌ Error getting internet learning status: $e',
      );
      return {};
    }
  }

  Future getSystemStatus() async {}

  Future getAIStatus() async {}

  Future testBackendConnection({required String userId}) async {}

  Future<void> learnFromOathPaper(Map<String, dynamic> oathPaper) async {}
}
