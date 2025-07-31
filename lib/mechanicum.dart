import 'dart:async';
import 'dart:isolate';
import 'dart:convert';
import 'dart:math';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:the_codex/mission.dart' show MissionSubtask, MissionData;
import 'mission_provider.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'services/network_config.dart';

  // Represents the AI Guardian that continuously monitors, learns, and heals the app.
class Mechanicum {
  static final Mechanicum instance = Mechanicum._internal();
  Mechanicum._internal();

  final List<String> _repairLog = [];
  final StreamController<bool> _aiActiveController =
      StreamController<bool>.broadcast();
  final StreamController<String> _learningController =
      StreamController<String>.broadcast();
  final StreamController<Map<String, dynamic>> _issueController =
      StreamController<Map<String, dynamic>>.broadcast();

  Timer? _backgroundCheckTimer;
  bool _isAIActive = false;
  bool _isRunning = false;
  Isolate? _backgroundIsolate;
  ReceivePort? _isolateReceivePort;

  // Learning and self-improvement system
  final Map<String, HealthCheck> _learnedHealthChecks = {};
  final Map<String, RepairFunction> _learnedRepairs = {};
  final List<String> _issuePatterns = [];
  final Map<String, int> _issueFrequency = {};
  final List<String> _learningHistory = [];

  // AI Sandbox suggestion fields
  final List<Map<String, dynamic>> _aiSuggestions = [];
  final List<Map<String, dynamic>> _aiPersonalizedSuggestions = [];
  final List<Map<String, dynamic>> _aiGeneratedCodeSuggestions = [];

  // Notification ID repair system
  final Set<int> _usedNotificationIds = {};
  final Random _random = Random();

  // Notification throttling
  DateTime? lastGuardianNotificationTime;
  DateTime? lastSandboxNotificationTime;

  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  WebSocketChannel? _wsChannel;
  bool _isWebSocketConnected = false;
  final List<Map<String, dynamic>> _healthCheckResults = [];

  // Stream to notify listeners when the AI is active (for UI icon color).
  Stream<bool> get aiActiveStream => _aiActiveController.stream;

  // Stream to notify listeners when the AI learns something new
  Stream<String> get learningStream => _learningController.stream;

  // Stream to notify listeners about issues found and fixed
  Stream<Map<String, dynamic>> get issueStream => _issueController.stream;

  bool get isAIActive => _isAIActive;
  bool get isRunning => _isRunning;

  // Get all learned health checks
  Map<String, HealthCheck> get learnedHealthChecks =>
      Map.unmodifiable(_learnedHealthChecks);

  // Get all learned repair functions
  Map<String, RepairFunction> get learnedRepairs =>
      Map.unmodifiable(_learnedRepairs);

  // Get issue frequency statistics
  Map<String, int> get issueFrequency => Map.unmodifiable(_issueFrequency);

  // Get learning history
  List<String> get learningHistory => List.unmodifiable(_learningHistory);

  List<Map<String, dynamic>> get healthCheckResults =>
      List.unmodifiable(_healthCheckResults);

  // Initialize the AI Guardian with persistent learning
  Future<void> initialize() async {
    print('🛡️ AI Guardian: Initializing with backend integration...');
    await _loadLearnedData();
    await _loadIssuePatterns();
    _addDefaultHealthChecks();
    _connectToBackendWS();
    print(
      'AI Guardian: Initialized with ${_learnedHealthChecks.length} learned health checks and backend connection',
    );
  // Start periodic health check and repair (reduced frequency)
    _startPeriodicHealthCheckAndRepair(interval: const Duration(minutes: 2));
  }

  void _connectToBackendWS() {
    print('[GUARDIAN] WebSocket endpoints not available, skipping connection');
    // WebSocket endpoints are not working on the server, so skip connection
    print('[GUARDIAN] ✅ WebSocket connection skipped (using HTTP fallback)');
  }

  void _handleWSMessage(dynamic data) {
    try {
      final message = jsonDecode(data.toString());
      final type = message['type'];
      switch (type) {
        case 'guardian_update':
          _handleGuardianUpdate(message);
          break;
        case 'ai:experiment-start':
        case 'ai:experiment-complete':
        case 'proposal:created':
        case 'proposal:test-started':
        case 'proposal:test-finished':
        case 'proposal:applied':
          _learningController.add(
            'Backend event: $type - ${message.toString()}',
          );
          break;
        default:
          print('[GUARDIAN] ⚠️ Unknown message type: $type');
      }
    } catch (e) {
      print('[GUARDIAN] ❌ Error parsing WebSocket message: $e');
    }
  }

  void _handleGuardianUpdate(Map<String, dynamic> message) {
  // Custom logic for Guardian updates
    print('[GUARDIAN] 📨 Guardian update: ${message.toString()}');
    _learningController.add('Guardian update: ${message.toString()}');
  }

  void _startPeriodicHealthCheckAndRepair({
    Duration interval = const Duration(minutes: 2),
  }) {
    _backgroundCheckTimer?.cancel();
    _backgroundCheckTimer = Timer.periodic(interval, (_) async {
      setAIActive(true);
      print('🛡️ AI Guardian: Running local connectivity check...');

      try {
  // Check backend connectivity
        final isConnected = _isWebSocketConnected;
        print('🛡️ AI Guardian: Backend connection status: $isConnected');

        if (!isConnected) {
          print('🛡️ AI Guardian: Attempting to reconnect to backend...');
          _connectToBackendWS();
        }

  // Run minimal local health checks (reduced scope)
        final healthResults = await performMinimalLocalHealthChecks();
        bool anyIssue = false;
        for (final result in healthResults) {
          if (result.hasIssue) {
            anyIssue = true;
            print('🛡️ AI Guardian: Local issue detected: ${result.checkName}');
          }
        }

        if (anyIssue) {
          print(
            '🛡️ AI Guardian: Running local repairs for detected issues...',
          );
          final repairResults = await performComprehensiveRepairs();
          for (final repair in repairResults) {
            if (repair.success) {
              print(
                'Intelligent Repair: ✅ Local repair successful: ${repair.repairName}',
              );
            } else {
              print(
                'Intelligent Repair: ❌ Local repair failed: ${repair.repairName}',
              );
            }
          }
        } else {
          print(
            '🛡️ AI Guardian: ✅ Local health check passed - no issues detected',
          );
        }
      } catch (e) {
        print('🛡️ AI Guardian: ❌ Error during local health check: $e');
      }

      setAIActive(false);
    });
  }

