import 'dart:convert';
import 'dart:math';
import 'dart:async';
import 'dart:isolate';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/core/error/app_error.dart';
import 'package:the_codex/mastery_list.dart';
import 'package:timezone/data/latest.dart' as tz;
import 'dart:developer' as developer;
import 'package:app_badge_plus/app_badge_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:analyzer/dart/analysis/utilities.dart';
import 'package:analyzer/dart/ast/ast.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'ai_file_system_helper.dart';

import 'mission.dart';
import 'providers/app_history_provider.dart';
import 'mechanicum.dart';
import 'ai_brain.dart';

final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

/// Data class to hold the results from the AI sandbox isolate.
class _SandboxResult {
  final List<Map<String, String>> testFeed;
  final Map<String, dynamic> knowledgeGraph;
  final List<Map<String, String>> codeSuggestions;
  final List<Map<String, String>> extensionIdeas;
  final List<Map<String, String>> personalizedSuggestions;

  _SandboxResult({
    required this.testFeed,
    required this.knowledgeGraph,
    required this.codeSuggestions,
    required this.extensionIdeas,
    required this.personalizedSuggestions,
  });
}

/// Data class for the isolate request
class _SandboxRequest {
  final SendPort sendPort;
  final Map<String, String> suggestionFeedback;

  _SandboxRequest(this.sendPort, this.suggestionFeedback);
}

// Top-level function to be executed in the isolate

class MechanicumSandboxResult {
  final bool success;
  final String summary;
  final List<String> changes;
  final List<String> testResults;
  final Map<String, dynamic> sandboxState;

  MechanicumSandboxResult({
    required this.success,
    required this.summary,
    required this.changes,
    required this.testResults,
    required this.sandboxState,
  });
}

class NotificationChannels {
  static const String mission = 'mission_channel';
  static const String summary = 'summary_channel';
  static const String groupKey = 'com.example.lvl_up.missions';

  static const AndroidNotificationChannel missionChannel =
      AndroidNotificationChannel(
        mission,
        'Missions',
        description: 'Mission notifications',
        importance: Importance.max,
        playSound: true,
        enableVibration: true,
        showBadge: true,
        enableLights: true,
        ledColor: Colors.blue,
      );
}

class MissionProviderEnhancements {
  Timer? _notificationUpdateTimer;
  final Set<int> _pendingNotificationUpdates = {};
  final Map<int, NotificationDetails> _notificationCache = {};

  Future<void> _scheduleNotificationUpdate(
    MissionProvider provider,
    MissionData mission,
  ) async {
    _pendingNotificationUpdates.add(mission.notificationId);
    _notificationUpdateTimer?.cancel();
    _notificationUpdateTimer = Timer(
      const Duration(milliseconds: 300),
      () async {
        await _processPendingNotificationUpdates(provider);
      },
    );
  }

  Future<void> _processPendingNotificationUpdates(
    MissionProvider provider,
  ) async {
    final missionIds = List<int>.from(_pendingNotificationUpdates);
    _pendingNotificationUpdates.clear();
    for (final missionId in missionIds) {
      final mission = provider._missions.firstWhere(
        (m) => m.notificationId == missionId,
        orElse: () => throw StateError('Mission not found'),
      );
      await provider._scheduleNotification(
        mission,
        useEnhancements: false,
      ); // Avoid recursion
    }
    await provider._showSummaryNotification();
  }

  String _getEnhancedStatusEmoji(MissionData mission) {
    if (mission.hasFailed) return '❌';
    if (mission.isCompleted) return '✅';
    final progressPercent = mission.completionPercentage;
    if (progressPercent >= 0.75) return '🟢';
    if (progressPercent >= 0.5) return '🟡';
    if (progressPercent > 0) return '🔄';
    return '⚪';
  }

  String _buildOptimizedNotificationContent(MissionData mission) {
    final content = StringBuffer();
    if (mission.description.isNotEmpty) {
      content.writeln(mission.description);
    }
    if (mission.isCounterBased) {
      content.writeln(_buildCounterProgress(mission));
    } else if (mission.subtasks.isNotEmpty) {
      content.writeln(_buildSubtaskProgress(mission));
    }
    if (!mission.isCounterBased) {
      final percentage = (mission.completionPercentage * 100).toInt();
      content.writeln('Progress: $percentage%');
    }
    if (mission.hasFailed) {
      content.writeln('\n⚠️ MISSION FAILED - GET SHIT DONE !!!!');
    }
    return content.toString().trim();
  }

  String _buildCounterProgress(MissionData mission) {
    final buffer = StringBuffer('Count: ${mission.currentCount}');
    if (mission.targetCount > 0) {
      buffer.write(' / ${mission.targetCount}');
      final percentage =
          (mission.currentCount / mission.targetCount * 100).toInt();
      buffer.write(' ($percentage%)');
    }
    return buffer.toString();
  }

  /// Build notification details for a mission
  Future<NotificationDetails> _buildNotificationDetails(
    MissionData mission, {
    List<AndroidNotificationAction>? actions,
    bool isSummary = false,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      NotificationChannels.mission,
      'Mission Notifications',
      channelDescription: 'Notifications for mission updates',
      importance: Importance.max,
      priority: Priority.max,
      groupKey: NotificationChannels.groupKey,
      setAsGroupSummary: isSummary,
      groupAlertBehavior: GroupAlertBehavior.all,
      ongoing: !mission.isCompleted && !isSummary,
      autoCancel: false,
      actions: actions,
      icon: '@mipmap/ic_launcher',
      largeIcon: const DrawableResourceAndroidBitmap('@mipmap/ic_launcher'),
      styleInformation: BigTextStyleInformation(
        _buildOptimizedNotificationContent(mission),
        contentTitle: '${_getEnhancedStatusEmoji(mission)} ${mission.title}',
        htmlFormatContent: false,
        htmlFormatTitle: false,
      ),
      visibility: NotificationVisibility.public,
      onlyAlertOnce: false,
      showWhen: true,
      enableLights: true,
      ledColor: Colors.blue,
      playSound: true,
      enableVibration: true,
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
      threadIdentifier: NotificationChannels.groupKey,
      interruptionLevel: InterruptionLevel.timeSensitive,
    );

    return NotificationDetails(android: androidDetails, iOS: iosDetails);
  }

  String _buildSubtaskProgress(MissionData mission) {
    final buffer = StringBuffer('Tasks:\n');
    for (final subtask in mission.subtasks) {
      final emoji = _getSubtaskEmoji(subtask);
      final progress =
          subtask.isCounterBased
              ? '${subtask.currentCount}${subtask.requiredCompletions > 0 ? '/${subtask.requiredCompletions}' : ''}'
              : '${subtask.currentCompletions}/${subtask.requiredCompletions}';
      buffer.writeln('$emoji ${subtask.name}: $progress');
    }
    return buffer.toString().trim();
  }

  String _getSubtaskEmoji(MissionSubtask subtask) {
    final isComplete =
        subtask.isCounterBased
            ? subtask.currentCount >=
                (subtask.requiredCompletions > 0
                    ? subtask.requiredCompletions
                    : 1)
            : subtask.currentCompletions >= subtask.requiredCompletions;
    if (isComplete) return '✅';
    final hasProgress =
        subtask.isCounterBased
            ? subtask.currentCount > 0
            : subtask.currentCompletions > 0;
    return hasProgress ? '🔄' : '⚪';
  }

  List<AndroidNotificationAction> _buildOptimizedActions(MissionData mission) {
    final actions = <AndroidNotificationAction>[];

    // Add actions for subtasks
    for (var subtask in mission.subtasks) {
      if (subtask.isCounterBased) {
        actions.add(
          AndroidNotificationAction(
            'progress_${mission.notificationId}_${subtask.name}',
            '', // Empty text for counter-based subtasks
            showsUserInterface: false,
            cancelNotification: false,
          ),
        );
      } else if (subtask.currentCompletions < subtask.requiredCompletions) {
        actions.add(
          AndroidNotificationAction(
            'progress_${mission.notificationId}_${subtask.name}',
            'Progress ${subtask.name}',
            showsUserInterface: false,
            cancelNotification: false,
          ),
        );
      }
    }

    // Add increment action for counter-based missions with no subtasks
    if (mission.isCounterBased &&
        mission.subtasks.isEmpty &&
        !mission.isCompleted) {
      actions.add(
        AndroidNotificationAction(
          'increment_${mission.notificationId}',
          'Increment',
          showsUserInterface: false,
          cancelNotification: false,
        ),
      );
    }

    // Add complete action for missions without subtasks
    if (mission.subtasks.isEmpty && !mission.isCompleted) {
      actions.add(
        AndroidNotificationAction(
          'complete_${mission.notificationId}',
          'Mark Complete',
          showsUserInterface: false,
          cancelNotification: false,
        ),
      );
    }

    return actions;
  }

  Future<NotificationDetails> _getCachedNotificationDetails(
    MissionData mission, {
    List<AndroidNotificationAction>? actions,
    bool isSummary = false,
  }) async {
    final cacheKey = _generateCacheKey(mission, actions, isSummary);
    if (_notificationCache.containsKey(cacheKey)) {
      return _notificationCache[cacheKey]!;
    }
    final details = await _buildNotificationDetails(
      mission,
      actions: actions,
      isSummary: isSummary,
    );
    _notificationCache[cacheKey] = details;
    return details;
  }

  int _generateCacheKey(
    MissionData mission,
    List<AndroidNotificationAction>? actions,
    bool isSummary,
  ) {
    return Object.hash(
      mission.notificationId,
      mission.isCompleted,
      mission.hasFailed,
      mission.completionPercentage,
      actions?.length ?? 0,
      isSummary,
    );
  }

  Future<void> _safeNotificationOperation(
    String operationName,
    Future<void> Function() operation,
  ) async {
    try {
      await operation();
    } catch (e, stackTrace) {
      developer.log(
        'Error in $operationName: $e',
        error: e,
        stackTrace: stackTrace,
      );
    }
  }
}

class MissionProvider extends ChangeNotifier {
  static MissionProvider? latestInstance;
  List<MissionData> _missions = [];
  List<MissionData> _completedMissions = [];
  List<MissionData> _deletedMissions = [];
  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();
  final Map<DateTime, int> _dailyGoalsCreated = {};
  final Set<String> _usedImages = {}; // Track used image URLs
  bool _isTestingMode = false;
  bool _isDailyLocked = false;
  bool _isWeeklyLocked = false;
  Color _refreshButtonColor = Colors.white;
  DateTime? _lastRefreshTime;
  bool _notificationsInitialized = false;

  // AI Guardian instance
  final mechanicum = Mechanicum.instance;

  // Add repair log
  final List<String> _repairLog = [];
  List<String> getRepairLog() => List.unmodifiable(_repairLog);

  // Persistent repair log loading
  Future<void> loadRepairLog() async {
    final prefs = await SharedPreferences.getInstance();
    final logString = prefs.getString('mission_repair_log');
    if (logString != null) {
      final List<dynamic> decoded = jsonDecode(logString);
      _repairLog.clear();
      _repairLog.addAll(decoded.cast<String>());
    }
  }

