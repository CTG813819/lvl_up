import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/ai_brain.dart';
import 'mission.dart' show MissionProvider;
import 'providers/ai_growth_analytics_provider.dart';
import 'widgets/ai_growth_analytics_dashboard.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/flutter_svg.dart';

class MechanicumAnalyticsScreen extends StatefulWidget {
  const MechanicumAnalyticsScreen({super.key});

  @override
  State<MechanicumAnalyticsScreen> createState() =>
      _MechanicumAnalyticsScreenState();
}

class _MechanicumAnalyticsScreenState extends State<MechanicumAnalyticsScreen> {
  final _subjectController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _codeController = TextEditingController();
  final _tagsController = TextEditingController();
  final _searchController = TextEditingController();
  String _searchQuery = '';
  String _uploadType = 'app_improvement';

  get mermaid => null;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      if (mounted) {
        setState(() {
          _searchQuery = _searchController.text;
        });
      }
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        _loadAnalytics();
      }
    });
  }

  @override
  void dispose() {
    _subjectController.dispose();
    _descriptionController.dispose();
    _codeController.dispose();
    _tagsController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadAnalytics() async {
    try {
      final provider = Provider.of<MissionProvider>(context, listen: false);
      if (provider == null) {
        print('MissionProvider is null in _loadAnalytics');
        return;
      }
      // Analytics loaded successfully
    } catch (e) {
      print('Error loading analytics: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MissionProvider>(
      builder: (context, provider, child) {
        final aiSuggestions = provider.aiSuggestions;
        final lastTested = provider.lastAISuggestionTime;
        final sandboxFeed = provider.sandboxTestFeed;
        final isSandboxWorking = provider.isSandboxWorking;
        return Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            title: const Text(
              'Terra',
              style: TextStyle(color: Colors.white),
            ),
            backgroundColor: Colors.black,
            elevation: 4,
            centerTitle: true,
            shadowColor: Colors.cyan.withValues(alpha: 0.2),
            iconTheme: const IconThemeData(color: Colors.white),
            foregroundColor: Colors.white,
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (lastTested != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(
                      'Last tested: ${lastTested.toLocal().toString().substring(0, 19)}',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ),
                Card(
                  color: Colors.grey[900],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: 12,
                      horizontal: 10,
                    ),
                    child:
                        (aiSuggestions.isEmpty)
                            ? const Text(
                              'No suggestions at this time. The AI is learning and testing in the background.',
                              style: TextStyle(color: Colors.white70),
                            )
                            : SingleChildScrollView(
                              scrollDirection: Axis.horizontal,
                              child: Row(
                                children: [
                                  ...aiSuggestions.map<Widget>((s) {
                                    final accepted = s['accepted'] == true;
                                    final ignored = s['ignored'] == true;
                                    Color? borderColor;
                                    if (accepted) {
                                      borderColor = Colors.greenAccent;
                                    } else if (ignored) {
                                      borderColor = Colors.redAccent;
                                    } else {
                                      borderColor = Colors.amber;
                                    }
                                    return Container(
                                      width: 320,
                                      margin: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 8,
                                      ),
                                      decoration: BoxDecoration(
                                        border: Border(
                                          left: BorderSide(
                                            color: borderColor,
                                            width: 5,
                                          ),
                                        ),
                                        borderRadius: BorderRadius.circular(12),
                                        color: Colors.grey[850],
                                      ),
                                      child: ListTile(
                                        contentPadding:
                                            const EdgeInsets.symmetric(
                                              vertical: 8,
                                              horizontal: 12,
                                            ),
                                        leading: Icon(
                                          accepted
                                              ? Icons.check_circle
                                              : ignored
                                              ? Icons.cancel
                                              : Icons.lightbulb,
                                          color: borderColor,
                                          size: 32,
                                        ),
                                        title: Text(
                                          s['issue'] ?? 'Unknown',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 16,
                                          ),
                                        ),
                                        subtitle: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            if (s['explanation'] != null &&
                                                s['explanation']
                                                    .toString()
                                                    .isNotEmpty)
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                  bottom: 2,
                                                ),
                                                child: Text(
                                                  s['explanation'],
                                                  style: const TextStyle(
                                                    color: Colors.white70,
                                                  ),
                                                ),
                                              ),
                                            if (s['changes'] != null &&
                                                ((s['changes'] as List?)
                                                        ?.isNotEmpty ??
                                                    false))
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                ),
                                                child: Wrap(
                                                  spacing: 6,
                                                  runSpacing: 2,
                                                  children:
                                                      (s['changes'] as List?)
                                                          ?.map<Widget>(
                                                            (c) => Chip(
                                                              label: Text(
                                                                c,
                                                                style: const TextStyle(
                                                                  color:
                                                                      Colors
                                                                          .white70,
                                                                ),
                                                              ),
                                                              backgroundColor:
                                                                  Colors
                                                                      .grey[800],
                                                            ),
                                                          )
                                                          .toList() ??
                                                      [],
                                                ),
                                              ),
                                            if (s['testResults'] != null &&
                                                ((s['testResults'] as List?)
                                                        ?.isNotEmpty ??
                                                    false))
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                ),
                                                child: Wrap(
                                                  spacing: 6,
                                                  runSpacing: 2,
                                                  children:
                                                      (s['testResults']
                                                              as List?)
                                                          ?.map<Widget>(
                                                            (t) => Chip(
                                                              label: Text(
                                                                t,
                                                                style: const TextStyle(
                                                                  color:
                                                                      Colors
                                                                          .white70,
                                                                ),
                                                              ),
                                                              backgroundColor:
                                                                  Colors
                                                                      .blueGrey[800],
                                                            ),
                                                          )
                                                          .toList() ??
                                                      [],
                                                ),
                                              ),
                                            if (accepted &&
                                                s['acceptedAt'] != null)
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                ),
                                                child: Text(
                                                  'Accepted at: \\${s['acceptedAt']}',
                                                  style: const TextStyle(
                                                    color: Colors.greenAccent,
                                                    fontSize: 12,
                                                  ),
                                                ),
                                              ),
                                            if (ignored &&
                                                s['ignoredAt'] != null)
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                ),
                                                child: Text(
                                                  'Ignored at: \\${s['ignoredAt']}',
                                                  style: const TextStyle(
                                                    color: Colors.redAccent,
                                                    fontSize: 12,
                                                  ),
                                                ),
                                              ),
                                          ],
                                        ),
                                      ),
                                    );
                                  }).toList(),
                                ],
                              ),
                            ),
                  ),
                ),
                const SizedBox(height: 18),
                _SectionHeader('Test Coverage', icon: Icons.analytics),
                Card(
                  color: Colors.grey[900],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: 16,
                      horizontal: 12,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ...provider.testCoverage.entries.map(
                          (entry) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text(
                              '${entry.key}: ${entry.value} tests',
                              style: const TextStyle(
                                color: Colors.lightGreenAccent,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                _SectionHeader('AI Sandbox Test Feed', icon: Icons.science),
                Card(
                  color: Colors.grey[900],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: 16,
                      horizontal: 12,
                    ),
                    child:
                        ((sandboxFeed.isEmpty))
                            ? const Text(
                              'No tests run yet. The AI is preparing...',
                              style: TextStyle(color: Colors.white70),
                            )
                            : Container(
                              height: 300,
                              child: ListView(
                                children:
                                    sandboxFeed
                                        .take(10)
                                        .map<Widget>(
                                          (test) => Card(
                                            color:
                                                test['result'] == 'pass'
                                                    ? Colors.green[900]
                                                    : Colors.red[900],
                                            shape: RoundedRectangleBorder(
                                              borderRadius:
                                                  BorderRadius.circular(10),
                                            ),
                                            margin: const EdgeInsets.symmetric(
                                              vertical: 6,
                                            ),
                                            child: ListTile(
                                              leading: Icon(
                                                test['result'] == 'pass'
                                                    ? Icons.check_circle
                                                    : Icons.cancel,
                                                color:
                                                    test['result'] == 'pass'
                                                        ? Colors.greenAccent
                                                        : Colors.redAccent,
                                              ),
                                              title: Text(
                                                '${test['testType']} test on ${test['function'] ?? 'code'}',
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                ),
                                              ),
                                              subtitle: Column(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  Text(
                                                    '${test['details']}',
                                                    style: const TextStyle(
                                                      color: Colors.white70,
                                                    ),
                                                  ),
                                                  if (test['reasoning'] != null)
                                                    Padding(
                                                      padding:
                                                          const EdgeInsets.only(
                                                            top: 4,
                                                          ),
                                                      child: Text(
                                                        'Reasoning: ${test['reasoning']}',
                                                        style: const TextStyle(
                                                          color:
                                                              Colors
                                                                  .amberAccent,
                                                          fontSize: 12,
                                                        ),
                                                      ),
                                                    ),
                                                ],
                                              ),
                                              trailing: Text(
                                                test['result']?.toUpperCase() ??
                                                    '',
                                                style: TextStyle(
                                                  color:
                                                      test['result'] == 'pass'
                                                          ? Colors.greenAccent
                                                          : Colors.redAccent,
                                                ),
                                              ),
                                            ),
                                          ),
                                        )
                                        .toList(),
                              ),
                            ),
                  ),
                ),
                const SizedBox(height: 18),
                _SectionHeader('The Imperium', icon: Icons.cyclone),
                Card(
                  color: Colors.grey[900],
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 20),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(
                      vertical: 16,
                      horizontal: 12,
                    ),
                    child: Builder(
                      builder: (context) {
                        final metaLog = TheImperium.instance.metaLearningLog;
                        if (metaLog.isEmpty) {
                          return const Text(
                            'No meta-AI activity yet.',
                            style: TextStyle(color: Colors.amberAccent),
                          );
                        }
                        final proposalCount =
                            metaLog
                                .where(
                                  (e) =>
                                      e['suggestion'] != null &&
                                      e['suggestion'].toString().isNotEmpty,
                                )
                                .length;
                        final appliedCount =
                            metaLog
                                .where(
                                  (e) => (e['insight'] ?? '').contains(
                                    'Applied proposal',
                                  ),
                                )
                                .length;
                        final issueCounts = <String, int>{};
                        for (final entry in metaLog) {
                          final event = entry['event'] as Map<String, dynamic>?;
                          final action = event?['action']?.toString() ?? '';
                          if (action.isNotEmpty) {
                            issueCounts[action] =
                                (issueCounts[action] ?? 0) + 1;
                          }
                        }
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  'Proposals: $proposalCount',
                                  style: const TextStyle(
                                    color: Colors.amberAccent,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Text(
                                  'Applied: $appliedCount',
                                  style: const TextStyle(
                                    color: Colors.greenAccent,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Text(
                                  'Unique Issues: ${issueCounts.length}',
                                  style: const TextStyle(
                                    color: Colors.orangeAccent,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            ...metaLog.map<Widget>((entry) {
                              final ts = entry['timestamp'] ?? '';
                              final insight = entry['insight'] ?? '';
                              final suggestion = entry['suggestion'] ?? '';
                              final code = entry['code'] ?? '';
                              return Card(
                                color: Colors.black,
                                child: Padding(
                                  padding: const EdgeInsets.all(8),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        ts,
                                        style: const TextStyle(
                                          color: Colors.amberAccent,
                                          fontSize: 10,
                                        ),
                                      ),
                                      Text(
                                        insight,
                                        style: const TextStyle(
                                          color: Colors.amberAccent,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      if (suggestion.isNotEmpty)
                                        Padding(
                                          padding: const EdgeInsets.only(
                                            top: 4,
                                          ),
                                          child: Text(
                                            'Proposal: $suggestion',
                                            style: const TextStyle(
                                              color: Colors.orangeAccent,
                                            ),
                                          ),
                                        ),
                                      if (code.isNotEmpty)
                                        Padding(
                                          padding: const EdgeInsets.only(
                                            top: 4,
                                          ),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              const Text(
                                                'Proposed Code:',
                                                style: TextStyle(
                                                  color: Colors.orangeAccent,
                                                ),
                                              ),
                                              Container(
                                                width: double.infinity,
                                                margin: const EdgeInsets.only(
                                                  top: 2,
                                                ),
                                                padding: const EdgeInsets.all(
                                                  8,
                                                ),
                                                decoration: BoxDecoration(
                                                  color: Colors.grey[850],
                                                  borderRadius:
                                                      BorderRadius.circular(8),
                                                ),
                                                child: SelectableText(
                                                  code,
                                                  style: const TextStyle(
                                                    color: Colors.white,
                                                    fontFamily: 'monospace',
                                                  ),
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              ElevatedButton.icon(
                                                icon: const Icon(
                                                  Icons.check,
                                                  color: Colors.amberAccent,
                                                ),
                                                label: const Text(
                                                  'Approve & Apply',
                                                  style: TextStyle(
                                                    color: Colors.amberAccent,
                                                  ),
                                                ),
                                                style: ElevatedButton.styleFrom(
                                                  backgroundColor: Colors.black,
                                                  foregroundColor:
                                                      Colors.amberAccent,
                                                ),
                                                onPressed: () async {
                                                  await TheImperium.instance
                                                      .applyProposal(entry);
                                                  ScaffoldMessenger.of(
                                                    context,
                                                  ).showSnackBar(
                                                    const SnackBar(
                                                      content: Text(
                                                        'Proposal applied!',
                                                      ),
                                                      backgroundColor:
                                                          Colors.amber,
                                                    ),
                                                  );
                                                },
                                              ),
                                            ],
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              );
                            }),
                          ],
                        );
                      },
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _generateMermaidGraph(Map<String, List<String>> graph) {
    final buffer = StringBuffer('graph TD;\n');
    graph.forEach((node, deps) {
      if (deps.isEmpty) {
        buffer.writeln('  "$node";');
      } else {
        for (final dep in deps) {
          buffer.writeln('  "$node"-->"$dep";');
        }
      }
    });
    return buffer.toString();
  }

  Widget _buildFeedbackAnalytics(MissionProvider provider) {
    final sandboxFeed = provider.sandboxTestFeed;
    int pass = 0, fail = 0;
    int accepted = 0, ignored = 0;
    for (final test in sandboxFeed) {
      if (test['result'] == 'pass') pass++;
      if (test['result'] == 'fail') fail++;
      if (test['accepted'] == true) accepted++;
      if (test['ignored'] == true) ignored++;
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Test pass rate: ${pass + fail == 0 ? 'N/A' : ((pass / (pass + fail) * 100).toStringAsFixed(1)) + '%'}',
          style: const TextStyle(color: Colors.orangeAccent),
        ),
        Text(
          'Suggestions accepted: $accepted',
          style: const TextStyle(color: Colors.greenAccent),
        ),
        Text(
          'Suggestions ignored: $ignored',
          style: const TextStyle(color: Colors.redAccent),
        ),
        if (provider.testCoverage.isNotEmpty)
          Text(
            'Least tested: ${_leastTested(provider.testCoverage)}',
            style: const TextStyle(color: Colors.yellowAccent),
          ),
      ],
    );
  }

  String _leastTested(Map<String, int> coverage) {
    if (coverage.isEmpty) return 'N/A';
    final sorted =
        coverage.entries.toList()..sort((a, b) => a.value.compareTo(b.value));
    return '${sorted.first.key} (${sorted.first.value} tests)';
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData? icon;
  const _SectionHeader(this.title, {this.icon});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 8),
      child: Row(
        children: [
          if (icon != null) ...[
            Icon(icon, color: Colors.cyanAccent, size: 24),
            const SizedBox(width: 8),
          ],
          Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 20,
            ),
          ),
        ],
      ),
    );
  }
}

class _ExtensionIdeaForm extends StatefulWidget {
  @override
  State<_ExtensionIdeaForm> createState() => _ExtensionIdeaFormState();
}

class _ExtensionIdeaFormState extends State<_ExtensionIdeaForm> {
  final _featureController = TextEditingController();
  final _rationaleController = TextEditingController();
  bool _submitting = false;

  @override
  void dispose() {
    _featureController.dispose();
    _rationaleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: _featureController,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            labelText: 'Feature Name',
            labelStyle: TextStyle(color: Colors.white70),
            filled: true,
            fillColor: Colors.black,
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _rationaleController,
          style: const TextStyle(color: Colors.white),
          decoration: const InputDecoration(
            labelText: 'Why is this useful?',
            labelStyle: TextStyle(color: Colors.white70),
            filled: true,
            fillColor: Colors.black,
            border: OutlineInputBorder(),
          ),
          maxLines: 2,
        ),
        const SizedBox(height: 8),
        ElevatedButton.icon(
          icon: const Icon(Icons.send),
          label:
              _submitting
                  ? const Text('Submitting...')
                  : const Text('Suggest Extension'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.cyan,
            foregroundColor: Colors.white,
          ),
          onPressed:
              _submitting
                  ? null
                  : () async {
                    if (_featureController.text.trim().isEmpty) return;
                    setState(() => _submitting = true);
                    Provider.of<MissionProvider>(
                      context,
                      listen: false,
                    ).suggestExtensionIdea(
                      _featureController.text.trim(),
                      _rationaleController.text.trim(),
                    );
                    setState(() => _submitting = false);
                    _featureController.clear();
                    _rationaleController.clear();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Extension idea submitted!'),
                      ),
                    );
                  },
        ),
      ],
    );
  }
}

