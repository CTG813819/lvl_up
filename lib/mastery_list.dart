import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'entry_manager.dart';
import 'dart:math';
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class MasteryEntry {
  final String id;
  String title;
  final double targetValue;
  final List<MasteryProgress> progress;
  final String imageUrl;
  int currentLevel;
  double nextLevelTarget;

  // Add maxLevel getter
  int get maxLevel => 100; // Maximum level is 100

  MasteryEntry({
    required this.id,
    required this.title,
    this.targetValue = 10000.0,
    List<MasteryProgress>? progress,
    required this.imageUrl,
    this.currentLevel = 0,
    this.nextLevelTarget = 100.0,
  }) : progress = progress ?? [];

  // Convert minutes to hours for leveling calculations
  double _convertToHours(double minutes) {
    return minutes / 60.0;
  }

  // Format minutes into HH:MM format
  String formatTime(double minutes) {
    final hours = (minutes / 60).floor();
    final remainingMinutes = (minutes % 60).round();
    return '${hours.toString().padLeft(2, '0')}:${remainingMinutes.toString().padLeft(2, '0')}';
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'targetValue': targetValue,
      'progress': progress.map((p) => p.toJson()).toList(),
      'imageUrl': imageUrl,
      'currentLevel': currentLevel,
      'nextLevelTarget': nextLevelTarget,
    };
  }

  factory MasteryEntry.fromJson(Map<String, dynamic> json) {
    return MasteryEntry(
      id: json['id'],
      title: json['title'],
      targetValue: json['targetValue'],
      progress:
          (json['progress'] as List)
              .map((p) => MasteryProgress.fromJson(p))
              .toList(),
      imageUrl: json['imageUrl'],
      currentLevel: json['currentLevel'] ?? 0,
      nextLevelTarget: json['nextLevelTarget'] ?? 100.0,
    );
  }

  void updateLevel(double totalProgress) {
    // Convert total progress from minutes to hours for leveling
    final totalHours = _convertToHours(totalProgress);
    while (totalHours >= nextLevelTarget && currentLevel < 100) {
      currentLevel++;
      nextLevelTarget *= 2;
    }
  }

  String getLevelDescription() {
    if (currentLevel == 0) return 'Level 1 (0-6000 minutes)';
    if (currentLevel == 1) return 'Level 2 (6000-12000 minutes)';
    if (currentLevel == 2) return 'Level 3 (12000-24000 minutes)';
    if (currentLevel >= 3 && currentLevel < 100) {
      final currentTarget = 6000 * (1 << (currentLevel - 1));
      final nextTarget = currentTarget * 2;
      return 'Level ${currentLevel + 1} ($currentTarget-$nextTarget minutes)';
    }
    return 'Master Level (600,000 minutes)';
  }

  // Get total progress in hours
  double getTotalProgressHours() {
    final totalMinutes = progress.fold<double>(
      0.0,
      (sum, progress) => sum + progress.value,
    );
    return _convertToHours(totalMinutes);
  }

  // Get total progress in minutes
  double getTotalProgressMinutes() {
    return progress.fold<double>(0.0, (sum, progress) => sum + progress.value);
  }
}

class MasteryProgress {
  final String subject;
  final double value; // This is now in minutes
  final DateTime timestamp;

  MasteryProgress({
    required this.subject,
    required this.value,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'subject': subject,
      'value': value,
      'timestamp': timestamp.toIso8601String(),
    };
  }

  factory MasteryProgress.fromJson(Map<String, dynamic> json) {
    return MasteryProgress(
      subject: json['subject'],
      value: json['value'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }
}

class MasteryProvider extends ChangeNotifier {
  final List<MasteryEntry> _entries = [];
  final EntryManager _entryManager = EntryManager();
  static const String _storageKey = 'mastery_entries';
  // Track the last progress entry for each mission/subtask to prevent duplicates
  final Map<String, DateTime> _lastProgressTime = {};

  List<MasteryEntry> get entries => _entries;

  MasteryProvider() {
    _loadEntries();
  }

  Future<void> _loadEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final entriesJson = prefs.getStringList(_storageKey) ?? [];
    _entries.clear();
    _entries.addAll(
      entriesJson.map((json) => MasteryEntry.fromJson(jsonDecode(json))),
    );
    // Recalculate all progress after loading
    for (var entry in _entries) {
      _recalculateProgress(entry);
    }
    notifyListeners();
  }

  // Public method to load entries
  Future<void> loadEntries() async {
    await _loadEntries();
  }

  void _recalculateProgress(MasteryEntry entry) {
    // Calculate total progress in minutes
    final totalProgress = entry.progress.fold<double>(
      0.0,
      (sum, progress) => sum + progress.value,
    );

    // Update level based on total progress (converted to hours)
    entry.currentLevel = 0;
    entry.nextLevelTarget = 100.0;

    while (entry._convertToHours(totalProgress) >= entry.nextLevelTarget &&
        entry.currentLevel < 100) {
      entry.currentLevel++;
      entry.nextLevelTarget *= 2;
    }
  }

  Future<void> _saveEntries() async {
    final prefs = await SharedPreferences.getInstance();
    final entriesJson =
        _entries.map((entry) => jsonEncode(entry.toJson())).toList();
    await prefs.setStringList(_storageKey, entriesJson);
    notifyListeners();
  }

  String getRandomImage() {
    final images = _entryManager.imageList;
    return images[Random().nextInt(images.length)];
  }

  Future<void> addEntry(String title) async {
    final entry = MasteryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      imageUrl: getRandomImage(),
    );
    _entries.add(entry);
    await _saveEntries();
    notifyListeners();
  }

