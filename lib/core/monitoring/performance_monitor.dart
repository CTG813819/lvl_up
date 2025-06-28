import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import '../../providers/app_history_provider.dart';
import '../../mission_provider.dart';

class PerformanceMonitor {
  static final Map<String, List<Duration>> _operationDurations = {};
  static const int _maxStoredDurations = 100;
  static const Duration _minSignificantDuration = Duration(milliseconds: 10);

  static Future<T> measureOperation<T>({
    required String operationName,
    required Future<T> Function() operation,
  }) async {
    final stopwatch = Stopwatch()..start();
    try {
      final result = await operation();
      stopwatch.stop();

      // Only record if the operation took a significant amount of time
      if (stopwatch.elapsed >= _minSignificantDuration) {
        _recordDuration(operationName, stopwatch.elapsed);
      }

      return result;
    } catch (e, stackTrace) {
      stopwatch.stop();
      _recordDuration(operationName, stopwatch.elapsed);

      // Log error using AppHistoryProvider if context is available
      try {
        final context = navigatorKey.currentContext;
        if (context != null) {
          final historyProvider = Provider.of<AppHistoryProvider>(
            context,
            listen: false,
          );
          await historyProvider.logError(
            title: 'Operation Failed',
            description: 'Operation $operationName failed',
            errorCode: 'PERFORMANCE_ERROR',
            errorType: 'Operation Error',
            stackTrace: stackTrace.toString(),
            errorContext: {
              'operationName': operationName,
              'duration': stopwatch.elapsed.inMilliseconds,
            },
          );
        }
      } catch (loggingError) {
        // Silently fail if we can't log - this is a monitoring system
        debugPrint('Failed to log performance error: $loggingError');
      }
      rethrow;
    }
  }

  static void _recordDuration(String operationName, Duration duration) {
    if (!_operationDurations.containsKey(operationName)) {
      _operationDurations[operationName] = [];
    }

    final durations = _operationDurations[operationName]!;

    // If we're at capacity, remove the oldest entry
    if (durations.length >= _maxStoredDurations) {
      durations.removeAt(0);
    }

    // Add the new duration
    durations.add(duration);

    if (kDebugMode) {
      // Log debug information using AppHistoryProvider if context is available
      try {
        final context = navigatorKey.currentContext;
        if (context != null) {
          final historyProvider = Provider.of<AppHistoryProvider>(
            context,
            listen: false,
          );
          historyProvider.logSystem(
            title: 'Performance Debug',
            description:
                'Operation $operationName took ${duration.inMilliseconds}ms',
            metadata: {
              'operationName': operationName,
              'duration': duration.inMilliseconds,
              'timestamp': DateTime.now().toIso8601String(),
            },
          );
        }
      } catch (loggingError) {
        // Silently fail if we can't log - this is a monitoring system
        debugPrint('Failed to log performance debug: $loggingError');
      }
    }
  }

  static Map<String, Duration> getAverageDurations() {
    final averages = <String, Duration>{};
    _operationDurations.forEach((operation, durations) {
      if (durations.isNotEmpty) {
        // Calculate average excluding outliers
        final sortedDurations = List<Duration>.from(durations)
          ..sort((a, b) => a.compareTo(b));

        // Remove top and bottom 10% as outliers
        final removeCount = (durations.length * 0.1).floor();
        final trimmedDurations = sortedDurations.sublist(
          removeCount,
          durations.length - removeCount,
        );

        if (trimmedDurations.isNotEmpty) {
          final total = trimmedDurations.fold<Duration>(
            Duration.zero,
            (sum, duration) => sum + duration,
          );
          averages[operation] = Duration(
            milliseconds: total.inMilliseconds ~/ trimmedDurations.length,
          );
        }
      }
    });
    return averages;
  }

  static void clearDurations() {
    _operationDurations.clear();
  }
}
