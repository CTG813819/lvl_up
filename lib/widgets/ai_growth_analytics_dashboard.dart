import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import '../providers/ai_learning_provider.dart';
import '../providers/conquest_ai_provider.dart';
import '../models/ai_proposal.dart';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../providers/ai_growth_analytics_provider.dart';
import '../services/network_config.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../providers/ai_customization_provider.dart';

// AI Growth Analytics Dashboard
// Comprehensive analytics showing AI growth, learning, failures, and successes
class AIGrowthAnalyticsDashboard extends StatefulWidget {
  final Widget? connectionIndicator;

  const AIGrowthAnalyticsDashboard({Key? key, this.connectionIndicator})
    : super(key: key);

  @override
  State<AIGrowthAnalyticsDashboard> createState() =>
      _AIGrowthAnalyticsDashboardState();
}

class _AIGrowthAnalyticsDashboardState extends State<AIGrowthAnalyticsDashboard>
    with TickerProviderStateMixin {
  Timer? _pollingTimer;
  bool _isLoading = true;
  Map<String, dynamic> _growthData = {};
  Map<String, dynamic> _aiStatus = {};
  List<Map<String, dynamic>> _recentFailures = [];
  List<Map<String, dynamic>> _recentSuccesses = [];
  List<Map<String, dynamic>> _learningInsights = [];

  // Track previous agent levels for level-up notifications
  Map<String, String> _previousAgentLevels = {};

  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  final FlutterLocalNotificationsPlugin _aiNotifications =
      FlutterLocalNotificationsPlugin();
  final Map<String, int> _aiNotificationIds = {
    'imperium': 20001,
    'guardian': 20002,
    'sandbox': 20003,
    'conquest': 20004,
  };

  @override
  void initState() {
    super.initState();
    // --- Always load cached data before backend fetch for persistence ---
    _loadSavedDashboardData().then((_) {
      _loadData();
    });
    _initializeAnimations();
    _initAINotifications();
    _startPolling();
    // --- Real-time provider listener for notifications ---
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<AIGrowthAnalyticsProvider>(
        context,
        listen: false,
      );
      provider.addListener(_onProviderUpdate);
    });
  }

  void _onProviderUpdate() {
    if (!mounted) return;
    final provider = Provider.of<AIGrowthAnalyticsProvider>(
      context,
      listen: false,
    );
    final agents = provider.aiStatus['agents'] as Map<String, dynamic>? ?? {};
    for (final entry in agents.entries) {
      final aiType = entry.key;
      final agentData = entry.value;
      final score = agentData['learning_score'] ?? 0.0;
      final level = _getAgentLevelAndTitle(score, aiType);
      // FIX: Use level-based progress (0-100 per level)
      final progress = provider.getLevelProgressForAI(aiType) / 100.0;
      _showOrUpdateAINotification(aiType, score, level, progress);
    }
    _checkForLevelUps();
  }

  void _initializeAnimations() {
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(parent: _slideController, curve: Curves.easeOutCubic),
    );

    _fadeController.forward();
    _slideController.forward();
  }

  Future<void> _initAINotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    final InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);
    await _aiNotifications.initialize(initializationSettings);
  }

  // Call this whenever AI progress/level changes
  Future<void> _showOrUpdateAINotification(
    String aiType,
    double score,
    String level,
    double progress,
  ) async {
    final int notificationId =
        _aiNotificationIds[aiType.toLowerCase()] ?? 20000;
    final String aiTitle =
        aiType.isNotEmpty
            ? aiType[0].toUpperCase() + aiType.substring(1).toLowerCase()
            : aiType;
    final String emoji = _getAIEmoji(aiType);
    final Color aiColor = _getAIColor(aiType);

    // FIX: Use level-based progress instead of complex calculations
    final provider = Provider.of<AIGrowthAnalyticsProvider>(
      context,
      listen: false,
    );
    final levelProgress = provider.getLevelProgressForAI(aiType);
    final aiLevel = provider.getAILevel(aiType);

    final AndroidNotificationDetails
    androidPlatformChannelSpecifics = AndroidNotificationDetails(
      'ai_progress_channel',
      'AI Level Progress',
      channelDescription: 'Persistent notifications for AI level progress',
      importance: Importance.low, // Silent
      priority: Priority.low, // Silent
      playSound: false, // Silent
      showWhen: false,
      autoCancel: false,
      ongoing: true,
      onlyAlertOnce: true,
      color: aiColor,
      colorized: true,
      styleInformation: BigTextStyleInformation(
        'Level: $aiLevel\nScore: ${score.toStringAsFixed(0)}\nProgress: ${levelProgress.toStringAsFixed(0)}%',
        contentTitle: '$emoji $aiTitle Level Progress',
      ),
      progress: levelProgress.toInt(),
      maxProgress: 100,
      showProgress: true,
      indeterminate: false,
    );
    final NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    final displayLevel =
        int.tryParse(level) != null ? _toRomanNumeral(int.parse(level)) : level;
    await _aiNotifications.show(
      notificationId,
      '$emoji $aiTitle Level Progress',
      'Level: $aiLevel | Score: ${score.toStringAsFixed(0)} | Progress: ${levelProgress.toStringAsFixed(0)}%',
      platformChannelSpecifics,
    );
  }

  // Show level-up notification (with sound/high importance)
  Future<void> _showLevelUpNotification(
    String agentName,
    String oldLevel,
    String newLevel,
    double learningScore,
  ) async {
    final aiType = agentName.toLowerCase();
    final levelColor = _getAgentLevelColor(learningScore, agentName);
    final String emoji = _getAIEmoji(aiType);
    final int notificationId =
        30000 + (aiType.hashCode % 1000); // Unique per AI
    final AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'ai_levelup_channel',
          'AI Level Up',
          channelDescription: 'Persistent notifications for AI level up',
          importance: Importance.max, // Prominent
          priority: Priority.max, // Prominent
          playSound: true, // Play sound for level up
          showWhen: true,
          autoCancel: false,
          ongoing: true,
          color: levelColor,
          colorized: true,
          styleInformation: BigTextStyleInformation(
            '$oldLevel → $newLevel',
            contentTitle: '$emoji $agentName has leveled up!',
          ),
        );
    final NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
    );
    final displayOldLevel =
        int.tryParse(oldLevel) != null
            ? _toRomanNumeral(int.parse(oldLevel))
            : oldLevel;
    final displayNewLevel =
        int.tryParse(newLevel) != null
            ? _toRomanNumeral(int.parse(newLevel))
            : newLevel;
    await _aiNotifications.show(
      notificationId,
      '$emoji $agentName has leveled up!',
      '$displayOldLevel → $displayNewLevel',
      platformChannelSpecifics,
    );
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    _fadeController.dispose();
    _slideController.dispose();
    // Remove provider listener safely
    try {
      final provider = Provider.of<AIGrowthAnalyticsProvider>(
        context,
        listen: false,
      );
      provider.removeListener(_onProviderUpdate);
    } catch (e) {
      // Widget is already disposed, ignore the error
      print('Provider already disposed, ignoring: $e');
    }
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      // Load all data in parallel
      await Future.wait([
        _loadGrowthData(),
        _loadAIStatus(),
        _loadRecentActivity(),
        _loadLearningInsights(),
      ]);
      // Save dashboard data after loading
      await _saveDashboardData();
    } catch (e) {
      print('Error loading analytics data: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadGrowthData() async {
    try {
      final response = await http
          .get(Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/agents'))
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          final backendGrowth = _transformAgentDataToGrowthData(data);
          final mergedGrowth = await _mergeWithSavedDashboardData(
            backendGrowth,
            'dashboard_growth_data',
          );
          setState(() {
            _growthData = mergedGrowth;
          });
          await _saveDashboardData();
        }
      }
    } catch (e) {
      print('Error loading growth data: $e');
    }
  }

  Map<String, dynamic> _transformAgentDataToGrowthData(
    Map<String, dynamic> agentData,
  ) {
    final agents = agentData['agents'] as Map<String, dynamic>? ?? {};
    final aiGrowthInsights = <String, dynamic>{};

    for (final entry in agents.entries) {
      final agentId = entry.key;
      final agent = entry.value as Map<String, dynamic>;

      aiGrowthInsights[agentId] = {
        'growth_potential': {
          'growth_score':
              (agent['learning_score'] ??
                  0.0), // Use raw XP for display and progress
          'growth_stage': _getGrowthStage(agent['learning_score'] ?? 0.0),
        },
        'current_performance': {
          'avg_confidence': (agent['success_rate'] ?? 0.0), // Keep as decimal
          'approval_rate': (agent['success_rate'] ?? 0.0), // Keep as decimal
          'total_learning': agent['total_learning_cycles'] ?? 0,
          'total_proposals': agent['total_learning_cycles'] ?? 0,
        },
        'expansion_opportunities': [],
        'growth_recommendations': [],
      };
    }

    // Filter agents to show only main AI types for calculations
    final filteredAgents = _filterMainAIAgents(agents);

    return {
      'ai_growth_insights': aiGrowthInsights,
      'overall_growth': {
        'system_maturity': 'mature',
        // FIX: Do not show as percent, just as a number
        'average_growth_score': _calculateAverageGrowthScore(filteredAgents),
        'total_learning_entries': _calculateTotalLearningEntries(
          filteredAgents,
        ),
        'total_expansion_opportunities': 0,
      },
    };
  }

  String _getGrowthStage(double learningScore) {
    if (learningScore >= 90) return 'advanced';
    if (learningScore >= 70) return 'mature';
    if (learningScore >= 50) return 'developing';
    return 'emerging';
  }

  double _calculateAverageGrowthScore(Map<String, dynamic> agents) {
    if (agents.isEmpty) return 0.0;
    double total = 0.0;
    int count = 0;
    for (final agent in agents.values) {
      if (agent is Map<String, dynamic>) {
        total += (agent['learning_score'] ?? 0.0);
        count++;
      }
    }
    return count > 0 ? total / count : 0.0;
  }

  int _calculateTotalLearningEntries(Map<String, dynamic> agents) {
    int total = 0;
    for (final agent in agents.values) {
      if (agent is Map<String, dynamic>) {
        final cyclesRaw = agent['total_learning_cycles'] ?? 0;
        final num cyclesNum = (cyclesRaw is num) ? cyclesRaw : 0;
        total += cyclesNum.toInt();
      }
    }
    return total;
  }

  Future<void> _loadAIStatus() async {
    try {
      final response = await http
          .get(Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/agents'))
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          final mergedStatus = await _mergeWithSavedDashboardData(
            data,
            'dashboard_ai_status',
          );
          setState(() {
            _aiStatus = mergedStatus;
            // Check for level-ups after updating AI status
            _checkForLevelUps();
            // Update persistent notifications for main AIs only
            final agents = _aiStatus['agents'] as Map<String, dynamic>? ?? {};
            final filteredAgents = _filterMainAIAgents(agents);
            for (final entry in filteredAgents.entries) {
              final aiType = entry.key;
              final agentData = entry.value;
              final score = agentData['learning_score'] ?? 0.0;
              final level = _getAgentLevelAndTitle(score, aiType);
              final progress = (score / 1000000).clamp(0.0, 1.0);
              _showOrUpdateAINotification(aiType, score, level, progress);
            }
          });
          await _saveDashboardData();
        }
      }
    } catch (e) {
      print('Error loading AI status: $e');
    }
  }

  // Check for level-ups and show notifications
  void _checkForLevelUps() {
    final agents = _aiStatus['agents'] as Map<String, dynamic>? ?? {};
    final filteredAgents = _filterMainAIAgents(agents);

    for (final entry in filteredAgents.entries) {
      final agentName = entry.key;
      final agentData = entry.value;
      final learningScore = agentData['learning_score'] ?? 0.0;

      // Get current level
      final currentLevel = _getAgentLevelAndTitle(learningScore, agentName);

      // Check if this is a new level
      if (_previousAgentLevels.containsKey(agentName)) {
        final previousLevel = _previousAgentLevels[agentName]!;
        if (previousLevel != currentLevel) {
          // Level up detected!
          _showLevelUpNotification(
            agentName,
            previousLevel,
            currentLevel,
            learningScore,
          );
        }
      }

      // Update previous level
      _previousAgentLevels[agentName] = currentLevel;
    }
  }

  // Get Conquest AI apps count
  Future<int> _getConquestAppsCount() async {
    try {
      final conquestProvider = Provider.of<ConquestAIProvider>(
        context,
        listen: false,
      );
      return conquestProvider.totalAppsCount;
    } catch (e) {
      print('Error getting Conquest apps count: $e');
      return 0;
    }
  }

  Future<void> _loadRecentActivity() async {
    try {
      // Use the existing agent data to create recent activity
      final response = await http
          .get(Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/agents'))
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _processActivityDataFromAgents(data);
      }
    } catch (e) {
      print('Error loading recent activity: $e');
    }
  }

  void _processActivityDataFromAgents(Map<String, dynamic> data) async {
    final failures = <Map<String, dynamic>>[];
    final successes = <Map<String, dynamic>>[];

    final agents = data['agents'] as Map<String, dynamic>? ?? {};
    final filteredAgents = _filterMainAIAgents(agents);

    for (final entry in filteredAgents.entries) {
      final aiType = entry.key;
      final agent = entry.value as Map<String, dynamic>;

      // Create success entries based on learning cycles
      final totalCyclesRaw = agent['total_learning_cycles'] ?? 0;
      final num totalCyclesNum =
          (totalCyclesRaw is num)
              ? totalCyclesRaw
              : num.tryParse(totalCyclesRaw.toString()) ?? 0;
      final int totalCyclesInt = totalCyclesNum.toInt();
      final successRate = agent['success_rate'] ?? 0.0;
      final failureRate = agent['failure_rate'] ?? 0.0;

      if (totalCyclesInt > 0) {
        final int successCount = (totalCyclesNum * successRate).round().toInt();
        for (int i = 0; i < successCount && i < 5; i++) {
          successes.add({
            'ai_type': aiType,
            'type': 'learning_success',
            'message': 'Learning cycle completed successfully',
            'timestamp':
                agent['last_success'] ?? DateTime.now().toIso8601String(),
            'confidence': successRate,
          });
        }

        // Add recent failures
        final int failureCount = (totalCyclesNum * failureRate).round().toInt();
        for (int i = 0; i < failureCount && i < 3; i++) {
          failures.add({
            'ai_type': aiType,
            'type': 'learning_failure',
            'message': 'Learning cycle encountered issues',
            'timestamp':
                agent['last_failure'] ?? DateTime.now().toIso8601String(),
            'confidence': failureRate,
          });
        }
      }
    }

    // Sort by timestamp (most recent first)
    failures.sort((a, b) {
      final aTimestamp = a['timestamp']?.toString() ?? '';
      final bTimestamp = b['timestamp']?.toString() ?? '';
      return bTimestamp.compareTo(aTimestamp);
    });
    successes.sort((a, b) {
      final aTimestamp = a['timestamp']?.toString() ?? '';
      final bTimestamp = b['timestamp']?.toString() ?? '';
      return bTimestamp.compareTo(aTimestamp);
    });

    if (mounted) {
      final mergedFailures = await _mergeWithSavedDashboardList(
        failures.take(10).toList(),
        'dashboard_recent_failures',
        maxItems: 10,
      );
      final mergedSuccesses = await _mergeWithSavedDashboardList(
        successes.take(10).toList(),
        'dashboard_recent_successes',
        maxItems: 10,
      );
      setState(() {
        _recentFailures = mergedFailures;
        _recentSuccesses = mergedSuccesses;
      });
      await _saveDashboardData();
    }
  }

  Future<void> _loadLearningInsights() async {
    try {
      // Use the existing agent data to create learning insights
      final response = await http
          .get(Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/agents'))
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _processLearningInsightsFromAgents(data);
      }
    } catch (e) {
      print('Error loading learning insights: $e');
    }
  }

  void _processLearningInsightsFromAgents(Map<String, dynamic> data) async {
    final insights = <Map<String, dynamic>>[];
    final agents = data['agents'] as Map<String, dynamic>? ?? {};
    final filteredAgents = _filterMainAIAgents(agents);

    for (final entry in filteredAgents.entries) {
      final aiType = entry.key;
      final agent = entry.value as Map<String, dynamic>;

      final learningPatterns = agent['learning_patterns'] as List? ?? [];
      final recommendations = <String>[];

      // Generate recommendations based on learning patterns
      if (learningPatterns.isNotEmpty) {
        recommendations.add('Continue focusing on ${learningPatterns.first}');
        if (learningPatterns.length > 1) {
          recommendations.add('Explore ${learningPatterns[1]} for improvement');
        }
      }

      // Add performance-based recommendations
      final learningScore = agent['learning_score'] ?? 0.0;
      if (learningScore < 80) {
        recommendations.add('Focus on improving learning efficiency');
      } else if (learningScore >= 95) {
        recommendations.add('Consider advanced learning strategies');
      }

      insights.add({
        'ai_type': aiType,
        'insights': {
          'recommendations': recommendations,
          'learning_score': learningScore,
          'success_rate': agent['success_rate'] ?? 0.0,
          'total_cycles': agent['total_learning_cycles'] ?? 0,
        },
      });
    }

    if (mounted) {
      final mergedInsights = await _mergeWithSavedDashboardList(
        insights,
        'dashboard_learning_insights',
        maxItems: 20,
      );
      setState(() {
        _learningInsights = mergedInsights;
      });
      await _saveDashboardData();
    }
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        _loadDataSilently(); // Use silent refresh instead of full reload
      }
    });
  }

  // Load data silently without showing loading screen
  Future<void> _loadDataSilently() async {
    try {
      // Load all data in parallel without showing loading state
      await Future.wait([
        _loadGrowthData(),
        _loadAIStatus(),
        _loadRecentActivity(),
        _loadLearningInsights(),
      ]);
    } catch (e) {
      print('Error loading analytics data silently: $e');
    }
  }

  // Utility: Save dashboard data to SharedPreferences
  Future<void> _saveDashboardData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('dashboard_growth_data', jsonEncode(_growthData));
      await prefs.setString('dashboard_ai_status', jsonEncode(_aiStatus));
      await prefs.setString(
        'dashboard_recent_failures',
        jsonEncode(_recentFailures),
      );
      await prefs.setString(
        'dashboard_recent_successes',
        jsonEncode(_recentSuccesses),
      );
      await prefs.setString(
        'dashboard_learning_insights',
        jsonEncode(_learningInsights),
      );
    } catch (e) {
      print('Error saving dashboard data: $e');
    }
  }

  // Utility: Load dashboard data from SharedPreferences
  Future<void> _loadSavedDashboardData() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final growth = prefs.getString('dashboard_growth_data');
      final status = prefs.getString('dashboard_ai_status');
      final failures = prefs.getString('dashboard_recent_failures');
      final successes = prefs.getString('dashboard_recent_successes');
      final insights = prefs.getString('dashboard_learning_insights');
      setState(() {
        if (growth != null) _growthData = jsonDecode(growth);
        if (status != null) _aiStatus = jsonDecode(status);
        if (failures != null)
          _recentFailures = List<Map<String, dynamic>>.from(
            jsonDecode(failures),
          );
        if (successes != null)
          _recentSuccesses = List<Map<String, dynamic>>.from(
            jsonDecode(successes),
          );
        if (insights != null)
          _learningInsights = List<Map<String, dynamic>>.from(
            jsonDecode(insights),
          );
      });
    } catch (e) {
      print('Error loading saved dashboard data: $e');
    }
  }

  // Merge backend data with local data (max for numbers, prefer backend for non-numeric)
  Future<Map<String, dynamic>> _mergeWithSavedDashboardData(
    Map<String, dynamic> backend,
    String key,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final str = prefs.getString(key);
    Map<String, dynamic> local = {};
    if (str != null) {
      local = jsonDecode(str) as Map<String, dynamic>;
    }
    final merged = <String, dynamic>{};
    for (final k in backend.keys) {
      if (backend[k] is num && local[k] is num) {
        // Avoid double counting: always use the latest (max) value
        merged[k] =
            (backend[k] as num) > (local[k] as num) ? backend[k] : local[k];
      } else {
        merged[k] = backend[k];
      }
    }
    for (final k in local.keys) {
      if (!merged.containsKey(k)) merged[k] = local[k];
    }
    return merged;
  }

  // Merge backend list with local list (deduplicate by timestamp+type, keep latest N)
  Future<List<Map<String, dynamic>>> _mergeWithSavedDashboardList(
    List<Map<String, dynamic>> backend,
    String key, {
    int maxItems = 10,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    final str = prefs.getString(key);
    List<Map<String, dynamic>> local = [];
    if (str != null) {
      local = List<Map<String, dynamic>>.from(jsonDecode(str));
    }
    final Map<String, Map<String, dynamic>> unique = {};
    for (final item in [...local, ...backend]) {
      final ts = item['timestamp']?.toString() ?? '';
      final type = item['type']?.toString() ?? '';
      final key = '$ts|$type';
      unique[key] = item;
    }
    final merged = unique.values.toList();
    merged.sort(
      (a, b) => (b['timestamp'] ?? '').compareTo(a['timestamp'] ?? ''),
    );
    return merged.take(maxItems).toList();
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AIGrowthAnalyticsProvider>(context);
    final log = provider.internetLearningLog;

    // Debug: Show raw agent data
    Widget _buildRawAgentData() {
      return Card(
        color: Colors.black87,
        margin: const EdgeInsets.only(bottom: 16),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Text(
              'Raw agent data: ' +
                  (_aiStatus['agents'] != null
                      ? _aiStatus['agents'].toString()
                      : 'No data'),
              style: const TextStyle(fontSize: 12, color: Colors.greenAccent),
            ),
          ),
        ),
      );
    }

    return FadeTransition(
      opacity: _fadeAnimation,
      child: SlideTransition(
        position: _slideAnimation,
        child: Scaffold(
          backgroundColor: Colors.grey[900],
          appBar: AppBar(
            title: const Text(
              '🤖 AI Growth Analytics',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 20,
              ),
            ),
            backgroundColor: Colors.grey[900],
            elevation: 0,
            centerTitle: true,
            actions: [
              if (widget.connectionIndicator != null)
                widget.connectionIndicator!,
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.white),
                onPressed: _loadDataSilently, // Use silent refresh
              ),
            ],
          ),
          body:
              _isLoading
                  ? const Center(
                    child: CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                    ),
                  )
                  : SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _buildSystemOverview(),
                        const SizedBox(height: 20),
                        _buildGrowthScores(),
                        const SizedBox(height: 20),
                        _buildAgentRankings(),
                        const SizedBox(height: 20),
                        _buildRecentActivity(),
                        const SizedBox(height: 20),
                        _buildLearningInsights(),
                        const SizedBox(height: 20),
                        _buildAIStatusGrid(),
                        // Removed imperium AI learning sections at the bottom
                      ],
                    ),
                  ),
        ),
      ),
    );
  }

  Widget _buildSystemOverview() {
    final overallGrowth =
        _growthData['overall_growth'] as Map<String, dynamic>? ?? {};
    final systemMaturity = overallGrowth['system_maturity'] ?? 'unknown';
    final avgGrowthScore = overallGrowth['average_growth_score'] ?? 0.0;
    final totalLearning = overallGrowth['total_learning_entries'] ?? 0;
    final opportunities = overallGrowth['total_expansion_opportunities'] ?? 0;

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.grey[850],
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.blue.withOpacity(0.1),
              Colors.purple.withOpacity(0.1),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.psychology, color: Colors.blue[300], size: 28),
                  const SizedBox(width: 12),
                  Text(
                    'System Overview',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: _buildOverviewMetric(
                      'System Maturity',
                      systemMaturity.toUpperCase(),
                      Icons.trending_up,
                      _getMaturityColor(systemMaturity),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildOverviewMetric(
                      'Avg Growth Score',
                      // FIX: Show as a number, not percent
                      avgGrowthScore.toStringAsFixed(1),
                      Icons.analytics,
                      Colors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: _buildOverviewMetric(
                      'Learning Entries',
                      totalLearning.toString(),
                      Icons.school,
                      Colors.orange,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildOverviewMetric(
                      'Opportunities',
                      opportunities.toString(),
                      Icons.lightbulb,
                      Colors.purple,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOverviewMetric(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(fontSize: 12, color: Colors.grey[400]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildGrowthScores() {
    final agents = _aiStatus['agents'] as Map<String, dynamic>? ?? {};
    final filteredAgents = _filterMainAIAgents(agents);

    final provider = Provider.of<AICustomizationProvider>(
      context,
      listen: false,
    );

    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.grey[850],
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.trending_up, color: Colors.green[300], size: 24),
                const SizedBox(width: 12),
                Text(
                  'AI Growth Scores',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...filteredAgents.entries.toList().asMap().entries.map((entry) {
              final rank = entry.key + 1;
              final aiType = entry.value.key;
              final agentData = entry.value.value as Map<String, dynamic>;

              final learningScore = (agentData['learning_score'] ?? 0.0) as num;
              final totalCycles = agentData['total_learning_cycles'] ?? 0;
              final confidence = (agentData['confidence'] ?? 0.0) * 100;
              final approvalRate = (agentData['approval_rate'] ?? 0.0) * 100;

              // Apply dynamic difficulty based on leveling system
              final dynamicGrowthScore = _calculateDynamicGrowthScore(
                learningScore.toDouble(),
                aiType,
              );
              final dynamicApprovalRate = _calculateDynamicApprovalRate(
                approvalRate,
                aiType,
              );
              final difficultyDescription = _getLevelDifficultyDescription(
                aiType,
              );

              // Progress bar calculation
              final thresholds = _getLevelThresholds(
                learningScore.toDouble(),
                aiType,
              );
              final currentLevelMin = thresholds['current']!;
              final nextLevelMin = thresholds['next']!;
              final progress = ((learningScore - currentLevelMin) /
                      (nextLevelMin - currentLevelMin))
                  .clamp(0.0, 1.0);

              // --- Always use provider's getColorForAI for persistent color ---
              final Color color = provider.getColorForAI(aiType);

              return Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: color.withOpacity(0.3)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(_getAIIcon(aiType), color: color, size: 24),
                        const SizedBox(width: 12),
                        Text(
                          aiType,
                          style: TextStyle(
                            color: color,
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _getAgentLevelAndTitle(
                            learningScore.toDouble(),
                            aiType,
                          ),
                          style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Cycles: $totalCycles',
                          style: TextStyle(
                            color: Colors.orange[300],
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // Progress bar for leveling
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          LinearProgressIndicator(
                            value: progress.toDouble(),
                            minHeight: 8,
                            backgroundColor: Colors.grey[700],
                            valueColor: AlwaysStoppedAnimation<Color>(color),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Level Progress: ${learningScore.toStringAsFixed(0)} / ${nextLevelMin.toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[300],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _buildGrowthMetric(
                            'Growth Score',
                            dynamicGrowthScore.toStringAsFixed(0),
                            Colors.green,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildGrowthMetric(
                            'Confidence',
                            '${confidence.toStringAsFixed(1)}%',
                            Colors.blue,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildGrowthMetric(
                            'Approval Rate',
                            '${dynamicApprovalRate.toStringAsFixed(1)}%',
                            Colors.orange,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey[700],
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        difficultyDescription,
                        style: TextStyle(
                          color: Colors.grey[300],
                          fontSize: 10,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildGrowthMetric(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: TextStyle(fontSize: 10, color: Colors.grey[400]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildAgentRankings() {
    final agents = _aiStatus['agents'] as Map<String, dynamic>? ?? {};
    if (agents.isEmpty) {
      return const SizedBox.shrink();
    }

    // Filter to show only main AI types
    final filteredAgents = _filterMainAIAgents(agents);

    // Sort agents by learning score (highest to lowest)
    final sortedAgents =
        filteredAgents.entries.toList()..sort(
          (a, b) => (b.value['learning_score'] ?? 0.0).compareTo(
            a.value['learning_score'] ?? 0.0,
          ),
        );

    final provider = Provider.of<AICustomizationProvider>(
      context,
      listen: false,
    );

    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.grey[850],
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.leaderboard, color: Colors.purple[300], size: 24),
                const SizedBox(width: 12),
                Text(
                  'AI Rankings',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ...sortedAgents.asMap().entries.map((entry) {
              final rank = entry.key + 1;
              final agentName = entry.value.key;
              final agentData = entry.value.value;
              final learningScore = agentData['learning_score'] ?? 0.0;
              final totalCycles = agentData['total_learning_cycles'] ?? 0;
              final levelTitle = _getAgentLevelAndTitle(
                learningScore,
                agentName,
              );
              final romanLevel =
                  _extractNumericLevel(levelTitle) != null
                      ? _toRomanNumeral(_extractNumericLevel(levelTitle)!)
                      : null;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: provider.getColorForAI(agentName).withOpacity(0.3),
                    width: 1,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header row with icon and name
                    Row(
                      children: [
                        Icon(
                          _getAIIcon(agentName),
                          color: provider.getColorForAI(agentName),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          agentName,
                          style: TextStyle(
                            color: provider.getColorForAI(agentName),
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _getAgentLevelAndTitle(
                            learningScore.toDouble(),
                            agentName,
                          ),
                          style: TextStyle(
                            color: provider.getColorForAI(agentName),
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Cycles: $totalCycles',
                          style: TextStyle(
                            color: Colors.orange[300],
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Score: ${learningScore.toStringAsFixed(0)}',
                      style: TextStyle(color: Colors.grey[300], fontSize: 11),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.grey[850],
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.history, color: Colors.orange[300], size: 24),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Recent Activity',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (context, constraints) {
                return Row(
                  children: [
                    Expanded(
                      child: _buildActivitySection(
                        'Recent Failures',
                        _recentFailures,
                        Icons.error,
                        Colors.red,
                        constraints.maxWidth / 2 - 12, // Adjusted width
                      ),
                    ),
                    const SizedBox(width: 12), // Reduced spacing
                    Expanded(
                      child: _buildActivitySection(
                        'Recent Successes',
                        _recentSuccesses,
                        Icons.check_circle,
                        Colors.green,
                        constraints.maxWidth / 2 - 12, // Adjusted width
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActivitySection(
    String title,
    List<Map<String, dynamic>> activities,
    IconData icon,
    Color color,
    double maxWidth,
  ) {
    return Container(
      height: 180, // Reduced height to prevent overflow
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Icon(icon, color: color, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: TextStyle(
                      color: color,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children:
                    activities.isEmpty
                        ? [
                          Center(
                            child: Padding(
                              padding: const EdgeInsets.all(20),
                              child: Text(
                                'No ${title.toLowerCase()}',
                                style: TextStyle(color: Colors.grey[500]),
                              ),
                            ),
                          ),
                        ]
                        : activities.map<Widget>((activity) {
                          return Container(
                            margin: const EdgeInsets.only(bottom: 8),
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.grey[750],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Expanded(
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 6,
                                          vertical: 2,
                                        ),
                                        decoration: BoxDecoration(
                                          color: _getAIColor(
                                            activity['ai_type'],
                                          ).withOpacity(0.2),
                                          borderRadius: BorderRadius.circular(
                                            4,
                                          ),
                                        ),
                                        child: Text(
                                          activity['ai_type'],
                                          style: TextStyle(
                                            fontSize: 10,
                                            color: _getAIColor(
                                              activity['ai_type'],
                                            ),
                                            fontWeight: FontWeight.bold,
                                          ),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      '${((activity['confidence'] * 100).clamp(1, 100)).toStringAsFixed(0)}%',
                                      style: TextStyle(
                                        fontSize: 10,
                                        color: Colors.grey[400],
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  activity['message'],
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Colors.white,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          );
                        }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLearningInsights() {
    return Card(
      elevation: 6,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      color: Colors.grey[850],
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb, color: Colors.yellow[300], size: 24),
                const SizedBox(width: 12),
                Text(
                  'Learning Insights',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._learningInsights.map((insight) {
              final aiType = insight['ai_type'] as String;
              final insights =
                  insight['insights'] as Map<String, dynamic>? ?? {};
              final recommendations =
                  insights['recommendations'] as List? ?? [];

              return Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _getAIColor(aiType).withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          _getAIIcon(aiType),
                          color: _getAIColor(aiType),
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '${aiType[0].toUpperCase()}${aiType.substring(1)} Insights',
                          style: TextStyle(
                            color: _getAIColor(aiType),
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (recommendations.isNotEmpty)
                      ...recommendations
                          .map(
                            (rec) => Container(
                              margin: const EdgeInsets.only(bottom: 8),
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.grey[750],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.tips_and_updates,
                                    color: Colors.yellow[300],
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      rec,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.white,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          )
                          .toList()
                    else
                      Text(
                        'No specific insights available',
                        style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                      ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildAIStatusGrid() {
    // Return empty container to remove agent status section
    return const SizedBox.shrink();
  }

  // Helper methods
  Color _getAIColor(String aiType) {
    final normalizedType = aiType.toLowerCase();
    switch (normalizedType) {
      case 'imperium':
        return Colors.purple;
      case 'guardian':
        return Colors.green;
      case 'sandbox':
        return Colors.blue;
      case 'conquest':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getAIIcon(String aiType) {
    final normalizedType = aiType.toLowerCase();
    switch (normalizedType) {
      case 'imperium':
        return Icons.emoji_events; // Crown icon
      case 'guardian':
        return Icons.security;
      case 'sandbox':
        return Icons.science;
      case 'conquest':
        return Icons.rocket_launch;
      default:
        return Icons.smart_toy;
    }
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'healthy':
        return Colors.green;
      case 'warning':
        return Colors.orange;
      case 'error':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Color _getMaturityColor(String maturity) {
    switch (maturity) {
      case 'emerging':
        return Colors.blue;
      case 'developing':
        return Colors.orange;
      case 'mature':
        return Colors.green;
      case 'advanced':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  Color _getGrowthStageColor(String stage) {
    switch (stage) {
      case 'emerging':
        return Colors.blue;
      case 'developing':
        return Colors.orange;
      case 'mature':
        return Colors.green;
      case 'advanced':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  // Get agent level and title based on learning score and AI type
  // New scaling system: 1,000,000 points for highest level
  String _getAgentLevelAndTitle(double learningScore, String aiType) {
    final normalizedType = aiType.toLowerCase();

    // Conquest and Sandbox leveling system (based on apps created and learning)
    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      // Get Conquest AI data for apps created
      int appsCreated = 0;
      if (normalizedType == 'conquest') {
        try {
          final conquestProvider = Provider.of<ConquestAIProvider>(
            context,
            listen: false,
          );
          appsCreated = conquestProvider.totalAppsCount;
        } catch (e) {
          print('Error getting Conquest apps count: $e');
        }
      }

      // Conquest leveling based on apps created and learning score
      if (normalizedType == 'conquest') {
        if (learningScore >= 20000000 && appsCreated >= 10000) {
          return 'Fabricator General';
        } else if (learningScore >= 15000000 && appsCreated >= 5000) {
          return 'Archmagos';
        } else if (learningScore >= 10000000 && appsCreated >= 2500) {
          return 'Tech Priest Dominus';
        } else if (learningScore >= 5000000 && appsCreated >= 1000) {
          return 'Magos';
        } else if (learningScore >= 2000000 && appsCreated >= 500) {
          return 'Tech Priest (Engineer)';
        } else if (learningScore >= 1000000 && appsCreated >= 250) {
          return 'Initiate/Apprentice';
        } else if (learningScore >= 500000 && appsCreated >= 100) {
          return 'Skitarii';
        } else if (learningScore >= 200000 && appsCreated >= 50) {
          return 'Servitor';
        } else if (learningScore >= 50000) {
          return 'Menial';
        } else {
          return 'Cadet';
        }
      }
      // Sandbox leveling (based on learning score only)
      else {
        if (learningScore >= 20000000) {
          return 'Fabricator General';
        } else if (learningScore >= 15000000) {
          return 'Archmagos';
        } else if (learningScore >= 10000000) {
          return 'Tech Priest Dominus';
        } else if (learningScore >= 5000000) {
          return 'Magos';
        } else if (learningScore >= 2000000) {
          return 'Tech Priest (Cogitator)';
        } else if (learningScore >= 1000000) {
          return 'Initiate/Apprentice';
        } else if (learningScore >= 500000) {
          return 'Skitarii';
        } else if (learningScore >= 200000) {
          return 'Servitor';
        } else if (learningScore >= 50000) {
          return 'Menial';
        } else {
          return 'Cadet';
        }
      }
    }
    // Imperium and Guardian leveling system
    else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      if (learningScore >= 20000000) {
        if (normalizedType == 'imperium') {
          return 'Emperor';
        } else {
          return 'Chapter Master';
        }
      } else if (learningScore >= 15000000) {
        return 'Master of the Forge';
      } else if (learningScore >= 10000000) {
        // Specialist roles based on learning
        if (normalizedType == 'imperium') {
          return 'Librarian';
        } else {
          return 'Techmarine';
        }
      } else if (learningScore >= 5000000) {
        return 'Lieutenant';
      } else if (learningScore >= 2000000) {
        return 'Sergeant';
      } else if (learningScore >= 1000000) {
        return 'Veteran';
      } else if (learningScore >= 500000) {
        return 'Battle Brother';
      } else if (learningScore >= 200000) {
        return 'Neophyte';
      } else if (learningScore >= 50000) {
        return 'Aspirant';
      } else {
        return 'Recruit';
      }
    }

    // Default fallback
    return 'Cadet';
  }

  // Get color for agent level based on AI type
  Color _getAgentLevelColor(double learningScore, String aiType) {
    final normalizedType = aiType.toLowerCase();

    // Conquest and Sandbox colors (purple/blue theme)
    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      if (learningScore >= 1000000) {
        return Colors.deepPurple;
      } else if (learningScore >= 500000) {
        return Colors.purple;
      } else if (learningScore >= 250000) {
        return Colors.indigo;
      } else if (learningScore >= 100000) {
        return Colors.blue;
      } else if (learningScore >= 50000) {
        return Colors.teal;
      } else if (learningScore >= 25000) {
        return Colors.green;
      } else if (learningScore >= 10000) {
        return Colors.orange;
      } else if (learningScore >= 5000) {
        return Colors.deepOrange;
      } else if (learningScore >= 1000) {
        return Colors.red;
      } else {
        return Colors.grey;
      }
    }
    // Imperium and Guardian colors (gold/red theme)
    else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      if (learningScore >= 1000000) {
        return Colors.amber;
      } else if (learningScore >= 500000) {
        return Colors.deepOrange;
      } else if (learningScore >= 250000) {
        return Colors.orange;
      } else if (learningScore >= 100000) {
        return Colors.red;
      } else if (learningScore >= 50000) {
        return Colors.red[700]!;
      } else if (learningScore >= 25000) {
        return Colors.brown;
      } else if (learningScore >= 10000) {
        return Colors.orange;
      } else if (learningScore >= 5000) {
        return Colors.yellow;
      } else if (learningScore >= 1000) {
        return Colors.lightGreen;
      } else {
        return Colors.grey;
      }
    }

    // Default fallback
    return Colors.grey;
  }

  // Check if agent leveled up and show notification
  void _checkAndNotifyLevelUp(
    String agentName,
    double oldScore,
    double newScore,
    String aiType,
  ) {
    final oldLevel = _getAgentLevelAndTitle(oldScore, aiType);
    final newLevel = _getAgentLevelAndTitle(newScore, aiType);

    if (oldLevel != newLevel) {
      // Show level up notification
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.star, color: Colors.amber),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  '$agentName has leveled up to $newLevel!',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          backgroundColor: _getAgentLevelColor(newScore, aiType),
          duration: Duration(seconds: 4),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  // Get icon for agent type
  IconData _getAgentIcon(String agentName) {
    switch (agentName.toLowerCase()) {
      case 'imperium':
        return Icons.psychology;
      case 'guardian':
        return Icons.security;
      case 'sandbox':
        return Icons.science;
      case 'conquest':
        return Icons.rocket_launch;
      default:
        return Icons.smart_toy;
    }
  }

  double _toDouble(dynamic value) {
    if (value is num) {
      return value.toDouble();
    }
    return 0.0;
  }

  // Calculate dynamic growth score based on leveling system
  double _calculateDynamicGrowthScore(double baseScore, String aiType) {
    final normalizedType = aiType.toLowerCase();
    final level = _getAgentLevelAndTitle(baseScore, aiType);

    // Define difficulty multipliers based on level - much more extreme scaling
    double difficultyMultiplier = 1.0;

    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      switch (level) {
        case 'Fabricator General':
          difficultyMultiplier = 10000.0; // Extremely hard to improve
          break;
        case 'Archmagos':
          difficultyMultiplier = 5000.0;
          break;
        case 'Tech Priest Dominus':
          difficultyMultiplier = 2500.0;
          break;
        case 'Magos':
          difficultyMultiplier = 1000.0;
          break;
        case 'Tech Priest (Engineer)':
        case 'Tech Priest (Cogitator)':
          difficultyMultiplier = 500.0;
          break;
        case 'Initiate/Apprentice':
          difficultyMultiplier = 250.0;
          break;
        case 'Skitarii':
          difficultyMultiplier = 100.0;
          break;
        case 'Servitor':
          difficultyMultiplier = 50.0;
          break;
        case 'Menial':
          difficultyMultiplier = 20.0;
          break;
        default: // Cadet
          difficultyMultiplier = 10.0;
      }
    } else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      switch (level) {
        case 'Emperor':
        case 'Chapter Master':
          difficultyMultiplier = 10000.0; // Extremely hard to improve
          break;
        case 'Master of the Forge':
          difficultyMultiplier = 5000.0;
          break;
        case 'Librarian':
        case 'Techmarine':
          difficultyMultiplier = 2500.0;
          break;
        case 'Lieutenant':
          difficultyMultiplier = 1000.0;
          break;
        case 'Sergeant':
          difficultyMultiplier = 500.0;
          break;
        case 'Veteran':
          difficultyMultiplier = 250.0;
          break;
        case 'Battle Brother':
          difficultyMultiplier = 100.0;
          break;
        case 'Neophyte':
          difficultyMultiplier = 50.0;
          break;
        case 'Aspirant':
          difficultyMultiplier = 20.0;
          break;
        default: // Recruit
          difficultyMultiplier = 10.0;
      }
    }

    // Apply difficulty multiplier to make growth harder at higher levels
    return (baseScore / difficultyMultiplier).clamp(0.0, 100.0);
  }

  // Calculate dynamic approval rate based on leveling system
  double _calculateDynamicApprovalRate(double baseApprovalRate, String aiType) {
    final normalizedType = aiType.toLowerCase();
    final level = _getAgentLevelAndTitle(baseApprovalRate, aiType);

    // Define approval rate difficulty based on level - much more extreme scaling
    double approvalDifficulty = 1.0;

    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      switch (level) {
        case 'Fabricator General':
          approvalDifficulty =
              10000.0; // Requires 10000 successful proposals to count as 1
          break;
        case 'Archmagos':
          approvalDifficulty = 5000.0;
          break;
        case 'Tech Priest Dominus':
          approvalDifficulty = 2500.0;
          break;
        case 'Magos':
          approvalDifficulty = 1000.0;
          break;
        case 'Tech Priest (Engineer)':
        case 'Tech Priest (Cogitator)':
          approvalDifficulty = 500.0;
          break;
        case 'Initiate/Apprentice':
          approvalDifficulty = 250.0;
          break;
        case 'Skitarii':
          approvalDifficulty = 100.0;
          break;
        case 'Servitor':
          approvalDifficulty = 50.0;
          break;
        case 'Menial':
          approvalDifficulty = 20.0;
          break;
        default: // Cadet
          approvalDifficulty = 10.0;
      }
    } else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      switch (level) {
        case 'Emperor':
        case 'Chapter Master':
          approvalDifficulty =
              10000.0; // Requires 10000 successful proposals to count as 1
          break;
        case 'Master of the Forge':
          approvalDifficulty = 5000.0;
          break;
        case 'Librarian':
        case 'Techmarine':
          approvalDifficulty = 2500.0;
          break;
        case 'Lieutenant':
          approvalDifficulty = 1000.0;
          break;
        case 'Sergeant':
          approvalDifficulty = 500.0;
          break;
        case 'Veteran':
          approvalDifficulty = 250.0;
          break;
        case 'Battle Brother':
          approvalDifficulty = 100.0;
          break;
        case 'Neophyte':
          approvalDifficulty = 50.0;
          break;
        case 'Aspirant':
          approvalDifficulty = 20.0;
          break;
        default: // Recruit
          approvalDifficulty = 10.0;
      }
    }

    // Apply approval difficulty - higher levels need more successful proposals
    return (baseApprovalRate / approvalDifficulty).clamp(0.0, 100.0);
  }

  // Get level-based difficulty description
  String _getLevelDifficultyDescription(String aiType) {
    final normalizedType = aiType.toLowerCase();
    final level = _getAgentLevelAndTitle(0.0, aiType); // Get current level

    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      switch (level) {
        case 'Fabricator General':
          return 'Legendary difficulty - 10000x harder to improve';
        case 'Archmagos':
          return 'Mythic difficulty - 5000x harder to improve';
        case 'Tech Priest Dominus':
          return 'Epic difficulty - 2500x harder to improve';
        case 'Magos':
          return 'Master difficulty - 1000x harder to improve';
        case 'Tech Priest (Engineer)':
        case 'Tech Priest (Cogitator)':
          return 'Expert difficulty - 500x harder to improve';
        case 'Initiate/Apprentice':
          return 'Advanced difficulty - 250x harder to improve';
        case 'Skitarii':
          return 'Intermediate difficulty - 100x harder to improve';
        case 'Servitor':
          return 'Apprentice difficulty - 50x harder to improve';
        case 'Menial':
          return 'Novice difficulty - 20x harder to improve';
        default: // Cadet
          return 'Standard difficulty - 10x harder to improve';
      }
    } else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      switch (level) {
        case 'Emperor':
        case 'Chapter Master':
          return 'Legendary difficulty - 10000x harder to improve';
        case 'Master of the Forge':
          return 'Mythic difficulty - 5000x harder to improve';
        case 'Librarian':
        case 'Techmarine':
          return 'Epic difficulty - 2500x harder to improve';
        case 'Lieutenant':
          return 'Master difficulty - 1000x harder to improve';
        case 'Sergeant':
          return 'Expert difficulty - 500x harder to improve';
        case 'Veteran':
          return 'Advanced difficulty - 250x harder to improve';
        case 'Battle Brother':
          return 'Intermediate difficulty - 100x harder to improve';
        case 'Neophyte':
          return 'Apprentice difficulty - 50x harder to improve';
        case 'Aspirant':
          return 'Novice difficulty - 20x harder to improve';
        default: // Recruit
          return 'Standard difficulty - 10x harder to improve';
      }
    }

    return 'Standard difficulty - 10x harder to improve';
  }

  // Helper to get current and next level thresholds for an AI
  Map<String, num> _getLevelThresholds(double score, String aiType) {
    final normalizedType = aiType.toLowerCase();
    List<num> thresholds;
    if (normalizedType == 'conquest') {
      thresholds = [
        0,
        50000,
        200000,
        500000,
        1000000,
        2000000,
        5000000,
        10000000,
        15000000,
        20000000,
      ];
    } else if (normalizedType == 'sandbox') {
      thresholds = [
        0,
        50000,
        200000,
        500000,
        1000000,
        2000000,
        5000000,
        10000000,
        15000000,
        20000000,
      ];
    } else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      thresholds = [
        0,
        50000,
        200000,
        500000,
        1000000,
        2000000,
        5000000,
        10000000,
        15000000,
        20000000,
      ];
    } else {
      thresholds = [
        0,
        50000,
        200000,
        500000,
        1000000,
        2000000,
        5000000,
        10000000,
        15000000,
        20000000,
      ];
    }
    num current = thresholds[0];
    num next = thresholds.last;
    for (int i = 1; i < thresholds.length; i++) {
      if (score < thresholds[i]) {
        current = thresholds[i - 1];
        next = thresholds[i];
        break;
      }
    }
    return {'current': current, 'next': next};
  }

  // Helper to get emoji for each AI type
  String _getAIEmoji(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'imperium':
        return '👑';
      case 'conquest':
        return '⚔️';
      case 'guardian':
        return '🛡️';
      case 'sandbox':
        return '🧪';
      default:
        return '🤖';
    }
  }

  // Utility: Convert integer to Roman numeral
  String _toRomanNumeral(int number) {
    if (number <= 0) return '0';
    const List<String> romanSymbols = [
      'M',
      'CM',
      'D',
      'CD',
      'C',
      'XC',
      'L',
      'XL',
      'X',
      'IX',
      'V',
      'IV',
      'I',
    ];
    const List<int> values = [
      1000,
      900,
      500,
      400,
      100,
      90,
      50,
      40,
      10,
      9,
      5,
      4,
      1,
    ];
    String result = '';
    int num = number;
    for (int i = 0; i < romanSymbols.length; i++) {
      while (num >= values[i]) {
        result += romanSymbols[i];
        num -= values[i];
      }
    }
    return result;
  }

  // Helper to extract numeric level from title (returns null if not numeric)
  int? _extractNumericLevel(String levelTitle) {
    final match = RegExp(r'^Level (\d+)').firstMatch(levelTitle);
    if (match != null) {
      return int.tryParse(match.group(1)!);
    }
    return null;
  }

  // Filter and normalize AI agent names to show only main AI types
  Map<String, dynamic> _filterMainAIAgents(Map<String, dynamic> agents) {
    final Map<String, dynamic> filteredAgents = {};
    final Set<String> processedTypes = <String>{};

    // Define the main AI types we want to display
    final List<String> mainAITypes = [
      'sandbox',
      'imperium',
      'conquest',
      'guardian',
    ];

    for (final entry in agents.entries) {
      final agentName = entry.key.toLowerCase();
      final agentData = entry.value;

      // Find the main AI type this agent belongs to
      String? mainType;
      for (final mainAIType in mainAITypes) {
        if (agentName.contains(mainAIType)) {
          mainType = mainAIType;
          break;
        }
      }

      // If this is a main AI type and we haven't processed it yet
      if (mainType != null && !processedTypes.contains(mainType)) {
        processedTypes.add(mainType);

        // Use the main type name (capitalized) as the key
        final displayName = mainType[0].toUpperCase() + mainType.substring(1);
        filteredAgents[displayName] = agentData;
      }
    }

    return filteredAgents;
  }
}
