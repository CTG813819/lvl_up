import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/ai_learning_provider.dart';
import 'models/ai_proposal.dart';

  // Test screen for AI learning functionality
class TestAILearning extends StatefulWidget {
  const TestAILearning({Key? key}) : super(key: key);

  @override
  State<TestAILearning> createState() => _TestAILearningState();
}

class _TestAILearningState extends State<TestAILearning> {
  final TextEditingController _feedbackController = TextEditingController();
  String _selectedAI = 'Imperium';
  String _selectedTestType = 'compilation';

  @override
  void dispose() {
    _feedbackController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🧪 AI Learning Test'),
        backgroundColor: Colors.orange,
      ),
      body: Consumer<AILearningProvider>(
        builder: (context, learningProvider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
  // Test controls
                _buildTestControls(learningProvider),

                const SizedBox(height: 24),

  // Learning summary
                _buildLearningSummary(learningProvider),

                const SizedBox(height: 24),

  // AI performance comparison
                _buildPerformanceComparison(learningProvider),

                const SizedBox(height: 24),

  // Debug output
                _buildDebugOutput(learningProvider),

                const SizedBox(height: 24),

  // Test results
                _buildTestResults(learningProvider),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildTestControls(AILearningProvider learningProvider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🧪 Test Controls',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

  // AI Selection
            DropdownButtonFormField<String>(
              value: _selectedAI,
              decoration: const InputDecoration(
                labelText: 'Select AI',
                border: OutlineInputBorder(),
              ),
              items:
                  ['Imperium', 'Sandbox', 'Guardian'].map((ai) {
                    return DropdownMenuItem(value: ai, child: Text(ai));
                  }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedAI = value!;
                });
              },
            ),

            const SizedBox(height: 16),

  // Test Type Selection
            DropdownButtonFormField<String>(
              value: _selectedTestType,
              decoration: const InputDecoration(
                labelText: 'Test Type',
                border: OutlineInputBorder(),
              ),
              items:
                  [
                    'compilation',
                    'dependency',
                    'null_safety',
                    'performance',
                    'security',
                    'integration',
                  ].map((type) {
                    return DropdownMenuItem(value: type, child: Text(type));
                  }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedTestType = value!;
                });
              },
            ),

            const SizedBox(height: 16),

  // Feedback input
            TextField(
              controller: _feedbackController,
              decoration: const InputDecoration(
                labelText: 'Feedback/Details',
                border: OutlineInputBorder(),
                hintText: 'Enter test details or feedback...',
              ),
              maxLines: 3,
            ),

            const SizedBox(height: 16),

  // Test buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _simulateTestSuccess(learningProvider),
                    icon: const Icon(Icons.check),
                    label: const Text('Test Success'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _simulateTestFailure(learningProvider),
                    icon: const Icon(Icons.close),
                    label: const Text('Test Failure'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

  // Backend test simulation
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        () => _simulateBackendTestSuccess(learningProvider),
                    icon: const Icon(Icons.cloud_done),
                    label: const Text('Backend Success'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        () => _simulateBackendTestFailure(learningProvider),
                    icon: const Icon(Icons.cloud_off),
                    label: const Text('Backend Failure'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

  // Proposal simulation
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        () => _simulateProposalApproval(learningProvider),
                    icon: const Icon(Icons.thumb_up),
                    label: const Text('Approve Proposal'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        () => _simulateProposalRejection(learningProvider),
                    icon: const Icon(Icons.thumb_down),
                    label: const Text('Reject Proposal'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

  // Utility buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => learningProvider.simulateLearning(),
                    icon: const Icon(Icons.auto_awesome),
                    label: const Text('Simulate Learning'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.purple,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => learningProvider.clearLearningData(),
                    icon: const Icon(Icons.clear_all),
                    label: const Text('Clear Data'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLearningSummary(AILearningProvider learningProvider) {
    final summary = learningProvider.getLearningSummary();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '📊 Learning Summary',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            Row(
              children: [
                _buildSummaryItem(
                  'AIs',
                  '${summary['totalAIs']}',
                  Icons.psychology,
                ),
                _buildSummaryItem(
                  'Lessons',
                  '${summary['totalLessons']}',
                  Icons.school,
                ),
                _buildSummaryItem(
                  'Proposals',
                  '${summary['totalProposals']}',
                  Icons.assignment,
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                _buildSummaryItem(
                  'Tests',
                  '${summary['totalBackendTests']}',
                  Icons.science,
                ),
                _buildSummaryItem(
                  'Avg Score',
                  '${summary['averageLearningScore']}%',
                  Icons.trending_up,
                ),
                _buildSummaryItem(
                  'Debug Logs',
                  '${summary['totalDebugEntries']}',
                  Icons.bug_report,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Theme.of(context).primaryColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(icon, color: Theme.of(context).primaryColor),
            const SizedBox(height: 4),
            Text(
              value,
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            Text(label, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }

  Widget _buildPerformanceComparison(AILearningProvider learningProvider) {
    final comparison = learningProvider.getAIPerformanceComparison();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🏆 AI Performance Comparison',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            ...comparison.entries.map((entry) {
              final aiType = entry.key;
              final metrics = entry.value as Map<String, dynamic>;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).scaffoldBackgroundColor,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.withOpacity(0.2)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          aiType,
                          style: Theme.of(context).textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getScoreColor(
                              metrics['learningScore'] as int,
                            ),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '${metrics['learningScore']}%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    _buildMetricRow(
                      'Success Rate',
                      metrics['successRate'] as int,
                    ),
                    _buildMetricRow(
                      'Applied Learning',
                      metrics['appliedLearning'] as int,
                    ),
                    _buildMetricRow(
                      'Test Success',
                      metrics['backendTestSuccessRate'] as int,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Proposals: ${metrics['totalProposals']}'),
                        Text('Tests: ${metrics['backendTests']}'),
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

  Widget _buildMetricRow(String label, int value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(label, style: Theme.of(context).textTheme.bodySmall),
          ),
          Expanded(
            flex: 3,
            child: LinearProgressIndicator(
              value: value / 100,
              backgroundColor: Colors.grey.withOpacity(0.2),
              valueColor: AlwaysStoppedAnimation<Color>(
                value >= 80
                    ? Colors.green
                    : value >= 60
                    ? Colors.orange
                    : value >= 40
                    ? Colors.yellow.shade700
                    : Colors.red,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Text(
            '$value%',
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildDebugOutput(AILearningProvider learningProvider) {
    final debugLogs = learningProvider.debugLogs;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '🐛 Debug Output',
                  style: Theme.of(
                    context,
                  ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                ),
                Text(
                  '${debugLogs.values.fold(0, (sum, logs) => sum + logs.length)} entries',
                ),
              ],
            ),
            const SizedBox(height: 16),

            ...debugLogs.entries.map((entry) {
              final aiType = entry.key;
              final logs = entry.value;

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      aiType,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).primaryColor,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...logs.take(3).map((log) {
                      final timestamp = DateTime.parse(log['timestamp']);
                      final message = log['message'] as String;

                      return Container(
                        margin: const EdgeInsets.only(bottom: 4),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Theme.of(context).scaffoldBackgroundColor,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _formatTimestamp(timestamp),
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(color: Colors.grey[600]),
                            ),
                            Text(
                              message,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTestResults(AILearningProvider learningProvider) {
    final learningData = learningProvider.learningData;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🧪 Test Results',
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            ...learningData.entries.map((entry) {
              final aiType = entry.key;
              final data = entry.value as Map<String, dynamic>;
              final testResults = data['testResults'] as List;
              final backendTests = data['backendTestResults'] as List;

              return Container(
                margin: const EdgeInsets.only(bottom: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      aiType,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),

                    if (testResults.isNotEmpty) ...[
                      Text(
                        'Local Tests (${testResults.length})',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      ...testResults.take(3).map((test) {
                        return _buildTestResultItem(test, 'local');
                      }).toList(),
                      const SizedBox(height: 8),
                    ],

                    if (backendTests.isNotEmpty) ...[
                      Text(
                        'Backend Tests (${backendTests.length})',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                      const SizedBox(height: 4),
                      ...backendTests.take(3).map((test) {
                        return _buildTestResultItem(test, 'backend');
                      }).toList(),
                    ],
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTestResultItem(Map<String, dynamic> test, String source) {
    final result = test['result'] as String;
    final testType = test['testType'] as String;
    final details = test['details'] as String;
    final timestamp = DateTime.parse(test['timestamp']);

    return Container(
      margin: const EdgeInsets.only(bottom: 4),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color:
            result == 'pass'
                ? Colors.green.withOpacity(0.1)
                : Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: result == 'pass' ? Colors.green : Colors.red,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Icon(
            result == 'pass' ? Icons.check_circle : Icons.error,
            color: result == 'pass' ? Colors.green : Colors.red,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$testType ($source)',
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold),
                ),
                Text(
                  details.length > 50
                      ? '${details.substring(0, 50)}...'
                      : details,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Text(
            _formatTimestamp(timestamp),
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(fontSize: 10),
          ),
        ],
      ),
    );
  }

  // Test simulation methods
  void _simulateTestSuccess(AILearningProvider learningProvider) {
    final details =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Test passed successfully';

    learningProvider.learnFromTestResult(
      _selectedAI,
      _selectedTestType,
      'pass',
      details,
    );
    _showSnackBar('✅ Test success simulated for $_selectedAI');
  }

  void _simulateTestFailure(AILearningProvider learningProvider) {
    final details =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Test failed with errors';

    learningProvider.learnFromTestResult(
      _selectedAI,
      _selectedTestType,
      'fail',
      details,
    );
    _showSnackBar('❌ Test failure simulated for $_selectedAI');
  }

  void _simulateBackendTestSuccess(AILearningProvider learningProvider) {
    final details =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Backend test passed successfully';

    learningProvider.learnFromBackendTestResult(_selectedAI, {
      'testType': _selectedTestType,
      'result': 'pass',
      'details': details,
      'filePath': 'lib/test_file.dart',
      'function': 'testFunction',
    });
    _showSnackBar('☁️ Backend test success simulated for $_selectedAI');
  }

  void _simulateBackendTestFailure(AILearningProvider learningProvider) {
    final details =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Backend test failed with errors';

    learningProvider.learnFromBackendTestResult(_selectedAI, {
      'testType': _selectedTestType,
      'result': 'fail',
      'details': details,
      'filePath': 'lib/test_file.dart',
      'function': 'testFunction',
    });
    _showSnackBar('☁️ Backend test failure simulated for $_selectedAI');
  }

  void _simulateProposalApproval(AILearningProvider learningProvider) {
    final feedback =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Good proposal, approved!';

  // Create a mock proposal
    final proposal = AIProposal(
      id: 'test_${DateTime.now().millisecondsSinceEpoch}',
      aiType: _selectedAI,
      filePath: 'lib/test_file.dart',
      oldCode: '/ old code',
      newCode: '/ new code',
      timestamp: DateTime.now(),
      status: ProposalStatus.pending,
    );

    learningProvider.learnFromProposal(proposal, 'approved', feedback);
    _showSnackBar('👍 Proposal approval simulated for $_selectedAI');
  }

  void _simulateProposalRejection(AILearningProvider learningProvider) {
    final feedback =
        _feedbackController.text.isNotEmpty
            ? _feedbackController.text
            : 'Proposal rejected due to issues';

  // Create a mock proposal
    final proposal = AIProposal(
      id: 'test_${DateTime.now().millisecondsSinceEpoch}',
      aiType: _selectedAI,
      filePath: 'lib/test_file.dart',
      oldCode: '/ old code',
      newCode: '/ new code',
      timestamp: DateTime.now(),
      status: ProposalStatus.pending,
    );

    learningProvider.learnFromProposal(proposal, 'rejected', feedback);
    _showSnackBar('👎 Proposal rejection simulated for $_selectedAI');
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), duration: const Duration(seconds: 2)),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    if (score >= 40) return Colors.yellow.shade700;
    return Colors.red;
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }
}