  Future<void> addProgress(String entryId, String subject, double value) async {
    final entry = _entries.firstWhere((e) => e.id == entryId);

    // Ensure value is positive
    if (value <= 0) {
      print('Warning: Attempted to add non-positive mastery value: $value');
      return;
    }

    // Create a unique key for this progress entry
    final progressKey = '$entryId:$subject';
    final now = DateTime.now();

    // Check if we've added progress for this entry/subject recently (within 1 second)
    if (_lastProgressTime.containsKey(progressKey)) {
      final lastTime = _lastProgressTime[progressKey]!;
      if (now.difference(lastTime).inSeconds < 1) {
        print('Warning: Skipping duplicate progress entry for $subject');
        return;
      }
    }

    // Add the new progress entry (value is in minutes)
    entry.progress.add(
      MasteryProgress(
        subject: subject,
        value: value, // Store the raw minute value
        timestamp: now,
      ),
    );

    // Update the last progress time
    _lastProgressTime[progressKey] = now;

    // Recalculate progress and level
    _recalculateProgress(entry);

    // Save changes and notify listeners immediately
    await _saveEntries();
    notifyListeners();
  }

  double getTotalProgress(String entryId) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    return entry.getTotalProgressMinutes(); // Return minutes
  }

  // Get recent progress entries for a mastery
  List<MasteryProgress> getRecentProgress(String entryId, {int limit = 5}) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    final sortedProgress = List<MasteryProgress>.from(entry.progress)
      ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return sortedProgress.take(limit).toList();
  }

  // Get progress for a specific time period
  double getProgressForPeriod(String entryId, DateTime start, DateTime end) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    return entry.progress
        .where((p) => p.timestamp.isAfter(start) && p.timestamp.isBefore(end))
        .fold<double>(0.0, (sum, progress) => sum + progress.value);
  }

  // Get today's progress
  double getTodayProgress(String entryId) {
    final now = DateTime.now();
    final startOfDay = DateTime(now.year, now.month, now.day);
    return getProgressForPeriod(entryId, startOfDay, now);
  }

  // Get this week's progress
  double getWeekProgress(String entryId) {
    final now = DateTime.now();
    final startOfWeek = now.subtract(Duration(days: now.weekday - 1));
    return getProgressForPeriod(entryId, startOfWeek, now);
  }

  // Get this month's progress
  double getMonthProgress(String entryId) {
    final now = DateTime.now();
    final startOfMonth = DateTime(now.year, now.month, 1);
    return getProgressForPeriod(entryId, startOfMonth, now);
  }

  // Get monthly progress data for all months since creation
  Map<DateTime, double> getMonthlyProgress(String entryId) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    if (entry.progress.isEmpty) return {};

    // Get the earliest progress entry
    final earliestProgress = entry.progress.reduce(
      (a, b) => a.timestamp.isBefore(b.timestamp) ? a : b,
    );

    // Start from the beginning of the month when the first progress was recorded
    final startDate = DateTime(
      earliestProgress.timestamp.year,
      earliestProgress.timestamp.month,
      1,
    );

    // End at the current month
    final endDate = DateTime.now();

    // Create a map to store monthly progress
    final monthlyProgress = <DateTime, double>{};

    // Initialize all months with 0 progress
    var currentDate = startDate;
    while (currentDate.isBefore(endDate) ||
        (currentDate.year == endDate.year &&
            currentDate.month == endDate.month)) {
      monthlyProgress[DateTime(currentDate.year, currentDate.month, 1)] = 0.0;
      currentDate = DateTime(currentDate.year, currentDate.month + 1, 1);
    }

    // Calculate progress for each month
    for (final progress in entry.progress) {
      final monthKey = DateTime(
        progress.timestamp.year,
        progress.timestamp.month,
        1,
      );
      monthlyProgress[monthKey] =
          (monthlyProgress[monthKey] ?? 0.0) + progress.value;
    }

    return monthlyProgress;
  }

  int getCurrentLevel(String entryId) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    return entry.currentLevel;
  }

  double getNextLevelTarget(String entryId) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    return entry.nextLevelTarget;
  }

  // Get progress percentage towards next level
  double getProgressPercentage(String entryId) {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    final totalProgress = getTotalProgress(entryId);
    final previousLevelTarget =
        entry.currentLevel == 0 ? 0.0 : entry.nextLevelTarget / 2;
    final progressInCurrentLevel =
        entry._convertToHours(totalProgress) - previousLevelTarget;
    final levelRange = entry.nextLevelTarget - previousLevelTarget;
    return (progressInCurrentLevel / levelRange * 100).clamp(0, 100);
  }

  Future<void> editEntry(String entryId, String newTitle) async {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    entry.title = newTitle;
    await _saveEntries();
    notifyListeners();
  }

  Future<void> resetHours(String entryId) async {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    // Clear all progress entries
    entry.progress.clear();
    // Reset level and target
    entry.currentLevel = 0;
    entry.nextLevelTarget = 100.0;
    // Clear any tracked progress times for this entry
    _lastProgressTime.removeWhere((key, _) => key.startsWith('$entryId:'));
    // Save changes
    await _saveEntries();
    notifyListeners();
  }

  Future<void> subtractHours(String entryId, double hoursToSubtract) async {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    if (entry.progress.isEmpty) return;

    // Convert hours to minutes
    final minutesToSubtract = hoursToSubtract * 60;
    double remainingMinutes = minutesToSubtract;

    // Remove progress entries until we've subtracted enough minutes
    while (remainingMinutes > 0 && entry.progress.isNotEmpty) {
      final lastProgress = entry.progress.last;
      if (lastProgress.value <= remainingMinutes) {
        // Remove entire entry
        remainingMinutes -= lastProgress.value;
        entry.progress.removeLast();
      } else {
        // Partially reduce the last entry
        entry.progress[entry.progress.length - 1] = MasteryProgress(
          subject: lastProgress.subject,
          value: lastProgress.value - remainingMinutes,
          timestamp: lastProgress.timestamp,
        );
        remainingMinutes = 0;
      }
    }

    // Recalculate progress and level
    _recalculateProgress(entry);

    // Save changes
    await _saveEntries();
    notifyListeners();
  }

  Future<void> subtractMinute(String entryId) async {
    await subtractHours(entryId, 1.0 / 60);
  }

  Future<void> deleteEntry(String entryId) async {
    _entries.removeWhere((entry) => entry.id == entryId);
    await _saveEntries();
    notifyListeners();
  }

  Future<void> subtractMinutes(String entryId, double minutes) async {
    final entry = _entries.firstWhere((e) => e.id == entryId);
    if (entry.progress.isEmpty) return;

    double remainingMinutes = minutes;
    while (remainingMinutes > 0 && entry.progress.isNotEmpty) {
      final lastProgress = entry.progress.last;
      if (lastProgress.value <= remainingMinutes) {
        // Remove entire entry
        remainingMinutes -= lastProgress.value;
        entry.progress.removeLast();
      } else {
        // Partially reduce the last entry
        entry.progress[entry.progress.length - 1] = MasteryProgress(
          subject: lastProgress.subject,
          value: lastProgress.value - remainingMinutes,
          timestamp: lastProgress.timestamp,
        );
        remainingMinutes = 0;
      }
    }

    // Recalculate progress and level
    _recalculateProgress(entry);

    // Save changes
    await _saveEntries();
    notifyListeners();
  }
}