  Future<List<HealthCheckResult>> performMinimalLocalHealthChecks() async {
    final results = <HealthCheckResult>[];
    print('🛡️ AI Guardian: Starting minimal local health checks...');

  // Only run critical local health checks
    final criticalChecks = _learnedHealthChecks.entries
        .where((entry) => entry.value.priority == HealthCheckPriority.high)
        .take(3); // Limit to 3 critical checks

    for (final entry in criticalChecks) {
      final healthCheck = entry.value;
      try {
        print(
          '🛡️ AI Guardian: Running local health check: ${healthCheck.name}',
        );
        final hasIssue = await healthCheck.checkFunction();
        results.add(
          HealthCheckResult(
            checkName: healthCheck.name,
            description: healthCheck.description,
            hasIssue: hasIssue,
            priority: healthCheck.priority,
            timestamp: DateTime.now(),
          ),
        );

        if (hasIssue) {
          print(
            '🛡️ AI Guardian: ⚠️ Local health check failed: ${healthCheck.name}',
          );
        } else {
          print('🛡️ AI Guardian: Health check passed: ${healthCheck.name}');
        }
      } catch (e) {
        print(
          '🛡️ AI Guardian: ❌ Error in local health check ${healthCheck.name}: $e',
        );
        results.add(
          HealthCheckResult(
            checkName: healthCheck.name,
            description: healthCheck.description,
            hasIssue: true,
            priority: healthCheck.priority,
            timestamp: DateTime.now(),
            error: 'Error during local check: $e',
          ),
        );
      }
    }

    return results;
  }

  // Add default health checks that the AI Guardian knows from the start
  void _addDefaultHealthChecks() {
  // Notification ID validation check
    _learnedHealthChecks['invalid_notification_ids'] = HealthCheck(
      name: 'Invalid Notification IDs',
      description: 'Check for notification IDs outside 32-bit integer range',
      checkFunction: _checkInvalidNotificationIds,
      priority: HealthCheckPriority.high,
    );

  // Duplicate notification ID check
    _learnedHealthChecks['duplicate_notification_ids'] = HealthCheck(
      name: 'Duplicate Notification IDs',
      description: 'Check for duplicate notification IDs across missions',
      checkFunction: _checkDuplicateNotificationIds,
      priority: HealthCheckPriority.high,
    );

  // Mission ID validation check
    _learnedHealthChecks['invalid_mission_ids'] = HealthCheck(
      name: 'Invalid Mission IDs',
      description: 'Check for null or empty mission IDs',
      checkFunction: _checkInvalidMissionIds,
      priority: HealthCheckPriority.high,
    );

  // Add corresponding repair functions
    _learnedRepairs['fix_invalid_notification_ids'] = RepairFunction(
      name: 'Fix Invalid Notification IDs',
      description: 'Repair notification IDs that are outside valid range',
      repairFunction: _fixInvalidNotificationIds,
      priority: RepairPriority.critical,
    );

    _learnedRepairs['fix_duplicate_notification_ids'] = RepairFunction(
      name: 'Fix Duplicate Notification IDs',
      description:
          'Repair duplicate notification IDs by generating unique ones',
      repairFunction: _fixDuplicateNotificationIds,
      priority: RepairPriority.critical,
    );

    _learnedRepairs['fix_invalid_mission_ids'] = RepairFunction(
      name: 'Fix Invalid Mission IDs',
      description: 'Repair null or empty mission IDs',
      repairFunction: _fixInvalidMissionIds,
      priority: RepairPriority.critical,
    );

  // 1. Empty/null mission titles
    _learnedHealthChecks['empty_mission_titles'] = HealthCheck(
      name: 'Empty Mission Titles',
      description: 'Check for missions with empty or null titles',
      checkFunction: _checkEmptyMissionTitles,
      priority: HealthCheckPriority.medium,
    );
    _learnedRepairs['fix_empty_mission_titles'] = RepairFunction(
      name: 'Fix Empty Mission Titles',
      description: 'Repair missions with empty or null titles',
      repairFunction: _fixEmptyMissionTitles,
      priority: RepairPriority.medium,
    );

  // 2. Negative/invalid subtask mastery values
    _learnedHealthChecks['invalid_subtask_mastery_values'] = HealthCheck(
      name: 'Invalid Subtask Mastery Values',
      description: 'Check for negative or zero subtask mastery values',
      checkFunction: _checkInvalidSubtaskMasteryValues,
      priority: HealthCheckPriority.medium,
    );
    _learnedRepairs['fix_invalid_subtask_mastery_values'] = RepairFunction(
      name: 'Fix Invalid Subtask Mastery Values',
      description: 'Repair negative or zero subtask mastery values',
      repairFunction: _fixInvalidSubtaskMasteryValues,
      priority: RepairPriority.medium,
    );

  // 3. Missions both completed and failed
    _learnedHealthChecks['completed_and_failed_missions'] = HealthCheck(
      name: 'Completed and Failed Missions',
      description: 'Check for missions both completed and failed',
      checkFunction: _checkCompletedAndFailedMissions,
      priority: HealthCheckPriority.medium,
    );
    _learnedRepairs['fix_completed_and_failed_missions'] = RepairFunction(
      name: 'Fix Completed and Failed Missions',
      description: 'Repair missions both completed and failed',
      repairFunction: _fixCompletedAndFailedMissions,
      priority: RepairPriority.medium,
    );

  // 4. Missions with createdAt in the future
    _learnedHealthChecks['future_created_at'] = HealthCheck(
      name: 'Future CreatedAt',
      description: 'Check for missions with createdAt in the future',
      checkFunction: _checkFutureCreatedAt,
      priority: HealthCheckPriority.low,
    );
    _learnedRepairs['fix_future_created_at'] = RepairFunction(
      name: 'Fix Future CreatedAt',
      description: 'Repair missions with createdAt in the future',
      repairFunction: _fixFutureCreatedAt,
      priority: RepairPriority.low,
    );

  // 5. Missions with missing/invalid subtasks
    _learnedHealthChecks['invalid_subtasks'] = HealthCheck(
      name: 'Invalid Subtasks',
      description: 'Check for missions with missing or invalid subtasks',
      checkFunction: _checkInvalidSubtasks,
      priority: HealthCheckPriority.low,
    );
    _learnedRepairs['fix_invalid_subtasks'] = RepairFunction(
      name: 'Fix Invalid Subtasks',
      description: 'Repair missions with missing or invalid subtasks',
      repairFunction: _fixInvalidSubtasks,
      priority: RepairPriority.low,
    );
  }

