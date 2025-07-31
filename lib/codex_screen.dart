import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import './home_page.dart';
import 'package:provider/provider.dart';
import 'providers/ai_growth_analytics_provider.dart';

// Standalone widget for backend connection dot
class BackendConnectionDot extends StatelessWidget {
  const BackendConnectionDot({super.key});

  Future<bool> _checkBackendConnection() async {
    // This logic should match the one in AILearningDashboard
    // You may want to refactor this to a shared service if needed
    try {
      // Simulate a check or use your actual backend health check
      // For now, always return true for demo
      return true;
    } catch (_) {
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
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

class CodexScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AIGrowthAnalyticsProvider()..initializeInternetLearning(),
      child: Consumer<AIGrowthAnalyticsProvider>(
        builder: (context, provider, child) {
          final log = provider.internetLearningLog.reversed.toList();
          return Scaffold(
            appBar: AppBar(
              leading: IconButton(
                icon: Icon(Icons.arrow_back),
                onPressed: () => Navigator.pop(context),
              ),
              title: Text('Codex'),
              actions: [
                Icon(
                  provider.wsConnected ? Icons.wifi : Icons.wifi_off,
                  color: provider.wsConnected ? Colors.green : Colors.red,
                ),
                IconButton(
                  icon: const Icon(Icons.refresh),
                  onPressed: () => provider.fetchInternetLearningLog(),
                ),
              ],
            ),
            body:
                log.isEmpty
                    ? const Center(
                      child: Text('No internet learning events yet.'),
                    )
                    : ListView.builder(
                      itemCount: log.length,
                      itemBuilder: (context, index) {
                        final entry = log[index];
                        return Card(
                          color: Colors.blueGrey[900],
                          margin: const EdgeInsets.symmetric(
                            vertical: 4,
                            horizontal: 8,
                          ),
                          child: ListTile(
                            leading: Icon(
                              Icons.lightbulb,
                              color: Colors.amberAccent,
                            ),
                            title: Text(
                              '${entry['agent_id']} learned: ${entry['topic']}',
                            ),
                            subtitle: Text(
                              'Sources: ${entry['results']?.map((r) => r['url']).join(', ') ?? ''}\n'
                              'Time: ${entry['timestamp']}',
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            trailing:
                                entry['results_count'] > 0
                                    ? CircleAvatar(
                                      backgroundColor: Colors.green,
                                      child: Text('${entry['results_count']}'),
                                    )
                                    : null,
                          ),
                        );
                      },
                    ),
          );
        },
      ),
    );
  }
}

class AICycleStatusBanner extends StatelessWidget {
  final Map<String, dynamic> status;
  const AICycleStatusBanner({Key? key, required this.status}) : super(key: key);

  Color _statusColor(String s) {
    switch (s) {
      case 'idle':
        return Colors.grey;
      case 'internet_searching':
        return Colors.blue;
      case 'improving':
        return Colors.green;
      default:
        return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    final agents = status['agents'] as Map<String, dynamic>?;
    if (agents == null) return SizedBox.shrink();
    return Container(
      width: double.infinity,
      color: Colors.black.withOpacity(0.05),
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Wrap(
        spacing: 16,
        runSpacing: 4,
        children:
            agents.entries.map((e) {
              final ai = e.key;
              final s = e.value as Map<String, dynamic>;
              return Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.circle,
                    color: _statusColor(s['status'] ?? ''),
                    size: 12,
                  ),
                  const SizedBox(width: 4),
                  Text('$ai: ${s['status']}'),
                  if (s['last_action'] != null) ...[
                    const SizedBox(width: 4),
                    Text(
                      '(${s['last_action']})',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ],
              );
            }).toList(),
      ),
    );
  }
}

class CodexChapter {
  final String chapter;
  final String date;
  final String summary;
  final List<CodexEvent> proposals;
  CodexChapter({
    required this.chapter,
    required this.date,
    required this.summary,
    required this.proposals,
  });
  factory CodexChapter.fromJson(Map<String, dynamic> json) => CodexChapter(
    chapter: json['chapter'],
    date: json['date'],
    summary: json['summary'],
    proposals:
        (json['proposals'] as List).map((e) => CodexEvent.fromJson(e)).toList(),
  );
}

class CodexEvent {
  final String id;
  final String aiType;
  final String filePath;
  final String status;
  final String? improvementType;
  final double confidence;
  final String? userFeedback;
  final String testStatus;
  final String createdAt;
  final String? updatedAt;
  final String? aiReasoning;
  final String? userFeedbackReason;
  CodexEvent({
    required this.id,
    required this.aiType,
    required this.filePath,
    required this.status,
    this.improvementType,
    required this.confidence,
    this.userFeedback,
    required this.testStatus,
    required this.createdAt,
    this.updatedAt,
    this.aiReasoning,
    this.userFeedbackReason,
  });
  factory CodexEvent.fromJson(Map<String, dynamic> json) => CodexEvent(
    id: json['id'],
    aiType: json['ai_type'],
    filePath: json['file_path'],
    status: json['status'],
    improvementType: json['improvement_type'],
    confidence:
        (json['confidence'] is int)
            ? (json['confidence'] as int).toDouble()
            : (json['confidence'] ?? 0.0),
    userFeedback: json['user_feedback'],
    testStatus: json['test_status'],
    createdAt: json['created_at'],
    updatedAt: json['updated_at'],
    aiReasoning: json['ai_reasoning'],
    userFeedbackReason: json['user_feedback_reason'],
  );
}

class TimelineWidget extends StatelessWidget {
  final List<CodexEvent> events;
  const TimelineWidget({Key? key, required this.events}) : super(key: key);

  Color _statusColor(String status) {
    switch (status) {
      case 'accepted':
        return Colors.green;
      case 'rejected':
        return Colors.red;
      case 'pending':
        return Colors.orange;
      case 'testing':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _aiIcon(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'imperium':
        return Icons.security;
      case 'guardian':
        return Icons.shield;
      case 'sandbox':
        return Icons.science;
      case 'conquest':
        return Icons.flag;
      default:
        return Icons.memory;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Column(
      children:
          events.map((event) {
            return ListTile(
              leading: CircleAvatar(
                backgroundColor: isDark ? Colors.grey[900] : Colors.grey[200],
                child: Icon(
                  _aiIcon(event.aiType),
                  color: _statusColor(event.status),
                ),
              ),
              title: Text(
                '${event.aiType} — ${event.status.toUpperCase()}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: _statusColor(event.status),
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('File: ${event.filePath}'),
                  if (event.improvementType != null)
                    Text('Type: ${event.improvementType}'),
                  if (event.aiReasoning != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 4.0),
                      child: Text('Reasoning: ${event.aiReasoning}'),
                    ),
                  if (event.userFeedbackReason != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 2.0),
                      child: Text('Feedback: ${event.userFeedbackReason}'),
                    ),
                  Text(
                    'Confidence: ${(event.confidence * 100).toStringAsFixed(1)}%',
                  ),
                  Text('Created: ${event.createdAt}'),
                  if (event.updatedAt != null)
                    Text('Updated: ${event.updatedAt}'),
                ],
              ),
              trailing: Chip(
                label: Text(event.status.toUpperCase()),
                backgroundColor: _statusColor(event.status).withOpacity(0.2),
                labelStyle: TextStyle(
                  color: _statusColor(event.status),
                  fontWeight: FontWeight.bold,
                ),
              ),
              contentPadding: const EdgeInsets.symmetric(
                vertical: 8,
                horizontal: 16,
              ),
            );
          }).toList(),
    );
  }
}
