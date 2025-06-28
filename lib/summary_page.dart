import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/mastery_list.dart';
import 'package:the_codex/mission.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:the_codex/mission_provider.dart' hide MissionProvider;

class DailySummary {
  final DateTime date;
  final int missionsMade;
  final double totalProgress; // Raw sum of progress values for the day
  final double
  dailyProgressPercentage; // Average daily completion percentage across active missions
  final double? previousDayProgress;

  DailySummary({
    required this.date,
    required this.missionsMade,
    required this.totalProgress,
    required this.dailyProgressPercentage,
    this.previousDayProgress,
  });

  DailySummary copyWith({
    DateTime? date,
    int? missionsMade,
    double? totalProgress,
    double? dailyProgressPercentage,
    double? previousDayProgress,
  }) {
    return DailySummary(
      date: date ?? this.date,
      missionsMade: missionsMade ?? this.missionsMade,
      totalProgress: totalProgress ?? this.totalProgress,
      dailyProgressPercentage:
          dailyProgressPercentage ?? this.dailyProgressPercentage,
      previousDayProgress: previousDayProgress ?? this.previousDayProgress,
    );
  }
}

class SummaryPage extends StatefulWidget {
  const SummaryPage({super.key});

  @override
  State<SummaryPage> createState() => _SummaryPageState();
}

class _SummaryPageState extends State<SummaryPage> with WidgetsBindingObserver {
  int? selectedYear;
  int? selectedMonth;
  final Map<int, List<int>> _yearMonthMap = {};
  StreamController<void>? _calculationController;
  StreamSubscription<void>? _calculationSubscription;
  Map<MissionType, double> _cachedCompletionByType = {};
  bool _isCalculating = false;
  Map<DateTime, DailySummary> _cachedDailySummaries =
      {}; // New cache for daily summaries

  // Add caching for calculations
  final Map<String, double> _calculationCache = {};

  // Define max bar height for the chart

  late PageController _pageController; // Add PageController
  StreamSubscription? _missionSubscription; // Add this line
  Timer? _refreshTimer; // Add timer for periodic refresh

  // Utility to save and load daily progress
  Future<void> _saveDailyProgress(DateTime date, double progress) async {
    final prefs = await SharedPreferences.getInstance();
    final key = 'progress_${date.toIso8601String().substring(0, 10)}';
    await prefs.setDouble(key, progress);

    // Also store the timestamp of when this progress was saved
    await prefs.setString('${key}_timestamp', DateTime.now().toIso8601String());
  }

  Future<double?> _loadDailyProgress(DateTime date) async {
    final prefs = await SharedPreferences.getInstance();
    final key = 'progress_${date.toIso8601String().substring(0, 10)}';
    return prefs.getDouble(key);
  }