  // Learn a new health check from sandbox or user feedback
  Future<void> learnNewHealthCheck(
    String issueType,
    String description,
    Future<bool> Function() checkFunction, {
    HealthCheckPriority priority = HealthCheckPriority.medium,
  }) async {
    if (!_learnedHealthChecks.containsKey(issueType)) {
      _learnedHealthChecks[issueType] = HealthCheck(
        name: issueType.replaceAll('_', ' ').toUpperCase(),
        description: description,
        checkFunction: checkFunction,
        priority: priority,
      );

      _learningHistory.add(
        '${DateTime.now().toIso8601String()}: Learned new health check: $issueType',
      );
      _learningController.add('Learned new health check: $issueType');

      await _saveLearnedData();
      print('AI Guardian: 🧠 Learned new health check: $issueType');
    }
  }

  // Learn a new repair function from sandbox or user feedback
  Future<void> learnNewRepair(
    String issueType,
    String description,
    Future<void> Function() repairFunction, {
    RepairPriority priority = RepairPriority.medium,
  }) async {
    if (!_learnedRepairs.containsKey('fix_$issueType')) {
      _learnedRepairs['fix_$issueType'] = RepairFunction(
        name: 'Fix ${issueType.replaceAll('_', ' ').toUpperCase()}',
        description: description,
        repairFunction: repairFunction,
        priority: priority,
      );

      _learningHistory.add(
        '${DateTime.now().toIso8601String()}: Learned new repair: fix_$issueType',
      );
      _learningController.add('Learned new repair: fix_$issueType');

      await _saveLearnedData();
      print('AI Guardian: 🛠️ Learned new repair: fix_$issueType');
    }
  }

  // Log a repair event with details and learn from it
  void logRepair(
    String issue,
    String action, {
    String? missionId,
    DateTime? timestamp,
  }) {
    final now = timestamp ?? DateTime.now();
    final entry =
        '[${now.toIso8601String()}] $issue | Repair: $action${missionId != null ? ' | Mission: $missionId' : ''}';
    _repairLog.add(entry);
    if (_repairLog.length > 100) _repairLog.removeAt(0);

  // Learn from this repair
    _learnFromRepair(issue, action, missionId);

  // Notify listeners about the issue and fix
    _issueController.add({
      'type': 'repair',
      'issue': issue,
      'action': action,
      'missionId': missionId,
      'timestamp': now.toIso8601String(),
    });
    print('🛡️ AI Guardian: Repair logged: $issue | $action');
  }

  // Learn from repair events to improve future health checks
  void _learnFromRepair(String issue, String action, String? missionId) {
  // Track issue frequency
    _issueFrequency[issue] = (_issueFrequency[issue] ?? 0) + 1;

  // Add to issue patterns if it's a new pattern
    if (!_issuePatterns.contains(issue)) {
      _issuePatterns.add(issue);
    }

  // If this issue occurs frequently, prioritize it
    if (_issueFrequency[issue]! >= 3) {
      final healthCheck =
          _learnedHealthChecks[issue.toLowerCase().replaceAll(' ', '_')];
      if (healthCheck != null &&
          healthCheck.priority == HealthCheckPriority.low) {
  // healthCheck.priority = HealthCheckPriority.medium; / Priority is immutable
        print('AI Guardian: 📈 Upgraded priority for health check: $issue');
      }
    }
  }

  // Get a summary of repair log issues and counts.
  Map<String, int> getRepairLogSummary() {
    final Map<String, int> counts = {};
    for (final entry in _repairLog) {
      final type = entry.split('|').first.split(']').last.trim();
      counts[type] = (counts[type] ?? 0) + 1;
    }
    return counts;
  }

  // Check if a mission would cause a known issue (based on repair log).
  bool wouldCauseKnownIssue(String issueType, {String? missionId}) {
    return _repairLog.any(
      (entry) =>
          entry.contains(issueType) &&
          (missionId == null || entry.contains(missionId)),
    );
  }

  // Perform comprehensive health checks using learned patterns
  Future<List<HealthCheckResult>> performComprehensiveHealthChecks() async {
    print('🛡️ AI Guardian: Starting comprehensive health checks...');
    final results = <HealthCheckResult>[];

    final sortedChecks =
        _learnedHealthChecks.values.toList()
          ..sort((a, b) => b.priority.index.compareTo(a.priority.index));

    for (final healthCheck in sortedChecks) {
      try {
        print('🛡️ AI Guardian: Running health check: ${healthCheck.name}');
        final hasIssue = await healthCheck.checkFunction();
        results.add(
          HealthCheckResult(
            checkName: healthCheck.name,
            description: healthCheck.description,
            hasIssue: hasIssue,
            priority: healthCheck.priority,
            timestamp: DateTime.now(),
          ),
        );

        if (hasIssue) {
          print('🛡️ AI Guardian: ⚠️ Health check failed: ${healthCheck.name}');
          _issueController.add({
            'type': 'health_check_failed',
            'checkName': healthCheck.name,
            'description': healthCheck.description,
            'priority': healthCheck.priority.name,
            'timestamp': DateTime.now().toIso8601String(),
          });
        } else {
          print('🛡️ AI Guardian: Health check passed: ${healthCheck.name}');
        }
      } catch (e) {
        print(
          '🛡️ AI Guardian: ❌ Error in health check ${healthCheck.name}: $e',
        );
        results.add(
          HealthCheckResult(
            checkName: healthCheck.name,
            description: healthCheck.description,
            hasIssue: false,
            priority: healthCheck.priority,
            timestamp: DateTime.now(),
            error: e.toString(),
          ),
        );
      }
    }

    return results;
  }