class MasteryList extends StatelessWidget {
  const MasteryList({Key? key}) : super(key: key);

  void _showEditDialog(BuildContext context, MasteryEntry entry) {
    final titleController = TextEditingController(text: entry.title);
    final subtractController = TextEditingController();
    final masteryProvider = Provider.of<MasteryProvider>(
      context,
      listen: false,
    );
    double currentMinutes = masteryProvider.getTotalProgress(entry.id);
    String selectedUnit = 'minutes'; // Default to minutes

    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            backgroundColor: Colors.grey[900],
            title: const Text(
              'Edit Mastery',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: titleController,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    labelText: 'Title',
                    labelStyle: TextStyle(color: Colors.white),
                    enabledBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.white24),
                    ),
                    focusedBorder: UnderlineInputBorder(
                      borderSide: BorderSide(color: Colors.purpleAccent),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.black,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Current Time:',
                        style: TextStyle(color: Colors.white, fontSize: 16),
                      ),
                      Text(
                        entry.formatTime(currentMinutes),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: subtractController,
                        keyboardType: const TextInputType.numberWithOptions(
                          decimal: true,
                        ),
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Amount to Subtract',
                          labelStyle: const TextStyle(color: Colors.white),
                          filled: true,
                          fillColor: Colors.grey[850],
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    DropdownButton<String>(
                      value: selectedUnit,
                      dropdownColor: Colors.black,
                      style: const TextStyle(color: Colors.white),
                      items: const [
                        DropdownMenuItem(
                          value: 'minutes',
                          child: Text('Minutes'),
                        ),
                        DropdownMenuItem(value: 'hours', child: Text('Hours')),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          selectedUnit = value;
                        }
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        onPressed: () async {
                          double subtractValue =
                              double.tryParse(subtractController.text) ?? 0;
                          if (subtractValue > 0) {
                            // Convert to minutes if hours selected
                            if (selectedUnit == 'hours') {
                              subtractValue *= 60;
                            }
                            if (subtractValue <= currentMinutes) {
                              await masteryProvider.subtractMinutes(
                                entry.id,
                                subtractValue,
                              );
                              if (context.mounted) Navigator.of(context).pop();
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Cannot subtract more than current time',
                                  ),
                                ),
                              );
                            }
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Enter a valid number to subtract',
                                ),
                              ),
                            );
                          }
                        },
                        child: const Text('Subtract Time'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        onPressed: () async {
                          await masteryProvider.resetHours(entry.id);
                          if (context.mounted) Navigator.of(context).pop();
                        },
                        child: const Text('Reset Time'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.purpleAccent),
                ),
              ),
              TextButton(
                onPressed: () async {
                  await masteryProvider.editEntry(
                    entry.id,
                    titleController.text,
                  );
                  if (context.mounted) Navigator.of(context).pop();
                },
                child: const Text(
                  'Save',
                  style: TextStyle(color: Colors.purpleAccent),
                ),
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => MasteryProvider(),
      child: Consumer<MasteryProvider>(
        builder: (context, provider, child) {
          return Scaffold(
            backgroundColor: Colors.black,
            appBar: AppBar(
              backgroundColor: Colors.black,
              title: const Text(
                'Mastery',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              iconTheme: const IconThemeData(color: Colors.white),
            ),
            body:
                provider.entries.isEmpty
                    ? const Center(
                      child: Text(
                        'No mastery entries yet. Add one!',
                        style: TextStyle(color: Colors.white, fontSize: 20),
                      ),
                    )
                    : ListView.builder(
                      itemCount: provider.entries.length,
                      itemBuilder: (context, index) {
                        final entry = provider.entries[index];
                        return Card(
                          color: Colors.grey[900],
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          child: ListTile(
                            title: Text(
                              entry.title,
                              style: const TextStyle(color: Colors.white),
                            ),
                            subtitle: Text(
                              entry.getLevelDescription(),
                              style: TextStyle(color: Colors.grey[400]),
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: const Icon(
                                    Icons.edit,
                                    color: Colors.white,
                                  ),
                                  onPressed:
                                      () => _showEditDialog(context, entry),
                                ),
                                IconButton(
                                  icon: const Icon(
                                    Icons.delete,
                                    color: Colors.red,
                                  ),
                                  onPressed:
                                      () => _showDeleteDialog(
                                        context,
                                        provider,
                                        entry,
                                      ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            floatingActionButton: FloatingActionButton(
              onPressed: () => _showAddEntryDialog(context),
              backgroundColor: Colors.black,
              child: const Icon(Icons.add, color: Colors.white),
            ),
          );
        },
      ),
    );
  }

  void _showDeleteDialog(
    BuildContext context,
    MasteryProvider provider,
    MasteryEntry entry,
  ) {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: const Text(
              'Delete Mastery',
              style: TextStyle(color: Colors.white),
            ),
            content: Text(
              'Are you sure you want to delete "${entry.title}"?',
              style: const TextStyle(color: Colors.white),
            ),
            actions: [
              TextButton(
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.white),
                ),
                onPressed: () => Navigator.pop(context),
              ),
              TextButton(
                child: const Text(
                  'Delete',
                  style: TextStyle(color: Colors.red),
                ),
                onPressed: () async {
                  await provider.deleteEntry(entry.id);
                  if (context.mounted) Navigator.pop(context);
                },
              ),
            ],
          ),
    );
  }

  Future<void> _showAddEntryDialog(BuildContext context) async {
    final controller = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('New Mastery'),
            content: TextField(
              controller: controller,
              decoration: const InputDecoration(
                labelText: 'Enter mastery title',
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(controller.text),
                child: const Text('Save'),
              ),
            ],
          ),
    );

    if (result != null && result.isNotEmpty) {
      context.read<MasteryProvider>().addEntry(result);
    }
  }
}