  // Save repair log persistently
  Future<void> _saveRepairLog() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('mission_repair_log', jsonEncode(_repairLog));
  }

  // Add StreamController for mission updates
  final _missionController = StreamController<void>.broadcast();
  Stream<void> get missionStream => _missionController.stream;

  final MissionProviderEnhancements _enhancements =
      MissionProviderEnhancements();

  bool _isSameDay(DateTime a, DateTime b) {
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  // Add method to check for missed refreshes
  Future<void> _checkMissedRefreshes() async {
    try {
      final now = DateTime.now();
      bool needsRefresh = false;

      // Check for missed daily refreshes
      if (now.hour < 12) {
        for (final mission in _missions.where(
          (m) => m.type == MissionType.daily,
        )) {
          if (mission.createdAt != null &&
              !_isSameDay(mission.createdAt!, now)) {
            needsRefresh = true;
            _refreshButtonColor = Colors.red;
            _isDailyLocked = true;
            break;
          }
        }
      }

      // Check for missed weekly refreshes
      if (now.weekday == DateTime.monday && now.hour < 12) {
        for (final mission in _missions.where(
          (m) => m.type == MissionType.weekly,
        )) {
          if (mission.createdAt != null &&
              mission.createdAt!.isBefore(
                now.subtract(const Duration(days: 1)),
              )) {
            needsRefresh = true;
            _refreshButtonColor = Colors.orange;
            _isWeeklyLocked = true;
            break;
          }
        }
      }

      if (needsRefresh) {
        notifyListeners();
        await _performBackgroundRefresh();
      }
    } catch (e) {
      developer.log('Error checking missed refreshes: $e');
    }
  }

  Future<void> requestNotificationPermission() async {
    var status = await Permission.notification.status;
    if (!status.isGranted) {
      status = await Permission.notification.request();
      if (!status.isGranted) {
        developer.log('Notification permission denied');
      } else {
        developer.log('Notification permission granted');
      }
    }
  }

  bool _hasMeaningfulProgress(MissionData mission) {
    // For counter-based missions
    if (mission.isCounterBased) {
      if (mission.targetCount > 0) {
        return mission.currentCount < mission.targetCount;
      }
      return mission.currentCount < 1;
    }

    // For missions with subtasks
    if (mission.subtasks.isNotEmpty) {
      return mission.subtasks.any((subtask) {
        if (subtask.isCounterBased) {
          if (subtask.requiredCompletions > 0) {
            return subtask.currentCount < subtask.requiredCompletions;
          }
          return subtask.currentCount < 1;
        } else {
          return subtask.currentCompletions < subtask.requiredCompletions;
        }
      });
    }

    // For simple missions
    return !mission.isCompleted;
  }

  Future<bool> _isValidMissionState(MissionData mission) async {
    try {
      // Validate mission identifiers
      if (mission.id == null ||
          mission.missionId == null ||
          mission.notificationId == null) {
        developer.log(
          'Mission validation failed: Missing identifiers for ${mission.title}',
        );
        await _logMissionValidation(
          mission: mission,
          isValid: false,
          reason: 'Missing mission identifiers',
        );
        return false;
      }

      // Check for duplicate identifiers
      final hasDuplicateId = _missions.any(
        (m) => m.id == mission.id && m.notificationId != mission.notificationId,
      );
      if (hasDuplicateId) {
        developer.log(
          'Mission validation failed: Duplicate ID detected for ${mission.title}',
        );
        await _logMissionValidation(
          mission: mission,
          isValid: false,
          reason: 'Duplicate mission ID',
        );
        return false;
      }

      // Validate mission type and state
      if (mission.type == MissionType.daily ||
          mission.type == MissionType.weekly) {
        if (mission.createdAt == null) {
          developer.log(
            'Mission validation failed: Missing creation date for ${mission.title}',
          );
          await _logMissionValidation(
            mission: mission,
            isValid: false,
            reason: 'Missing creation date',
          );
          return false;
        }
      }

      // Validate counter-based mission
      if (mission.isCounterBased) {
        if (mission.currentCount < 0 || mission.targetCount < 0) {
          developer.log('Invalid counter values for mission: ${mission.title}');
          await _logMissionValidation(
            mission: mission,
            isValid: false,
            reason: 'Invalid counter values',
          );
          return false;
        }
      }

      // Validate subtasks
      if (mission.subtasks.isNotEmpty) {
        for (final subtask in mission.subtasks) {
          if (!_validateSubtaskState(subtask)) {
            developer.log('Invalid subtask state in mission: ${mission.title}');
            await _logMissionValidation(
              mission: mission,
              isValid: false,
              reason: 'Invalid subtask state',
            );
            return false;
          }
        }
      }

      // Validate completion state
      if (mission.isCompleted && mission.hasFailed) {
        developer.log(
          'Invalid state: mission cannot be both completed and failed: ${mission.title}',
        );
        await _logMissionValidation(
          mission: mission,
          isValid: false,
          reason: 'Mission cannot be both completed and failed',
        );
        return false;
      }

      // Validate mastery values
      if (mission.linkedMasteryId != null && mission.masteryValue <= 0) {
        developer.log('Invalid mastery value for mission: ${mission.title}');
        await _logMissionValidation(
          mission: mission,
          isValid: false,
          reason: 'Invalid mastery value',
        );
        return false;
      }

      await _logMissionValidation(
        mission: mission,
        isValid: true,
        reason: 'All validation checks passed',
      );
      return true;
    } catch (e) {
      developer.log('Error validating mission state: $e');
      await _logMissionValidation(
        mission: mission,
        isValid: false,
        reason: 'Error during validation: $e',
      );
      return false;
    }
  }

  List<MissionData> get missions => _missions;
  List<MissionData> get completedMissions => _completedMissions;
  List<MissionData> get deletedMissions => _deletedMissions;
  List<MissionData> get allMissions => [
    ..._missions,
    ..._completedMissions,
    ..._deletedMissions,
  ];

  List<MissionData> get activeMissions =>
      _missions.where((m) => !m.isCompleted).toList();

  List<MissionData> get dailyMissions =>
      _missions.where((m) => m.type == MissionType.daily).toList();
  List<MissionData> get weeklyMissions =>
      _missions.where((m) => m.type == MissionType.weekly).toList();
  List<MissionData> get simpleTasks =>
      _missions.where((m) => m.type == MissionType.simple).toList();

  Map<DateTime, int> get dailyGoalsCreated => _dailyGoalsCreated;

  // Add getter for mission history by type
  List<MissionData> getMissionHistoryByType(MissionType type) {
    return allMissions.where((m) => m.type == type).toList();
  }

  // Add getter for testing mode
  bool get isTestingMode => _isTestingMode;

  // Add method to toggle testing mode
  void toggleTestingMode() {
    _isTestingMode = !_isTestingMode;
    notifyListeners();
  }

  // Getters for mission locking state
  bool get isDailyLocked => _isDailyLocked;
  bool get isWeeklyLocked => _isWeeklyLocked;
  Color get refreshButtonColor => _refreshButtonColor;

  // Add background refresh controller
  Timer? _backgroundRefreshTimer;
  bool _isBackgroundRefreshActive = false;

  @override
  void dispose() {
    _backgroundRefreshTimer?.cancel();
    _missionController.close();
    mechanicum.dispose();
    _sandboxTimer?.cancel();
    // _isolateReceivePort?.close(); // Removed as isolates are no longer used
    super.dispose();
  }

  void _startBackgroundRefresh() {
    if (_isBackgroundRefreshActive) return;
    _isBackgroundRefreshActive = true;

    // Check every 15 seconds in background
    _backgroundRefreshTimer = Timer.periodic(const Duration(seconds: 15), (
      timer,
    ) async {
      mechanicum.setAIActive(true); // Mechanicum icon ON during background work
      try {
        final now = DateTime.now();
        bool needsRefresh = false;

        // Check for pending refreshes
        for (final mission in _missions) {
          if (_shouldRefreshMission(mission, now)) {
            needsRefresh = true;
            break;
          }
        }

        if (needsRefresh) {
          await _performBackgroundRefresh();
        }
      } catch (e) {
        developer.log('Error in background refresh: $e');
      } finally {
        mechanicum.setAIActive(false); // Mechanicum icon OFF when done
      }
    });
  }

  Future<void> _performBackgroundRefresh() async {
    try {
      final now = DateTime.now();
      final missionsToRefresh =
          _missions
              .where((mission) => _shouldRefreshMission(mission, now))
              .toList();

      if (missionsToRefresh.isEmpty) return;

      // Process refreshes in parallel
      await Future.wait(
        missionsToRefresh.map((mission) => _refreshMission(mission)),
      );

      // Update state
      _lastRefreshTime = now;
      _refreshButtonColor = Colors.green;
      _isDailyLocked = false;
      _isWeeklyLocked = false;

      // Update UI and notifications
      await Future.wait([
        _saveMissions(_missions),
        _updateBadge(),
        _showSummaryNotification(),
      ]);

      notifyListeners();
    } catch (e) {
      developer.log('Error in background refresh: $e');
      _showErrorNotification('Background refresh failed');
    }
  }

  // Update the constructor to start background refresh
  MissionProvider() {
    print('MissionProvider: Constructor START');
    latestInstance = this;
    print('HELLO FROM PROVIDER');
    try {
      print("MissionProvider: Constructor called");
      // AI Guardian starts immediately
      // initializeAIGuardian();
      print(
        'AI Guardian: Initialization requested from MissionProvider constructor',
      );
      // Delay AI Sandbox and Workmanager by 5 seconds
      // Future.delayed(const Duration(seconds: 5), () {
      //   print('AI Sandbox: Initialization requested after 5s delay');
      //   initializeAISandbox();
      //   print('Workmanager: Initialization requested after 5s delay');
      //   // You may want to call your Workmanager init here if needed
      // });
      _loadMissions();
      _startRefreshCheck();
      _startBackgroundRefresh();
      _checkMissedRefreshes();
      _setupAppLifecycleListener();
      _validateMissionIdentifiers();
      _verifyRefreshState();
      _checkFailedMissions();
      _verifyMissionCreation();
      _initializeState();
      // Notification logic moved out
      // _initNotifications();
      // _startNotificationCheck();
      // ...
      _initializeMechanicum();
      // Listen to Mechanicum's aiActiveStream and notify listeners for UI updates
      mechanicum.aiActiveStream.listen((active) {
        notifyListeners();
      });
      _loadKnowledge();
      // Start the periodic AI sandbox
      startAISandbox();
      // Initialize AI Guardian
      // Start The Imperium meta-AI in the background
      print('MissionProvider: About to start The Imperium');
      try {
        TheImperium.ensureStarted();
        print(
          'MissionProvider: The Imperium ensureStarted() called successfully',
        );
      } catch (e, st) {
        print(
          'MissionProvider: ERROR calling TheImperium.ensureStarted(): $e\n$st',
        );
      }
      print(
        '🏆 The Imperium: Running in background. Directive: Constant growth, self-learning, and improvement of all AIs.',
      );
    } catch (e, st) {
      print('ERROR in MissionProvider constructor: $e\n$st');
    }
  }

  static void triggerSandboxNow() {
    if (latestInstance != null) {
      print('MissionProvider: Static triggerSandboxNow called');
    } else {
      print('MissionProvider: No instance available for static trigger');
    }
  }

  // New public method to start notifications after loading screen
  Future<void> startNotifications() async {
    print('MissionProvider: startNotifications called');
    try {
      // Add a longer delay to ensure video loading is completely finished
      await Future.delayed(const Duration(seconds: 2));

      // Initialize notifications with proper error handling
      await _initNotifications();

      // Start notification checking with reduced frequency for better performance
      _startNotificationCheck();

      print('MissionProvider: Notifications started successfully');
    } catch (e) {
      print('MissionProvider: Error starting notifications: $e');
      // Don't rethrow - notifications are not critical for app functionality
    }
  }

  // Add a method to check if notifications should be delayed

  /// Initialize the Mechanicum with proper error handling
  Future<void> _initializeMechanicum() async {
    try {
      print('Mechanicum: Initializing...');

      // Start the continuous health check with independent background monitoring
      mechanicum.startContinuousHealthCheck(() async {
        print('🛡️ AI Guardian: Timer tick');
        try {
          print('Mechanicum: Performing background health check...');
          await validateAllMissions(attemptRepair: true);
          print('Mechanicum: Background health check completed');
        } catch (e) {
          print('Mechanicum: Error in background health check: $e');
          mechanicum.logRepair('Background health check error', 'Error: $e');
        }
      }, interval: const Duration(seconds: 30));

      // Perform initial health check and repair
      await mechanicum.performImmediateHealthCheck(() async {
        print('Mechanicum: Performing initial health check...');
        await validateAllMissions(attemptRepair: true);
        print('Mechanicum: Initial health check completed');
      });

      print('Mechanicum: Initialization completed successfully');
    } catch (e) {
      print('Mechanicum: Error during initialization: $e');
      // Continue without Mechanicum if initialization fails
    }
  }

  // Add new method to initialize state
  Future<void> _initializeState() async {
    try {
      // Load missions if not already loaded
      if (_missions.isEmpty) {
        await _loadMissions();
      }

      // Initialize notifications
      await _initNotifications();

      // Start background tasks
      _startBackgroundRefresh();
      _startRefreshCheck();

      // Validate and repair state
      await _validateMissionIdentifiers();
      await _verifyRefreshState();
      await _checkFailedMissions();
      await _verifyMissionCreation();

      // Initialize AI Guardian (Mechanicum)
      await mechanicum.initialize();

      // Notify listeners of state update
      notifyListeners();
    } catch (e) {
      developer.log('Error initializing state: $e');
      // Attempt recovery
      await _attemptStateRecovery();
    }
  }

  // Add state recovery method
  Future<void> _attemptStateRecovery() async {
    try {
      // Clear potentially corrupted state
      _missions.clear();
      _completedMissions.clear();
      _deletedMissions.clear();

      // Reload from storage
      await _loadMissions();
      await _loadDeletedMissions();

      // Reinitialize notifications
      await _initNotifications();

      // Notify listeners
      notifyListeners();
    } catch (e) {
      developer.log('Error in state recovery: $e');
    }
  }

  // Update notifyListeners to be more robust
  @override
  void notifyListeners() {
    try {
      super.notifyListeners();
      _missionController.add(null);
    } catch (e) {
      developer.log('Error notifying listeners: $e');
    }
  }

  get dailyCompletionStatus => null;

  // Public method to refresh missions
  Future<void> refreshMissions() async {
    try {
      developer.log('Starting mission refresh...');
      final now = DateTime.now();
      final missionsToRefresh = <MissionData>[];
      final processedIds = <String>{};

      // Determine which missions need refreshing based on the current state
      for (final mission in _missions) {
        // Skip if mission ID has already been processed
        if (!processedIds.add(mission.id!)) {
          continue;
        }

        // Check if mission should be refreshed
        if (_shouldRefreshMission(mission, now)) {
          // Check if mission should be marked as failed before refreshing
          final shouldMarkAsFailed = _shouldMarkMissionAsFailed(mission, now);
          if (shouldMarkAsFailed) {
            developer.log(
              'Mission "${mission.title}" will be marked as failed',
            );
          }
          missionsToRefresh.add(mission);
          developer.log('Mission "${mission.title}" will be refreshed');
        }
      }

      if (missionsToRefresh.isEmpty) {
        developer.log('No missions need refreshing');
        return;
      }

      // Create a new list to store refreshed missions
      final refreshedMissions = List<MissionData>.from(_missions);

      // Process each mission
      for (final mission in missionsToRefresh) {
        try {
          final now = DateTime.now();
          final shouldMarkAsFailed = _shouldMarkMissionAsFailed(mission, now);

          // Create a new mission with the same data but reset progress
          final refreshedMission = mission.copyWith(
            isCompleted: false,
            lastCompleted: null,
            createdAt: now,
            hasFailed: shouldMarkAsFailed,
            currentCount: 0,
            subtasks:
                mission.subtasks
                    .map(
                      (subtask) => subtask.copyWith(
                        currentCompletions: 0,
                        currentCount: 0,
                      ),
                    )
                    .toList(),
            boltColor: mission.boltColor,
            timelapseColor: mission.timelapseColor,
            linkedMasteryId: mission.linkedMasteryId,
            masteryValue: mission.masteryValue,
            subtaskMasteryValues: mission.subtaskMasteryValues,
          );

          // Update the mission in the list
          // Match on both id and notificationId, log if more than one match
          final matches =
              refreshedMissions
                  .where(
                    (m) =>
                        m.id == mission.id &&
                        m.notificationId == mission.notificationId,
                  )
                  .toList();
          if (matches.length > 1) {
            developer.log(
              'Warning: More than one mission matched for update (id: ${mission.id}, notificationId: ${mission.notificationId})',
            );
          }
          final index = refreshedMissions.indexWhere(
            (m) =>
                m.id == mission.id &&
                m.notificationId == mission.notificationId,
          );

          if (index != -1) {
            refreshedMissions[index] = refreshedMission;

            // Update notification
            await _notifications.cancel(mission.notificationId);
            await _showNotificationForMission(refreshedMission);
            developer.log(
              'Updated notification for mission "${mission.title}"',
            );
          }
        } catch (e) {
          developer.log('Error refreshing mission "${mission.title}": $e');
          // Attempt recovery for failed mission
          await _attemptMissionRecovery(mission);
        }
      }

      // Update state atomically
      _missions = refreshedMissions;
      _lastRefreshTime = now;
      _refreshButtonColor = Colors.green;
      _isDailyLocked = false;
      _isWeeklyLocked = false;

      // Update UI and notifications in parallel
      await Future.wait([
        _saveMissions(_missions),
        _updateBadge(),
        _showSummaryNotification(),
      ]);

      // Always validate after refresh
      await _validateMissionIdentifiers();
      await _validateDataConsistency();

      notifyListeners();
      developer.log(
        'Successfully refreshed ${missionsToRefresh.length} missions',
      );
    } catch (e, stackTrace) {
      developer.log('Error in refreshMissions: $e\n$stackTrace');
      throw AppError(
        'Failed to refresh missions',
        'REFRESH_MISSIONS_ERROR',
        code: 'REFRESH_MISSIONS_ERROR',
        originalError: e,
      );
    }
  }

  Future<MissionData> _refreshMission(MissionData mission) async {
    try {
      final now = DateTime.now();
      final shouldMarkAsFailed = _shouldMarkMissionAsFailed(mission, now);

      // Create a new mission with the same data but reset progress
      final refreshedMission = mission.copyWith(
        isCompleted: false,
        lastCompleted: null,
        createdAt: now,
        hasFailed: shouldMarkAsFailed,
        currentCount: 0,
        subtasks:
            mission.subtasks
                .map(
                  (subtask) =>
                      subtask.copyWith(currentCompletions: 0, currentCount: 0),
                )
                .toList(),
        boltColor: mission.boltColor,
        timelapseColor: mission.timelapseColor,
        linkedMasteryId: mission.linkedMasteryId,
        masteryValue: mission.masteryValue,
        subtaskMasteryValues: mission.subtaskMasteryValues,
      );

      // Update notification
      await _notifications.cancel(mission.notificationId);
      await _showNotificationForMission(refreshedMission);
      developer.log('Updated notification for mission "${mission.title}"');

      return refreshedMission;
    } catch (e) {
      developer.log('Error refreshing mission "${mission.title}": $e');
      throw AppError(
        'Failed to refresh mission',
        'REFRESH_MISSION_ERROR',
        code: 'REFRESH_MISSION_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _attemptMissionRecovery(MissionData mission) async {
    try {
      // Try to recover the mission state
      final recoveredMission = mission.copyWith(
        isCompleted: false,
        hasFailed: false,
        currentCount: 0,
        subtasks:
            mission.subtasks
                .map(
                  (subtask) =>
                      subtask.copyWith(currentCompletions: 0, currentCount: 0),
                )
                .toList(),
      );

      // Update the mission in state
      final index = _missions.indexWhere((m) => m.id == mission.id);
      if (index != -1) {
        _missions[index] = recoveredMission;
        await _saveMissions(_missions);
        notifyListeners();
      }
    } catch (e) {
      developer.log('Error in mission recovery: $e');
    }
  }

  void _showErrorNotification(String message) {
    _notifications.show(
      0,
      'Error',
      message,
      NotificationDetails(
        android: AndroidNotificationDetails(
          NotificationChannels.mission,
          'Mission Notifications',
          channelDescription: 'Notifications for mission updates',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }

  Future<void> _initNotifications() async {
    tz.initializeTimeZones();
    const androidSettings = AndroidInitializationSettings(
      '@mipmap/ic_launcher',
    );
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    // Request notification permissions
    await requestNotificationPermission();

    await _notifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) async {
        await _handleProgressAction(response);
      },
    );

    // Only schedule notifications for active missions that don't already have notifications
    final activeNotifications = await _notifications.getActiveNotifications();
    final activeNotificationIds = activeNotifications.map((n) => n.id).toSet();

    for (var mission in _missions.where((m) => !m.isCompleted)) {
      if (!activeNotificationIds.contains(mission.notificationId)) {
        await _scheduleNotification(mission);
      }
    }
  }

  Future<List<MissionData>> _loadMissions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final missionsJson = prefs.getString('missions');
      if (missionsJson != null) {
        final List<dynamic> decoded = jsonDecode(missionsJson);
        _missions =
            decoded
                .map(
                  (json) => MissionData.fromJson(json as Map<String, dynamic>),
                )
                .toList();
      }
      await _loadDeletedMissions();

      // Only initialize notifications if they haven't been initialized yet
      if (!_notificationsInitialized) {
        await _initNotifications();
        _notificationsInitialized = true;
      }

      return _missions;
    } catch (e) {
      print('Error loading missions: $e');
      throw AppError(
        'Failed to load missions',
        'LOAD_MISSIONS_ERROR',
        code: 'LOAD_MISSIONS_ERROR',
        originalError: e,
      );
    }
  }

  // Add flag to track notification initialization

  // Update notification check to be less frequent and more efficient
  void _startNotificationCheck() {
    Future<void> checkNotifications() async {
      try {
        final activeNotifications =
            await _notifications.getActiveNotifications();
        final activeNotificationIds =
            activeNotifications.map((n) => n.id).toSet();

        // Only show notifications for missions that don't have active notifications
        for (var mission in _missions.where((m) => !m.isCompleted)) {
          if (!activeNotificationIds.contains(mission.notificationId)) {
            await _scheduleNotification(mission);
          }
        }

        // Only show summary if there are active missions
        if (_missions.any((m) => !m.isCompleted)) {
          await _showSummaryNotification();
        }
      } catch (e) {
        developer.log('Error checking notifications: $e');
      }
    }

    // Check less frequently (every 30 minutes instead of 15) for better performance
    Timer.periodic(const Duration(minutes: 30), (timer) async {
      await checkNotifications();
    });

    // Initial check after a longer delay to avoid interfering with video loading
    Future.delayed(const Duration(seconds: 60), checkNotifications);
  }

  Future<void> _loadDeletedMissions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final deletedMissionsJson = prefs.getString('deleted_missions');
      if (deletedMissionsJson != null) {
        final List<dynamic> decoded = jsonDecode(deletedMissionsJson);
        _deletedMissions =
            decoded
                .map(
                  (json) => MissionData.fromJson(json as Map<String, dynamic>),
                )
                .toList();
      }
    } catch (e) {
      print('Error loading deleted missions: $e');
      throw AppError(
        'Failed to load deleted missions',
        'LOAD_DELETED_MISSIONS_ERROR',
        code: 'LOAD_DELETED_MISSIONS_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _validateMissionMastery(
    MissionData mission,
    MasteryProvider masteryProvider,
  ) async {
    try {
      // Check main mission mastery
      if (mission.linkedMasteryId != null && mission.masteryValue > 0) {
        if (mission.isCompleted) {
          // Mission is completed, ensure mastery was added
          await masteryProvider.addProgress(
            mission.linkedMasteryId!,
            'Mission: ${mission.title}',
            mission.masteryValue,
          );
        } else if (mission.isCounterBased && mission.currentCount > 0) {
          // Counter-based mission with progress, add mastery for each increment
          await masteryProvider.addProgress(
            mission.linkedMasteryId!,
            'Mission: ${mission.title}',
            mission.masteryValue * mission.currentCount,
          );
        }
      }

      // Check subtask mastery
      for (final subtask in mission.subtasks) {
        if (subtask.linkedMasteryId != null && subtask.masteryValue > 0) {
          if (subtask.isCounterBased) {
            // Counter-based subtask, add mastery for total count
            await masteryProvider.addProgress(
              subtask.linkedMasteryId!,
              '${mission.title} - ${subtask.name}',
              subtask.masteryValue * subtask.currentCount,
            );
          } else if (subtask.currentCompletions > 0) {
            // Regular subtask with progress, add mastery for total completions
            await masteryProvider.addProgress(
              subtask.linkedMasteryId!,
              '${mission.title} - ${subtask.name}',
              subtask.masteryValue * subtask.currentCompletions,
            );
          }
        }
      }

      masteryProvider.notifyListeners();
    } catch (e) {
      developer.log('Error validating mission mastery: $e');
    }
  }

  // Public method to validate all mastery progress
  Future<void> validateAllMasteryProgress() async {
    try {
      final masteryProvider = Provider.of<MasteryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );

      // Validate active missions
      for (final mission in _missions) {
        await _validateMissionMastery(mission, masteryProvider);
      }

      // Validate completed missions
      for (final mission in _completedMissions) {
        await _validateMissionMastery(mission, masteryProvider);
      }

      notifyListeners();
    } catch (e) {
      developer.log('Error validating mastery progress: $e');
    }
  }

  Future<void> _saveMissions(List<MissionData> missions) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final missionsJson = missions.map((m) => m.toJson()).toList();
      await prefs.setString('missions', jsonEncode(missionsJson));
    } catch (e) {
      print('Error saving missions: $e');
      throw AppError(
        'Failed to save missions',
        'SAVE_MISSIONS_ERROR',
        code: 'SAVE_MISSIONS_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _saveDeletedMissions(List<MissionData> deletedMissions) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final deletedMissionsJson =
          deletedMissions.map((m) => m.toJson()).toList();
      await prefs.setString(
        'deleted_missions',
        jsonEncode(deletedMissionsJson),
      );
    } catch (e) {
      print('Error saving deleted missions: $e');
      throw AppError(
        'Failed to save deleted missions',
        'SAVE_DELETED_MISSIONS_ERROR',
        code: 'SAVE_DELETED_MISSIONS_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _saveData() async {
    try {
      await _saveMissions(_missions);
      await _updateBadge();
      await _showSummaryNotification();
    } catch (e) {
      developer.log('Error in _saveData: $e');
    }
  }

  Future<void> _scheduleNotification(
    MissionData mission, {
    bool useEnhancements = true,
  }) async {
    try {
      if (useEnhancements) {
        await _enhancements._safeNotificationOperation(
          'scheduleNotification',
          () => _enhancements._scheduleNotificationUpdate(this, mission),
        );
        return;
      }

      // Ensure we have the latest notification settings
      await _notifications.initialize(
        const InitializationSettings(
          android: AndroidInitializationSettings('@mipmap/ic_launcher'),
          iOS: DarwinInitializationSettings(
            requestAlertPermission: true,
            requestBadgePermission: true,
            requestSoundPermission: true,
          ),
        ),
      );

      List<AndroidNotificationAction>? actions = _enhancements
          ._buildOptimizedActions(mission);
      final details = await _enhancements._getCachedNotificationDetails(
        mission,
        actions: actions,
        isSummary: false,
      );

      // Cancel any existing notification first
      await _notifications.cancel(mission.notificationId);

      // Schedule the new notification with exact timing
      await _notifications.show(
        mission.notificationId,
        '${_enhancements._getEnhancedStatusEmoji(mission)} ${mission.title}',
        _enhancements._buildOptimizedNotificationContent(mission),
        details,
      );

      // For daily missions, also schedule a backup notification
      if (mission.type == MissionType.daily && !mission.isCompleted) {
        final backupId =
            mission.notificationId + 1000; // Use a different ID for backup
        await _notifications.show(
          backupId,
          'Backup: ${mission.title}',
          'Don\'t forget to complete your daily mission!',
          details,
        );
      }

      developer.log(
        'Successfully scheduled notification for mission: ${mission.title}',
      );
    } catch (e) {
      developer.log(
        'Error scheduling notification for mission ${mission.title}: $e',
      );
      // Attempt to recover by rescheduling with basic settings
      try {
        final basicDetails = NotificationDetails(
          android: AndroidNotificationDetails(
            NotificationChannels.mission,
            'Missions',
            channelDescription: 'Mission notifications',
            importance: Importance.max,
            priority: Priority.high,
          ),
        );
        await _notifications.show(
          mission.notificationId,
          mission.title,
          'Complete your mission!',
          basicDetails,
        );
      } catch (recoveryError) {
        developer.log('Failed to recover notification: $recoveryError');
      }
    }
  }

  Future<void> editMission(
    MissionData mission,
    MissionData updatedMission, {
    String? title,
    String? description,
    MissionType? type,
    List<MissionSubtask>? subtasks,
    bool? isCounterBased,
    int? targetCount,
    String? linkedMasteryId,
    double? masteryValue,
    Map<String, double>? subtaskMasteryValues,
    String? imageUrl,
  }) async {
    try {
      // Find the mission in the state
      final index = _missions.indexWhere(
        (m) => m.notificationId == mission.notificationId,
      );

      if (index != -1) {
        // Create edited mission with updated values
        final editedMission = mission.copyWith(
          title: title ?? mission.title,
          description: description ?? mission.description,
          type: type ?? mission.type,
          subtasks: subtasks ?? mission.subtasks,
          isCounterBased: isCounterBased ?? mission.isCounterBased,
          targetCount: targetCount ?? mission.targetCount,
          linkedMasteryId: linkedMasteryId ?? mission.linkedMasteryId,
          masteryValue: masteryValue ?? mission.masteryValue,
          subtaskMasteryValues:
              subtaskMasteryValues ?? mission.subtaskMasteryValues,
          imageUrl: imageUrl ?? mission.imageUrl,
        );

        // Update the mission in the state
        _missions[index] = editedMission;

        // Update notification
        await _notifications.cancel(mission.notificationId);
        await _showNotificationForMission(editedMission);

        // Save changes
        await _saveData();
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        developer.log('Successfully edited mission: ${mission.title}');
        developer.log('Updated subtask counts:');
        for (var subtask in editedMission.subtasks) {
          developer.log(
            'Subtask ${subtask.name}: count=${subtask.currentCount}, completions=${subtask.currentCompletions}, required=${subtask.requiredCompletions}',
          );
        }
        // Call comprehensive repair after edit
        await _validateAndRepairAllIssues();
      } else {
        developer.log('Mission not found for editing: ${mission.title}');
        throw AppError(
          'Mission not found',
          'MISSION_NOT_FOUND',
          code: 'MISSION_NOT_FOUND',
        );
      }
    } catch (e, stackTrace) {
      developer.log('Error editing mission ${mission.title}: $e\n$stackTrace');
      throw AppError(
        'Failed to edit mission',
        'EDIT_MISSION_ERROR',
        code: 'EDIT_MISSION_ERROR',
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> deleteMission(MissionData mission) async {
    try {
      // Find the mission using both id and notificationId for precise identification
      final missionIndex = _missions.indexWhere(
        (m) => m.id == mission.id && m.notificationId == mission.notificationId,
      );

      if (missionIndex == -1) {
        print('Mission not found for deletion: ${mission.title}');
        return;
      }

      // Remove the specific mission
      final deletedMission = _missions.removeAt(missionIndex);

      // Add to deleted missions
      _deletedMissions.add(deletedMission);

      // Clear any cached data
      await _clearMissionCache(deletedMission.id!);

      // Cancel notification
      await _notifications.cancel(deletedMission.notificationId);

      // Clean up unused images
      if (!_missions.any((m) => m.imageUrl == deletedMission.imageUrl)) {
        _usedImages.remove(deletedMission.imageUrl);
      }

      // Save changes
      await _saveMissions(_missions);
      await _saveDeletedMissions(_deletedMissions);

      notifyListeners();
      await _updateBadge();
    } catch (e) {
      print('Error deleting mission: $e');
      throw AppError(
        'Failed to delete mission',
        'DELETE_MISSION_ERROR',
        code: 'DELETE_MISSION_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _clearMissionCache(String missionId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = 'mission_cache_$missionId';
      await prefs.remove(cacheKey);
    } catch (e) {
      print('Error clearing mission cache: $e');
    }
  }

  Future<void> deleteAllMissions() async {
    try {
      // Move all missions to deleted missions list before clearing
      _deletedMissions.addAll(_missions);

      // Cancel all notifications
      for (var mission in _missions) {
        await _notifications.cancel(mission.notificationId);
      }

      // Clear missions and used images
      _missions.clear();
      _usedImages.clear();

      // Save changes
      await _saveData();
      notifyListeners();
      await _updateBadge();

      final historyProvider = Provider.of<AppHistoryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );
      await historyProvider.logMission(
        title: 'All Missions Deleted',
        description: 'Successfully deleted all missions',
        metadata: {
          'deletedAt': DateTime.now().toIso8601String(),
          'deletedCount': _deletedMissions.length,
        },
      );
    } catch (e, stackTrace) {
      final historyProvider = Provider.of<AppHistoryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );
      await historyProvider.logError(
        title: 'Delete All Missions Error',
        description: 'Failed to delete all missions',
        errorCode: 'DELETE_ALL_MISSIONS_ERROR',
        errorType: 'System Error',
        stackTrace: stackTrace.toString(),
      );
      throw AppError(
        'Failed to delete all missions',
        'DELETE_ALL_MISSIONS_ERROR',
        code: 'DELETE_ALL_MISSIONS_ERROR',
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> deleteCompletedMissions() async {
    try {
      final completedMissions = _missions.where((m) => m.isCompleted).toList();

      // Move completed missions to deleted missions list
      _deletedMissions.addAll(completedMissions);

      // Cancel notifications for completed missions
      for (var mission in completedMissions) {
        await _notifications.cancel(mission.notificationId);
      }

      // Remove completed missions
      _missions.removeWhere((m) => m.isCompleted);

      // Clean up unused images
      for (var mission in completedMissions) {
        if (!_missions.any((m) => m.imageUrl == mission.imageUrl)) {
          _usedImages.remove(mission.imageUrl);
        }
      }

      // Save changes
      await _saveData();
      notifyListeners();
      await _updateBadge();

      final historyProvider = Provider.of<AppHistoryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );
      await historyProvider.logMission(
        title: 'Completed Missions Deleted',
        description:
            'Successfully deleted ${completedMissions.length} completed missions',
        metadata: {
          'deletedAt': DateTime.now().toIso8601String(),
          'deletedCount': completedMissions.length,
        },
      );
    } catch (e, stackTrace) {
      final historyProvider = Provider.of<AppHistoryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );
      await historyProvider.logError(
        title: 'Delete Completed Missions Error',
        description: 'Failed to delete completed missions',
        errorCode: 'DELETE_COMPLETED_MISSIONS_ERROR',
        errorType: 'System Error',
        stackTrace: stackTrace.toString(),
      );
      throw AppError(
        'Failed to delete completed missions',
        'DELETE_COMPLETED_MISSIONS_ERROR',
        code: 'DELETE_COMPLETED_MISSIONS_ERROR',
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> deleteMissionsByType(MissionType type) async {
    final missionsToDelete = _missions.where((m) => m.type == type).toList();

    // Cancel notifications for missions of the specified type
    for (var mission in missionsToDelete) {
      await _notifications.cancel(mission.notificationId);
    }

    _missions.removeWhere((m) => m.type == type);
    await _saveMissions(_missions);
    notifyListeners();
    // Always validate after deletion
    await _validateMissionIdentifiers();
    await _validateDataConsistency();
  }

  Future<bool> _validateMissionCreation({
    required String title,
    required MissionType type,
    required List<MissionSubtask> subtasks,
    required bool isCounterBased,
    required int? targetCount,
    required String? linkedMasteryId,
    required double? masteryValue,
  }) async {
    try {
      // Validate title
      if (title.trim().isEmpty) {
        developer.log('Mission validation failed: Empty title');
        return false;
      }

      // Strengthened duplicate check: check for duplicate id, notificationId, and title/type/time
      final now = DateTime.now();
      final isDuplicate = _missions.any(
        (mission) =>
            mission.title == title &&
                mission.type == type &&
                mission.createdAt?.isAtSameMomentAs(now) == true ||
            _missions.where((m) => m.id == mission.id).length > 1 ||
            _missions
                    .where((m) => m.notificationId == mission.notificationId)
                    .length >
                1,
      );
      if (isDuplicate) {
        developer.log(
          'Mission validation failed: Duplicate mission detected (id, notificationId, or title/type/time)',
        );
        return false;
      }

      // Validate counter-based mission
      if (isCounterBased) {
        if (targetCount != null && targetCount < 0) {
          developer.log('Mission validation failed: Invalid target count');
          return false;
        }
      }

      // Validate subtasks
      if (subtasks.isNotEmpty) {
        for (final subtask in subtasks) {
          if (!_validateSubtaskState(subtask)) {
            developer.log('Mission validation failed: Invalid subtask state');
            return false;
          }
        }
      }

      // Validate mastery values
      if (linkedMasteryId != null && (masteryValue ?? 0) <= 0) {
        developer.log('Mission validation failed: Invalid mastery value');
        return false;
      }

      // Validate mission type specific requirements
      if (type == MissionType.daily || type == MissionType.weekly) {
        // Check if we've reached the limit for this type
        final typeCount = _missions.where((m) => m.type == type).length;
        if (typeCount >= 5) {
          // Assuming max 5 missions per type
          developer.log(
            'Mission validation failed: Maximum missions reached for type $type',
          );
          return false;
        }
      }

      return true;
    } catch (e) {
      developer.log('Error validating mission creation: $e');
      return false;
    }
  }

  Future<MissionData> createMission({
    required String title,
    required MissionType type,
    String? description,
    List<MissionSubtask> subtasks = const [],
    bool isCounterBased = false,
    int? targetCount,
    String? linkedMasteryId,
    double? masteryValue,
    Map<String, double> subtaskMasteryValues = const {},
    String? imageUrl,
  }) async {
    try {
      // Validate mission creation parameters
      if (!await _validateMissionCreation(
        title: title,
        type: type,
        subtasks: subtasks,
        isCounterBased: isCounterBased,
        targetCount: targetCount,
        linkedMasteryId: linkedMasteryId,
        masteryValue: masteryValue,
      )) {
        throw AppError(
          'Invalid mission configuration',
          'INVALID_MISSION_CONFIG',
          code: 'INVALID_MISSION_CONFIG',
        );
      }

      // Check refresh state before creating mission
      await _verifyRefreshState();

      // Generate unique identifiers
      final uniqueId = _generateUniqueMissionId();
      final uniqueNotificationId = _generateUniqueNotificationId();

      // Initialize subtasks with proper state
      final initializedSubtasks =
          subtasks
              .map(
                (subtask) => MissionSubtask(
                  name: subtask.name,
                  requiredCompletions: subtask.requiredCompletions,
                  currentCompletions: 0,
                  linkedMasteryId: subtask.linkedMasteryId,
                  masteryValue: subtask.masteryValue,
                  isCounterBased: subtask.isCounterBased,
                  currentCount: 0,
                  boltColor: subtask.boltColor,
                  createdAt: DateTime.now(),
                ),
              )
              .toList();

      // Create the mission
      final mission = MissionData(
        id: uniqueId,
        missionId: uniqueId,
        title: title,
        description: description ?? '',
        type: type,
        subtasks: initializedSubtasks,
        linkedMasteryId: linkedMasteryId,
        masteryValue: masteryValue ?? 0.0,
        subtaskMasteryValues: subtaskMasteryValues,
        isCounterBased: isCounterBased,
        targetCount: targetCount ?? 0,
        notificationId: uniqueNotificationId,
        imageUrl: imageUrl ?? '',
        createdAt: DateTime.now(),
      );

      // Add the mission to the state
      _missions = [..._missions, mission];

      // Initialize mission state
      await _initializeMissionState(mission);

      // Save changes
      await _saveData();
      notifyListeners();

      // Always validate after creation
      await _validateMissionIdentifiers();
      await _validateDataConsistency();

      return mission;
    } catch (e) {
      developer.log('Error creating mission: $e');
      throw AppError(
        'Failed to create mission',
        'CREATE_MISSION_ERROR',
        code: 'CREATE_MISSION_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> _initializeMissionState(MissionData mission) async {
    try {
      // Initialize notifications
      await _showImmediateNotification(mission);
      await _showNotificationForMission(mission);

      // Update badge
      await _updateBadge();

      // Record creation
      incrementGoalsCreated(DateTime.now());

      // Verify mission state
      await _verifyMissionCreation();

      developer.log('Successfully initialized mission state: ${mission.title}');
    } catch (e) {
      developer.log('Error initializing mission state: $e');
      throw AppError(
        'Failed to initialize mission state',
        'INIT_MISSION_STATE_ERROR',
        code: 'INIT_MISSION_STATE_ERROR',
        originalError: e,
      );
    }
  }

  String _generateUniqueMissionId() {
    final existingIds = {
      ..._missions.map((m) => m.id),
      ..._completedMissions.map((m) => m.id),
      ..._deletedMissions.map((m) => m.id),
    };
    String newId;
    do {
      final timestamp = DateTime.now().microsecondsSinceEpoch;
      final random = Random().nextInt(1000000);
      newId = 'mission_${timestamp}_${random}_${Random().nextInt(1000)}';
    } while (existingIds.contains(newId));
    return newId;
  }

  int _generateUniqueNotificationId() {
    final existingIds = {
      ..._missions.map((m) => m.notificationId),
      ..._completedMissions.map((m) => m.notificationId),
      ..._deletedMissions.map((m) => m.notificationId),
    };
    int newId;
    do {
      // Use modulo to ensure the ID stays within 32-bit signed integer range
      newId =
          (DateTime.now().millisecondsSinceEpoch + Random().nextInt(1000000)) %
          0x7FFFFFFF;
      // Ensure it's not 0 or negative
      if (newId <= 0) {
        newId = Random().nextInt(1000000) + 1000;
      }
    } while (existingIds.contains(newId));
    return newId;
  }

  Future<void> _showNotificationForMission(MissionData mission) async {
    try {
      // Check if notification already exists
      final activeNotifications = await _notifications.getActiveNotifications();
      if (activeNotifications.any((n) => n.id == mission.notificationId)) {
        return; // Skip if notification already exists
      }

      // Validate mission state before showing notification
      final isValid = await _isValidMissionState(mission);
      if (!isValid) {
        developer.log(
          'Invalid mission state for notification: ${mission.title}',
        );
        return;
      }

      // Build notification content
      final content = StringBuffer();
      if (mission.description.isNotEmpty) {
        content.writeln(mission.description);
      }

      // Add mission-specific content
      if (mission.isCounterBased) {
        content.writeln(
          'Count: ${mission.currentCount}${mission.targetCount > 0 ? '/${mission.targetCount}' : ''}',
        );
      } else if (mission.subtasks.isNotEmpty) {
        content.writeln('Tasks:');
        for (final subtask in mission.subtasks) {
          final progress =
              subtask.isCounterBased
                  ? '${subtask.currentCount}${subtask.requiredCompletions > 0 ? '/${subtask.requiredCompletions}' : ''}'
                  : '${subtask.currentCompletions}/${subtask.requiredCompletions}';
          content.writeln('• ${subtask.name}: $progress');
        }
      }

      // Create notification details with mission-specific settings
      final details = NotificationDetails(
        android: AndroidNotificationDetails(
          NotificationChannels.mission,
          'Mission Notifications',
          channelDescription: 'Notifications for mission updates',
          importance: Importance.max,
          priority: Priority.max,
          groupKey: NotificationChannels.groupKey,
          setAsGroupSummary: false,
          styleInformation: BigTextStyleInformation(
            content.toString(),
            contentTitle:
                '${_enhancements._getEnhancedStatusEmoji(mission)} ${mission.title}',
            htmlFormatContent: false,
            htmlFormatTitle: false,
          ),
          icon: '@mipmap/ic_launcher',
          ongoing: !mission.isCompleted,
          autoCancel: false,
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
          threadIdentifier: NotificationChannels.groupKey,
          interruptionLevel: InterruptionLevel.timeSensitive,
        ),
      );

      // Show notification with unique ID
      await _notifications.show(
        mission.notificationId,
        '${_enhancements._getEnhancedStatusEmoji(mission)} ${mission.title}',
        content.toString(),
        details,
      );

      developer.log(
        'Successfully created notification for mission: ${mission.title}',
      );
    } catch (e) {
      developer.log(
        'Error showing notification for mission ${mission.title}: $e',
      );
    }
  }

  Future<void> _updateBadge() async {
    try {
      final activeMissions = _missions.where((m) => !m.isCompleted).length;
      await AppBadgePlus.updateBadge(activeMissions);
    } catch (e) {
      developer.log('Error updating badge: $e');
    }
  }

  Future<void> _showSummaryNotification() async {
    try {
      final activeMissions = _missions.where((m) => !m.isCompleted).toList();
      if (activeMissions.isEmpty) {
        await _notifications.cancel(9998);
        return;
      }

      // Build summary string efficiently
      final summaryBuilder = StringBuffer('Mission Summary\n\n');
      summaryBuilder.writeln('Active Missions: ${activeMissions.length}\n');

      // Group missions by type efficiently
      final missionCounts = <MissionType, int>{
        MissionType.daily: 0,
        MissionType.weekly: 0,
        MissionType.simple: 0,
      };

      int failedCount = 0;
      for (final mission in activeMissions) {
        missionCounts[mission.type] = (missionCounts[mission.type] ?? 0) + 1;
        if (mission.hasFailed) failedCount++;
      }

      // Add mission type counts
      for (final entry in missionCounts.entries) {
        if (entry.value > 0) {
          summaryBuilder.writeln(
            '${_getMissionTypeName(entry.key)}: ${entry.value}',
          );
        }
      }

      // Add failed missions count if any
      if (failedCount > 0) {
        summaryBuilder.writeln('\nFailed Missions: $failedCount');
      }

      // Show notification with optimized details
      await _notifications.show(
        9998,
        'Mission Summary',
        summaryBuilder.toString(),
        NotificationDetails(
          android: AndroidNotificationDetails(
            NotificationChannels.summary,
            'Mission Summary',
            channelDescription: 'Summary of mission progress',
            importance: Importance.high,
            priority: Priority.high,
            groupKey: NotificationChannels.groupKey,
            setAsGroupSummary: true,
            styleInformation: BigTextStyleInformation(
              summaryBuilder.toString(),
            ),
            icon: '@mipmap/ic_launcher',
          ),
          iOS: const DarwinNotificationDetails(
            threadIdentifier: NotificationChannels.groupKey,
            interruptionLevel: InterruptionLevel.timeSensitive,
          ),
        ),
      );
    } catch (e) {
      developer.log('Error showing summary notification: $e');
    }
  }

  String _getMissionTypeName(MissionType type) {
    switch (type) {
      case MissionType.daily:
        return 'Daily Missions';
      case MissionType.weekly:
        return 'Weekly Missions';
      case MissionType.simple:
        return 'Simple Tasks';
      case MissionType.persistent:
        return 'Persistent Missions';
    }
  }

  Future<void> _handleProgressAction(NotificationResponse response) async {
    print('Handling progress action: ${response.actionId}');
    final parts = response.actionId!.split('_');
    if (parts.length >= 3) {
      final missionId = int.tryParse(parts[1]);
      final subtaskName = parts.sublist(2).join('_');
      if (missionId != null) {
        final missionIndex = _missions.indexWhere(
          (m) => m.notificationId == missionId,
        );
        if (missionIndex != -1) {
          final mission = _missions[missionIndex];
          print('Found mission: ${mission.title}');
          final subtaskIndex = mission.subtasks.indexWhere(
            (s) => s.name == subtaskName,
          );
          if (subtaskIndex != -1) {
            final subtask = mission.subtasks[subtaskIndex];
            print(
              'Found subtask: ${subtask.name}, isCounterBased: ${subtask.isCounterBased}',
            );

            if (subtask.isCounterBased) {
              print('Handling counter-based subtask increment');
              // Handle counter-based subtask
              final updatedSubtask = subtask.copyWith(
                currentCount: subtask.currentCount + 1,
              );
              print('Updated subtask count: ${updatedSubtask.currentCount}');

              // Create updated mission with new subtask
              final updatedSubtasks = List<MissionSubtask>.from(
                mission.subtasks,
              );
              updatedSubtasks[subtaskIndex] = updatedSubtask;

              // Check if all subtasks are complete
              bool allSubtasksComplete = updatedSubtasks.every(
                (s) =>
                    s.isCounterBased
                        ? s.currentCount >=
                            (s.requiredCompletions > 0
                                ? s.requiredCompletions
                                : 1)
                        : s.currentCompletions >= s.requiredCompletions,
              );

              final updatedMission = mission.copyWith(
                isCompleted: allSubtasksComplete,
                lastCompleted: allSubtasksComplete ? DateTime.now() : null,
                hasFailed: false, // Remove failed status when progress is made
                subtasks: updatedSubtasks,
              );

              // Update the mission in state
              final updatedMissions = List<MissionData>.from(_missions);
              updatedMissions[missionIndex] = updatedMission;
              _missions = updatedMissions;

              // Save changes
              await _saveMissions(_missions);

              // Update notification
              await _notifications.cancel(mission.notificationId);
              await _showNotificationForMission(updatedMission);

              // Add mastery progress if linked
              if (updatedSubtask.linkedMasteryId != null &&
                  updatedSubtask.masteryValue > 0) {
                final masteryProvider = Provider.of<MasteryProvider>(
                  navigatorKey.currentContext!,
                  listen: false,
                );
                masteryProvider.addProgress(
                  updatedSubtask.linkedMasteryId!,
                  'Subtask: ${updatedSubtask.name}',
                  updatedSubtask.masteryValue,
                );
              }

              notifyListeners();
              await _updateBadge();
              await _showSummaryNotification();
            } else {
              print('Handling regular subtask completion');
              // Handle regular subtask
              await completeSubtask(mission, subtask);
            }
          } else {
            print('Subtask not found: $subtaskName');
          }
        } else {
          print('Mission not found for ID: $missionId');
        }
      } else {
        print('Invalid mission ID in action: ${response.actionId}');
      }
    } else {
      print('Invalid progress action format: ${response.actionId}');
    }
  }

  void _startRefreshCheck() {
    // Check more frequently (every 30 seconds instead of every minute)
    Timer.periodic(const Duration(seconds: 30), (timer) async {
      final now = DateTime.now();
      bool needsRefresh = false;
      bool hasError = false;

      // Check for automatic daily refresh at midnight
      if (now.hour == 0 && now.minute == 0) {
        for (var mission in _missions) {
          if (mission.type == MissionType.daily) {
            try {
              await _refreshMission(mission);
              needsRefresh = true;
            } catch (e) {
              developer.log('Error in automatic daily refresh: $e');
              hasError = true;
            }
          }
        }
        if (needsRefresh && !hasError) {
          _lastRefreshTime = now;
          _refreshButtonColor = Colors.green;
          _isDailyLocked = false;
          _isWeeklyLocked = false;
          notifyListeners();
        }
      }

      // Check for automatic weekly refresh at end of week
      if (now.weekday == DateTime.sunday &&
          now.hour == 23 &&
          now.minute >= 59) {
        for (var mission in _missions) {
          if (mission.type == MissionType.weekly ||
              mission.type == MissionType.daily) {
            try {
              await _refreshMission(mission);
              needsRefresh = true;
            } catch (e) {
              developer.log('Error in automatic weekly refresh: $e');
              hasError = true;
            }
          }
        }
        if (needsRefresh && !hasError) {
          _lastRefreshTime = now;
          _refreshButtonColor = Colors.green;
          _isDailyLocked = false;
          _isWeeklyLocked = false;
          notifyListeners();
        }
      }

      // Check for missed daily refresh (before midday)
      if (now.hour < 12 && now.hour >= 0) {
        final lastRefresh = _lastRefreshTime;
        if (lastRefresh == null || !_isSameDay(lastRefresh, now)) {
          _refreshButtonColor = Colors.red;
          _isDailyLocked = true;
          _isWeeklyLocked = false;
          notifyListeners();
        }
      }

      // Check for missed weekly refresh (Monday before midday)
      if (now.weekday == DateTime.monday && now.hour < 12) {
        final lastRefresh = _lastRefreshTime;
        if (lastRefresh == null || lastRefresh.weekday != DateTime.sunday) {
          _refreshButtonColor = Colors.orange;
          _isDailyLocked = true;
          _isWeeklyLocked = true;
          notifyListeners();
        }
      }

      // Force UI update if any state changed
      if (needsRefresh) {
        notifyListeners();
      }
    });
  }

  bool _shouldRefreshMission(MissionData mission, DateTime now) {
    try {
      // In testing mode, always refresh
      if (_isTestingMode) {
        return true;
      }

      // Persistent missions should not reset their progress
      if (mission.type == MissionType.persistent) {
        return false;
      }

      // Check if mission should be refreshed based on type and time
      if (mission.type == MissionType.daily) {
        // Daily missions should refresh at midnight
        if (mission.createdAt == null) return false;
        return !_isSameDay(mission.createdAt!, now);
      } else if (mission.type == MissionType.weekly) {
        // Weekly missions should refresh on Sunday at 11:59 PM
        if (mission.createdAt == null) return false;
        final isSunday = now.weekday == DateTime.sunday;
        final isEndOfWeek = isSunday && now.hour == 23 && now.minute >= 59;
        return isEndOfWeek;
      }

      // For other mission types, check if they're locked
      if (mission.type == MissionType.daily && _isDailyLocked) {
        return true;
      } else if (mission.type == MissionType.weekly && _isWeeklyLocked) {
        return true;
      }

      return false;
    } catch (e) {
      developer.log('Error checking if mission should refresh: $e');
      return false;
    }
  }

  void incrementGoalsCreated(DateTime date) {
    final currentCount = _dailyGoalsCreated[date] ?? 0;
    _dailyGoalsCreated[date] = currentCount + 1;
    notifyListeners();
  }

  // Add health check system
  Future<void> performHealthCheck({
    required bool showPopup,
    BuildContext? context,
  }) async {
    try {
      developer.log('Starting application health check...');

      // 1. Validate all missions
      for (final mission in _missions) {
        final isValid = await _isValidMissionState(mission);
        if (!isValid) {
          developer.log(
            'Health check: Invalid mission state detected for ${mission.title}',
          );
          await _repairMissionState(mission);
        }
      }

      // 2. Verify notifications
      await _verifyNotifications();

      // 3. Validate data consistency
      await _validateDataConsistency();

      // 4. Check for missed refreshes
      _checkMissedRefreshes();

      // 5. Update UI state
      await _updateBadge();
      await _showSummaryNotification();

      // 6. Restore any lost notifications
      await _restoreLostNotifications();

      // 7. Verify mission timers and schedules
      await _verifyMissionSchedules();

      developer.log('Health check completed successfully');
    } catch (e) {
      developer.log('Health check failed: $e');
    }
  }

  Future<void> _repairMissionState(MissionData mission) async {
    mechanicum.setAIActive(true);
    try {
      final oldState = mission.isCompleted ? 'completed' : 'incomplete';
      // Create a repaired version of the mission
      final repairedMission = mission.copyWith(
        currentCount: mission.currentCount.clamp(0, mission.targetCount),
        hasFailed: !mission.isCompleted && _hasMeaningfulProgress(mission),
        subtasks:
            mission.subtasks
                .map(
                  (subtask) => subtask.copyWith(
                    currentCount: subtask.currentCount.clamp(
                      0,
                      subtask.requiredCompletions,
                    ),
                    currentCompletions: subtask.currentCompletions.clamp(
                      0,
                      subtask.requiredCompletions,
                    ),
                  ),
                )
                .toList(),
      );

      // Update the mission in the list
      final index = _missions.indexWhere(
        (m) => m.notificationId == mission.notificationId,
      );
      if (index != -1) {
        _missions[index] = repairedMission;
        await _scheduleNotification(repairedMission);

        // Log state change
        await _logMissionStateChange(
          mission: repairedMission,
          oldState: oldState,
          newState: 'repaired',
        );
        await _saveData();
        notifyListeners();
        print('Repaired mission state for: ${mission.title}');
        printAllMissionData();
      }
    } catch (e) {
      print('Failed to repair mission state: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _verifyNotifications() async {
    try {
      // Get all active notifications
      final activeNotifications = await _notifications.getActiveNotifications();
      final activeNotificationIds =
          activeNotifications.map((n) => n.id).toSet();

      // Verify each mission has its notification
      for (final mission in _missions.where((m) => !m.isCompleted)) {
        if (!activeNotificationIds.contains(mission.notificationId)) {
          developer.log(
            'Health check: Missing notification for mission ${mission.title}',
          );
          await _scheduleNotification(mission);
        }
      }

      // Remove any orphaned notifications
      for (final notification in activeNotifications) {
        if (notification.id != null) {
          // Add null check
          final missionExists = _missions.any(
            (m) => m.notificationId == notification.id,
          );
          if (!missionExists) {
            await _notifications.cancel(
              notification.id!,
            ); // Use non-null assertion after check
            developer.log(
              'Health check: Removed orphaned notification ${notification.id}',
            );
          }
        }
      }
    } catch (e) {
      developer.log('Failed to verify notifications: $e');
    }
  }

  Future<void> _validateDataConsistency() async {
    try {
      // Verify mission IDs are unique
      final notificationIds = _missions.map((m) => m.notificationId).toSet();
      if (notificationIds.length != _missions.length) {
        developer.log('Health check: Duplicate mission IDs detected');
        await _repairDuplicateIds();
      }

      // Verify mission references in completed and deleted lists
      for (final mission in _completedMissions) {
        if (_missions.any((m) => m.notificationId == mission.notificationId)) {
          developer.log(
            'Health check: Mission ${mission.title} exists in both active and completed lists',
          );
          _completedMissions.removeWhere(
            (m) => m.notificationId == mission.notificationId,
          );
        }
      }

      for (final mission in _deletedMissions) {
        if (_missions.any((m) => m.notificationId == mission.notificationId)) {
          developer.log(
            'Health check: Mission ${mission.title} exists in both active and deleted lists',
          );
          _deletedMissions.removeWhere(
            (m) => m.notificationId == mission.notificationId,
          );
        }
      }

      // Save any changes
      if (_missions.isNotEmpty) {
        await _saveMissions(_missions);
      }
    } catch (e) {
      developer.log('Failed to validate data consistency: $e');
    }
  }

  Future<void> _repairDuplicateIds() async {
    mechanicum.setAIActive(true);
    try {
      final seenIds = <String>{};
      final missionsToUpdate = <MissionData>[];
      for (final mission in _missions) {
        final currentId = mission.id ?? '';
        if (seenIds.contains(currentId)) {
          final newId = _generateUniqueMissionId();
          missionsToUpdate.add(mission.copyWith(id: newId));
          print('Repaired duplicate mission ID: ${mission.title}');
          _logRepair(
            'Duplicate mission ID',
            'Assigned new ID $newId to ${mission.title}',
          );
        } else {
          seenIds.add(currentId);
        }
      }
      for (final mission in missionsToUpdate) {
        final index = _missions.indexWhere(
          (m) => m.notificationId == mission.notificationId,
        );
        if (index != -1) {
          _missions[index] = mission;
          await _scheduleNotification(mission);
        }
      }
      await _saveData();
      notifyListeners();
      printAllMissionData();
    } catch (e) {
      print('Error repairing duplicate mission IDs: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _restoreLostNotifications() async {
    try {
      final activeNotifications = await _notifications.getActiveNotifications();
      final activeIds = activeNotifications.map((n) => n.id).toSet();

      for (final mission in _missions.where((m) => !m.isCompleted)) {
        if (!activeIds.contains(mission.notificationId)) {
          developer.log(
            'Restoring lost notification for mission: ${mission.title}',
          );
          await _scheduleNotification(mission);
        }
      }
    } catch (e) {
      developer.log('Error restoring lost notifications: $e');
    }
  }

  Future<void> _verifyMissionSchedules() async {
    try {
      final now = DateTime.now();
      for (final mission in _missions) {
        if (mission.type == MissionType.daily && !mission.isCompleted) {
          final lastCompleted = mission.lastCompleted;
          if (lastCompleted != null && !_isSameDay(lastCompleted, now)) {
            // Mission should be refreshed
            await _refreshMission(mission);
          }
        }
      }
    } catch (e) {
      developer.log('Error verifying mission schedules: $e');
    }
  }

  void _setupAppLifecycleListener() {
    SystemChannels.lifecycle.setMessageHandler((msg) async {
      if (msg == AppLifecycleState.resumed.toString()) {
        // Resume background refresh
        _startBackgroundRefresh();
        // Check for missed refreshes
        _checkMissedRefreshes();
      } else if (msg == AppLifecycleState.paused.toString()) {
        // Pause background refresh
        _backgroundRefreshTimer?.cancel();
        _isBackgroundRefreshActive = false;
      }
      return null;
    });
  }

  Future<void> completeSubtask(
    MissionData mission,
    MissionSubtask subtask, {
    bool fromNotification = false,
  }) async {
    try {
      developer.log(
        'Completing subtask: ${subtask.name} for mission: ${mission.title}',
      );

      // Match on both id and notificationId, log if more than one match
      final missionIndexes =
          _missions
              .asMap()
              .entries
              .where(
                (entry) =>
                    entry.value.id == mission.id &&
                    entry.value.notificationId == mission.notificationId,
              )
              .map((entry) => entry.key)
              .toList();
      if (missionIndexes.length > 1) {
        developer.log(
          'Warning: More than one mission matched for subtask completion (id: ${mission.id}, notificationId: ${mission.notificationId})',
        );
      }
      final missionIndex =
          missionIndexes.isNotEmpty ? missionIndexes.first : -1;

      if (missionIndex != -1) {
        // Create updated subtask with incremented count
        final updatedSubtask = subtask.copyWith(
          currentCompletions: subtask.currentCompletions + 1,
          currentCount:
              subtask.isCounterBased
                  ? subtask.currentCount + 1
                  : subtask.currentCount,
        );

        // Create updated mission with new subtask
        final updatedSubtasks = List<MissionSubtask>.from(mission.subtasks);
        final subtaskIndex = updatedSubtasks.indexWhere(
          (s) => s.name == subtask.name,
        );
        if (subtaskIndex != -1) {
          updatedSubtasks[subtaskIndex] = updatedSubtask;
        }

        // Check if all subtasks are complete
        bool allSubtasksComplete = updatedSubtasks.every(
          (s) =>
              s.isCounterBased
                  ? s.currentCount >=
                      (s.requiredCompletions > 0 ? s.requiredCompletions : 1)
                  : s.currentCompletions >= s.requiredCompletions,
        );

        final updatedMission = mission.copyWith(
          isCompleted: allSubtasksComplete,
          lastCompleted: allSubtasksComplete ? DateTime.now() : null,
          hasFailed: false, // Remove failed status when progress is made
          subtasks: updatedSubtasks,
        );

        // Log subtask completion
        await _logMissionEvent(
          title: 'Subtask Completed',
          description:
              'Completed subtask: ${subtask.name} in mission: ${mission.title}',
          mission: updatedMission,
          metadata: {
            'subtaskName': subtask.name,
            'isCounterBased': updatedSubtask.isCounterBased,
            'newCount': updatedSubtask.currentCount,
            'newCompletions': updatedSubtask.currentCompletions,
            'missionCompleted': allSubtasksComplete,
          },
        );

        // Update the mission in state
        final updatedMissions = List<MissionData>.from(_missions);
        updatedMissions[missionIndex] = updatedMission;
        _missions = updatedMissions;

        // Update notification
        await _notifications.cancel(mission.notificationId);
        await _showNotificationForMission(updatedMission);

        // Save changes
        await _saveMissions(_missions);
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        // Always validate after completion
        await _validateMissionIdentifiers();
        await _validateDataConsistency();
      } else {
        developer.log(
          'Mission not found for subtask completion: ${mission.title}',
        );
      }
    } catch (e, stackTrace) {
      developer.log(
        'Error completing subtask ${subtask.name}: $e\n$stackTrace',
        error: e,
        stackTrace: stackTrace,
      );
      throw AppError(
        'Failed to complete subtask',
        'COMPLETE_SUBTASK_ERROR',
        code: 'COMPLETE_SUBTASK_ERROR',
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  // Add new methods for robust mission identification

  Future<void> _validateMissionIdentifiers() async {
    try {
      // Check for duplicate IDs
      final missionIds = _missions.map((m) => m.id).toSet();
      final notificationIds = _missions.map((m) => m.notificationId).toSet();

      if (missionIds.length != _missions.length) {
        developer.log('Duplicate mission IDs detected');
        await _repairDuplicateMissionIds();
      }

      if (notificationIds.length != _missions.length) {
        developer.log('Duplicate notification IDs detected');
        await _repairDuplicateNotificationIds();
      }

      // Validate mission references
      for (final mission in _missions) {
        if (mission.id == null ||
            (mission.id != null && mission.id?.isEmpty == true) ||
            mission.notificationId <= 0) {
          developer.log(
            'Invalid mission identifiers detected for: ${mission.title}',
          );
          await _repairMissionIdentifiers(mission);
        }
      }
    } catch (e) {
      developer.log('Error validating mission identifiers: $e');
    }
  }

  Future<void> _repairDuplicateMissionIds() async {
    mechanicum.setAIActive(true);
    try {
      final seenIds = <String>{};
      final missionsToUpdate = <MissionData>[];
      for (final mission in _missions) {
        final currentId = mission.id ?? '';
        if (seenIds.contains(currentId)) {
          final newId = _generateUniqueMissionId();
          missionsToUpdate.add(mission.copyWith(id: newId));
          print('Repaired duplicate mission ID: ${mission.title}');
          _logRepair(
            'Duplicate mission ID',
            'Assigned new ID $newId to ${mission.title}',
          );
        } else {
          seenIds.add(currentId);
        }
      }
      for (final mission in missionsToUpdate) {
        final index = _missions.indexWhere(
          (m) => m.notificationId == mission.notificationId,
        );
        if (index != -1) {
          _missions[index] = mission;
          await _scheduleNotification(mission);
        }
      }
      await _saveData();
      notifyListeners();
      printAllMissionData();
    } catch (e) {
      print('Error repairing duplicate mission IDs: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _repairDuplicateNotificationIds() async {
    mechanicum.setAIActive(true);
    try {
      print('Starting repair of duplicate notification IDs...');
      final seenIds = <int>{};
      final missionsToUpdate = <MissionData>[];

      // First pass: identify duplicates
      for (final mission in _missions) {
        if (seenIds.contains(mission.notificationId)) {
          final newId = _generateUniqueNotificationId();
          missionsToUpdate.add(mission.copyWith(notificationId: newId));
          print(
            'Found duplicate notification ID: ${mission.notificationId} for mission: ${mission.title}',
          );
          _logRepair(
            'Duplicate notification ID',
            'Assigned new notificationId $newId to ${mission.title}',
            missionId: mission.id,
          );
        } else {
          seenIds.add(mission.notificationId);
        }
      }

      // Second pass: update missions in the list
      if (missionsToUpdate.isNotEmpty) {
        for (final updatedMission in missionsToUpdate) {
          final index = _missions.indexWhere((m) => m.id == updatedMission.id);
          if (index != -1) {
            _missions[index] = updatedMission;
            await _scheduleNotification(updatedMission);
            print(
              'Updated mission with new notification ID: ${updatedMission.title}',
            );
          }
        }

        await _saveMissions(_missions);
        notifyListeners();
        print('Completed repair of duplicate notification IDs');
        printAllMissionData();
      } else {
        print('No duplicate notification IDs found to repair');
      }
    } catch (e) {
      print('Error repairing duplicate notification IDs: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _repairMissionIdentifiers(MissionData mission) async {
    mechanicum.setAIActive(true);
    try {
      final newId = _generateUniqueMissionId();
      final newNotificationId = _generateUniqueNotificationId();
      final repairedMission = mission.copyWith(
        id: newId,
        notificationId: newNotificationId,
      );
      final index = _missions.indexWhere((m) => m.title == mission.title);
      if (index != -1) {
        _missions[index] = repairedMission;
        await _scheduleNotification(repairedMission);
        await _saveData();
        notifyListeners();
        print('Repaired mission identifiers for: ${mission.title}');
        _logRepair(
          'Invalid mission identifiers',
          'Assigned new id $newId and notificationId $newNotificationId to ${mission.title}',
        );
        printAllMissionData();
      }
    } catch (e) {
      print('Error repairing mission identifiers: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _repairMissionCreationState(MissionData mission) async {
    mechanicum.setAIActive(true);
    try {
      final repairedMission = mission.copyWith(
        createdAt: mission.createdAt ?? DateTime.now(),
        isCompleted: false,
        hasFailed: false,
        currentCount: 0,
        subtasks:
            mission.subtasks
                .map(
                  (subtask) =>
                      subtask.copyWith(currentCompletions: 0, currentCount: 0),
                )
                .toList(),
      );
      final index = _missions.indexWhere((m) => m.id == mission.id);
      if (index != -1) {
        _missions[index] = repairedMission;
        await _showNotificationForMission(repairedMission);
        print('Repaired mission creation state: ${mission.title}');
        _logRepair(
          'Invalid mission creation state',
          'Reset state for ${mission.title}',
        );
        await _saveData();
        notifyListeners();
        printAllMissionData();
      }
    } catch (e) {
      print('Error repairing mission creation state: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  // Enhanced repair methods for specific health check failures
  Future<void> _repairInvalidSubtaskMasteryValues() async {
    mechanicum.setAIActive(true);
    try {
      print('Starting repair of invalid subtask mastery values...');
      bool hasChanges = false;

      for (int i = 0; i < _missions.length; i++) {
        final mission = _missions[i];
        final updatedSubtaskMasteryValues = <String, double>{};
        bool missionNeedsUpdate = false;

        // Check and fix subtask mastery values
        for (final entry in mission.subtaskMasteryValues.entries) {
          if (entry.value <= 0) {
            // Set a valid default mastery value (1.0)
            updatedSubtaskMasteryValues[entry.key] = 1.0;
            missionNeedsUpdate = true;
            print(
              'Fixed invalid subtask mastery value for mission: ${mission.title}, subtask: ${entry.key}',
            );
            _logRepair(
              'Invalid subtask mastery value',
              'Set mastery value to 1.0 for subtask ${entry.key} in mission ${mission.title}',
              missionId: mission.id,
            );
          } else {
            updatedSubtaskMasteryValues[entry.key] = entry.value;
          }
        }

        if (missionNeedsUpdate) {
          final repairedMission = mission.copyWith(
            subtaskMasteryValues: updatedSubtaskMasteryValues,
          );
          _missions[i] = repairedMission;
          hasChanges = true;
        }
      }

      if (hasChanges) {
        await _saveMissions(_missions);
        notifyListeners();
        print('Completed repair of invalid subtask mastery values');
        printAllMissionData();
      } else {
        print('No invalid subtask mastery values found to repair');
      }
    } catch (e) {
      print('Error repairing invalid subtask mastery values: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  Future<void> _repairInvalidMissionIdentifiers() async {
    mechanicum.setAIActive(true);
    try {
      print('Starting repair of invalid mission identifiers...');
      bool hasChanges = false;

      for (int i = 0; i < _missions.length; i++) {
        final mission = _missions[i];
        bool needsRepair = false;
        String? newId;
        int? newNotificationId;

        // Check for null or empty mission ID
        if (mission.id == null || mission.id!.isEmpty) {
          newId = _generateUniqueMissionId();
          needsRepair = true;
          print('Fixed null/empty mission ID for: ${mission.title}');
          _logRepair(
            'Invalid mission ID',
            'Generated new mission ID $newId for ${mission.title}',
            missionId: mission.id,
          );
        }

        // Check for invalid notification ID
        if (mission.notificationId <= 0) {
          newNotificationId = _generateUniqueNotificationId();
          needsRepair = true;
          print('Fixed invalid notification ID for: ${mission.title}');
          _logRepair(
            'Invalid notification ID',
            'Generated new notification ID $newNotificationId for ${mission.title}',
            missionId: mission.id,
          );
        }

        if (needsRepair) {
          final repairedMission = mission.copyWith(
            id: newId ?? mission.id,
            notificationId: newNotificationId ?? mission.notificationId,
          );
          _missions[i] = repairedMission;
          hasChanges = true;

          // Update notification if notification ID changed
          if (newNotificationId != null) {
            await _scheduleNotification(repairedMission);
          }
        }
      }

      if (hasChanges) {
        await _saveMissions(_missions);
        notifyListeners();
        print('Completed repair of invalid mission identifiers');
        printAllMissionData();
      } else {
        print('No invalid mission identifiers found to repair');
      }
    } catch (e) {
      print('Error repairing invalid mission identifiers: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  // Enhanced validation method that calls specific repairs
  // REMOVED: Duplicate function - keeping the more comprehensive version below

  Future<void> _logMissionEvent({
    required String title,
    required String description,
    MissionData? mission,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final eventMetadata = {
        'eventTime': DateTime.now().toIso8601String(),
        if (mission != null) ...{
          'missionId': mission.id,
          'missionTitle': mission.title,
          'missionType': mission.type.toString(),
        },
        if (metadata != null) ...metadata,
      };

      final context = navigatorKey.currentContext;
      if (context != null) {
        final historyProvider = Provider.of<AppHistoryProvider>(
          context,
          listen: false,
        );
        await historyProvider.logMission(
          title: title,
          description: description,
          metadata: eventMetadata,
        );
      }
    } catch (e) {
      developer.log('Error logging mission event: $e');
    }
  }

  Future<void> _logMissionStateChange({
    required MissionData mission,
    required String oldState,
    required String newState,
  }) async {
    try {
      final context = navigatorKey.currentContext;
      if (context != null) {
        final historyProvider = Provider.of<AppHistoryProvider>(
          context,
          listen: false,
        );
        await historyProvider.logStateChange(
          component: 'Mission',
          change: 'State changed from $oldState to $newState',
          metadata: {
            'missionId': mission.id,
            'missionTitle': mission.title,
            'oldState': oldState,
            'newState': newState,
            'timestamp': DateTime.now().toIso8601String(),
          },
        );
      }
    } catch (e) {
      developer.log('Error logging mission state change: $e');
    }
  }

  Future<void> _logMissionValidation({
    required MissionData mission,
    required bool isValid,
    required String reason,
  }) async {
    try {
      final context = navigatorKey.currentContext;
      if (context != null) {
        final historyProvider = Provider.of<AppHistoryProvider>(
          context,
          listen: false,
        );
        await historyProvider.logMission(
          title: 'Mission Validation',
          description:
              'Mission validation ${isValid ? 'passed' : 'failed'}: $reason',
          metadata: {
            'isValid': isValid,
            'reason': reason,
            'missionId': mission.id,
            'missionTitle': mission.title,
            'missionType': mission.type.toString(),
            'validatedAt': DateTime.now().toIso8601String(),
          },
        );
      }
    } catch (e) {
      developer.log('Error logging mission validation: $e');
    }
  }

  Future<void> completeMission(MissionData mission) async {
    try {
      final updatedMission = mission.copyWith(
        isCompleted: true,
        lastCompleted: DateTime.now(),
        hasFailed: false,
      );

      // Update the mission in state
      final index = _missions.indexWhere((m) => m.id == mission.id);
      if (index != -1) {
        final updatedMissions = List<MissionData>.from(_missions);
        updatedMissions[index] = updatedMission;
        _missions.clear();
        _missions.addAll(updatedMissions);

        // Record daily progress after completing the mission
        updatedMission.recordDailyProgress();

        // Add mastery progress if linked
        if (mission.linkedMasteryId != null && mission.masteryValue > 0) {
          final masteryProvider = Provider.of<MasteryProvider>(
            navigatorKey.currentContext!,
            listen: false,
          );
          // Add mastery value for each completion
          await masteryProvider.addProgress(
            mission.linkedMasteryId!,
            'Mission: ${mission.title}',
            mission.masteryValue,
          );
        }

        // Save changes
        await _saveMissions(_missions);
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();
      }
    } catch (e) {
      print('Error completing mission: $e');
    }
  }

  bool _validateSubtaskState(MissionSubtask subtask) {
    try {
      // Validate subtask name
      if (subtask.name.trim().isEmpty) {
        developer.log('Subtask validation failed: Empty name');
        return false;
      }

      // Validate counter-based subtask
      if (subtask.isCounterBased) {
        if (subtask.currentCount < 0) {
          developer.log('Invalid current count for subtask: ${subtask.name}');
          return false;
        }
        if (subtask.requiredCompletions < 0) {
          developer.log(
            'Invalid required completions for subtask: ${subtask.name}',
          );
          return false;
        }
      } else {
        // Validate regular subtask
        if (subtask.currentCompletions < 0) {
          developer.log(
            'Invalid current completions for subtask: ${subtask.name}',
          );
          return false;
        }
        if (subtask.requiredCompletions < 0) {
          developer.log(
            'Invalid required completions for subtask: ${subtask.name}',
          );
          return false;
        }
      }

      // Validate mastery values if present
      if (subtask.linkedMasteryId != null && subtask.masteryValue <= 0) {
        developer.log('Invalid mastery value for subtask: ${subtask.name}');
        return false;
      }

      return true;
    } catch (e) {
      developer.log('Error validating subtask state: $e');
      return false;
    }
  }

  // Add method to check if app should be locked
  bool shouldLockApp() {
    return _isDailyLocked || _isWeeklyLocked;
  }

  // Add method to get current refresh state
  String getRefreshState() {
    if (_isWeeklyLocked) {
      return 'Weekly refresh required';
    } else if (_isDailyLocked) {
      return 'Daily refresh required';
    }
    return 'Up to date';
  }

  void incrementMissionCounter(MissionData mission) {
    final index = _missions.indexWhere(
      (m) => m.notificationId == mission.notificationId,
    );
    if (index != -1) {
      final updatedMission = mission.copyWith(
        currentCount: mission.currentCount + 1,
      );
      _missions[index] = updatedMission;

      // Record daily progress after incrementing the counter
      updatedMission.recordDailyProgress();

      // Update UI immediately
      notifyListeners();

      // Update notifications and save in background
      _updateNotification(updatedMission);
      _saveMissions(_missions);
    }
  }

  Future<void> _updateNotification(MissionData mission) async {
    try {
      await _notifications.cancel(mission.notificationId);
      await _showNotificationForMission(mission);
    } catch (e) {
      developer.log('Error updating notification: $e');
    }
  }

  // Add this call in _startRefreshCheck()

  Future<void> _attemptRefreshRecovery() async {
    try {
      final now = DateTime.now();

      // Check for missed daily refreshes
      if (now.hour < 12) {
        for (var mission in _missions.where(
          (m) => m.type == MissionType.daily,
        )) {
          if (mission.createdAt != null &&
              !_isSameDay(mission.createdAt!, now)) {
            await _refreshMission(mission);
          }
        }
      }

      // Check for missed weekly refreshes
      if (now.weekday == DateTime.monday && now.hour < 12) {
        for (var mission in _missions.where(
          (m) => m.type == MissionType.weekly,
        )) {
          if (mission.createdAt != null &&
              mission.createdAt!.isBefore(
                now.subtract(const Duration(days: 1)),
              )) {
            await _refreshMission(mission);
          }
        }
      }

      _lastRefreshTime = now;
      _refreshButtonColor = Colors.green;
      _isDailyLocked = false;
      _isWeeklyLocked = false;
      notifyListeners();
    } catch (e) {
      developer.log('Error in refresh recovery: $e');
    }
  }

  Future<void> _verifyRefreshState() async {
    try {
      final now = DateTime.now();
      bool needsRefresh = false;

      // Check daily missions
      for (var mission in _missions.where((m) => m.type == MissionType.daily)) {
        if (mission.createdAt != null && !_isSameDay(mission.createdAt!, now)) {
          needsRefresh = true;
          _refreshButtonColor = Colors.red;
          _isDailyLocked = true;
          break;
        }
      }

      // Check weekly missions
      if (now.weekday == DateTime.monday) {
        for (var mission in _missions.where(
          (m) => m.type == MissionType.weekly,
        )) {
          if (mission.createdAt != null &&
              mission.createdAt!.isBefore(
                now.subtract(const Duration(days: 1)),
              )) {
            needsRefresh = true;
            _refreshButtonColor = Colors.orange;
            _isWeeklyLocked = true;
            break;
          }
        }
      }

      if (needsRefresh) {
        developer.log('Refresh state verification: Refresh needed');
        await _attemptRefreshRecovery();
      } else {
        // Reset refresh state if no refresh is needed
        _refreshButtonColor = Colors.white;
        _isDailyLocked = false;
        _isWeeklyLocked = false;
        developer.log('Refresh state verification: All missions up to date');
      }

      notifyListeners();
    } catch (e) {
      developer.log('Error verifying refresh state: $e');
      // Reset refresh state on error to prevent blocking mission creation
      _refreshButtonColor = Colors.white;
      _isDailyLocked = false;
      _isWeeklyLocked = false;
      notifyListeners();
    }
  }

  bool _shouldMarkMissionAsFailed(MissionData mission, DateTime now) {
    // For daily missions, check if they're incomplete at the end of day
    if (mission.type == MissionType.daily) {
      if (now.hour >= 23 && now.minute >= 59) {
        return !mission.isCompleted && _missionHasProgress(mission);
      }
    }
    // For weekly missions, check if they're incomplete at the end of week
    else if (mission.type == MissionType.weekly) {
      if (now.weekday == DateTime.sunday &&
          now.hour >= 23 &&
          now.minute >= 59) {
        return !mission.isCompleted && _missionHasProgress(mission);
      }
    }
    return false;
  }

  bool _missionHasProgress(MissionData mission) {
    // For counter-based missions
    if (mission.isCounterBased) {
      // If mission has a target count, check against that
      if (mission.targetCount > 0) {
        return mission.currentCount < mission.targetCount;
      }
      // For missions without target count, check if count is less than 1
      return mission.currentCount < 1;
    }

    // For missions with subtasks
    if (mission.subtasks.isNotEmpty) {
      return mission.subtasks.any((subtask) {
        if (subtask.isCounterBased) {
          // If subtask has required completions, check against that
          if (subtask.requiredCompletions > 0) {
            return subtask.currentCount < subtask.requiredCompletions;
          }
          // For subtasks without required completions, check if count is less than 1
          return subtask.currentCount < 1;
        } else {
          // For regular subtasks, check if not fully completed
          return subtask.currentCompletions < subtask.requiredCompletions;
        }
      });
    }

    // For simple missions without counters or subtasks
    return !mission.isCompleted;
  }

  Future<void> _checkFailedMissions() async {
    try {
      final now = DateTime.now();
      bool needsUpdate = false;

      // Check all missions for failure status
      for (var mission in _missions) {
        if (_shouldMarkMissionAsFailed(mission, now)) {
          final index = _missions.indexWhere((m) => m.id == mission.id);
          if (index != -1) {
            _missions[index] = mission.copyWith(hasFailed: true);
            needsUpdate = true;
            developer.log(
              'Marked mission as failed on startup: ${mission.title}',
            );
          }
        }
      }

      if (needsUpdate) {
        await _saveMissions(_missions);
        notifyListeners();
      }
    } catch (e) {
      developer.log('Error checking failed missions: $e');
    }
  }

  Future<void> _verifyMissionCreation() async {
    try {
      final now = DateTime.now();
      bool needsUpdate = false;

      // Check all missions for creation date
      for (var mission in _missions) {
        if (mission.createdAt == null) {
          // Fix missions without creation date
          final index = _missions.indexWhere((m) => m.id == mission.id);
          if (index != -1) {
            _missions[index] = mission.copyWith(createdAt: now);
            needsUpdate = true;
            developer.log('Fixed mission creation date: ${mission.title}');
          }
        }
      }

      // Check for missions with invalid state
      for (var mission in _missions) {
        // Skip validation for newly created missions (within last 5 minutes)
        if (mission.createdAt != null &&
            now.difference(mission.createdAt!) < const Duration(minutes: 5)) {
          continue;
        }

        if (!await _validateMissionCreation(
          title: mission.title,
          type: mission.type,
          subtasks: mission.subtasks,
          isCounterBased: mission.isCounterBased,
          targetCount: mission.targetCount,
          linkedMasteryId: mission.linkedMasteryId,
          masteryValue: mission.masteryValue,
        )) {
          developer.log('Found mission with invalid state: ${mission.title}');
          // Attempt to repair the mission
          await _repairMissionCreationState(mission);
          needsUpdate = true;
        }
      }

      if (needsUpdate) {
        await _saveMissions(_missions);
        notifyListeners();
      }
    } catch (e) {
      developer.log('Error verifying mission creation: $e');
    }
  }

  Future<void> _showImmediateNotification(MissionData mission) async {
    try {
      const androidDetails = AndroidNotificationDetails(
        'mission_notifications',
        'Mission Notifications',
        channelDescription: 'Notifications for mission updates',
        importance: Importance.high,
        priority: Priority.high,
        showWhen: true,
      );

      const iosDetails = DarwinNotificationDetails(
        presentAlert: true,
        presentBadge: true,
        presentSound: true,
      );

      const notificationDetails = NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      );

      await _notifications.show(
        mission.notificationId,
        'New Mission Created',
        'Mission "${mission.title}" has been created',
        notificationDetails,
      );

      developer.log(
        'Immediate notification shown for mission: ${mission.title}',
      );
    } catch (e) {
      developer.log('Error showing immediate notification: $e');
      // Don't throw the error as this is not critical functionality
    }
  }

  /// Comprehensive AI Watchdog: Validate all missions and system health
  Future<List<String>> validateAllMissions({
    bool attemptRepair = true,
    bool stepwise = false,
    void Function(int idx, String result, bool passed)? onStep,
    BuildContext? context,
    bool showUser = false,
  }) async {
    print('MissionProvider.validateAllMissions called!');
    final checklist = <String>[];
    bool allPassed = true;
    int idx = 0;

    // Print mission data before repair
    printAllMissionData();

    // Backup before attempting repair
    if (attemptRepair) {
      await backupMissions();
    }

    // --- Add summary of frequent issues and health score ---
    final repairCountsSummary = getRepairLogSummary();
    String healthScore;
    if (repairCountsSummary.values.any((v) => v > 10)) {
      healthScore = '❌ Frequent mission integrity problems!';
    } else if (repairCountsSummary.values.any((v) => v > 3)) {
      healthScore = '⚠️ Some recurring issues detected.';
    } else {
      healthScore = '✅ All good (no frequent issues).';
    }
    if (repairCountsSummary.isNotEmpty) {
      checklist.add('--- Mechanicum Summary ---');
      checklist.add('Health: $healthScore');
      checklist.add('Most frequent issues:');
      repairCountsSummary.entries.toList().sort(
        (a, b) => b.value.compareTo(a.value),
      );
      for (final entry in repairCountsSummary.entries) {
        if (entry.value > 1) {
          checklist.add('• ${entry.key}: ${entry.value} times');
        }
      }
      checklist.add('--------------------------');
    } else {
      checklist.add('--- Mechanicum Summary ---');
      checklist.add('Health: $healthScore');
      checklist.add('--------------------------');
    }
    // ... existing code ...

    // 1. Unique IDs and notification IDs
    final allMissions = [
      ..._missions,
      ..._completedMissions,
      ..._deletedMissions,
    ];
    final idSet = <String>{};
    final notificationIdSet = <int>{};
    bool uniquePassed = true;
    for (final m in allMissions) {
      if (m.id == null || m.id!.isEmpty) {
        checklist.add('❌ Mission with empty or null ID: ${m.title}');
        uniquePassed = false;
        if (attemptRepair) {
          developer.log(
            'Attempting to repair empty/null mission ID for: ${m.title}',
          );
          m.copyWith(id: _generateUniqueMissionId());
          _logRepair(
            'Empty or null mission ID',
            'Generated new unique ID for mission ${m.title}',
          );
        }
      }
      if (!idSet.add(m.id!)) {
        checklist.add('❌ Duplicate mission ID: ${m.id} (${m.title})');
        uniquePassed = false;
        if (attemptRepair) {
          developer.log(
            'Attempting to repair duplicate mission ID for: ${m.title}',
          );
          await _repairDuplicateMissionIds();
          _logRepair(
            'Duplicate mission ID',
            'Repaired duplicate mission ID for ${m.title}',
          );
        }
      }
      if (!notificationIdSet.add(m.notificationId)) {
        checklist.add(
          '❌ Duplicate notification ID: ${m.notificationId} (${m.title})',
        );
        uniquePassed = false;
        if (attemptRepair) {
          developer.log(
            'Attempting to repair duplicate notification ID for: ${m.title}',
          );
          await _repairDuplicateNotificationIds();
          _logRepair(
            'Duplicate notification ID',
            'Repaired duplicate notification ID for ${m.title}',
          );
        }
      }
    }
    if (uniquePassed)
      checklist.add('✅ All mission IDs and notification IDs are unique.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, uniquePassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

    // 2. Mission state validity
    bool statePassed = true;
    for (final m in allMissions) {
      if (m.id == null || m.id!.isEmpty || m.notificationId <= 0) {
        checklist.add('❌ Invalid mission identifiers: ${m.title}');
        statePassed = false;
        if (attemptRepair) {
          developer.log(
            'Attempting to repair invalid mission identifiers for: ${m.title}',
          );
          await _repairInvalidMissionIdentifiers();
          _logRepair(
            'Invalid mission identifiers',
            'Repaired mission identifiers for ${m.title}',
          );
        }
      }
      if (m.title.trim().isEmpty) {
        checklist.add('❌ Mission with empty title: ${m.id}');
        statePassed = false;
      }
      if (m.isCounterBased && (m.targetCount < 0 || m.currentCount < 0)) {
        checklist.add('❌ Invalid counter values for mission: ${m.title}');
        statePassed = false;
      }
      if (m.subtasks.isNotEmpty) {
        for (final subtask in m.subtasks) {
          if (!_validateSubtaskState(subtask)) {
            checklist.add('❌ Invalid subtask state in mission: ${m.title}');
            statePassed = false;
          }
        }
      }
      if (m.isCompleted && m.hasFailed) {
        checklist.add(
          '❌ Mission cannot be both completed and failed: ${m.title}',
        );
        statePassed = false;
      }
      if (m.linkedMasteryId != null && m.masteryValue <= 0) {
        checklist.add('❌ Invalid mastery value for mission: ${m.title}');
        statePassed = false;
      }
      for (final entry in m.subtaskMasteryValues.entries) {
        if (entry.value <= 0) {
          checklist.add(
            '❌ Invalid subtask mastery value in mission: ${m.title}',
          );
          statePassed = false;
          if (attemptRepair) {
            developer.log(
              'Attempting to repair invalid subtask mastery value for: ${m.title}',
            );
            await _repairInvalidSubtaskMasteryValues();
            _logRepair(
              'Invalid subtask mastery value',
              'Repaired subtask mastery value for ${m.title}',
            );
          }
        }
      }
    }
    if (statePassed) checklist.add('✅ All missions have valid state.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, statePassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

    // If repairs were attempted, run comprehensive repair and reload data
    if (attemptRepair) {
      print('Running comprehensive repair for all detected issues...');
      await _validateAndRepairAllIssues();

      // Reload missions from storage to ensure we have the latest data
      await _loadMissions();
      await _loadDeletedMissions();

      print(
        'Data reloaded after repairs. Current mission count: ${_missions.length}',
      );
    }

    // Print mission data after repair
    printAllMissionData();

    // ... existing code ...
    return checklist;
  }

  // Example: log a repair
  void _logRepair(String issue, String action, {String? missionId}) {
    mechanicum.logRepair(issue, action, missionId: missionId);
    // Optionally, keep only the last 100 entries
    if (_repairLog.length > 100) _repairLog.removeAt(0);
    _saveRepairLog();
  }

  // Get a summary of repair log issues and counts
  Map<String, int> getRepairLogSummary() {
    return mechanicum.getRepairLogSummary();
  }

  // Add a stub for compatibility with the shield dialog signature
  Future<void> validateAllMissionsCompat({
    required bool stepwise,
    required Null Function(dynamic idx, dynamic result, dynamic passed) onStep,
    required BuildContext context,
    required bool showUser,
  }) async {
    await validateAllMissions(
      stepwise: stepwise,
      onStep:
          (int idx, String result, bool passed) => onStep(idx, result, passed),
      context: context,
      showUser: showUser,
    );
  }

  // Call this in the constructor or on app start
  Future<void> initializeProvider() async {
    await loadRepairLog();
    await validateAllMissions(attemptRepair: true);
  }

  // After any mission state change, automatically validate and repair
  Future<void> onMissionStateChanged() async {
    await validateAllMissions(attemptRepair: true);
  }

  // In mission creation, edit, refresh, completion, deletion, and app start, call onMissionStateChanged()
  // For example, after _saveData(), _saveMissions(), or notifyListeners(), call onMissionStateChanged() if not already

  // Backup missions before repair
  Future<void> backupMissions() async {
    final prefs = await SharedPreferences.getInstance();
    final backup = jsonEncode({
      'missions': _missions.map((m) => m.toJson()).toList(),
      'completedMissions': _completedMissions.map((m) => m.toJson()).toList(),
      'deletedMissions': _deletedMissions.map((m) => m.toJson()).toList(),
    });
    await prefs.setString('missions_backup', backup);
  }

  // Restore missions from backup (for debug/developer use)
  Future<void> restoreMissionsFromBackup() async {
    final prefs = await SharedPreferences.getInstance();
    final backup = prefs.getString('missions_backup');
    if (backup != null) {
      final decoded = jsonDecode(backup);
      _missions =
          (decoded['missions'] as List)
              .map((m) => MissionData.fromJson(m as Map<String, dynamic>))
              .toList();
      _completedMissions =
          (decoded['completedMissions'] as List)
              .map((m) => MissionData.fromJson(m as Map<String, dynamic>))
              .toList();
      _deletedMissions =
          (decoded['deletedMissions'] as List)
              .map((m) => MissionData.fromJson(m as Map<String, dynamic>))
              .toList();
      await _saveData();
      notifyListeners();
    }
  }

  // Ensure isAIActive always reflects Mechanicum's state
  bool get isAIActive => mechanicum.isAIActive;

  // Refactored health check to always check all missions
  Future<void> performHealth({
    bool showPopup = false,
    BuildContext? context,
  }) async {
    mechanicum.setAIActive(true);
    try {
      developer.log('Starting application health check...');
      final allMissions = [
        ..._missions,
        ..._completedMissions,
        ..._deletedMissions,
      ];
      final idSet = <String>{};
      final notificationIdSet = <int>{};
      bool hasDuplicate = false;
      for (final m in allMissions) {
        if (m.id == null || m.id!.isEmpty || !idSet.add(m.id!)) {
          hasDuplicate = true;
        }
        if (!notificationIdSet.add(m.notificationId)) {
          hasDuplicate = true;
        }
      }
      if (hasDuplicate && context != null && showPopup) {
        await showDialog(
          context: context,
          builder:
              (ctx) => AlertDialog(
                title: const Text('Mission Integrity Warning'),
                content: const Text(
                  'Duplicate mission IDs or notification IDs found!',
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.of(ctx).pop(),
                    child: const Text('OK'),
                  ),
                ],
              ),
        );
      }
      // Validate and repair all missions
      for (final m in allMissions) {
        await _isValidMissionState(m);
      }
      await _verifyNotifications();
      await _validateDataConsistency();
      _checkMissedRefreshes();
      await _updateBadge();
      await _showSummaryNotification();
      await _restoreLostNotifications();
      await _verifyMissionSchedules();
      developer.log('Health check completed successfully');
    } catch (e) {
      developer.log('Health check failed: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  // Call health check after mission creation or edit
  Future<void> addMission(
    MissionData mission, {
    BuildContext? context,
    required String title,
    required String description,
    required MissionType type,
    required List<MissionSubtask> subtasks,
    String? linkedMasteryId,
    required double masteryValue,
    required Map<String, double> subtaskMasteryValues,
    required bool isCounterBased,
    required int targetCount,
    required String imageUrl,
  }) async {
    _missions.add(mission);
    await _validateAndRepairAllIssues();
    notifyListeners();
  }

  void printAllMissionData() {
    print('--- Current Missions ---');
    for (final m in _missions) {
      print(
        'Mission: id=${m.id}, notificationId=${m.notificationId}, title=${m.title}',
      );
    }
    print('--- End Missions ---');
  }

  /// Comprehensive repair method that fixes all detected issues in all mission lists
  Future<void> _validateAndRepairAllIssues() async {
    mechanicum.setAIActive(true);
    final List<String> suggestions = [];
    try {
      print(
        'Mechanicum: Starting comprehensive repair of all detected issues...',
      );
      final allMissions = <MissionData>[];
      allMissions.addAll(_missions);
      allMissions.addAll(_completedMissions);
      allMissions.addAll(_deletedMissions);

      final usedIds = <String>{};
      final usedNotificationIds = <int>{};
      final updatedMissions =
          <String, MissionData>{}; // key: mission.id or fallback to title

      for (var mission in allMissions) {
        var needsUpdate = false;
        var id = mission.id;
        var notificationId = mission.notificationId;

        // Fix ID
        if (id == null || id.isEmpty || usedIds.contains(id)) {
          id = _generateUniqueMissionId();
          needsUpdate = true;
          print(
            'Mechanicum: Fixed invalid or duplicate mission ID for: ${mission.title}',
          );
          _logRepair(
            'Invalid mission ID',
            'Generated new mission ID $id for ${mission.title}',
            missionId: mission.id,
          );
          suggestions.add(
            'Consider improving mission creation to always generate unique IDs.',
          );
          await _incrementIssue('duplicate_or_invalid_mission_id');
        }
        usedIds.add(id);

        // Fix notification ID
        if (notificationId <= 0 ||
            usedNotificationIds.contains(notificationId)) {
          notificationId = _generateUniqueNotificationId();
          needsUpdate = true;
          print(
            'Mechanicum: Fixed invalid or duplicate notification ID for: ${mission.title}',
          );
          _logRepair(
            'Invalid notification ID',
            'Generated new notification ID $notificationId for ${mission.title}',
            missionId: mission.id,
          );
          suggestions.add(
            'Consider improving notification scheduling to always use unique IDs.',
          );
          await _incrementIssue('duplicate_or_invalid_notification_id');
        }
        usedNotificationIds.add(notificationId);

        // Fix subtask mastery values and subtask state
        final fixedMastery = <String, double>{};
        final fixedSubtasks = <MissionSubtask>[];
        for (final subtask in mission.subtasks) {
          var subtaskNeedsUpdate = false;
          var masteryValue =
              subtask.masteryValue > 0 ? subtask.masteryValue : 1.0;
          if (subtask.masteryValue <= 0) {
            subtaskNeedsUpdate = true;
            print(
              'Mechanicum: Fixed invalid subtask mastery value for mission: ${mission.title}, subtask: ${subtask.name}',
            );
            _logRepair(
              'Invalid subtask mastery value',
              'Set mastery value to 1.0 for subtask ${subtask.name} in mission ${mission.title}',
              missionId: mission.id,
            );
            suggestions.add(
              'Consider validating mastery values on subtask creation.',
            );
            await _incrementIssue('invalid_subtask_mastery_value');
          }
          fixedMastery[subtask.name] = masteryValue;

          // Validate subtask state
          int currentCount = subtask.currentCount;
          int currentCompletions = subtask.currentCompletions;
          int requiredCompletions = subtask.requiredCompletions;
          if (subtask.isCounterBased) {
            if (currentCount < 0) {
              currentCount = 0;
              subtaskNeedsUpdate = true;
              suggestions.add(
                'Counter-based subtask ${subtask.name} had negative count. Reset to 0.',
              );
              await _incrementIssue('negative_counter_subtask_count');
            }
            if (requiredCompletions < 0) {
              requiredCompletions = 0;
              subtaskNeedsUpdate = true;
              suggestions.add(
                'Counter-based subtask ${subtask.name} had negative requiredCompletions. Reset to 0.',
              );
              await _incrementIssue(
                'negative_counter_subtask_requiredCompletions',
              );
            }
          } else {
            if (currentCompletions < 0) {
              currentCompletions = 0;
              subtaskNeedsUpdate = true;
              suggestions.add(
                'Completion-based subtask ${subtask.name} had negative completions. Reset to 0.',
              );
              await _incrementIssue('negative_completion_subtask_completions');
            }
            if (requiredCompletions < 0) {
              requiredCompletions = 1;
              subtaskNeedsUpdate = true;
              suggestions.add(
                'Completion-based subtask ${subtask.name} had negative requiredCompletions. Reset to 1.',
              );
              await _incrementIssue(
                'negative_completion_subtask_requiredCompletions',
              );
            }
          }
          if (subtask.name.trim().isEmpty) {
            subtaskNeedsUpdate = true;
            suggestions.add(
              'Subtask with empty name found in mission ${mission.title}.',
            );
            await _incrementIssue('empty_subtask_name');
          }
          fixedSubtasks.add(
            subtaskNeedsUpdate
                ? subtask.copyWith(
                  masteryValue: masteryValue,
                  currentCount: currentCount,
                  currentCompletions: currentCompletions,
                  requiredCompletions: requiredCompletions,
                  name: subtask.name.trim().isEmpty ? 'Subtask' : subtask.name,
                )
                : subtask,
          );
        }

        // Fix mission state
        var hasFailed = mission.hasFailed;
        if (mission.isCompleted && hasFailed) {
          hasFailed = false;
          needsUpdate = true;
          print(
            'Mechanicum: Fixed mission that was both completed and failed: ${mission.title}',
          );
          _logRepair(
            'Invalid mission state',
            'Reset failed state for completed mission ${mission.title}',
            missionId: mission.id,
          );
          suggestions.add(
            'Mission ${mission.title} was both completed and failed. Logic should prevent this.',
          );
          await _incrementIssue('completed_and_failed_mission');
        }

        // Fix empty title
        var title = mission.title;
        if (title.trim().isEmpty) {
          title = 'Mission $id';
          needsUpdate = true;
          print('Mechanicum: Fixed mission with empty title: $id');
          _logRepair(
            'Empty mission title',
            'Set default title for mission $id',
            missionId: id,
          );
          suggestions.add(
            'Mission with empty title found. Consider enforcing title on creation.',
          );
          await _incrementIssue('empty_mission_title');
        }

        // Fix counter-based missions with invalid values
        var targetCount = mission.targetCount;
        var currentCount = mission.currentCount;
        if (mission.isCounterBased) {
          if (targetCount < 0) {
            targetCount = 0;
            needsUpdate = true;
            suggestions.add(
              'Counter-based mission ${mission.title} had negative targetCount. Reset to 0.',
            );
            await _incrementIssue('negative_counter_mission_targetCount');
          }
          if (currentCount < 0) {
            currentCount = 0;
            needsUpdate = true;
            suggestions.add(
              'Counter-based mission ${mission.title} had negative currentCount. Reset to 0.',
            );
            await _incrementIssue('negative_counter_mission_currentCount');
          }
        }

        if (needsUpdate ||
            fixedSubtasks.any(
              (s) => s != mission.subtasks[fixedSubtasks.indexOf(s)],
            )) {
          updatedMissions[mission.id ?? mission.title] = mission.copyWith(
            id: id,
            notificationId: notificationId,
            subtaskMasteryValues:
                fixedMastery.isNotEmpty
                    ? fixedMastery
                    : mission.subtaskMasteryValues,
            hasFailed: hasFailed,
            title: title,
            targetCount: targetCount,
            currentCount: currentCount,
            subtasks:
                fixedSubtasks.isNotEmpty ? fixedSubtasks : mission.subtasks,
          );
        }
      }

      // Helper to update a list in place
      void updateList(List<MissionData> list) {
        for (var i = 0; i < list.length; i++) {
          final updated = updatedMissions[list[i].id ?? list[i].title];
          if (updated != null) list[i] = updated;
        }
      }

      updateList(_missions);
      updateList(_completedMissions);
      updateList(_deletedMissions);

      await _saveMissions(_missions);
      await _saveData();
      notifyListeners();
      print('Mechanicum: Comprehensive repair completed successfully');
      printAllMissionData();
      if (suggestions.isNotEmpty) {
        print('Mechanicum Suggestions for Improvement:');
        for (final suggestion in suggestions) {
          print('- $suggestion');
        }
        // Optionally, notify the user via UI or notification
        await showMechanicumAnalyticsNotification();
      }
    } catch (e) {
      print('Mechanicum: Error during comprehensive repair: $e');
      _logRepair('Comprehensive repair error', 'Error: $e');
    } finally {
      mechanicum.setAIActive(false);
    }
  }

  /// Public method to force a comprehensive repair of all issues
  Future<void> forceComprehensiveRepair() async {
    print('Mechanicum: Force comprehensive repair requested...');
    await mechanicum.performImmediateHealthCheck(() async {
      await _validateAndRepairAllIssues();
    });
  }

  /// Public method to check if Mechanicum is running
  bool get isMechanicumRunning => mechanicum.isRunning;

  /// Public method to get Mechanicum status
  String get mechanicumStatus {
    if (!mechanicum.isRunning) return 'Stopped';
    if (mechanicum.isAIActive) return 'Active - Repairing';
    return 'Running - Monitoring';
  }

  /// Public method to restart the Mechanicum
  Future<void> restartMechanicum() async {
    print('Mechanicum: Restart requested...');

    // Stop current instance
    mechanicum.stopContinuousHealthCheck();

    // Wait a moment
    await Future.delayed(const Duration(seconds: 1));

    // Reinitialize
    await _initializeMechanicum();

    print('Mechanicum: Restart completed');
  }

  Map<String, int> _issueFrequency = {};
  final String _issueFrequencyKey = 'mechanicum_issues';
  final int _issueNotificationThreshold =
      3; // Show notification if issue occurs 3+ times

  Future<void> _incrementIssue(String issue) async {
    _issueFrequency[issue] = (_issueFrequency[issue] ?? 0) + 1;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_issueFrequencyKey, jsonEncode(_issueFrequency));
  }

  Future<void> _loadIssueFrequency() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonStr = prefs.getString(_issueFrequencyKey);
    if (jsonStr != null) {
      _issueFrequency = Map<String, int>.from(jsonDecode(jsonStr));
    }
  }

  Future<void> showMechanicumAnalyticsNotification() async {
    // Find the most frequent issue
    if (_issueFrequency.isEmpty) return;
    final sorted =
        _issueFrequency.entries.toList()
          ..sort((a, b) => b.value.compareTo(a.value));
    final top = sorted.first;
    if (top.value >= _issueNotificationThreshold) {
      final plugin = FlutterLocalNotificationsPlugin();
      const android = AndroidNotificationDetails(
        'mechanicum_analytics',
        'Mechanicum Analytics',
        channelDescription: 'Mechanicum suggestions and analytics',
        importance: Importance.high,
        priority: Priority.high,
        icon: '@mipmap/ic_launcher',
      );
      const details = NotificationDetails(android: android);
      await plugin.show(
        10001,
        'Mechanicum Suggestion',
        'The issue "${top.key}" has occurred ${top.value} times. Consider improving this area.',
        details,
      );
    }
  }

  // Call this in your app's initState or provider init
  Future<void> initializeMechanicumAnalytics() async {
    await _loadIssueFrequency();
  }

  MechanicumSandboxResult? _lastSandboxResult;
  Map<String, dynamic>? _lastSandboxState;

  /// Deep copy missions and state for sandboxing
  Map<String, dynamic> _cloneAppState() {
    return {
      'missions':
          _missions
              .map(
                (m) => m.copyWith(
                  subtasks: m.subtasks.map((s) => s.copyWith()).toList(),
                ),
              )
              .toList(),
      'completedMissions':
          _completedMissions
              .map(
                (m) => m.copyWith(
                  subtasks: m.subtasks.map((s) => s.copyWith()).toList(),
                ),
              )
              .toList(),
      'deletedMissions':
          _deletedMissions
              .map(
                (m) => m.copyWith(
                  subtasks: m.subtasks.map((s) => s.copyWith()).toList(),
                ),
              )
              .toList(),
    };
  }

  /// Run a suggestion/repair in a sandboxed environment and return a report
  Future<MechanicumSandboxResult> runSandboxedSuggestion(
    String issueKey,
  ) async {
    // Deep copy state
    final sandbox = _cloneAppState();
    final List<String> changes = [];
    final List<String> testResults = [];
    bool success = true;
    String summary = '';

    // Simulate the repair logic on the sandbox state
    try {
      // Example: For each known issue, run the corresponding repair logic on the sandbox
      if (issueKey == 'duplicate_or_invalid_mission_id' ||
          issueKey == 'duplicate_or_invalid_notification_id') {
        // Enforce unique IDs in sandbox
        final ids = <String>{};
        final notificationIds = <int>{};
        for (var m in sandbox['missions']) {
          if (ids.contains(m.id) || m.id == null || m.id.isEmpty) {
            m = m.copyWith(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
            );
            changes.add('Fixed mission ID for: ${m.title}');
          }
          ids.add(m.id);
          if (notificationIds.contains(m.notificationId) ||
              m.notificationId <= 0) {
            m = m.copyWith(notificationId: Random().nextInt(100000) + 1000);
            changes.add('Fixed notification ID for: ${m.title}');
          }
          notificationIds.add(m.notificationId);
        }
        summary = 'Sandboxed unique ID repair complete.';
      } else if (issueKey == 'invalid_subtask_mastery_value' ||
          issueKey == 'negative_counter_subtask_count' ||
          issueKey == 'negative_counter_subtask_requiredCompletions' ||
          issueKey == 'negative_completion_subtask_completions' ||
          issueKey == 'negative_completion_subtask_requiredCompletions') {
        for (var m in sandbox['missions']) {
          for (var i = 0; i < m.subtasks.length; i++) {
            var s = m.subtasks[i];
            if (s.masteryValue <= 0) {
              m.subtasks[i] = s.copyWith(masteryValue: 1.0);
              changes.add(
                'Fixed mastery value for subtask ${s.name} in ${m.title}',
              );
            }
            if (s.isCounterBased && s.currentCount < 0) {
              m.subtasks[i] = s.copyWith(currentCount: 0);
              changes.add(
                'Fixed negative count for subtask ${s.name} in ${m.title}',
              );
            }
            if (!s.isCounterBased && s.currentCompletions < 0) {
              m.subtasks[i] = s.copyWith(currentCompletions: 0);
              changes.add(
                'Fixed negative completions for subtask ${s.name} in ${m.title}',
              );
            }
          }
        }
        summary = 'Sandboxed subtask value repair complete.';
      } else if (issueKey == 'empty_subtask_name' ||
          issueKey == 'empty_mission_title') {
        for (var m in sandbox['missions']) {
          if (m.title.trim().isEmpty) {
            m = m.copyWith(title: 'Mission ${m.id}');
            changes.add('Filled empty mission title for: ${m.id}');
          }
          for (var i = 0; i < m.subtasks.length; i++) {
            var s = m.subtasks[i];
            if (s.name.trim().isEmpty) {
              m.subtasks[i] = s.copyWith(name: 'Subtask');
              changes.add('Filled empty subtask name in ${m.title}');
            }
          }
        }
        summary = 'Sandboxed name/title repair complete.';
      } else if (issueKey == 'completed_and_failed_mission') {
        for (var m in sandbox['missions']) {
          if (m.isCompleted && m.hasFailed) {
            m = m.copyWith(hasFailed: false);
            changes.add('Fixed completed+failed state for: ${m.title}');
          }
        }
        summary = 'Sandboxed mission state repair complete.';
      } else {
        summary = 'Sandboxed generic repair complete.';
      }

      // Run built-in health checks on sandbox
      for (var m in sandbox['missions']) {
        if (m.id == null || m.id.isEmpty) {
          testResults.add('Mission with missing ID: ${m.title}');
          success = false;
        }
        if (m.notificationId == null || m.notificationId <= 0) {
          testResults.add('Mission with invalid notification ID: ${m.title}');
          success = false;
        }
        if (m.title.trim().isEmpty) {
          testResults.add('Mission with empty title: ${m.id}');
          success = false;
        }
        if (m.isCompleted && m.hasFailed) {
          testResults.add('Mission both completed and failed: ${m.title}');
          success = false;
        }
        for (var s in m.subtasks) {
          if (s.masteryValue <= 0) {
            testResults.add('Subtask with invalid mastery value: ${s.name}');
            success = false;
          }
          if (s.isCounterBased && s.currentCount < 0) {
            testResults.add(
              'Counter-based subtask with negative count: ${s.name}',
            );
            success = false;
          }
          if (!s.isCounterBased && s.currentCompletions < 0) {
            testResults.add(
              'Completion-based subtask with negative completions: ${s.name}',
            );
            success = false;
          }
        }
      }
      // Custom test: check for duplicate IDs
      final idSet = <String>{};
      for (var m in sandbox['missions']) {
        if (idSet.contains(m.id)) {
          testResults.add('Duplicate mission ID: ${m.id}');
          success = false;
        }
        idSet.add(m.id);
      }
      // Add more custom tests as needed
    } catch (e) {
      summary = 'Sandbox test failed: $e';
      success = false;
      testResults.add('Exception: $e');
    }
    _lastSandboxResult = MechanicumSandboxResult(
      success: success,
      summary: summary,
      changes: changes,
      testResults: testResults,
      sandboxState: sandbox,
    );
    _lastSandboxState = sandbox;
    return _lastSandboxResult!;
  }

  /// Apply the last sandboxed suggestion to the real app state if approved
  Future<void> applySandboxedSuggestion() async {
    if (_lastSandboxResult == null || _lastSandboxState == null) return;
    // Overwrite real state with sandboxed state
    final sandbox = _lastSandboxState!;
    _missions = List<MissionData>.from(sandbox['missions']);
    _completedMissions = List<MissionData>.from(sandbox['completedMissions']);
    _deletedMissions = List<MissionData>.from(sandbox['deletedMissions']);
    await _saveMissions(_missions);
    await _saveData();
    notifyListeners();
    // Clear sandbox
    _lastSandboxResult = null;
    _lastSandboxState = null;
  }

  // Mechanicum improvement strategies
  final List<Map<String, dynamic>> _improvementStrategies = [
    {
      'name': 'Enforce Unique IDs',
      'description': 'Ensures all missions and notifications have unique IDs.',
      'apply':
          (MissionProvider provider) async =>
              await provider.forceComprehensiveRepair(),
    },
    {
      'name': 'Fix Subtask Values',
      'description': 'Repairs invalid or negative subtask values.',
      'apply':
          (MissionProvider provider) async =>
              await provider.forceComprehensiveRepair(),
    },
    {
      'name': 'Fill Missing Names/Titles',
      'description': 'Fills in empty mission titles and subtask names.',
      'apply':
          (MissionProvider provider) async =>
              await provider.forceComprehensiveRepair(),
    },
    {
      'name': 'Fix Mission State',
      'description': 'Repairs missions that are both completed and failed.',
      'apply':
          (MissionProvider provider) async =>
              await provider.forceComprehensiveRepair(),
    },
  ];

  // User-uploaded code memory
  List<Map<String, dynamic>> _appImprovementCode = [];
  List<Map<String, dynamic>> _mechanicumKnowledgeBase = [];

  Future<void> _saveKnowledge() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      'mechanicum_app_improvement_code',
      jsonEncode(_appImprovementCode),
    );
    await prefs.setString(
      'mechanicum_knowledge_base',
      jsonEncode(_mechanicumKnowledgeBase),
    );
  }

  Future<void> _loadKnowledge() async {
    final prefs = await SharedPreferences.getInstance();
    final improvementJson = prefs.getString('mechanicum_app_improvement_code');
    if (improvementJson != null) {
      _appImprovementCode = List<Map<String, dynamic>>.from(
        jsonDecode(
          improvementJson,
        ).map((item) => Map<String, dynamic>.from(item)),
      );
    }
    final knowledgeJson = prefs.getString('mechanicum_knowledge_base');
    if (knowledgeJson != null) {
      _mechanicumKnowledgeBase = List<Map<String, dynamic>>.from(
        jsonDecode(
          knowledgeJson,
        ).map((item) => Map<String, dynamic>.from(item)),
      );
    }
    notifyListeners();
  }

  /// Advanced search for Mechanicum to query its knowledge base.
  List<Map<String, dynamic>> searchKnowledgeBase(String query) {
    final lowerCaseQuery = query.toLowerCase();
    if (lowerCaseQuery.isEmpty) return [];

    final allKnowledge = [..._appImprovementCode, ..._mechanicumKnowledgeBase];
    final results = <Map<String, dynamic>>[];

    for (final entry in allKnowledge) {
      final subject = (entry['subject'] as String? ?? '').toLowerCase();
      final description = (entry['description'] as String? ?? '').toLowerCase();
      final tags =
          (entry['tags'] as List<dynamic>? ?? [])
              .map((t) => t.toString().toLowerCase())
              .toList();

      if (subject.contains(lowerCaseQuery) ||
          description.contains(lowerCaseQuery) ||
          tags.any((tag) => tag.contains(lowerCaseQuery))) {
        results.add(entry);
      }
    }
    return results;
  }

  List<Map<String, dynamic>> get appImprovementCode =>
      List.unmodifiable(_appImprovementCode);
  List<Map<String, dynamic>> get mechanicumKnowledgeBase =>
      List.unmodifiable(_mechanicumKnowledgeBase);
  List<Map<String, dynamic>> get improvementStrategies =>
      List.unmodifiable(_improvementStrategies);
  Map<String, int> get issueFrequency => Map.unmodifiable(_issueFrequency);

  /// Public method to force Mechanicum to be more active
  Future<void> activateMechanicum() async {
    print('Mechanicum: Force activation requested...');

    // Make Mechanicum visible immediately
    mechanicum.setAIActive(true);

    // Make Mechanicum more active by triggering immediate health check
    await mechanicum.performImmediateHealthCheck(() async {
      await _validateAndRepairAllIssues();
    });

    // Also trigger a comprehensive repair to ensure everything is working
    await forceComprehensiveRepair();

    // Keep Mechanicum active for a longer period to show it's working
    await Future.delayed(const Duration(seconds: 5));
    mechanicum.setAIActive(false);

    print('Mechanicum: Force activation completed');
  }

  /// Public method to perform comprehensive cleanup of all missions
  Future<void> performComprehensiveCleanup() async {
    // Implement comprehensive cleanup logic
    print('Performing comprehensive cleanup...');
    // Add any additional cleanup logic you want to execute
  }

  // --- User Code AI Analysis Fields ---
  List<Map<String, dynamic>> _userCodeAnalysis = [];
  List<Map<String, dynamic>> _userCodeTestResults = [];
  Map<String, List<String>> _userCodeKnowledgeGraph = {};
  List<String> _userCodeSuggestions = [];
  Map<String, dynamic> _userCodePatternStats = {};

  List<Map<String, dynamic>> get userCodeAnalysis =>
      List.unmodifiable(_userCodeAnalysis);
  List<Map<String, dynamic>> get userCodeTestResults =>
      List.unmodifiable(_userCodeTestResults);
  Map<String, List<String>> get userCodeKnowledgeGraph =>
      Map.unmodifiable(_userCodeKnowledgeGraph);
  List<String> get userCodeSuggestions =>
      List.unmodifiable(_userCodeSuggestions);
  Map<String, dynamic> get userCodePatternStats =>
      Map.unmodifiable(_userCodePatternStats);

  // --- Enhanced uploadCode/ingestCode ---
  void uploadCode({
    required String type,
    required String subject,
    required String description,
    required String code,
    required List<String> tags,
  }) {
    final entry = {
      'subject': subject,
      'description': description,
      'code': code,
      'tags': tags,
    };
    if (type == 'app_improvement') {
      _appImprovementCode.add(entry);
    } else {
      _mechanicumKnowledgeBase.add(entry);
    }
    // --- AI-powered analysis for all uploaded code ---
    _analyzeAndTestUserCode(code);
    _saveKnowledge();
    notifyListeners();
  }

  void ingestCode(String code, {required bool isUserUpload}) {
    // For legacy upload, treat as user upload
    _analyzeAndTestUserCode(code);
    notifyListeners();
  }

  void _analyzeAndTestUserCode(String code) {
    // 1. Static code analysis (function/class parsing, edge case detection)
    final analysis = _parseDartCodeStructure(code);
    _userCodeAnalysis.add(analysis);

    // 2. Dynamic test generation (unit, integration, mutation, property-based, fuzzing)
    final tests = _generateTestsForCode(analysis);
    _userCodeTestResults.addAll(tests);

    // 3. Knowledge graph update
    _updateUserCodeKnowledgeGraph(analysis);

    // 4. Pattern recognition/adaptive strategies (stub)
    _updateUserCodePatternStats();

    // 5. Proactive suggestions
    _userCodeSuggestions = _generateUserCodeSuggestions();
  }

  Map<String, dynamic> _parseDartCodeStructure(String code) {
    // Use analyzer to parse code (stub: fallback to regex if analyzer not available)
    try {
      final result = parseString(content: code);
      final unit = result.unit;
      final functions = <String>[];
      final classes = <String>[];
      final dependencies = <String>[];
      unit.declarations.forEach((decl) {
        if (decl is FunctionDeclaration) {
          functions.add(decl.name.lexeme);
        } else if (decl is ClassDeclaration) {
          classes.add(decl.name.lexeme);
          for (final member in decl.members) {
            if (member is MethodDeclaration) {
              functions.add('${decl.name.lexeme}.${member.name.lexeme}');
            }
          }
        }
      });
      // Find imports (dependencies)
      for (final directive in unit.directives) {
        if (directive is ImportDirective) {
          dependencies.add(directive.uri.stringValue ?? '');
        }
      }
      // Edge case detection (stub: just note nulls, boundaries)
      final edgeCases = [
        'null',
        'empty',
        'boundary',
        'negative',
        'large',
        'zero',
      ];
      return {
        'functions': functions,
        'classes': classes,
        'dependencies': dependencies,
        'edgeCases': edgeCases,
        'raw': code,
      };
    } catch (e) {
      // Fallback: just store code
      return {
        'functions': [],
        'classes': [],
        'dependencies': [],
        'edgeCases': [],
        'raw': code,
        'error': e.toString(),
      };
    }
  }

  List<Map<String, dynamic>> _generateTestsForCode(
    Map<String, dynamic> analysis,
  ) {
    // Stub: generate mock tests for each function/class
    final tests = <Map<String, dynamic>>[];
    final rand = Random();
    for (final fn in analysis['functions'] ?? []) {
      // Unit test
      tests.add({
        'type': 'unit',
        'target': fn,
        'input': 'edge cases',
        'result': rand.nextBool() ? 'pass' : 'fail',
        'reasoning': 'Covers edge cases for $fn',
      });
      // Mutation test
      tests.add({
        'type': 'mutation',
        'target': fn,
        'input': 'mutated input',
        'result': rand.nextBool() ? 'pass' : 'fail',
        'reasoning': 'Checks if $fn is robust to mutation',
      });
      // Property-based test
      tests.add({
        'type': 'property',
        'target': fn,
        'input': 'randomized',
        'result': rand.nextBool() ? 'pass' : 'fail',
        'reasoning': 'Property-based test for $fn',
      });
      // Fuzzing test
      tests.add({
        'type': 'fuzz',
        'target': fn,
        'input': 'fuzzed',
        'result': rand.nextBool() ? 'pass' : 'fail',
        'reasoning': 'Fuzzing test for $fn',
      });
    }
    // Integration test for classes
    for (final cls in analysis['classes'] ?? []) {
      tests.add({
        'type': 'integration',
        'target': cls,
        'input': 'integration scenario',
        'result': rand.nextBool() ? 'pass' : 'fail',
        'reasoning': 'Integration test for $cls',
      });
    }
    return tests;
  }

  void _updateUserCodeKnowledgeGraph(Map<String, dynamic> analysis) {
    // Build a simple graph: class/function -> dependencies
    for (final fn in analysis['functions'] ?? []) {
      _userCodeKnowledgeGraph[fn] = List<String>.from(
        analysis['dependencies'] ?? [],
      );
    }
    for (final cls in analysis['classes'] ?? []) {
      _userCodeKnowledgeGraph[cls] = List<String>.from(
        analysis['dependencies'] ?? [],
      );
    }
  }

  void _updateUserCodePatternStats() {
    // Stub: count test types and pass/fail
    final stats = <String, int>{};
    for (final test in _userCodeTestResults) {
      final type = test['type'] ?? 'unknown';
      final result = test['result'] ?? 'unknown';
      stats['${type}_$result'] = (stats['${type}_$result'] ?? 0) + 1;
    }
    _userCodePatternStats = stats;
  }

  List<String> _generateUserCodeSuggestions() {
    // Suggest uploading code for functions/classes with no tests or failed tests
    final suggestions = <String>[];
    final tested = _userCodeTestResults.map((t) => t['target']).toSet();
    for (final analysis in _userCodeAnalysis) {
      for (final fn in analysis['functions'] ?? []) {
        if (!tested.contains(fn)) {
          suggestions.add('Upload more code/tests for function $fn');
        }
      }
      for (final cls in analysis['classes'] ?? []) {
        if (!tested.contains(cls)) {
          suggestions.add('Upload more code/tests for class $cls');
        }
      }
    }
    // Suggest for failed tests
    for (final test in _userCodeTestResults) {
      if (test['result'] == 'fail') {
        suggestions.add(
          'Improve code or tests for ${test['target']} (failed ${test['type']} test)',
        );
      }
    }
    return suggestions.toSet().toList();
  }

  // --- Periodic AI Sandbox for All App/User Code ---
  bool _isSandboxWorking = false;
  bool get isSandboxWorking => _isSandboxWorking;

  set isSandboxWorking(bool value) {
    print('isSandboxWorking set to: $value');
    _isSandboxWorking = value;
    notifyListeners();
  }

  Timer? _sandboxTimer;
  Duration sandboxInterval = const Duration(seconds: 30); // Reduced frequency
  IO.Socket? _sandboxSocket;

  void startAISandbox() {
    print('🧪 AI Sandbox: Starting with backend integration...');
    _connectToBackend();

    // Reduced frequency timer for local health checks only
    _sandboxTimer?.cancel();
    _sandboxTimer = Timer.periodic(sandboxInterval, (_) async {
      print('🧪 AI Sandbox: Timer tick - running local health check');
      await _runLocalHealthCheck();
    });

    // Run initial health check
    _runLocalHealthCheck();
  }

  void _connectToBackend() {
    print('[SANDBOX] Connecting to backend Socket.IO...');
    _sandboxSocket = IO.io('http://234.55.93.144:4000', <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
    });

    _sandboxSocket!.onConnect((_) {
      print('[SANDBOX] ✅ Connected to backend Socket.IO');
      isSandboxWorking = true;
      notifyListeners();
    });

    _sandboxSocket!.onDisconnect((_) {
      print('[SANDBOX] ❌ Disconnected from backend Socket.IO');
      isSandboxWorking = false;
      notifyListeners();
    });

    // Listen to backend Sandbox events
    _sandboxSocket!.on('ai:experiment-start', (data) {
      final ai = data['ai'] ?? 'Unknown AI';
      if (ai == 'Sandbox') {
        print('[SANDBOX] 📨 Backend Sandbox started experiment');
        isSandboxWorking = true;
        notifyListeners();
      }
    });

    _sandboxSocket!.on('ai:experiment-complete', (data) {
      final ai = data['ai'] ?? 'Unknown AI';
      if (ai == 'Sandbox') {
        print('[SANDBOX] 📨 Backend Sandbox completed experiment');
        isSandboxWorking = false;
        notifyListeners();
      }
    });

    _sandboxSocket!.on('proposal:created', (data) {
      final aiType = data['aiType'] ?? 'Unknown AI';
      if (aiType == 'Sandbox') {
        print('[SANDBOX] 📨 Backend Sandbox created proposal');
        // Update local state to reflect backend activity
        _updateLocalStateFromBackend(data);
      }
    });

    _sandboxSocket!.connect();
  }

  void _updateLocalStateFromBackend(Map<String, dynamic> data) {
    final filePath = data['filePath'] ?? 'unknown file';
    final aiType = data['aiType'] ?? 'Unknown AI';

    // Add to AI suggestions to reflect backend activity
    _aiGeneratedCodeSuggestions.add({
      'title': 'Backend ${aiType} Proposal',
      'description': 'Proposal created by backend $aiType for $filePath',
      'targetFile': filePath,
      'code': '// Backend proposal for $filePath',
      'isExtension': false,
      'userConfirmed': false,
      'timestamp': DateTime.now().toIso8601String(),
    });

    notifyListeners();
  }

  Future<void> _runLocalHealthCheck() async {
    if (_isSandboxRunning) {
      print("🧪 AI Sandbox: Local health check already in progress. Skipping.");
      return;
    }

    _isSandboxRunning = true;
    print("🧪 AI Sandbox: Running local health check...");

    try {
      // Simple local health check - just verify connectivity and basic functionality
      final isConnected = _sandboxSocket?.connected ?? false;
      print("🧪 AI Sandbox: Backend connection status: $isConnected");

      if (!isConnected) {
        print("🧪 AI Sandbox: Attempting to reconnect to backend...");
        _sandboxSocket?.connect();
      }

      // Update test feed with connection status
      print(
        '🧪 AI Sandbox: Local health check completed. Backend connected: $isConnected',
      );
    } catch (e) {
      print('🧪 AI Sandbox: Error during local health check: $e');
      print('🧪 AI Sandbox: Local health check failed: $e');
    } finally {
      _isSandboxRunning = false;
      notifyListeners();
    }
  }

  void stopAISandbox() {
    _sandboxTimer?.cancel();
    _sandboxSocket?.disconnect();
    _sandboxSocket?.dispose();
    _sandboxSocket = null;
    isSandboxWorking = false;
    print('AI Sandbox: Stopped');
  }

  // --- AI-Generated Code Suggestions, Extension Ideas, Personalized Suggestions ---
  List<Map<String, dynamic>> _aiGeneratedCodeSuggestions = [];
  List<Map<String, dynamic>> _aiExtensionIdeas = [];
  List<Map<String, dynamic>> _aiPersonalizedSuggestions = [];

  List<Map<String, dynamic>> get aiGeneratedCodeSuggestions =>
      List.unmodifiable(_aiGeneratedCodeSuggestions);
  List<Map<String, dynamic>> get aiExtensionIdeas =>
      List.unmodifiable(_aiExtensionIdeas);
  List<Map<String, dynamic>> get aiPersonalizedSuggestions =>
      List.unmodifiable(_aiPersonalizedSuggestions);

  // --- Feedback tracking for AI suggestions ---
  Map<String, String> _aiSuggestionFeedback =
      {}; // {suggestionId: 'accepted'|'ignored'|'applied'}
  List<Map<String, dynamic>> _appliedAISuggestions = [];

  Map<String, String> get aiSuggestionFeedback =>
      Map.unmodifiable(_aiSuggestionFeedback);
  List<Map<String, dynamic>> get appliedAISuggestions =>
      List.unmodifiable(_appliedAISuggestions);

  void acceptAISuggestion(String id) {
    _aiSuggestionFeedback[id] = 'accepted';
    notifyListeners();
  }

  void ignoreAISuggestion(String id) {
    _aiSuggestionFeedback[id] = 'ignored';
    notifyListeners();
  }

  void applyAISuggestion(String id) {
    final suggestion = _aiGeneratedCodeSuggestions.firstWhere(
      (s) => s['title'] == id,
      orElse: () => {},
    );
    if (suggestion.isNotEmpty) {
      // Prevent re-applying the same suggestion
      if (_appliedAISuggestions.any((s) => s['title'] == id)) {
        print('🧪 AI Sandbox: Suggestion "$id" already applied, skipping.');
        return;
      }
      // Only allow files in lib/, assets/gif/, or assets/images/
      final targetFile = suggestion['targetFile']?.toString();
      if (targetFile == null ||
          !(targetFile.startsWith('lib/') ||
              targetFile.startsWith('assets/gif/') ||
              targetFile.startsWith('assets/images/'))) {
        print(
          '🧪 AI Sandbox: Target file $targetFile is not allowed. Only files in /lib or /assets are permitted.',
        );
        return;
      }
      print('🧪 AI Sandbox: Target file for modification: $targetFile');
      // If new extension/tool, create new Dart file in lib/extensions/
      if (suggestion['isExtension'] == true) {
        final extPath =
            'lib/extensions/ai_extension_${DateTime.now().millisecondsSinceEpoch}.dart';
        final file = File(extPath);
        file.writeAsStringSync(suggestion['code'] ?? '// AI extension');
        print('🧪 AI Sandbox: New extension created at $extPath');
        _appliedAISuggestions.add({
          ...suggestion,
          'appliedAt': DateTime.now().toIso8601String(),
          'appliedTo': extPath,
        });
        notifyListeners();
        return;
      }
      // Confirm with user (UI already does this, but double-check)
      if (suggestion['userConfirmed'] != true) {
        print('🧪 AI Sandbox: User confirmation required for $id.');
        return;
      }
      _aiSuggestionFeedback[id] = 'applied';
      _appliedAISuggestions.add(suggestion);
      print('🧪 AI Sandbox: Applied code: ${suggestion['code']}');
      final code = suggestion['code']?.toString().trim();
      final targetSymbol = suggestion['targetSymbol']?.toString();
      try {
        final file = File(targetFile);
        if (!file.existsSync()) {
          print('Target file $targetFile does not exist.');
          return;
        }
        // Backup
        final backupPath = targetFile + '.bak';
        file.copySync(backupPath);
        print('Backup created at $backupPath');
        // Read file
        final content = file.readAsStringSync();
        // Regex for function or class (simple, not perfect)
        final functionRegex = RegExp(
          r'(\n|^)([\w<>\s]*?)' +
              targetSymbol! +
              r'\s*\([^)]*\)\s*\{[\s\S]*?^\}',
          multiLine: true,
        );
        final classRegex = RegExp(
          r'(\n|^)class\s+' + targetSymbol + r'\s*\{[\s\S]*?^\}',
          multiLine: true,
        );
        String? newContent;
        if (functionRegex.hasMatch(content)) {
          newContent = content.replaceFirst(functionRegex, '\n' + code! + '\n');
          print('Function $targetSymbol replaced in $targetFile');
        } else if (classRegex.hasMatch(content)) {
          newContent = content.replaceFirst(classRegex, '\n' + code! + '\n');
          print('Class $targetSymbol replaced in $targetFile');
        } else {
          print('Symbol $targetSymbol not found in $targetFile.');
          return;
        }
        file.writeAsStringSync(newContent);
        print('File $targetFile updated successfully.');
        AIFileSystemHelper.logFileAction(
          'AI Sandbox',
          'write',
          targetFile,
          details: 'Suggestion $id applied',
        );
      } catch (e) {
        print('Error applying suggestion: $e');
        // Restore from backup
        if (targetFile != null) {
          final backupPath = targetFile + '.bak';
          if (File(backupPath).existsSync()) {
            File(backupPath).copySync(targetFile);
            print('Restored $targetFile from backup.');
          }
        }
      }
      notifyListeners();
      if (code != null && code.isNotEmpty) {
        TheImperium.instance.learnFromExternalCode(
          source: 'AI Suggestion',
          code: code,
          description: 'AI suggestion applied to app.',
        );
        print('🏆 The Imperium: Notified of AI suggestion application.');
      }
    }
  }

  // --- Stub for real backend integration ---
  Future<void> saveMissions(List<MissionData> missions) async {
    await _saveMissions(missions);
  }

  final List<Map<String, dynamic>> _aiLearningLog = [];
  final StreamController<Map<String, dynamic>> _aiLearningLogController =
      StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get aiLearningLogStream =>
      _aiLearningLogController.stream;

  void applyAISuggestionFromImperium(String suggestion, String code) {}

  // Track if the AI sandbox is currently running
  bool _isSandboxRunning = false;
}