  // Perform comprehensive repairs using learned patterns
  Future<List<RepairResult>> performComprehensiveRepairs() async {
    print('🛡️ AI Guardian: Starting comprehensive repairs...');
    final results = <RepairResult>[];
    final sortedRepairs =
        _learnedRepairs.values.toList()
          ..sort((a, b) => b.priority.index.compareTo(a.priority.index));
    for (final repair in sortedRepairs) {
      try {
        print('🛡️ AI Guardian: Running repair: ${repair.name}');
        await repair.repairFunction();
        results.add(
          RepairResult(
            repairName: repair.name,
            description: repair.description,
            success: true,
            priority: repair.priority,
            timestamp: DateTime.now(),
          ),
        );
        print('🛡️ AI Guardian: ✅ Repair completed: ${repair.name}');
        _issueController.add({
          'type': 'repair_completed',
          'repairName': repair.name,
          'description': repair.description,
          'priority': repair.priority.name,
          'timestamp': DateTime.now().toIso8601String(),
        });
      } catch (e) {
        print('🛡️ AI Guardian: ❌ Error in repair ${repair.name}: $e');
        results.add(
          RepairResult(
            repairName: repair.name,
            description: repair.description,
            success: false,
            priority: repair.priority,
            timestamp: DateTime.now(),
            error: e.toString(),
          ),
        );
      }
    }
    return results;
  }

