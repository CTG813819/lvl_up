import 'dart:collection';
import 'dart:math';
import 'dart:ui';
import 'package:hive/hive.dart';
import 'package:the_codex/mission.dart';
import '../models/entry.dart';
import 'package:synchronized/synchronized.dart';
import 'dart:io';
import 'package:image/image.dart' as img;
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'dart:developer' as developer;
import 'package:path_provider/path_provider.dart';

// Define the Disposable interface
abstract class Disposable {
  void dispose();
}

class EntryManager {
  static final EntryManager _instance = EntryManager._internal();
  factory EntryManager() => _instance;
  EntryManager._internal();

  final _box = Hive.box<Entry>('entries');
  final _imageBox = Hive.box<String>('images');
  int _currentImageIndex = 0;  // Add counter for sequential access

  // Default images that come with the app
  final List<String> _defaultImages = [
    'images/88.jpeg',
    'images/imag1.jpeg',
    'images/berserk_red.jpeg',
    'images/clouds.jpeg',
    'images/gas_station.jpeg',
    'images/horus.jpeg',
    'images/idea_one.jpeg',
    'images/idea_two.jpeg',
    'images/idea_three.jpeg',
    'images/idea_four.jpeg',
    'images/idea_six.jpeg',
    'images/pic_one.jpeg',
    'images/pic_two.jpeg',
    'images/pic_three.jpeg',
    'images/pic.jpeg',
    'images/gmeboy.jpeg',
    'images/new_pic.jpeg',
    'images/random.jpeg',
    'images/picture.jpeg',
    'images/sky.jpeg',
    'images/image.jpeg',
    'images/cam.jpeg',
    'images/butters.jpeg',
    'images/eric.jpeg',
    'images/cartman.jpeg',
    'images/kyle.jpeg',
    'images/kenny.jpeg',
    'images/skull_flow.jpeg',
    'images/bike.jpeg',
    'images/madara.jpeg',
    'images/quote.jpeg',
    'images/kakashi.jpeg',
    'images/neon.jpeg',
    'images/kame.jpeg',
    'images/madara_two.jpeg',
    'images/peace.jpeg',
    'images/unknown.jpeg',
    'images/vinland.jpeg',
    'images/quote_two.jpeg',
    'images/icarus.jpeg',
    'images/guts_peace.jpeg',
    'images/images23.jpeg',
    'images/tkyo.jpeg',
    'images/tokyo_blsm.jpeg',
    'images/guts_sword.jpeg',
    'images/gohan.jpeg',
    'images/scene.jpeg',
    'images/scene_2.jpeg',
    'images/villans.jpeg',
    'images/focus.jpeg',
    'images/rage.jpeg',
    'images/tranquil.jpeg',
  ];

  // Get all images (both default and custom)
  List<String> get _imageList {
    final customImages = _imageBox.values.toList();
    return [..._defaultImages, ...customImages];
  }

  // Get next image sequentially
  String getNextImage() {
    final images = _imageList;
    if (images.isEmpty) {
      return 'images/default_mission.jpeg'; // Fallback image
    }
    final image = images[_currentImageIndex];
    _currentImageIndex = (_currentImageIndex + 1) % images.length;
    return image;
  }

  // Reset the image index
  void resetImageIndex() {
    _currentImageIndex = 0;
  }

  List<Entry> get entries => _box.values.toList();

  String intToRoman(int num) {
    const List<String> romanSymbols = [
      'M',
      'CM',
      'D',
      'CD',
      'C',
      'XC',
      'L',
      'XL',
      'V',
      'IV',
      'I',
    ];
    const List<int> values = [1000, 900, 500, 400, 100, 90, 50, 40, 5, 4, 1];
    String result = '';
    for (int i = 0; i < values.length; i++) {
      while (num >= values[i]) {
        result += romanSymbols[i];
        num -= values[i];
      }
    }
    return result;
  }

  Future<bool> addEntry(String content) async {
    try {
      final id = _box.isEmpty ? 1 : _box.values.last.id + 1;
      final title = intToRoman(id);
      final imageUrl = _imageList[Random().nextInt(_imageList.length)];
      final entry = Entry(
        id: id,
        title: title,
        content: content,
        imageUrl: imageUrl,
        createdAt: DateTime.now().toIso8601String().substring(0, 10),
      );
      await _box.put(id, entry);
      return true;
    } catch (e) {
      developer.log('Error adding entry', error: e);
      return false;
    }
  }

