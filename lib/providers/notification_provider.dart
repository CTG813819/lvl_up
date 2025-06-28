import 'package:flutter/material.dart';
import '../models/ai_notification.dart';
import 'dart:collection';

class NotificationProvider extends ChangeNotifier {
  final List<AINotification> _notifications = [];

  UnmodifiableListView<AINotification> get notifications => UnmodifiableListView(_notifications);

  int get unreadCount => _notifications.where((n) => !n.isRead).length;

  void addNotification(String title, String message, String type, DateTime timestamp) {
    // Map notification type to appropriate icon and color
    IconData icon;
    Color iconColor;
    
    switch (type.toLowerCase()) {
      case 'chaos':
        icon = Icons.warning;
        iconColor = Colors.purple;
        break;
      case 'warp':
        icon = Icons.block;
        iconColor = Colors.red;
        break;
      case 'imperium':
        icon = Icons.psychology;
        iconColor = Colors.blue;
        break;
      case 'sandbox':
        icon = Icons.science;
        iconColor = Colors.orange;
        break;
      case 'guardian':
        icon = Icons.shield;
        iconColor = Colors.green;
        break;
      default:
        icon = Icons.notifications;
        iconColor = Colors.grey;
    }
    
    final notification = AINotification(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      body: message,
      aiSource: type,
      icon: icon,
      iconColor: iconColor,
      timestamp: timestamp,
      isRead: false,
    );
    
    // Avoid duplicate notifications
    if (_notifications.any((n) => n.id == notification.id)) return;
    
    _notifications.insert(0, notification);
    notifyListeners();
  }

  void markAsRead(String id) {
    final index = _notifications.indexWhere((n) => n.id == id);
    if (index != -1 && !_notifications[index].isRead) {
      _notifications[index].isRead = true;
      notifyListeners();
    }
  }

  void markAllAsRead() {
    for (var notification in _notifications) {
      notification.isRead = true;
    }
    notifyListeners();
  }

  void clearAll() {
    _notifications.clear();
    notifyListeners();
  }
} 