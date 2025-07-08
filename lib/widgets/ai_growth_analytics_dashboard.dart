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

/// AI Growth Analytics Dashboard
/// Comprehensive analytics showing AI growth, learning, failures, and successes
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

  late AnimationController _fadeController;
  late AnimationController _slideController;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _loadData();
    _startPolling();
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

  @override
  void dispose() {
    _pollingTimer?.cancel();
    _fadeController.dispose();
    _slideController.dispose();
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
    } catch (e) {
      print('Error loading analytics data: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadGrowthData() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/imperium/growth/all',
        ),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _growthData = data;
        });
      }
    } catch (e) {
      print('Error loading growth data: $e');
    }
  }

  Future<void> _loadAIStatus() async {
    try {
      final response = await http.get(
        Uri.parse(
          'http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/agents/status',
        ),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _aiStatus = data;
        });
      }
    } catch (e) {
      print('Error loading AI status: $e');
    }
  }

  Future<void> _loadRecentActivity() async {
    try {
      // Load recent failures and successes from learning data
      final response = await http.get(
        Uri.parse(
          'http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/learning/data',
        ),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _processActivityData(data);
      }
    } catch (e) {
      print('Error loading recent activity: $e');
    }
  }

  Future<void> _loadLearningInsights() async {
    try {
      final aiTypes = ['Imperium', 'Guardian', 'Sandbox', 'Conquest'];
      final insights = <Map<String, dynamic>>[];

      for (final aiType in aiTypes) {
        final response = await http.get(
          Uri.parse(
            'http://ec2-34-202-215-209.compute-1.amazonaws.com:4001/api/learning/insights/$aiType',
          ),
        );
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          insights.add({'ai_type': aiType, 'insights': data});
        }
      }

      setState(() {
        _learningInsights = insights;
      });
    } catch (e) {
      print('Error loading learning insights: $e');
    }
  }

  void _processActivityData(Map<String, dynamic> data) {
    final failures = <Map<String, dynamic>>[];
    final successes = <Map<String, dynamic>>[];

    // Process learning data to extract failures and successes
    for (final aiType in data.keys) {
      final aiData = data[aiType] as Map<String, dynamic>;
      final userFeedback = aiData['userFeedback'] as List? ?? [];
      final backendTests = aiData['backendTestResults'] as List? ?? [];

      // Process user feedback
      for (final feedback in userFeedback) {
        if (feedback['accepted'] == false) {
          failures.add({
            'ai_type': aiType,
            'type': 'user_rejection',
            'message': feedback['feedback'] ?? 'Proposal rejected',
            'timestamp': feedback['timestamp'],
            'confidence': feedback['confidence'] ?? 0.0,
          });
        } else if (feedback['accepted'] == true) {
          successes.add({
            'ai_type': aiType,
            'type': 'user_acceptance',
            'message': feedback['feedback'] ?? 'Proposal accepted',
            'timestamp': feedback['timestamp'],
            'confidence': feedback['confidence'] ?? 0.0,
          });
        }
      }

      // Process backend tests
      for (final test in backendTests) {
        if (test['result'] == 'fail') {
          failures.add({
            'ai_type': aiType,
            'type': 'backend_failure',
            'message': test['error'] ?? 'Backend test failed',
            'timestamp': test['timestamp'],
            'confidence': test['confidence'] ?? 0.0,
          });
        } else if (test['result'] == 'pass') {
          successes.add({
            'ai_type': aiType,
            'type': 'backend_success',
            'message': test['message'] ?? 'Backend test passed',
            'timestamp': test['timestamp'],
            'confidence': test['confidence'] ?? 0.0,
          });
        }
      }
    }

    // Sort by timestamp (most recent first)
    failures.sort((a, b) => b['timestamp'].compareTo(a['timestamp']));
    successes.sort((a, b) => b['timestamp'].compareTo(a['timestamp']));

    setState(() {
      _recentFailures = failures.take(10).toList();
      _recentSuccesses = successes.take(10).toList();
    });
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        _loadData();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AIGrowthAnalyticsProvider>(context);
    final log = provider.internetLearningLog;
    final aiList = ['imperium', 'guardian', 'sandbox', 'conquest'];

    return FutureBuilder<Map<String, dynamic>>(
      future: provider.fetchInternetLearningImpact(),
      builder: (context, snapshot) {
        final impact = snapshot.data ?? {};
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
                    onPressed: _loadData,
                  ),
                ],
              ),
              body:
                  _isLoading
                      ? const Center(
                        child: CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Colors.blue,
                          ),
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
                            _buildRecentActivity(),
                            const SizedBox(height: 20),
                            _buildLearningInsights(),
                            const SizedBox(height: 20),
                            _buildAIStatusGrid(),
                            const SizedBox(height: 20),
                            ...aiList.map((ai) {
                              final aiLog =
                                  log
                                      .where((e) => e['agent_id'] == ai)
                                      .toList();
                              final aiImpact = impact[ai] ?? {};
                              return Card(
                                margin: const EdgeInsets.all(8),
                                child: ExpansionTile(
                                  title: Text(
                                    '${ai[0].toUpperCase()}${ai.substring(1)} AI Learning',
                                  ),
                                  children: [
                                    ListTile(
                                      title: Text('Currently Learning:'),
                                      subtitle: Text(
                                        aiLog.isNotEmpty
                                            ? aiLog.last['topic']
                                            : 'N/A',
                                      ),
                                    ),
                                    ListTile(
                                      title: Text('Recent Learnings:'),
                                      subtitle: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children:
                                            aiLog
                                                .take(5)
                                                .map(
                                                  (e) => Text(
                                                    '${e['topic']} (${e['timestamp']})',
                                                  ),
                                                )
                                                .toList(),
                                      ),
                                    ),
                                    ListTile(
                                      title: Text('Recommendations:'),
                                      subtitle: Text(
                                        (aiImpact['improvement_suggestions']
                                                    as List?)
                                                ?.join(', ') ??
                                            'N/A',
                                      ),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.all(8.0),
                                      child: _AddTopicForm(
                                        ai: ai,
                                        provider: provider,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ],
                        ),
                      ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSystemOverview() {
    final overallGrowth =
        _growthData['overall_growth'] as Map<String, dynamic>? ?? {};
    final systemMaturity = overallGrowth['system_maturity'] ?? 'unknown';
    final avgGrowthScore = (overallGrowth['average_growth_score'] ?? 0.0) * 100;
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
                      '${avgGrowthScore.toStringAsFixed(1)}%',
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
    final aiGrowthInsights =
        _growthData['ai_growth_insights'] as Map<String, dynamic>? ?? {};

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
            ...aiGrowthInsights.entries.map((entry) {
              final aiType = entry.key;
              final insight = entry.value as Map<String, dynamic>;
              final growthPotential =
                  insight['growth_potential'] as Map<String, dynamic>? ?? {};
              final currentPerformance =
                  insight['current_performance'] as Map<String, dynamic>? ?? {};

              final growthScore =
                  (growthPotential['growth_score'] ?? 0.0) * 100;
              final growthStage = growthPotential['growth_stage'] ?? 'unknown';
              final avgConfidence =
                  (currentPerformance['avg_confidence'] ?? 0.0) * 100;
              final approvalRate =
                  (currentPerformance['approval_rate'] ?? 0.0) * 100;

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
                          size: 24,
                        ),
                        const SizedBox(width: 12),
                        Text(
                          aiType,
                          style: TextStyle(
                            color: _getAIColor(aiType),
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getGrowthStageColor(growthStage),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            growthStage.toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: _buildGrowthMetric(
                            'Growth Score',
                            '${growthScore.toStringAsFixed(1)}%',
                            Colors.green,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildGrowthMetric(
                            'Confidence',
                            '${((avgConfidence * 100).clamp(1, 100)).toStringAsFixed(0)}%',
                            Colors.blue,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: _buildGrowthMetric(
                            'Approval Rate',
                            '${approvalRate.toStringAsFixed(1)}%',
                            Colors.orange,
                          ),
                        ),
                      ],
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
                        constraints.maxWidth / 2 - 8, // pass width
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: _buildActivitySection(
                        'Recent Successes',
                        _recentSuccesses,
                        Icons.check_circle,
                        Colors.green,
                        constraints.maxWidth / 2 - 8, // pass width
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
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children:
              activities.isEmpty
                  ? [
                    Center(
                      child: Text(
                        'No ${title.toLowerCase()}',
                        style: TextStyle(color: Colors.grey[500]),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
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
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: _getAIColor(
                                    activity['ai_type'],
                                  ).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  activity['ai_type'],
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: _getAIColor(activity['ai_type']),
                                    fontWeight: FontWeight.bold,
                                  ),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              const Spacer(),
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
                          '$aiType Insights',
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
    final agents = _aiStatus['agents'] as Map<String, dynamic>? ?? {};
    final autonomousRunning = _aiStatus['autonomous_cycle_running'] ?? false;

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
                Icon(Icons.dashboard, color: Colors.blue[300], size: 24),
                const SizedBox(width: 12),
                Text(
                  'AI Agent Status',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: autonomousRunning ? Colors.green : Colors.red,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    autonomousRunning ? 'AUTONOMOUS' : 'MANUAL',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.5,
              children:
                  agents.entries.map((entry) {
                    final aiType = entry.key;
                    final status = entry.value as Map<String, dynamic>;
                    final agentStatus = status['status'] ?? 'unknown';
                    final lastRun = status['last_run'] ?? 'unknown';

                    return Container(
                      decoration: BoxDecoration(
                        color: Colors.grey[800],
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _getStatusColor(agentStatus).withOpacity(0.3),
                        ),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              _getAIIcon(aiType),
                              color: _getAIColor(aiType),
                              size: 32,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              aiType,
                              style: TextStyle(
                                color: _getAIColor(aiType),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: _getStatusColor(agentStatus),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                agentStatus.toUpperCase(),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  // Helper methods
  Color _getAIColor(String aiType) {
    switch (aiType) {
      case 'Imperium':
        return Colors.purple;
      case 'Guardian':
        return Colors.green;
      case 'Sandbox':
        return Colors.blue;
      case 'Conquest':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  IconData _getAIIcon(String aiType) {
    switch (aiType) {
      case 'Imperium':
        return Icons.psychology;
      case 'Guardian':
        return Icons.security;
      case 'Sandbox':
        return Icons.science;
      case 'Conquest':
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
}

class _AddTopicForm extends StatefulWidget {
  final String ai;
  final AIGrowthAnalyticsProvider provider;
  const _AddTopicForm({required this.ai, required this.provider});

  @override
  State<_AddTopicForm> createState() => _AddTopicFormState();
}

class _AddTopicFormState extends State<_AddTopicForm> {
  final controller = TextEditingController();
  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: controller,
            decoration: InputDecoration(
              labelText: 'Add topic for ${widget.ai}',
              border: OutlineInputBorder(),
            ),
          ),
        ),
        const SizedBox(width: 8),
        ElevatedButton(
          onPressed: () {
            if (controller.text.trim().isNotEmpty) {
              widget.provider.addTopicForAI(widget.ai, controller.text.trim());
              controller.clear();
            }
          },
          child: const Text('Add'),
        ),
      ],
    );
  }
}