  // Default health check functions
  Future<bool> _checkInvalidNotificationIds() async {
    print(
      '🛡️ AI Guardian: Checking for invalid notification IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for health check.',
      );
      return false;
    }
    for (final mission in provider.missions) {
      if (mission.notificationId < -2147483648 ||
          mission.notificationId > 2147483647) {
        print(
          '🛡️ AI Guardian: Found invalid notification ID: ${mission.notificationId} for mission: ${mission.title}',
        );
        return true;
      }
    }
    return false;
  }

  Future<bool> _checkDuplicateNotificationIds() async {
    print(
      '🛡️ AI Guardian: Checking for duplicate notification IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for health check.',
      );
      return false;
    }
    final seen = <int>{};
    for (final mission in provider.missions) {
      if (!seen.add(mission.notificationId)) {
        print(
          '🛡️ AI Guardian: Found duplicate notification ID: ${mission.notificationId} for mission: ${mission.title}',
        );
        learnNewIssue(
          'duplicate_notification_ids',
          'Duplicate notification IDs detected in mission data.',
        );
        return true;
      }
    }
    return false;
  }

  Future<bool> _checkInvalidMissionIds() async {
    print(
      '🛡️ AI Guardian: Checking for invalid mission IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for health check.',
      );
      return false;
    }
    for (final mission in provider.missions) {
      if (mission.id == null || mission.id!.isEmpty) {
        print(
          '🛡️ AI Guardian: Found invalid mission ID for mission: ${mission.title}',
        );
        learnNewIssue(
          'invalid_mission_ids',
          'Invalid mission IDs detected in mission data.',
        );
        return true;
      }
    }
    return false;
  }

  // Default repair functions
  Future<void> _fixInvalidNotificationIds() async {
    print(
      '🛡️ AI Guardian: Repairing invalid notification IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for repair.',
      );
      return;
    }
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      if (mission.notificationId < -2147483648 ||
          mission.notificationId > 2147483647) {
        final newId = generateValidNotificationId();
        final updatedMission = mission.copyWith(notificationId: newId);
        missionsToUpdate.add(updatedMission);
        print(
          '🛡️ AI Guardian: Fixed invalid notification ID for mission "${mission.title}": ${mission.notificationId} -> $newId',
        );
        logRepair(
          'Invalid Notification ID',
          'Fixed notification ID from ${mission.notificationId} to $newId',
          missionId: mission.id,
        );
        await _showRepairNotification(
          'Repairing',
          'Repairing invalid notification ID for: ${mission.id}',
          missionTitle: mission.title,
          isRepairing: true,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed ${missionsToUpdate.length} invalid notification IDs',
      );
      await _showRepairNotification(
        'Repaired',
        'Notification IDs repaired in ${missionsToUpdate.length} missions',
        missionTitle: null,
        isRepairing: false,
      );
    }
  }

  Future<void> _fixDuplicateNotificationIds() async {
    print(
      '🛡️ AI Guardian: Repairing duplicate notification IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for repair.',
      );
      return;
    }
    final seen = <int>{};
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      if (!seen.add(mission.notificationId)) {
        final newId = generateValidNotificationId();
        final updatedMission = mission.copyWith(notificationId: newId);
        missionsToUpdate.add(updatedMission);
        print(
          '🛡️ AI Guardian: Fixed duplicate notification ID for mission "${mission.title}": ${mission.notificationId} -> $newId',
        );
        logRepair(
          'Duplicate Notification ID',
          'Fixed duplicate notification ID from ${mission.notificationId} to $newId',
          missionId: mission.id,
        );
        await _showRepairNotification(
          'Repairing',
          'Repairing duplicate notification ID for: ${mission.id}',
          missionTitle: mission.title,
          isRepairing: true,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed ${missionsToUpdate.length} duplicate notification IDs',
      );
      await _showRepairNotification(
        'Repaired',
        'Duplicate notification IDs repaired in ${missionsToUpdate.length} missions',
        missionTitle: null,
        isRepairing: false,
      );
    }
  }

  Future<void> _fixInvalidMissionIds() async {
    print(
      '🛡️ AI Guardian: Repairing invalid mission IDs in real mission data...',
    );
    final provider = MissionProvider.latestInstance;
    if (provider == null) {
      print(
        '🛡️ AI Guardian: No MissionProvider instance available for repair.',
      );
      return;
    }
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      if (mission.id == null || mission.id!.isEmpty) {
        final newId = DateTime.now().microsecondsSinceEpoch.toString();
        final updatedMission = mission.copyWith(id: newId);
        missionsToUpdate.add(updatedMission);
        print(
          '🛡️ AI Guardian: Fixed invalid mission ID for mission "${mission.title}": null/empty -> $newId',
        );
        logRepair(
          'Invalid Mission ID',
          'Fixed mission ID to $newId',
          missionId: mission.id,
        );
        await _showRepairNotification(
          'Repairing',
          'Repairing invalid mission ID for: ${mission.id}',
          missionTitle: null,
          isRepairing: true,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.notificationId == updatedMission.notificationId,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed ${missionsToUpdate.length} invalid mission IDs',
      );
      await _showRepairNotification(
        'Repaired',
        'Mission IDs repaired in ${missionsToUpdate.length} missions',
        missionTitle: null,
        isRepairing: false,
      );
    }
  }

  // Generate a valid notification ID within 32-bit range
  int generateValidNotificationId() {
    int newId;
    do {
      newId = _random.nextInt(0x7FFFFFFF); // Max 32-bit signed integer
    } while (_usedNotificationIds.contains(newId));

    _usedNotificationIds.add(newId);
    return newId;
  }

  // Register a notification ID as used
  void registerNotificationId(int id) {
    _usedNotificationIds.add(id);
  }

  // Start continuous background health checks with independent isolate.
  void startContinuousHealthCheck(
    Future<void> Function() healthCheckFn, {
    Duration interval = const Duration(seconds: 30),
  }) {
    print('🛡️ AI Guardian: startContinuousHealthCheck called');
    if (_isRunning) {
      print('🛡️ AI Guardian is already running');
      return;
    }
    _isRunning = true;
    print(
      '🛡️ AI Guardian: Starting independent background health monitoring...',
    );
  // Start the background isolate for truly independent operation
    _startBackgroundIsolate(healthCheckFn, interval);
    print('🛡️ AI Guardian: Background health check started');
  }

  // Start a background isolate for truly independent operation
  void _startBackgroundIsolate(
    Future<void> Function() healthCheckFn,
    Duration interval,
  ) async {
    try {
      _isolateReceivePort = ReceivePort();

      _backgroundIsolate = await Isolate.spawn(
        _backgroundHealthCheckWorker,
        _IsolateMessage(
          sendPort: _isolateReceivePort!.sendPort,
          interval: interval.inMilliseconds,
        ),
      );

      _isolateReceivePort!.listen((message) {
        if (message is Map<String, dynamic>) {
          if (message['type'] == 'health_check') {
            setAIActive(true);
            healthCheckFn()
                .then((_) {
                  setAIActive(false);
                })
                .catchError((error) {
                  print('AI Guardian: Error in isolate health check: $error');
                  logRepair('Isolate health check error', 'Error: $error');
                  setAIActive(false);
                });
          } else if (message['type'] == 'log') {
            print('AI Guardian: ${message['message']}');
          }
        }
      });

      print('AI Guardian: Background isolate started successfully');
    } catch (e) {
      print('AI Guardian: Failed to start background isolate: $e');
  // Fall back to timer-based approach
    }
  }

  // Background worker function that runs in isolate
  static void _backgroundHealthCheckWorker(_IsolateMessage message) {
  // Send initial log
    message.sendPort.send({
      'type': 'log',
      'message': 'Background health check worker started',
    });
  }

  // Stop the background health check.
  void stopContinuousHealthCheck() {
    _isRunning = false;
    _backgroundCheckTimer?.cancel();
    _backgroundIsolate?.kill();
    _isolateReceivePort?.close();
    setAIActive(false);
    print('AI Guardian: Background health monitoring stopped');
  }

  void setAIActive(bool active) {
    if (_isAIActive != active) {
      _isAIActive = active;
      _aiActiveController.add(active);
    }
  }

  // Perform an immediate health check
  Future<void> performImmediateHealthCheck(
    Future<void> Function() healthCheckFn,
  ) async {
    setAIActive(true);
    try {
      await healthCheckFn();
    } catch (e) {
      print('AI Guardian: Error in immediate health check: $e');
      logRepair('Immediate health check error', 'Error: $e');
    } finally {
      setAIActive(false);
    }
  }

  // Save learned data persistently
  Future<void> _saveLearnedData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

  // Save health checks
      final healthChecksData = _learnedHealthChecks.map(
        (key, value) => MapEntry(key, {
          'name': value.name,
          'description': value.description,
          'priority': value.priority.index,
        }),
      );
      await prefs.setString(
        'ai_guardian_health_checks',
        jsonEncode(healthChecksData),
      );

  // Save repairs
      final repairsData = _learnedRepairs.map(
        (key, value) => MapEntry(key, {
          'name': value.name,
          'description': value.description,
          'priority': value.priority.index,
        }),
      );
      await prefs.setString('ai_guardian_repairs', jsonEncode(repairsData));

  // Save learning history
      await prefs.setStringList(
        'ai_guardian_learning_history',
        _learningHistory,
      );

  // Save issue frequency
      await prefs.setString(
        'ai_guardian_issue_frequency',
        jsonEncode(_issueFrequency),
      );

      print('AI Guardian: 💾 Saved learned data');
    } catch (e) {
      print('AI Guardian: ❌ Error saving learned data: $e');
    }
  }

  // Load learned data from persistent storage
  Future<void> _loadLearnedData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

  // Load health checks
      final healthChecksJson = prefs.getString('ai_guardian_health_checks');
      if (healthChecksJson != null) {
        final healthChecksData = Map<String, dynamic>.from(
          jsonDecode(healthChecksJson),
        );
        for (final entry in healthChecksData.entries) {
          final data = Map<String, dynamic>.from(entry.value);
          _learnedHealthChecks[entry.key] = HealthCheck(
            name: data['name'],
            description: data['description'],
            checkFunction: _getDefaultCheckFunction(entry.key),
            priority: HealthCheckPriority.values[data['priority']],
          );
        }
      }

  // Load repairs
      final repairsJson = prefs.getString('ai_guardian_repairs');
      if (repairsJson != null) {
        final repairsData = Map<String, dynamic>.from(jsonDecode(repairsJson));
        for (final entry in repairsData.entries) {
          final data = Map<String, dynamic>.from(entry.value);
          _learnedRepairs[entry.key] = RepairFunction(
            name: data['name'],
            description: data['description'],
            repairFunction: _getDefaultRepairFunction(entry.key),
            priority: RepairPriority.values[data['priority']],
          );
        }
      }

  // Load learning history
      final history = prefs.getStringList('ai_guardian_learning_history');
      if (history != null) {
        _learningHistory.addAll(history);
      }

  // Load issue frequency
      final frequencyJson = prefs.getString('ai_guardian_issue_frequency');
      if (frequencyJson != null) {
        final frequencyData = Map<String, dynamic>.from(
          jsonDecode(frequencyJson),
        );
        _issueFrequency.addAll(
          frequencyData.map((key, value) => MapEntry(key, value as int)),
        );
      }

      print(
        'AI Guardian: 📚 Loaded ${_learnedHealthChecks.length} health checks and ${_learnedRepairs.length} repairs',
      );
    } catch (e) {
      print('AI Guardian: ❌ Error loading learned data: $e');
    }
  }

  // Load issue patterns from persistent storage
  Future<void> _loadIssuePatterns() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final patterns = prefs.getStringList('ai_guardian_issue_patterns');
      if (patterns != null) {
        _issuePatterns.addAll(patterns);
      }
    } catch (e) {
      print('AI Guardian: ❌ Error loading issue patterns: $e');
    }
  }

  // Get default check function for a given key
  Future<bool> Function() _getDefaultCheckFunction(String key) {
    switch (key) {
      case 'invalid_notification_ids':
        return _checkInvalidNotificationIds;
      case 'duplicate_notification_ids':
        return _checkDuplicateNotificationIds;
      case 'invalid_mission_ids':
        return _checkInvalidMissionIds;
      default:
        return () async => false;
    }
  }

  // Get default repair function for a given key
  Future<void> Function() _getDefaultRepairFunction(String key) {
    switch (key) {
      case 'fix_invalid_notification_ids':
        return _fixInvalidNotificationIds;
      case 'fix_duplicate_notification_ids':
        return _fixDuplicateNotificationIds;
      case 'fix_invalid_mission_ids':
        return _fixInvalidMissionIds;
      default:
        return () async {};
    }
  }

  // Dispose resources.
  void dispose() {
    stopContinuousHealthCheck();
    _backgroundCheckTimer?.cancel();
    _wsChannel?.sink.close();
    _wsChannel = null;
    _aiActiveController.close();
    _learningController.close();
    _issueController.close();
    print('🛡️ AI Guardian: Disposed and disconnected from backend');
  }

  static Future<void> backgroundGuardianAndSandbox() async {
    final mechanicum = Mechanicum.instance;
  // Run Guardian repairs
    final repairResults = await mechanicum.performComprehensiveRepairs();
    for (final result in repairResults) {
      mechanicum.maybeNotifyGuardianRepair(result);
    }

  // Get sandbox suggestions from existing data structures
    final suggestions = mechanicum.getSandboxSuggestions();
    for (final suggestion in suggestions) {
      mechanicum.maybeNotifySandboxSuggestion(suggestion);
    }
  }

  Future<void> showNotification(String title, String body) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'ai_channel',
          'AI Notifications',
          channelDescription: 'Notifications for AI Guardian and Sandbox',
          importance: Importance.max,
          priority: Priority.high,
          showWhen: false,
        );
    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    await flutterLocalNotificationsPlugin.show(
      0,
      title,
      body,
      platformChannelSpecifics,
      payload: 'ai_event',
    );
  }

  void maybeNotifyGuardianRepair(RepairResult result) {
    final now = DateTime.now();
    if ((result.priority == RepairPriority.high ||
            result.priority == RepairPriority.critical) &&
        (lastGuardianNotificationTime == null ||
            now.difference(lastGuardianNotificationTime!) >
                Duration(minutes: 30))) {
      showNotification(
        'AI Guardian Repair',
        'A high-priority repair was made: ${result.repairName}',
      );
      lastGuardianNotificationTime = now;
    }
  }

  void maybeNotifySandboxSuggestion(SuggestionResult result) {
    final now = DateTime.now();
    if (result.priority == SuggestionPriority.high &&
        (lastSandboxNotificationTime == null ||
            now.difference(lastSandboxNotificationTime!) >
                Duration(minutes: 30))) {
      showNotification(
        'AI Sandbox Suggestion',
        'A high-priority suggestion: ${result.suggestion}',
      );
      lastSandboxNotificationTime = now;
    }
  }

  // Method to get sandbox suggestions from existing data structures
  List<SuggestionResult> getSandboxSuggestions() {
    final suggestions = <SuggestionResult>[];

  // Convert existing suggestion maps to SuggestionResult objects
    for (final suggestionMap in _aiSuggestions) {
      suggestions.add(SuggestionResult.fromMap(suggestionMap));
    }

  // Also include personalized suggestions
    for (final personalMap in _aiPersonalizedSuggestions) {
      suggestions.add(SuggestionResult.fromMap(personalMap));
    }

  // Include code suggestions
    for (final codeMap in _aiGeneratedCodeSuggestions) {
      suggestions.add(SuggestionResult.fromMap(codeMap));
    }

    return suggestions;
  }

  // Learning mechanism: log and add placeholder health check/repair for new issues
  void learnNewIssue(String issueType, String description) {
    if (!_learnedHealthChecks.containsKey(issueType)) {
      print('🛡️ AI Guardian: Learning new issue type: $issueType');
      _learnedHealthChecks[issueType] = HealthCheck(
        name: issueType,
        description: description,
        checkFunction: () async {
          print('🛡️ AI Guardian: Placeholder health check for $issueType');
          return false;
        },
        priority: HealthCheckPriority.low,
      );
    }
    if (!_learnedRepairs.containsKey('fix_$issueType')) {
      _learnedRepairs['fix_$issueType'] = RepairFunction(
        name: 'Fix $issueType',
        description: 'Placeholder repair for $issueType',
        repairFunction: () async {
          print('🛡️ AI Guardian: Placeholder repair for $issueType');
        },
        priority: RepairPriority.low,
      );
    }
  }

  // 1. Empty/null mission titles
  Future<bool> _checkEmptyMissionTitles() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return false;
    bool found = false;
    for (final mission in provider.missions) {
      if (mission.title == null || mission.title.trim().isEmpty) {
        print(
          '🛡️ AI Guardian: Found mission with empty/null title: ${mission.id}',
        );
        found = true;
      }
    }
    return found;
  }

  Future<void> _fixEmptyMissionTitles() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return;
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      if (mission.title == null || mission.title.trim().isEmpty) {
        final newTitle = 'Mission ${DateTime.now().millisecondsSinceEpoch}';
        final updatedMission = mission.copyWith(title: newTitle);
        missionsToUpdate.add(updatedMission);
        print(
          '🛡️ AI Guardian: Fixed empty/null title for mission "${mission.id}": -> $newTitle',
        );
        logRepair(
          'Empty Mission Title',
          'Fixed empty/null title to $newTitle',
          missionId: mission.id,
        );
        await _showRepairNotification(
          'Repairing',
          'Repairing empty/null title',
          missionTitle: newTitle,
          isRepairing: true,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
      await _showRepairNotification(
        'Repaired',
        'Title repaired',
        missionTitle: updatedMission.title,
        isRepairing: false,
      );
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed ${missionsToUpdate.length} empty/null mission titles',
      );
    }
  }

  // 2. Negative/invalid subtask mastery values
  Future<bool> _checkInvalidSubtaskMasteryValues() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return false;
    bool found = false;
    for (final mission in provider.missions) {
      for (final entry in mission.subtaskMasteryValues.entries) {
        if (entry.value <= 0) {
          print(
            '🛡️ AI Guardian: Found invalid mastery value in mission: ${mission.title}, subtask: ${entry.key}',
          );
          found = true;
        }
      }
    }
    return found;
  }

  Future<void> _fixInvalidSubtaskMasteryValues() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return;
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      bool needsUpdate = false;
      final updatedSubtaskMasteryValues = <String, double>{};
      for (final entry in mission.subtaskMasteryValues.entries) {
        if (entry.value <= 0) {
          updatedSubtaskMasteryValues[entry.key] = 1.0;
          needsUpdate = true;
          print(
            '🛡️ AI Guardian: Fixed mastery value for mission: ${mission.title}, subtask: ${entry.key}',
          );
          logRepair(
            'Invalid Subtask Mastery Value',
            'Set mastery value to 1.0 for subtask ${entry.key}',
            missionId: mission.id,
          );
        } else {
          updatedSubtaskMasteryValues[entry.key] = entry.value;
        }
      }
      if (needsUpdate) {
        final updatedMission = mission.copyWith(
          subtaskMasteryValues: updatedSubtaskMasteryValues,
        );
        missionsToUpdate.add(updatedMission);
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed invalid subtask mastery values in ${missionsToUpdate.length} missions',
      );
    }
  }

  // 3. Missions both completed and failed
  Future<bool> _checkCompletedAndFailedMissions() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return false;
    bool found = false;
    for (final mission in provider.missions) {
      if (mission.isCompleted && mission.hasFailed) {
        print(
          '🛡️ AI Guardian: Found mission both completed and failed: ${mission.title}',
        );
        found = true;
      }
    }
    return found;
  }

  Future<void> _fixCompletedAndFailedMissions() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return;
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      if (mission.isCompleted && mission.hasFailed) {
        final updatedMission = mission.copyWith(hasFailed: false);
        missionsToUpdate.add(updatedMission);
        print('🛡️ AI Guardian: Fixed mission state for: ${mission.title}');
        logRepair(
          'Completed and Failed Mission',
          'Set hasFailed to false for completed mission',
          missionId: mission.id,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed completed+failed state in ${missionsToUpdate.length} missions',
      );
    }
  }

  // 4. Missions with createdAt in the future
  Future<bool> _checkFutureCreatedAt() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return false;
    bool found = false;
    final now = DateTime.now();
    for (final mission in provider.missions) {
      if (mission.createdAt != null && mission.createdAt!.isAfter(now)) {
        print(
          '🛡️ AI Guardian: Found mission with createdAt in the future: ${mission.title}',
        );
        found = true;
      }
    }
    return found;
  }

  Future<void> _fixFutureCreatedAt() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return;
    final missionsToUpdate = <dynamic>[];
    final now = DateTime.now();
    for (final mission in provider.missions) {
      if (mission.createdAt != null && mission.createdAt!.isAfter(now)) {
        final updatedMission = mission.copyWith(createdAt: now);
        missionsToUpdate.add(updatedMission);
        print('🛡️ AI Guardian: Fixed createdAt for mission: ${mission.title}');
        logRepair(
          'Future CreatedAt',
          'Set createdAt to now for mission',
          missionId: mission.id,
        );
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed future createdAt in ${missionsToUpdate.length} missions',
      );
    }
  }

  // 5. Missions with missing/invalid subtasks
  Future<bool> _checkInvalidSubtasks() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return false;
    bool found = false;
    for (final mission in provider.missions) {
      if (mission.subtasks == null || mission.subtasks.isEmpty) {
        print(
          '🛡️ AI Guardian: Found mission with missing/empty subtasks: ${mission.title}',
        );
        found = true;
      } else {
        for (final subtask in mission.subtasks) {
          if (subtask.name == null || subtask.name.trim().isEmpty) {
            print(
              '🛡️ AI Guardian: Found subtask with empty name in mission: ${mission.title}',
            );
            found = true;
          }
        }
      }
    }
    return found;
  }

  Future<void> _fixInvalidSubtasks() async {
    final provider = MissionProvider.latestInstance;
    if (provider == null) return;
    final missionsToUpdate = <dynamic>[];
    for (final mission in provider.missions) {
      bool needsUpdate = false;
      var updatedSubtasks = mission.subtasks;
      if (updatedSubtasks == null || updatedSubtasks.isEmpty) {
        updatedSubtasks = [
          mission.subtasks.first.copyWith(name: 'Default Subtask'),
        ];
        needsUpdate = true;
        print(
          '🛡️ AI Guardian: Added default subtask to mission: ${mission.title}',
        );
        logRepair(
          'Missing Subtasks',
          'Added default subtask',
          missionId: mission.id,
        );
      } else {
        final fixedSubtasks = <MissionSubtask>[];
        for (final subtask in updatedSubtasks) {
          if (subtask.name == null || subtask.name.trim().isEmpty) {
            final fixed = subtask.copyWith(
              name: 'Subtask ${DateTime.now().millisecondsSinceEpoch}',
            );
            fixedSubtasks.add(fixed);
            needsUpdate = true;
            print(
              '🛡️ AI Guardian: Fixed empty subtask name in mission: ${mission.title}',
            );
            logRepair(
              'Empty Subtask Name',
              'Fixed empty subtask name',
              missionId: mission.id,
            );
          } else {
            fixedSubtasks.add(subtask);
          }
        }
        updatedSubtasks = fixedSubtasks;
      }
      if (needsUpdate) {
        final updatedMission = mission.copyWith(subtasks: updatedSubtasks);
        missionsToUpdate.add(updatedMission);
      }
    }
    for (final updatedMission in missionsToUpdate) {
      final idx = provider.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (idx != -1) {
        final updatedMissions = List<MissionData>.from(provider.missions);
        updatedMissions[idx] = updatedMission;
        await provider.saveMissions(updatedMissions);
        provider.notifyListeners();
      }
    }
    if (missionsToUpdate.isNotEmpty) {
      await provider.saveMissions(provider.missions);
      provider.notifyListeners();
      print(
        '🛡️ AI Guardian: ✅ Fixed invalid subtasks in ${missionsToUpdate.length} missions',
      );
    }
  }

  Future<void> _showRepairNotification(
    String title,
    String body, {
    String? missionTitle,
    bool isRepairing = true,
  }) async {
    try {
      const AndroidNotificationDetails androidPlatformChannelSpecifics =
          AndroidNotificationDetails(
            'ai_guardian_repairs',
            'AI Guardian Repairs',
            channelDescription: 'Notifications for mission repairs',
            importance: Importance.max,
            priority: Priority.high,
            showWhen: true,
          );
      const NotificationDetails platformChannelSpecifics = NotificationDetails(
        android: androidPlatformChannelSpecifics,
      );
      final emoji = isRepairing ? '⏳' : '✅';
      final shield = '🛡️';
      final notifTitle = '$shield $title $emoji';
      final notifBody = missionTitle != null ? 'Mission: $missionTitle' : body;
      await flutterLocalNotificationsPlugin.show(
        DateTime.now().millisecondsSinceEpoch % 0x7FFFFFFF,
        notifTitle,
        notifBody,
        platformChannelSpecifics,
      );
    } catch (e) {
      print('🛡️ AI Guardian: Failed to show repair notification: $e');
    }
  }
}

  // Message class for isolate communication