  Future<bool> updateEntry(int id, String content) async {
    try {
      final entry = _box.get(id);
      if (entry == null) return false;
      final imageUrl = _imageList[Random().nextInt(_imageList.length)];
      final updatedEntry = Entry(
        id: id,
        title: entry.title,
        content: content,
        imageUrl: imageUrl,
        createdAt: entry.createdAt,
      );
      await _box.put(id, updatedEntry);
      return true;
    } catch (e) {
      developer.log('Error updating entry', error: e);
      return false;
    }
  }

  Future<bool> deleteEntry(int id) async {
    try {
      await _box.delete(id);
      return true;
    } catch (e) {
      developer.log('Error deleting entry', error: e);
      return false;
    }
  }

  Future<void> clearAllEntries() async {
    try {
      await _box.clear();
    } catch (e) {
      developer.log('Error clearing entries', error: e);
      rethrow;
    }
  }

  // Get all images (both default and custom)
  List<String> get imageList => _imageList;

  Future<void> addCustomImage(String imagePath) async {
    try {
      // Read the image file
      final File imageFile = File(imagePath);
      final bytes = await imageFile.readAsBytes();
      
      // Decode the image
      final image = img.decodeImage(bytes);
      if (image == null) {
        throw Exception('Failed to decode image');
      }

      // Get the app's documents directory
      final appDir = await getApplicationDocumentsDirectory();
      final imagesDir = Directory('${appDir.path}/images');
      if (!await imagesDir.exists()) {
        await imagesDir.create(recursive: true);
      }

      // Generate a unique filename with .jpeg extension
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final newImagePath = '${imagesDir.path}/image_$timestamp.jpeg';

      // Convert and save as JPEG
      final jpegBytes = img.encodeJpg(image, quality: 85);
      final newImageFile = File(newImagePath);
      await newImageFile.writeAsBytes(jpegBytes);

      // Store the path in Hive
      final key = timestamp.toString();
      await _imageBox.put(key, newImagePath);
    } catch (e) {
      developer.log('Error adding custom image', error: e);
      rethrow;
    }
  }

  Future<void> removeCustomImage(String imagePath) async {
    try {
      final key = _imageBox.values.toList().indexOf(imagePath);
      if (key != -1) {
        await _imageBox.deleteAt(key);
      }
    } catch (e) {
      developer.log('Error removing custom image', error: e);
      rethrow;
    }
  }

  Future<void> clearCustomImages() async {
    try {
      await _imageBox.clear();
    } catch (e) {
      developer.log('Error clearing custom images', error: e);
      rethrow;
    }
  }

  final _backgroundTaskManager = BackgroundTaskManager();

  Future<void> syncMission(MissionData mission) async {
    await _backgroundTaskManager.scheduleTask(
      () => _processMissionSync(mission),
      TaskPriority.high,
      taskId: 'sync_mission_${mission.notificationId}',
    );
  }

  Future<void> _processMissionSync(MissionData mission) async {
    try {
      // Implementation of mission sync logic
      await Future.delayed(const Duration(milliseconds: 100));
    } catch (e, stackTrace) {
      developer.log(
        'Error syncing mission ${mission.title}',
        error: e,
        stackTrace: stackTrace,
      );
      rethrow;
    }
  }

  void dispose() {
    _backgroundTaskManager.cancelAllTasks();
  }
}

// 1. Add a proper state management class
class MissionState {
  final List<MissionData> missions;
  final bool isLoading;
  final String? error;
  final DateTime lastSync;

  MissionState({
    required this.missions,
    this.isLoading = false,
    this.error,
    required this.lastSync,
  });

  MissionState copyWith({
    List<MissionData>? missions,
    bool? isLoading,
    String? error,
    DateTime? lastSync,
  }) {
    return MissionState(
      missions: missions ?? this.missions,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
      lastSync: lastSync ?? this.lastSync,
    );
  }
}

// 2. Add proper synchronization mechanism
class MissionSyncManager {
  final _lock = Lock();
  final _syncQueue = Queue<Future<void> Function()>();
  bool _isProcessing = false;

  Future<void> syncMission(MissionData mission) async {
    await _lock.synchronized(() async {
      _syncQueue.add(() => _processMissionSync(mission));
      if (!_isProcessing) {
        await _processQueue();
      }
    });
  }

  Future<void> _processQueue() async {
    _isProcessing = true;
    while (_syncQueue.isNotEmpty) {
      final operation = _syncQueue.removeFirst();
      await operation();
    }
    _isProcessing = false;
  }

