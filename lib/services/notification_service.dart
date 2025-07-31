import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:provider/provider.dart';
import '../models/ai_notification.dart';
import '../providers/notification_provider.dart';
import '../providers/system_status_provider.dart';
import 'package:uuid/uuid.dart';
import '../main.dart'; // To get the navigatorKey
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/services.dart';
import '../services/dynamic_island_platform_service.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  static NotificationService get instance => _instance;

  static bool suppressNotifications =
      true; // Suppress notifications until app is ready

  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();
  final Uuid _uuid = Uuid();

  bool _isInitialized = false;
  Completer<void>? _initCompleter;

  NotificationService._internal();

  Future<void> initialize() async {
    if (_isInitialized) {
      print('NotificationService: Already initialized');
      return;
    }

    if (_initCompleter != null) {
      print('NotificationService: Initialization already in progress');
      await _initCompleter!.future;
      return;
    }

    _initCompleter = Completer<void>();

    try {
      print('NotificationService: Starting initialization...');

  // Initialize settings based on platform
      const AndroidInitializationSettings androidSettings =
          AndroidInitializationSettings('@drawable/notification_icon');

  // For Windows, we need to provide Windows-specific settings

      const InitializationSettings initSettings = InitializationSettings(
        android: androidSettings,
      );

      await _notifications.initialize(initSettings);

      _isInitialized = true;
      print('NotificationService: Initialization successful');
      _initCompleter?.complete();
    } catch (e) {
      print('NotificationService: Initialization failed: $e');
      _initCompleter?.completeError(e);
  // Don't rethrow - let the app continue without notifications
    }
  }

  Future<void> showNotification({
    required String aiSource,
    required String message,
    String? iconChar,
  }) async {
    if (suppressNotifications) {
      print('NotificationService: Suppressing notification (app not ready)');
      return;
    }

    if (!_isInitialized) {
      print('NotificationService: Not initialized, skipping notification');
      return;
    }

    try {
      const AndroidNotificationDetails androidDetails =
          AndroidNotificationDetails(
            'ai_notifications',
            'AI Notifications',
            channelDescription: 'Notifications from AI systems',
            importance: Importance.high,
            priority: Priority.high,
            showWhen: true,
          );

      const WindowsNotificationDetails windowsDetails =
          WindowsNotificationDetails();

      const NotificationDetails details = NotificationDetails(
        android: androidDetails,
        windows: windowsDetails,
      );

      await _notifications.show(
        (DateTime.now().millisecondsSinceEpoch % 2147483647),
        '$iconChar $aiSource',
        message,
        details,
      );

      print('NotificationService: Notification shown: $aiSource - $message');
    } catch (e) {
      print('NotificationService: Error showing notification: $e');
    }
  }

  // Show Dynamic Island-style AI progress notification
  Future<void> showAIProgressNotification({
    required String aiName,
    required double progress,
    required String metric,
    Color? aiColor,
    IconData? aiIcon,
    String? additionalInfo,
  }) async {
    if (suppressNotifications) {
      print(
        'NotificationService: Suppressing AI progress notification (app not ready)',
      );
      return;
    }

    if (!_isInitialized) {
      print(
        'NotificationService: Not initialized, skipping AI progress notification',
      );
      return;
    }

    try {
  // Capitalize AI name
      final displayName =
          aiName.isNotEmpty
              ? aiName[0].toUpperCase() + aiName.substring(1)
              : aiName;

  // Create Dynamic Island-style content
      final progressBar = _createDynamicIslandProgressBar(progress);
      final progressPercent = (progress * 100).toStringAsFixed(1);

  // Get AI-specific colors for gradient
      final primaryColor = aiColor ?? Colors.blue;
      final secondaryColor = _getSecondaryColor(primaryColor);

  // Create rich notification content
      final String iconEmoji =
          aiIcon != null ? String.fromCharCode(aiIcon.codePoint) : '🤖';
      final title = '$iconEmoji $displayName';

  // Dynamic Island-style body with gradient colors and rich formatting
      final body = _createDynamicIslandBody(
        progressBar: progressBar,
        progressPercent: progressPercent,
        metric: metric,
        additionalInfo: additionalInfo,
        primaryColor: primaryColor,
        secondaryColor: secondaryColor,
      );

  // Create Dynamic Island-style notification details
      final androidDetails = AndroidNotificationDetails(
        'ai_dynamic_island_${displayName.toLowerCase()}',
        'AI Dynamic Island - $displayName',
        channelDescription:
            'Dynamic Island-style progress updates for $displayName',
        importance: Importance.max,
        priority: Priority.max,
        color: primaryColor,
        icon: '@mipmap/ic_launcher',
        showWhen: true,
        enableVibration: true,
        enableLights: true,
        ledColor: primaryColor,
        ledOnMs: 1500,
        ledOffMs: 1500,
  // Use BigTextStyle for rich content display
        styleInformation: BigTextStyleInformation(
          body,
          contentTitle: title,
          htmlFormatContent: false,
          htmlFormatTitle: false,
        ),
  // Add custom actions for Dynamic Island interactivity
        actions: [
          AndroidNotificationAction(
            'view_details_${displayName.toLowerCase()}',
            'View Details',
            showsUserInterface: true,
            cancelNotification: false,
          ),
          AndroidNotificationAction(
            'dismiss_${displayName.toLowerCase()}',
            'Dismiss',
            showsUserInterface: false,
            cancelNotification: true,
          ),
        ],
      );

      final notificationDetails = NotificationDetails(android: androidDetails);

  // Use AI name hash for consistent notification ID
      final notificationId = displayName.hashCode;

      await _notifications.show(
        notificationId,
        title,
        body,
        notificationDetails,
      );

      print(
        'NotificationService: Dynamic Island AI Progress notification shown: $displayName - $progressPercent%',
      );
    } catch (e) {
      print('NotificationService: Error showing AI progress notification: $e');
    }
  }

  // Create Dynamic Island-style progress bar
  String _createDynamicIslandProgressBar(double progress) {
    const int barLength = 12;
    final int filledLength = (progress * barLength).round();
    final int emptyLength = barLength - filledLength;

  // Use more sophisticated characters for Dynamic Island style
    final filled = '█' * filledLength;
    final empty = '░' * emptyLength;

    return filled + empty;
  }

  // Create Dynamic Island-style notification body
  String _createDynamicIslandBody({
    required String progressBar,
    required String progressPercent,
    required String metric,
    String? additionalInfo,
    required Color primaryColor,
    required Color secondaryColor,
  }) {
    final buffer = StringBuffer();

  // Add progress bar with percentage
    buffer.writeln('$progressBar  $progressPercent%');
    buffer.writeln('');

  // Add metric information
    buffer.writeln('📊 Metric: $metric');

  // Add additional info if available
    if (additionalInfo != null && additionalInfo.isNotEmpty) {
      buffer.writeln('');
      buffer.writeln('ℹ️  $additionalInfo');
    }

  // Add Dynamic Island-style footer
    buffer.writeln('');
    buffer.writeln('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    buffer.writeln('🎯 AI Progress Update');

    return buffer.toString();
  }

  // Get secondary color for gradient effect
  Color _getSecondaryColor(Color primaryColor) {
  // Create a complementary or lighter version of the primary color
    final hsl = HSLColor.fromColor(primaryColor);
    return hsl.withLightness((hsl.lightness + 0.2).clamp(0.0, 1.0)).toColor();
  }

  // Create a text-based progress bar for notifications
  String _createProgressBarText(double progress) {
    const int barLength = 10;
    final int filledLength = (progress * barLength).round();
    final int emptyLength = barLength - filledLength;

    final filled = '█' * filledLength;
    final empty = '░' * emptyLength;

    return filled + empty;
  }

  // Show multiple AI progress notifications simultaneously
  Future<void> showMultipleAIProgressNotifications({
    required Map<String, Map<String, dynamic>> aiProgressData,
  }) async {
    if (suppressNotifications) {
      print(
        'NotificationService: Suppressing multiple AI progress notifications (app not ready)',
      );
      return;
    }

    if (!_isInitialized) {
      print(
        'NotificationService: Not initialized, skipping multiple AI progress notifications',
      );
      return;
    }

    try {
      for (final entry in aiProgressData.entries) {
        final aiName = entry.key;
        final data = entry.value;

        final progress = data['progress'] as double? ?? 0.0;
        final metric = data['metric'] as String? ?? 'leveling_progress';
        final aiColor = data['color'] as Color?;
        final aiIcon = data['icon'] as IconData?;
        final additionalInfo = data['additionalInfo'] as String?;

        await showAIProgressNotification(
          aiName: aiName,
          progress: progress,
          metric: metric,
          aiColor: aiColor,
          aiIcon: aiIcon,
          additionalInfo: additionalInfo,
        );
      }

      print(
        'NotificationService: Multiple Dynamic Island AI progress notifications shown for ${aiProgressData.length} AIs',
      );
    } catch (e) {
      print(
        'NotificationService: Error showing multiple AI progress notifications: $e',
      );
    }
  }

  // Show Dynamic Island-style system status notification
  Future<void> showDynamicIslandSystemNotification({
    required String title,
    required String message,
    required SystemHealth status,
    Color? customColor,
  }) async {
    final context = navigatorKey.currentContext;
    if (context == null) return;

    final notificationProvider = Provider.of<NotificationProvider>(
      context,
      listen: false,
    );

  // Add to in-app notification center
    notificationProvider.addNotification(
      title,
      message,
      'System',
      DateTime.now(),
    );

  // Create Dynamic Island-style system notification
    final statusColor = customColor ?? _getStatusColor(status);
    final secondaryColor = _getSecondaryColor(statusColor);

    final androidDetails = AndroidNotificationDetails(
      'system_dynamic_island',
      'System Dynamic Island',
      channelDescription: 'Dynamic Island-style system status notifications',
      importance: Importance.max,
      priority: Priority.max,
      icon: 'notification_icon',
      color: statusColor,
      styleInformation: BigTextStyleInformation(
        _createDynamicIslandBody(
          progressBar: _createDynamicIslandProgressBar(1.0),
          progressPercent: '100.0',
          metric: 'System Status',
          additionalInfo: message,
          primaryColor: statusColor,
          secondaryColor: secondaryColor,
        ),
        contentTitle: '🔧 $title',
      ),
    );
    final platformDetails = NotificationDetails(android: androidDetails);

    await _notifications.show(
      (DateTime.now().millisecondsSinceEpoch % 2147483647),
      '🔧 $title',
      message,
      platformDetails,
    );
  }

  Future<void> showProposalNotification({
    required String aiSource,
    required String filePath,
    required String proposalType,
  }) async {
    String message = '';
    String iconChar = '';

    switch (proposalType) {
      case 'created':
        message = 'New proposal for $filePath';
        iconChar = '💡';
        break;
      case 'approved':
        message = 'Proposal for $filePath approved';
        iconChar = '✅';

      case 'rejected':
        message = 'Proposal for $filePath rejected';
        iconChar = '❌';
        break;
      case 'applied':
        message = 'Proposal applied to $filePath';
        iconChar = '🚀';
        break;
      default:
        message = 'Proposal update for $filePath';
        iconChar = '📝';
    }

    await showNotification(
      aiSource: aiSource,
      message: message,
      iconChar: iconChar,
    );
  }

  Future<void> showSystemStatusNotification({
    required String title,
    required String message,
    required SystemHealth status,
  }) async {
    final context = navigatorKey.currentContext;
    if (context == null) return;

    final notificationProvider = Provider.of<NotificationProvider>(
      context,
      listen: false,
    );

  // Add to in-app notification center
    notificationProvider.addNotification(
      title,
      message,
      'System',
      DateTime.now(),
    );

  // Show system notification
    final androidDetails = AndroidNotificationDetails(
      'system_channel_id',
      'System Notifications',
      channelDescription: 'System status and health notifications',
      importance: Importance.high,
      priority: Priority.high,
      icon: 'notification_icon',
      color: _getStatusColor(status),
    );
    final platformDetails = NotificationDetails(android: androidDetails);

    await _notifications.show(
      (DateTime.now().millisecondsSinceEpoch % 2147483647),
      title,
      message,
      platformDetails,
    );
  }

  Future<void> showBackendActivityNotification({
    required String activity,
    required String details,
    bool isError = false,
  }) async {
    final title = isError ? 'Backend Error' : 'Backend Activity';
    final message = '$activity: $details';

    await showSystemStatusNotification(
      title: title,
      message: message,
      status: isError ? SystemHealth.critical : SystemHealth.healthy,
    );
  }

  // Get status color for system notifications
  Color _getStatusColor(SystemHealth status) {
    switch (status) {
      case SystemHealth.healthy:
        return Colors.green;
      case SystemHealth.warning:
        return Colors.orange;
      case SystemHealth.critical:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  // Show Dynamic Island-style AI proposal notification
  Future<void> showAIProposalNotification({
    required String aiType,
    required String action,
    required String filePath,
    String? details,
  }) async {
    String title = '';
    String message = '';
    String iconChar = '';

    switch (action) {
      case 'created':
        title = 'New AI Proposal';
        message = '$aiType created a proposal for $filePath';
        iconChar = '💡';
        break;
      case 'approved':
        title = 'Proposal Approved';
        message = 'Proposal for $filePath was approved';
        iconChar = '✅';
        break;
      case 'rejected':
        title = 'Proposal Rejected';
        message = 'Proposal for $filePath was rejected';
        iconChar = '❌';
        break;
      case 'applied':
        title = 'Proposal Applied';
        message = 'Proposal for $filePath was applied';
        iconChar = '🚀';
        break;
      default:
        title = 'AI Activity';
        message = '$aiType: $action on $filePath';
        iconChar = '🤖';
    }

    if (details != null) {
      message += '\n$details';
    }

    await showNotification(
      aiSource: aiType,
      message: message,
      iconChar: iconChar,
    );
  }

  Future<void> showConquestNotification({
    required String action,
    required String appName,
    String? details,
    bool isError = false,
  }) async {
    String title = '';
    String message = '';
    String iconChar = '';

    switch (action) {
      case 'app_created':
        title = 'New App Created';
        message = 'Conquest AI created: $appName';
        iconChar = '📱';
        break;
      case 'apk_built':
        title = 'APK Ready';
        message = 'APK for $appName is ready for download';
        iconChar = '📦';
        break;
      case 'repo_created':
        title = 'Repository Created';
        message = 'GitHub repo created for $appName';
        iconChar = '📤';
        break;
      case 'build_started':
        title = 'Build Started';
        message = 'Building $appName...';
        iconChar = '🔨';
        break;
      case 'build_completed':
        title = 'Build Completed';
        message = '$appName build finished successfully';
        iconChar = '✅';
        break;
      case 'build_failed':
        title = 'Build Failed';
        message = '$appName build failed';
        iconChar = '❌';
        break;
      default:
        title = 'Conquest Activity';
        message = '$action: $appName';
        iconChar = '🐉';
    }

    if (details != null) {
      message += '\n$details';
    }

    await showNotification(
      aiSource: 'Conquest',
      message: message,
      iconChar: iconChar,
    );
  }

  // Show custom AI Dynamic Island notification using the platform channel
  Future<void> showAICustomDynamicIslandNotification({
    required String aiName,
    required double progress, // 0.0 - 1.0
    required String iconName,
    required Color aiColor,
    String? backgroundImagePath,
    String? progressText,
    Duration autoHideDuration = const Duration(seconds: 5),
  }) async {
    try {
      await DynamicIslandPlatformService.showDynamicIsland(
        aiName: aiName,
        iconName: iconName,
        iconColor: aiColor,
        progress: progress,
        progressText: progressText,
        backgroundImagePath: backgroundImagePath,
        autoHideDuration: autoHideDuration,
      );
    } catch (e) {
      print(
        'NotificationService: Error showing custom Dynamic Island notification: $e',
      );
    }
  }

  // Enable notifications (call this after app is ready)
  static void enableNotifications() {
    suppressNotifications = false;
    print('NotificationService: Notifications enabled');
  }

  // Disable notifications (call this when app is not ready)
  static void disableNotifications() {
    suppressNotifications = true;
    print('NotificationService: Notifications disabled');
  }
}
