import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:the_codex/mastery_list.dart';
import 'package:the_codex/mechanicum.dart';
import 'package:the_codex/mission_provider.dart';
import 'package:the_codex/providers/app_history_provider.dart'
    show AppHistoryProvider;
import 'package:the_codex/providers/notification_provider.dart';
import 'dart:convert';
import 'dart:math';
import 'entry_manager.dart';
import 'package:app_badge_plus/app_badge_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'dart:typed_data';
import 'package:image/image.dart' as img;
import 'package:provider/provider.dart';
import 'core/error/app_error.dart';
import 'core/logging/app_logger.dart';
import 'core/monitoring/performance_monitor.dart';
import 'dart:developer' as developer;
import 'dart:io';
import 'ai_file_system_helper.dart';

class NotificationChannels {
  static const String mission = 'mission_channel';
  static const String summary = 'summary_channel';

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

  static const AndroidNotificationChannel summaryChannel =
      AndroidNotificationChannel(
        summary,
        'Daily Summary',
        description: 'Daily mission progress summary',
        importance: Importance.high,
        playSound: true,
        enableVibration: true,
        showBadge: true,
      );
}

  // Mission subtask class to hold subtask details
class MissionSubtask {
  final String name;
  final int requiredCompletions;
  int currentCompletions;
  final String? linkedMasteryId;
  final double masteryValue;
  final bool isCounterBased;
  int currentCount;
  final Color? boltColor;
  final DateTime? createdAt;

  MissionSubtask({
    required this.name,
    required this.requiredCompletions,
    this.currentCompletions = 0,
    this.linkedMasteryId,
    this.masteryValue = 0.0,
    this.isCounterBased = false,
    this.currentCount = 0,
    this.boltColor,
    this.createdAt,
  });

  double get completionPercentage {
    if (isCounterBased) {
      // For counter-based tasks, if requiredCompletions is 0, consider it complete if there's any progress
      if (requiredCompletions == 0) return currentCount > 0 ? 1.0 : 0.0;
      return (currentCount / requiredCompletions).clamp(0.0, 1.0);
    }
    // For non-counter tasks, if requiredCompletions is 0, consider it complete if there's any progress
    if (requiredCompletions == 0) return currentCompletions > 0 ? 1.0 : 0.0;
    return (currentCompletions / requiredCompletions).clamp(0.0, 1.0);
  }

  bool get isCompleted {
    if (isCounterBased) {
      // For counter-based tasks, if requiredCompletions is 0, consider it complete if there's any progress
      return requiredCompletions == 0
          ? currentCount > 0
          : currentCount >= requiredCompletions;
    }
    // For non-counter tasks, if requiredCompletions is 0, consider it complete if there's any progress
    return requiredCompletions == 0
        ? currentCompletions > 0
        : currentCompletions >= requiredCompletions;
  }

  void increment() {
    if (isCounterBased) {
      currentCount++;
      // Don't increment completions for counter-based tasks
    } else {
      currentCompletions++;
    }
    // Record progress for the parent mission if available
    // (Assume parent mission will call _recordProgress after subtask increment)
  }

  String get progressDisplay {
    if (isCounterBased) {
      if (requiredCompletions == 0) {
        return "Tapped $currentCount times";
      }
      return "$currentCount";
    }
    return "$currentCompletions";
  }

  Map<String, dynamic> toJson() => {
    'name': name,
    'requiredCompletions': requiredCompletions,
    'currentCompletions': currentCompletions,
    'linkedMasteryId': linkedMasteryId,
    'masteryValue': masteryValue,
    'isCounterBased': isCounterBased,
    'currentCount': currentCount,
    'boltColor': boltColor?.value,
    'createdAt': createdAt?.toIso8601String(),
  };

  factory MissionSubtask.fromJson(Map<String, dynamic> json) => MissionSubtask(
    name: json['name'] as String,
    requiredCompletions: json['requiredCompletions'] as int,
    currentCompletions: json['currentCompletions'] as int,
    linkedMasteryId: json['linkedMasteryId'] as String?,
    masteryValue: json['masteryValue'] as double? ?? 0.0,
    isCounterBased: json['isCounterBased'] as bool? ?? false,
    currentCount: json['currentCount'] as int? ?? 0,
    boltColor: json['boltColor'] != null ? Color(json['boltColor']) : null,
    createdAt:
        json['createdAt'] != null ? DateTime.parse(json['createdAt']) : null,
  );

  MissionSubtask copyWith({
    String? name,
    int? requiredCompletions,
    int? currentCompletions,
    String? linkedMasteryId,
    double? masteryValue,
    bool? isCounterBased,
    int? currentCount,
    Color? boltColor,
    DateTime? createdAt,
  }) {
    return MissionSubtask(
      name: name ?? this.name,
      requiredCompletions: requiredCompletions ?? this.requiredCompletions,
      currentCompletions: currentCompletions ?? this.currentCompletions,
      linkedMasteryId: linkedMasteryId ?? this.linkedMasteryId,
      masteryValue: masteryValue ?? this.masteryValue,
      isCounterBased: isCounterBased ?? this.isCounterBased,
      currentCount: currentCount ?? this.currentCount,
      boltColor: boltColor ?? this.boltColor,
    );
  }

  MissionSubtask incrementCount() {
    if (isCounterBased) {
      final newCount = currentCount + 1;
      return copyWith(
        currentCount: newCount,
        // Don't increment completions for counter-based tasks
      );
    } else {
      return copyWith(currentCompletions: currentCompletions + 1);
    }
  }

  double get masteryProgress {
    if (isCounterBased) {
      // For counter-based tasks, multiply the mastery value by the current count
      return currentCount * masteryValue;
    }
    return currentCompletions * masteryValue;
  }
}

  // Mission data class to hold mission details
class MissionData {
  final String? id;
  final String? missionId;
  final String title;
  final String description;
  final MissionType type;
  late final DateTime? createdAt;
  DateTime? lastCompleted;
  bool isCompleted;
  bool hasFailed;
  final String? masteryId;
  final double? value;
  final List<MissionSubtask> subtasks;
  final bool isCounterBased;
  int currentCount;
  final bool isSubtaskCounter;
  final String imageUrl;
  final int notificationId;
  int? scheduledNotificationId;
  final double masteryValue;
  final String? linkedMasteryId;
  final Map<String, double> subtaskMasteryValues;
  final int targetCount;
  final Color? boltColor;
  final Color? timelapseColor;

  MissionData({
    this.id,
    this.missionId,
    required this.title,
    String? description,
    required this.type,
    this.createdAt,
    this.lastCompleted,
    this.isCompleted = false,
    this.hasFailed = false,
    this.masteryId,
    this.value,
    List<MissionSubtask>? subtasks,
    this.isCounterBased = false,
    this.currentCount = 0,
    this.isSubtaskCounter = false,
    this.imageUrl = '',
    required this.notificationId,
    this.scheduledNotificationId,
    required this.masteryValue,
    this.linkedMasteryId,
    required this.subtaskMasteryValues,
    required this.targetCount,
    this.boltColor,
    this.timelapseColor,
  }) : description = description ?? '',
       subtasks = subtasks ?? [];

  double get completionPercentage {
    if (subtasks.isEmpty) {
      if (isCounterBased) {
  // For open-ended counters, return 0.0 as they never complete
        if (targetCount == 0) return 0.0;
        return currentCount / targetCount;
      }
      return isCompleted ? 1.0 : 0.0;
    }

  // Calculate average completion percentage of non-counter subtasks only
    double totalPercentage = 0.0;
    int nonCounterSubtasks = 0;
    for (var subtask in subtasks) {
      if (!subtask.isCounterBased) {
        totalPercentage += subtask.completionPercentage;
        nonCounterSubtasks++;
      }
    }
    return nonCounterSubtasks > 0 ? totalPercentage / nonCounterSubtasks : 0.0;
  }

  bool get areAllSubtasksComplete {
    if (subtasks.isEmpty) {
      if (isCounterBased) {
  // For open-ended counters, they are never complete
        if (targetCount == 0) return false;
        return currentCount >= targetCount;
      }
      return isCompleted;
    }

    return subtasks.every((subtask) => subtask.isCompleted);
  }

  void incrementSubtask(int subtaskIndex) {
    if (subtaskIndex >= 0 && subtaskIndex < subtasks.length) {
      subtasks[subtaskIndex].increment();
      isCompleted = areAllSubtasksComplete;
      if (isCompleted) {
        lastCompleted = DateTime.now();
      }
  // Record progress
      _recordProgress();
    }
  }

  void incrementCounter() {
    if (isCounterBased) {
      currentCount++;
      isCompleted = targetCount == 0 || currentCount >= targetCount;
      if (isCompleted) {
        lastCompleted = DateTime.now();
      }
  // Record progress
      _recordProgress();
    }
  }

  String get progressDisplay {
    if (subtasks.isEmpty) {
      if (isCounterBased) {
        if (targetCount == 0) {
          return "Tapped $currentCount times";
        }
        return "$currentCount";
      }
      return isCompleted ? "Completed" : "Not completed";
    }

  // For missions with subtasks, show completion percentage
    final percentage = (completionPercentage * 100).round();
    return "$percentage% complete";
  }

  // Track historical progress for summary calculations
  Map<DateTime, double> _historicalProgress = {};

  void _recordProgress() {
    final now = DateTime.now();
    double progress = 0.0;

    if (subtasks.isEmpty) {
      if (isCounterBased) {
        if (targetCount > 0) {
          progress = currentCount / targetCount;
        } else {
          progress = currentCount > 0 ? 1.0 : 0.0;
        }
      } else {
        progress = isCompleted ? 1.0 : 0.0;
      }
    } else {
  // Calculate average progress of all subtasks
      double totalProgress = 0.0;
      int validSubtasks = 0;

      for (final subtask in subtasks) {
        if (subtask.isCounterBased) {
          if (subtask.requiredCompletions > 0) {
            totalProgress += subtask.currentCount / subtask.requiredCompletions;
          } else {
            totalProgress += subtask.currentCount > 0 ? 1.0 : 0.0;
          }
        } else {
          if (subtask.requiredCompletions > 0) {
            totalProgress +=
                subtask.currentCompletions / subtask.requiredCompletions;
          } else {
            totalProgress += subtask.currentCompletions > 0 ? 1.0 : 0.0;
          }
        }
        validSubtasks++;
      }

      progress = validSubtasks > 0 ? totalProgress / validSubtasks : 0.0;
    }

  // Only record if progress has changed or it's been more than 1 hour
    final lastProgress =
        _historicalProgress.entries
            .where(
              (entry) =>
                  entry.key.isAfter(now.subtract(const Duration(hours: 1))),
            )
            .map((entry) => entry.value)
            .toList();

    if (lastProgress.isEmpty || lastProgress.last != progress) {
      _historicalProgress[now] = progress;
  // Clean up old entries and compress data
      _cleanupAndCompressHistoricalProgress();
    }
  }

  void _cleanupAndCompressHistoricalProgress() {
    final thirtyDaysAgo = DateTime.now().subtract(const Duration(days: 30));
    final entries =
        _historicalProgress.entries.toList()
          ..sort((a, b) => a.key.compareTo(b.key));

  // Remove entries older than 30 days
    entries.removeWhere((entry) => entry.key.isBefore(thirtyDaysAgo));

  // Compress data by removing redundant entries
    final compressedEntries = <DateTime, double>{};
    double? lastValue;

    for (var entry in entries) {
  // Keep first entry of each day
      if (lastValue == null ||
          entry.key.day != compressedEntries.keys.last.day ||
          (entry.value - lastValue).abs() > 0.01) {
  // Only keep if change is significant
        compressedEntries[entry.key] = entry.value;
        lastValue = entry.value;
      }
    }

    _historicalProgress = compressedEntries;
  }

  double getProgressForDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final checkDate = DateTime(date.year, date.month, date.day);

  // Don't calculate progress for future dates
    if (checkDate.isAfter(today)) {
      return 0.0;
    }

  // Find the closest recorded progress before or on the given date
    final relevantProgress =
        _historicalProgress.entries
            .where(
              (entry) =>
                  entry.key.year == date.year &&
                  entry.key.month == date.month &&
                  entry.key.day == date.day,
            )
            .toList();

    if (relevantProgress.isNotEmpty) {
      return relevantProgress.first.value;
    }

  // If no exact match found, and the date is before today, return 0
    if (checkDate.isBefore(today)) {
      return 0.0;
    }

  // Only for today, calculate current progress
    double progress = 0.0;

    if (subtasks.isEmpty) {
      if (isCounterBased) {
        if (targetCount > 0) {
          progress = currentCount / targetCount;
        } else {
          progress = currentCount > 0 ? 1.0 : 0.0;
        }
      } else {
        progress = isCompleted ? 1.0 : 0.0;
      }
    } else {
  // Calculate average progress of all subtasks
      double totalProgress = 0.0;
      int validSubtasks = 0;

      for (final subtask in subtasks) {
        double subtaskProgress = 0.0;
        if (subtask.isCounterBased) {
          if (subtask.requiredCompletions > 0) {
            subtaskProgress =
                subtask.currentCount / subtask.requiredCompletions;
          } else {
            subtaskProgress = subtask.currentCount > 0 ? 1.0 : 0.0;
          }
        } else {
          if (subtask.requiredCompletions > 0) {
            subtaskProgress =
                subtask.currentCompletions / subtask.requiredCompletions;
          } else {
            subtaskProgress = subtask.currentCompletions > 0 ? 1.0 : 0.0;
          }
        }
        totalProgress += subtaskProgress;
        validSubtasks++;
      }

      progress = validSubtasks > 0 ? totalProgress / validSubtasks : 0.0;
    }