  Future<void> _processMissionSync(MissionData mission) async {
    // Implementation of mission sync logic
    await Future.delayed(
      Duration(milliseconds: 100),
    ); // Placeholder for actual sync logic
  }
}

// 3. Add proper transaction handling
class MissionTransaction {
  final Box<dynamic> _db;

  MissionTransaction(this._db);

  Future<void> executeTransaction(MissionData mission) async {
    try {
      // Update mission
      await _db.put('mission_${mission.id}', mission.toJson());

      // Update history
      final historyKey =
          'history_${mission.id}_${DateTime.now().millisecondsSinceEpoch}';
      await _db.put(historyKey, {
        'mission_id': mission.id,
        'timestamp': DateTime.now().toIso8601String(),
        'state': mission.isCompleted ? 'completed' : 'in_progress',
      });

      // Update notifications
      await _updateNotifications(mission);
    } catch (e) {
      if (kDebugMode) {
        print('Error in mission transaction: $e');
      }
      // If any operation fails, we should clean up
      await _rollback(mission);
      rethrow;
    }
  }

  Future<void> _rollback(MissionData mission) async {
    try {
      // Remove the mission update
      await _db.delete('mission_${mission.id}');

      // Remove the history entry
      final historyKey =
          'history_${mission.id}_${DateTime.now().millisecondsSinceEpoch}';
      await _db.delete(historyKey);
    } catch (e) {
      print('Error during rollback: $e');
    }
  }

  Future<void> _updateNotifications(MissionData mission) async {
    try {
      final notifications = FlutterLocalNotificationsPlugin();

      // Cancel existing notification if any
      if (mission.scheduledNotificationId != null) {
        await notifications.cancel(mission.scheduledNotificationId!);
      }

      // Only schedule new notification if mission is not completed
      if (!mission.isCompleted) {
        final androidDetails = AndroidNotificationDetails(
          NotificationChannels.mission,
          'Mission Notifications',
          channelDescription: 'Notifications for mission updates',
          importance: Importance.max,
          priority: Priority.high,
        );

        final notificationDetails = NotificationDetails(
          android: androidDetails,
        );

        // Schedule notification for next day if mission is not completed
        final scheduledTime = DateTime.now().add(const Duration(days: 1));
        await notifications.zonedSchedule(
          mission.notificationId,
          'Mission Reminder',
          'Don\'t forget to complete: ${mission.title}',
          tz.TZDateTime.from(scheduledTime, tz.local),
          notificationDetails,
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
          matchDateTimeComponents: DateTimeComponents.time,
        );

        // Update mission with the notification ID we used
        mission.scheduledNotificationId = mission.notificationId;
      }
    } catch (e) {
      print('Error updating notifications: $e');
      // Don't throw the error to prevent transaction rollback
      // Just log it and continue
    }
  }
}

// 1. Add image optimization and caching
class ImageOptimizer {
  final _cache = <String, Uint8List>{};

  Future<Uint8List> optimizeImage(File imageFile) async {
    final cacheKey = imageFile.path;
    if (_cache.containsKey(cacheKey)) {
      return _cache[cacheKey]!;
    }

    final bytes = await imageFile.readAsBytes();
    final image = img.decodeImage(bytes);
    if (image != null) {
      final resized = img.copyResize(
        image,
        width: 800,
        height: 800,
        interpolation: img.Interpolation.linear,
      );
      final optimized = img.encodeJpg(resized, quality: 85);
      _cache[cacheKey] = Uint8List.fromList(optimized);
      return _cache[cacheKey]!;
    }
    return bytes;
  }
}

// 2. Add background processing
class MissionProcessor {
  Future<void> processMission(MissionData mission) async {
    await compute(_heavyComputation, mission);
  }

  static Future<void> _heavyComputation(MissionData mission) async {
    // Heavy computation logic
  }
}

// 3. Add proper caching
class MissionCache {
  final _cache = <String, MissionData>{};
  final _expiryTimes = <String, DateTime>{};

  void cacheMission(MissionData mission) {
    _cache[mission.id!] = mission;
    _expiryTimes[mission.id!] = DateTime.now().add(const Duration(minutes: 30));
  }

  MissionData? getMission(String id) {
    if (_expiryTimes.containsKey(id) &&
        DateTime.now().isAfter(_expiryTimes[id]!)) {
      _cache.remove(id);
      _expiryTimes.remove(id);
      return null;
    }
    return _cache[id];
  }
}

