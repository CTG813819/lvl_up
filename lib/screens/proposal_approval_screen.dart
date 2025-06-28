import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/proposal_provider.dart';
import '../models/ai_proposal.dart';
import 'package:timeago/timeago.dart' as timeago;
import 'package:flutter_highlight/flutter_highlight.dart';
import 'package:flutter_highlight/themes/github.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../providers/ai_learning_provider.dart';

class ProposalApprovalScreen extends StatefulWidget {
  const ProposalApprovalScreen({super.key});

  @override
  State<ProposalApprovalScreen> createState() => _ProposalApprovalScreenState();
}

class _ProposalApprovalScreenState extends State<ProposalApprovalScreen> {
  String? _selectedAIType;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Proposals'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          // Approve All button
          IconButton(
            icon: const Icon(Icons.approval),
            onPressed: () async {
              final provider = Provider.of<ProposalProvider>(context, listen: false);
              final pendingCount = provider.pendingProposals.length;
              
              if (pendingCount == 0) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('No pending proposals to approve'),
                      backgroundColor: Colors.orange,
                    ),
                  );
                }
                return;
              }
              
              // Show confirmation dialog
              if (context.mounted) {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('Approve All Proposals'),
                    content: Text('Are you sure you want to approve all $pendingCount pending proposals?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('Cancel'),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                        child: const Text('Approve All'),
                      ),
                    ],
                  ),
                );
                
                if (confirmed == true) {
                  await provider.approveAllProposals();
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Approved all $pendingCount proposals'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                }
              }
            },
            tooltip: 'Approve all pending proposals',
          ),
          // Debug button
          IconButton(
            icon: const Icon(Icons.bug_report),
            onPressed: () async {
              final provider = Provider.of<ProposalProvider>(context, listen: false);
              await provider.testBackendConnection();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Debug: Fetched ${provider.proposals.length} total proposals, ${provider.pendingProposals.length} pending'),
                    backgroundColor: Colors.blue,
                  ),
                );
              }
            },
            tooltip: 'Debug: Test backend connection',
          ),
          // Debug Learning button
          IconButton(
            icon: const Icon(Icons.psychology),
            onPressed: () async {
              try {
                final url = Uri.parse('${ProposalProvider.backendUrl}/debug/learning');
                final response = await http.get(url).timeout(const Duration(seconds: 10));
                
                if (response.statusCode == 200) {
                  final data = jsonDecode(response.body);
                  if (context.mounted) {
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('AI Learning Debug'),
                        content: SingleChildScrollView(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text('Imperium Insights: ${data['imperiumInsights']}'),
                              Text('Sandbox Insights: ${data['sandboxInsights']}'),
                              Text('Guardian Insights: ${data['guardianInsights']}'),
                              const SizedBox(height: 8),
                              const Text('Imperium Lessons:', style: TextStyle(fontWeight: FontWeight.bold)),
                              ...(data['imperiumLessons'] as List).take(3).map((l) => Text('• $l')),
                              const SizedBox(height: 8),
                              const Text('Sandbox Lessons:', style: TextStyle(fontWeight: FontWeight.bold)),
                              ...(data['sandboxLessons'] as List).take(3).map((l) => Text('• $l')),
                              const SizedBox(height: 8),
                              const Text('Guardian Lessons:', style: TextStyle(fontWeight: FontWeight.bold)),
                              ...(data['guardianLessons'] as List).take(3).map((l) => Text('• $l')),
                            ],
                          ),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(),
                            child: const Text('Close'),
                          ),
                        ],
                      ),
                    );
                  }
                } else {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Debug learning failed: ${response.statusCode}'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Debug learning error: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            tooltip: 'Debug: Check AI learning state',
          ),
          // Learning Verification button
          IconButton(
            icon: const Icon(Icons.verified),
            onPressed: () async {
              try {
                final url = Uri.parse('${ProposalProvider.backendUrl}/api/learning-verification');
                final response = await http.get(url).timeout(const Duration(seconds: 15));
                
                if (context.mounted) {
                  if (response.statusCode == 200) {
                    final data = jsonDecode(response.body);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Learning verification: ${data['verification']?.length ?? 0} AIs analyzed'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Learning verification failed: ${response.statusCode}'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Learning verification error: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            tooltip: 'Verify AI learning effectiveness',
          ),
          // Learning Effectiveness button
          IconButton(
            icon: const Icon(Icons.analytics),
            onPressed: () async {
              try {
                final url = Uri.parse('${ProposalProvider.backendUrl}/api/learning-effectiveness');
                final response = await http.get(url).timeout(const Duration(seconds: 15));
                
                if (context.mounted) {
                  if (response.statusCode == 200) {
                    final data = jsonDecode(response.body);
                    final effectiveness = data['effectiveness'] ?? {};
                    final overall = effectiveness['overall'] ?? {};
                    
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Learning effectiveness: ${overall['completionRate'] ?? 0}% completion rate'),
                        backgroundColor: Colors.blue,
                        duration: const Duration(seconds: 3),
                      ),
                    );
                  } else {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('Learning effectiveness failed: ${response.statusCode}'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Learning effectiveness error: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            tooltip: 'View learning effectiveness metrics',
          ),
          // Manual Learning Trigger button
          IconButton(
            icon: const Icon(Icons.play_arrow),
            onPressed: () async {
              try {
                // Show dialog to select AI
                final selectedAI = await showDialog<String>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('Trigger Learning'),
                    content: const Text('Select an AI to manually trigger learning check:'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop('Imperium'),
                        child: const Text('Imperium'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop('Sandbox'),
                        child: const Text('Sandbox'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop('Guardian'),
                        child: const Text('Guardian'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(null),
                        child: const Text('Cancel'),
                      ),
                    ],
                  ),
                );
                
                if (selectedAI != null && context.mounted) {
                  final url = Uri.parse('${ProposalProvider.backendUrl}/api/ai/$selectedAI/trigger-learning');
                  final response = await http.post(url).timeout(const Duration(seconds: 15));
                  
                  if (context.mounted) {
                    if (response.statusCode == 200) {
                      final data = jsonDecode(response.body);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('${data['message']} - ${selectedAI} isLearning: ${data['isLearning']}'),
                          backgroundColor: data['isLearning'] ? Colors.orange : Colors.green,
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('Learning trigger failed: ${response.statusCode}'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  }
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('Learning trigger error: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            tooltip: 'Manually trigger learning check',
          ),
          // Refresh button
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              final provider = Provider.of<ProposalProvider>(context, listen: false);
              await provider.fetchProposals();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Refreshed: ${provider.proposals.length} total proposals, ${provider.pendingProposals.length} pending'),
                    backgroundColor: Colors.green,
                  ),
                );
              }
            },
            tooltip: 'Refresh proposals',
          ),
        ],
      ),
      body: Consumer<ProposalProvider>(
        builder: (context, provider, child) {
          final pendingProposals = provider.pendingProposals;
          final totalProposals = provider.proposals.length;
          
          if (totalProposals == 0) {
            return _buildEmptyState(context, provider);
          }
          
          if (pendingProposals.isEmpty) {
            return _buildNoPendingState(context, provider, totalProposals);
          }

          // Filter proposals by selected AI type
          final filteredProposals = _selectedAIType == null 
              ? pendingProposals 
              : pendingProposals.where((p) => p.aiType == _selectedAIType).toList();
          
          return Column(
            children: [
              // Filter chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    FilterChip(
                      label: const Text('All'),
                      selected: _selectedAIType == null,
                      onSelected: (selected) {
                        setState(() {
                          _selectedAIType = null;
                        });
                      },
                      selectedColor: Colors.cyanAccent.withValues(alpha: 0.3),
                      checkmarkColor: Colors.cyanAccent,
                    ),
                    const SizedBox(width: 8),
                    ...['Imperium', 'Sandbox', 'Guardian'].map((aiType) {
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: Text(aiType),
                          selected: _selectedAIType == aiType,
                          onSelected: (selected) {
                            setState(() {
                              _selectedAIType = selected ? aiType : null;
                            });
                          },
                          selectedColor: Colors.cyanAccent.withValues(alpha: 0.3),
                          checkmarkColor: Colors.cyanAccent,
                        ),
                      );
                    }),
                  ],
                ),
              ),
              // Summary header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.deepPurple.shade50, Colors.white],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Pending Reviews',
                              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                                color: Colors.deepPurple.shade800,
                              ),
                            ),
                            Text(
                              '$totalProposals total proposals',
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: Colors.orange.shade100,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: Colors.orange.shade300),
                          ),
                          child: Text(
                            '${filteredProposals.length} pending',
                            style: TextStyle(
                              color: Colors.orange.shade800,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
              // Proposals list with proper height constraint
              Flexible(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: filteredProposals.length,
                  itemBuilder: (context, index) {
                    final proposal = filteredProposals[index];
                    return _buildProposalCard(context, proposal, provider);
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildFilterChip(String label, String? aiType, Color color) {
    final isSelected = _selectedAIType == aiType;
    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedAIType = isSelected ? null : aiType;
        });
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isSelected ? color : color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? color : color.withOpacity(0.3),
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? Colors.white : _getShadeColor(color),
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
            fontSize: 12,
          ),
        ),
      ),
    );
  }

  Color _getShadeColor(Color color) {
    // Convert to a darker shade for better contrast
    return color.withOpacity(0.8);
  }

  Widget _buildAITypeChip(String aiType, int count, Color color) {
    if (count == 0) return const SizedBox.shrink();
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        '$aiType: $count',
        style: TextStyle(
          color: _getShadeColor(color),
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, ProposalProvider provider) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: Colors.grey.shade400),
          const SizedBox(height: 16),
          Text(
            'No proposals found.',
            style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 8),
          Text(
            'Total proposals: 0',
            style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
          ),
          const SizedBox(height: 24),
          _buildActionButtons(context, provider),
        ],
      ),
    );
  }

  Widget _buildNoPendingState(BuildContext context, ProposalProvider provider, int totalProposals) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle_outline, size: 64, color: Colors.green.shade400),
          const SizedBox(height: 16),
          Text(
            'No pending proposals.',
            style: TextStyle(fontSize: 18, color: Colors.grey.shade600),
          ),
          const SizedBox(height: 8),
          Text(
            'Total proposals: $totalProposals',
            style: TextStyle(fontSize: 14, color: Colors.grey.shade500),
          ),
          const SizedBox(height: 24),
          _buildActionButtons(context, provider),
        ],
      ),
    );
  }

  Widget _buildActionButtons(BuildContext context, ProposalProvider provider) {
    return Column(
      children: [
        ElevatedButton.icon(
          onPressed: () async {
            await provider.fetchProposals();
          },
          icon: const Icon(Icons.refresh),
          label: const Text('Refresh Proposals'),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.deepPurple,
            foregroundColor: Colors.white,
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () async {
            await provider.createTestProposal();
          },
          icon: const Icon(Icons.add),
          label: const Text('Create Test Proposal'),
          style: OutlinedButton.styleFrom(
            foregroundColor: Colors.orange.withOpacity(0.8),
            side: BorderSide(color: Colors.orange.shade300),
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () async {
            await provider.testBackendConnection();
          },
          icon: const Icon(Icons.wifi),
          label: const Text('Test Backend Connection'),
          style: OutlinedButton.styleFrom(
            foregroundColor: Colors.blue.withOpacity(0.8),
            side: BorderSide(color: Colors.blue.shade300),
          ),
        ),
      ],
    );
  }

  Widget _buildProposalCard(BuildContext context, AIProposal proposal, ProposalProvider provider) {
    final aiLearningProvider = Provider.of<AILearningProvider>(context, listen: false);
    final isLearning = aiLearningProvider.aiLearningStatus[proposal.aiType]?['isLearning'] == true;
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: _ProposalCardContent(
        proposal: proposal,
        provider: provider,
        isLearning: isLearning,
      ),
    );
  }
}

