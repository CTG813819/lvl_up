// Fix for notification ID issue - ensure IDs fit in 32-bit integer range

/// Extension to fix notification ID generation
extension NotificationIdFix on int {
  /// Convert any integer to a valid 32-bit notification ID
  int toValidNotificationId() {
    // Use modulo to ensure it fits in 32-bit range (2^31 - 1)
    return this % (1 << 31 - 1);
  }
}

/// Helper class for generating valid notification IDs
class NotificationIdGenerator {
  static int _counter = 1;

  /// Generate a valid notification ID that fits in 32-bit range
  static int generateValidId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final validId = timestamp.toValidNotificationId();
    _counter++;
    return validId + (_counter % 1000); // Add some uniqueness
  }

  /// Convert existing timestamp to valid notification ID
  static int fromTimestamp(int timestamp) {
    return timestamp.toValidNotificationId();
  }
}

/// Fix for mission notification IDs
class MissionNotificationFix {
  /// Fix notification ID for a mission
  static int fixMissionNotificationId(int originalId) {
    return originalId.toValidNotificationId();
  }

  /// Generate new valid notification ID for mission
  static int generateNewMissionNotificationId() {
    return NotificationIdGenerator.generateValidId();
  }
}

/// Usage example:
///
/// // In mission_provider.dart, replace:
/// mission.notificationId = DateTime.now().millisecondsSinceEpoch;
///
/// // With:
/// mission.notificationId = NotificationIdGenerator.generateValidId();
///
/// // Or fix existing IDs:
/// mission.notificationId = MissionNotificationFix.fixMissionNotificationId(mission.notificationId);
