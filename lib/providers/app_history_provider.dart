import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/app_history.dart';
import 'dart:developer' as developer;

class AppHistoryProvider extends ChangeNotifier {
  static const _historyKey = 'app_history';
  static const _pinKey = 'app_history_pin';
  static const _maxHistoryEntries = 1000;

  List<AppHistoryEntry> _history = [];
  bool _isAuthenticated = false;
  String? _pin;

  List<AppHistoryEntry> get history => List.unmodifiable(_history);
  bool get isAuthenticated => _isAuthenticated;
  bool get isPinSet => _pin != null;

  AppHistoryProvider() {
    _loadHistory();
    _loadPin();
  }

  Future<void> _loadHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getStringList(_historyKey) ?? [];
      _history =
          historyJson
              .map((e) => AppHistoryEntry.fromJson(json.decode(e)))
              .toList();
      developer.log('Loaded ${_history.length} history entries');
      notifyListeners();
    } catch (e, stackTrace) {
      developer.log('Error loading history: $e\n$stackTrace');
      _history = [];
    }
  }

  Future<void> _saveHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = _history.map((e) => json.encode(e.toJson())).toList();
      await prefs.setStringList(_historyKey, historyJson);
      developer.log('Saved ${_history.length} history entries');
    } catch (e, stackTrace) {
      developer.log('Error saving history: $e\n$stackTrace');
    }
  }

  Future<void> _loadPin() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _pin = prefs.getString(_pinKey);
      // If no PIN is set, automatically authenticate
      if (_pin == null) {
        _isAuthenticated = true;
        notifyListeners();
      }
      developer.log('PIN loaded: ${_pin != null ? 'set' : 'not set'}');
    } catch (e) {
      developer.log('Error loading PIN: $e');
    }
  }

  Future<void> setPin(String pin) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_pinKey, pin);
      _pin = pin;
      _isAuthenticated = true;
      notifyListeners();
      developer.log('PIN set successfully');
    } catch (e) {
      developer.log('Error setting PIN: $e');
    }
  }

  Future<bool> verifyPin(String pin) async {
    try {
      if (_pin == null) {
        await setPin(pin);
        return true;
      }
      if (_pin == pin) {
        _isAuthenticated = true;
        notifyListeners();
        developer.log('PIN verified successfully');
        return true;
      }
      developer.log('Invalid PIN entered');
      return false;
    } catch (e) {
      developer.log('Error verifying PIN: $e');
      return false;
    }
  }

  Future<void> addEntry(AppHistoryEntry entry) async {
    try {
      _history.insert(0, entry);

      // Maintain maximum history size
      if (_history.length > _maxHistoryEntries) {
        _history = _history.sublist(0, _maxHistoryEntries);
      }

      await _saveHistory();
      notifyListeners();
      developer.log('Added new history entry: ${entry.title}');
    } catch (e, stackTrace) {
      developer.log('Error adding history entry: $e\n$stackTrace');
    }
  }

  Future<void> logError({
    required String title,
    required String description,
    required String errorCode,
    String? stackTrace,
    String? errorType,
    Map<String, dynamic>? errorContext,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.error(
        title: title,
        description: description,
        errorCode: errorCode,
        stackTrace: stackTrace,
        errorType: errorType,
        errorContext: errorContext,
        metadata: metadata,
      );
      await addEntry(entry);
      developer.log('Logged error: $title');
    } catch (e) {
      developer.log('Error logging error: $e');
    }
  }

  Future<void> logMission({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.mission(
        title: title,
        description: description,
        metadata: metadata,
      );
      await addEntry(entry);
      developer.log('Logged mission event: $title');
    } catch (e) {
      developer.log('Error logging mission: $e');
    }
  }

  Future<void> logSystem({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.system(
        title: title,
        description: description,
        metadata: metadata,
      );
      await addEntry(entry);
      developer.log('Logged system event: $title');
    } catch (e) {
      developer.log('Error logging system event: $e');
    }
  }

  Future<void> logSecurity({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.security(
        title: title,
        description: description,
        metadata: metadata,
      );
      await addEntry(entry);
      developer.log('Logged security event: $title');
    } catch (e) {
      developer.log('Error logging security event: $e');
    }
  }

  Future<void> clearHistory() async {
    try {
      _history.clear();
      await _saveHistory();
      notifyListeners();
      developer.log('History cleared');
    } catch (e) {
      developer.log('Error clearing history: $e');
    }
  }

  List<AppHistoryEntry> getEntriesByCategory(HistoryCategory category) {
    final entries = _history.where((e) => e.category == category).toList();
    developer.log(
      'Retrieved ${entries.length} entries for category: $category',
    );
    return entries;
  }

  List<AppHistoryEntry> searchHistory(String query) {
    final lower = query.toLowerCase();
    final results =
        _history
            .where(
              (e) =>
                  e.title.toLowerCase().contains(lower) ||
                  e.description.toLowerCase().contains(lower) ||
                  (e.errorCode?.toLowerCase().contains(lower) ?? false) ||
                  (e.errorType?.toLowerCase().contains(lower) ?? false),
            )
            .toList();
    developer.log('Search found ${results.length} entries for query: $query');
    return results;
  }

  List<AppHistoryEntry> getErrorsByCode(String errorCode) {
    return _history
        .where(
          (e) =>
              e.category == HistoryCategory.error && e.errorCode == errorCode,
        )
        .toList();
  }

  List<AppHistoryEntry> getErrorsByType(String errorType) {
    return _history
        .where(
          (e) =>
              e.category == HistoryCategory.error && e.errorType == errorType,
        )
        .toList();
  }

  Future<void> loadHistory() async {
    await _loadHistory();
  }

  Future<void> logEntry({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry(
        id: (DateTime.now().millisecondsSinceEpoch % 100000).toString(),
        title: title,
        description: description,
        timestamp: DateTime.now(),
        category: HistoryCategory.entry,
        metadata: metadata,
      );
      await addEntry(entry);
    } catch (e) {
      print('Error logging entry: $e');
    }
  }

  Future<void> logAppLifecycle(String state) async {
    try {
      final entry = AppHistoryEntry.system(
        title: 'App Lifecycle Change',
        description: 'App state changed to: $state',
        metadata: {
          'state': state,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      await addEntry(entry);
    } catch (e) {
      print('Error logging app lifecycle: $e');
    }
  }

  Future<void> logPerformance({
    required String operation,
    required Duration duration,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.system(
        title: 'Performance Event',
        description: 'Operation: $operation took ${duration.inMilliseconds}ms',
        metadata: {
          'operation': operation,
          'duration': duration.inMilliseconds,
          'timestamp': DateTime.now().toIso8601String(),
          ...?metadata,
        },
      );
      await addEntry(entry);
    } catch (e) {
      print('Error logging performance: $e');
    }
  }

  Future<void> logStateChange({
    required String component,
    required String change,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final entry = AppHistoryEntry.system(
        title: 'State Change',
        description: '$component: $change',
        metadata: {
          'component': component,
          'change': change,
          'timestamp': DateTime.now().toIso8601String(),
          ...?metadata,
        },
      );
      await addEntry(entry);
    } catch (e) {
      print('Error logging state change: $e');
    }
  }
}