// 1. Add comprehensive error handling
class MissionError extends Error {
  final String message;
  final String? code;
  final dynamic originalError;

  MissionError(this.message, {this.code, this.originalError});

  @override
  String toString() => 'MissionError: $message (Code: $code)';
}

// 2. Add retry mechanism
class RetryHandler {
  Future<T> withRetry<T>(
    Future<T> Function() operation, {
    int maxAttempts = 3,
    Duration delay = const Duration(seconds: 1),
  }) async {
    int attempts = 0;
    while (attempts < maxAttempts) {
      try {
        return await operation();
      } catch (e) {
        attempts++;
        if (attempts == maxAttempts) rethrow;
        await Future.delayed(delay * attempts);
      }
    }
    throw MissionError('Max retry attempts reached');
  }
}

// 3. Add error reporting
class ErrorReporter {
  static final ErrorReporter _instance = ErrorReporter._internal();
  factory ErrorReporter() => _instance;
  ErrorReporter._internal();

  Future<void> reportError(MissionError error) async {
    // Log error
    developer.log(
      error.toString(),
      error: error.originalError,
      stackTrace: StackTrace.current,
    );

    // For now, just log to console since we don't have analytics set up
    print('Error reported: ${error.message}');
    if (error.code != null) {
      print('Error code: ${error.code}');
    }
    if (error.originalError != null) {
      print('Original error: ${error.originalError}');
    }
  }
}

// 1. Add resource cleanup
class ResourceManager {
  final _disposables = <Disposable>[];

  void registerDisposable(Disposable disposable) {
    _disposables.add(disposable);
  }

  void dispose() {
    for (final disposable in _disposables) {
      disposable.dispose();
    }
    _disposables.clear();
  }
}

// 2. Add proper image cleanup
class ImageManager {
  final _imageCache = <String, Image>{};

  void dispose() {
    for (final image in _imageCache.values) {
      image.dispose();
    }
    _imageCache.clear();
  }

  Future<void> preloadImages(List<String> paths) async {
    for (final path in paths) {
      if (!_imageCache.containsKey(path)) {
        final image = await _loadImage(path);
        _imageCache[path] = image;
      }
    }
  }

  Future<Image> _loadImage(String path) async {
    try {
      final ByteData data = await rootBundle.load(path);
      final Uint8List bytes = data.buffer.asUint8List();
      final codec = await instantiateImageCodec(bytes);
      final frame = await codec.getNextFrame();
      return frame.image;
    } catch (e) {
      developer.log(
        'Error loading image: $path',
        error: e,
        stackTrace: StackTrace.current,
      );
      // Return a placeholder image or rethrow based on your needs
      rethrow;
    }
  }
}

// Define the NotificationRequest class
class NotificationRequest {
  final int id;
  final String title;
  final String body;
  final NotificationDetails details;
  final DateTime? scheduledTime;

  NotificationRequest({
    required this.id,
    required this.title,
    required this.body,
    required this.details,
    this.scheduledTime,
  });
}

// 1. Add batch notification processing
class NotificationManager {
  final _notificationQueue = <NotificationRequest>[];
  Timer? _processTimer;

  void queueNotification(NotificationRequest request) {
    _notificationQueue.add(request);
    _scheduleProcessing();
  }

  void _scheduleProcessing() {
    _processTimer?.cancel();
    _processTimer = Timer(const Duration(milliseconds: 300), _processQueue);
  }

  Future<void> _processQueue() async {
    final requests = List<NotificationRequest>.from(_notificationQueue);
    _notificationQueue.clear();

    for (final request in requests) {
      await _scheduleNotification(request);
    }
  }

  Future<void> _scheduleNotification(NotificationRequest request) async {
    try {
      final notifications = FlutterLocalNotificationsPlugin();

      if (request.scheduledTime != null) {
        await notifications.zonedSchedule(
          request.id,
          request.title,
          request.body,
          tz.TZDateTime.from(request.scheduledTime!, tz.local),
          request.details,
          androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
          matchDateTimeComponents: DateTimeComponents.time,
        );
      } else {
        await notifications.show(
          request.id,
          request.title,
          request.body,
          request.details,
        );
      }
    } catch (e) {
      developer.log(
        'Error scheduling notification',
        error: e,
        stackTrace: StackTrace.current,
      );
    }
  }
}

