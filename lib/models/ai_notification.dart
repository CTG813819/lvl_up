import 'package:flutter/material.dart';

class AINotification {
  final String id;
  final String title;
  final String body;
  final String aiSource;
  final IconData icon;
  final Color iconColor;
  final DateTime timestamp;
  bool isRead;

  AINotification({
    required this.id,
    required this.title,
    required this.body,
    required this.aiSource,
    required this.icon,
    required this.iconColor,
    required this.timestamp,
    this.isRead = false,
  });
} 