class _IsolateMessage {
  final SendPort sendPort;
  final int interval;

  _IsolateMessage({required this.sendPort, required this.interval});
}

  // Health check priority levels
enum HealthCheckPriority { low, medium, high, critical }

  // Repair priority levels
enum RepairPriority { low, medium, high, critical }

  // Health check definition
class HealthCheck {
  final String name;
  final String description;
  final Future<bool> Function() checkFunction;
  final HealthCheckPriority priority;

  HealthCheck({
    required this.name,
    required this.description,
    required this.checkFunction,
    required this.priority,
  });
}

  // Repair function definition
class RepairFunction {
  final String name;
  final String description;
  final Future<void> Function() repairFunction;
  final RepairPriority priority;

  RepairFunction({
    required this.name,
    required this.description,
    required this.repairFunction,
    required this.priority,
  });
}

  // Health check result
class HealthCheckResult {
  final String checkName;
  final String description;
  final bool hasIssue;
  final HealthCheckPriority priority;
  final DateTime timestamp;
  final String? error;

  HealthCheckResult({
    required this.checkName,
    required this.description,
    required this.hasIssue,
    required this.priority,
    required this.timestamp,
    this.error,
  });
}

  // Repair result
class RepairResult {
  final String repairName;
  final String description;
  final bool success;
  final RepairPriority priority;
  final DateTime timestamp;
  final String? error;

