import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:timeago/timeago.dart' as timeago;
import '../providers/notification_provider.dart';
import '../models/ai_notification.dart';

class NotificationCenterScreen extends StatelessWidget {
  const NotificationCenterScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notification Center'),
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all),
            tooltip: 'Mark all as read',
            onPressed: () {
              Provider.of<NotificationProvider>(
                context,
                listen: false,
              ).markAllAsRead();
            },
          ),
          IconButton(
            icon: const Icon(Icons.delete_sweep),
            tooltip: 'Clear all',
            onPressed: () {
              Provider.of<NotificationProvider>(
                context,
                listen: false,
              ).clearAll();
            },
          ),
        ],
      ),
      body: Consumer<NotificationProvider>(
        builder: (context, provider, child) {
          if (provider.notifications.isEmpty) {
            return const Center(
              child: Text(
                'No notifications yet.',
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
            );
          }
          return ListView.builder(
            itemCount: provider.notifications.length,
            itemBuilder: (context, index) {
              final notification = provider.notifications[index];
              return _buildNotificationTile(context, notification, provider);
            },
          );
        },
      ),
    );
  }

  Widget _buildNotificationTile(
    BuildContext context,
    AINotification notification,
    NotificationProvider provider,
  ) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: notification.iconColor.withOpacity(0.2),
        child: Icon(notification.icon, color: notification.iconColor),
      ),
      title: Text(
        notification.title,
        style: TextStyle(
          fontWeight: notification.isRead ? FontWeight.normal : FontWeight.bold,
        ),
      ),
      subtitle: Text(notification.body),
      trailing: Text(
        timeago.format(notification.timestamp),
        style: const TextStyle(fontSize: 12, color: Colors.grey),
      ),
      onTap: () {
        if (!notification.isRead) {
          provider.markAsRead(notification.id);
        }
        // Optionally, navigate to a detail screen
      },
      tileColor: notification.isRead ? null : Colors.blue.withOpacity(0.05),
    );
  }
}