// 2. Add notification grouping
class NotificationGrouper {
  final _groupKey = 'com.example.lvl_up.missions';
  final _notifications = FlutterLocalNotificationsPlugin();

  Future<void> groupNotifications(List<NotificationRequest> requests) async {
    final summary = _createSummaryNotification(requests);
    await _notifications.show(
      summary.id,
      summary.title,
      summary.body,
      summary.details,
    );

    for (final request in requests) {
      await _notifications.show(
        request.id,
        request.title,
        request.body,
        request.details,
      );
    }
  }

  NotificationRequest _createSummaryNotification(
    List<NotificationRequest> requests,
  ) {
    final completedCount =
        requests
            .where((r) => r.body.toLowerCase().contains('completed'))
            .length;
    final totalCount = requests.length;

    final androidDetails = AndroidNotificationDetails(
      NotificationChannels.mission,
      'Mission Notifications',
      channelDescription: 'Notifications for mission updates',
      importance: Importance.max,
      priority: Priority.high,
      groupKey: _groupKey,
      setAsGroupSummary: true,
      groupAlertBehavior: GroupAlertBehavior.all,
    );

    final notificationDetails = NotificationDetails(android: androidDetails);

    return NotificationRequest(
      id: DateTime.now().millisecondsSinceEpoch.hashCode,
      title: 'Mission Summary',
      body: 'You have $completedCount out of $totalCount missions completed',
      details: notificationDetails,
    );
  }
}

class BackgroundTaskManager {
  static const int _maxConcurrentTasks = 3;
  static const Duration _taskTimeout = Duration(seconds: 30);

  final List<_BackgroundTask> _taskQueue = [];
  final _runningTasks = <_BackgroundTask>{};
  final _lock = Lock();
  bool _isProcessing = false;

  Future<void> scheduleTask(
    Future<void> Function() task,
    TaskPriority priority, {
    String? taskId,
    Duration? timeout,
  }) async {
    final backgroundTask = _BackgroundTask(
      task: task,
      priority: priority,
      id: taskId ?? DateTime.now().millisecondsSinceEpoch.toString(),
      timeout: timeout ?? _taskTimeout,
    );

    await _lock.synchronized(() async {
      _taskQueue.add(backgroundTask);
      _taskQueue.sort((a, b) => b.priority.index.compareTo(a.priority.index));
      if (!_isProcessing) {
        _processQueue();
      }
    });
  }

  Future<void> _processQueue() async {
    _isProcessing = true;

    while (_taskQueue.isNotEmpty &&
        _runningTasks.length < _maxConcurrentTasks) {
      final task = _taskQueue.removeAt(0);
      _runningTasks.add(task);

      unawaited(
        _executeTask(task).then((_) {
          _runningTasks.remove(task);
          if (_taskQueue.isNotEmpty) {
            _processQueue();
          } else {
            _isProcessing = false;
          }
        }),
      );
    }

    if (_taskQueue.isEmpty) {
      _isProcessing = false;
    }
  }

  Future<void> _executeTask(_BackgroundTask task) async {
    try {
      await task.task().timeout(
        task.timeout,
        onTimeout: () {
          throw TimeoutException(
            'Task ${task.id} timed out after ${task.timeout}',
          );
        },
      );
    } catch (e, stackTrace) {
      developer.log(
        'Error executing background task ${task.id}',
        error: e,
        stackTrace: stackTrace,
      );
      // Implement retry logic for failed tasks
      if (task.retryCount < 3) {
        task.retryCount++;
        _taskQueue.add(task);
        _taskQueue.sort((a, b) => b.priority.index.compareTo(a.priority.index));
      }
    }
  }

  Future<void> cancelTask(String taskId) async {
    await _lock.synchronized(() {
      _taskQueue.removeWhere((task) => task.id == taskId);
    });
  }

  Future<void> cancelAllTasks() async {
    await _lock.synchronized(() {
      _taskQueue.clear();
      _runningTasks.clear();
      _isProcessing = false;
    });
  }
}

class _BackgroundTask implements Comparable<_BackgroundTask> {
  final Future<void> Function() task;
  final TaskPriority priority;
  final String id;
  final Duration timeout;
  int retryCount = 0;

  _BackgroundTask({
    required this.task,
    required this.priority,
    required this.id,
    required this.timeout,
  });

  @override
  int compareTo(_BackgroundTask other) {
    return other.priority.index.compareTo(priority.index);
  }
}

enum TaskPriority { high, medium, low }
