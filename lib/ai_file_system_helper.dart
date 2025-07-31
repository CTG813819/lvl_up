import 'dart:io';

class AIFileSystemHelper {
  // Recursively list all files under [root]. Optionally filter by [extension] (e.g., '.dart').
  static Future<List<String>> listFilesRecursively(
    String root, {
    String? extension,
  }) async {
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

  // Watch a directory for file changes (create, modify, delete).
  static Stream<FileSystemEvent> watchDirectory(String root) {
    final dir = Directory(root);
    return dir.watch(recursive: true);
  }

  // Log file actions for granular AI tracking.
  static void logFileAction(
    String aiName,
    String action,
    String filePath, {
    String? details,
  }) {
    final now = DateTime.now().toIso8601String();
    print(
      '[AI FS LOG][$now][$aiName][$action] $filePath${details != null ? ' | $details' : ''}',
    );
  // Optionally, add to a persistent log or broadcast to listeners
  }

  // Get all directories that should be watched for AI scanning
  static List<String> getWatchedDirectories() {
    final currentDir = Directory.current.path;
    final directories = <String>[];

  // Standard directories
    final standardDirs = [
      '$currentDir/lib',
      '$currentDir/assets',
      '$currentDir/test',
      '$currentDir/web',
    ];

    for (final dir in standardDirs) {
      if (Directory(dir).existsSync()) {
        directories.add(dir);
      }
    }

  // Terra and Conquest app directories
    final terraConquestDirs = [
      '$currentDir/terra_apps',
      '$currentDir/conquest_apps',
      '$currentDir/generated_apps',
      '$currentDir/ai_generated',
    ];

    for (final dir in terraConquestDirs) {
      if (Directory(dir).existsSync()) {
        directories.add(dir);
        print('[AI FS] Found Terra/Conquest directory: $dir');
      }
    }

  // Check parent directory for Terra/Conquest apps
    final parentDir = Directory('$currentDir/..').absolute.path;
    final parentAppDirs = [
      '$parentDir/terra_apps',
      '$parentDir/conquest_apps',
      '$parentDir/generated_apps',
    ];

    for (final dir in parentAppDirs) {
      if (Directory(dir).existsSync()) {
        directories.add(dir);
        print('[AI FS] Found Terra/Conquest directory in parent: $dir');
      }
    }

    return directories;
  }

  // Scan for new files created by Terra and Conquest
  static Future<List<String>> scanForNewAppFiles() async {
    final newFiles = <String>[];
    final watchedDirs = getWatchedDirectories();

    for (final dir in watchedDirs) {
      try {
        final files = await listFilesRecursively(dir, extension: '.dart');
        for (final file in files) {
  // Check if this is a new file (created in the last hour)
          final fileStat = await File(file).stat();
          final oneHourAgo = DateTime.now().subtract(const Duration(hours: 1));

          if (fileStat.modified.isAfter(oneHourAgo)) {
            newFiles.add(file);
            logFileAction(
              'AI Scanner',
              'new_file_detected',
              file,
              details: 'Created by Terra/Conquest or other AI',
            );
          }
        }
      } catch (e) {
        print('[AI FS] Error scanning directory $dir: $e');
      }
    }

    if (newFiles.isNotEmpty) {
      print(
        '[AI FS] Found ${newFiles.length} new files: ${newFiles.join(', ')}',
      );
    }

    return newFiles;
  }
}