class _AIBrainExperimentList extends StatefulWidget {
  @override
  State<_AIBrainExperimentList> createState() => _AIBrainExperimentListState();
}

class _AIBrainExperimentListState extends State<_AIBrainExperimentList> {
  String? _selectedDate;
  Map<String, List<Map<String, dynamic>>> _grouped = {};
  List<String> _sortedKeys = [];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _groupAndSort();
  }

  void _groupAndSort() {
    final provider = Provider.of<MissionProvider>(context, listen: false);
    final experiments = provider.aiExperiments;
    final Map<String, List<Map<String, dynamic>>> grouped = {};
    for (final exp in experiments) {
      final dt = exp['timestamp'];
      String key;
      if (dt is DateTime) {
        key =
            '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
      } else if (dt is String) {
        final parsed = DateTime.tryParse(dt);
        if (parsed != null) {
          key =
              '${parsed.year}-${parsed.month.toString().padLeft(2, '0')}-${parsed.day.toString().padLeft(2, '0')}';
        } else {
          key = 'Unknown Date';
        }
      } else {
        key = 'Unknown Date';
      }
      grouped.putIfAbsent(key, () => []).add(exp);
    }
    final sortedKeys =
        grouped.keys.toList()
          ..sort((a, b) => b.compareTo(a)); // Most recent first
    setState(() {
      _grouped = grouped;
      _sortedKeys = sortedKeys;
      _selectedDate ??= sortedKeys.isNotEmpty ? sortedKeys.first : null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<MissionProvider>(context, listen: false);
    final experiments = provider.aiExperiments;
    final learningLog = provider.aiLearningLog;
    final fileInsights = provider.fileInsights;

    if (experiments.isEmpty) {
      return const Text(
        'AI is currently reflecting and preparing new experiments...',
        style: TextStyle(color: Colors.white70),
      );
    }

    // Group by month for dropdown
    final Map<String, List<String>> monthToDates = {};
    for (final date in _sortedKeys) {
      if (date == 'Unknown Date') continue;
      final parts = date.split('-');
      if (parts.length < 2) continue;
      final monthKey = '${parts[0]}-${parts[1]}';
      monthToDates.putIfAbsent(monthKey, () => []).add(date);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Learning Insights
        if (learningLog.isNotEmpty) ...[
          const Padding(
            padding: EdgeInsets.only(bottom: 8),
            child: Text(
              '🧠 AI Learning from Test Results',
              style: TextStyle(
                color: Colors.amberAccent,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ),
          Container(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: learningLog.length,
              itemBuilder: (context, index) {
                final entry =
                    learningLog[learningLog.length -
                        1 -
                        index]; // Most recent first
                final testResults =
                    entry['testResults'] as List<Map<String, dynamic>>? ?? [];
                final learnings = entry['learnings'] as List<String>? ?? [];

                // Extract test-based learnings
                String learningText = 'No test results available';
                if (testResults.isNotEmpty) {
                  final lastTest = testResults.last;
                  final result = lastTest['result'] ?? 'unknown';
                  final testType = lastTest['testType'] ?? 'test';
                  final details = lastTest['details'] ?? '';

                  if (result == 'pass') {
                    learningText = '✅ $testType passed: $details';
                  } else if (result == 'fail') {
                    learningText = '❌ $testType failed: $details';
                  } else {
                    learningText = '⚠️ $testType: $details';
                  }
                } else if (learnings.isNotEmpty) {
                  learningText = learnings.first;
                }

                return Container(
                  width: 250,
                  margin: const EdgeInsets.only(right: 8),
                  child: Card(
                    color: Colors.deepPurple[700],
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${entry['totalElements']} elements tested',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Expanded(
                            child: Text(
                              learningText,
                              style: const TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                              overflow: TextOverflow.ellipsis,
                              maxLines: 3,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),
        ],

        // File Insights
        if (fileInsights.isNotEmpty) ...[
          const Padding(
            padding: EdgeInsets.only(bottom: 8),
            child: Text(
              '🔍 Code Pattern Analysis',
              style: TextStyle(
                color: Colors.greenAccent,
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ),
          Container(
            height: 80,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: fileInsights.length,
              itemBuilder: (context, index) {
                final entry = fileInsights.entries.elementAt(index);
                final filePath = entry.key;
                final insights = entry.value;

                if (insights.isEmpty) return const SizedBox.shrink();

                final latestInsight = insights.last;
                final patterns =
                    latestInsight['patterns'] as List<String>? ?? [];
                final functions =
                    latestInsight['functions'] as List<String>? ?? [];
                final classes = latestInsight['classes'] as List<String>? ?? [];

                return Container(
                  width: 220,
                  margin: const EdgeInsets.only(right: 8),
                  child: Card(
                    color: Colors.deepPurple[700],
                    child: Padding(
                      padding: const EdgeInsets.all(8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            filePath.split('/').last,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                          Text(
                            '${functions.length} funcs, ${classes.length} classes',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 10,
                            ),
                          ),
                          if (patterns.isNotEmpty)
                            Text(
                              patterns.first,
                              style: const TextStyle(
                                color: Colors.greenAccent,
                                fontSize: 10,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),
        ],

        // Date selector
        Row(
          children: [
            const Icon(
              Icons.calendar_today,
              color: Colors.cyanAccent,
              size: 20,
            ),
            const SizedBox(width: 8),
            Expanded(
              child: DropdownButton<String>(
                value: _selectedDate,
                isExpanded: true,
                dropdownColor: Colors.deepPurple[900],
                iconEnabledColor: Colors.cyanAccent,
                items: [
                  for (final month in monthToDates.keys) ...[
                    DropdownMenuItem<String>(
                      enabled: false,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Text(
                          '${_monthName(month.split('-')[1])} ${month.split('-')[0]}',
                          style: const TextStyle(
                            color: Colors.cyanAccent,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    ...monthToDates[month]!.map(
                      (date) => DropdownMenuItem<String>(
                        value: date,
                        child: Padding(
                          padding: const EdgeInsets.only(left: 16),
                          child: Text(
                            date,
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                      ),
                    ),
                  ],
                ],
                onChanged: (val) {
                  if (val != null && val != _selectedDate) {
                    setState(() {
                      _selectedDate = val;
                    });
                  }
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        // Enhanced experiment list
        SizedBox(
          height: 220,
          child:
              _selectedDate == null || _grouped[_selectedDate] == null
                  ? const Center(
                    child: Text(
                      'No experiments for this date.',
                      style: TextStyle(color: Colors.white70),
                    ),
                  )
                  : ListView(
                    shrinkWrap: true,
                    physics: const AlwaysScrollableScrollPhysics(),
                    children: [
                      for (final exp in _grouped[_selectedDate]!)
                        Card(
                          color: Colors.deepPurple[700],
                          child: ExpansionTile(
                            leading: const Icon(
                              Icons.psychology,
                              color: Colors.amberAccent,
                            ),
                            title: Text(
                              exp['focus'] ?? 'Unknown',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Text(
                              exp['description'] ?? '',
                              style: const TextStyle(color: Colors.white70),
                            ),
                            trailing: Text(
                              exp['timestamp'] != null
                                  ? (exp['timestamp'] is DateTime
                                      ? (exp['timestamp'] as DateTime)
                                          .toString()
                                          .substring(11, 19)
                                      : (exp['timestamp'].toString().length >=
                                              19
                                          ? exp['timestamp']
                                              .toString()
                                              .substring(11, 19)
                                          : exp['timestamp'].toString()))
                                  : '',
                              style: const TextStyle(
                                color: Colors.white38,
                                fontSize: 12,
                              ),
                            ),
                            children: [
                              // File analysis details
                              if (exp['filesAnalyzed'] != null) ...[
                                Padding(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        '📁 Files Analyzed:',
                                        style: TextStyle(
                                          color: Colors.cyanAccent,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      ...(exp['filesAnalyzed'] as List<String>)
                                          .take(3)
                                          .map(
                                            (file) => Padding(
                                              padding: const EdgeInsets.only(
                                                left: 8,
                                              ),
                                              child: Text(
                                                file.split('/').last,
                                                style: const TextStyle(
                                                  color: Colors.white70,
                                                  fontSize: 12,
                                                ),
                                              ),
                                            ),
                                          ),
                                      if ((exp['filesAnalyzed'] as List<String>)
                                              .length >
                                          3)
                                        Padding(
                                          padding: const EdgeInsets.only(
                                            left: 8,
                                          ),
                                          child: Text(
                                            '... and ${(exp['filesAnalyzed'] as List<String>).length - 3} more',
                                            style: const TextStyle(
                                              color: Colors.white54,
                                              fontSize: 12,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              ],

                              // Learning insights
                              if (exp['learning'] != null) ...[
                                Padding(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        '🧠 Key Learnings:',
                                        style: TextStyle(
                                          color: Colors.amberAccent,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      ...(exp['learning'] as List<String>)
                                          .take(2)
                                          .map(
                                            (learning) => Padding(
                                              padding: const EdgeInsets.only(
                                                left: 8,
                                              ),
                                              child: Text(
                                                learning,
                                                style: const TextStyle(
                                                  color: Colors.white70,
                                                  fontSize: 12,
                                                ),
                                              ),
                                            ),
                                          ),
                                      if ((exp['learning'] as List<String>)
                                              .length >
                                          2)
                                        Padding(
                                          padding: const EdgeInsets.only(
                                            left: 8,
                                          ),
                                          child: Text(
                                            '... and ${(exp['learning'] as List<String>).length - 2} more insights',
                                            style: const TextStyle(
                                              color: Colors.white54,
                                              fontSize: 12,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                ),
                              ],

                              // Primary focus
                              if (exp['primaryFile'] != null) ...[
                                Padding(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 8,
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      const Text(
                                        '🎯 Primary Focus:',
                                        style: TextStyle(
                                          color: Colors.greenAccent,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Padding(
                                        padding: const EdgeInsets.only(left: 8),
                                        child: Text(
                                          '${exp['primaryFile']}:${exp['primarySymbol'] ?? 'unknown'}',
                                          style: const TextStyle(
                                            color: Colors.white70,
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                    ],
                  ),
        ),
      ],
    );
  }

  String _monthName(String monthNum) {
    switch (monthNum) {
      case '01':
        return 'January';
      case '02':
        return 'February';
      case '03':
        return 'March';
      case '04':
        return 'April';
      case '05':
        return 'May';
      case '06':
        return 'June';
      case '07':
        return 'July';
      case '08':
        return 'August';
      case '09':
        return 'September';
      case '10':
        return 'October';
      case '11':
        return 'November';
      case '12':
        return 'December';
      default:
        return '';
    }
  }
}

class _MechanicumSuggestionsInstantUI extends StatefulWidget {
  final List<Map<String, dynamic>> suggestions;
  final dynamic provider;
  const _MechanicumSuggestionsInstantUI({
    required this.suggestions,
    required this.provider,
  });

  @override
  State<_MechanicumSuggestionsInstantUI> createState() =>
      _MechanicumSuggestionsInstantUIState();
}

class _MechanicumSuggestionsInstantUIState
    extends State<_MechanicumSuggestionsInstantUI> {
  final Set<String> _locallyApplied = {};
  final Set<String> _locallyIgnored = {};

  // Cache provider data to prevent repeated calls
  Map<String, String>? _cachedFeedback;
  List<Map<String, dynamic>>? _cachedAppliedSuggestions;

  @override
  void initState() {
    super.initState();
    _cacheProviderData();
  }

  void _cacheProviderData() {
    _cachedFeedback = Map<String, String>.from(
      widget.provider.aiSuggestionFeedback,
    );
    _cachedAppliedSuggestions = List<Map<String, dynamic>>.from(
      widget.provider.appliedAISuggestions,
    );
  }

  @override
  Widget build(BuildContext context) {
    // Group by month
    final Map<String, List<Map<String, dynamic>>> grouped = {};
    for (final s in widget.suggestions) {
      final ts = s['timestamp'];
      DateTime dt;
      if (ts is DateTime) {
        dt = ts;
      } else if (ts is String) {
        dt = DateTime.tryParse(ts) ?? DateTime.now();
      } else {
        dt = DateTime.now();
      }
      final key = '${dt.year}-${dt.month.toString().padLeft(2, '0')}';
      grouped.putIfAbsent(key, () => []).add(s);
    }
    // Sort months descending
    final sortedKeys = grouped.keys.toList()..sort((a, b) => b.compareTo(a));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final month in sortedKeys) ...[
          // Counters
          Builder(
            builder: (context) {
              final monthSuggestions = grouped[month]!;
              int redCount = 0;
              int greenCount = 0;

              // Cache provider data to prevent repeated calls
              final aiSuggestionFeedback = _cachedFeedback ?? {};
              final appliedAISuggestions = _cachedAppliedSuggestions ?? [];

              for (final s in monthSuggestions) {
                final title = s['title'];
                final status = aiSuggestionFeedback[title] ?? '';
                final isLocallyApplied = _locallyApplied.contains(title);
                final isLocallyIgnored = _locallyIgnored.contains(title);
                final isApplied =
                    isLocallyApplied ||
                    status == 'applied' ||
                    appliedAISuggestions.any((a) => a['title'] == title);
                final isIgnored = isLocallyIgnored || status == 'ignored';

                if (isApplied) {
                  greenCount++;
                } else if (isIgnored) {
                  redCount++;
                } else {
                  redCount++;
                }
              }

              final monthName = () {
                final parts = month.split('-');
                final y = parts[0];
                final m = int.tryParse(parts[1]) ?? 1;
                const names = [
                  '',
                  'January',
                  'February',
                  'March',
                  'April',
                  'May',
                  'June',
                  'July',
                  'August',
                  'September',
                  'October',
                  'November',
                  'December',
                ];
                return '${names[m]} $y';
              }();

              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(
                  children: [
                    Text(
                      monthName,
                      style: const TextStyle(
                        color: Colors.cyanAccent,
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(width: 12),
                    if (redCount > 0)
                      Chip(
                        label: Text('$redCount'),
                        backgroundColor: Colors.redAccent,
                        labelStyle: const TextStyle(color: Colors.white),
                      ),
                    const SizedBox(width: 6),
                    if (greenCount > 0)
                      Chip(
                        label: Text('$greenCount'),
                        backgroundColor: Colors.green,
                        labelStyle: const TextStyle(color: Colors.white),
                      ),
                  ],
                ),
              );
            },
          ),
          // Suggestion cards (only show not applied/ignored locally)
          ...grouped[month]!
              .where((s) {
                final title = s['title'];
                // Cache provider data to prevent repeated calls
                final aiSuggestionFeedback = _cachedFeedback ?? {};
                final appliedAISuggestions = _cachedAppliedSuggestions ?? [];

                final status = aiSuggestionFeedback[title] ?? '';
                final isLocallyApplied = _locallyApplied.contains(title);
                final isLocallyIgnored = _locallyIgnored.contains(title);
                final isApplied =
                    isLocallyApplied ||
                    status == 'applied' ||
                    appliedAISuggestions.any((a) => a['title'] == title);
                final isIgnored = isLocallyIgnored || status == 'ignored';

                return !isApplied && !isIgnored;
              })
              .map<Widget>((s) {
                final title = s['title'];
                // Cache provider data to prevent repeated calls
                final aiSuggestionFeedback = _cachedFeedback ?? {};
                final status = aiSuggestionFeedback[title] ?? '';
                final isLocallyIgnored = _locallyIgnored.contains(title);

                return SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Card(
                    color: Colors.black,
                    child: Container(
                      width: 420,
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    s['title'] ?? '',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                if (status == 'ignored' || isLocallyIgnored)
                                  const Icon(
                                    Icons.cancel,
                                    color: Colors.redAccent,
                                  ),
                              ],
                            ),
                            if (s['reasoning'] != null)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 4),
                                child: Text(
                                  'Reason: ${s['reasoning']}',
                                  style: const TextStyle(color: Colors.white70),
                                ),
                              ),
                            if (s['diff'] != null)
                              Padding(
                                padding: const EdgeInsets.only(bottom: 4),
                                child: Text(
                                  'Diff: ${s['diff']}',
                                  style: const TextStyle(
                                    color: Colors.greenAccent,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              ),
                            if (s['code'] != null)
                              Container(
                                width: double.infinity,
                                margin: const EdgeInsets.only(
                                  top: 4,
                                  bottom: 4,
                                ),
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.grey[850],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: SelectableText(
                                  s['code'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              ),
                            Row(
                              children: [
                                IconButton(
                                  icon: const Icon(
                                    Icons.copy,
                                    color: Colors.cyanAccent,
                                  ),
                                  tooltip: 'Copy code',
                                  onPressed: () {
                                    Clipboard.setData(
                                      ClipboardData(text: s['code'] ?? ''),
                                    );
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text(
                                          'Code copied to clipboard',
                                        ),
                                      ),
                                    );
                                  },
                                ),
                                const SizedBox(width: 8),
                                if (!_locallyApplied.contains(title) &&
                                    !_locallyIgnored.contains(title))
                                  _ApplySuggestionButton(
                                    suggestion: s,
                                    onApplied: () {
                                      // Only update if not already applied
                                      if (!_locallyApplied.contains(title)) {
                                        setState(() {
                                          _locallyApplied.add(title);
                                        });
                                      }
                                    },
                                  ),
                                const SizedBox(width: 8),
                                if (!_locallyApplied.contains(title) &&
                                    !_locallyIgnored.contains(title))
                                  OutlinedButton.icon(
                                    icon: const Icon(
                                      Icons.close,
                                      size: 16,
                                      color: Colors.redAccent,
                                    ),
                                    label: const Text(
                                      'Ignore',
                                      style: TextStyle(color: Colors.redAccent),
                                    ),
                                    style: OutlinedButton.styleFrom(
                                      side: const BorderSide(
                                        color: Colors.redAccent,
                                      ),
                                    ),
                                    onPressed: () {
                                      // Only update if not already ignored
                                      if (!_locallyIgnored.contains(title)) {
                                        setState(() {
                                          _locallyIgnored.add(title);
                                        });
                                      }
                                      // Call provider in background
                                      Future.microtask(
                                        () => widget.provider
                                            .ignoreAISuggestion(title),
                                      );
                                    },
                                  ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              })
              .toList(),
        ],
      ],
    );
  }
}

class _ApplySuggestionButton extends StatefulWidget {
  final Map<String, dynamic> suggestion;
  final VoidCallback? onApplied;
  const _ApplySuggestionButton({required this.suggestion, this.onApplied});

  @override
  State<_ApplySuggestionButton> createState() => _ApplySuggestionButtonState();
}

class _ApplySuggestionButtonState extends State<_ApplySuggestionButton> {
  bool _loading = false;

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<MissionProvider>(context, listen: false);
    final suggestion = widget.suggestion;
    final hasTarget =
        suggestion.containsKey('targetFile') &&
        suggestion.containsKey('targetSymbol') &&
        (suggestion['targetFile']?.toString().isNotEmpty ?? false) &&
        (suggestion['targetSymbol']?.toString().isNotEmpty ?? false);

    return _loading
        ? const SizedBox(
          width: 90,
          child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
        )
        : ElevatedButton.icon(
          icon: const Icon(Icons.build, size: 16),
          label: const Text('Apply'),
          style: ElevatedButton.styleFrom(
            backgroundColor: hasTarget ? Colors.blueAccent : Colors.grey,
            foregroundColor: Colors.white,
          ),
          onPressed:
              hasTarget
                  ? () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder:
                          (context) => AlertDialog(
                            backgroundColor: Colors.grey[900],
                            title: const Text(
                              'Apply Suggestion?',
                              style: TextStyle(color: Colors.white),
                            ),
                            content: const Text(
                              'Are you sure you want to apply this suggestion?',
                              style: TextStyle(color: Colors.white70),
                            ),
                            actions: [
                              TextButton(
                                onPressed:
                                    () => Navigator.of(context).pop(false),
                                child: const Text(
                                  'No',
                                  style: TextStyle(color: Colors.redAccent),
                                ),
                              ),
                              TextButton(
                                onPressed:
                                    () => Navigator.of(context).pop(true),
                                child: const Text(
                                  'Yes',
                                  style: TextStyle(color: Colors.greenAccent),
                                ),
                              ),
                            ],
                          ),
                    );
                    if (confirmed == true) {
                      setState(() => _loading = true);

                      // Call the onApplied callback first
                      if (widget.onApplied != null) {
                        widget.onApplied!();
                      }

                      // Apply the suggestion in the background without waiting
                      Future.microtask(() {
                        try {
                          provider.applyAISuggestion(suggestion['title']);
                        } catch (e) {
                          // Silently handle errors
                        }
                      });

                      if (mounted) {
                        setState(() => _loading = false);
                        // Use the context safely after checking mounted
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Suggestion applied!'),
                            ),
                          );
                        }
                      }
                    }
                  }
                  : null,
        );
  }
}
