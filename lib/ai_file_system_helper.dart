import 'dart:io';

class AIFileSystemHelper {
  /// Recursively list all files under [root]. Optionally filter by [extension] (e.g., '.dart').
  static Future<List<String>> listFilesRecursively(String root, {String? extension}) async {
    final result = <String>[];
    final dir = Directory(root);
    if (!await dir.exists()) return result;
    await for (final entity in dir.list(recursive: true, followLinks: false)) {
      if (entity is File) {
        if (extension == null || entity.path.endsWith(extension)) {
          result.add(entity.path);
        }
      }
    }
    return result;
  }

  /// Watch a directory for file changes (create, modify, delete).
  static Stream<FileSystemEvent> watchDirectory(String root) {
    final dir = Directory(root);
    return dir.watch(recursive: true);
  }

  /// Log file actions for granular AI tracking.
  static void logFileAction(String aiName, String action, String filePath, {String? details}) {
    final now = DateTime.now().toIso8601String();
    print('[AI FS LOG][$now][$aiName][$action] $filePath${details != null ? ' | $details' : ''}');
    // Optionally, add to a persistent log or broadcast to listeners
  }
} 