import 'package:flutter/material.dart';
import 'mission.dart';

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
    return MissionData(
      id: json['id'],
      missionId: json['missionId'],
      notificationId: json['notificationId'],
      title: json['title'],
      description: json['description'],
      type: MissionType.values.firstWhere((e) => e.toString() == json['type']),
      isCounterBased: json['isCounterBased'],
      targetCount: json['targetCount'],
      currentCount: json['currentCount'],
      isCompleted: json['isCompleted'],
      lastCompleted: json['lastCompleted'] != null ? DateTime.parse(json['lastCompleted']) : null,
      createdAt: json['createdAt'] != null ? DateTime.parse(json['createdAt']) : null,
      hasFailed: json['hasFailed'],
      subtasks: (json['subtasks'] as List).map((s) => MissionSubtask.fromJson(s)).toList(),
      linkedMasteryId: json['linkedMasteryId'],
      masteryValue: json['masteryValue'],
      imageUrl: json['imageUrl'],
      boltColor: json['boltColor'] != null ? Color(json['boltColor']) : null,
      timelapseColor: json['timelapseColor'] != null ? Color(json['timelapseColor']) : null,
      isLocked: json['isLocked'] ?? false,
      masteryId: json['masteryId'],
      value: json['value'],
      isSubtaskCounter: json['isSubtaskCounter'] ?? false,
      subtaskMasteryValues: Map<String, double>.from(json['subtaskMasteryValues'] ?? {}),
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
      scheduledNotificationId: scheduledNotificationId ?? this.scheduledNotificationId,
    );
  }
}
