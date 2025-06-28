import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:provider/provider.dart';
import '../models/ai_notification.dart';
import '../providers/notification_provider.dart';
import 'package:uuid/uuid.dart';
import '../main.dart'; // To get the navigatorKey

class NotificationService {
  static final NotificationService instance = NotificationService._internal();
  factory NotificationService() => instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
  final Uuid _uuid = Uuid();

  Future<void> initialize() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher'); // default icon

    final InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
    );

    await _flutterLocalNotificationsPlugin.initialize(initializationSettings);
    print('NotificationService Initialized');
  }

  Future<void> showNotification({
    required String aiSource,
    required String message,
    required String iconChar, // Using a string for the icon character
  }) async {
    final context = navigatorKey.currentContext;
    if (context == null) return;
    
    final notificationProvider = Provider.of<NotificationProvider>(context, listen: false);

    final notification = _createAINotification(aiSource, message, iconChar);

    // Add to in-app notification center
    notificationProvider.addNotification(
      notification.title,
      notification.body,
      notification.aiSource,
      notification.timestamp,
    );

    // Show system notification
    final androidDetails = AndroidNotificationDetails(
      'ai_channel_id',
      'AI Notifications',
      channelDescription: 'Notifications from in-app AIs',
      importance: Importance.max,
      priority: Priority.high,
      icon: _getAndroidIconName(aiSource), // Use a specific drawable for the icon
    );
    final platformDetails = NotificationDetails(android: androidDetails);

    await _flutterLocalNotificationsPlugin.show(
      notification.hashCode, // Use a unique int ID
      notification.title,
      notification.body,
      platformDetails,
    );
  }

  AINotification _createAINotification(String aiSource, String message, String iconChar) {
    IconData iconData;
    Color iconColor;

    switch (aiSource) {
      case 'The Imperium':
        iconData = Icons.auto_awesome; 
        iconColor = Colors.amber;
        break;
      case 'Mechanicum':
        iconData = Icons.shield;
        iconColor = Colors.blue;
        break;
      case 'AI Sandbox':
        iconData = Icons.science;
        iconColor = Colors.green;
        break;
      default:
        iconData = Icons.info;
        iconColor = Colors.grey;
    }

    return AINotification(
      id: _uuid.v4(),
      title: aiSource,
      body: message,
      aiSource: aiSource,
      icon: iconData,
      iconColor: iconColor,
      timestamp: DateTime.now(),
    );
  }
  
  String? _getAndroidIconName(String aiSource) {
    // These must correspond to drawable resources in android/app/src/main/res/drawable
    // For now, returning null to use the default.
    // Example: 'ic_imperium'
    return null; 
  }
} 