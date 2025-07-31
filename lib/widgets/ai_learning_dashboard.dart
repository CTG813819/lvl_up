import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/providers/conquest_ai_provider.dart';
import 'package:the_codex/providers/proposal_provider.dart';
import '../providers/ai_learning_provider.dart';
import '../services/network_config.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import '../services/ai_learning_service.dart';
import 'package:url_launcher/url_launcher.dart';

// AI Learning Dashboard Widget
// Displays comprehensive learning analytics for all AIs
class AILearningDashboard extends StatefulWidget {
  final Widget? connectionIndicator;
  const AILearningDashboard({Key? key, this.connectionIndicator})
    : super(key: key);

  @override
  State<AILearningDashboard> createState() => _AILearningDashboardState();
}

class _AILearningDashboardState extends State<AILearningDashboard> {
  bool _showDebugOutput = false;
  bool _isConnected = false;
  Timer? _pollingTimer;
  bool _connectionChecked = false;
  bool _isRefreshing = false; // For refresh button spinner

  @override
  void initState() {
    super.initState();
    _initializeData();
    _startPolling();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<AILearningProvider, ProposalProvider>(
      builder: (context, learningProvider, proposalProvider, child) {
        final aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
        final isOperating = true; // Always true as chaos/warp is removed
        final warpActive = false; // Always false as chaos/warp is removed
        final chaosActive = false; // Always false as chaos/warp is removed
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'AI Learning Analytics',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.deepPurple,
                ),
              ),
              const SizedBox(height: 18),
              // Centralized buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _isRefreshing
                      ? Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Colors.deepPurple,
                            ),
                          ),
                        ),
                      )
                      : ElevatedButton.icon(
                        icon: const Icon(Icons.refresh, size: 16),
                        label: const Text('Refresh Data'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor:
                              isOperating ? Colors.deepPurple : Colors.grey,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                        ),
                        onPressed:
                            isOperating
                                ? () async {
                                  setState(() => _isRefreshing = true);
                                  final learningProvider =
                                      Provider.of<AILearningProvider>(
                                        context,
                                        listen: false,
                                      );
                                  await Future.wait([
                                    learningProvider.fetchAIStatus(),
                                    learningProvider.fetchLearningData(),
                                    learningProvider.fetchLearningMetrics(),
                                    learningProvider.fetchDebugLog(),
                                    learningProvider.fetchQuotaStatus(),
                                  ]);
                                  setState(() => _isRefreshing = false);
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text(
                                        'Refreshing AI learning data...',
                                      ),
                                      backgroundColor: Colors.deepPurple,
                                    ),
                                  );
                                }
                                : null,
                      ),
                  const SizedBox(width: 16),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.science, size: 16),
                    label: const Text('Test Data'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          isOperating ? Colors.orange : Colors.grey,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                    ),
                    onPressed: isOperating ? () => _fetchTestData() : null,
                  ),
                ],
              ),
              const SizedBox(height: 18),
              // Operational Hours Status (always display, no spinner)
              FutureBuilder<Map<String, dynamic>>(
                future: _fetchOperatingHours(),
                builder: (context, snapshot) {
                  final fallbackHours = '5:00 AM - 9:00 PM';
                  final fallbackStatus = 'UNKNOWN';
                  final fallbackColor = Colors.grey;
                  String operatingHoursText = fallbackHours;
                  String currentTime = '';
                  String statusText = fallbackStatus;
                  Color statusColor = fallbackColor;
                  String pausedMsg = '';
                  bool isOperating = false;

                  if (snapshot.hasData && snapshot.data != null) {
                    final operatingHours = snapshot.data!;
                    operatingHoursText =
                        operatingHours['operationalHours']?['formatted'] ??
                        fallbackHours;
                    currentTime = operatingHours['currentTime'] ?? '';
                    isOperating =
                        operatingHours['isWithinOperationalHours'] ?? false;
                    if (isOperating) {
                      statusText = 'ACTIVE';
                      statusColor = Colors.green;
                    } else {
                      statusText = 'PAUSED';
                      statusColor = Colors.orange;
                      pausedMsg =
                          'System is currently paused/outside operational hours.';
                    }
                  } else if (snapshot.hasError) {
                    statusText = 'UNKNOWN';
                    statusColor = fallbackColor;
                  }

                  return Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.access_time,
                                color: statusColor,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Operating Hours',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              const Spacer(),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: statusColor.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: statusColor,
                                    width: 1,
                                  ),
                                ),
                                child: Text(
                                  statusText,
                                  style: TextStyle(
                                    color: statusColor,
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      'Hours: $operatingHoursText',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey[600],
                                      ),
                                    ),
                                    if (currentTime.isNotEmpty) ...[
                                      const SizedBox(height: 4),
                                      Text(
                                        'Current: ${DateTime.tryParse(currentTime)?.toLocal().toString().substring(11, 16) ?? currentTime}',
                                        style: TextStyle(
                                          fontSize: 14,
                                          color: Colors.grey[600],
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                            ],
                          ),
                          if (pausedMsg.isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              pausedMsg,
                              style: TextStyle(
                                color: Colors.orange,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 18),
              // Chaos/Warp Status
              // Removed chaos/warp status section
              const SizedBox(height: 18),
              ...aiTypes.map((aiType) {
                final data = learningProvider.getLearningDataForAI(aiType);
                final metrics = learningProvider.getLearningMetricsForAI(
                  aiType,
                );
                final isLearning =
                    learningProvider.aiLearningStatus[aiType]?['isLearning'] ==
                    true;

                // Debug: Print data to console
                print('[AI_LEARNING_DASHBOARD] $aiType data: $data');
                print('[AI_LEARNING_DASHBOARD] $aiType metrics: $metrics');
                print(
                  '[AI_LEARNING_DASHBOARD] $aiType isLearning: $isLearning',
                );

                final proposals = (data['userFeedback'] as List?)?.length ?? 0;
                final tests =
                    (data['backendTestResults'] as List?)?.length ?? 0;
                final lessons = (data['lessons'] as List?)?.length ?? 0;
                final score = metrics['learningScore'] ?? 0;
                final successRate = metrics['successRate'] ?? 0;
                final appliedLearning = metrics['appliedLearning'] ?? 0;
                final backendTestSuccessRate =
                    metrics['backendTestSuccessRate'] ?? 0;

                // Debug: Print calculated values
                print(
                  '[AI_LEARNING_DASHBOARD] $aiType calculated values: proposals=$proposals, tests=$tests, lessons=$lessons, score=$score, successRate=$successRate',
                );

                return Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SingleChildScrollView(
                          scrollDirection: Axis.horizontal,
                          child: Row(
                            children: [
                              Icon(
                                _getAIIcon(aiType),
                                color: _getAIColor(aiType),
                                size: 28,
                              ),
                              const SizedBox(width: 12),
                              Text(
                                aiType,
                                style: Theme.of(
                                  context,
                                ).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: _getAIColor(aiType),
                                ),
                              ),
                              const SizedBox(width: 16),
                              Chip(
                                avatar: Icon(
                                  isLearning
                                      ? Icons.pause_circle
                                      : Icons.play_circle,
                                  color:
                                      isLearning ? Colors.orange : Colors.green,
                                  size: 18,
                                ),
                                label: Text(
                                  isLearning ? 'Learning...' : 'Active',
                                  style: TextStyle(fontSize: 12),
                                ),
                                backgroundColor:
                                    isLearning
                                        ? Colors.orange.withOpacity(0.1)
                                        : Colors.green.withOpacity(0.1),
                              ),
                              const SizedBox(width: 8),
                              // Quota Status
                              Consumer<AILearningProvider>(
                                builder: (context, provider, child) {
                                  final quotaData =
                                      provider.quotaStatus[aiType];
                                  if (quotaData == null)
                                    return SizedBox.shrink();

                                  final currentPhase =
                                      quotaData['currentPhase'] ?? 'unknown';
                                  final cycleActive =
                                      quotaData['cycleActive'] ?? false;
                                  final phaseProgress =
                                      quotaData['phaseProgress'] ?? {};
                                  final phaseQuotas =
                                      quotaData['phaseQuotas'] ?? {};
                                  final isOperating =
                                      quotaData['isOperating'] ?? false;

                                  return Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Container(
                                        padding: EdgeInsets.symmetric(
                                          horizontal: 6,
                                          vertical: 2,
                                        ),
                                        decoration: BoxDecoration(
                                          color:
                                              cycleActive
                                                  ? Colors.blue.withOpacity(0.1)
                                                  : Colors.grey.withOpacity(
                                                    0.1,
                                                  ),
                                          borderRadius: BorderRadius.circular(
                                            8,
                                          ),
                                          border: Border.all(
                                            color:
                                                cycleActive
                                                    ? Colors.blue
                                                    : Colors.grey,
                                            width: 1,
                                          ),
                                        ),
                                        child: Text(
                                          currentPhase.toUpperCase(),
                                          style: TextStyle(
                                            color:
                                                cycleActive
                                                    ? Colors.blue
                                                    : Colors.grey,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 10,
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      if (cycleActive && isOperating) ...[
                                        Text(
                                          '${phaseProgress[currentPhase] ?? 0}',
                                          style: TextStyle(
                                            fontSize: 12,
                                            fontWeight: FontWeight.bold,
                                            color: Colors.grey[700],
                                          ),
                                        ),
                                      ] else if (!isOperating) ...[
                                        Icon(
                                          Icons.access_time,
                                          size: 16,
                                          color: Colors.orange,
                                        ),
                                      ],
                                    ],
                                  );
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        if (isLearning)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    Icon(
                                      Icons.pause_circle,
                                      color: Colors.orange,
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        'Learning in progress. Actions are paused.',
                                        style: TextStyle(
                                          color: Colors.orange,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.end,
                                  children: [
                                    ElevatedButton.icon(
                                      icon: const Icon(Icons.refresh, size: 16),
                                      label: const Text('Reset Learning'),
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: Colors.red,
                                        foregroundColor: Colors.white,
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 12,
                                          vertical: 8,
                                        ),
                                      ),
                                      onPressed:
                                          () => _resetLearningState(aiType),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        Wrap(
                          spacing: 16,
                          runSpacing: 12,
                          children: [
                            _buildInfoChip(
                              Icons.psychology,
                              'Lessons',
                              lessons,
                              Colors.deepPurple,
                            ),
                            _buildInfoChip(
                              Icons.assignment,
                              'Proposals',
                              proposals,
                              Colors.green,
                            ),
                            _buildInfoChip(
                              Icons.science,
                              'Tests',
                              tests,
                              Colors.orange,
                            ),
                            _buildInfoChip(
                              Icons.trending_up,
                              'Score',
                              score,
                              Colors.cyan,
                            ),
                            _buildInfoChip(
                              Icons.check_circle,
                              'Success Rate',
                              '$successRate%',
                              Colors.blue,
                            ),
                            _buildInfoChip(
                              Icons.school,
                              'Applied Learning',
                              '$appliedLearning%',
                              Colors.purple,
                            ),
                            _buildInfoChip(
                              Icons.cloud_done,
                              'Backend Test Success',
                              '$backendTestSuccessRate%',
                              Colors.teal,
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        if ((data['lessons'] as List?)?.isNotEmpty ??
                            false) ...[
                          Text(
                            'Recent Lessons:',
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          SizedBox(
                            height: 120, // Adjust as needed
                            child: ListView.builder(
                              itemCount: (data['lessons'] as List).length,
                              itemBuilder: (context, i) {
                                final lesson = (data['lessons'] as List)[i];
                                return Text(
                                  '• ${lesson['lesson']}',
                                  style: TextStyle(color: Colors.grey[800]),
                                );
                              },
                            ),
                          ),
                        ],
                        if ((data['backendTestResults'] as List?)?.isNotEmpty ??
                            false) ...[
                          const SizedBox(height: 12),
                          Text(
                            'Recent Test Results:',
                            style: Theme.of(context).textTheme.titleMedium
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 8),
                          ...List.generate(
                            (data['backendTestResults'] as List).length > 3
                                ? 3
                                : (data['backendTestResults'] as List).length,
                            (i) {
                              final test =
                                  (data['backendTestResults'] as List)[i];
                              return Text(
                                '• ${test['testType']}: ${test['result']}',
                                style: TextStyle(
                                  color:
                                      test['result'] == 'pass'
                                          ? Colors.green
                                          : Colors.red,
                                ),
                              );
                            },
                          ),
                        ],
                        // Debug section to show raw data
                        if (_showDebugOutput) ...[
                          const SizedBox(height: 12),
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: Colors.grey[300]!),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Debug Data for $aiType:',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 12,
                                  ),
                                ),
                                Text(
                                  'Data keys: ${data.keys.toList()}',
                                  style: TextStyle(fontSize: 10),
                                ),
                                Text(
                                  'Metrics keys: ${metrics.keys.toList()}',
                                  style: TextStyle(fontSize: 10),
                                ),
                                Text(
                                  'Learning status: ${learningProvider.aiLearningStatus[aiType]}',
                                  style: TextStyle(fontSize: 10),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              }),
              // Add Conquest AI analytics card
              Consumer<ConquestAIProvider>(
                builder: (context, conquestProvider, child) {
                  final conquestStatus = conquestProvider.conquestStatus;
                  final totalApps = conquestProvider.totalAppsCount;
                  final successRate = (conquestProvider.successRate * 100)
                      .toStringAsFixed(1);
                  final avgBuildTime = conquestProvider.averageBuildTime;
                  final isActive = conquestProvider.isConquestActive;
                  final completedApps =
                      conquestProvider.getCompletedApps.take(3).toList();
                  Color conquestColor = Colors.deepPurple.shade900;
                  return Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(18),
                    ),
                    margin: const EdgeInsets.only(bottom: 20),
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons
                                    .whatshot, // Monster/dragon icon alternative
                                color: conquestColor,
                                size: 32,
                                shadows: [
                                  Shadow(
                                    color: Colors.purpleAccent.withOpacity(0.7),
                                    blurRadius: 16,
                                  ),
                                ],
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Conquest AI',
                                style: Theme.of(
                                  context,
                                ).textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: conquestColor,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Chip(
                                avatar: Icon(
                                  isActive
                                      ? Icons.play_circle
                                      : Icons.pause_circle,
                                  color:
                                      isActive ? Colors.green : Colors.orange,
                                  size: 18,
                                ),
                                label: Text(
                                  isActive ? 'Active' : 'Paused',
                                  style: TextStyle(fontSize: 12),
                                ),
                                backgroundColor:
                                    isActive
                                        ? Colors.green.withOpacity(0.1)
                                        : Colors.orange.withOpacity(0.1),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Wrap(
                            spacing: 16,
                            runSpacing: 12,
                            children: [
                              _buildInfoChip(
                                Icons.apps,
                                'Total Apps',
                                totalApps,
                                conquestColor,
                              ),
                              _buildInfoChip(
                                Icons.check_circle,
                                'Success Rate',
                                '$successRate%',
                                Colors.green,
                              ),
                              _buildInfoChip(
                                Icons.timer,
                                'Avg Build Time',
                                avgBuildTime.inMinutes > 0
                                    ? '${avgBuildTime.inMinutes} min'
                                    : '${avgBuildTime.inSeconds} sec',
                                Colors.purple,
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          if (completedApps.isNotEmpty) ...[
                            Text(
                              'Recent Completed Apps:',
                              style: Theme.of(context).textTheme.titleMedium
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            ...completedApps.map(
                              (app) => ListTile(
                                leading: Icon(
                                  Icons.android,
                                  color: conquestColor,
                                ),
                                title: Text(
                                  app.name,
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                subtitle: Text(
                                  'Status: ${app.status} | Progress: ${(app.progress * 100).toStringAsFixed(0)}%',
                                ),
                                trailing:
                                    app.githubRepoUrl != null
                                        ? IconButton(
                                          icon: Icon(
                                            Icons.link,
                                            color: Colors.blue,
                                          ),
                                          onPressed: () {
                                            // Open GitHub repo
                                            if (app.githubRepoUrl != null) {
                                              launchUrl(
                                                Uri.parse(app.githubRepoUrl!),
                                              );
                                            }
                                          },
                                        )
                                        : null,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 18),

              // Debug Log Section
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.bug_report,
                            color: Colors.orange,
                            size: 24,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Debug Log & Learning Events',
                            style: Theme.of(
                              context,
                            ).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.orange,
                            ),
                          ),
                          const Spacer(),
                          Switch(
                            value: _showDebugOutput,
                            onChanged: (value) {
                              setState(() {
                                _showDebugOutput = value;
                              });
                            },
                          ),
                        ],
                      ),
                      if (_showDebugOutput) ...[
                        const SizedBox(height: 12),
                        Container(
                          height: 200,
                          decoration: BoxDecoration(
                            color: Colors.black,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey[700]!),
                          ),
                          child: Consumer<AILearningProvider>(
                            builder: (context, provider, child) {
                              final debugEntries =
                                  provider.getRecentDebugEntries();
                              if (debugEntries.isEmpty) {
                                return const Center(
                                  child: Text(
                                    'No debug events yet...',
                                    style: TextStyle(color: Colors.grey),
                                  ),
                                );
                              }
                              return ListView.builder(
                                padding: const EdgeInsets.all(8),
                                itemCount: debugEntries.length,
                                itemBuilder: (context, index) {
                                  final entry = debugEntries[index];
                                  final message =
                                      entry['message']?.toString() ?? '';
                                  final timestamp =
                                      entry['timestamp']?.toString() ?? '';

                                  // Color code based on message content
                                  Color textColor = Colors.white;
                                  if (message.contains('ERROR') ||
                                      message.contains('❌')) {
                                    textColor = Colors.red;
                                  } else if (message.contains('WARNING') ||
                                      message.contains('⚠️')) {
                                    textColor = Colors.orange;
                                  } else if (message.contains('SUCCESS') ||
                                      message.contains('✅')) {
                                    textColor = Colors.green;
                                  } else if (message.contains('LEARNING') ||
                                      message.contains('🧠')) {
                                    textColor = Colors.blue;
                                  }

                                  return Padding(
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 2,
                                    ),
                                    child: Row(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          timestamp.length > 19
                                              ? timestamp.substring(11, 19)
                                              : timestamp,
                                          style: TextStyle(
                                            color: Colors.grey[500],
                                            fontSize: 10,
                                            fontFamily: 'monospace',
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Text(
                                            message,
                                            style: TextStyle(
                                              color: textColor,
                                              fontSize: 11,
                                              fontFamily: 'monospace',
                                            ),
                                            overflow: TextOverflow.ellipsis,
                                            maxLines: 2,
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              );
                            },
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 18),

              // Learning Effectiveness Section (show only in last 30 min of operational day)
              FutureBuilder<Map<String, dynamic>>(
                future: _fetchOperatingHours(),
                builder: (context, snapshot) {
                  if (!snapshot.hasData || snapshot.data == null)
                    return SizedBox.shrink();
                  final operatingHours = snapshot.data!;
                  final endTimeStr =
                      operatingHours['operationalHours']
                          ?.split('-')
                          .last
                          .trim() ??
                      '23:30';
                  final now = DateTime.now();
                  final endParts = endTimeStr.split(':');
                  final endHour = int.tryParse(endParts[0]) ?? 21;
                  final endMinute =
                      int.tryParse(endParts.length > 1 ? endParts[1] : '0') ??
                      0;
                  final endOfDay = DateTime(
                    now.year,
                    now.month,
                    now.day,
                    endHour,
                    endMinute,
                  );
                  final diff = endOfDay.difference(now);
                  if (diff.inMinutes > 30 || diff.isNegative)
                    return SizedBox.shrink();
                  return Card(
                    elevation: 1,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.analytics,
                                color: Colors.grey[600],
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                'Learning Effectiveness (End of Day Analysis)',
                                style: Theme.of(
                                  context,
                                ).textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.grey[600],
                                ),
                              ),
                              const Spacer(),
                              Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 6,
                                  vertical: 2,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.grey.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: Colors.grey.withOpacity(0.3),
                                  ),
                                ),
                                child: Text(
                                  'SCHEDULED',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontWeight: FontWeight.bold,
                                    fontSize: 10,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Runs 30 minutes before end of operational day to analyze learning patterns and optimize future sessions.',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                          const SizedBox(height: 12),
                          FutureBuilder<Map<String, dynamic>>(
                            future: _fetchLearningEffectiveness(),
                            builder: (context, snapshot) {
                              if (snapshot.connectionState ==
                                  ConnectionState.waiting) {
                                return const Center(
                                  child: SizedBox(
                                    height: 20,
                                    width: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                    ),
                                  ),
                                );
                              }
                              if (snapshot.hasError || !snapshot.hasData) {
                                return Text(
                                  'Analysis scheduled for end of day',
                                  style: TextStyle(
                                    color: Colors.grey[500],
                                    fontSize: 12,
                                  ),
                                );
                              }
                              final effectiveness = snapshot.data!;
                              final overall =
                                  (effectiveness['overall'] ?? {}) as Map;
                              final overallMap =
                                  overall.cast<String, dynamic>();
                              return Row(
                                children: [
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Completion Rate',
                                      '${overallMap['completionRate'] ?? 0}%',
                                      Colors.grey[600]!,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Improvement',
                                      '${overallMap['averageImprovement'] ?? 0}%',
                                      Colors.grey[600]!,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Sessions',
                                      '${overallMap['totalLearningSessions'] ?? 0}',
                                      Colors.grey[600]!,
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
                },
              ),

              const SizedBox(height: 18),
            ],
          ),
        );
      },
    );
  }

  List<Map<String, dynamic>> _getGroupedLessons(List lessons) {
    // Group lessons by month and return the most recent 3
    final now = DateTime.now();
    final lessonsWithDates =
        lessons
            .map((lesson) {
              final timestamp = lesson['timestamp'] ?? now.toIso8601String();
              final date = DateTime.tryParse(timestamp) ?? now;
              return {
                ...lesson,
                'date': date,
                'month':
                    '${date.year}-${date.month.toString().padLeft(2, '0')}',
              };
            })
            .map((e) => (e as Map).cast<String, dynamic>())
            .toList();

    // Sort by date (most recent first)
    lessonsWithDates.sort((a, b) => b['date'].compareTo(a['date']));

    // Group by month
    final grouped = <String, List<Map<String, dynamic>>>{};
    for (final lesson in lessonsWithDates) {
      final month = lesson['month'];
      grouped.putIfAbsent(month, () => []).add(lesson);
    }

    // Return the most recent 3 lessons
    return lessonsWithDates.take(3).toList();
  }

  Widget _buildInfoChip(
    IconData icon,
    String label,
    dynamic value,
    Color color,
  ) {
    return Chip(
      avatar: Icon(icon, color: color, size: 18),
      label: Text(
        '$value $label',
        style: TextStyle(color: color, fontWeight: FontWeight.bold),
      ),
      backgroundColor: color.withOpacity(0.08),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    );
  }

  IconData _getAIIcon(String aiType) {
    switch (aiType) {
      case 'Imperium':
        return Icons.fort;
      case 'Sandbox':
        return Icons.science;
      case 'Guardian':
        return Icons.security;
      default:
        return Icons.psychology;
    }
  }

  Color _getAIColor(String aiType) {
    switch (aiType) {
      case 'Imperium':
        return Colors.purple;
      case 'Sandbox':
        return Colors.blue;
      case 'Guardian':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Widget _buildMetricCard(String title, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.05),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.2)),
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
            style: TextStyle(fontSize: 10, color: color.withOpacity(0.8)),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Future<Map<String, dynamic>> _fetchLearningEffectiveness() async {
    try {
      final response = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/learning/data'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['effectiveness'] ?? {};
      }
    } catch (e) {
      print('[AI_LEARNING_DASHBOARD] Error fetching effectiveness: $e');
    }
    return {};
  }

  Future<void> _resetLearningState(String aiType) async {
    try {
      final provider = Provider.of<AILearningProvider>(context, listen: false);
      final success = await provider.resetLearningState(aiType);

      if (context.mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Learning state reset for $aiType'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to reset learning state for $aiType'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error resetting learning state: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<bool> _checkBackendConnection() async {
    try {
      final service = AILearningService();
      return await service.testBackendConnection(userId: 'dashboard-user');
    } catch (e) {
      print('[AI_LEARNING_DASHBOARD] Error checking backend connection: $e');
      return false;
    }
  }

  Future<void> _fetchTestData() async {
    try {
      final response = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/learning/data'),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print(
          '[AI_LEARNING_DASHBOARD] Test data received: ${data.keys.toList()}',
        );
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Test data fetched successfully: ${data.keys.length} AIs',
              ),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Failed to fetch test data: ${response.statusCode}',
              ),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error fetching test data: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<Map<String, dynamic>> _fetchOperatingHours() async {
    try {
      final response = await http.get(
        Uri.parse(
          '${NetworkConfig.backendUrl}/chaos-warp/operational-hours',
        ),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data;
      }
    } catch (e) {
      print('[AI_LEARNING_DASHBOARD] Error fetching operating hours: $e');
    }
    return {};
  }

  void _initializeData() {
    // Initialize data when widget loads
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final learningProvider = Provider.of<AILearningProvider>(
        context,
        listen: false,
      );
      setState(() => _isRefreshing = true);
      await Future.wait([
        learningProvider.fetchAIStatus(),
        learningProvider.fetchLearningData(),
        learningProvider.fetchLearningMetrics(),
        learningProvider.fetchDebugLog(),
        learningProvider.fetchQuotaStatus(),
      ]);
      setState(() => _isRefreshing = false);
    });
  }

  void _startPolling() {
    // Poll for updates every 30 seconds (less frequent)
    _pollingTimer = Timer.periodic(Duration(seconds: 30), (timer) async {
      if (mounted) {
        final learningProvider = Provider.of<AILearningProvider>(
          context,
          listen: false,
        );
        await Future.wait([
          learningProvider.fetchAIStatus(),
          learningProvider.fetchLearningData(),
          learningProvider.fetchLearningMetrics(),
          learningProvider.fetchDebugLog(),
          learningProvider.fetchQuotaStatus(),
        ]);
      }
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  // Add a getter for the backend connection indicator dot only
  Widget getBackendConnectionDot() {
    return FutureBuilder<bool>(
      future: _checkBackendConnection(),
      builder: (context, snapshot) {
        Color dotColor;
        if (snapshot.connectionState == ConnectionState.waiting) {
          dotColor = Colors.orange;
        } else {
          dotColor = (snapshot.data ?? false) ? Colors.green : Colors.red;
        }
        return Container(
          width: 12,
          height: 12,
          margin: const EdgeInsets.only(right: 16),
          decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle),
        );
      },
    );
  }
}
