import 'package:flutter/material.dart';
import 'mission.dart';
import 'dart:convert';

class MissionData {
  final String? id;
  final String? missionId;
  final int notificationId;
  final String title;
  final String description;
  final MissionType type;
  final bool isCounterBased;
  final int targetCount;
  final int currentCount;
  final bool isCompleted;
  final DateTime? lastCompleted;
  final DateTime? createdAt;
  final bool hasFailed;
  final List<MissionSubtask> subtasks;
  final String? linkedMasteryId;
  final double masteryValue;
  final String imageUrl;
  final Color? boltColor;
  final Color? timelapseColor;
  final bool isLocked;
  final String? masteryId;
  final double? value;
  final bool isSubtaskCounter;
  final Map<String, double> subtaskMasteryValues;
  final int? scheduledNotificationId;

  MissionData({
    this.id,
    this.missionId,
    required this.notificationId,
    required this.title,
    required this.description,
    required this.type,
    required this.isCounterBased,
    required this.targetCount,
    this.currentCount = 0,
    this.isCompleted = false,
    this.lastCompleted,
    this.createdAt,
    this.hasFailed = false,
    this.subtasks = const [],
    this.linkedMasteryId,
    this.masteryValue = 0,
    required this.imageUrl,
    this.boltColor,
    this.timelapseColor,
    this.isLocked = false,
    this.masteryId,
    this.value,
    this.isSubtaskCounter = false,
    required this.subtaskMasteryValues,
    this.scheduledNotificationId,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'missionId': missionId,
      'notificationId': notificationId,
      'title': title,
      'description': description,
      'type': type.toString(),
      'isCounterBased': isCounterBased,
      'targetCount': targetCount,
      'currentCount': currentCount,
      'isCompleted': isCompleted,
      'lastCompleted': lastCompleted?.toIso8601String(),
      'createdAt': createdAt?.toIso8601String(),
      'hasFailed': hasFailed,
      'subtasks': subtasks.map((s) => s.toJson()).toList(),
      'linkedMasteryId': linkedMasteryId,
      'masteryValue': masteryValue,
      'imageUrl': imageUrl,
      'boltColor': boltColor?.value,
      'timelapseColor': timelapseColor?.value,
      'isLocked': isLocked,
      'masteryId': masteryId,
      'value': value,
      'isSubtaskCounter': isSubtaskCounter,
      'subtaskMasteryValues': subtaskMasteryValues,
      'scheduledNotificationId': scheduledNotificationId,
    };
  }

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
    // Defensive parsing for notificationId
    int? rawId = json['notificationId'];
    int notificationId = 0;
    if (rawId is int) {
      if (rawId < -2147483648 || rawId > 2147483647) {
        notificationId = rawId % 0x7FFFFFFF;
      } else {
        notificationId = rawId;
      }
    } else if (rawId is String) {
      try {
        int parsed = int.parse(rawId as String);
        notificationId =
            (parsed < -2147483648 || parsed > 2147483647)
                ? parsed % 0x7FFFFFFF
                : parsed;
      } catch (_) {
        notificationId = 0;
      }
    }
    // Defensive parsing for createdAt
    final createdAtRaw = json['createdAt'];
    DateTime? createdAt =
        (createdAtRaw is String && createdAtRaw.isNotEmpty)
            ? DateTime.parse(createdAtRaw)
            : null;
    // Defensive parsing for imageUrl
    final imageUrlRaw = json['imageUrl'];
    String imageUrl =
        (imageUrlRaw is String && imageUrlRaw.isNotEmpty) ? imageUrlRaw : '';
    // Defensive parsing for subtaskMasteryValues
    final subtaskMasteryValuesRaw = json['subtaskMasteryValues'];
    Map<String, double> subtaskMasteryValues = {};
    if (subtaskMasteryValuesRaw is Map) {
      subtaskMasteryValues = Map<String, double>.from(subtaskMasteryValuesRaw);
    } else if (subtaskMasteryValuesRaw == null) {
      subtaskMasteryValues = {};
    }
    return MissionData(
      id: json['id'],
      missionId: json['missionId'],
      notificationId: notificationId,
      title: (json['title'] as String?) ?? '',
      description: (json['description'] as String?) ?? '',
      type: MissionType.values.firstWhere((e) => e.toString() == json['type']),
      isCounterBased: json['isCounterBased'],
      targetCount: json['targetCount'],
      currentCount: json['currentCount'],
      isCompleted: json['isCompleted'],
      lastCompleted:
          json['lastCompleted'] != null
              ? DateTime.parse(json['lastCompleted'])
              : null,
      createdAt: createdAt,
      hasFailed: json['hasFailed'],
      subtasks:
          subtasksList
              .where((s) => s is Map<String, dynamic>)
              .map((s) => MissionSubtask.fromJson(s as Map<String, dynamic>))
              .toList(),
      linkedMasteryId: json['linkedMasteryId'],
      masteryValue: json['masteryValue'],
      imageUrl: imageUrl,
      boltColor: json['boltColor'] != null ? Color(json['boltColor']) : null,
      timelapseColor:
          json['timelapseColor'] != null ? Color(json['timelapseColor']) : null,
      isLocked: json['isLocked'] ?? false,
      masteryId: json['masteryId'],
      value: json['value'],
      isSubtaskCounter: json['isSubtaskCounter'] ?? false,
      subtaskMasteryValues: subtaskMasteryValues,
      scheduledNotificationId: json['scheduledNotificationId'],
    );
  }

  MissionData copyWith({
    String? id,
    String? missionId,
    int? notificationId,
    String? title,
    String? description,
    MissionType? type,
    bool? isCounterBased,
    int? targetCount,
    int? currentCount,
    bool? isCompleted,
    DateTime? lastCompleted,
    DateTime? createdAt,
    bool? hasFailed,
    List<MissionSubtask>? subtasks,
    String? linkedMasteryId,
    double? masteryValue,
    String? imageUrl,
    Color? boltColor,
    Color? timelapseColor,
    bool? isLocked,
    String? masteryId,
    double? value,
    bool? isSubtaskCounter,
    Map<String, double>? subtaskMasteryValues,
    int? scheduledNotificationId,
  }) {
    return MissionData(
      id: id ?? this.id,
      missionId: missionId ?? this.missionId,
      notificationId: notificationId ?? this.notificationId,
      title: title ?? this.title,
      description: description ?? this.description,
      type: type ?? this.type,
      isCounterBased: isCounterBased ?? this.isCounterBased,
      targetCount: targetCount ?? this.targetCount,
      currentCount: currentCount ?? this.currentCount,
      isCompleted: isCompleted ?? this.isCompleted,
      lastCompleted: lastCompleted ?? this.lastCompleted,
      createdAt: createdAt ?? this.createdAt,
      hasFailed: hasFailed ?? this.hasFailed,
      subtasks: subtasks ?? this.subtasks,
      linkedMasteryId: linkedMasteryId ?? this.linkedMasteryId,
      masteryValue: masteryValue ?? this.masteryValue,
      imageUrl: imageUrl ?? this.imageUrl,
      boltColor: boltColor ?? this.boltColor,
      timelapseColor: timelapseColor ?? this.timelapseColor,
      isLocked: isLocked ?? this.isLocked,
      masteryId: masteryId ?? this.masteryId,
      value: value ?? this.value,
      isSubtaskCounter: isSubtaskCounter ?? this.isSubtaskCounter,
      subtaskMasteryValues: subtaskMasteryValues ?? this.subtaskMasteryValues,
      scheduledNotificationId:
          scheduledNotificationId ?? this.scheduledNotificationId,
    );
  }
}
