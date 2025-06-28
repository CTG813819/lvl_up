import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/ai_learning_provider.dart';
import '../providers/proposal_provider.dart';
import '../providers/chaos_warp_provider.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';

/// AI Learning Dashboard Widget
/// Displays comprehensive learning analytics for all AIs
class AILearningDashboard extends StatefulWidget {
  const AILearningDashboard({Key? key}) : super(key: key);

  @override
  State<AILearningDashboard> createState() => _AILearningDashboardState();
}

class _AILearningDashboardState extends State<AILearningDashboard> {
  bool _showDebugOutput = false;
  bool _isExpanded = false;
  bool _isLoading = false;
  bool _isConnected = false;
  Map<String, dynamic>? _aiStatus;
  List<Map<String, dynamic>> _debugLogs = [];
  List<Map<String, dynamic>> _learningData = [];
  Map<String, dynamic>? _operatingHours;
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _initializeData();
    _startPolling();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AILearningProvider>(
      builder: (context, learningProvider, child) {
        // Fetch all data when dashboard loads
        WidgetsBinding.instance.addPostFrameCallback((_) {
          learningProvider.fetchAIStatus();
          learningProvider.fetchLearningData();
          learningProvider.fetchLearningMetrics();
          learningProvider.fetchDebugLog();
        });
        
        final aiTypes = ['Imperium', 'Sandbox', 'Guardian'];
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
              // Refresh button
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Real-time AI learning data and analytics',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 14,
                          ),
                        ),
                        const SizedBox(height: 4),
                        FutureBuilder<bool>(
                          future: _checkBackendConnection(),
                          builder: (context, snapshot) {
                            if (snapshot.connectionState == ConnectionState.waiting) {
                              return Row(
                                children: [
                                  SizedBox(width: 12, height: 12, child: CircularProgressIndicator(strokeWidth: 2)),
                                  const SizedBox(width: 8),
                                  Text('Checking connection...', style: TextStyle(fontSize: 12, color: Colors.orange)),
                                ],
                              );
                            }
                            
                            final isConnected = snapshot.data ?? false;
                            return Row(
                              children: [
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: isConnected ? Colors.green : Colors.red,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  isConnected ? 'Backend connected' : 'Backend disconnected',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: isConnected ? Colors.green : Colors.red,
                                  ),
                                ),
                              ],
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('Refresh Data'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                    onPressed: () {
                      learningProvider.fetchAIStatus();
                      learningProvider.fetchLearningData();
                      learningProvider.fetchLearningMetrics();
                      learningProvider.fetchDebugLog();
                      learningProvider.fetchQuotaStatus();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Refreshing AI learning data...'),
                          backgroundColor: Colors.deepPurple,
                        ),
                      );
                    },
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.science, size: 16),
                    label: const Text('Test Data'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                    onPressed: () => _fetchTestData(),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              // Operating Hours Status
              FutureBuilder<Map<String, dynamic>>(
                future: _fetchOperatingHours(),
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)),
                            const SizedBox(width: 12),
                            Text('Loading operating hours...'),
                          ],
                        ),
                      ),
                    );
                  }
                  
                  final operatingHours = snapshot.data;
                  if (operatingHours == null) {
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            Icon(Icons.error, color: Colors.red),
                            const SizedBox(width: 12),
                            Text('Failed to load operating hours'),
                          ],
                        ),
                      ),
                    );
                  }
                  
                  final isOperating = operatingHours['isOperating'] ?? false;
                  final timeUntilOperating = operatingHours['timeUntilOperatingFormatted'] ?? 'Unknown';
                  final currentTime = operatingHours['currentTime'] ?? '';
                  final operatingHoursText = operatingHours['operatingHours'] ?? '5:00 AM - 9:00 PM';
                  
                  return Card(
                    elevation: 2,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                Icons.access_time,
                                color: isOperating ? Colors.green : Colors.orange,
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
                                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: isOperating ? Colors.green.withOpacity(0.1) : Colors.orange.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: isOperating ? Colors.green : Colors.orange,
                                    width: 1,
                                  ),
                                ),
                                child: Text(
                                  isOperating ? 'ACTIVE' : 'PAUSED',
                                  style: TextStyle(
                                    color: isOperating ? Colors.green : Colors.orange,
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
                                      style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Current: ${DateTime.parse(currentTime).toLocal().toString().substring(11, 16)}',
                                      style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                                    ),
                                  ],
                                ),
                              ),
                              if (!isOperating) ...[
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.end,
                                  children: [
                                    Text(
                                      'Resumes in:',
                                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                                    ),
                                    Text(
                                      timeUntilOperating,
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: Colors.orange,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 18),
              // Chaos/Warp Status
              Consumer<ChaosWarpProvider>(
                builder: (context, chaosWarpProvider, child) {
                  if (chaosWarpProvider.chaosMode || chaosWarpProvider.warpMode) {
                    return Card(
                      elevation: 3,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  chaosWarpProvider.chaosMode ? Icons.warning : Icons.block,
                                  color: chaosWarpProvider.chaosMode ? Colors.purple : Colors.red,
                                  size: 24,
                                ),
                                const SizedBox(width: 12),
                                Text(
                                  chaosWarpProvider.chaosMode ? 'CHAOS MODE' : 'WARP MODE',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 18,
                                    color: chaosWarpProvider.chaosMode ? Colors.purple : Colors.red,
                                  ),
                                ),
                                const Spacer(),
                                Container(
                                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: chaosWarpProvider.chaosMode 
                                        ? Colors.purple.withOpacity(0.1) 
                                        : Colors.red.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(
                                      color: chaosWarpProvider.chaosMode ? Colors.purple : Colors.red,
                                      width: 1,
                                    ),
                                  ),
                                  child: Text(
                                    'ACTIVE',
                                    style: TextStyle(
                                      color: chaosWarpProvider.chaosMode ? Colors.purple : Colors.red,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            if (chaosWarpProvider.chaosMode) ...[
                              Text(
                                'AI operations running outside normal hours',
                                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Remaining time: ${chaosWarpProvider.chaosRemainingTimeFormatted}',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.purple,
                                ),
                              ),
                            ] else if (chaosWarpProvider.warpMode) ...[
                              Text(
                                'All AI operations completely stopped',
                                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Only Chaos mode can restart operations',
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.red,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    );
                  }
                  return SizedBox.shrink();
                },
              ),
              const SizedBox(height: 18),
              ...aiTypes.map((aiType) {
                final data = learningProvider.getLearningDataForAI(aiType);
                final metrics = learningProvider.getLearningMetricsForAI(aiType);
                final isLearning = learningProvider.aiLearningStatus[aiType]?['isLearning'] == true;
                
                // Debug: Print data to console
                print('[AI_LEARNING_DASHBOARD] $aiType data: $data');
                print('[AI_LEARNING_DASHBOARD] $aiType metrics: $metrics');
                print('[AI_LEARNING_DASHBOARD] $aiType isLearning: $isLearning');
                
                final proposals = (data['userFeedback'] as List?)?.length ?? 0;
                final tests = (data['backendTestResults'] as List?)?.length ?? 0;
                final lessons = (data['lessons'] as List?)?.length ?? 0;
                final score = metrics['learningScore'] ?? 0;
                final successRate = metrics['successRate'] ?? 0;
                final appliedLearning = metrics['appliedLearning'] ?? 0;
                final backendTestSuccessRate = metrics['backendTestSuccessRate'] ?? 0;
                
                // Debug: Print calculated values
                print('[AI_LEARNING_DASHBOARD] $aiType calculated values: proposals=$proposals, tests=$tests, lessons=$lessons, score=$score, successRate=$successRate');
                
                return Card(
                  elevation: 3,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(_getAIIcon(aiType), color: _getAIColor(aiType), size: 28),
                            const SizedBox(width: 12),
                            Text(
                              aiType,
                              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: _getAIColor(aiType),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Chip(
                              avatar: Icon(
                                isLearning ? Icons.pause_circle : Icons.play_circle,
                                color: isLearning ? Colors.orange : Colors.green,
                                size: 18,
                              ),
                              label: Text(
                                isLearning ? 'Learning...' : 'Active',
                                style: TextStyle(fontSize: 12),
                              ),
                              backgroundColor: isLearning ? Colors.orange.withOpacity(0.1) : Colors.green.withOpacity(0.1),
                            ),
                            const Spacer(),
                            // Quota Status
                            Consumer<AILearningProvider>(
                              builder: (context, provider, child) {
                                final quotaData = provider.quotaStatus[aiType];
                                if (quotaData == null) return SizedBox.shrink();
                                
                                final currentPhase = quotaData['currentPhase'] ?? 'unknown';
                                final cycleActive = quotaData['cycleActive'] ?? false;
                                final phaseProgress = quotaData['phaseProgress'] ?? {};
                                final phaseQuotas = quotaData['phaseQuotas'] ?? {};
                                final isOperating = quotaData['isOperating'] ?? false;
                                
                                return Row(
                                  children: [
                                    Container(
                                      padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: cycleActive ? Colors.blue.withOpacity(0.1) : Colors.grey.withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(
                                          color: cycleActive ? Colors.blue : Colors.grey,
                                          width: 1,
                                        ),
                                      ),
                                      child: Text(
                                        currentPhase.toUpperCase(),
                                        style: TextStyle(
                                          color: cycleActive ? Colors.blue : Colors.grey,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 10,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    if (cycleActive && isOperating) ...[
                                      Text(
                                        '${phaseProgress[currentPhase] ?? 0}/${phaseQuotas[currentPhase] ?? 0}',
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.grey[700],
                                        ),
                                      ),
                                    ] else if (!isOperating) ...[
                                      Icon(Icons.access_time, size: 16, color: Colors.orange),
                                    ],
                                  ],
                                );
                              },
                            ),
                            ElevatedButton.icon(
                              icon: const Icon(Icons.play_arrow, size: 16),
                              label: const Text('Trigger'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                              ),
                              onPressed: () => _triggerAI(aiType),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        if (isLearning)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 8.0),
                            child: Row(
                              children: [
                                Icon(Icons.pause_circle, color: Colors.orange, size: 20),
                                const SizedBox(width: 8),
                                Text(
                                  'Learning in progress. Actions are paused.',
                                  style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold),
                                ),
                                const Spacer(),
                                ElevatedButton.icon(
                                  icon: const Icon(Icons.refresh, size: 16),
                                  label: const Text('Reset Learning'),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.red,
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                  ),
                                  onPressed: () => _resetLearningState(aiType),
                                ),
                              ],
                            ),
                          ),
                        Wrap(
                          spacing: 16,
                          runSpacing: 12,
                          children: [
                            _buildInfoChip(Icons.psychology, 'Lessons', lessons, Colors.deepPurple),
                            _buildInfoChip(Icons.assignment, 'Proposals', proposals, Colors.green),
                            _buildInfoChip(Icons.science, 'Tests', tests, Colors.orange),
                            _buildInfoChip(Icons.trending_up, 'Score', score, Colors.cyan),
                            _buildInfoChip(Icons.check_circle, 'Success Rate', '$successRate%', Colors.blue),
                            _buildInfoChip(Icons.school, 'Applied Learning', '$appliedLearning%', Colors.purple),
                            _buildInfoChip(Icons.cloud_done, 'Backend Test Success', '$backendTestSuccessRate%', Colors.teal),
                          ],
                        ),
                        const SizedBox(height: 16),
                        if ((data['lessons'] as List?)?.isNotEmpty ?? false) ...[
                          Text('Recent Lessons:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          ...List.generate(
                            (data['lessons'] as List).length > 3 ? 3 : (data['lessons'] as List).length,
                            (i) => Text('• ${(data['lessons'] as List)[i]['lesson']}', style: TextStyle(color: Colors.grey[800])),
                          ),
                        ],
                        if ((data['backendTestResults'] as List?)?.isNotEmpty ?? false) ...[
                          const SizedBox(height: 12),
                          Text('Recent Test Results:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          ...List.generate(
                            (data['backendTestResults'] as List).length > 3 ? 3 : (data['backendTestResults'] as List).length,
                            (i) {
                              final test = (data['backendTestResults'] as List)[i];
                              return Text('• ${test['testType']}: ${test['result']}', style: TextStyle(color: test['result'] == 'pass' ? Colors.green : Colors.red));
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
                                Text('Debug Data for $aiType:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                Text('Data keys: ${data.keys.toList()}', style: TextStyle(fontSize: 10)),
                                Text('Metrics keys: ${metrics.keys.toList()}', style: TextStyle(fontSize: 10)),
                                Text('Learning status: ${learningProvider.aiLearningStatus[aiType]}', style: TextStyle(fontSize: 10)),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              }),
              const SizedBox(height: 18),
              
              // Debug Log Section
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.bug_report, color: Colors.orange, size: 24),
                          const SizedBox(width: 8),
                          Text(
                            'Debug Log & Learning Events',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
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
                              final debugEntries = provider.getRecentDebugEntries();
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
                                  final message = entry['message']?.toString() ?? '';
                                  final timestamp = entry['timestamp']?.toString() ?? '';
                                  
                                  // Color code based on message content
                                  Color textColor = Colors.white;
                                  if (message.contains('ERROR') || message.contains('❌')) {
                                    textColor = Colors.red;
                                  } else if (message.contains('WARNING') || message.contains('⚠️')) {
                                    textColor = Colors.orange;
                                  } else if (message.contains('SUCCESS') || message.contains('✅')) {
                                    textColor = Colors.green;
                                  } else if (message.contains('LEARNING') || message.contains('🧠')) {
                                    textColor = Colors.blue;
                                  }
                                  
                                  return Padding(
                                    padding: const EdgeInsets.symmetric(vertical: 2),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          timestamp.length > 19 ? timestamp.substring(11, 19) : timestamp,
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
              
              // Learning Effectiveness Section
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.analytics, color: Colors.blue, size: 24),
                          const SizedBox(width: 8),
                          Text(
                            'Learning Effectiveness',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.blue,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      FutureBuilder<Map<String, dynamic>>(
                        future: _fetchLearningEffectiveness(),
                        builder: (context, snapshot) {
                          if (snapshot.connectionState == ConnectionState.waiting) {
                            return const Center(child: CircularProgressIndicator());
                          }
                          
                          if (snapshot.hasError || !snapshot.hasData) {
                            return Text(
                              'Error loading effectiveness data',
                              style: TextStyle(color: Colors.red),
                            );
                          }
                          
                          final effectiveness = snapshot.data!;
                          final overall = effectiveness['overall'] ?? {};
                          final byAI = effectiveness['byAI'] ?? {};
                          
                          return Column(
                            children: [
                              // Overall metrics
                              Row(
                                children: [
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Overall Completion Rate',
                                      '${overall['completionRate'] ?? 0}%',
                                      Colors.green,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Average Improvement',
                                      '${overall['averageImprovement'] ?? 0}%',
                                      Colors.blue,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: _buildMetricCard(
                                      'Total Sessions',
                                      '${overall['totalLearningSessions'] ?? 0}',
                                      Colors.purple,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              
                              // Per-AI breakdown
                              ...aiTypes.map((aiType) {
                                final aiData = byAI[aiType] ?? {};
                                return Padding(
                                  padding: const EdgeInsets.only(bottom: 12),
                                  child: Row(
                                    children: [
                                      Expanded(
                                        flex: 2,
                                        child: Text(
                                          aiType,
                                          style: TextStyle(fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                      Expanded(
                                        child: Text('${aiData['completionRate'] ?? 0}%'),
                                      ),
                                      Expanded(
                                        child: Text('${aiData['averageDuration'] ?? 0}h'),
                                      ),
                                      Expanded(
                                        child: Text('${aiData['successImprovement'] ?? 0}%'),
                                      ),
                                      Expanded(
                                        child: Text('${aiData['learningSessions'] ?? 0}'),
                                      ),
                                    ],
                                  ),
                                );
                              }).toList(),
                              
                              // Header for per-AI table
                              Padding(
                                padding: const EdgeInsets.only(bottom: 8),
                                child: Row(
                                  children: [
                                    Expanded(flex: 2, child: Text('AI', style: TextStyle(fontWeight: FontWeight.bold))),
                                    Expanded(child: Text('Completion', style: TextStyle(fontWeight: FontWeight.bold))),
                                    Expanded(child: Text('Duration', style: TextStyle(fontWeight: FontWeight.bold))),
                                    Expanded(child: Text('Improvement', style: TextStyle(fontWeight: FontWeight.bold))),
                                    Expanded(child: Text('Sessions', style: TextStyle(fontWeight: FontWeight.bold))),
                                  ],
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 18),
            ],
          ),
        );
      },
    );
  }

  Widget _buildInfoChip(IconData icon, String label, dynamic value, Color color) {
    return Chip(
      avatar: Icon(icon, color: color, size: 18),
      label: Text('$value $label', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
      backgroundColor: color.withOpacity(0.08),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    );
  }

  IconData _getAIIcon(String aiType) {
    switch (aiType) {
      case 'Imperium':
        return Icons.auto_awesome;
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
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: color.withOpacity(0.8),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Future<Map<String, dynamic>> _fetchLearningEffectiveness() async {
    try {
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/learning/effectiveness'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['effectiveness'] ?? {};
      }
    } catch (e) {
      print('[AI_LEARNING_DASHBOARD] Error fetching effectiveness: $e');
    }
    return {};
  }

  Future<void> _triggerAI(String aiType) async {
    try {
      final response = await http.post(
        Uri.parse('${ProposalProvider.backendUrl}/api/ai/$aiType/trigger'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({}),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('${data['message']} - ${aiType} isLearning: ${data['isLearning']}'),
              backgroundColor: data['isLearning'] ? Colors.orange : Colors.green,
            ),
          );
        }
      } else {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to trigger $aiType: ${response.statusCode}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error triggering $aiType: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
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
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/health'));
      return response.statusCode == 200;
    } catch (e) {
      print('[AI_LEARNING_DASHBOARD] Error checking backend connection: $e');
      return false;
    }
  }

  Future<void> _fetchTestData() async {
    try {
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/learning/test'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('[AI_LEARNING_DASHBOARD] Test data received: ${data.keys.toList()}');
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Test data fetched successfully: ${data.keys.length} AIs'),
              backgroundColor: Colors.green,
            ),
          );
        }
      } else {
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to fetch test data: ${response.statusCode}'),
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
      final response = await http.get(Uri.parse('${ProposalProvider.backendUrl}/api/proposals/operating-hours'));
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
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final learningProvider = Provider.of<AILearningProvider>(context, listen: false);
      learningProvider.fetchAIStatus();
      learningProvider.fetchLearningData();
      learningProvider.fetchLearningMetrics();
      learningProvider.fetchDebugLog();
    });
  }

  void _startPolling() {
    // Poll for updates every 5 seconds
    _pollingTimer = Timer.periodic(Duration(seconds: 5), (timer) {
      if (mounted) {
        final learningProvider = Provider.of<AILearningProvider>(context, listen: false);
        learningProvider.fetchAIStatus();
        learningProvider.fetchLearningData();
        learningProvider.fetchLearningMetrics();
        learningProvider.fetchDebugLog();
      }
    });
  }

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }
} 