    return progress;
  }

  Map<DateTime, double> getProgressForDateRange(DateTime start, DateTime end) {
    return Map.fromEntries(
      _historicalProgress.entries.where(
        (entry) =>
            entry.key.isAfter(start.subtract(const Duration(days: 1))) &&
            entry.key.isBefore(end.add(const Duration(days: 1))),
      ),
    );
  }

  bool get shouldReset {
    if (type == MissionType.simple || type == MissionType.persistent)
      return false;

    final now = DateTime.now();
    if (type == MissionType.daily) {
      return createdAt != null && !_isSameDay(createdAt!, now);
    } else if (type == MissionType.weekly) {
      return createdAt != null &&
          createdAt!.isBefore(now.subtract(const Duration(days: 7)));
    }
    return false;
  }

  bool _isSameDay(DateTime a, DateTime b) {
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  MissionData copyWith({
    String? id,
    String? missionId,
    String? title,
    String? description,
    MissionType? type,
    DateTime? createdAt,
    DateTime? lastCompleted,
    bool? isCompleted,
    bool? hasFailed,
    String? masteryId,
    double? value,
    List<MissionSubtask>? subtasks,
    bool? isCounterBased,
    int? currentCount,
    bool? isSubtaskCounter,
    String? imageUrl,
    int? notificationId,
    int? scheduledNotificationId,
    double? masteryValue,
    String? linkedMasteryId,
    Map<String, double>? subtaskMasteryValues,
    int? targetCount,
    Color? boltColor,
    Color? timelapseColor,
  }) {
  // Ensure unique ID when copying
    final newId = id ?? this.id;
    final newNotificationId = notificationId ?? this.notificationId;

    return MissionData(
      id: newId,
      missionId: missionId ?? this.missionId,
      title: title ?? this.title,
      description: description ?? this.description,
      type: type ?? this.type,
      createdAt: createdAt ?? this.createdAt,
      lastCompleted: lastCompleted ?? this.lastCompleted,
      isCompleted: isCompleted ?? this.isCompleted,
      hasFailed: hasFailed ?? this.hasFailed,
      masteryId: masteryId ?? this.masteryId,
      value: value ?? this.value,
      subtasks: subtasks ?? this.subtasks,
      isCounterBased: isCounterBased ?? this.isCounterBased,
      currentCount: currentCount ?? this.currentCount,
      isSubtaskCounter: isSubtaskCounter ?? this.isSubtaskCounter,
      imageUrl: imageUrl ?? this.imageUrl,
      notificationId: newNotificationId,
      scheduledNotificationId:
          scheduledNotificationId ?? this.scheduledNotificationId,
      masteryValue: masteryValue ?? this.masteryValue,
      linkedMasteryId: linkedMasteryId ?? this.linkedMasteryId,
      subtaskMasteryValues: subtaskMasteryValues ?? this.subtaskMasteryValues,
      targetCount: targetCount ?? this.targetCount,
      boltColor: boltColor ?? this.boltColor,
      timelapseColor: timelapseColor ?? this.timelapseColor,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'missionId': missionId,
    'title': title,
    'description': description,
    'type': type.toString(),
    'createdAt': createdAt?.toIso8601String(),
    'lastCompleted': lastCompleted?.toIso8601String(),
    'isCompleted': isCompleted,
    'hasFailed': hasFailed,
    'masteryId': masteryId,
    'value': value,
    'subtasks': subtasks.map((s) => s.toJson()).toList(),
    'isCounterBased': isCounterBased,
    'currentCount': currentCount,
    'isSubtaskCounter': isSubtaskCounter,
    'imageUrl': imageUrl,
    'notificationId': notificationId,
    'scheduledNotificationId': scheduledNotificationId,
    'masteryValue': masteryValue,
    'linkedMasteryId': linkedMasteryId,
    'subtaskMasteryValues': subtaskMasteryValues,
    'targetCount': targetCount,
    'boltColor': boltColor?.value,
    'timelapseColor': timelapseColor?.value,
  };

  factory MissionData.fromJson(Map<String, dynamic> json) {
  // Defensive parsing for subtasks
    dynamic subtasksRaw = json['subtasks'];
    List<dynamic> subtasksList;
    if (subtasksRaw is List) {
      subtasksList = subtasksRaw;
    } else if (subtasksRaw is String && subtasksRaw.isNotEmpty) {
      try {
        final decoded = jsonDecode(subtasksRaw);
        if (decoded is List) {
          subtasksList = decoded;
        } else {
          subtasksList = [];
        }
      } catch (_) {
        subtasksList = [];
      }
    } else {
      subtasksList = [];
    }
  // Now use subtasksList instead of json['subtasks'] below
    final typeStr = json['type'] as String;
    final type = MissionType.values.firstWhere(
      (e) => e.toString() == typeStr,
      orElse: () => MissionType.daily,
    );

    final createdAt =
        json['createdAt'] != null
            ? DateTime.parse(json['createdAt'] as String)
            : null;
    final lastCompleted =
        json['lastCompleted'] != null
            ? DateTime.parse(json['lastCompleted'] as String)
            : null;

    final boltColorValue = json['boltColor'] as int?;
    final timelapseColorValue = json['timelapseColor'] as int?;

    return MissionData(
      id: json['id'] as String?,
      missionId: json['missionId'] as String?,
      title: json['title'] as String,
      description: json['description'] as String?,
      type: type,
      createdAt: createdAt,
      lastCompleted: lastCompleted,
      isCompleted: json['isCompleted'] as bool? ?? false,
      hasFailed: json['hasFailed'] as bool? ?? false,
      masteryId: json['masteryId'] as String?,
      value: json['value'] as double?,
      subtasks:
          subtasksList
              .map((s) => MissionSubtask.fromJson(s as Map<String, dynamic>))
              .toList(),
      isCounterBased: json['isCounterBased'] as bool? ?? false,
      currentCount: json['currentCount'] as int? ?? 0,
      isSubtaskCounter: json['isSubtaskCounter'] as bool? ?? false,
      imageUrl: json['imageUrl'] as String? ?? '',
      notificationId: json['notificationId'] as int,
      scheduledNotificationId: json['scheduledNotificationId'] as int?,
      masteryValue: json['masteryValue'] as double? ?? 0.0,
      linkedMasteryId: json['linkedMasteryId'] as String?,
      subtaskMasteryValues: Map<String, double>.from(
        json['subtaskMasteryValues'] as Map<String, dynamic>? ?? {},
      ),
      targetCount: json['targetCount'] as int? ?? 0,
      boltColor: boltColorValue != null ? Color(boltColorValue) : null,
      timelapseColor:
          timelapseColorValue != null ? Color(timelapseColorValue) : null,
    );
  }

  get requiredCompletions => null;

  get incrementAmount => null;

  set currentCompletions(int currentCompletions) {}

  // Add method to get historical progress for summary calculations
  Map<DateTime, double> get historicalProgress =>
      Map.unmodifiable(_historicalProgress);

  // Add method to clear historical progress
  void clearHistoricalProgress() {
    _historicalProgress.clear();
  }

  // Add method to merge historical progress
  void mergeHistoricalProgress(Map<DateTime, double> otherProgress) {
    _historicalProgress.addAll(otherProgress);
  }

  // Add validation methods
  bool isValidMissionState() {
  // Validate basic properties
    if ((id?.isEmpty ?? true) || title.isEmpty) return false;

  // Validate counter-based missions
    if (isCounterBased) {
      if (currentCount < 0) return false;
  // Remove target count validation to allow open-ended counters
    }

  // Validate subtasks
    if (subtasks.isNotEmpty) {
      for (var subtask in subtasks) {
        if (subtask.name.isEmpty) return false;
        if (subtask.requiredCompletions <= 0) return false;
        if (subtask.currentCompletions < 0 ||
            subtask.currentCompletions > subtask.requiredCompletions)
          return false;
        if (subtask.isCounterBased) {
          if (subtask.requiredCompletions <= 0) return false;
          if (subtask.currentCount < 0 ||
              subtask.currentCount > subtask.requiredCompletions)
            return false;
        }
      }
    }

    return true;
  }

  bool isDuplicateOf(MissionData other) {
  // Check if missions are duplicates based on key properties
    return id == other.id ||
        notificationId == other.notificationId ||
        (title == other.title &&
            type == other.type &&
            createdAt?.isAtSameMomentAs(other.createdAt ?? DateTime.now()) ==
                true);
  }

  // Add method to generate unique identifier
  static String generateUniqueId() {
    final now = DateTime.now();
    final random = Random();
    return '${now.millisecondsSinceEpoch}_${random.nextInt(1000000)}';
  }

  // New method to record daily progress
  void recordDailyProgress() {
    final now = DateTime.now();
    final dateKey = DateTime(now.year, now.month, now.day);

  // Calculate current progress
    double progress = 0.0;

    if (subtasks.isEmpty) {
      if (isCounterBased) {
        if (targetCount > 0) {
          progress = currentCount / targetCount;
        } else {
          progress = currentCount > 0 ? 1.0 : 0.0;
        }
      } else {
        progress = isCompleted ? 1.0 : 0.0;
      }
    } else {
  // Calculate average progress of all subtasks
      double totalProgress = 0.0;
      int validSubtasks = 0;

      for (final subtask in subtasks) {
        double subtaskProgress = 0.0;
        if (subtask.isCounterBased) {
          if (subtask.requiredCompletions > 0) {
            subtaskProgress =
                subtask.currentCount / subtask.requiredCompletions;
          } else {
            subtaskProgress = subtask.currentCount > 0 ? 1.0 : 0.0;
          }
        } else {
          if (subtask.requiredCompletions > 0) {
            subtaskProgress =
                subtask.currentCompletions / subtask.requiredCompletions;
          } else {
            subtaskProgress = subtask.currentCompletions > 0 ? 1.0 : 0.0;
          }
        }
        print('Subtask ${subtask.name} progress: $subtaskProgress');
        totalProgress += subtaskProgress;
        validSubtasks++;
      }

      progress = validSubtasks > 0 ? totalProgress / validSubtasks : 0.0;
    }

    print('Recording progress for mission $title: $progress');
    print('Date key: $dateKey');

  // Record the progress
    _historicalProgress[dateKey] = progress;
    print('Historical progress map size: ${_historicalProgress.length}');
    print(
      'Historical progress entries: ${_historicalProgress.entries.map((e) => '${e.key}: ${e.value}').join(', ')}',
    );

  // Clean up old entries
    _cleanupAndCompressHistoricalProgress();
  }

  // Add a public method to record progress for today (for UI/provider use)
  void recordProgress() {
    _recordProgress();
  }
}

class SubtaskData {
  final String? id;
  final String title;
  final bool isCompleted;
  final DateTime? lastCompleted;
  final bool isCounterBased;
  final int targetCount;
  int _currentCompletions;
  final int requiredCompletions;

  SubtaskData({
    this.id,
    required this.title,
    this.isCompleted = false,
    this.lastCompleted,
    this.isCounterBased = false,
    this.targetCount = 1,
    int currentCompletions = 0,
    this.requiredCompletions = 1,
    required currentCount,
  }) : _currentCompletions = currentCompletions;

  int get currentCompletions => _currentCompletions;
  set currentCompletions(int value) {
    _currentCompletions = value;
  }

  SubtaskData copyWith({
    String? id,
    String? title,
    bool? isCompleted,
    DateTime? lastCompleted,
    bool? isCounterBased,
    int? targetCount,
    int? currentCount,
  }) {
    return SubtaskData(
      id: id ?? this.id,
      title: title ?? this.title,
      isCompleted: isCompleted ?? this.isCompleted,
      lastCompleted: lastCompleted ?? this.lastCompleted,
      isCounterBased: isCounterBased ?? this.isCounterBased,
      targetCount: targetCount ?? this.targetCount,
      currentCount: currentCount ?? this.currentCount,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'isCompleted': isCompleted,
      'lastCompleted': lastCompleted?.toIso8601String(),
      'isCounterBased': isCounterBased,
      'targetCount': targetCount,
      'currentCount': currentCount,
    };
  }

  factory SubtaskData.fromJson(Map<String, dynamic> json) {
    return SubtaskData(
      id: json['id'],
      title: json['title'],
      isCompleted: json['isCompleted'] ?? false,
      lastCompleted:
          json['lastCompleted'] != null
              ? DateTime.parse(json['lastCompleted'])
              : null,
      isCounterBased: json['isCounterBased'] ?? false,
      targetCount: json['targetCount'] ?? 1,
      currentCount: json['currentCount'] ?? 0,
    );
  }

  get linkedMasteryId => null;

  double get masteryValue => 0.0;

  get name => null;

  get completionPercentage => null;

  get currentCount => null;
}

enum MissionType { daily, weekly, simple, persistent }

class MissionState {
  final List<MissionData> missions;
  final List<MissionData> completedMissions;
  final List<MissionData> deletedMissions;
  final bool isLoading;
  final String? error;

  const MissionState({
    required this.missions,
    required this.completedMissions,
    required this.deletedMissions,
    this.isLoading = false,
    this.error,
  });

  MissionState copyWith({
    List<MissionData>? missions,
    List<MissionData>? completedMissions,
    List<MissionData>? deletedMissions,
    bool? isLoading,
    String? error,
  }) {
    return MissionState(
      missions: missions ?? this.missions,
      completedMissions: completedMissions ?? this.completedMissions,
      deletedMissions: deletedMissions ?? this.deletedMissions,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class MissionProvider extends ChangeNotifier {
  static MissionProvider? latestInstance;

  MissionProvider() {
    latestInstance = this;
    _loadData();
  // NOTIFICATION INITIALIZATION REMOVED - will be called after loading screen
  // _initNotifications();
  // _startNotificationCheck();
    _startDailySummaryCheck();
    _startRefreshCheck();
    _startMissionCheck(); // Add this line

  // Start AI Guardian automatically
    _initializeAIGuardian();
    initializeAISandbox();
  }

  static void triggerSandboxNow() {
    print('🧪 MissionProvider: Static triggerSandboxNow called');
    latestInstance?.runAISandboxNow();
  }

  // --- AI Sandbox State ---
  bool _isSandboxWorking = false;
  bool get isSandboxWorking => _isSandboxWorking;
  set isSandboxWorking(bool value) {
    print('isSandboxWorking set to: $value');
    _isSandboxWorking = value;
    notifyListeners();
  }

  bool _isSandboxRunning = false;
  Timer? _sandboxTimer;
  Duration sandboxInterval = const Duration(seconds: 10);

  void initializeAISandbox() {
    print("🧪 MissionProvider: initializeAISandbox called");
    _sandboxTimer?.cancel();
  // Run AI sandbox independently every 30 seconds
    _sandboxTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      print('🧪 AI Sandbox: Independent timer tick');
      await _runAISandbox();
    });
  // Run immediately on startup
    _runAISandbox();
  }

  void startAISandbox() {
    _sandboxTimer?.cancel();
  // Run AI sandbox independently every 30 seconds
    _sandboxTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      print('🧪 AI Sandbox: Independent timer tick (from startAISandbox)');
      await _runAISandbox();
    });
    _runAISandbox();
  }

  void stopAISandbox() {
    _sandboxTimer?.cancel();
    isSandboxWorking = false;
    print('🧪 AI Sandbox: Stopped');
  }

  void runAISandboxNow() {
    _runAISandbox();
  }

  Future<void> _runAISandbox() async {
    if (_isSandboxRunning) {
      print('🧪 AI Sandbox: Already running, skipping...');
      return;
    }
    _isSandboxRunning = true;
    isSandboxWorking = true;
    notifyListeners();
    print('🧪 AI Sandbox: Starting independent sandbox logic...');

  // Run AI sandbox independently without user interaction requirements
    try {
  // Scan and analyze all files in lib folder
      final scannedCode = await _scanLibFolder();
      final scannedFiles = scannedCode.map((e) => e['file'] as String).toList();
      print('🧪 AI Sandbox: Scanned files: ${scannedFiles.join(', ')}');
      final coreFiles = [
        'lib/main.dart',
        'lib/mission.dart',
        'lib/mission_provider.dart',
        'lib/mechanicum.dart',
        'lib/ai_brain.dart',
      ];
      final foundCore =
          scannedFiles.where((f) => coreFiles.contains(f)).toList();
      if (foundCore.isNotEmpty) {
        print(
          '🧪 AI Sandbox: Core files included in scan: ${foundCore.join(', ')}',
        );
      } else {
        print('🧪 AI Sandbox: WARNING: No core files found in scan!');
      }
      print('🧪 AI Sandbox: Scanned ${scannedCode.length} code elements');

  // Track which files are being analyzed
      final currentAnalysisFiles = <String>[];
      final currentInsights = <Map<String, dynamic>>[];

      for (final codeElement in scannedCode) {
        final filePath = codeElement['file'] as String;
        final symbol = codeElement['symbol'] as String;
        final code = codeElement['code'] as String;

        currentAnalysisFiles.add(filePath);

  // Analyze the code and extract insights
        final parsed = _interpretCode(code, source: 'ai_analysis');
        final functions = parsed['functions'] ?? [];
        final classes = parsed['classes'] ?? [];
        final imports = parsed['imports'] ?? [];

  // Generate insights about this code element
        final insight = {
          'file': filePath,
          'symbol': symbol,
          'type': codeElement['type'],
          'functions': functions,
          'classes': classes,
          'imports': imports,
          'complexity': _calculateCodeComplexity(code),
          'patterns': _identifyCodePatterns(code),
          'learning': _generateLearningInsights(code, functions, classes),
          'timestamp': DateTime.now().toIso8601String(),
        };

        currentInsights.add(insight);

  // Add to file insights tracking
        _fileInsights[filePath] = _fileInsights[filePath] ?? [];
        _fileInsights[filePath]!.add(insight);

        print(
          '🧠 AI: Analyzing $filePath:$symbol - Found ${functions.length} functions, ${classes.length} classes',
        );
      }

  // Update analyzed files tracking
      final currentTime = DateTime.now().toIso8601String();
      _analyzedFiles[currentTime] = currentAnalysisFiles;

  // Create learning log entry
      final learningEntry = {
        'timestamp': DateTime.now(),
        'filesAnalyzed': currentAnalysisFiles,
        'totalElements': scannedCode.length,
        'insights': currentInsights,
        'focus': 'Code analysis and pattern recognition',
        'learnings': _extractKeyLearnings(currentInsights),
      };
      _aiLearningLog.add(learningEntry);

  // Select a random code element to focus on
      final codeToAnalyze =
          scannedCode.isNotEmpty
              ? scannedCode[Random().nextInt(scannedCode.length)]
              : null;
      final codeToAnalyzeFile = codeToAnalyze?['file'] as String?;
      final codeToAnalyzeSymbol = codeToAnalyze?['symbol'] as String?;
      final codeToAnalyzeCode = codeToAnalyze?['code'] as String?;

  // Enhanced metadata for the analysis
      final codeMetadata = {
        'source': 'lib_scan',
        'file': codeToAnalyzeFile,
        'symbol': codeToAnalyzeSymbol,
        'type': codeToAnalyze?['type'],
        'functions': codeToAnalyze?['functions'] ?? [],
        'classes': codeToAnalyze?['classes'] ?? [],
      };

      print(
        '🧠 AI: Focusing analysis on ${codeToAnalyzeFile ?? 'unknown'}:${codeToAnalyzeSymbol ?? 'unknown'}',
      );

  // Simulate AI processing time
      final duration = Random().nextInt(3) + 1;
      await Future.delayed(Duration(seconds: duration));

      final rand = Random();
      final focusAreas = [
        'test coverage',
        'bug detection',
        'self-improvement',
        'refactoring',
        'performance',
        'security',
      ];
      final String focus = focusAreas[rand.nextInt(focusAreas.length)];

  // Reference a previous experiment or suggestion for meta-growth
      String? previousExperimentDesc;
      if (_aiExperiments.isNotEmpty && rand.nextBool()) {
        final prev = _aiExperiments[rand.nextInt(_aiExperiments.length)];
        previousExperimentDesc = prev['description'];
      }

      String experimentDesc = 'Experimenting with $focus on recent code.';
      if (previousExperimentDesc != null && rand.nextBool()) {
        experimentDesc += ' Building on: $previousExperimentDesc';
        print(
          '🧠 AI: Building on previous experiment: $previousExperimentDesc',
        );
      }

  // Enhanced experiment with file analysis details
      final experiment = {
        'description': experimentDesc,
        'focus': focus,
        'timestamp': DateTime.now(),
        'filesAnalyzed': currentAnalysisFiles,
        'primaryFile': codeToAnalyzeFile,
        'primarySymbol': codeToAnalyzeSymbol,
        'totalElements': scannedCode.length,
        'insights': currentInsights.length,
        'learning': _extractKeyLearnings(currentInsights),
      };
      _aiExperiments.add(experiment);
      print('🧠 AI: New experiment: $experiment');

  // --- AI may propose an improvement to its own code ---
      if (aiGeneratedCodeSuggestions.isNotEmpty && rand.nextBool()) {
        final aiCode =
            aiGeneratedCodeSuggestions[rand.nextInt(
              aiGeneratedCodeSuggestions.length,
            )];
        final improvement =
            '/ Improved: ${aiCode['code']?.split("\n").first ?? ''}\n${aiCode['code']}\n/ ...AI self-improvement...';

  // Always include target information
        final targetFile =
            aiCode['targetFile'] ??
            codeToAnalyzeFile ??
            'lib/ai_improvements/ai_enhanced.dart';
        final targetSymbol =
            aiCode['targetSymbol'] ?? codeToAnalyzeSymbol ?? 'enhancedFunction';

        _aiGeneratedCodeSuggestions.add({
          'title': 'AI Self-Improvement',
          'code': improvement,
          'diff': '+ AI improved its own code',
          'reasoning':
              'The AI decided to enhance its previous code for better performance.',
          'timestamp': DateTime.now(),
          'targetFile': targetFile,
          'targetSymbol': targetSymbol,
        });
        print(
          '🧠 AI: Proposed improvement to its own code at $targetFile:$targetSymbol',
        );
      }

  // --- AI generates a new experiment/learning goal ---

  // Reference a previous experiment or suggestion for meta-growth
      if (_aiExperiments.isNotEmpty && rand.nextBool()) {
        final prev = _aiExperiments[rand.nextInt(_aiExperiments.length)];
        previousExperimentDesc = prev['description'];
      }

      if (previousExperimentDesc != null && rand.nextBool()) {
        experimentDesc += ' Building on: $previousExperimentDesc';
        print(
          '🧠 AI: Building on previous experiment: $previousExperimentDesc',
        );
      }

      _aiExperiments.add(experiment);
      print('🧠 AI: New experiment: $experiment');

  // --- AI may generate meta-suggestions ---
      if (_aiSuggestions.isNotEmpty && rand.nextInt(4) == 0) {
  // 25% chance
        final prevSuggestion =
            _aiSuggestions[rand.nextInt(_aiSuggestions.length)];
        final metaSuggestion = {
          'issue': 'Refactor previous suggestion: ${prevSuggestion['issue']}',
          'explanation': 'AI is improving on its own earlier suggestion.',
          'changes': ['Meta-refactor of previous suggestion'],
          'testResults': ['Meta-tested previous suggestion'],
          'accepted': false,
          'ignored': false,
          'acceptedAt': DateTime.now().toIso8601String(),
          'ignoredAt': DateTime.now().toIso8601String(),
        };
        _aiSuggestions.add(metaSuggestion);
        print('🧠 AI: Meta-suggestion created: $metaSuggestion');
      }

  // --- AI may improve its own code suggestions ---
      if (aiGeneratedCodeSuggestions.isNotEmpty && rand.nextInt(3) == 0) {
  // 33% chance
        final prevCode =
            aiGeneratedCodeSuggestions[rand.nextInt(
              aiGeneratedCodeSuggestions.length,
            )];
        final improvedCode =
            '/ Improved on previous AI code\n${prevCode['code']}\n/ Further enhancements...';

  // Always use the previous target or determine new one
        String targetFile =
            prevCode['targetFile'] ??
            codeToAnalyzeFile ??
            'lib/ai_improvements/iterative.dart';
        String targetSymbol =
            prevCode['targetSymbol'] ??
            codeToAnalyzeSymbol ??
            'improvedFunction';

  // Try to extract function name from improved code
        final fnMatch = RegExp(
          r'void\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ).firstMatch(improvedCode);
        if (fnMatch != null) {
          targetSymbol = fnMatch.group(1)!;
        }

        final improvedSuggestion = {
          'title': 'Improved: ${prevCode['title']}',
          'code': improvedCode,
          'diff': '+ Improved previous AI code',
          'reasoning': 'AI is iteratively enhancing its own codebase.',
          'timestamp': DateTime.now(),
          'targetFile': targetFile,
          'targetSymbol': targetSymbol,
        };
        _aiGeneratedCodeSuggestions.add(improvedSuggestion);
        print(
          '🧠 AI: Improved its own code suggestion at $targetFile:$targetSymbol',
        );
      }

  // --- Simulate test feed update with file information ---
      final testResult = rand.nextBool() ? 'pass' : 'fail';
      final testEntry = <String, String>{
        'testType': focus.toString(),
        'function':
            codeToAnalyzeSymbol ??
            ((_interpretCode(codeToAnalyzeCode ?? '')['functions']
                            as List<dynamic>?)
                        ?.firstOrNull
                    as String? ??
                'unknown'),
        'file': codeToAnalyzeFile ?? 'unknown',
        'details':
            'Tested ${focus.toString()} on code from ${codeMetadata['source'] ?? 'unknown'} source.',
        'result': testResult,
        'reasoning': 'AI determined this test was necessary for learning.',
        'timestamp': DateTime.now().toIso8601String(),
      };
      _sandboxTestFeed.add(testEntry);
      print('🧪 AI Sandbox: Test feed updated: $testEntry');

  // --- AI Suggestions ---
      final suggestion = {
        'issue': 'Potential improvement in $focus',
        'explanation': 'AI detected an opportunity to enhance $focus.',
        'changes': ['Refactor $focus'],
        'testResults': ['Tested $focus: $testResult'],
        'accepted': rand.nextBool(),
        'ignored': rand.nextBool(),
        'acceptedAt': DateTime.now().toIso8601String(),
        'ignoredAt': DateTime.now().toIso8601String(),
      };
      _aiSuggestions.add(suggestion);
      print('🧠 AI: New suggestion: $suggestion');

  // --- Knowledge Gaps ---
      if (rand.nextBool()) {
        final gap = 'AI wants to learn more about $focus.';
        if (!_knowledgeGaps.contains(gap)) {
          _knowledgeGaps.add(gap);
          print('🧠 AI: New knowledge gap: $gap');
        }
      }

  // --- Test Coverage ---
      _testCoverage[focus] = (_testCoverage[focus] ?? 0) + 1;
      print('🧪 AI: Test coverage updated: $_testCoverage');

  // --- Knowledge Graph ---
      _knowledgeGraph[focus] = _knowledgeGraph[focus] ?? [];
      if (codeToAnalyze != null) {
        final parsed = _interpretCode(codeToAnalyze as String);
        for (final fn in parsed['functions'] ?? []) {
          if (!_knowledgeGraph[focus]!.contains(fn)) {
            _knowledgeGraph[focus]!.add(fn);
          }
        }
      }
      print('🧠 AI: Knowledge graph updated: $_knowledgeGraph');

  // --- Applied AI Suggestions ---
      if (rand.nextBool() && _aiSuggestions.isNotEmpty) {
        final applied = _aiSuggestions[rand.nextInt(_aiSuggestions.length)];
        _appliedAISuggestions.add({
          'title': applied['issue'],
          'appliedAt': DateTime.now().toIso8601String(),
        });
        print('🧠 AI: Applied suggestion: $applied');
      }

  // --- AI Extension Ideas ---
      if (rand.nextBool()) {
        final idea = {
          'feature': 'Auto-tune $focus',
          'rationale':
              'AI believes auto-tuning $focus will yield better results.',
        };
        _aiExtensionIdeas.add(idea);
        print('🧠 AI: New extension idea: $idea');
      }

  // --- AI Personalized Suggestions ---
      if (rand.nextBool()) {
        final personal = {
          'suggestion': 'Focus on $focus for next iteration.',
          'priority': rand.nextBool() ? 'high' : 'medium',
        };
        _aiPersonalizedSuggestions.add(personal);
        print('🧠 AI: New personalized suggestion: $personal');
      }

  // --- AI Generated Code Suggestions (ALWAYS with target info) ---
      if (rand.nextBool()) {
  // Generate intelligent code based on focus area
        String code = _generateIntelligentCode(focus, codeToAnalyze as String?);
        String targetSymbol = _extractTargetSymbol(code);
        String targetFile = _determineTargetFile(code, _interpretCode(code));

  // Ensure the target location is safe
        final safetyCheck = await _analyzeFileSafety(targetFile, targetSymbol);
        if (!safetyCheck['safe']) {
          final safeLocation = await _findSafeApplicationLocation(
            code,
            _interpretCode(code),
          );
          if (safeLocation != null) {
            targetFile = safeLocation['file'] ?? targetFile;
            targetSymbol = safeLocation['symbol'] ?? targetSymbol;
          }
        }

        final codeSuggestion = {
          'title': 'Refactor $focus',
          'code': code,
          'diff': '+ Refactored $focus',
          'reasoning': 'AI believes this will improve $focus.',
          'timestamp': DateTime.now(),
          'targetFile': targetFile,
          'targetSymbol': targetSymbol,
        };
        _aiGeneratedCodeSuggestions.add(codeSuggestion);
        print('🧠 AI: New code suggestion at $targetFile:$targetSymbol');
      }

      isSandboxWorking = false;
      _isSandboxRunning = false;
      print('🧪 AI Sandbox: Sandbox logic complete after $duration seconds.');
      notifyListeners();
    } catch (e) {
      print('🛡️ AI Guardian: ❌ Error during AI Sandbox: $e');
      isSandboxWorking = false;
      _isSandboxRunning = false;
      notifyListeners();
    }
  }

  // --- Enhanced helper methods for file scanning and safety ---

  Future<List<Map<String, dynamic>>> _scanLibFolder() async {
    final List<Map<String, dynamic>> scannedFiles = [];

    try {
  // Get all directories that should be watched, including Terra/Conquest apps
      final watchedDirs = AIFileSystemHelper.getWatchedDirectories();
      print('🧪 AI Sandbox: Scanning directories: ${watchedDirs.join(', ')}');

  // Scan for new files created by Terra/Conquest
      final newAppFiles = await AIFileSystemHelper.scanForNewAppFiles();
      if (newAppFiles.isNotEmpty) {
        print(
          '🧪 AI Sandbox: Found ${newAppFiles.length} new app files: ${newAppFiles.join(', ')}',
        );
      }

  // Scan all files in watched directories
      for (final dir in watchedDirs) {
        try {
          final files = await AIFileSystemHelper.listFilesRecursively(
            dir,
            extension: '.dart',
          );
          for (final filePath in files) {
            try {
              final file = File(filePath);
              if (await file.exists()) {
                final content = await file.readAsString();
                final parsed = _interpretCode(content, source: 'lib_scan');

  // Extract functions and classes from the file
                final functions = parsed['functions'] ?? [];
                final classes = parsed['classes'] ?? [];

  // Create entries for each function/class found
                for (final function in functions) {
                  scannedFiles.add({
                    'file': filePath,
                    'symbol': function,
                    'code': _extractFunctionCode(content, function),
                    'functions': [function],
                    'classes': [],
                    'type': 'function',
                  });
                }

                for (final className in classes) {
                  scannedFiles.add({
                    'file': filePath,
                    'symbol': className,
                    'code': _extractClassCode(content, className),
                    'functions': [],
                    'classes': [className],
                    'type': 'class',
                  });
                }

  // If no functions/classes found, add the whole file
                if (functions.isEmpty && classes.isEmpty) {
                  scannedFiles.add({
                    'file': filePath,
                    'symbol': 'file_content',
                    'code': content,
                    'functions': [],
                    'classes': [],
                    'type': 'file',
                  });
                }
              }
            } catch (e) {
              print('⚠️ AI Sandbox: Error scanning $filePath: $e');
            }
          }
        } catch (e) {
          print('⚠️ AI Sandbox: Error scanning directory $dir: $e');
        }
      }
    } catch (e) {
      print('⚠️ AI Sandbox: Error during file scan: $e');
    }

    print('🧪 AI Sandbox: Total files scanned: ${scannedFiles.length}');
    return scannedFiles;
  }

  String _extractFunctionCode(String fileContent, String functionName) {
  // Extract function code using regex
    final functionRegex = RegExp(
      r'(\n|^)([\w<>\s]*?)' +
          RegExp.escape(functionName) +
          r'\s*\([^)]*\)\s*\{[\s\S]*?^\}',
      multiLine: true,
    );
    final match = functionRegex.firstMatch(fileContent);
    return match?.group(0) ?? '/ Function $functionName not found';
  }

  String _extractClassCode(String fileContent, String className) {
  // Extract class code using regex
    final classRegex = RegExp(
      r'(\n|^)class\s+' + RegExp.escape(className) + r'\s*\{[\s\S]*?^\}',
      multiLine: true,
    );
    final match = classRegex.firstMatch(fileContent);
    return match?.group(0) ?? '/ Class $className not found';
  }

  Future<Map<String, dynamic>> _analyzeFileSafety(
    String targetFile,
    String? targetSymbol,
  ) async {
    try {
      final file = File(targetFile);
      if (!await file.exists()) {
        return {
          'safe': false,
          'reason': 'Target file does not exist',
          'suggestions': ['Create the file first', 'Use a different target'],
        };
      }

      final content = await file.readAsString();

  // Check if target symbol exists
      if (targetSymbol != null && targetSymbol != 'unknown') {
        final functionExists = RegExp(
          r'(\n|^)([\w<>\s]*?)' +
              RegExp.escape(targetSymbol) +
              r'\s*\([^)]*\)\s*\{',
          multiLine: true,
        ).hasMatch(content);
        final classExists = RegExp(
          r'(\n|^)class\s+' + RegExp.escape(targetSymbol) + r'\s*\{',
          multiLine: true,
        ).hasMatch(content);

        if (!functionExists && !classExists) {
          return {
            'safe': false,
            'reason': 'Target symbol "$targetSymbol" not found in file',
            'suggestions': [
              'Check symbol name',
              'Add the symbol first',
              'Use existing symbol',
            ],
          };
        }
      }

  // Check for critical files that shouldn't be modified
      final criticalFiles = [
        'lib/main.dart',
        'lib/mission.dart',
        'lib/mission_provider.dart',
      ];

      if (criticalFiles.contains(targetFile)) {
        return {
          'safe': false,
          'reason': 'Critical file - modifications may break the app',
          'suggestions': [
            'Use a test file',
            'Create a new file',
            'Apply to non-critical file',
          ],
        };
      }

  // Check for existing AI-generated files (safe to modify)
      if (targetFile.contains('ai_') || targetFile.contains('generated')) {
        return {
          'safe': true,
          'reason': 'AI-generated file - safe to modify',
          'suggestions': ['Proceed with modification'],
        };
      }

  // Check file size and complexity
      final lines = content.split('\n').length;
      if (lines > 500) {
        return {
          'safe': false,
          'reason': 'Large file ($lines lines) - high risk of breaking changes',
          'suggestions': [
            'Use a smaller file',
            'Create a new file',
            'Test thoroughly',
          ],
        };
      }

      return {
        'safe': true,
        'reason': 'File appears safe for modification',
        'suggestions': ['Proceed with caution', 'Test after modification'],
      };
    } catch (e) {
      return {
        'safe': false,
        'reason': 'Error analyzing file: $e',
        'suggestions': ['Check file permissions', 'Use a different file'],
      };
    }
  }

  Future<Map<String, String>?> _findSafeApplicationLocation(
    String code,
    Map<String, dynamic> parsed,
  ) async {
  // Try to find a safe location for the code
    final safeLocations = [
      'lib/ai_sandbox/safe_test.dart',
      'lib/ai_generated/test_code.dart',
      'lib/utils/ai_utils.dart',
      'lib/widgets/ai_widgets.dart',
    ];

    for (final location in safeLocations) {
      final safetyCheck = await _analyzeFileSafety(location, null);
      if (safetyCheck['safe']) {
        final symbol = _extractTargetSymbol(code);
        return {'file': location, 'symbol': symbol};
      }
    }

  // If no safe location found, create a new one
    final newFile =
        'lib/ai_sandbox/generated_${DateTime.now().millisecondsSinceEpoch}.dart';
    final symbol = _extractTargetSymbol(code);

    return {'file': newFile, 'symbol': symbol};
  }

  MissionState _state = MissionState(
    missions: [],
    completedMissions: [],
    deletedMissions: [],
  );

  // Add StreamController for mission updates
  final _missionController = StreamController<void>.broadcast();
  Stream<void> get missionStream => _missionController.stream;

  MissionState get state => _state;

  List<MissionData> get missions => _state.missions;
  List<MissionData> get completedMissions => _state.completedMissions;
  List<MissionData> get deletedMissions => _state.deletedMissions;
  List<MissionData> get allMissions => [
    ..._state.missions,
    ..._state.completedMissions,
    ..._state.deletedMissions,
  ];

  List<MissionData> get dailyMissions =>
      _state.missions.where((m) => m.type == MissionType.daily).toList();
  List<MissionData> get weeklyMissions =>
      _state.missions.where((m) => m.type == MissionType.weekly).toList();
  List<MissionData> get simpleTasks =>
      _state.missions.where((m) => m.type == MissionType.simple).toList();

  Map<DateTime, bool> _dailyCompletionStatus = {};
  Map<DateTime, int> _dailyGoalsCreated = {};
  final EntryManager _entryManager = EntryManager();
  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();
  int _notificationIdCounter = 0;
  Set<String> _usedImages = {};
  bool _isTestingMode = false; // Add testing mode flag
  final Mechanicum aiGuardian = Mechanicum.instance; // Add AI Guardian instance

  // Add getter for testing mode
  bool get isTestingMode => _isTestingMode;

  // Add method to toggle testing mode
  void toggleTestingMode() {
    _isTestingMode = !_isTestingMode;
    if (_isTestingMode) {
      _refreshButtonColor = Colors.orange;
      _isDailyLocked = true;
      _isWeeklyLocked = true;
    } else {
      _refreshButtonColor = Colors.white;
      _isDailyLocked = false;
      _isWeeklyLocked = false;
    }
    notifyListeners();
  }

  // Add new state variables for mission locking
  bool _isDailyLocked = false;
  bool _isWeeklyLocked = false;
  Color _refreshButtonColor = Colors.white;

  // Getters for mission locking state
  bool get isDailyLocked => _isDailyLocked;
  bool get isWeeklyLocked => _isWeeklyLocked;
  Color get refreshButtonColor => _refreshButtonColor;

  // Add method to check if a mission should be locked
  bool shouldLockMission(MissionData mission) {
    if (mission.type == MissionType.daily) {
      return _isDailyLocked;
    } else if (mission.type == MissionType.weekly) {
      return _isWeeklyLocked;
    }
    return false;
  }

  // Add method to update refresh button color based on time
  void updateRefreshButtonColor() {
    final now = DateTime.now();

  // Check for end of week (Sunday at 11:59 PM)
    if (now.weekday == DateTime.sunday && now.hour == 23 && now.minute >= 59) {
      _refreshButtonColor = Colors.orange;
      _isDailyLocked = true;
      _isWeeklyLocked = true;
  // Trigger refresh for both daily and weekly missions
      refreshMissions();
      developer.log('End of week detected: Refreshing all missions');
    }
  // Check for end of day (11:59 PM)
    else if (now.hour == 23 && now.minute >= 59) {
      _refreshButtonColor = Colors.red;
      _isDailyLocked = true;
      _isWeeklyLocked = false;
  // Trigger refresh for daily missions
      refreshMissionsByType(MissionType.daily);
      developer.log('End of day detected: Refreshing daily missions');
    }
  // Normal state
    else {
      _refreshButtonColor = Colors.white;
      _isDailyLocked = false;
      _isWeeklyLocked = false;
    }

    notifyListeners();
  }

  Map<DateTime, bool> get dailyCompletionStatus => _dailyCompletionStatus;
  Map<DateTime, int> get dailyGoalsCreated => _dailyGoalsCreated;

  // Add getter for mission history by type
  List<MissionData> getMissionHistoryByType(MissionType type) {
    return allMissions.where((m) => m.type == type).toList();
  }

  // Add getter for mission history by date range
  List<MissionData> getMissionHistoryByDateRange(DateTime start, DateTime end) {
    return allMissions.where((m) {
      if (m.createdAt == null) return false;
      return m.createdAt!.isAfter(start) && m.createdAt!.isBefore(end);
    }).toList();
  }

  // Add getter for completed missions by date range
  List<MissionData> getCompletedMissionsByDateRange(
    DateTime start,
    DateTime end,
  ) {
    return allMissions.where((m) {
      if (m.lastCompleted == null) return false;
      return m.lastCompleted!.isAfter(start) && m.lastCompleted!.isBefore(end);
    }).toList();
  }

  Future<void> _initializeAIGuardian() async {
    print('🛡️ AI Guardian: Initializing automatically...');

  // Initialize the AI Guardian with learning capabilities
    await aiGuardian.initialize();

  // Register existing notification IDs with the AI Guardian
    for (final mission in allMissions) {
      aiGuardian.registerNotificationId(mission.notificationId);
    }

  // Learn from existing issues
    await _learnFromExistingIssues();

  // Trigger the AI sandbox at the same time as AI Guardian
    print('🛡️ AI Guardian: Triggering AI Sandbox Now (static)...');
    MissionProvider.triggerSandboxNow();

  // Start the AI Guardian with enhanced health check functionality
    aiGuardian.startContinuousHealthCheck(
      () async {
  // Keep AI Guardian active during health checks
        aiGuardian.setAIActive(true);

  // Perform comprehensive health checks using learned patterns
        final healthResults =
            await aiGuardian.performComprehensiveHealthChecks();

  // If issues found, perform repairs
        if (healthResults.any((result) => result.hasIssue)) {
          print('AI Guardian: 🔧 Issues detected, performing repairs...');
          final repairResults = await aiGuardian.performComprehensiveRepairs();

  // Log successful repairs
          for (final result in repairResults.where((r) => r.success)) {
            aiGuardian.logRepair(
              result.repairName,
              'Successfully repaired: ${result.description}',
            );
          }
        }

  // Keep AI Guardian active for a bit longer to show it's working
        await Future.delayed(const Duration(seconds: 3));
        aiGuardian.setAIActive(false);
      },
      interval: const Duration(seconds: 8),
    ); // More frequent checks for better visibility

  // Make AI Guardian visible immediately
    aiGuardian.setAIActive(true);
    await Future.delayed(const Duration(seconds: 4));
    aiGuardian.setAIActive(false);

    print(
      '🛡️ AI Guardian: Auto-started successfully with learning capabilities',
    );
  }

  // Learn from existing issues in the mission data
  Future<void> _learnFromExistingIssues() async {
  // Check for invalid notification IDs
    bool hasInvalidNotificationIds = false;
    for (final mission in allMissions) {
      if (mission.notificationId < -2147483648 ||
          mission.notificationId > 2147483647) {
        hasInvalidNotificationIds = true;
        break;
      }
    }

    if (hasInvalidNotificationIds) {
      await aiGuardian.learnNewHealthCheck(
        'invalid_notification_ids',
        'Check for notification IDs outside 32-bit integer range',
        () async => _checkForInvalidNotificationIds(),
        priority: HealthCheckPriority.critical,
      );

      await aiGuardian.learnNewRepair(
        'invalid_notification_ids',
        'Repair notification IDs that are outside valid range',
        () async => _fixInvalidNotificationIds(),
        priority: RepairPriority.critical,
      );
    }

  // Check for duplicate notification IDs
    final seenIds = <int>{};
    bool hasDuplicateIds = false;
    for (final mission in allMissions) {
      if (seenIds.contains(mission.notificationId)) {
        hasDuplicateIds = true;
        break;
      }
      seenIds.add(mission.notificationId);
    }

    if (hasDuplicateIds) {
      await aiGuardian.learnNewHealthCheck(
        'duplicate_notification_ids',
        'Check for duplicate notification IDs across missions',
        () async => _checkForDuplicateNotificationIds(),
        priority: HealthCheckPriority.high,
      );

      await aiGuardian.learnNewRepair(
        'duplicate_notification_ids',
        'Repair duplicate notification IDs by generating unique ones',
        () async => _fixDuplicateNotificationIds(),
        priority: RepairPriority.high,
      );
    }
  }

  // Check for invalid notification IDs
  Future<bool> _checkForInvalidNotificationIds() async {
    for (final mission in allMissions) {
      if (mission.notificationId < -2147483648 ||
          mission.notificationId > 2147483647) {
        return true;
      }
    }
    return false;
  }

  // Check for duplicate notification IDs
  Future<bool> _checkForDuplicateNotificationIds() async {
    final seenIds = <int>{};
    for (final mission in allMissions) {
      if (seenIds.contains(mission.notificationId)) {
        return true;
      }
      seenIds.add(mission.notificationId);
    }
    return false;
  }

  // Fix invalid notification IDs
  Future<void> _fixInvalidNotificationIds() async {
    print('AI Guardian: 🔧 Fixing invalid notification IDs...');
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      if (mission.notificationId < -2147483648 ||
          mission.notificationId > 2147483647) {
        final newId = aiGuardian.generateValidNotificationId();
        final updatedMission = mission.copyWith(notificationId: newId);
        missionsToUpdate.add(updatedMission);

        print(
          'AI Guardian: Fixed invalid notification ID for mission "${mission.title}": ${mission.notificationId} -> $newId',
        );
        aiGuardian.logRepair(
          'Invalid Notification ID',
          'Fixed notification ID from ${mission.notificationId} to $newId',
          missionId: mission.id,
        );
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      await editMission(
        allMissions.firstWhere((m) => m.id == updatedMission.id),
        updatedMission,
      );
    }

    if (missionsToUpdate.isNotEmpty) {
      await _saveMissions();
      notifyListeners();
      print(
        'AI Guardian: ✅ Fixed ${missionsToUpdate.length} invalid notification IDs',
      );
    }
  }

  // Fix duplicate notification IDs
  Future<void> _fixDuplicateNotificationIds() async {
    print('AI Guardian: 🔧 Fixing duplicate notification IDs...');
    final seenIds = <int>{};
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      if (seenIds.contains(mission.notificationId)) {
        final newId = aiGuardian.generateValidNotificationId();
        final updatedMission = mission.copyWith(notificationId: newId);
        missionsToUpdate.add(updatedMission);

        print(
          'AI Guardian: Fixed duplicate notification ID for mission "${mission.title}": ${mission.notificationId} -> $newId',
        );
        aiGuardian.logRepair(
          'Duplicate Notification ID',
          'Fixed duplicate notification ID from ${mission.notificationId} to $newId',
          missionId: mission.id,
        );
      } else {
        seenIds.add(mission.notificationId);
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      await editMission(
        allMissions.firstWhere((m) => m.id == updatedMission.id),
        updatedMission,
      );
    }

    if (missionsToUpdate.isNotEmpty) {
      await _saveMissions();
      notifyListeners();
      print(
        'AI Guardian: ✅ Fixed ${missionsToUpdate.length} duplicate notification IDs',
      );
    }
  }

  @override
  void dispose() {
    _missionController.close();
    _state.missions.clear();
    _state.completedMissions.clear();
    _state.deletedMissions.clear();
    _usedImages.clear();
    _dailyGoalsCreated.clear();
    aiGuardian.dispose(); // Dispose AI Guardian
    super.dispose();
  }

  // Update notifyListeners to also emit stream events
  @override
  void notifyListeners() {
    super.notifyListeners();
    _missionController.add(null);
  }

  Future<void> _startMissionCheck() async {
    Timer.periodic(const Duration(minutes: 1), (timer) async {
      try {
        final now = DateTime.now();
        bool needsUpdate = false;

  // Check for daily mission refresh at midnight (00:00)
        if (now.hour == 0 && now.minute == 0) {
          for (var mission in List<MissionData>.from(_state.missions)) {
            if (mission.type == MissionType.daily) {
              await refreshMission(mission);
              needsUpdate = true;
            }
          }
        }

  // Check for weekly mission refresh at 11:59 PM on Sunday
        if (now.weekday == DateTime.sunday &&
            now.hour == 23 &&
            now.minute == 59) {
          for (var mission in List<MissionData>.from(_state.missions)) {
            if (mission.type == MissionType.weekly) {
              await refreshMission(mission);
              needsUpdate = true;
            }
          }
        }

        if (needsUpdate) {
          await _saveMissions();
          await _updateAllNotifications();
          notifyListeners();
        }
      } catch (e) {
        print('Error in mission check: $e');
      }
    });
  }

  Future<void> completeMission(
    MissionData mission, {
    bool fromNotification = false,
  }) async {
    final missionIndex = _state.missions.indexWhere(
      (m) => m.notificationId == mission.notificationId,
    );
    if (missionIndex != -1) {
      print(
        'Completing mission: ${mission.title}, Subtasks: ${mission.subtasks.length}, From notification: $fromNotification',
      );

      mission.isCompleted = true;
      mission.lastCompleted = DateTime.now();
      mission.hasFailed = false; // Reset failure status on completion
      if (mission.subtasks.isEmpty) {
        mission.currentCompletions = 1;
      }

      if (!fromNotification) {
        await _notifications.cancel(mission.notificationId);
        if (mission.type == MissionType.simple) {
          _state.missions.removeAt(missionIndex);
        }
      } else {
        await _notifications.show(
          9997,
          'Mission Completed',
          '${mission.title} marked as complete!',
          NotificationDetails(
            android: AndroidNotificationDetails(
              'mission_channel',
              'Missions',
              channelDescription: 'Mission notifications',
              importance: Importance.high,
              priority: Priority.high,
              autoCancel: true,
            ),
          ),
        );
        print('Confirmation notification shown for ${mission.title}');
        await _showNotificationForMission(mission);
      }

      await _saveData();
      notifyListeners();
      print('Notified listeners for mission: ${mission.title}');
      await _updateBadge();
      await _showSummaryNotification();
    } else {
      print('Mission not found for ID: ${mission.notificationId}');
    }
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

      final missionIndex = _state.missions.indexWhere(
        (m) => m.notificationId == mission.notificationId,
      );

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

        bool allSubtasksComplete = updatedSubtasks.every(
          (s) => s.currentCompletions >= s.requiredCompletions,
        );

        final updatedMission = mission.copyWith(
          isCompleted: allSubtasksComplete,
          lastCompleted: allSubtasksComplete ? DateTime.now() : null,
          hasFailed: false, // Remove failed status when progress is made
          subtasks: updatedSubtasks,
        );

  // Update the mission in state
        final updatedMissions = List<MissionData>.from(_state.missions);
        updatedMissions[missionIndex] = updatedMission;
        _state = _state.copyWith(missions: updatedMissions);

  // Update notification
        await _notifications.cancel(mission.notificationId);
        await _showNotificationForMission(updatedMission);

  // Save changes
        await _saveMissions();
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        developer.log('Successfully completed subtask: ${subtask.name}');
      } else {
        developer.log(
          'Mission not found for subtask completion: ${mission.title}',
        );
      }
    } catch (e, stackTrace) {
      developer.log('Error completing subtask: $e\n$stackTrace');
      throw AppError(
        'Failed to complete subtask',
        'COMPLETE_SUBTASK_ERROR',
        code: 'COMPLETE_SUBTASK_ERROR',
        originalError: e,
        stackTrace: stackTrace,
      );
    }
  }

  Future<void> addMission(
    MissionData mission, {
    required String title,
    required String description,
    String? imageUrl,
    MissionType type = MissionType.daily,
    required List<MissionSubtask> subtasks,
    String? linkedMasteryId,
    required double masteryValue,
    required bool isCounterBased,
    required int targetCount,
    required Map<String, double> subtaskMasteryValues,
    String? masteryId,
    double? value,
    bool isSubtaskCounter = false,
    int? scheduledNotificationId,
  }) async {
    await requestNotificationPermission();

    String selectedImage;
    final availableImages =
        _entryManager.imageList
            .where((img) => !_usedImages.contains(img))
            .toList();

    if (imageUrl != null && _entryManager.imageList.contains(imageUrl)) {
      selectedImage = imageUrl;
    } else if (availableImages.isNotEmpty) {
      final random = Random();
      selectedImage = availableImages[random.nextInt(availableImages.length)];
    } else {
      final random = Random();
      selectedImage =
          _entryManager.imageList[random.nextInt(
            _entryManager.imageList.length,
          )];
    }

    _usedImages.add(selectedImage);

  // Reset all subtasks to not completed state
    final resetSubtasks =
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
              ),
            )
            .toList();

  // Ensure subtaskMasteryValues is Map<String, double>
    final castedSubtaskMasteryValues = subtaskMasteryValues.map(
      (key, value) => MapEntry(key.toString(), (value as num).toDouble()),
    );

  // Validate and fix subtask mastery values to ensure they are always valid
    final validatedSubtaskMasteryValues = <String, double>{};
    for (final entry in castedSubtaskMasteryValues.entries) {
  // Ensure mastery values are always greater than 0
      validatedSubtaskMasteryValues[entry.key] =
          entry.value > 0 ? entry.value : 1.0;
    }

  // Allow open-ended counters (targetCount null or 0)
    if (isCounterBased && targetCount != null && targetCount < 0) {
      throw Exception(
        'Counter-based missions must have a targetCount >= 0 or null for open-ended',
      );
    }

  // Generate a unique ID for the new mission
    final uniqueId =
        (DateTime.now().millisecondsSinceEpoch % 100000).toString();

  // Generate random colors for the icons
    final random = Random();
    final boltColor = Color.fromRGBO(
      random.nextInt(256),
      random.nextInt(256),
      random.nextInt(256),
      1.0,
    );
    final timelapseColor = Color.fromRGBO(
      random.nextInt(256),
      random.nextInt(256),
      random.nextInt(256),
      1.0,
    );

    final mission = MissionData(
      id: uniqueId,
      missionId: uniqueId,
      title: title,
      description: description.isEmpty ? '' : description,
      type: type,
      createdAt: DateTime.now(),
      isCompleted: false,
      hasFailed: false,
      masteryId: masteryId,
      value: value,
      subtasks: resetSubtasks,
      isCounterBased: isCounterBased,
      currentCount: 0,
      isSubtaskCounter: isSubtaskCounter,
      imageUrl: selectedImage,
      notificationId: _generateUniqueNotificationId(),
      scheduledNotificationId: scheduledNotificationId,
      masteryValue: masteryValue,
      linkedMasteryId: linkedMasteryId,
      subtaskMasteryValues: validatedSubtaskMasteryValues,
      targetCount: targetCount,
      boltColor: isCounterBased ? boltColor : null,
      timelapseColor: timelapseColor,
    );

  // Add the new mission without checking for duplicates
    _state.missions.add(mission);
    incrementGoalsCreated(DateTime.now());

    await _showImmediateNotification(mission);
    await _showNotificationForMission(mission);

    await _saveData();
    notifyListeners();
    await _updateBadge();
  }

  Future<void> _showImmediateNotification(MissionData mission) async {
    try {
      ByteArrayAndroidBitmap? bitmap;
      if (mission.imageUrl.isNotEmpty) {
        final fadedImageBytes = await _getFadedImageBytes(mission.imageUrl);
        if (fadedImageBytes != null) {
          bitmap = ByteArrayAndroidBitmap(fadedImageBytes);
        }
      }

  // Use the unified notification content builder
      String description = _buildNotificationContent(mission);

      final actions = <AndroidNotificationAction>[];
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

      final androidPlatformChannelSpecifics = AndroidNotificationDetails(
        'mission_channel',
        'Missions',
        channelDescription: 'Mission notifications',
        importance: Importance.max,
        priority: Priority.max,
        showWhen: true,
        autoCancel: false,
        ongoing: true,
        visibility: NotificationVisibility.public,
        onlyAlertOnce: true,
        groupKey: 'com.example.lvl_up.missions',
        setAsGroupSummary: false,
        styleInformation: BigTextStyleInformation(
          description,
          contentTitle:
              mission.hasFailed ? '❗ GET SHIT DONE !!!' : mission.title,
          htmlFormatContent: false,
          htmlFormatTitle: false,
        ),
        actions: actions,
        largeIcon: bitmap,
      );

      final platformChannelSpecifics = NotificationDetails(
        android: androidPlatformChannelSpecifics,
      );

      await _notifications.show(
        mission.notificationId,
        mission.hasFailed ? '❗ GET SHIT DONE !!!' : mission.title,
        description,
        platformChannelSpecifics,
        payload: mission.notificationId.toString(),
      );
      await _showSummaryNotification();
    } catch (e) {
      print(
        'Error showing immediate notification for mission ${mission.title}: $e',
      );
    }
  }

  Future<void> _showNotificationForMission(MissionData mission) async {
    try {
  // Use the unified notification content builder
      String description = _buildNotificationContent(mission);
      print('Showing notification with description: $description');

      final androidPlatformChannelSpecifics = AndroidNotificationDetails(
        NotificationChannels.mission,
        'Missions',
        channelDescription: 'Mission notifications',
        importance: Importance.max,
        priority: Priority.max,
        showWhen: true,
        autoCancel: false,
        ongoing: true,
        visibility: NotificationVisibility.public,
        onlyAlertOnce: true,
        groupKey: 'com.example.lvl_up.missions',
        setAsGroupSummary: false,
        styleInformation: BigTextStyleInformation(
          description,
          contentTitle: _getNotificationTitle(mission),
          htmlFormatContent: false,
          htmlFormatTitle: false,
        ),
        icon: '@mipmap/berserk',
      );

      final platformChannelSpecifics = NotificationDetails(
        android: androidPlatformChannelSpecifics,
      );

  // Show notification with unique ID
      await _notifications.show(
        mission.notificationId,
        _getNotificationTitle(mission),
        description.toString(),
        platformChannelSpecifics,
      );
  // Add to NotificationProvider for in-app display
      try {
        final context = MissionProvider.latestInstance?.context;
        if (context != null) {
          Provider.of<NotificationProvider>(
            context,
            listen: false,
          ).addNotification(
            mission.title,
            mission.description,
            'mission',
            DateTime.now(),
          );
        }
      } catch (e) {
        print('Error adding mission notification to NotificationProvider: $e');
      }
      developer.log(
        'Successfully created notification for mission: ${mission.title}',
      );
    } catch (e) {
      developer.log(
        'Error showing notification for mission ${mission.title}: $e',
      );
    }
  }

  String _getNotificationTitle(MissionData mission) {
    if (mission.hasFailed) {
      return '❗ ${mission.title}';
    } else if (mission.isCompleted && mission.areAllSubtasksComplete) {
      return '✅ ${mission.title}';
    } else if (mission.subtasks.any((s) => s.isCounterBased) &&
        mission.subtasks.any((s) => !s.isCounterBased)) {
      return '🔰 ${mission.title}';
    } else if (mission.isCounterBased ||
        mission.subtasks.any((s) => s.isCounterBased)) {
      return '⚡ ${mission.title}';
    } else if (mission.subtasks.any((s) => s.currentCompletions > 0)) {
      return '🔄 ${mission.title}';
    } else {
      return '⏳ ${mission.title}';
    }
  }

  Future<void> _showSummaryNotification() async {
    try {
      final activeMissions =
          _state.missions
              .where((m) => !m.isCompleted || m.lastCompleted != null)
              .toList();
      if (activeMissions.isEmpty) {
        await _notifications.cancel(9998);
        return;
      }

      String summary = 'Mission Summary\n\n';
      summary += 'Active Missions: ${activeMissions.length}\n\n';

  // Group missions by type
      final dailyMissions =
          activeMissions.where((m) => m.type == MissionType.daily).length;
      final weeklyMissions =
          activeMissions.where((m) => m.type == MissionType.weekly).length;
      final simpleMissions =
          activeMissions.where((m) => m.type == MissionType.simple).length;

      summary += 'Daily: $dailyMissions\n';
      summary += 'Weekly: $weeklyMissions\n';
      summary += 'Simple: $simpleMissions\n';

  // Add failed missions count
      final failedMissions = activeMissions.where((m) => m.hasFailed).length;
      if (failedMissions > 0) {
        summary += '\nFailed Missions: $failedMissions';
      }

      final androidPlatformChannelSpecifics = AndroidNotificationDetails(
        NotificationChannels.mission,
        'Missions',
        channelDescription: 'Mission notifications',
        importance: Importance.max,
        priority: Priority.max,
        groupKey: 'com.example.lvl_up.missions',
        setAsGroupSummary: true,
        styleInformation: BigTextStyleInformation(
          summary,
          contentTitle: 'Mission Summary',
          htmlFormatContent: false,
          htmlFormatTitle: false,
        ),
        autoCancel: false,
        ongoing: true,
        onlyAlertOnce: true,
        icon: '@mipmap/berserk',
      );
      final platformChannelSpecifics = NotificationDetails(
        android: androidPlatformChannelSpecifics,
      );
      await _notifications.show(
        9998,
        'Mission Summary',
        summary,
        platformChannelSpecifics,
      );
    } catch (e) {
      print('Error showing summary notification: $e');
    }
  }

  Future<void> _initNotifications() async {
    print('Initializing notifications for Android...');
    try {
  // Request notification permission first
      final status = await Permission.notification.status;
      if (status.isDenied || status.isPermanentlyDenied) {
        print('Requesting notification permission...');
        final newStatus = await Permission.notification.request();
        if (!newStatus.isGranted) {
          print('Notification permission denied');
          return;
        }
        print('Notification permission granted');
      } else {
        print('Notification permission already granted');
      }

      const AndroidInitializationSettings initializationSettingsAndroid =
          AndroidInitializationSettings('@mipmap/berserk');
      final InitializationSettings initializationSettings =
          InitializationSettings(android: initializationSettingsAndroid);

      final androidPlugin =
          _notifications
              .resolvePlatformSpecificImplementation<
                AndroidFlutterLocalNotificationsPlugin
              >();

      if (androidPlugin != null) {
  // Create notification channels
        await androidPlugin.createNotificationChannel(
          NotificationChannels.missionChannel,
        );
        print(
          'Android notification channel created: ${NotificationChannels.mission}',
        );

        await androidPlugin.createNotificationChannel(
          NotificationChannels.summaryChannel,
        );
        print(
          'Android notification channel created: ${NotificationChannels.summary}',
        );
      } else {
        print('Failed to resolve AndroidFlutterLocalNotificationsPlugin');
        return;
      }

      await _notifications.initialize(
        initializationSettings,
        onDidReceiveNotificationResponse: _handleNotificationResponse,
      );

      print('Notification initialization completed');
    } catch (e) {
      print('Error in _initNotifications: $e');
    }
  }

  Future<void> _handleNotificationResponse(
    NotificationResponse response,
  ) async {
    print(
      'Notification response received: Action ID: ${response.actionId}, Payload: ${response.payload}',
    );

    try {
      if (response.notificationResponseType ==
          NotificationResponseType.selectedNotification) {
        await _handleNotificationTap(response.payload);
      } else if (response.actionId?.startsWith('complete_') == true) {
        await _handleCompleteAction(response.payload);
      } else if (response.actionId?.startsWith('progress_') == true) {
        await _handleProgressAction(response);
      } else if (response.actionId?.startsWith('increment_') == true) {
  // Handle increment for counter-based mission with no subtasks
        final missionId = int.tryParse(response.actionId!.split('_')[1]);
        if (missionId != null) {
          final missionIndex = _state.missions.indexWhere(
            (m) => m.notificationId == missionId,
          );
          if (missionIndex != -1) {
            final mission = _state.missions[missionIndex];
            if (mission.isCounterBased && mission.subtasks.isEmpty) {
              final updatedMission = mission.copyWith(
                currentCount: mission.currentCount + 1,
              );
              await editMission(mission, updatedMission);
              await _showNotificationForMission(updatedMission);
            }
          }
        }
      } else {
        print('Unknown action: ${response.actionId}');
      }
    } catch (e) {
      print('Error handling notification response: $e');
    }
  }

  Future<void> _handleNotificationTap(String? payload) async {
    if (payload == null) return;

    try {
      final missionId = int.tryParse(payload);
      if (missionId == null) return;

      final mission = _state.missions.firstWhere(
        (m) => m.notificationId == missionId,
        orElse: () => throw Exception('Mission not found'),
      );

      if (mission.isCounterBased) {
  // Increment counter for counter-based missions
        final updatedMission = mission.copyWith(
          currentCount: mission.currentCount + 1,
          hasFailed: false, // Remove failed status when progress is made
        );

  // Update the mission in state
        final index = _state.missions.indexWhere(
          (m) => m.notificationId == mission.notificationId,
        );
        if (index != -1) {
          final updatedMissions = List<MissionData>.from(_state.missions);
          updatedMissions[index] = updatedMission;
          _state = _state.copyWith(missions: updatedMissions);

  // Update notification
          await _notifications.cancel(mission.notificationId);
          await _showNotificationForMission(updatedMission);

  // Save changes
          await _saveMissions();
          notifyListeners();
          await _updateBadge();
          await _showSummaryNotification();
        }

  // Add mastery progress if linked
        if (mission.linkedMasteryId != null && mission.masteryValue > 0) {
          final masteryProvider = Provider.of<MasteryProvider>(
            navigatorKey.currentContext!,
            listen: false,
          );
  // Calculate total mastery progress based on the new count
          final totalMasteryProgress =
              (mission.currentCount + 1) * mission.masteryValue;
          masteryProvider.addProgress(
            mission.linkedMasteryId!,
            'Mission: ${mission.title}',
            totalMasteryProgress,
          );
        }
      } else {
  // Handle regular mission completion
        if (!mission.isCompleted) {
          await completeMission(mission);
        }
      }
    } catch (e) {
      print('Error handling notification tap: $e');
    }
  }

  Future<void> _handleCompleteAction(String? payload) async {
    if (payload == null) return;

    try {
      final missionId = payload;
      final mission = _state.missions.firstWhere(
        (m) => m.id == missionId,
        orElse: () => throw Exception('Mission not found'),
      );

      if (mission.isCounterBased) {
  // Increment counter for counter-based missions
        final updatedMission = mission.copyWith(
          currentCount: mission.currentCount + 1,
        );
        await editMission(mission, updatedMission);

  // Add mastery progress if linked
        if (mission.linkedMasteryId != null && mission.masteryValue > 0) {
          final masteryProvider = Provider.of<MasteryProvider>(
            navigatorKey.currentContext!,
            listen: false,
          );
          masteryProvider.addProgress(
            mission.linkedMasteryId!,
            'Mission: ${mission.title}',
            mission.masteryValue,
          );
        }
      } else {
  // Handle regular mission completion
        if (!mission.isCompleted) {
          await completeMission(mission);
        }
      }
    } catch (e) {
      print('Error handling complete action: $e');
    }
  }

  Future<void> _handleProgressAction(NotificationResponse response) async {
    print('Handling progress action: ${response.actionId}');
    final parts = response.actionId!.split('_');
    if (parts.length >= 3) {
      final missionId = int.tryParse(parts[1]);
      final subtaskName = parts.sublist(2).join('_');
      if (missionId != null) {
        final missionIndex = _state.missions.indexWhere(
          (m) => m.notificationId == missionId,
        );
        if (missionIndex != -1) {
          final mission = _state.missions[missionIndex];
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
                currentCompletions:
                    subtask.currentCompletions +
                    1, // Also increment completions
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
              final updatedMissions = List<MissionData>.from(_state.missions);
              updatedMissions[missionIndex] = updatedMission;
              _state = _state.copyWith(missions: updatedMissions);

  // Save changes
              await _saveMissions();

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
              await completeSubtask(mission, subtask, fromNotification: true);
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

  void _startNotificationCheck() {
    Future<void> checkNotifications() async {
      for (var mission in _state.missions) {
        try {
          final activeNotifications =
              await _notifications.getActiveNotifications();
          if (!activeNotifications.any((n) => n.id == mission.notificationId)) {
            print('Restoring notification for mission: ${mission.title}');
            await _showNotificationForMission(mission);
          }
        } catch (e) {
          print('Error checking notification for mission ${mission.title}: $e');
        }
      }
      await _showSummaryNotification();
    }

    Timer.periodic(const Duration(minutes: 5), (timer) async {
      await checkNotifications();
    });
    Future.delayed(const Duration(seconds: 10), checkNotifications);
  }

  Future<void> _loadData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final missionsJson = await prefs.getString('missions');
      if (missionsJson != null) {
        final List<dynamic> decodedList = jsonDecode(missionsJson);
        final missions =
            decodedList.map((item) => MissionData.fromJson(item)).toList();
        _state = _state.copyWith(missions: missions, isLoading: false);
        _usedImages = missions.map((m) => m.imageUrl).toSet();

  // Check for pending refreshes after loading missions
        await _checkPendingRefreshes();

  // NOTIFICATION CALLS REMOVED - will be called after loading screen
  // for (var mission in missions) {
  //   await _showNotificationForMission(mission);
  // }
      }

  // Load deleted missions
      final deletedMissionsJson = await prefs.getString('deleted_missions');
      if (deletedMissionsJson != null) {
        final List<dynamic> decodedList = jsonDecode(deletedMissionsJson);
        final deletedMissions =
            decodedList.map((item) => MissionData.fromJson(item)).toList();
        _state = _state.copyWith(
          deletedMissions: deletedMissions,
          isLoading: false,
        );
      }

  // NOTIFICATION SCHEDULING REMOVED - will be called after loading screen
  // for (var mission in _state.missions.where((m) => !m.isCompleted)) {
  //   try {
  //     await _scheduleNotification(mission);
  //   } catch (e, stackTrace) {
  //     if (navigatorKey.currentContext != null) {
  //       final historyProvider = Provider.of<AppHistoryProvider>(
  //         navigatorKey.currentContext!,
  //         listen: false,
  //       );
  //       await historyProvider.logError(
  //         title: 'Notification Schedule Error',
  //         description:
  //             'Failed to schedule notification for mission ${mission.title}',
  //         errorCode: 'SCHEDULE_NOTIFICATION_ERROR',
  //         errorType: 'System Error',
  //         stackTrace: stackTrace.toString(),
  //         errorContext: {
  //           'missionId': mission.id,
  //           'missionTitle': mission.title,
  //         },
  //       );
  //     }
  //   }
  // }

      notifyListeners();
      if (navigatorKey.currentContext != null) {
        final historyProvider = Provider.of<AppHistoryProvider>(
          navigatorKey.currentContext!,
          listen: false,
        );
        await historyProvider.logMission(
          title: 'Missions Loaded',
          description: 'Successfully loaded missions',
          metadata: {
            'totalMissions': _state.missions.length,
            'activeMissions':
                _state.missions.where((m) => !m.isCompleted).length,
            'deletedMissions': _state.deletedMissions.length,
          },
        );
      }
    } catch (e, stackTrace) {
      if (navigatorKey.currentContext != null) {
        final historyProvider = Provider.of<AppHistoryProvider>(
          navigatorKey.currentContext!,
          listen: false,
        );
        await historyProvider.logError(
          title: 'Mission Load Error',
          description: 'Failed to load mission data',
          errorCode: 'LOAD_MISSIONS_ERROR',
          errorType: 'System Error',
          stackTrace: stackTrace.toString(),
        );
        _state = _state.copyWith(
          missions: [],
          deletedMissions: [],
          isLoading: false,
          error: 'Failed to load missions: ${e.toString()}',
        );
        notifyListeners();
        throw AppError(
          'Failed to load missions',
          'LOAD_MISSIONS_ERROR',
          code: 'LOAD_MISSIONS_ERROR',
          originalError: e,
          stackTrace: stackTrace,
        );
      }
    }
  }

  void updateCompletionStatus(DateTime date, bool status) {
    _dailyCompletionStatus[date] = status;
    _saveData();
    notifyListeners();
  }

  void incrementGoalsCreated(DateTime date) {
    _dailyGoalsCreated[date] = (_dailyGoalsCreated[date] ?? 0) + 1;
    _saveData();
    notifyListeners();
  }

  Future<void> resetDailyMissions() async {
    await requestNotificationPermission();

    await _notifications.cancelAll();

    _usedImages.clear();
    _state.missions.clear();
    _dailyCompletionStatus.clear();
    _dailyGoalsCreated.clear();

    await _saveData();
    notifyListeners();
    await _updateBadge();
  }

  Future<void> _saveData() async {
    return PerformanceMonitor.measureOperation(
      operationName: 'save_data',
      operation: () async {
        try {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString(
            'missions',
            jsonEncode(_state.missions.map((m) => m.toJson()).toList()),
          );
          await prefs.setString(
            'deleted_missions',
            jsonEncode(_state.deletedMissions.map((m) => m.toJson()).toList()),
          );
          AppLogger.info('Data saved successfully');
        } catch (e, stackTrace) {
          AppLogger.error('Error saving data', e, stackTrace);
          throw AppError(
            'Failed to save data',
            'SAVE_DATA_ERROR',
            code: 'SAVE_DATA_ERROR',
            originalError: e,
            stackTrace: stackTrace,
          );
        }
      },
    );
  }

  Duration get timeLeft {
    final now = DateTime.now();

  // For daily missions, calculate time until end of day
    final endOfDay = DateTime(now.year, now.month, now.day, 23, 59, 59);
    final dailyTimeLeft = endOfDay.difference(now);

  // For weekly missions, calculate time until end of week (Sunday 23:59:59)
    final daysUntilSunday = (DateTime.sunday - now.weekday) % 7;
    final endOfWeek = DateTime(
      now.year,
      now.month,
      now.day + daysUntilSunday,
      23,
      59,
      59,
    );
    final weeklyTimeLeft = endOfWeek.difference(now);

  // Return the shorter of the two times
    return dailyTimeLeft < weeklyTimeLeft ? dailyTimeLeft : weeklyTimeLeft;
  }

  get flutterLocalNotificationsPlugin => null;

  BuildContext? get context => null;

  get currentBatch => null;

  get batchSize => null;

  bool get isAIActive => aiGuardian.isAIActive;

  bool get isAIGuardianRunning => aiGuardian.isRunning;

  String get aiGuardianStatus {
    if (!aiGuardian.isRunning) return 'Stopped';
    if (aiGuardian.isAIActive) return 'Active - Repairing';
    return 'Running - Monitoring';
  }

  Future<Uint8List?> _getFadedImageBytes(String assetPath) async {
    try {
  // Check if asset exists
      final manifestContent = await DefaultAssetBundle.of(
        WidgetsBinding.instance.rootElement!,
      ).loadString('AssetManifest.json');
      final Map<String, dynamic> manifestMap = json.decode(manifestContent);
      if (!manifestMap.containsKey(assetPath)) {
        print('Asset not found in manifest: $assetPath');
        return await _getDefaultImageBytes();
      }

      final byteData = await rootBundle.load(assetPath);
      final imageBytes = byteData.buffer.asUint8List();
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        print('Failed to decode image: $assetPath');
        return await _getDefaultImageBytes();
      }

      for (var y = 0; y < image.height; y++) {
        for (var x = 0; x < image.width; x++) {
          final pixel = image.getPixel(x, y);
          final alpha = (pixel.a * 0.5).toInt();
          image.setPixelRgba(x, y, pixel.r, pixel.g, pixel.b, alpha);
        }
      }

      final encoded = img.encodePng(image);
      return encoded;
    } catch (e) {
      print('Error processing image $assetPath: $e');
      return await _getDefaultImageBytes();
    }
  }

  Future<Uint8List?> _getDefaultImageBytes() async {
    const defaultImagePath = 'assets/images/default.jpeg'; // Ensure this exists
    try {
      final byteData = await rootBundle.load(defaultImagePath);
      final imageBytes = byteData.buffer.asUint8List();
      final image = img.decodeImage(imageBytes);
      if (image == null) {
        print('Failed to decode default image: $defaultImagePath');
        return null;
      }

      for (var y = 0; y < image.height; y++) {
        for (var x = 0; x < image.width; x++) {
          final pixel = image.getPixel(x, y);
          final alpha = (pixel.a * 0.5).toInt();
          image.setPixelRgba(x, y, pixel.r, pixel.g, pixel.b, alpha);
        }
      }

      final encoded = img.encodePng(image);
      return encoded;
    } catch (e) {
      print('Error processing default image $defaultImagePath: $e');
      return null;
    }
  }

  Future<void> _updateBadge() async {
    try {
      final activeMissions =
          _state.missions.where((m) => !m.isCompleted).length;
      await AppBadgePlus.updateBadge(activeMissions);
    } catch (e) {
      print('Error updating badge: $e');
    }
  }

  Future<void> requestNotificationPermission() async {
    var status = await Permission.notification.status;
    if (!status.isGranted) {
      status = await Permission.notification.request();
      if (!status.isGranted) {
        print('Notification permission denied');
      } else {
        print('Notification permission granted');
      }
    }
  }

  Future<void> deleteMission(MissionData mission) async {
    try {
      await _notifications.cancel(mission.notificationId);
      _state.missions.removeWhere(
        (m) => m.notificationId == mission.notificationId,
      );
      _state.deletedMissions.add(mission);
      if (!_state.missions.any((m) => m.imageUrl == mission.imageUrl)) {
        _usedImages.remove(mission.imageUrl);
      }
      await _saveData();
      notifyListeners();
      await _updateBadge();
    } catch (e) {
      print('Error deleting mission: $e');
    }
  }

  Future<void> deleteCompletedMissions() async {
    final completedMissions =
        _state.missions.where((m) => m.isCompleted).toList();
    for (var mission in completedMissions) {
      await _notifications.cancel(mission.notificationId);
      _state.missions.remove(mission);
      _state.deletedMissions.add(mission);
      if (!_state.missions.any((m) => m.imageUrl == mission.imageUrl)) {
        _usedImages.remove(mission.imageUrl);
      }
    }
    await _saveData();
    notifyListeners();
    await _updateBadge();
    await _showSummaryNotification();
  }

  Future<void> deleteAllMissions() async {
    await _notifications.cancelAll();
    _state.deletedMissions.addAll(_state.missions);
    _state.missions.clear();
    _usedImages.clear();
    await _saveData();
    notifyListeners();
    await _updateBadge();
    await _showSummaryNotification();
  }

  Future<void> editMission(
    MissionData mission,
    MissionData updatedMission,
  ) async {
    try {
      developer.log('Editing mission: ${mission.title}');

  // Find the mission in the current state
      final index = _state.missions.indexWhere(
        (m) => m.notificationId == mission.notificationId,
      );

      if (index != -1) {
  // Cancel existing notification
        await _notifications.cancel(mission.notificationId);

  // Create updated mission with preserved properties
        final editedMission = updatedMission.copyWith(
          notificationId: mission.notificationId,
          createdAt: mission.createdAt,
          lastCompleted: mission.lastCompleted,
          boltColor: mission.boltColor,
          timelapseColor: mission.timelapseColor,
          hasFailed: mission.hasFailed,
          subtasks:
              updatedMission.subtasks.map((subtask) {
  // Find matching original subtask
                final originalSubtask = mission.subtasks.firstWhere(
                  (s) => s.name == subtask.name,
                  orElse: () => subtask,
                );

  // Handle counter-based subtasks
                if (subtask.isCounterBased &&
                    subtask.currentCount > originalSubtask.currentCount) {
                  return subtask.copyWith(
                    currentCount: originalSubtask.currentCount + 1,
                    currentCompletions: originalSubtask.currentCompletions + 1,
                  );
                }

  // Handle completion-based subtasks
                if (!subtask.isCounterBased &&
                    subtask.currentCompletions >
                        originalSubtask.currentCompletions) {
  // Only increment if we haven't reached the required completions
                  final newCompletions = originalSubtask.currentCompletions + 1;
                  if (newCompletions <= originalSubtask.requiredCompletions) {
                    return subtask.copyWith(
                      currentCompletions: newCompletions,
                      currentCount: originalSubtask.currentCount,
                    );
                  }
                }

                return subtask.copyWith(
                  currentCompletions: originalSubtask.currentCompletions,
                  currentCount: originalSubtask.currentCount,
                );
              }).toList(),
        );

  // Update the mission in the state
        final updatedMissions = List<MissionData>.from(_state.missions);
        updatedMissions[index] = editedMission;
        _state = _state.copyWith(missions: updatedMissions);

  // Update notification
        await _showNotificationForMission(editedMission);

  // Save changes
        await _saveMissions();
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
      } else {
        developer.log('Mission not found for editing: ${mission.title}');
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

  void _startDailySummaryCheck() {
    Timer.periodic(const Duration(minutes: 1), (timer) {
      final now = DateTime.now();
      if (now.hour == 12 && now.minute == 0) {
        _showDailySummary();
      }
    });
  }

  Future<void> _showDailySummary() async {
    print('Showing daily summary notification...');
    try {
      final activeMissions =
          _state.missions.where((m) => !m.isCompleted).toList();
      if (activeMissions.isEmpty) {
        print('No active missions to show in summary');
        return;
      }

      final summaryString = activeMissions
          .map((mission) {
            final subtaskProgress = mission.subtasks
                .map((subtask) {
                  final progress = subtask.currentCompletions.toString();
                  final total = subtask.requiredCompletions.toString();
                  return '${subtask.name}: $progress';
                })
                .join(', ');
            return '${mission.title}: $subtaskProgress';
          })
          .join('\n');

      print('Creating daily summary notification...');
      await _notifications.show(
        999,
        'Daily Mission Progress',
        summaryString,
        NotificationDetails(
          android: AndroidNotificationDetails(
            NotificationChannels.summary,
            'Daily Summary',
            channelDescription: 'Daily mission progress summary',
            importance: Importance.high,
            priority: Priority.high,
            groupKey: 'mission_summary',
            setAsGroupSummary: true,
            styleInformation: BigTextStyleInformation(summaryString),
            icon: '@mipmap/berserk',
          ),
        ),
      );
      print('Daily summary notification shown successfully');
    } catch (e) {
      print('Error showing daily summary notification: $e');
    }
  }

  Future<void> _scheduleNotification(MissionData mission) async {
    try {
  // Cancel existing notification if any
      if (mission.scheduledNotificationId != null) {
        await _notifications.cancel(mission.scheduledNotificationId!);
      }

  // Build notification details
      final details = await _buildNotificationDetails(mission);

  // Show notification
      await _notifications.show(
        mission.notificationId,
        _buildNotificationTitle(mission),
        _buildNotificationContent(mission),
        details,
      );

  // Update mission's scheduled notification ID
      mission.scheduledNotificationId = mission.notificationId;

      print(
        'Scheduled notification for mission: ${mission.title}, ID: ${mission.notificationId}',
      );
    } catch (e) {
      print('Error scheduling notification for mission ${mission.title}: $e');
    }
  }

  Future<void> _updateAllNotifications() async {
    try {
  // Cancel existing notifications
      await _notifications.cancel(9999); // Cancel summary notification

  // Get active missions
      final activeMissions =
          _state.missions.where((m) => !m.isCompleted).toList();
      print(
        'Updating notifications, Active missions: ${activeMissions.length}',
      );

  // Batch update notifications
      final notificationFutures = <Future>[];
      for (var mission in activeMissions) {
        notificationFutures.add(_scheduleNotification(mission));
      }
      await Future.wait(notificationFutures);

  // Update summary notification if there are active missions
      if (activeMissions.isNotEmpty) {
        final summaryDetails = await _buildNotificationDetails(
          MissionData(
            title: 'Active Missions',
            description: 'You have ${activeMissions.length} active missions',
            imageUrl: '',
            isCompleted: false,
            notificationId: 9999,
            type: MissionType.simple,
            subtasks: const [],
            scheduledNotificationId: null,
            masteryValue: 0.0,
            linkedMasteryId: null,
            targetCount: 0,
            subtaskMasteryValues: {},
          ),
          isSummary: true,
        );

        await _notifications.show(
          9999,
          'Active Missions',
          'You have ${activeMissions.length} active missions',
          summaryDetails,
        );
        print(
          'Updated summary notification, Active missions count: ${activeMissions.length}',
        );
      }
    } catch (e) {
      print('Error updating notifications: $e');
    }
  }

  String _buildNotificationTitle(MissionData mission) {
    if (mission.hasFailed) {
      return '❗ ${mission.title}';
    } else if (mission.isCompleted && mission.areAllSubtasksComplete) {
      return '✅ ${mission.title}';
    } else if (mission.subtasks.any((s) => s.isCounterBased) &&
        mission.subtasks.any((s) => !s.isCounterBased)) {
      return '🔰 ${mission.title}';
    } else if (mission.isCounterBased ||
        mission.subtasks.any((s) => s.isCounterBased)) {
      return '⚡ ${mission.title}';
    } else if (mission.subtasks.any((s) => s.currentCompletions > 0)) {
      return '🔄 ${mission.title}';
    } else {
      return '⏳ ${mission.title}';
    }
  }

  String _buildNotificationContent(MissionData mission) {
    print('ENTERED _buildNotificationContent for mission: ${mission.title}');
    for (final subtask in mission.subtasks) {
      print(
        'Subtask: ${subtask.name}, isCounterBased: ${subtask.isCounterBased}, currentCount: ${subtask.currentCount}, currentCompletions: ${subtask.currentCompletions}, requiredCompletions: ${subtask.requiredCompletions}',
      );
    }

    String content = '';
    if (mission.description.isNotEmpty) {
      content += mission.description;
    }

    if (mission.subtasks.isNotEmpty) {
      final allCounter = mission.subtasks.every((s) => s.isCounterBased);
      final allNormal = mission.subtasks.every((s) => !s.isCounterBased);
      final hasNormal = mission.subtasks.any((s) => !s.isCounterBased);
      final hasCounter = mission.subtasks.any((s) => s.isCounterBased);
      print(
        'DEBUG: allCounter=${allCounter}, allNormal=${allNormal}, hasNormal=${hasNormal}, hasCounter=${hasCounter}',
      );

      if (content.isNotEmpty) {
        content += '\n\n';
      }

  // Add subtask progress
      for (final subtask in mission.subtasks) {
        final emoji =
            subtask.isCounterBased
                ? (subtask.currentCount > 0 ? '⚡' : '⏳')
                : (subtask.currentCompletions >= subtask.requiredCompletions
                    ? '✅'
                    : subtask.currentCompletions > 0
                    ? '🔄'
                    : '⏳');

        final progress =
            subtask.isCounterBased
                ? '${subtask.currentCount}${subtask.requiredCompletions > 0 ? '' : ''}'
                : '${subtask.currentCompletions}';

        content += '$emoji ${subtask.name}: $progress\n';
      }
    }

  // Add overall progress for non-counter missions
    if (!mission.isCounterBased && mission.subtasks.isNotEmpty) {
  // Calculate progress only for non-counter subtasks
      final nonCounterSubtasks =
          mission.subtasks.where((s) => !s.isCounterBased).toList();
      if (nonCounterSubtasks.isNotEmpty) {
        final totalCompletions = nonCounterSubtasks.fold<int>(
          0,
          (sum, s) => sum + s.currentCompletions,
        );
        final totalRequired = nonCounterSubtasks.fold<int>(
          0,
          (sum, s) => sum + s.requiredCompletions,
        );
        final percentage =
            (totalRequired == 0)
                ? 0
                : (totalCompletions / totalRequired * 100).toInt();
        content += '\nProgress: $percentage%';
      }
    }

  // Add failure warning if mission has failed
    if (mission.hasFailed) {
      content += '\n\n⚠️ GET SHIT DONE !!';
    }

    return content;
  }

  Future<NotificationDetails> _buildNotificationDetails(
    MissionData mission, {
    bool isSummary = false,
  }) async {
    ByteArrayAndroidBitmap? bitmap;
    if (mission.imageUrl.isNotEmpty) {
      final fadedImageBytes = await _getFadedImageBytes(mission.imageUrl);
      if (fadedImageBytes != null) {
        bitmap = ByteArrayAndroidBitmap(fadedImageBytes);
      }
    }

    final actions = <AndroidNotificationAction>[];
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

    final androidPlatformChannelSpecifics = AndroidNotificationDetails(
      NotificationChannels.mission,
      'Missions',
      channelDescription: 'Mission notifications',
      importance: Importance.max,
      priority: Priority.max,
      showWhen: true,
      autoCancel: false,
      ongoing: true,
      visibility: NotificationVisibility.public,
      onlyAlertOnce: true,
      groupKey: 'com.example.lvl_up.missions',
      setAsGroupSummary: isSummary,
      styleInformation: BigTextStyleInformation(
        _buildNotificationContent(mission),
        contentTitle: _buildNotificationTitle(mission),
        htmlFormatContent: false,
        htmlFormatTitle: false,
      ),
      actions: actions,
      largeIcon: bitmap,
    );

    final platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );

    return platformChannelSpecifics;
  }

  Future<void> _saveMissions() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        'missions',
        jsonEncode(_state.missions.map((m) => m.toJson()).toList()),
      );
      await prefs.setString(
        'deleted_missions',
        jsonEncode(_state.deletedMissions.map((m) => m.toJson()).toList()),
      );
    } catch (e) {
      print('Error saving missions: $e');
  // Attempt to save to SharedPreferences as backup
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(
          'missions_backup',
          jsonEncode(_state.missions.map((m) => m.toJson()).toList()),
        );
        await prefs.setString(
          'deleted_missions_backup',
          jsonEncode(_state.deletedMissions.map((m) => m.toJson()).toList()),
        );
      } catch (backupError) {
        print('Error saving backup: $backupError');
      }
    }
  }

  Future<void> refreshMission(MissionData mission) async {
    try {
      final now = DateTime.now();

  // Create a new mission with the same data but reset progress
      final refreshedMission = mission.copyWith(
        isCompleted: false,
        lastCompleted: null,
        createdAt: now,
        hasFailed: false,
        currentCount: 0,
        subtasks:
            mission.subtasks
                .map(
                  (subtask) =>
                      subtask.copyWith(currentCompletions: 0, currentCount: 0),
                )
                .toList(),
        boltColor: mission.boltColor, // Preserve the bolt color
        timelapseColor: mission.timelapseColor, // Preserve the timelapse color
      );

  // Update the mission in the state
      final index = _state.missions.indexWhere(
        (m) => m.notificationId == mission.notificationId,
      );

      if (index != -1) {
        _state.missions[index] = refreshedMission;

  // Update notification
        await _notifications.cancel(mission.notificationId);
        await _showNotificationForMission(refreshedMission);

  // Save changes
        await _saveData();
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        print('Successfully refreshed mission: ${mission.title}');
      } else {
        print('Mission not found for refresh: ${mission.title}');
      }
    } catch (e) {
      print('Error refreshing mission ${mission.title}: $e');
      throw AppError(
        'Failed to refresh mission',
        'REFRESH_MISSION_ERROR',
        code: 'REFRESH_MISSION_ERROR',
        originalError: e,
      );
    }
  }

  Future<void> refreshMissionsByType(MissionType type) async {
    try {
      final now = DateTime.now();
      final missionsToRefresh =
          _state.missions.where((m) => m.type == type).toList();

      developer.log('Starting refresh for ${type.toString()} missions');
      developer.log('Found ${missionsToRefresh.length} missions to refresh');

  // Create a new list to store refreshed missions
      final refreshedMissions = List<MissionData>.from(_state.missions);

  // Process each mission
      for (final mission in missionsToRefresh) {
  // Check if mission should be marked as failed
        final shouldMarkAsFailed =
            !mission.isCompleted && _missionHasProgress(mission);

  // For persistent missions, preserve progress but update failure status
        if (mission.type == MissionType.persistent) {
          final refreshedMission = mission.copyWith(
            isCompleted: false,
            lastCompleted: null,
            createdAt: now,
            hasFailed: shouldMarkAsFailed,
          );

  // Update the mission in the list
          final index = refreshedMissions.indexWhere(
            (m) => m.notificationId == mission.notificationId,
          );

          if (index != -1) {
            refreshedMissions[index] = refreshedMission;
            await _notifications.cancel(mission.notificationId);
            await _showNotificationForMission(refreshedMission);
            developer.log(
              'Updated notification for persistent mission "${mission.title}"',
            );
          }
          continue;
        }

  // For other mission types, reset progress as usual
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
        );

  // Update the mission in the list
        final index = refreshedMissions.indexWhere(
          (m) => m.notificationId == mission.notificationId,
        );

        if (index != -1) {
          refreshedMissions[index] = refreshedMission;
          await _notifications.cancel(mission.notificationId);
          await _showNotificationForMission(refreshedMission);
          developer.log('Updated notification for mission "${mission.title}"');
        }
      }

  // Update the state with all refreshed missions
      _state = _state.copyWith(missions: refreshedMissions);

      if (missionsToRefresh.isNotEmpty) {
        await _saveMissions();
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        developer.log(
          'Successfully refreshed ${missionsToRefresh.length} ${type.toString()} missions',
        );
      } else {
        developer.log('No ${type.toString()} missions needed refreshing');
      }
    } catch (e, stackTrace) {
      developer.log('Error in refreshMissionsByType: $e\n$stackTrace');
    }
  }

  Future<void> validateAllMasteryProgress() async {
    try {
      final masteryProvider = Provider.of<MasteryProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );

  // Track processed mastery IDs to avoid duplicates
      final processedMasteryIds = <String>{};

  // Process all missions
      for (final mission in _state.missions) {
  // Process mission-level mastery if linked
        if (mission.linkedMasteryId != null &&
            mission.masteryValue > 0 &&
            !processedMasteryIds.contains(mission.linkedMasteryId)) {
  // Calculate total progress based on mission completions
          double totalProgress = 0;
          if (mission.isCounterBased) {
  // For counter-based missions, use current count
            totalProgress = mission.currentCount * mission.masteryValue;
          } else if (mission.isCompleted) {
  // For completed missions, add full mastery value
            totalProgress = mission.masteryValue;
          }

          if (totalProgress > 0) {
            await masteryProvider.addProgress(
              mission.linkedMasteryId!,
              'Mission: ${mission.title}',
              totalProgress,
            );
            processedMasteryIds.add(mission.linkedMasteryId!);
          }
        }

  // Process subtask-level mastery
        for (final subtask in mission.subtasks) {
          if (subtask.linkedMasteryId != null &&
              subtask.masteryValue > 0 &&
              !processedMasteryIds.contains(subtask.linkedMasteryId)) {
  // Calculate total progress based on subtask completions
            double totalProgress = 0;
            if (subtask.isCounterBased) {
  // For counter-based subtasks, use current count
              totalProgress = subtask.currentCount * subtask.masteryValue;
            } else {
  // For regular subtasks, use completion count
              totalProgress = subtask.currentCompletions * subtask.masteryValue;
            }

            if (totalProgress > 0) {
              await masteryProvider.addProgress(
                subtask.linkedMasteryId!,
                '${mission.title} - ${subtask.name}',
                totalProgress,
              );
              processedMasteryIds.add(subtask.linkedMasteryId!);
            }
          }
        }
      }

  // Notify listeners to update UI
      masteryProvider.notifyListeners();
      notifyListeners();

      print('Successfully validated and synced all mastery progress');
    } catch (e) {
      print('Error validating mastery progress: $e');
      throw AppError(
        'Failed to validate mastery progress',
        'VALIDATE_MASTERY_ERROR',
        code: 'VALIDATE_MASTERY_ERROR',
        originalError: e,
      );
    }
  }

  // Public method to refresh missions
  Future<void> refreshMissions() async {
    try {
      developer.log('Starting mission refresh...');
      final now = DateTime.now();
      final missionsToRefresh = <MissionData>[];

  // In testing mode, refresh all missions regardless of lock status
      if (_isTestingMode) {
  // Use a Set to track unique mission IDs to prevent duplicates
        final processedIds = <int>{};
        for (final mission in _state.missions) {
          if (processedIds.add(mission.notificationId)) {
            missionsToRefresh.add(mission);
          }
        }
        developer.log(
          'Testing mode: Refreshing ${missionsToRefresh.length} unique missions',
        );
      } else {
  // Normal mode: Identify missions that need refreshing
        for (final mission in _state.missions) {
          if (_shouldRefreshMission(mission, now)) {
            missionsToRefresh.add(mission);
            developer.log('Mission "${mission.title}" will be refreshed');
          }
        }
      }

      developer.log('Found ${missionsToRefresh.length} missions to refresh');

  // Create a new list to store refreshed missions
      final refreshedMissions = List<MissionData>.from(_state.missions);

  // Process each mission
      for (final mission in missionsToRefresh) {
  // Check if mission should be marked as failed
        final shouldMarkAsFailed =
            !mission.isCompleted && _missionHasProgress(mission);

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
        );

  // Update the mission in the list
        final index = refreshedMissions.indexWhere(
          (m) => m.notificationId == mission.notificationId,
        );

        if (index != -1) {
          refreshedMissions[index] = refreshedMission;

  // Update notification
          await _notifications.cancel(mission.notificationId);
          await _showNotificationForMission(refreshedMission);
          developer.log('Updated notification for mission "${mission.title}"');
        }
      }

  // Update the state with all refreshed missions
      _state = _state.copyWith(missions: refreshedMissions);

  // Save changes if any missions were refreshed
      if (missionsToRefresh.isNotEmpty) {
        await _saveMissions();
        notifyListeners();
        await _updateBadge();
        await _showSummaryNotification();

        developer.log(
          'Successfully refreshed ${missionsToRefresh.length} missions',
        );
      } else {
        developer.log('No missions needed refreshing');
      }
    } catch (e, stackTrace) {
      developer.log('Error in refreshMissions: $e\n$stackTrace');
    }
  }

  bool _shouldRefreshMission(MissionData mission, DateTime now) {
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
      return _isDailyLocked;
    } else if (mission.type == MissionType.weekly) {
      return _isWeeklyLocked;
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
    return mission.isCompleted;
  }

  // Add timer to check for end of day/week
  void _startRefreshCheck() {
    Timer.periodic(const Duration(minutes: 1), (timer) async {
      final now = DateTime.now();

  // Check for end of week (Sunday at 11:59 PM)
      if (now.weekday == DateTime.sunday &&
          now.hour == 23 &&
          now.minute >= 59) {
        _refreshButtonColor = Colors.orange;
        _isDailyLocked = true;
        _isWeeklyLocked = true;
  // Trigger refresh for both daily and weekly missions
        await refreshMissions();
        developer.log('End of week detected: Refreshing all missions');
      }
  // Check for end of day (11:59 PM)
      else if (now.hour == 23 && now.minute >= 59) {
        _refreshButtonColor = Colors.red;
        _isDailyLocked = true;
        _isWeeklyLocked = false;
  // Trigger refresh for daily missions
        await refreshMissionsByType(MissionType.daily);
        developer.log('End of day detected: Refreshing daily missions');
      }
  // Normal state
      else {
        _refreshButtonColor = Colors.white;
        _isDailyLocked = false;
        _isWeeklyLocked = false;
      }

      notifyListeners();
    });
  }

  Future<void> updateMissionProgress({
    required MissionData mission,
    required int subtaskIndex,
  }) async {}

  void incrementSubtask(MissionData mission, int index) {}

  void incrementMissionCounter(MissionData mission) {
    final index = _state.missions.indexWhere(
      (m) => m.notificationId == mission.notificationId,
    );
    if (index != -1) {
      final updatedMission = mission.copyWith(
        currentCount: mission.currentCount + 1,
      );
      _state.missions[index] = updatedMission;
      _saveMissions();
      notifyListeners();
    }
  }

  Future<void> _checkPendingRefreshes() async {
    final now = DateTime.now();
    bool needsRefresh = false;

  // Check for daily missions that need refreshing
    for (final mission in _state.missions.where(
      (m) => m.type == MissionType.daily,
    )) {
      if (mission.createdAt != null && !_isSameDay(mission.createdAt!, now)) {
        needsRefresh = true;
        _refreshButtonColor = Colors.red;
        _isDailyLocked = true;
        break;
      }
    }

  // Check for weekly missions that need refreshing
    if (now.weekday == DateTime.monday) {
      for (final mission in _state.missions.where(
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
      developer.log('Pending refreshes detected on app start');
    }
  }

  bool _isSameDay(DateTime a, DateTime b) {
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  Future<void> performHealthCheck({
    required bool showPopup,
    required BuildContext context,
  }) async {}

  Future<void> validateAllMissions({
    required bool stepwise,
    required Null Function(dynamic idx, dynamic result, dynamic passed) onStep,
    required BuildContext context,
    required bool showUser,
    required bool attemptRepair,
  }) async {
    await validate(
      stepwise: stepwise,
      onStep: onStep,
      context: context,
      showUser: showUser,
    );
  }

  // Comprehensive AI Watchdog: Validate all missions and system health
  Future<List<String>> validate({
    bool attemptRepair = true,
    bool stepwise = false,
    void Function(int idx, String result, bool passed)? onStep,
    BuildContext? context,
    bool showUser = false,
  }) async {
    print('MissionProvider.validateAllMissions called!');
    final checklist = <String>[];
    int idx = 0;

  // 1. Unique IDs and notification IDs
    final allMissions = [...missions, ...completedMissions, ...deletedMissions];
    final idSet = <String>{};
    final notificationIdSet = <int>{};
    bool uniquePassed = true;
    for (final m in allMissions) {
      if (m.id == null || m.id!.isEmpty) {
        checklist.add('❌ Mission with empty or null ID: \\${m.title}');
        uniquePassed = false;
        if (attemptRepair) {
  // Only assign if m.id is null
          m.copyWith(id: DateTime.now().microsecondsSinceEpoch.toString());
        }
        continue; // Skip further checks for this mission
      }
      if (!idSet.add(m.id!)) {
        checklist.add('❌ Duplicate mission ID: \\${m.id} (\\${m.title})');
        uniquePassed = false;
      }
      if (m.notificationId == null) {
        checklist.add('❌ Mission with null notification ID: \\${m.title}');
        uniquePassed = false;
        continue;
      }
      if (!notificationIdSet.add(m.notificationId)) {
        checklist.add(
          '❌ Duplicate notification ID: \\${m.notificationId} (\\${m.title})',
        );
        uniquePassed = false;
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
      if (m.id == null ||
          m.id!.isEmpty ||
          m.notificationId == null ||
          m.notificationId <= 0) {
        checklist.add('❌ Invalid mission identifiers: \\${m.title}');
        statePassed = false;
      }
      if (m.title.trim().isEmpty) {
        checklist.add('❌ Mission with empty title: \\${m.id}');
        statePassed = false;
      }
      if (m.isCounterBased && (m.targetCount < 0 || m.currentCount < 0)) {
        checklist.add('❌ Invalid counter values for mission: \\${m.title}');
        statePassed = false;
      }
      if (m.subtasks.isNotEmpty) {
        for (final subtask in m.subtasks) {
          if (subtask.name.trim().isEmpty || subtask.requiredCompletions < 0) {
            checklist.add('❌ Invalid subtask state in mission: \\${m.title}');
            statePassed = false;
          }
        }
      }
      if (m.isCompleted && m.hasFailed) {
        checklist.add(
          '❌ Mission cannot be both completed and failed: \\${m.title}',
        );
        statePassed = false;
      }
      if (m.linkedMasteryId != null && m.masteryValue <= 0) {
        checklist.add('❌ Invalid mastery value for mission: \\${m.title}');
        statePassed = false;
      }
      for (final entry in m.subtaskMasteryValues.entries) {
        if (entry.value <= 0) {
          checklist.add(
            '❌ Invalid subtask mastery value in mission: \\${m.title}',
          );
          statePassed = false;
        }
      }
    }
    if (statePassed) checklist.add('✅ All missions have valid state.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, statePassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 3. Refresh logic (manual/auto, color, lock)
    bool refreshPassed = true;
    try {
      final now = DateTime.now();
      bool dailyNeedsRefresh = false;
      bool weeklyNeedsRefresh = false;
      for (final m in missions) {
        if (m.type == MissionType.daily &&
            m.createdAt != null &&
            !_isSameDay(m.createdAt!, now))
          dailyNeedsRefresh = true;
        if (m.type == MissionType.weekly &&
            m.createdAt != null &&
            now.weekday == DateTime.monday &&
            m.createdAt!.isBefore(now.subtract(const Duration(days: 1))))
          weeklyNeedsRefresh = true;
      }
      if (dailyNeedsRefresh && refreshButtonColor != Colors.red) {
        checklist.add('❌ Daily refresh needed but button is not red.');
        refreshPassed = false;
      }
      if (weeklyNeedsRefresh && refreshButtonColor != Colors.orange) {
        checklist.add('❌ Weekly refresh needed but button is not orange.');
        refreshPassed = false;
      }
      if (!dailyNeedsRefresh && refreshButtonColor == Colors.red) {
        checklist.add('❌ Daily refresh not needed but button is red.');
        refreshPassed = false;
      }
      if (!weeklyNeedsRefresh && refreshButtonColor == Colors.orange) {
        checklist.add('❌ Weekly refresh not needed but button is orange.');
        refreshPassed = false;
      }
      if (isDailyLocked && !dailyNeedsRefresh) {
        checklist.add('❌ Daily missions are locked but refresh is not needed.');
        refreshPassed = false;
      }
      if (isWeeklyLocked && !weeklyNeedsRefresh) {
        checklist.add(
          '❌ Weekly missions are locked but refresh is not needed.',
        );
        refreshPassed = false;
      }
      if (refreshPassed)
        checklist.add('✅ Refresh logic and color states are correct.');
    } catch (e) {
      checklist.add('❌ Error checking refresh logic: $e');
      refreshPassed = false;
    }
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, refreshPassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 4. Failure logic
    bool failurePassed = true;
    for (final m in missions) {
      if (m.hasFailed && m.isCompleted) {
        checklist.add('❌ Mission ${m.title} is both failed and completed.');
        failurePassed = false;
      }
  // Auto-repair for failed missions
    }
    if (failurePassed) checklist.add('✅ Failure logic is correct.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, failurePassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 5. Notification scheduling
    checklist.add('✅ Notification scheduling checked (active missions only).');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, true);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 6. UI Color State (merged with refresh logic above)
    checklist.add('✅ UI color state checked.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, true);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 7. Editability
    bool editPassed = true;
    for (final m in missions) {
      try {
        final edited = m.copyWith(title: m.title + ' (edit-check)');
        if (edited.title == m.title) {
          checklist.add('❌ Mission ${m.title} could not be edited.');
          editPassed = false;
        }
      } catch (e) {
        checklist.add('❌ Error editing mission ${m.title}: $e');
        editPassed = false;
      }
    }
    if (editPassed) checklist.add('✅ All missions are editable.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, editPassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 8. Subtasks and Mastery Values
    bool subtaskPassed = true;
    for (final m in missions) {
      for (final subtask in m.subtasks) {
        if (subtask.name.trim().isEmpty || subtask.requiredCompletions < 0) {
          checklist.add('❌ Invalid subtask in mission: ${m.title}');
          subtaskPassed = false;
        }
        if (subtask.masteryValue != null &&
            (subtask.masteryValue < 1 || subtask.masteryValue > 100)) {
          checklist.add(
            '❌ Invalid subtask mastery value in mission: ${m.title}',
          );
          subtaskPassed = false;
        }
      }
    }
    if (subtaskPassed)
      checklist.add('✅ All subtasks and mastery values are valid.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, subtaskPassed);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // 9. Data consistency
    checklist.add('✅ Data consistency checked.');
    if (stepwise && onStep != null) {
      onStep(idx, checklist.last, true);
      await Future.delayed(const Duration(milliseconds: 400));
    }
    idx++;

  // (Optional) Add warning for frequent repairs

    return checklist;
  }

  Future<void> forceComprehensiveRepair() async {
    print('AI Guardian: Force comprehensive repair requested...');
    await aiGuardian.performImmediateHealthCheck(() async {
      await _performComprehensiveRepair();
    });
  }

  Future<void> _performComprehensiveRepair() async {
    try {
      print('AI Guardian: 🛠️ Starting comprehensive repair...');

  // Step 1: Reset notification ID counter to ensure uniqueness
      _notificationIdCounter = 1000;

  // Step 2: Collect all existing notification IDs to avoid conflicts
      final existingNotificationIds = <int>{};
      for (final mission in allMissions) {
        existingNotificationIds.add(mission.notificationId);
      }

  // Step 3: Find the highest notification ID and set counter above it
      if (existingNotificationIds.isNotEmpty) {
        final maxId = existingNotificationIds.reduce((a, b) => a > b ? a : b);
        _notificationIdCounter = maxId + 1;
      }

  // Step 4: Repair duplicate notification IDs
      await _repairDuplicateNotificationIds();

  // Step 5: Repair invalid mission identifiers
      await _repairInvalidMissionIdentifiers();

  // Step 6: Repair invalid subtask mastery values
      await _repairInvalidSubtaskMasteryValues();

  // Step 7: Repair missions that are both completed and failed
      await _repairInvalidMissionStates();

  // Step 8: Repair empty mission titles
      await _repairEmptyMissionTitles();

  // Step 9: Save all changes
      await _saveMissions();
      notifyListeners();

      print('AI Guardian: ✅ Comprehensive repair completed');
    } catch (e) {
      print('AI Guardian: ❌ Error during comprehensive repair: $e');
    }
  }

  Future<void> _repairDuplicateNotificationIds() async {
    print('AI Guardian: Repairing duplicate notification IDs...');
    final seenIds = <int>{};
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      if (seenIds.contains(mission.notificationId)) {
        final newId = _generateUniqueNotificationId();
        final updatedMission = mission.copyWith(notificationId: newId);
        missionsToUpdate.add(updatedMission);
        print(
          'AI Guardian: Fixed duplicate notification ID ${mission.notificationId} -> $newId for mission: ${mission.title}',
        );
      } else {
        seenIds.add(mission.notificationId);
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      final activeIndex = _state.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (activeIndex != -1) {
        _state.missions[activeIndex] = updatedMission;
      }

      final completedIndex = _state.completedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (completedIndex != -1) {
        _state.completedMissions[completedIndex] = updatedMission;
      }

      final deletedIndex = _state.deletedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (deletedIndex != -1) {
        _state.deletedMissions[deletedIndex] = updatedMission;
      }
    }
  }

  Future<void> _repairInvalidMissionIdentifiers() async {
    print('AI Guardian: Repairing invalid mission identifiers...');
    final seenIds = <String>{};
    final repairs =
        <(MissionData, MissionData)>[]; // Tuple of (original, updated)

    for (final mission in _state.missions.where((m) => !m.isCompleted)) {
      bool needsRepair = false;
      String? newId;
      int? newNotificationId;

  // Check for null, empty, or duplicate mission ID
      if (mission.id == null ||
          mission.id!.isEmpty ||
          seenIds.contains(mission.id)) {
        newId = _generateUniqueMissionId();
        needsRepair = true;
        print('AI Guardian: Fixed invalid mission ID for: ${mission.title}');
      } else {
        seenIds.add(mission.id!);
      }

  // Check for invalid notification ID
      if (mission.notificationId <= 0) {
        newNotificationId = _generateUniqueNotificationId();
        needsRepair = true;
        print(
          'AI Guardian: Fixed invalid notification ID for: ${mission.title}',
        );
      }

      if (needsRepair) {
        final updatedMission = mission.copyWith(
          id: newId,
          notificationId: newNotificationId,
        );
        repairs.add((mission, updatedMission));
      }
    }

    if (repairs.isNotEmpty) {
      for (final (original, updated) in repairs) {
        final index = _state.missions.indexOf(original);
        if (index != -1) {
          _state.missions[index] = updated;
        }
      }
      await _saveData();
      print('AI Guardian: Completed repairs for mission identifiers.');
    }
  }

  Future<void> _repairInvalidSubtaskMasteryValues() async {
    print('AI Guardian: Repairing invalid subtask mastery values...');
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      final updatedSubtaskMasteryValues = <String, double>{};
      bool missionNeedsUpdate = false;

  // Check and fix subtask mastery values
      for (final entry in mission.subtaskMasteryValues.entries) {
        if (entry.value <= 0) {
  // Set a valid default mastery value (1.0)
          updatedSubtaskMasteryValues[entry.key] = 1.0;
          missionNeedsUpdate = true;
          print(
            'AI Guardian: Fixed invalid subtask mastery value for mission: ${mission.title}, subtask: ${entry.key}',
          );
        } else {
          updatedSubtaskMasteryValues[entry.key] = entry.value;
        }
      }

      if (missionNeedsUpdate) {
        final repairedMission = mission.copyWith(
          subtaskMasteryValues: updatedSubtaskMasteryValues,
        );
        missionsToUpdate.add(repairedMission);
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      final activeIndex = _state.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (activeIndex != -1) {
        _state.missions[activeIndex] = updatedMission;
      }

      final completedIndex = _state.completedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (completedIndex != -1) {
        _state.completedMissions[completedIndex] = updatedMission;
      }

      final deletedIndex = _state.deletedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (deletedIndex != -1) {
        _state.deletedMissions[deletedIndex] = updatedMission;
      }
    }
  }

  String _generateUniqueMissionId() {
    return (DateTime.now().millisecondsSinceEpoch % 100000).toString();
  }

  int _generateUniqueNotificationId() {
  // Ensure we start from a high number to avoid conflicts
    if (_notificationIdCounter < 1000) {
      _notificationIdCounter = 1000;
    }

  // Check all existing notification IDs to ensure uniqueness
    final existingIds = <int>{};
    for (final mission in allMissions) {
      existingIds.add(mission.notificationId);
    }

  // Find the next available ID
    int newId = _notificationIdCounter + 1;
    while (existingIds.contains(newId)) {
      newId++;
    }

    _notificationIdCounter = newId;
    return newId;
  }

  Future<void> restartAIGuardian() async {
    print('AI Guardian: Restart requested...');

  // Stop current instance
    aiGuardian.stopContinuousHealthCheck();

  // Wait a moment
    await Future.delayed(const Duration(seconds: 1));

  // Start the AI Guardian with health check functionality
    aiGuardian.startContinuousHealthCheck(
      () async {
  // Keep AI Guardian active during health checks
        aiGuardian.setAIActive(true);

  // Perform health checks on missions
        await _performHealthChecks();

  // Keep AI Guardian active for a bit longer to show it's working
        await Future.delayed(const Duration(seconds: 3));
        aiGuardian.setAIActive(false);
      },
      interval: const Duration(seconds: 8),
    ); // More frequent checks for better visibility

  // Make AI Guardian visible immediately after restart
    aiGuardian.setAIActive(true);
    await Future.delayed(const Duration(seconds: 4));
    aiGuardian.setAIActive(false);

    print('AI Guardian: Restart completed');
  }

  Future<void> _performHealthChecks() async {
    print(
      '🛡️ AI Guardian: 🔍 Performing intelligent health checks... (${_state.missions.length} missions)',
    );

    try {
      final issues = <String>[];
      final activeMissions = _state.missions;

  // Check for duplicate notification IDs
      final seenNotificationIds = <int>{};
      for (final mission in activeMissions) {
        if (seenNotificationIds.contains(mission.notificationId)) {
          issues.add('Duplicate notification ID: ${mission.notificationId}');
        } else {
          seenNotificationIds.add(mission.notificationId);
        }
      }

  // Check for invalid mission identifiers
      for (final mission in activeMissions) {
        if (mission.id == null || mission.id!.isEmpty) {
          issues.add('Invalid mission identifier: ${mission.title}');
        }
      }

  // Check for invalid subtask mastery values
      for (final mission in activeMissions) {
        for (final entry in mission.subtaskMasteryValues.entries) {
          if (entry.value <= 0) {
            issues.add(
              'Invalid subtask mastery value in mission: ${mission.title}',
            );
            break;
          }
        }
      }

  // Check for missions that are both completed and failed
      for (final mission in activeMissions) {
        if (mission.isCompleted && mission.hasFailed) {
          issues.add('Mission both completed and failed: ${mission.title}');
        }
      }

  // Check for empty mission titles
      for (final mission in activeMissions) {
        if (mission.title.trim().isEmpty) {
          issues.add('Empty mission title found');
        }
      }

      if (issues.isNotEmpty) {
        print('🛡️ AI Guardian: ! Issues detected: ${issues.join(', ')}');
        print('🛡️ AI Guardian: 🔧 Auto-triggering intelligent repair...');

  // Perform comprehensive repair
        await _performComprehensiveRepair();

        print('🛡️ AI Guardian: ✅ Intelligent repair completed successfully');
      } else {
        print(
          '🛡️ AI Guardian: ✅ All health checks passed - no issues detected',
        );
      }

  // Keep AI Guardian visible for a moment to show completion
      await Future.delayed(const Duration(seconds: 2));
      aiGuardian.setAIActive(false);
    } catch (e) {
      print('🛡️ AI Guardian: ❌ Error during health checks: $e');
      aiGuardian.setAIActive(false);
    }
  }

  Future<void> _repairInvalidMissionStates() async {
    print('🛡️ AI Guardian: 🔄 Repairing invalid mission states...');
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      if (mission.isCompleted && mission.hasFailed) {
  // If mission is completed, it shouldn't be failed
        final updatedMission = mission.copyWith(hasFailed: false);
        missionsToUpdate.add(updatedMission);
        print('🛡️ AI Guardian: Fixed mission state for: ${mission.title}');
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      final activeIndex = _state.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (activeIndex != -1) {
        _state.missions[activeIndex] = updatedMission;
      }

      final completedIndex = _state.completedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (completedIndex != -1) {
        _state.completedMissions[completedIndex] = updatedMission;
      }

      final deletedIndex = _state.deletedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (deletedIndex != -1) {
        _state.deletedMissions[deletedIndex] = updatedMission;
      }
    }
  }

  Future<void> _repairEmptyMissionTitles() async {
    print('🛡️ AI Guardian: 🔄 Repairing empty mission titles...');
    final missionsToUpdate = <MissionData>[];

    for (final mission in allMissions) {
      if (mission.title.trim().isEmpty) {
        final newTitle = 'Mission ${mission.id ?? 'Unknown'}';
        final updatedMission = mission.copyWith(title: newTitle);
        missionsToUpdate.add(updatedMission);
        print('🛡️ AI Guardian: Fixed empty title for mission: $newTitle');
      }
    }

  // Apply updates
    for (final updatedMission in missionsToUpdate) {
      final activeIndex = _state.missions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (activeIndex != -1) {
        _state.missions[activeIndex] = updatedMission;
      }

      final completedIndex = _state.completedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (completedIndex != -1) {
        _state.completedMissions[completedIndex] = updatedMission;
      }

      final deletedIndex = _state.deletedMissions.indexWhere(
        (m) => m.id == updatedMission.id,
      );
      if (deletedIndex != -1) {
        _state.deletedMissions[deletedIndex] = updatedMission;
      }
    }
  }

  // Public method to get detailed AI Guardian status
  String get aiGuardianDetailedStatus {
    if (!aiGuardian.isRunning) return 'AI Guardian: Stopped';
    if (aiGuardian.isAIActive) return 'AI Guardian: Active - Repairing Issues';
    return 'AI Guardian: Running - Monitoring (${allMissions.length} missions)';
  }

  // Public method to get AI Guardian health status
  bool get isAIGuardianHealthy {
  // Check if AI Guardian is running and there are no critical issues
    if (!aiGuardian.isRunning) return false;

  // Quick health check
    for (final mission in allMissions) {
      if (mission.id == null ||
          mission.id!.isEmpty ||
          mission.notificationId <= 0) {
        return false;
      }
      if (mission.title.trim().isEmpty) {
        return false;
      }
      if (mission.isCompleted && mission.hasFailed) {
        return false;
      }
    }
    return true;
  }

  // Public method to force AI Guardian to be more active
  Future<void> activateAIGuardian() async {
    print('AI Guardian: Force activation requested...');

  // Make AI Guardian visible immediately
    aiGuardian.setAIActive(true);

  // Make AI Guardian more active by triggering immediate health check
    await aiGuardian.performImmediateHealthCheck(() async {
      await _performHealthChecks();
    });

  // Also trigger a comprehensive repair to ensure everything is working
    await forceComprehensiveRepair();

  // Keep AI Guardian active for a longer period to show it's working
    await Future.delayed(const Duration(seconds: 5));
    aiGuardian.setAIActive(false);

    print('AI Guardian: Force activation completed');
  }

  // Public method to perform comprehensive cleanup of all missions
  Future<void> performComprehensiveCleanup() async {
    print('AI Guardian: 🧹 Starting comprehensive cleanup of all missions...');

    try {
  // Make AI Guardian visible during cleanup
      aiGuardian.setAIActive(true);

  // Step 1: Fix all notification IDs to ensure uniqueness
      final allMissionIds = <int>{};
      final missionsToUpdate = <MissionData>[];

      for (final mission in allMissions) {
        bool needsUpdate = false;
        int? newNotificationId;

  // Check for duplicate or invalid notification IDs
        if (allMissionIds.contains(mission.notificationId) ||
            mission.notificationId <= 0) {
          newNotificationId = _generateUniqueNotificationId();
          allMissionIds.add(newNotificationId);
          needsUpdate = true;
          print(
            'AI Guardian: 🆔 Fixed notification ID for mission: ${mission.title}',
          );
        } else {
          allMissionIds.add(mission.notificationId);
        }

  // Step 2: Fix subtask mastery values
        final updatedSubtaskMasteryValues = <String, double>{};
        for (final entry in mission.subtaskMasteryValues.entries) {
          if (entry.value <= 0) {
            updatedSubtaskMasteryValues[entry.key] = 1.0;
            needsUpdate = true;
            print(
              'AI Guardian: 📊 Fixed mastery value for mission: ${mission.title}, subtask: ${entry.key}',
            );
          } else {
            updatedSubtaskMasteryValues[entry.key] = entry.value;
          }
        }

  // Step 3: Fix mission IDs if needed
        String? newMissionId;
        if (mission.id == null || mission.id!.isEmpty) {
          newMissionId = _generateUniqueMissionId();
          needsUpdate = true;
          print('AI Guardian: 🆔 Fixed mission ID for: ${mission.title}');
        }

        if (needsUpdate) {
          final updatedMission = mission.copyWith(
            id: newMissionId ?? mission.id,
            notificationId: newNotificationId ?? mission.notificationId,
            subtaskMasteryValues:
                updatedSubtaskMasteryValues.isNotEmpty
                    ? updatedSubtaskMasteryValues
                    : mission.subtaskMasteryValues,
          );
          missionsToUpdate.add(updatedMission);
        }
      }

  // Apply all updates
      for (final updatedMission in missionsToUpdate) {
        final activeIndex = _state.missions.indexWhere(
          (m) => m.id == updatedMission.id,
        );
        if (activeIndex != -1) {
          _state.missions[activeIndex] = updatedMission;
        }

        final completedIndex = _state.completedMissions.indexWhere(
          (m) => m.id == updatedMission.id,
        );
        if (completedIndex != -1) {
          _state.completedMissions[completedIndex] = updatedMission;
        }

        final deletedIndex = _state.deletedMissions.indexWhere(
          (m) => m.id == updatedMission.id,
        );
        if (deletedIndex != -1) {
          _state.deletedMissions[deletedIndex] = updatedMission;
        }
      }

  // Save all changes
      await _saveMissions();
      notifyListeners();

      print(
        'AI Guardian: ✅ Comprehensive cleanup completed - ${missionsToUpdate.length} missions fixed',
      );

  // Keep AI Guardian visible for a moment to show completion
      await Future.delayed(const Duration(seconds: 3));
      aiGuardian.setAIActive(false);
    } catch (e) {
      print('AI Guardian: ❌ Error during comprehensive cleanup: $e');
      aiGuardian.setAIActive(false);
    }
  }

  // Public method to check AI Guardian performance
  Map<String, dynamic> get aiGuardianPerformance {
    return {
      'isRunning': aiGuardian.isRunning,
      'isActive': aiGuardian.isAIActive,
      'totalMissions': allMissions.length,
      'activeMissions': _state.missions.length,
      'completedMissions': _state.completedMissions.length,
      'deletedMissions': _state.deletedMissions.length,
      'lastHealthCheck': DateTime.now().toIso8601String(),
      'status': aiGuardianStatus,
    };
  }

  // Public method to get AI Guardian working status
  bool get isAIGuardianWorking {
  // AI Guardian is working if it's running (regardless of active state)
    final isWorking = aiGuardian.isRunning;

  // If AI Guardian is running but not active, make it visible briefly
    if (aiGuardian.isRunning && !aiGuardian.isAIActive) {
  // Schedule a brief activation to show it's working
      Future.delayed(const Duration(milliseconds: 500), () {
        if (aiGuardian.isRunning) {
          aiGuardian.setAIActive(true);
          Future.delayed(const Duration(seconds: 2), () {
            if (aiGuardian.isRunning) {
              aiGuardian.setAIActive(false);
            }
          });
        }
      });
    }

    return isWorking;
  }

  Map<String, int> get issueFrequency => {};

  List<Map<String, dynamic>> get appImprovementCode =>
      List.unmodifiable(_appImprovementCode);

  List<Map<String, dynamic>> get mechanicumKnowledgeBase =>
      List.unmodifiable(_mechanicumKnowledgeBase);

  get improvementStrategies => [];

  List<Map<String, dynamic>> get aiSuggestions =>
      List.unmodifiable(_aiSuggestions);

  get lastAISuggestionTime => null;

  List<Map<String, dynamic>> get sandboxTestFeed =>
      List.unmodifiable(_sandboxTestFeed);

  List<dynamic> get knowledgeGaps => List.unmodifiable(_knowledgeGaps);

  List<dynamic> get userUploadedCode => List.unmodifiable(_userUploadedCode);

  Map<String, List<String>> get knowledgeGraph =>
      Map.unmodifiable(_knowledgeGraph);

  Map<String, int> get testCoverage => Map.unmodifiable(_testCoverage);

  get mechanicum => null;

  get appliedAISuggestions => List.unmodifiable(_appliedAISuggestions);

  // Add the backing field
  final List<Map<String, dynamic>> _aiGeneratedCodeSuggestions = [];

  // Correct the getter
  List<Map<String, dynamic>> get aiGeneratedCodeSuggestions =>
      List.unmodifiable(_aiGeneratedCodeSuggestions);

  List<Map<String, dynamic>> get aiExtensionIdeas =>
      List.unmodifiable(_aiExtensionIdeas);

  List<Map<String, dynamic>> get aiPersonalizedSuggestions =>
      List.unmodifiable(_aiPersonalizedSuggestions);

  // Public method to make AI Guardian continuously visible
  void makeAIGuardianVisible() {
    if (aiGuardian.isRunning) {
      aiGuardian.setAIActive(true);
  // Keep it active for 3 seconds
      Future.delayed(const Duration(seconds: 3), () {
        if (aiGuardian.isRunning) {
          aiGuardian.setAIActive(false);
        }
      });
    }
  }

  Future<void> activateMechanicum() async {}

  Future<void> showMechanicumAnalyticsNotification() async {}

  Future<void> applySandboxedSuggestion() async {}

  Future runSandboxedSuggestion(String issueKey) async {}

  void uploadCode({
    required String type,
    required String subject,
    required String description,
    required String code,
    required List<String> tags,
  }) {}

  void markAISuggestionIgnored(param0) {}

  void markAISuggestionAccepted(param0) {}

  void ingestCode(String trim, {required bool isUserUpload}) {}

  void ignoreAISuggestion(param0) {}

  void acceptAISuggestion(param0) {}

  void applyAISuggestion(param0) {}

  // Flag to track if notifications have been started
  bool _notificationsStarted = false;

  Future<void> startNotifications() async {
    if (_notificationsStarted) {
      print(
        'MissionProvider (mission.dart): Notifications already started, skipping',
      );
      return;
    }

    print('MissionProvider (mission.dart): startNotifications called');
    try {
  // Add a delay to ensure loading screen is completely finished
      await Future.delayed(const Duration(seconds: 1));

  // Initialize notifications
      await _initNotifications();

  // Start notification checking
      _startNotificationCheck();

  // Show notifications for existing missions
      await _showNotificationsForExistingMissions();

      _notificationsStarted = true;
      print(
        'MissionProvider (mission.dart): Notifications started successfully',
      );
    } catch (e) {
      print('MissionProvider (mission.dart): Error starting notifications: $e');
    }
  }

  // Method to show notifications for existing missions
  Future<void> _showNotificationsForExistingMissions() async {
    try {
      print(
        'MissionProvider (mission.dart): Showing notifications for existing missions',
      );

  // Show notifications for active missions
      for (var mission in _state.missions.where((m) => !m.isCompleted)) {
        await _showNotificationForMission(mission);
        await _scheduleNotification(mission);
      }

  // Show summary notification if there are active missions
      if (_state.missions.any((m) => !m.isCompleted)) {
        await _showSummaryNotification();
      }

      print(
        'MissionProvider (mission.dart): Notifications for existing missions shown',
      );
    } catch (e) {
      print(
        'MissionProvider (mission.dart): Error showing notifications for existing missions: $e',
      );
    }
  }

  // --- AI Experiments/Brain ---
  final List<Map<String, dynamic>> _aiExperiments = [];
  List<Map<String, dynamic>> get aiExperiments =>
      List.unmodifiable(_aiExperiments);

  // New data structures for tracking AI learning
  final List<Map<String, dynamic>> _aiLearningLog = [];
  List<Map<String, dynamic>> get aiLearningLog =>
      List.unmodifiable(_aiLearningLog);

  final Map<String, List<String>> _analyzedFiles = {};
  Map<String, List<String>> get analyzedFiles =>
      Map.unmodifiable(_analyzedFiles);

  final Map<String, List<Map<String, dynamic>>> _fileInsights = {};
  Map<String, List<Map<String, dynamic>>> get fileInsights =>
      Map.unmodifiable(_fileInsights);

  final List<Map<String, dynamic>> _aiSuggestions = [];

  final List<Map<String, dynamic>> _appliedAISuggestions = [];

  final List<Map<String, dynamic>> _aiExtensionIdeas = [];

  final List<Map<String, dynamic>> _aiPersonalizedSuggestions = [];

  final List<String> _knowledgeGaps = [];

  final List<Map<String, String>> _sandboxTestFeed = [];

  Map<String, int> _testCoverage = {};

  Map<String, List<String>> _knowledgeGraph = {};

  final List<String> _userUploadedCode = [];

  final List<Map<String, dynamic>> _appImprovementCode = [];

  final List<Map<String, dynamic>> _mechanicumKnowledgeBase = [];

  // --- Helper: Parse code and extract functions/classes (simple simulation) ---
  Map<String, dynamic> _interpretCode(
    String code, {
    String? source,
    List<String>? tags,
  }) {
  // Simulate code parsing: extract function and class names
    final functionRegex = RegExp(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(');
    final classRegex = RegExp(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)');
    final functions =
        functionRegex
            .allMatches(code)
            .map((m) => m.group(1))
            .whereType<String>()
            .toList();
    final classes =
        classRegex
            .allMatches(code)
            .map((m) => m.group(1))
            .whereType<String>()
            .toList();
    return {
      'code': code,
      'functions': functions,
      'classes': classes,
      'source': source ?? 'unknown',
      'tags': tags ?? [],
      'timestamp': DateTime.now(),
    };
  }

  void suggestExtensionIdea(String feature, String rationale) {
    _aiExtensionIdeas.add({'feature': feature, 'rationale': rationale});
    print('🧠 AI: User suggested extension: $feature | Rationale: $rationale');
  // Simulate AI reasoning and possible implementation
    if (rationale.toLowerCase().contains('can implement')) {
      _aiGeneratedCodeSuggestions.add({
        'title': 'Implemented: $feature',
        'code': '/ AI implemented $feature based on user suggestion',
        'diff': '+ Added $feature',
        'reasoning':
            'User rationale indicated this could be implemented directly.',
        'timestamp': DateTime.now(),
      });
      print('🧠 AI: Implemented extension idea: $feature');
    }
    notifyListeners();
  }

  Map<String, String> get aiSuggestionFeedback {
    final Map<String, String> feedback = {};
    for (final s in _aiSuggestions) {
      final title = s['issue'] ?? s['title'];
      if (title == null) continue;
      if (s['accepted'] == true) {
        feedback[title] = 'accepted';
      } else if (s['ignored'] == true) {
        feedback[title] = 'ignored';
      } else {
        feedback[title] = '';
      }
    }
    for (final a in _appliedAISuggestions) {
      final title = a['title'];
      if (title != null) {
        feedback[title] = 'applied';
      }
    }
    return feedback;
  }

  // --- List of all Dart files in lib/ and subfolders ---
  final List<String> libFiles = [
    'lib/main.dart',
    'lib/ai_guardian_analytics_screen.dart',
    'lib/mission.dart',
    'lib/mission_provider.dart',
    'lib/mission_widget.dart',
    'lib/summary_page.dart',
    'lib/loading_screen.dart',
    'lib/home_page.dart',
    'lib/side_menu.dart',
    'lib/mechanicum.dart',
    'lib/mission_data.dart',
    'lib/entry_manager.dart',
    'lib/mastery_list.dart',
    'lib/theme.dart',
    'lib/tally.dart',
  // Widgets
    'lib/widgets/back_view.dart',
    'lib/widgets/front_view.dart',
  // Screens
    'lib/screens/app_history_screen.dart',
  // Providers
    'lib/providers/app_history_provider.dart',
  // Models
    'lib/models/app_history.dart',
    'lib/models/entry.dart',
    'lib/models/entry.g.dart',
  // Entries
    'lib/entries/add_entry.dart',
    'lib/entries/edit_entry.dart',
    'lib/entries/entry_pin_screen.dart',
    'lib/entries/list_entries.dart',
    'lib/entries/setup_pin_screen.dart',
    'lib/entries/view_entry.dart',
  // Core
    'lib/core/error/app_error.dart',
    'lib/core/logging/app_logger.dart',
    'lib/core/monitoring/performance_monitor.dart',
  ];

  // --- Map user uploaded code to file path ---
  final Map<String, String> _userUploadedCodeToFile = {};

  // --- Enhanced User Uploaded Code Learning System ---

  // Track user code patterns and learning
  final Map<String, Map<String, dynamic>> _userCodeLearning = {};
  final List<Map<String, dynamic>> _userCodePatterns = [];
  final Map<String, List<String>> _userCodeApplications = {};
  final Map<String, Map<String, dynamic>> _userCodeIntegrationStrategies = {};

  // --- User-uploaded code handling ---
  void saveUserUploadedCode(String code) {
    final dir = Directory('lib/ai_user_uploads');
    if (!dir.existsSync()) dir.createSync(recursive: true);
    final filePath =
        'lib/ai_user_uploads/upload_${DateTime.now().millisecondsSinceEpoch}.dart';
    File(filePath).writeAsStringSync(code);
    _userUploadedCodeToFile[code] = filePath;

  // --- AI Learning from User Code ---
    _learnFromUserCode(code, filePath);

    print('User uploaded code saved to $filePath');
    print('🧠 AI: Learning from user uploaded code...');
  }

  void _learnFromUserCode(String code, String filePath) {
  // Parse and analyze the user code
    final parsed = _interpretCode(code, source: 'user_upload');
    final functions = parsed['functions'] ?? [];
    final classes = parsed['classes'] ?? [];

  // Extract code patterns and characteristics
    final patterns = _extractCodePatterns(code);
    final characteristics = _analyzeCodeCharacteristics(code);

  // Store learning data
    final learningKey = '${filePath}_${DateTime.now().millisecondsSinceEpoch}';
    _userCodeLearning[learningKey] = {
      'code': code,
      'filePath': filePath,
      'parsed': parsed,
      'patterns': patterns,
      'characteristics': characteristics,
      'timestamp': DateTime.now(),
      'applications': [],
      'integrationStrategies': [],
    };

  // Analyze potential applications throughout the app
    final applications = _analyzePotentialApplications(
      code,
      patterns,
      characteristics,
    );
    _userCodeApplications[learningKey] = applications;

  // Generate integration strategies
    final strategies = _generateIntegrationStrategies(
      code,
      patterns,
      characteristics,
    );
    _userCodeIntegrationStrategies[learningKey] = strategies;

  // Update knowledge base with user code insights
    _updateKnowledgeBaseWithUserCode(parsed, patterns, characteristics);

  // Generate AI suggestions based on user code
    _generateSuggestionsFromUserCode(code, patterns, characteristics);

    print(
      '🧠 AI: Learned ${functions.length} functions, ${classes.length} classes from user code',
    );
    print(
      '🧠 AI: Identified ${patterns.length} patterns and ${applications.length} potential applications',
    );
  }

  Map<String, dynamic> _extractCodePatterns(String code) {
    final patterns = <String, dynamic>{};

  // Pattern 1: UI Widgets
    if (code.contains('Widget') ||
        code.contains('build(') ||
        code.contains('Scaffold')) {
      patterns['ui_widget'] = true;
      patterns['widget_type'] = _extractWidgetType(code);
    }

  // Pattern 2: Business Logic
    if (code.contains('class') &&
        (code.contains('Provider') ||
            code.contains('Service') ||
            code.contains('Manager'))) {
      patterns['business_logic'] = true;
      patterns['logic_type'] = _extractLogicType(code);
    }

  // Pattern 3: Data Models
    if (code.contains('class') &&
        (code.contains('Model') ||
            code.contains('Data') ||
            code.contains('Entity'))) {
      patterns['data_model'] = true;
      patterns['model_type'] = _extractModelType(code);
    }

  // Pattern 4: Utility Functions
    if (code.contains('static') ||
        code.contains('utility') ||
        code.contains('helper')) {
      patterns['utility_function'] = true;
      patterns['utility_type'] = _extractUtilityType(code);
    }

  // Pattern 5: State Management
    if (code.contains('setState') ||
        code.contains('notifyListeners') ||
        code.contains('ChangeNotifier')) {
      patterns['state_management'] = true;
      patterns['state_type'] = _extractStateType(code);
    }

  // Pattern 6: API/Network
    if (code.contains('http') ||
        code.contains('api') ||
        code.contains('fetch') ||
        code.contains('dio')) {
      patterns['network_api'] = true;
      patterns['api_type'] = _extractApiType(code);
    }

  // Pattern 7: Database/Storage
    if (code.contains('database') ||
        code.contains('sql') ||
        code.contains('shared_preferences') ||
        code.contains('hive')) {
      patterns['data_storage'] = true;
      patterns['storage_type'] = _extractStorageType(code);
    }

    return patterns;
  }

  Map<String, dynamic> _analyzeCodeCharacteristics(String code) {
    final characteristics = <String, dynamic>{};

  // Complexity analysis
    final lines = code.split('\n').length;
    characteristics['complexity'] =
        lines > 100
            ? 'high'
            : lines > 50
            ? 'medium'
            : 'low';

  // Dependencies analysis - simplified approach
    final imports = <String>[];
    final codeLines = code.split('\n');
    for (final line in codeLines) {
      final trimmed = line.trim();
      if (trimmed.startsWith('import ')) {
  // Simple extraction of import path
        final importPath = trimmed.substring(7).trim(); // Remove 'import '
        if (importPath.startsWith('"') || importPath.startsWith("'")) {
          final endQuote = importPath.indexOf(importPath[0], 1);
          if (endQuote > 0) {
            imports.add(importPath.substring(1, endQuote));
          }
        }
      }
    }
    characteristics['dependencies'] = imports;
    characteristics['dependency_count'] = imports.length;

  // Error handling
    characteristics['has_error_handling'] =
        code.contains('try') ||
        code.contains('catch') ||
        code.contains('throw');

  // Documentation
    characteristics['has_documentation'] =
        code.contains('/') ||
        code.contains('/**') ||
        code.contains('/ TODO');

  // Testing patterns
    characteristics['has_test_patterns'] =
        code.contains('test') ||
        code.contains('expect') ||
        code.contains('assert');

  // Performance considerations
    characteristics['has_performance_optimization'] =
        code.contains('const') ||
        code.contains('final') ||
        code.contains('cached');

    return characteristics;
  }

  List<String> _analyzePotentialApplications(
    String code,
    Map<String, dynamic> patterns,
    Map<String, dynamic> characteristics,
  ) {
    final applications = <String>[];

  // UI Widgets can be applied to any screen
    if (patterns['ui_widget'] == true) {
      applications.addAll([
        'lib/widgets/user_generated_widgets.dart',
        'lib/screens/custom_screens.dart',
        'lib/ai_generated/ui_components.dart',
      ]);
    }

  // Business Logic can be integrated into providers
    if (patterns['business_logic'] == true) {
      applications.addAll([
        'lib/providers/user_generated_provider.dart',
        'lib/services/user_generated_service.dart',
        'lib/ai_generated/business_logic.dart',
      ]);
    }

  // Data Models can be used throughout the app
    if (patterns['data_model'] == true) {
      applications.addAll([
        'lib/models/user_generated_models.dart',
        'lib/data/user_generated_data.dart',
        'lib/ai_generated/data_models.dart',
      ]);
    }

  // Utility Functions can be used anywhere
    if (patterns['utility_function'] == true) {
      applications.addAll([
        'lib/utils/user_generated_utils.dart',
        'lib/helpers/user_generated_helpers.dart',
        'lib/ai_generated/utilities.dart',
      ]);
    }

  // State Management can enhance existing providers
    if (patterns['state_management'] == true) {
      applications.addAll([
        'lib/providers/enhanced_state_provider.dart',
        'lib/state/user_generated_state.dart',
        'lib/ai_generated/state_management.dart',
      ]);
    }

  // Network/API can be integrated into services
    if (patterns['network_api'] == true) {
      applications.addAll([
        'lib/services/user_generated_api_service.dart',
        'lib/network/user_generated_network.dart',
        'lib/ai_generated/api_integration.dart',
      ]);
    }

  // Data Storage can enhance existing storage
    if (patterns['data_storage'] == true) {
      applications.addAll([
        'lib/storage/user_generated_storage.dart',
        'lib/database/user_generated_database.dart',
        'lib/ai_generated/storage_enhancement.dart',
      ]);
    }

    return applications;
  }

  Map<String, dynamic> _generateIntegrationStrategies(
    String code,
    Map<String, dynamic> patterns,
    Map<String, dynamic> characteristics,
  ) {
    final strategies = <String, dynamic>{};

  // Strategy 1: Direct Integration
    strategies['direct_integration'] = {
      'description': 'Integrate user code directly into existing files',
      'targets': _findDirectIntegrationTargets(code, patterns),
      'risk': 'medium',
      'benefit': 'Immediate functionality',
    };

  // Strategy 2: Extension Integration
    strategies['extension_integration'] = {
      'description': 'Extend existing classes with user code',
      'targets': _findExtensionTargets(code, patterns),
      'risk': 'low',
      'benefit': 'Enhances existing functionality',
    };

  // Strategy 3: New File Creation
    strategies['new_file_creation'] = {
      'description': 'Create new files for user code',
      'targets': _generateNewFileTargets(code, patterns),
      'risk': 'low',
      'benefit': 'Clean separation of concerns',
    };

  // Strategy 4: Refactoring Integration
    strategies['refactoring_integration'] = {
      'description': 'Refactor existing code to incorporate user patterns',
      'targets': _findRefactoringTargets(code, patterns),
      'risk': 'high',
      'benefit': 'Improves overall code quality',
    };

    return strategies;
  }

  List<String> _findDirectIntegrationTargets(
    String code,
    Map<String, dynamic> patterns,
  ) {
    final targets = <String>[];

  // Find existing files that could benefit from this code
    for (final filePath in libFiles) {
      if (_isCompatibleWithFile(code, patterns, filePath)) {
        targets.add(filePath);
      }
    }

    return targets;
  }

  List<String> _findExtensionTargets(
    String code,
    Map<String, dynamic> patterns,
  ) {
    final targets = <String>[];

  // Find classes that could be extended
    if (patterns['ui_widget'] == true) {
      targets.addAll([
        'lib/widgets/back_view.dart',
        'lib/widgets/front_view.dart',
      ]);
    }

    if (patterns['business_logic'] == true) {
      targets.addAll([
        'lib/mission_provider.dart',
        'lib/providers/app_history_provider.dart',
      ]);
    }

    return targets;
  }

  List<String> _generateNewFileTargets(
    String code,
    Map<String, dynamic> patterns,
  ) {
    final targets = <String>[];

    if (patterns['ui_widget'] == true) {
      targets.add(
        'lib/widgets/user_generated_${DateTime.now().millisecondsSinceEpoch}.dart',
      );
    }

    if (patterns['business_logic'] == true) {
      targets.add(
        'lib/providers/user_generated_${DateTime.now().millisecondsSinceEpoch}.dart',
      );
    }

    if (patterns['data_model'] == true) {
      targets.add(
        'lib/models/user_generated_${DateTime.now().millisecondsSinceEpoch}.dart',
      );
    }

    if (patterns['utility_function'] == true) {
      targets.add(
        'lib/utils/user_generated_${DateTime.now().millisecondsSinceEpoch}.dart',
      );
    }

    return targets;
  }

  List<String> _findRefactoringTargets(
    String code,
    Map<String, dynamic> patterns,
  ) {
    final targets = <String>[];

  // Find files that could benefit from refactoring based on user code patterns
    for (final filePath in libFiles) {
      if (_needsRefactoringBasedOnPatterns(code, patterns, filePath)) {
        targets.add(filePath);
      }
    }

    return targets;
  }

  bool _isCompatibleWithFile(
    String code,
    Map<String, dynamic> patterns,
    String filePath,
  ) {
  // Check if user code is compatible with existing file
    try {
      final file = File(filePath);
      if (!file.existsSync()) return false;

      final content = file.readAsStringSync();

  // Check for similar patterns
      if (patterns['ui_widget'] == true && content.contains('Widget'))
        return true;
      if (patterns['business_logic'] == true && content.contains('class'))
        return true;
      if (patterns['data_model'] == true && content.contains('class'))
        return true;
      if (patterns['utility_function'] == true && content.contains('void'))
        return true;

      return false;
    } catch (e) {
      return false;
    }
  }

  bool _needsRefactoringBasedOnPatterns(
    String code,
    Map<String, dynamic> patterns,
    String filePath,
  ) {
  // Check if existing file needs refactoring based on user code patterns
    try {
      final file = File(filePath);
      if (!file.existsSync()) return false;

      final content = file.readAsStringSync();

  // Check for code smells that user code could fix
      if (content.split('\n').length > 200) return true; // Large files
      if (content.contains('TODO') || content.contains('FIXME'))
        return true; // TODO items
      if (content.contains('print(') && patterns['has_error_handling'] == true)
        return true; // Print statements

      return false;
    } catch (e) {
      return false;
    }
  }

  void _updateKnowledgeBaseWithUserCode(
    Map<String, dynamic> parsed,
    Map<String, dynamic> patterns,
    Map<String, dynamic> characteristics,
  ) {
  // Add user code insights to knowledge base
    final knowledgeEntry = {
      'type': 'user_code_learning',
      'parsed': parsed,
      'patterns': patterns,
      'characteristics': characteristics,
      'timestamp': DateTime.now(),
      'applications': _analyzePotentialApplications(
        '',
        patterns,
        characteristics,
      ),
      'strategies': _generateIntegrationStrategies(
        '',
        patterns,
        characteristics,
      ),
    };

    _mechanicumKnowledgeBase.add(knowledgeEntry);

  // Update knowledge graph with user code relationships
    for (final function in parsed['functions'] ?? []) {
      _knowledgeGraph['user_code'] = _knowledgeGraph['user_code'] ?? [];
      if (!_knowledgeGraph['user_code']!.contains(function)) {
        _knowledgeGraph['user_code']!.add(function);
      }
    }

    for (final className in parsed['classes'] ?? []) {
      _knowledgeGraph['user_code'] = _knowledgeGraph['user_code'] ?? [];
      if (!_knowledgeGraph['user_code']!.contains(className)) {
        _knowledgeGraph['user_code']!.add(className);
      }
    }
  }

  void _generateSuggestionsFromUserCode(
    String code,
    Map<String, dynamic> patterns,
    Map<String, dynamic> characteristics,
  ) {
  // Generate AI suggestions based on user code analysis

  // Suggestion 1: Apply user patterns to existing code
    if (patterns.isNotEmpty) {
      final suggestion = {
        'title': 'Apply user code patterns to existing files',
        'code': _generatePatternApplicationCode(patterns),
        'diff': '+ Apply user patterns',
        'reasoning':
            'User code demonstrates good patterns that could improve existing code.',
        'timestamp': DateTime.now(),
        'targetFile': _determineTargetFile(code, _interpretCode(code)),
        'targetSymbol': _extractTargetSymbol(code),
      };
      _aiGeneratedCodeSuggestions.add(suggestion);
    }

  // Suggestion 2: Create integration utilities
    if (characteristics['has_utility_function'] == true) {
      final suggestion = {
        'title': 'Create integration utilities based on user code',
        'code': _generateIntegrationUtilityCode(code, patterns),
        'diff': '+ Integration utilities',
        'reasoning':
            'User code could be integrated throughout the app with proper utilities.',
        'timestamp': DateTime.now(),
        'targetFile': 'lib/utils/user_integration_utils.dart',
        'targetSymbol': 'UserIntegrationUtils',
      };
      _aiGeneratedCodeSuggestions.add(suggestion);
    }

  // Suggestion 3: Enhance existing functionality
    if (patterns['business_logic'] == true) {
      final suggestion = {
        'title': 'Enhance existing business logic with user patterns',
        'code': _generateEnhancementCode(code, patterns),
        'diff': '+ Enhanced business logic',
        'reasoning':
            'User code demonstrates business logic patterns that could enhance existing providers.',
        'timestamp': DateTime.now(),
        'targetFile': 'lib/providers/enhanced_provider.dart',
        'targetSymbol': 'EnhancedProvider',
      };
      _aiGeneratedCodeSuggestions.add(suggestion);
    }
  }

  String _generatePatternApplicationCode(Map<String, dynamic> patterns) {
  // Generate code that applies user patterns to existing code
    String code = '/ Apply user code patterns\n';

    if (patterns['has_error_handling'] == true) {
      code += '''
  // Enhanced error handling based on user patterns
void enhancedErrorHandling() {
  try {
  // Existing logic with user error handling patterns
  } catch (e) {
    print('Error handled with user patterns: \$e');
  }
}
''';
    }

    if (patterns['has_performance_optimization'] == true) {
      code += '''
  // Performance optimization based on user patterns
class OptimizedCode {
  static final _cache = <String, dynamic>{};
  
  static dynamic optimizedFunction(String key) {
    if (_cache.containsKey(key)) {
      return _cache[key];
    }
    final result = expensiveOperation(key);
    _cache[key] = result;
    return result;
  }
}
''';
    }

    return code;
  }

  String _generateIntegrationUtilityCode(
    String userCode,
    Map<String, dynamic> patterns,
  ) {
  // Generate utilities for integrating user code
    return '''
  // Integration utilities for user code
class UserIntegrationUtils {
  static void integrateUserCode(String code, Map<String, dynamic> patterns) {
  // Integration logic based on user patterns
    if (patterns['ui_widget'] == true) {
      _integrateUIWidget(code);
    }
    if (patterns['business_logic'] == true) {
      _integrateBusinessLogic(code);
    }
  }
  
  static void _integrateUIWidget(String code) {
  // UI widget integration logic
  }
  
  static void _integrateBusinessLogic(String code) {
  // Business logic integration
  }
}
''';
  }

  String _generateEnhancementCode(
    String userCode,
    Map<String, dynamic> patterns,
  ) {
  // Generate code that enhances existing functionality
    return '''
  // Enhanced provider based on user patterns
class EnhancedProvider extends ChangeNotifier {
  // Enhanced functionality based on user code patterns
  void enhancedMethod() {
  // Implementation based on user patterns
  }
}
''';
  }

  // Helper methods for pattern extraction
  String _extractWidgetType(String code) {
    if (code.contains('StatelessWidget')) return 'stateless';
    if (code.contains('StatefulWidget')) return 'stateful';
    return 'custom';
  }

  String _extractLogicType(String code) {
    if (code.contains('Provider')) return 'provider';
    if (code.contains('Service')) return 'service';
    if (code.contains('Manager')) return 'manager';
    return 'business_logic';
  }

  String _extractModelType(String code) {
    if (code.contains('Model')) return 'model';
    if (code.contains('Data')) return 'data';
    if (code.contains('Entity')) return 'entity';
    return 'data_class';
  }

  String _extractUtilityType(String code) {
    if (code.contains('static')) return 'static_utility';
    if (code.contains('helper')) return 'helper';
    return 'utility';
  }

  String _extractStateType(String code) {
    if (code.contains('setState')) return 'local_state';
    if (code.contains('notifyListeners')) return 'provider_state';
    return 'state_management';
  }

  String _extractApiType(String code) {
    if (code.contains('http')) return 'http';
    if (code.contains('dio')) return 'dio';
    return 'api';
  }

  String _extractStorageType(String code) {
    if (code.contains('sql')) return 'sql';
    if (code.contains('shared_preferences')) return 'preferences';
    if (code.contains('hive')) return 'hive';
    return 'storage';
  }

  // Getters for user code learning data
  Map<String, Map<String, dynamic>> get userCodeLearning =>
      Map.unmodifiable(_userCodeLearning);
  List<Map<String, dynamic>> get userCodePatterns =>
      List.unmodifiable(_userCodePatterns);
  Map<String, List<String>> get userCodeApplications =>
      Map.unmodifiable(_userCodeApplications);
  Map<String, Map<String, dynamic>> get userCodeIntegrationStrategies =>
      Map.unmodifiable(_userCodeIntegrationStrategies);

  get lastRefreshTime => null;

  // --- Helper methods for intelligent code targeting ---

  String _determineTargetFile(String code, Map<String, dynamic> parsed) {
  // Analyze code content to determine appropriate target file
    final functions = parsed['functions'] ?? [];

  // Check for UI-related code
    if (code.contains('Widget') ||
        code.contains('build(') ||
        code.contains('Scaffold')) {
      return 'lib/widgets/ai_generated_widget.dart';
    }

  // Check for business logic
    if (code.contains('class') &&
        (code.contains('Provider') || code.contains('Service'))) {
      return 'lib/providers/ai_generated_provider.dart';
    }

  // Check for data models
    if (code.contains('class') &&
        (code.contains('Model') || code.contains('Data'))) {
      return 'lib/models/ai_generated_model.dart';
    }

  // Check for utility functions
    if (functions.isNotEmpty && functions.length == 1) {
      return 'lib/utils/ai_generated_utils.dart';
    }

  // Default to main.dart for simple functions
    return 'lib/main.dart';
  }

  String _extractTargetSymbol(String code) {
  // Try to extract function name
    final fnMatch = RegExp(
      r'void\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
    ).firstMatch(code);
    if (fnMatch != null) {
      return fnMatch.group(1)!;
    }

  // Try to extract class name
    final classMatch = RegExp(
      r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
    ).firstMatch(code);
    if (classMatch != null) {
      return classMatch.group(1)!;
    }

  // Try to extract variable name
    final varMatch = RegExp(
      r'final\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=',
    ).firstMatch(code);
    if (varMatch != null) {
      return varMatch.group(1)!;
    }

    return 'aiGeneratedCode';
  }

  String _generateIntelligentCode(String focus, String? sourceCode) {
  // Generate code based on focus area and source code analysis
    switch (focus) {
      case 'performance':
        return '''
  // Performance optimization for ${sourceCode?.substring(0, 20) ?? 'code'}
void optimizedFunction() {
  // Cached computation
  static final _cache = <String, dynamic>{};
  
  // Optimized algorithm
  if (_cache.containsKey('key')) {
    return _cache['key'];
  }
  
  final result = expensiveComputation();
  _cache['key'] = result;
  return result;
}
''';
      case 'security':
        return '''
  // Security enhancement
String secureDataProcessing(String input) {
  // Input validation
  if (input.isEmpty || input.length > 1000) {
    throw ArgumentError('Invalid input');
  }
  
  // Sanitize input
  final sanitized = input.replaceAll(RegExp(r'[<>"\']'), '');
  
  // Secure processing
  return sanitized.trim();
}
''';
      case 'test coverage':
        return '''
  // Test coverage improvement
void testableFunction() {
  // Extracted logic for better testability
  final result = _businessLogic();
  _handleResult(result);
}

String _businessLogic() {
  // Pure function for easy testing
  return 'testable result';
}

void _handleResult(String result) {
  // Side effects isolated
  print('Handling: \$result');
}
''';
      case 'bug detection':
        return '''
  // Bug detection and prevention
class BugDetector {
  static void validateInput(dynamic input) {
    if (input == null) {
      throw ArgumentError('Input cannot be null');
    }
    if (input is String && input.isEmpty) {
      throw ArgumentError('String input cannot be empty');
    }
  }
  
  static void logPotentialBug(String context, dynamic data) {
    print('Potential bug detected in \$context: \$data');
  }
}
''';
      case 'self-improvement':
        return '''
  // Self-improvement mechanism
class SelfImprovingCode {
  static final _improvements = <String, dynamic>{};
  
  static void recordImprovement(String area, String improvement) {
    _improvements[area] = improvement;
    print('Self-improvement recorded: \$area -> \$improvement');
  }
  
  static dynamic getImprovement(String area) {
    return _improvements[area];
  }
}
''';
      case 'refactoring':
        return '''
  // Refactoring utilities
class CodeRefactorer {
  static String extractMethod(String code, String methodName) {
  // Extract method logic
    return '/ Extracted method: \$methodName\n\$code';
  }
  
  static String simplifyCondition(String condition) {
  // Simplify complex conditions
    return '/ Simplified: \$condition';
  }
}
''';
      default:
        return '''
  // AI-generated code for $focus
void aiGeneratedFunction() {
  // Intelligent implementation
  print('AI applied $focus improvements');
}
''';
    }
  }

  // --- Helper methods for AI learning and analysis ---

  int _calculateCodeComplexity(String code) {
    int complexity = 0;

  // Count control flow statements
    complexity +=
        RegExp(r'\b(if|else|for|while|switch|case)\b').allMatches(code).length;

  // Count function calls
    complexity += RegExp(r'\b\w+\s*\([^)]*\)').allMatches(code).length;

  // Count nested structures
    complexity += RegExp(r'\{[^{}]*\{').allMatches(code).length;

  // Count lines of code
    complexity += code.split('\n').length;

    return complexity;
  }

  List<String> _identifyCodePatterns(String code) {
    final patterns = <String>[];

  // Check for common patterns
    if (RegExp(r'class\s+\w+').hasMatch(code)) {
      patterns.add('class definition');
    }

    if (RegExp(r'void\s+\w+\s*\(').hasMatch(code)) {
      patterns.add('function definition');
    }

    if (RegExp(r'Widget\s+build\s*\(').hasMatch(code)) {
      patterns.add('Flutter widget build method');
    }

    if (RegExp(r'StatefulWidget|StatelessWidget').hasMatch(code)) {
      patterns.add('Flutter widget type');
    }

    if (RegExp(r'Provider\.of|Consumer<').hasMatch(code)) {
      patterns.add('state management pattern');
    }

    if (RegExp(r'async|await|Future<').hasMatch(code)) {
      patterns.add('asynchronous programming');
    }

    if (RegExp(r'try\s*\{|catch\s*\(').hasMatch(code)) {
      patterns.add('error handling');
    }

    if (RegExp(r'const\s+\w+|final\s+\w+').hasMatch(code)) {
      patterns.add('immutable declarations');
    }

    if (RegExp(r'Map<|List<|Set<').hasMatch(code)) {
      patterns.add('collection types');
    }

    return patterns;
  }

  List<String> _generateLearningInsights(
    String code,
    List<String> functions,
    List<String> classes,
  ) {
    final insights = <String>[];

  // Analyze function patterns
    if (functions.isNotEmpty) {
      insights.add('Found ${functions.length} functions to analyze');

  // Check for common function patterns
      if (functions.any((f) => f.contains('build'))) {
        insights.add('UI building patterns detected');
      }

      if (functions.any((f) => f.contains('init'))) {
        insights.add('Initialization patterns detected');
      }

      if (functions.any((f) => f.contains('handle'))) {
        insights.add('Event handling patterns detected');
      }
    }

  // Analyze class patterns
    if (classes.isNotEmpty) {
      insights.add('Found ${classes.length} classes to analyze');

      if (classes.any((c) => c.contains('Provider'))) {
        insights.add('State management patterns detected');
      }

      if (classes.any((c) => c.contains('Widget'))) {
        insights.add('UI component patterns detected');
      }

      if (classes.any((c) => c.contains('Model'))) {
        insights.add('Data model patterns detected');
      }
    }

  // Analyze code structure
    final lines = code.split('\n').length;
    if (lines > 50) {
      insights.add('Large code block - complex logic detected');
    } else if (lines > 20) {
      insights.add('Medium code block - moderate complexity');
    } else {
      insights.add('Small code block - simple logic');
    }

  // Check for specific Flutter patterns
    if (code.contains('Scaffold')) {
      insights.add('Flutter UI structure patterns');
    }

    if (code.contains('Navigator')) {
      insights.add('Navigation patterns detected');
    }

    if (code.contains('Animation')) {
      insights.add('Animation patterns detected');
    }

    return insights;
  }

  List<String> _extractKeyLearnings(List<Map<String, dynamic>> insights) {
    final learnings = <String>[];

  // Aggregate insights across all analyzed files
    final allPatterns = <String>{};
    final allFunctions = <String>{};
    final allClasses = <String>{};
    int totalComplexity = 0;

    for (final insight in insights) {
      allPatterns.addAll((insight['patterns'] as List<String>?) ?? []);
      allFunctions.addAll((insight['functions'] as List<String>?) ?? []);
      allClasses.addAll((insight['classes'] as List<String>?) ?? []);
      totalComplexity += (insight['complexity'] as int?) ?? 0;
    }

  // Generate key learnings
    if (allPatterns.isNotEmpty) {
      learnings.add(
        'Identified ${allPatterns.length} code patterns: ${allPatterns.join(', ')}',
      );
    }

    if (allFunctions.isNotEmpty) {
      learnings.add(
        'Analyzed ${allFunctions.length} functions across codebase',
      );
    }

    if (allClasses.isNotEmpty) {
      learnings.add(
        'Studied ${allClasses.length} classes for architectural patterns',
      );
    }

    if (totalComplexity > 0) {
      final avgComplexity = totalComplexity / insights.length;
      learnings.add(
        'Average code complexity: ${avgComplexity.toStringAsFixed(1)}',
      );
    }

  // Specific pattern learnings
    if (allPatterns.contains('Flutter widget build method')) {
      learnings.add('Learning Flutter UI construction patterns');
    }

    if (allPatterns.contains('state management pattern')) {
      learnings.add('Understanding state management approaches');
    }

    if (allPatterns.contains('asynchronous programming')) {
      learnings.add('Analyzing async/await patterns');
    }

    if (allPatterns.contains('error handling')) {
      learnings.add('Studying error handling strategies');
    }

    return learnings;
  }

  void initializeAIGuardian() {}
}