  void _scheduleMidnightSave() {
    final now = DateTime.now();
    final tomorrow = DateTime(now.year, now.month, now.day + 1);
    final duration = tomorrow.difference(now);

    Future.delayed(duration, () {
      _handleMidnightProgressSave();
      _scheduleMidnightSave(); // Schedule next midnight save
    });
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeYearMonthMap();
    final now = DateTime.now();
    setState(() {
      selectedYear = now.year;
      selectedMonth = now.month;
    });
    _initializeCalculationStream();
    _initializeMissionListener();
    _initializeRefreshTimer();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _runCalculations();
      _backfillDailyProgress(); // Backfill on init
    });
    _pageController = PageController(initialPage: _getCurrentWeekIndex());
    _scheduleMidnightSave(); // Schedule midnight save
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _calculationController?.close();
    _calculationSubscription?.cancel();
    _missionSubscription?.cancel(); // Add this line
    _refreshTimer?.cancel(); // Cancel the refresh timer
    _pageController.dispose(); // Dispose PageController
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Clear cache when dependencies change
    _calculationCache.clear();
    _cachedDailySummaries.clear();
    _cachedCompletionByType.clear();
    // Recalculate when dependencies change
    _runCalculations();
    // Refresh current day progress
    _refreshCurrentDayProgress();
  }

  void _initializeCalculationStream() {
    _calculationController = StreamController<void>.broadcast();
    _calculationSubscription = _calculationController?.stream.listen((_) {
      // Clear cache when recalculating
      _calculationCache.clear();
      _cachedDailySummaries.clear();
      _cachedCompletionByType.clear();
      _runCalculations();
    });
  }

  void _initializeMissionListener() {
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    _missionSubscription = missionProvider.missionStream.listen((_) {
      // Clear cache and recalculate when missions change
      _calculationCache.clear();
      _cachedDailySummaries.clear();
      _cachedCompletionByType.clear();
      if (mounted) {
        // Force immediate recalculation
        _runCalculations();
        // Force rebuild of the weekly chart
        setState(() {});
        // Refresh current day progress immediately
        _refreshCurrentDayProgress();
      }
    });

    // Add listener for mission updates
    missionProvider.addListener(() {
      if (mounted) {
        _calculationCache.clear();
        _cachedDailySummaries.clear();
        _cachedCompletionByType.clear();
        _runCalculations();
        _refreshCurrentDayProgress();
      }
    });
  }

  void _initializeRefreshTimer() {
    // Cancel existing timer if any
    _refreshTimer?.cancel();

    // Create a new timer that fires every minute
    _refreshTimer = Timer.periodic(const Duration(minutes: 1), (timer) {
      if (mounted) {
        final now = DateTime.now();
        final today = DateTime(now.year, now.month, now.day);

        // Check if we've crossed midnight
        if (selectedYear == now.year && selectedMonth == now.month) {
          // Clear today's progress at midnight
          if (now.hour == 0 && now.minute == 0) {
            _saveDailyProgress(today, 0.0);
            _calculationCache.clear();
            _cachedDailySummaries.clear();
            _cachedCompletionByType.clear();
          }

          // Always refresh calculations for current month
          _runCalculations();
          _refreshCurrentDayProgress();
        }
      }
    });
  }

  void _refreshCurrentDayProgress() {
    if (!mounted) return;

    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final missions = missionProvider.missions;

    // Only refresh if we're viewing the current month
    if (selectedYear == now.year && selectedMonth == now.month) {
      // Recalculate progress for today
      final currentDayProgress = _calculateDailyAverageProgress(
        missions,
        now.year,
        now.month,
      );

      // Update the cached daily summaries with the new current day progress
      if (currentDayProgress.containsKey(today)) {
        setState(() {
          _cachedDailySummaries[today] = DailySummary(
            date: today,
            missionsMade: _cachedDailySummaries[today]?.missionsMade ?? 0,
            totalProgress: currentDayProgress[today]!,
            dailyProgressPercentage: currentDayProgress[today]!,
          );
        });
      }
    }
  }

  Future<void> _runCalculations() async {
    if (_isCalculating) return;

    // Always recalculate when month/year changes or on timer
    final cacheKey = 'monthly_${selectedYear}_${selectedMonth}';
    if (_calculationCache.containsKey(cacheKey)) {
      _calculationCache.remove(cacheKey);
    }

    _isCalculating = true;

    try {
      if (selectedYear != null && selectedMonth != null) {
        final missionProvider = Provider.of<MissionProvider>(
          context,
          listen: false,
        );
        final missions = missionProvider.missions;

        // Run calculations in background
        await Future.wait([
          Future(() {
            _calculateMonthlyCompletion(
              missions,
              selectedYear!,
              selectedMonth!,
            );
            if (mounted) {
              setState(() {});
            }
          }),
          Future(() {
            final completionByType = _calculateCompletionByType(
              missions,
              selectedYear!,
              selectedMonth!,
            );
            if (mounted) {
              setState(() {
                _cachedCompletionByType = completionByType;
              });
            }
          }),
          Future(() async {
            final dailySummaries = await _calculateMonthlyDailySummary(
              missions,
              selectedYear!,
              selectedMonth!,
              DateTime.now(),
            );
            if (mounted) {
              setState(() {
                _cachedDailySummaries = dailySummaries;
              });
            }
          }),
        ]);
      }
    } finally {
      _isCalculating = false;
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      final now = DateTime.now();
      final today = DateTime(now.year, now.month, now.day);
      // Backfill progress for previous days
      _backfillDailyProgress();
      // Reset today's progress if not saved
      _loadDailyProgress(today).then((lastSavedProgress) {
        if (lastSavedProgress == null) {
          _saveDailyProgress(today, 0.0);
        }
      });

      // Clear all caches and recalculate when app is resumed
      _calculationCache.clear();
      _cachedDailySummaries.clear();
      _cachedCompletionByType.clear();

      // Check if we need to reset today's progress (if app was closed overnight)
      if (selectedYear == now.year && selectedMonth == now.month) {
        final lastSavedProgress = _loadDailyProgress(today);
        if (lastSavedProgress != null) {
          final lastSavedDate = DateTime.fromMillisecondsSinceEpoch(
            int.parse(lastSavedProgress.toString().split('_').last),
          );
          if (!_isSameDay(lastSavedDate, today)) {
            _saveDailyProgress(today, 0.0);
          }
        }
      }

      _calculationController?.add(null);
      _refreshCurrentDayProgress();
    }
  }

  void _initializeYearMonthMap() {
    final now = DateTime.now();
    final currentYear = now.year;

    // Populate last 5 years
    for (int year = currentYear - 4; year <= currentYear; year++) {
      _yearMonthMap[year] = List.generate(12, (index) => index + 1);
    }
  }

  double _calculateMissionProgress(MissionData mission) {
    // For failed missions, still calculate progress but mark as failed
    if (mission.hasFailed) {
      double progress = 0.0;
      if (mission.subtasks.isNotEmpty) {
        progress = _calculateSubtaskProgress(mission.subtasks);
      } else if (mission.isCounterBased) {
        progress = _calculateCounterProgressWithDailyAverage(
          mission,
          selectedYear ?? DateTime.now().year,
          selectedMonth ?? DateTime.now().month,
        );
      } else {
        progress = _calculateRegularMissionProgress(mission);
      }
      return progress;
    }

    // Handle persistent missions
    if (mission.type == MissionType.persistent) {
      if (mission.subtasks.isEmpty) {
        return mission.isCompleted ? 1.0 : 0.0;
      }
      // For persistent missions, all subtasks must be completed
      return mission.subtasks.every(
            (s) => s.currentCompletions >= s.requiredCompletions,
          )
          ? 1.0
          : 0.0;
    }

    // Handle missions with subtasks
    if (mission.subtasks.isNotEmpty) {
      return _calculateSubtaskProgress(mission.subtasks);
    }

    // Handle counter-based missions
    if (mission.isCounterBased) {
      return _calculateCounterProgress(
        mission.currentCount,
        mission.targetCount,
      );
    }

    // Handle regular missions
    return _calculateRegularMissionProgress(mission);
  }

  double _calculateSubtaskProgress(List<MissionSubtask> subtasks) {
    if (subtasks.isEmpty) return 0.0;

    double totalProgress = 0.0;
    int validSubtasks = 0;

    for (final subtask in subtasks) {
      double subtaskProgress = 0.0;

      if (subtask.isCounterBased) {
        // For counter-based subtasks, use the new daily average calculation
        if (subtask.requiredCompletions == 0) {
          // Calculate daily average and monthly estimate
          final periodStart = DateTime(
            selectedYear ?? DateTime.now().year,
            selectedMonth ?? DateTime.now().month,
            1,
          );
          final periodEnd = DateTime(
            selectedYear ?? DateTime.now().year,
            selectedMonth ?? DateTime.now().month + 1,
            0,
          );

          // For subtasks, we'll use the current count and creation date
          if (subtask.createdAt != null) {
            final daysSinceCreation =
                periodEnd.difference(subtask.createdAt!).inDays;
            if (daysSinceCreation > 0) {
              // Calculate daily average based on current count and days since creation
              final dailyAverage = subtask.currentCount / daysSinceCreation;

              // Calculate total days in the month
              final daysInMonth = periodEnd.day;

              // Calculate active days (days since creation in this month)
              final activeDays = daysSinceCreation.clamp(0, daysInMonth);

              // Calculate current total for the month
              final currentTotal = subtask.currentCount.toDouble();

              // Calculate weekly pattern
              final weeklyPattern = <int, double>{};
              for (int day = 1; day <= activeDays; day++) {
                final date = DateTime(periodStart.year, periodStart.month, day);
                final weekday = date.weekday;
                weeklyPattern[weekday] =
                    (weeklyPattern[weekday] ?? 0) + dailyAverage;
              }

              // Project remaining days using weekly pattern
              double projectedTotal = currentTotal;
              for (int day = activeDays + 1; day <= daysInMonth; day++) {
                final date = DateTime(periodStart.year, periodStart.month, day);
                final weekday = date.weekday;
                projectedTotal += weeklyPattern[weekday] ?? dailyAverage;
              }

              // Use a reasonable cap for progress (e.g., 100 counts per month)
              const monthlyCap = 100.0;
              subtaskProgress = (projectedTotal / monthlyCap).clamp(0.0, 1.0);
            } else {
              // If created today, use current count
              subtaskProgress = subtask.currentCount > 0 ? 1.0 : 0.0;
            }
          }
        } else {
          subtaskProgress = _calculateCounterProgress(
            subtask.currentCount,
            subtask.requiredCompletions,
          );
        }
      } else {
        // For non-counter subtasks, consider partial progress
        if (subtask.requiredCompletions > 0) {
          final completionRatio =
              subtask.currentCompletions / subtask.requiredCompletions;
          if (completionRatio >= 0.25) {
            // If at least 25% complete, consider it as partial progress
            subtaskProgress = completionRatio;
          } else {
            subtaskProgress = 0.0;
          }
        } else {
          subtaskProgress = subtask.currentCompletions > 0 ? 1.0 : 0.0;
        }
      }

      // Only count subtasks that have some form of target or progress
      if (subtask.requiredCompletions > 0 ||
          (subtask.isCounterBased
                  ? subtask.currentCount
                  : subtask.currentCompletions) >
              0) {
        totalProgress += subtaskProgress;
        validSubtasks++;
      }
    }

    return validSubtasks > 0
        ? (totalProgress / validSubtasks).clamp(0.0, 1.0)
        : 0.0;
  }

  double _calculateCounterProgress(int currentValue, int? targetValue) {
    if (targetValue != null && targetValue > 0) {
      // Has target - calculate progress as ratio
      return (currentValue / targetValue).clamp(0.0, 1.0);
    } else if (currentValue > 0) {
      // No target but has progress - calculate monthly prediction based on daily/weekly patterns
      final now = DateTime.now();
      final daysSinceCreation = now.difference(DateTime.now()).inDays;

      if (daysSinceCreation > 0) {
        // Calculate average daily progress
        final dailyAverage = currentValue / daysSinceCreation;

        // Calculate weekly pattern (assuming 5 active days per week)
        final weeklyPattern = dailyAverage * 5;

        // Predict monthly progress (4 weeks)
        final predictedMonthly = weeklyPattern * 4;

        // Cap at 100% if predicted monthly is high
        return (predictedMonthly / 100).clamp(0.0, 1.0);
      }
      return 1.0; // If no days have passed, consider it complete if there's any progress
    }
    return 0.0; // No progress
  }

  // New method to calculate counter progress with daily averages
  double _calculateCounterProgressWithDailyAverage(
    MissionData mission,
    int year,
    int month,
  ) {
    if (!mission.isCounterBased || mission.currentCount == 0) {
      return 0.0;
    }

    final periodStart = DateTime(year, month, 1);
    final periodEnd = DateTime(year, month + 1, 0);
    final now = DateTime.now();

    // Get the progress history for this month
    final progressMap = mission.getProgressForDateRange(periodStart, periodEnd);

    if (progressMap.isEmpty) {
      return 0.0;
    }

    // Calculate daily averages and patterns
    final dailyCounts = <DateTime, double>{};
    final failedDays = <DateTime>[];
    double totalCount = 0.0;
    int activeDays = 0;
    int totalDays = 0;

    // First pass: collect all data
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      if (date.isAfter(mission.createdAt!.subtract(const Duration(days: 1))) &&
          date.isBefore(
            _getMissionEndDate(mission).add(const Duration(days: 1)),
          )) {
        totalDays++;

        if (progressMap.containsKey(date)) {
          final count = progressMap[date]!.toDouble();
          dailyCounts[date] = count;
          totalCount += count;
          activeDays++;
        }

        // Check for failed days
        if (mission.hasFailed && mission.lastCompleted != null) {
          final lastCompleted = mission.lastCompleted!;
          // If mission was completed after this date, it means it failed on this date
          if (lastCompleted.isAfter(date) &&
              lastCompleted.year == year &&
              lastCompleted.month == month) {
            failedDays.add(date);
          }
        }
      }
    }

    // If we have a target, calculate progress
    if (mission.targetCount != null && mission.targetCount > 0) {
      // Calculate daily target based on mission type
      double dailyTarget = 0.0;
      if (mission.type == MissionType.daily) {
        dailyTarget = mission.targetCount / totalDays;
      } else if (mission.type == MissionType.weekly) {
        dailyTarget = mission.targetCount / (totalDays / 7);
      } else {
        dailyTarget = mission.targetCount / totalDays;
      }

      // Calculate progress considering failed days
      double adjustedProgress = 0.0;
      for (final entry in dailyCounts.entries) {
        final date = entry.key;
        final count = entry.value;

        // Skip failed days in progress calculation
        if (!failedDays.contains(date)) {
          adjustedProgress += (count / dailyTarget).clamp(0.0, 1.0);
        }
      }

      // Calculate final progress
      final validDays = totalDays - failedDays.length;
      return validDays > 0 ? (adjustedProgress / validDays) * 100 : 0.0;
    }

    // If no target, calculate based on patterns
    if (activeDays > 0) {
      // Calculate daily average
      final dailyAverage = totalCount / activeDays;

      // Calculate weekly pattern
      final weeklyPattern = <int, double>{};
      for (final entry in dailyCounts.entries) {
        final weekday = entry.key.weekday;
        weeklyPattern[weekday] = (weeklyPattern[weekday] ?? 0) + entry.value;
      }

      // Calculate average per weekday
      for (final weekday in weeklyPattern.keys) {
        weeklyPattern[weekday] =
            weeklyPattern[weekday]! /
            dailyCounts.keys.where((d) => d.weekday == weekday).length;
      }

      // Project remaining days
      double projectedTotal = totalCount;

      for (int day = 1; day <= periodEnd.day; day++) {
        final date = DateTime(year, month, day);
        if (!dailyCounts.containsKey(date) &&
            !failedDays.contains(date) &&
            date.isAfter(now)) {
          // Use weekly pattern if available, otherwise use daily average
          final weekday = date.weekday;
          projectedTotal += weeklyPattern[weekday] ?? dailyAverage;
        }
      }

      // Calculate final progress
      final totalPossibleDays = totalDays - failedDays.length;
      if (totalPossibleDays > 0) {
        // Use a reasonable cap for progress (e.g., 100 counts per month)
        const monthlyCap = 100.0;
        return (projectedTotal / monthlyCap).clamp(0.0, 1.0) * 100;
      }
    }

    return 0.0;
  }

  double _calculateRegularMissionProgress(MissionData mission) {
    // Check if mission is explicitly completed
    if (mission.isCompleted) {
      return 1.0;
    }

    // Check if mission was completed in the current selected month/year
    if (mission.lastCompleted != null &&
        selectedYear != null &&
        selectedMonth != null) {
      final lastCompleted = mission.lastCompleted!;
      if (lastCompleted.year == selectedYear &&
          lastCompleted.month == selectedMonth) {
        return 1.0;
      }
    }

    // For missions that might have been completed but we're viewing a different month
    // we need to check if the mission was active and completed during the selected period
    if (mission.lastCompleted != null && mission.createdAt != null) {
      final creationDate = mission.createdAt!;
      final completionDate = mission.lastCompleted!;
      final selectedDate = DateTime(
        selectedYear ?? DateTime.now().year,
        selectedMonth ?? DateTime.now().month,
      );

      // If mission was created before or during selected month and completed during selected month
      if (creationDate.isBefore(selectedDate.add(const Duration(days: 32))) &&
          completionDate.year == selectedDate.year &&
          completionDate.month == selectedDate.month) {
        return 1.0;
      }
    }

    // For missions with subtasks, calculate partial progress
    if (mission.subtasks.isNotEmpty) {
      return _calculateSubtaskProgress(mission.subtasks);
    }

    // For counter-based missions without subtasks
    if (mission.isCounterBased) {
      return _calculateCounterProgress(
        mission.currentCount,
        mission.targetCount,
      );
    }

    // For simple missions, consider partial progress based on creation date
    if (mission.createdAt != null) {
      final daysSinceCreation =
          DateTime.now().difference(mission.createdAt!).inDays;
      if (daysSinceCreation > 0) {
        // Consider progress based on how long the mission has been active
        // Cap at 25% for partial progress
        return (0.25 * (daysSinceCreation / 30)).clamp(0.0, 0.25);
      }
    }

    return 0.0;
  }

  // Enhanced version that also considers the mission's lifecycle for the selected period

  double _calculateMonthlyCompletion(
    List<MissionData> missions,
    int year,
    int month,
  ) {
    if (missions.isEmpty) return 0.0;

    final periodStart = DateTime(year, month, 1);
    final periodEnd = DateTime(year, month + 1, 0);
    final now = DateTime.now();
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );

    double totalMonthlyProgress = 0.0;
    int daysWithProgress = 0;

    // Get all missions for the month including history
    final monthMissions = missionProvider.getMissionHistoryByDateRange(
      periodStart,
      periodEnd,
    );
    final completedMissions = missionProvider.getCompletedMissionsByDateRange(
      periodStart,
      periodEnd,
    );

    // Combine all missions
    final allMissions =
        [...missions, ...monthMissions, ...completedMissions].toSet().toList();

    // Calculate progress for each day
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);

      // Skip future days
      if (date.isAfter(now)) continue;

      // Get missions active on this day
      final activeMissions =
          allMissions.where((mission) {
            if (mission.createdAt == null) return false;
            final missionEnd = _getMissionEndDate(mission);
            return date.isAfter(
                  mission.createdAt!.subtract(const Duration(days: 1)),
                ) &&
                date.isBefore(missionEnd.add(const Duration(days: 1)));
          }).toList();

      if (activeMissions.isEmpty) continue;

      double dayProgress = 0.0;
      int validMissions = 0;

      for (final mission in activeMissions) {
        double missionProgress = 0.0;
        double missionWeight = 1.0;

        // Weight missions by type
        switch (mission.type) {
          case MissionType.daily:
            missionWeight = 1.2;
            break;
          case MissionType.weekly:
            missionWeight = 1.5;
            break;
          case MissionType.persistent:
            missionWeight = 1.3;
            break;
          default:
            missionWeight = 1.0;
        }

        // Check if mission failed on this day
        bool isFailed = false;
        if (mission.hasFailed && mission.lastCompleted != null) {
          final lastCompleted = mission.lastCompleted!;
          if (lastCompleted.isAfter(date) &&
              lastCompleted.year == year &&
              lastCompleted.month == month) {
            isFailed = true;
          }
        }

        if (!isFailed) {
          // Get progress for this specific day
          final progress = mission.getProgressForDate(date);

          if (progress != null) {
            if (mission.subtasks.isNotEmpty) {
              // Calculate subtask progress
              double subtaskTotal = 0.0;
              int validSubtasks = 0;

              for (final subtask in mission.subtasks) {
                double subtaskProgress = 0.0;

                if (subtask.isCounterBased) {
                  final progressMap = mission.getProgressForDateRange(
                    DateTime(date.year, date.month, date.day),
                    DateTime(date.year, date.month, date.day, 23, 59, 59),
                  );

                  if (progressMap.isNotEmpty) {
                    final dayProgress = progressMap.values.first;
                    if (subtask.requiredCompletions > 0) {
                      subtaskProgress = (dayProgress /
                              subtask.requiredCompletions)
                          .clamp(0.0, 1.0);
                    } else {
                      subtaskProgress = dayProgress > 0 ? 1.0 : 0.0;
                    }
                  }
                } else {
                  if (subtask.requiredCompletions > 0) {
                    subtaskProgress = (progress / subtask.requiredCompletions)
                        .clamp(0.0, 1.0);
                  } else {
                    subtaskProgress = progress > 0 ? 1.0 : 0.0;
                  }
                }

                subtaskTotal += subtaskProgress;
                validSubtasks++;
              }

              missionProgress =
                  validSubtasks > 0 ? subtaskTotal / validSubtasks : 0.0;
            } else if (mission.isCounterBased) {
              if (mission.targetCount > 0) {
                missionProgress = (progress / mission.targetCount).clamp(
                  0.0,
                  1.0,
                );
              } else if (mission.currentCount > 0) {
                missionProgress = 1.0;
              }
            } else if (mission.isCompleted) {
              missionProgress = 1.0;
            }
          }
        }

        // Apply mission weight and add to day's total
        if (missionProgress > 0 || isFailed) {
          dayProgress += missionProgress * missionWeight;
          validMissions++;
        }
      }

      // Calculate day's average progress
      if (validMissions > 0) {
        final dayAverage = (dayProgress / validMissions) * 100;
        totalMonthlyProgress += dayAverage;
        daysWithProgress++;
      }
    }

    // Calculate final monthly percentage
    return daysWithProgress > 0 ? totalMonthlyProgress / daysWithProgress : 0.0;
  }

  DateTime _getMissionEndDate(MissionData mission) {
    if (mission.type == MissionType.daily) {
      return mission.createdAt!.add(const Duration(days: 1));
    } else if (mission.type == MissionType.weekly) {
      // Find the next Sunday
      final daysUntilSunday =
          (DateTime.sunday - mission.createdAt!.weekday) % 7;
      return mission.createdAt!.add(Duration(days: daysUntilSunday));
    } else {
      // For simple missions, they don't expire
      return DateTime.now().add(const Duration(days: 365));
    }
  }

  Map<MissionType, double> _calculateCompletionByType(
    List<MissionData> missions,
    int year,
    int month,
  ) {
    final Map<MissionType, double> completionByType = {
      MissionType.daily: 0.0,
      MissionType.weekly: 0.0,
      MissionType.simple: 0.0,
      MissionType.persistent: 0.0,
    };

    final periodStart = DateTime(year, month, 1);
    final periodEnd = DateTime(year, month + 1, 0);

    // Filter missions that were active during this specific month
    final monthMissions =
        missions.where((mission) {
          if (mission.createdAt == null) return false;

          // Mission must have been created before or during this month
          final createdInMonth =
              mission.createdAt!.year == year &&
              mission.createdAt!.month == month;
          final createdBeforeMonth = mission.createdAt!.isBefore(periodStart);

          // Mission must not have been completed before this month
          final completedBeforeMonth =
              mission.lastCompleted != null &&
              mission.lastCompleted!.isBefore(periodStart);

          return (createdInMonth || createdBeforeMonth) &&
              !completedBeforeMonth;
        }).toList();

    // Group missions by type
    final missionsByType = <MissionType, List<MissionData>>{};
    for (final type in MissionType.values) {
      missionsByType[type] =
          monthMissions.where((m) => m.type == type).toList();
    }

    // Calculate completion for each type
    for (final entry in missionsByType.entries) {
      final type = entry.key;
      final typeMissions = entry.value;

      if (typeMissions.isNotEmpty) {
        double totalProgress = 0.0;
        int validMissions = 0;

        for (final mission in typeMissions) {
          double missionProgress = 0.0;

          // Get progress for the entire period at once
          final progressMap = mission.getProgressForDateRange(
            periodStart,
            periodEnd,
          );

          if (progressMap.isNotEmpty) {
            // Use the highest progress value in the period
            missionProgress = progressMap.values.reduce(
              (a, b) => a > b ? a : b,
            );
          } else if (mission.hasFailed) {
            missionProgress = 0.0;
          } else {
            missionProgress = _calculateMissionProgress(mission);
          }

          if (missionProgress > 0 || mission.hasFailed) {
            totalProgress += missionProgress;
            validMissions++;
          }
        }

        completionByType[type] =
            validMissions > 0 ? (totalProgress / validMissions) * 100 : 0.0;
      }
    }

    return completionByType;
  }

  // New method to calculate daily summaries for the chart
  Future<Map<DateTime, DailySummary>> _calculateMonthlyDailySummary(
    List<MissionData> missions,
    int year,
    int month,
    DateTime now,
  ) async {
    final dailySummaries = <DateTime, DailySummary>{};
    final periodEnd = DateTime(year, month + 1, 0); // Last day of the month

    // Initialize daily summaries for all days in the month
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      dailySummaries[date] = DailySummary(
        date: date,
        missionsMade: 0,
        totalProgress: 0.0,
        dailyProgressPercentage: 0.0,
      );
    }

    // Get all currently active missions
    final currentlyActiveMissions =
        missions.where((mission) {
          if (mission.createdAt == null) return false;
          final missionEnd = _getMissionEndDate(mission);
          return now.isAfter(
                mission.createdAt!.subtract(const Duration(days: 1)),
              ) &&
              now.isBefore(missionEnd.add(const Duration(days: 1)));
        }).toList();

    // Calculate cumulative missions created per day
    final missionsCreatedCount = <DateTime, int>{};
    for (final mission in missions) {
      if (mission.createdAt != null &&
          mission.createdAt!.year == year &&
          mission.createdAt!.month == month) {
        final date = DateTime(
          mission.createdAt!.year,
          mission.createdAt!.month,
          mission.createdAt!.day,
        );
        missionsCreatedCount.update(
          date,
          (value) => value + 1,
          ifAbsent: () => 1,
        );
      }
    }

    // Calculate cumulative missions for each day
    int cumulativeMissionsToday = 0;
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      cumulativeMissionsToday += missionsCreatedCount[date] ?? 0;
      dailySummaries.update(
        date,
        (summary) => summary.copyWith(missionsMade: cumulativeMissionsToday),
      );
    }

    // Calculate daily mission progress with weighted completion status
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      double totalProgress = 0.0;
      int totalMissionsForDay = 0;

      // Get all missions that were active on this day, prioritizing currently active missions
      final activeMissions =
          [
            ...currentlyActiveMissions,
            ...missions.where((m) => !currentlyActiveMissions.contains(m)),
          ].where((mission) {
            if (mission.createdAt == null) return false;
            final missionEnd = _getMissionEndDate(mission);
            return date.isAfter(
                  mission.createdAt!.subtract(const Duration(days: 1)),
                ) &&
                date.isBefore(missionEnd.add(const Duration(days: 1)));
          }).toList();

      totalMissionsForDay = activeMissions.length;

      for (final mission in activeMissions) {
        // Check if mission failed on this day
        bool isFailed = false;
        if (mission.hasFailed && mission.lastCompleted != null) {
          final lastCompleted = mission.lastCompleted!;
          if (lastCompleted.isAfter(date) &&
              lastCompleted.year == year &&
              lastCompleted.month == month) {
            isFailed = true;
          }
        }

        // Calculate weighted progress based on mission status
        double weightedProgress = 0.0;

        if (isFailed) {
          // Failed missions count as 0%
          weightedProgress = 0.0;
        } else {
          // Get mission progress for this specific day
          final progress = mission.getProgressForDate(date);

          if (progress != null) {
            if (progress >= 1.0) {
              // Completed missions count as 100%
              weightedProgress = 1.0;
            } else if (progress >= 0.5) {
              // Partially completed missions count as 50%
              weightedProgress = 0.5;
            } else {
              // Incomplete missions count as 0%
              weightedProgress = 0.0;
            }
          }
        }

        // Apply mission type weight
        double missionWeight = 1.0;
        switch (mission.type) {
          case MissionType.daily:
            missionWeight = 1.2;
            break;
          case MissionType.weekly:
            missionWeight = 1.5;
            break;
          case MissionType.persistent:
            missionWeight = 1.3;
            break;
          default:
            missionWeight = 1.0;
        }

        totalProgress += weightedProgress * missionWeight;
      }

      // Calculate final daily progress percentage
      final dailyCompletionPercentage =
          totalMissionsForDay > 0
              ? (totalProgress / totalMissionsForDay) * 100
              : 0.0;

      // Only update progress for past days or current day
      if (!date.isAfter(now)) {
        dailySummaries.update(
          date,
          (summary) => summary.copyWith(
            totalProgress: totalProgress,
            dailyProgressPercentage: dailyCompletionPercentage,
          ),
        );
      }
    }

    // Set previous day's progress for coloring the daily progress bar
    double? previousDayOverallProgress;
    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      final summary = dailySummaries[date]!;
      dailySummaries.update(
        date,
        (s) => s.copyWith(previousDayProgress: previousDayOverallProgress),
      );
      previousDayOverallProgress = summary.dailyProgressPercentage;
    }

    return dailySummaries;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text('Summary', style: TextStyle(color: Colors.white)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Consumer2<MissionProvider, MasteryProvider>(
        builder: (
          BuildContext context,
          MissionProvider missionProvider,
          MasteryProvider masteryProvider,
          Widget? child,
        ) {
          // Force rebuild when missions change
          final missions = missionProvider.missions;
          final now = DateTime.now();

          // Update selected year/month if viewing current month and it changed
          if (selectedYear == now.year && selectedMonth == now.month) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                setState(() {});
              }
            });
          }

          // Ensure we have a year and month selected
          if (selectedYear == null) {
            selectedYear = now.year;
          }
          if (selectedMonth == null) {
            selectedMonth = now.month;
          }

          return Column(
            children: [
              // Year/Month Selection
              Container(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    // Year Dropdown
                    DropdownButton<int>(
                      value: selectedYear,
                      hint: const Text(
                        'Select Year',
                        style: TextStyle(color: Colors.white),
                      ),
                      dropdownColor: Colors.black,
                      style: const TextStyle(color: Colors.white),
                      items:
                          _yearMonthMap.keys.map((year) {
                            return DropdownMenuItem<int>(
                              value: year,
                              child: Text(year.toString()),
                            );
                          }).toList(),
                      onChanged: (year) {
                        setState(() {
                          selectedYear = year;
                          selectedMonth = null;
                        });
                      },
                    ),
                    const SizedBox(width: 16),
                    // Month Dropdown
                    if (selectedYear != null)
                      DropdownButton<int>(
                        value: selectedMonth,
                        hint: const Text(
                          'Select Month',
                          style: TextStyle(color: Colors.white),
                        ),
                        dropdownColor: Colors.black,
                        style: const TextStyle(color: Colors.white),
                        items:
                            _yearMonthMap[selectedYear]!.map((month) {
                              return DropdownMenuItem<int>(
                                value: month,
                                child: Text(
                                  DateFormat(
                                    'MMMM',
                                  ).format(DateTime(2000, month)),
                                ),
                              );
                            }).toList(),
                        onChanged: (month) {
                          setState(() {
                            selectedMonth = month;
                          });
                        },
                      ),
                  ],
                ),
              ),

              // Summary Content
              if (selectedYear != null && selectedMonth != null)
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Overall Progress
                        _buildOverallProgress(missions),
                        const SizedBox(height: 24),

                        // Progress by Type
                        _buildProgressByType(missions),
                        const SizedBox(height: 24),

                        // Mastery Levels
                        _buildMasteryLevels(masteryProvider),
                        const SizedBox(height: 24),

                        // Mission List
                        _buildMissionList(missions),
                      ],
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildOverallProgress(List<MissionData> missions) {
    if (selectedYear == null || selectedMonth == null)
      return const SizedBox.shrink();

    final periodStart = DateTime(selectedYear!, selectedMonth!, 1);
    final periodEnd = DateTime(selectedYear!, selectedMonth! + 1, 0);
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );

    // Get all missions for the month including history
    final monthMissions = missionProvider.getMissionHistoryByDateRange(
      periodStart,
      periodEnd,
    );
    final completedMissions = missionProvider.getCompletedMissionsByDateRange(
      periodStart,
      periodEnd,
    );

    // Combine all missions
    final allMissions =
        [...missions, ...monthMissions, ...completedMissions].toSet().toList();

    // Calculate total progress for the month
    double totalProgress = 0.0;
    int validMissions = 0;

    // Count completed and failed missions within the month, broken down by type
    int completedCount = 0;
    int failedCount = 0;
    Map<MissionType, int> completedByType = {
      MissionType.daily: 0,
      MissionType.weekly: 0,
      MissionType.simple: 0,
      MissionType.persistent: 0,
    };
    Map<MissionType, int> failedByType = {
      MissionType.daily: 0,
      MissionType.weekly: 0,
      MissionType.simple: 0,
      MissionType.persistent: 0,
    };
    for (final mission in allMissions) {
      final progress = _calculateMissionProgress(mission);
      if (progress > 0 || mission.hasFailed) {
        totalProgress += progress;
        validMissions++;
      }
      // Completed in this month
      if (mission.lastCompleted != null &&
          mission.lastCompleted!.year == selectedYear &&
          mission.lastCompleted!.month == selectedMonth) {
        completedCount++;
        completedByType[mission.type] =
            (completedByType[mission.type] ?? 0) + 1;
      }
      // Failed in this month
      if (mission.hasFailed &&
          mission.lastCompleted != null &&
          mission.lastCompleted!.year == selectedYear &&
          mission.lastCompleted!.month == selectedMonth) {
        failedCount++;
        failedByType[mission.type] = (failedByType[mission.type] ?? 0) + 1;
      }
    }

    final monthlyCompletion =
        validMissions > 0 ? (totalProgress / validMissions) * 100 : 0.0;

    Widget _typeBreakdown(Map<MissionType, int> map, Color color) {
      List<Widget> children = [];
      map.forEach((type, count) {
        if (count > 0) {
          children.add(
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(_getTypeIcon(type), color: color, size: 14),
                const SizedBox(width: 2),
                Text(
                  '${_getMissionTypeShortName(type)}: $count',
                  style: TextStyle(
                    color: color,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 6),
              ],
            ),
          );
        }
      });
      return Row(children: children);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Title on its own line
        const Text(
          'Overall Progress',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        // Counters in a row below the title
        Row(
          children: [
            // Completed missions counter
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.green[700],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.white, size: 16),
                  const SizedBox(width: 4),
                  Text(
                    completedCount.toString(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 6),
                  _typeBreakdown(completedByType, Colors.white),
                ],
              ),
            ),
            const SizedBox(width: 8),
            // Failed missions counter
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.red[700],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.warning_rounded,
                    color: Colors.white,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    failedCount.toString(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 6),
                  _typeBreakdown(failedByType, Colors.white),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        LinearProgressIndicator(
          value: monthlyCompletion / 100,
          backgroundColor: Colors.grey[800],
          valueColor: AlwaysStoppedAnimation<Color>(
            _getProgressColor(monthlyCompletion),
          ),
          minHeight: 10,
          borderRadius: BorderRadius.circular(5),
        ),
        const SizedBox(height: 8),
        Text(
          '${monthlyCompletion.toStringAsFixed(1)}%',
          style: TextStyle(
            color: _getProgressColor(monthlyCompletion),
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        if (missions.isEmpty)
          const Padding(
            padding: EdgeInsets.only(top: 16.0),
            child: Text(
              'No missions for this month.',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
          ),
      ],
    );
  }

  // Helper for short mission type names
  String _getMissionTypeShortName(MissionType type) {
    switch (type) {
      case MissionType.daily:
        return 'Daily';
      case MissionType.weekly:
        return 'Weekly';
      case MissionType.simple:
        return 'Simple';
      case MissionType.persistent:
        return 'Persistent';
    }
  }

  // Helper for mission type icons
  IconData _getTypeIcon(MissionType type) {
    switch (type) {
      case MissionType.daily:
        return Icons.calendar_today;
      case MissionType.weekly:
        return Icons.calendar_view_week;
      case MissionType.simple:
        return Icons.task_alt;
      case MissionType.persistent:
        return Icons.all_inclusive;
    }
  }

  Widget _buildProgressByType(List<MissionData> missions) {
    // Get mission counts
    final allMissions =
        Provider.of<MissionProvider>(context, listen: false).allMissions;
    final dailyCount =
        allMissions.where((m) => m.type == MissionType.daily).length;
    final weeklyCount =
        allMissions.where((m) => m.type == MissionType.weekly).length;
    final simpleCount =
        allMissions.where((m) => m.type == MissionType.simple).length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Progress by Type',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ...MissionType.values.map((type) {
          final completion = _cachedCompletionByType[type] ?? 0.0;
          final count =
              type == MissionType.daily
                  ? dailyCount
                  : type == MissionType.weekly
                  ? weeklyCount
                  : simpleCount;

          if (count == 0) return const SizedBox.shrink();

          return Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${_getMissionTypeName(type)} (${count} mission${count != 1 ? 's' : ''})',
                  style: const TextStyle(color: Colors.white, fontSize: 16),
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: completion / 100,
                  backgroundColor: Colors.grey[800],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getProgressColor(completion),
                  ),
                  minHeight: 8,
                  borderRadius: BorderRadius.circular(4),
                ),
                const SizedBox(height: 4),
                Text(
                  '${completion.toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: _getProgressColor(completion),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ],
    );
  }

  Widget _buildMasteryLevels(MasteryProvider masteryProvider) {
    final entries = masteryProvider.entries;
    if (entries.isEmpty) return const SizedBox.shrink();

    // Sort entries by progress percentage (highest to lowest)
    final sortedEntries = List<MasteryEntry>.from(entries)..sort((a, b) {
      final progressA = masteryProvider.getProgressPercentage(a.id);
      final progressB = masteryProvider.getProgressPercentage(b.id);
      return progressB.compareTo(progressA); // Sort in descending order
    });

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Mastery Levels',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ...sortedEntries.map((entry) {
          final totalProgress = masteryProvider.getTotalProgress(
            entry.id,
          ); // This is in minutes
          final levelDescription = entry.getLevelDescription();

          // Calculate progress based on current level requirements
          final currentLevel = entry.currentLevel;
          final nextLevelThreshold =
              entry.nextLevelTarget * 60; // Convert hours to minutes
          final currentLevelThreshold =
              currentLevel == 0
                  ? 0
                  : (entry.nextLevelTarget / 2) *
                      60; // Convert hours to minutes

          // Calculate overall progress as percentage of current level
          final progressToCurrentLevel =
              currentLevel == 0
                  ? (totalProgress / 6000).clamp(
                    0.0,
                    1.0,
                  ) // Level 1 is 6000 minutes
                  : ((totalProgress - currentLevelThreshold) /
                          (nextLevelThreshold - currentLevelThreshold))
                      .clamp(0.0, 1.0);

          // Calculate progress to next level (if not at max level)
          final progressToNextLevel =
              currentLevel < entry.maxLevel
                  ? ((totalProgress - currentLevelThreshold) /
                          (nextLevelThreshold - currentLevelThreshold))
                      .clamp(0.0, 1.0)
                  : 1.0;

          // Get monthly progress data
          final monthlyProgress = masteryProvider.getMonthlyProgress(entry.id);
          final totalMinutesForLevel =
              currentLevel == 0
                  ? 6000
                  : (nextLevelThreshold - currentLevelThreshold);

          // Calculate monthly contributions
          final monthlyContributions = monthlyProgress.map((month, minutes) {
            final contribution = minutes / totalMinutesForLevel;
            return MapEntry(month, contribution);
          });

          // Determine color based on progress thresholds
          Color progressColor = Colors.grey;
          if (progressToCurrentLevel >= 1.0) {
            progressColor = Colors.green;
          } else if (progressToCurrentLevel >= 0.75) {
            progressColor = Colors.lightGreen;
          } else if (progressToCurrentLevel >= 0.5) {
            progressColor = Colors.yellow;
          } else if (progressToCurrentLevel >= 0.25) {
            progressColor = Colors.orange;
          }

          return Card(
            color: Colors.grey[900],
            margin: const EdgeInsets.only(bottom: 16.0),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          entry.title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Text(
                        levelDescription,
                        style: TextStyle(color: Colors.grey[400], fontSize: 14),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  // Overall progress bar
                  LinearProgressIndicator(
                    value: progressToCurrentLevel,
                    backgroundColor: Colors.grey[800],
                    valueColor: AlwaysStoppedAnimation<Color>(progressColor),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${(progressToCurrentLevel * 100).toStringAsFixed(1)}% of Level ${currentLevel + 1}',
                        style: TextStyle(color: progressColor, fontSize: 14),
                      ),
                      Text(
                        entry.formatTime(totalProgress),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  if (currentLevel < entry.maxLevel) ...[
                    const SizedBox(height: 8),
                    LinearProgressIndicator(
                      value: progressToNextLevel,
                      backgroundColor: Colors.grey[800],
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '${(progressToNextLevel * 100).toStringAsFixed(1)}% to Level ${currentLevel + 2}',
                      style: const TextStyle(color: Colors.blue, fontSize: 14),
                    ),
                  ],
                  const SizedBox(height: 16),
                  // Monthly contributions
                  Text(
                    'Monthly Progress Contributions',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...monthlyContributions.entries.map((monthData) {
                    final month = monthData.key;
                    final contribution = monthData.value;
                    final minutes = monthlyProgress[month] ?? 0;

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              DateFormat('MMMM yyyy').format(month),
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                              ),
                            ),
                            Text(
                              '${(contribution * 100).toStringAsFixed(1)}%',
                              style: TextStyle(
                                color: _getMonthProgressColor(contribution),
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        LinearProgressIndicator(
                          value: contribution,
                          backgroundColor: Colors.grey[800],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            _getMonthProgressColor(contribution),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '${entry.formatTime(minutes)}',
                          style: TextStyle(
                            color: Colors.grey[400],
                            fontSize: 12,
                          ),
                        ),
                        const SizedBox(height: 8),
                      ],
                    );
                  }).toList(),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'Today',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                          Text(
                            entry.formatTime(
                              masteryProvider.getTodayProgress(entry.id),
                            ),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'This Week',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                          Text(
                            entry.formatTime(
                              masteryProvider.getWeekProgress(entry.id),
                            ),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'This Month',
                            style: TextStyle(color: Colors.grey, fontSize: 12),
                          ),
                          Text(
                            entry.formatTime(
                              masteryProvider.getMonthProgress(entry.id),
                            ),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ],
    );
  }

  Color _getMonthProgressColor(double progress) {
    if (progress >= 1.0) return Colors.green;
    if (progress >= 0.75) return Colors.lightGreen;
    if (progress >= 0.5) return Colors.yellow;
    if (progress >= 0.25) return Colors.orange;
    return Colors.red;
  }

  Widget _buildMissionList(List<MissionData> missions) {
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final startDate = DateTime(selectedYear!, selectedMonth!, 1);
    final endDate = DateTime(selectedYear!, selectedMonth! + 1, 0);

    // Only missions created within the selected month
    final monthMissions =
        missions.where((mission) {
          if (mission.createdAt == null) return false;
          return mission.createdAt!.year == selectedYear &&
              mission.createdAt!.month == selectedMonth;
        }).toList();

    final completedMissions = missionProvider.getCompletedMissionsByDateRange(
      startDate,
      endDate,
    );

    Color _counterColor(double percent) {
      return percent >= 0.5 ? Colors.green : Colors.yellow;
    }

    Widget _buildCompletionCounter(MissionData mission) {
      final now = DateTime.now();
      final year = selectedYear!;
      final month = selectedMonth!;
      final daysInMonth = DateTime(year, month + 1, 0).day;
      if (mission.type == MissionType.daily) {
        int completedDays = 0;
        for (int day = 1; day <= daysInMonth; day++) {
          final date = DateTime(year, month, day);
          if (mission.getProgressForDate(date) >= 1.0) {
            completedDays++;
          }
        }
        final percent = completedDays / daysInMonth;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Row(
            children: [
              Icon(
                Icons.calendar_today,
                color: _counterColor(percent),
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                '$completedDays/$daysInMonth days completed',
                style: TextStyle(
                  color: _counterColor(percent),
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        );
      } else if (mission.type == MissionType.weekly) {
        // Calculate number of weeks in the month
        int weeksInMonth = 0;
        int completedWeeks = 0;
        DateTime weekStart = DateTime(year, month, 1);
        while (weekStart.month == month) {
          weeksInMonth++;
          // Find all days in this week
          List<DateTime> weekDays =
              List.generate(
                7,
                (i) => weekStart.add(Duration(days: i)),
              ).where((d) => d.month == month).toList();
          // If any day in the week is completed, count the week as completed
          bool weekCompleted = weekDays.any(
            (d) => mission.getProgressForDate(d) >= 1.0,
          );
          if (weekCompleted) completedWeeks++;
          weekStart = weekStart.add(Duration(days: 7 - weekStart.weekday + 1));
          if (weekStart.day == 1 && weekStart.month == month)
            break; // Prevent infinite loop
        }
        final percent = weeksInMonth > 0 ? completedWeeks / weeksInMonth : 0.0;
        return Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Row(
            children: [
              Icon(
                Icons.calendar_view_week,
                color: _counterColor(percent),
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                '$completedWeeks/$weeksInMonth weeks completed',
                style: TextStyle(
                  color: _counterColor(percent),
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        );
      }
      return SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Mission Details',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        ...monthMissions.map((mission) {
          // Find the completed version of the mission if it exists
          final completedMission = completedMissions.firstWhere(
            (m) => m.missionId == mission.missionId,
            orElse: () => mission,
          );

          bool isCompleted = false;
          bool isFailed = mission.hasFailed;

          if (completedMission.lastCompleted != null) {
            final lastCompleted = completedMission.lastCompleted!;
            if (lastCompleted.year == selectedYear &&
                lastCompleted.month == selectedMonth) {
              isCompleted = true;
            }
          }

          return Card(
            color: Colors.grey[900],
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title and Status Row
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          mission.title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (isFailed)
                            const Padding(
                              padding: EdgeInsets.only(right: 8.0),
                              child: Icon(
                                Icons.warning_rounded,
                                color: Colors.red,
                                size: 20,
                              ),
                            ),
                          Icon(
                            isCompleted
                                ? Icons.check_circle_rounded
                                : Icons.circle_outlined,
                            color: isCompleted ? Colors.green : Colors.grey,
                            size: 20,
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Mission Type
                  Text(
                    _getMissionTypeName(mission.type),
                    style: TextStyle(color: Colors.grey[400], fontSize: 14),
                  ),
                  const SizedBox(height: 8),

                  // Completion Counter
                  _buildCompletionCounter(mission),

                  // Counter Display (if applicable)
                  if (mission.isCounterBased && mission.currentCount > 0)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.grey[800],
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.countertops_rounded,
                              color: Colors.grey[400],
                              size: 16,
                            ),
                            const SizedBox(width: 4),
                            Text(
                              'Count: {mission.currentCount}',
                              style: TextStyle(
                                color: Colors.grey[400],
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  // Subtasks
                  if (mission.subtasks.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    ...mission.subtasks.map((subtask) {
                      final isSubtaskCompleted =
                          subtask.isCounterBased
                              ? subtask.currentCount > 0
                              : subtask.currentCompletions > 0;

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 4.0),
                        child: Row(
                          children: [
                            Icon(
                              isSubtaskCompleted
                                  ? Icons.check_circle_rounded
                                  : Icons.circle_outlined,
                              color:
                                  isSubtaskCompleted
                                      ? Colors.green
                                      : Colors.grey,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                subtask.name,
                                style: TextStyle(
                                  color: Colors.grey[400],
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            // Removed subtask.currentCount display
                          ],
                        ),
                      );
                    }).toList(),
                  ],

                  // Completion Date
                  if (mission.lastCompleted != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12.0),
                      child: Text(
                        'Completed on ${DateFormat('MMM d, y').format(mission.lastCompleted!)}',
                        style: TextStyle(color: Colors.grey[500], fontSize: 12),
                      ),
                    ),
                ],
              ),
            ),
          );
        }).toList(),
      ],
    );
  }

  String _getMissionTypeName(MissionType type) {
    switch (type) {
      case MissionType.daily:
        return 'Daily Mission';
      case MissionType.weekly:
        return 'Weekly Mission';
      case MissionType.simple:
        return 'Simple Task';
      case MissionType.persistent:
        return 'Persistent Mission';
    }
  }

  Color _getProgressColor(double percentage) {
    if (percentage < 0) return Colors.red;
    if (percentage >= 80) return Colors.green;
    if (percentage >= 60) return Colors.lightGreen;
    if (percentage >= 40) return Colors.yellow;
    if (percentage >= 20) return Colors.orange;
    return Colors.red;
  }

  // Helper to get the initial week index for the PageController
  int _getCurrentWeekIndex() {
    if (selectedYear == null || selectedMonth == null) return 0;

    final now = DateTime.now();
    final periodStart = DateTime(selectedYear!, selectedMonth!, 1);
    final periodEnd = DateTime(selectedYear!, selectedMonth! + 1, 0);

    final List<List<DailySummary>> weeks = [];
    List<DailySummary> currentWeek = [];
    DateTime currentDate = periodStart;

    int weekdayOfFirstDay = periodStart.weekday; // Monday is 1, Sunday is 7
    int daysToPrepend =
        (weekdayOfFirstDay == DateTime.sunday) ? 6 : weekdayOfFirstDay - 1;

    for (int i = 0; i < daysToPrepend; i++) {
      currentWeek.add(
        DailySummary(
          date: DateTime(0),
          missionsMade: 0,
          totalProgress: 0.0,
          dailyProgressPercentage: 0.0,
        ),
      );
    }

    while (currentDate.isBefore(periodEnd.add(const Duration(days: 1)))) {
      // Create a dummy DailySummary for the purpose of grouping into weeks.
      // The actual dailySummaries from _cachedDailySummaries will be used in _buildWeeklyProgressChart.
      currentWeek.add(
        DailySummary(
          date: currentDate,
          missionsMade: 0,
          totalProgress: 0.0,
          dailyProgressPercentage: 0.0,
        ),
      );
      if (currentWeek.length == 7) {
        weeks.add(currentWeek);
        currentWeek = [];
      }
      currentDate = currentDate.add(const Duration(days: 1));
    }

    if (currentWeek.isNotEmpty) {
      while (currentWeek.length < 7) {
        currentWeek.add(
          DailySummary(
            date: DateTime(0),
            missionsMade: 0,
            totalProgress: 0.0,
            dailyProgressPercentage: 0.0,
          ),
        );
      }
      weeks.add(currentWeek);
    }

    // Find the week containing today's date
    for (int i = 0; i < weeks.length; i++) {
      if (weeks[i].any((summary) => _isSameDay(summary.date, now))) {
        return i;
      }
    }
    return 0; // Default to the first week if today's week isn't found
  }

  // Helper to check if two DateTimes represent the same day
  bool _isSameDay(DateTime a, DateTime b) {
    return a.year == b.year && a.month == b.month && a.day == b.day;
  }

  // Modified: Calculate daily average progress for all missions for the weekly progress chart
  Map<DateTime, double> _calculateDailyAverageProgress(
    List<MissionData> missions,
    int year,
    int month,
  ) {
    final periodEnd = DateTime(year, month + 1, 0);
    final Map<DateTime, double> dailyAverages = {};
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      if (date.isAfter(today)) continue;
      double dayProgress = 0.0;
      int validMissions = 0;
      int failedMissions = 0;
      for (final mission in missions) {
        if (mission.createdAt == null) continue;
        final missionEnd = _getMissionEndDate(mission);
        if (date.isBefore(mission.createdAt!) || date.isAfter(missionEnd))
          continue;
        // Check if mission failed on this day
        if (mission.hasFailed && mission.lastCompleted != null) {
          final lastCompleted = mission.lastCompleted!;
          if (lastCompleted.isAfter(date) &&
              lastCompleted.year == date.year &&
              lastCompleted.month == date.month) {
            failedMissions++;
            continue; // Don't count progress for failed missions
          }
        }
        final progressToday = mission.getProgressForDate(date);
        final progressYesterday = mission.getProgressForDate(
          date.subtract(const Duration(days: 1)),
        );
        final delta = (progressToday - progressYesterday).clamp(0.0, 1.0);
        double missionWeight = 1.0;
        switch (mission.type) {
          case MissionType.daily:
            missionWeight = 1.2;
            break;
          case MissionType.weekly:
            missionWeight = 1.5;
            break;
          case MissionType.persistent:
            missionWeight = 1.3;
            break;
          default:
            missionWeight = 1.0;
        }
        dayProgress += delta * missionWeight;
        validMissions++;
      }
      // Apply failed mission penalty (-20% per failed mission)
      double failedPenalty = failedMissions * 20.0;
      final dayAverage =
          validMissions > 0
              ? ((dayProgress / validMissions) * 100 - failedPenalty).clamp(
                -100.0,
                100.0,
              )
              : -failedPenalty.clamp(-100.0, 100.0);
      dailyAverages[date] = dayAverage;
    }
    return dailyAverages;
  }

  // Add a method to handle midnight progress save
  void _handleMidnightProgressSave() {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    // Calculate and save today's final progress
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final missions = missionProvider.missions;

    double dayProgress = 0.0;
    int validMissions = 0;
    int failedMissions = 0;

    // Get active missions for today
    final activeMissions =
        missions.where((mission) {
          if (mission.createdAt == null) return false;
          final missionEnd = _getMissionEndDate(mission);
          return today.isAfter(
                mission.createdAt!.subtract(const Duration(days: 1)),
              ) &&
              today.isBefore(missionEnd.add(const Duration(days: 1)));
        }).toList();

    // Calculate final progress for today
    for (final mission in activeMissions) {
      double missionProgress = 0.0;
      double missionWeight = 1.0;

      // Check if mission failed
      bool isFailed = false;
      if (mission.hasFailed && mission.lastCompleted != null) {
        final lastCompleted = mission.lastCompleted!;
        if (lastCompleted.isAfter(today) &&
            lastCompleted.year == today.year &&
            lastCompleted.month == today.month) {
          isFailed = true;
          failedMissions++;
        }
      }

      if (!isFailed) {
        final progress = mission.getProgressForDate(today);
        if (progress != null) {
          if (mission.subtasks.isNotEmpty) {
            double subtaskTotal = 0.0;
            int validSubtasks = 0;

            for (final subtask in mission.subtasks) {
              double subtaskProgress = 0.0;

              if (subtask.isCounterBased) {
                if (subtask.requiredCompletions > 0) {
                  subtaskProgress = (progress / subtask.requiredCompletions)
                      .clamp(0.0, 1.0);
                } else {
                  subtaskProgress = progress > 0 ? 1.0 : 0.0;
                }
              } else {
                if (subtask.requiredCompletions > 0) {
                  subtaskProgress = (progress / subtask.requiredCompletions)
                      .clamp(0.0, 1.0);
                } else {
                  subtaskProgress = progress > 0 ? 1.0 : 0.0;
                }
              }

              subtaskTotal += subtaskProgress;
              validSubtasks++;
            }

            missionProgress =
                validSubtasks > 0 ? subtaskTotal / validSubtasks : 0.0;
          } else if (mission.isCounterBased) {
            if (mission.targetCount > 0) {
              missionProgress = (progress / mission.targetCount).clamp(
                0.0,
                1.0,
              );
            } else {
              missionProgress = progress > 0 ? 1.0 : 0.0;
            }
          } else {
            missionProgress = progress >= 1.0 ? 1.0 : 0.0;
          }
        }
      }

      // Apply mission type weight
      switch (mission.type) {
        case MissionType.daily:
          missionWeight = 1.2;
          break;
        case MissionType.weekly:
          missionWeight = 1.5;
          break;
        case MissionType.persistent:
          missionWeight = 1.3;
          break;
        default:
          missionWeight = 1.0;
      }

      dayProgress += missionProgress * missionWeight;
      validMissions++;
    }

    // Calculate and save final progress
    if (validMissions > 0) {
      double baseProgress = (dayProgress / validMissions) * 100;
      double failedPenalty = failedMissions * 20.0;
      final finalProgress = (baseProgress - failedPenalty).clamp(-100.0, 100.0);
      _saveDailyProgress(today, finalProgress);
    } else {
      final failedPenalty = failedMissions * 20.0;
      _saveDailyProgress(today, -failedPenalty.clamp(0.0, 100.0));
    }
  }

  // Add this method to backfill daily progress for previous days
  Future<void> _backfillDailyProgress() async {
    final now = DateTime.now();
    final year = selectedYear ?? now.year;
    final month = selectedMonth ?? now.month;
    final periodEnd = DateTime(year, month + 1, 0);
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final missions = missionProvider.missions;

    for (int day = 1; day <= periodEnd.day; day++) {
      final date = DateTime(year, month, day);
      if (date.isAfter(now)) continue;
      // Always calculate and save progress for each day
      double dayProgress = 0.0;
      int validMissions = 0;
      int failedMissions = 0;
      for (final mission in missions) {
        if (mission.createdAt == null) continue;
        final missionEnd = _getMissionEndDate(mission);
        if (date.isBefore(mission.createdAt!) || date.isAfter(missionEnd))
          continue;
        // Check if mission failed on this day
        if (mission.hasFailed && mission.lastCompleted != null) {
          final lastCompleted = mission.lastCompleted!;
          if (lastCompleted.isAfter(date) &&
              lastCompleted.year == date.year &&
              lastCompleted.month == date.month) {
            failedMissions++;
            continue; // Don't count progress for failed missions
          }
        }
        final progressToday = mission.getProgressForDate(date);
        final progressYesterday = mission.getProgressForDate(
          date.subtract(const Duration(days: 1)),
        );
        final delta = (progressToday - progressYesterday).clamp(0.0, 1.0);
        double missionWeight = 1.0;
        switch (mission.type) {
          case MissionType.daily:
            missionWeight = 1.2;
            break;
          case MissionType.weekly:
            missionWeight = 1.5;
            break;
          case MissionType.persistent:
            missionWeight = 1.3;
            break;
          default:
            missionWeight = 1.0;
        }
        dayProgress += delta * missionWeight;
        validMissions++;
      }
      double failedPenalty = failedMissions * 20.0;
      final dayAverage =
          validMissions > 0
              ? ((dayProgress / validMissions) * 100 - failedPenalty).clamp(
                -100.0,
                100.0,
              )
              : -failedPenalty.clamp(-100.0, 100.0);
      await _saveDailyProgress(date, dayAverage);
    }
  }
}