class _ProposalCardContent extends StatefulWidget {
  final AIProposal proposal;
  final ProposalProvider provider;
  final bool isLearning;
  const _ProposalCardContent({required this.proposal, required this.provider, this.isLearning = false});
  @override
  State<_ProposalCardContent> createState() => _ProposalCardContentState();
}

class _ProposalCardContentState extends State<_ProposalCardContent> {
  bool _isExpanded = false;

  Color _getAIColor(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'imperium':
        return Colors.blue;
      case 'sandbox':
        return Colors.green;
      case 'guardian':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Color _getShadeColor(Color color) {
    // Convert to a darker shade for better contrast
    return color.withOpacity(0.8);
  }

  String _getSummary(String oldCode, String newCode) {
    final oldLines = oldCode.split('\n').length;
    final newLines = newCode.split('\n').length;
    final addedLines = newLines - oldLines;
    
    if (addedLines > 0) {
      return '+$addedLines lines added';
    } else if (addedLines < 0) {
      return '${addedLines.abs()} lines removed';
    } else {
      return 'Code refactored';
    }
  }

  String _getFileType(String filePath) {
    if (filePath.contains('widget')) return 'UI Widget';
    if (filePath.contains('provider')) return 'State Management';
    if (filePath.contains('service')) return 'Service';
    if (filePath.contains('model')) return 'Data Model';
    if (filePath.contains('util')) return 'Utility';
    return 'Code';
  }

  @override
  Widget build(BuildContext context) {
    final aiColor = _getAIColor(widget.proposal.aiType);
    final summary = _getSummary(widget.proposal.oldCode, widget.proposal.newCode);
    final fileType = _getFileType(widget.proposal.filePath);
    
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: aiColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: aiColor.withOpacity(0.3)),
                ),
                child: Text(
                  widget.proposal.aiType,
                  style: TextStyle(
                    color: _getShadeColor(aiColor),
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  fileType,
                  style: TextStyle(
                    color: Colors.grey.withOpacity(0.8),
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                timeago.format(widget.proposal.timestamp),
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 12),
          
          // File path
          Text(
            widget.proposal.filePath,
            style: TextStyle(
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade800,
              fontSize: 14,
            ),
          ),
          
          const SizedBox(height: 8),
          
          // Summary
          Row(
            children: [
              Icon(
                Icons.edit,
                size: 16,
                color: Colors.grey.shade600,
              ),
              const SizedBox(width: 4),
              Text(
                summary,
                style: TextStyle(
                  color: Colors.grey.shade600,
                  fontSize: 13,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Action buttons - Made larger and clearer
          Column(
            children: [
              // Show Details button
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => setState(() => _isExpanded = !_isExpanded),
                  icon: Icon(_isExpanded ? Icons.expand_less : Icons.expand_more),
                  label: Text(_isExpanded ? 'Hide Details' : 'Show Details'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.grey.withOpacity(0.8),
                    side: BorderSide(color: Colors.grey.shade300),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Approve/Reject buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: widget.isLearning
                          ? () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('${widget.proposal.aiType} is currently learning. Actions are paused.'),
                                  backgroundColor: Colors.orange,
                                ),
                              );
                            }
                          : () async {
                              await widget.provider.approveProposal(widget.proposal.id);
                              if (mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('✅ ${widget.proposal.aiType} proposal approved!'),
                                    backgroundColor: Colors.green,
                                  ),
                                );
                              }
                            },
                      icon: const Icon(Icons.check, size: 18),
                      label: const Text('Approve'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: widget.isLearning ? Colors.grey : Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: widget.isLearning
                          ? () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('${widget.proposal.aiType} is currently learning. Actions are paused.'),
                                  backgroundColor: Colors.orange,
                                ),
                              );
                            }
                          : () => widget.provider.rejectProposal(widget.proposal.id),
                      icon: const Icon(Icons.close, size: 18),
                      label: const Text('Reject'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: widget.isLearning ? Colors.grey : Colors.red.withOpacity(0.8),
                        side: BorderSide(color: widget.isLearning ? Colors.grey : Colors.red.shade300),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          
          // Expandable details
          if (_isExpanded) ...[
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 12),
            Text(
              'Code Changes:',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade800,
              ),
            ),
            const SizedBox(height: 8),
            _buildCodePreview(widget.proposal.oldCode, widget.proposal.newCode),
          ],
        ],
      ),
    );
  }

  Widget _buildCodePreview(String oldCode, String newCode) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          // Before/After tabs
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.red.shade50,
                    border: Border(bottom: BorderSide(color: Colors.red.shade200)),
                  ),
                  child: Text(
                    'Before',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.red.withOpacity(0.8),
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    border: Border(bottom: BorderSide(color: Colors.green.shade200)),
                  ),
                  child: Text(
                    'After',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.green.withOpacity(0.8),
                      fontWeight: FontWeight.w500,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
          // Scrollable code preview with fixed height
          SizedBox(
            height: 300,
            child: Row(
              children: [
                Expanded(
                  child: SingleChildScrollView(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      child: HighlightView(
                        oldCode,
                        language: 'dart',
                        theme: githubTheme,
                        textStyle: const TextStyle(fontSize: 11),
                      ),
                    ),
                  ),
                ),
                Container(width: 1, color: Colors.grey.shade300),
                Expanded(
                  child: SingleChildScrollView(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      child: HighlightView(
                        newCode,
                        language: 'dart',
                        theme: githubTheme,
                        textStyle: const TextStyle(fontSize: 11),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 