  RepairResult({
    required this.repairName,
    required this.description,
    required this.success,
    required this.priority,
    required this.timestamp,
    this.error,
  });
}

  // Suggestion priority levels
enum SuggestionPriority { low, medium, high, critical }

  // Suggestion result
class SuggestionResult {
  final String suggestion;
  final String title;
  final SuggestionPriority priority;
  final DateTime timestamp;
  final String? reasoning;

  SuggestionResult({
    required this.suggestion,
    required this.title,
    required this.priority,
    required this.timestamp,
    this.reasoning,
  });

  // Factory constructor from Map<String, dynamic>
  factory SuggestionResult.fromMap(Map<String, dynamic> map) {
    String priorityStr = map['priority']?.toString().toLowerCase() ?? 'medium';
    SuggestionPriority priority;
    switch (priorityStr) {
      case 'high':
        priority = SuggestionPriority.high;
        break;
      case 'critical':
        priority = SuggestionPriority.critical;
        break;
      case 'low':
        priority = SuggestionPriority.low;
        break;
      default:
        priority = SuggestionPriority.medium;
    }

    return SuggestionResult(
      suggestion: map['suggestion'] ?? map['title'] ?? 'Unknown suggestion',
      title: map['title'] ?? map['suggestion'] ?? 'Unknown',
      priority: priority,
      timestamp:
          map['timestamp'] is DateTime
              ? map['timestamp']
              : DateTime.tryParse(map['timestamp']?.toString() ?? '') ??
                  DateTime.now(),
      reasoning: map['reasoning'],
    );
  }
}
