import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/services/network_config.dart';
import '../providers/proposal_provider.dart';
import '../models/ai_proposal.dart';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

class ProposalApprovalScreen extends StatefulWidget {
  static const String routeName = '/proposal_approval';
  const ProposalApprovalScreen({Key? key}) : super(key: key);

  @override
  State<ProposalApprovalScreen> createState() => _ProposalApprovalScreenState();
}

class _ProposalApprovalScreenState extends State<ProposalApprovalScreen>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _slideController;
  String _selectedCategory = 'All';
  String _selectedStatus = 'TestPassed';
  Timer? _refreshTimer;

  final List<String> _categories = [
    'All',
    'Sandbox',
    'Guardian',
    'Imperium',
    'Conquest',
  ];
  final List<String> _statuses = [
    'All',
    'Pending',
    'Approved',
    'Testing',
    'Rejected',
    'Applied',
    'TestPassed',
    'TestFailed',
  ];

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fadeController.forward();
      _slideController.forward();
      _startAutoRefresh();
    });
  }

  void _startAutoRefresh() {
    _refreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted) {
        Provider.of<ProposalProvider>(
          context,
          listen: false,
        ).fetchUserReadyProposals();
      }
    });
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _slideController.dispose();
    _refreshTimer?.cancel();
    super.dispose();
  }

  List<AIProposal> _getFilteredProposals(ProposalProvider provider) {
    var proposals = provider.proposals.toList();

    // Only show test-passed proposals
    proposals =
        proposals.where((p) => p.status == ProposalStatus.testPassed).toList();

    if (_selectedCategory != 'All') {
      proposals =
          proposals.where((p) => p.aiType == _selectedCategory).toList();
    }

    return proposals;
  }

  Future<void> _applyPatch(BuildContext context, AIProposal proposal) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Apply Patch?'),
            content: Text(
              'Do you want to apply this patch to the ${proposal.aiType} (${proposal.filePath})?',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Apply'),
              ),
            ],
          ),
    );
    if (confirmed != true) return;

    // Show loading screen
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator()),
    );

    try {
      final response = await http.post(
        Uri.parse(
          '${NetworkConfig.backendUrl}/api/proposals',
        ),
      );
      Navigator.pop(context); // Remove loading
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Patch applied successfully!')),
        );
        Provider.of<ProposalProvider>(
          context,
          listen: false,
        ).fetchUserReadyProposals();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Patch failed: ${response.body}')),
        );
      }
    } catch (e) {
      Navigator.pop(context); // Remove loading
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error applying patch: $e')));
    }
  }

  Color _getAITypeColor(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'sandbox':
        return Colors.purple;
      case 'guardian':
        return Colors.blue;
      case 'imperium':
        return Colors.orange;
      case 'conquest':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  IconData _getAITypeIcon(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'sandbox':
        return Icons.science;
      case 'guardian':
        return Icons.security;
      case 'imperium':
        return Icons.psychology;
      case 'conquest':
        return Icons.public;
      default:
        return Icons.smart_toy;
    }
  }

  Color _getStatusColor(ProposalStatus status) {
    switch (status) {
      case ProposalStatus.pending:
        return Colors.orange;
      case ProposalStatus.approved:
        return Colors.green;
      case ProposalStatus.testing:
        return Colors.blue;
      case ProposalStatus.rejected:
        return Colors.red;
      case ProposalStatus.applied:
        return Colors.blue;
      case ProposalStatus.testPassed:
        return Colors.green;
      case ProposalStatus.testFailed:
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  ProposalStatus _getStatusFromString(String status) {
    switch (status.toLowerCase()) {
      case 'pending':
        return ProposalStatus.pending;
      case 'approved':
        return ProposalStatus.approved;
      case 'testing':
        return ProposalStatus.testing;
      case 'rejected':
        return ProposalStatus.rejected;
      case 'applied':
        return ProposalStatus.applied;
      case 'testpassed':
        return ProposalStatus.testPassed;
      case 'testfailed':
        return ProposalStatus.testFailed;
      default:
        return ProposalStatus.pending;
    }
  }

  Color _getConfidenceColor(double? confidence) {
    if (confidence == null) return Colors.grey;
    if (confidence >= 0.8) {
      return Colors.green;
    } else if (confidence >= 0.5) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  String _generateDescription(AIProposal proposal) {
    final oldLines = proposal.oldCode.split('\n').length;
    final newLines = proposal.newCode.split('\n').length;
    final addedLines = newLines - oldLines;

    // Change type
    String changeType = '';
    if (addedLines > 0) {
      changeType = 'Adds $addedLines line${addedLines > 1 ? 's' : ''}.';
    } else if (addedLines < 0) {
      changeType =
          'Removes ${addedLines.abs()} line${addedLines.abs() > 1 ? 's' : ''}.';
    } else {
      changeType = 'Refactors code.';
    }

    // File type and purpose
    String fileType = '';
    String filePurpose = '';
    if (proposal.filePath.contains('widget')) {
      fileType = 'UI widget';
      filePurpose = 'user interface component';
    } else if (proposal.filePath.contains('provider')) {
      fileType = 'state management';
      filePurpose = 'data and state handling';
    } else if (proposal.filePath.contains('service')) {
      fileType = 'service';
      filePurpose = 'business logic and external communication';
    } else if (proposal.filePath.contains('model')) {
      fileType = 'data model';
      filePurpose = 'data structure and validation';
    } else if (proposal.filePath.contains('util')) {
      fileType = 'utility';
      filePurpose = 'helper functions and common operations';
    } else if (proposal.filePath.contains('screen')) {
      fileType = 'screen';
      filePurpose = 'user interface screen';
    } else if (proposal.filePath.contains('router')) {
      fileType = 'routing';
      filePurpose = 'navigation and routing logic';
    } else {
      fileType = 'code';
      filePurpose = 'application logic';
    }

    // Files analyzed information
    String filesAnalyzedInfo = '';
    if (proposal.filesAnalyzed != null && proposal.filesAnalyzed!.isNotEmpty) {
      final fileCount = proposal.filesAnalyzed!.length;
      final uniqueExtensions = proposal.filesAnalyzed!
          .map((f) => f.split('.').last)
          .toSet()
          .join(', ');
      filesAnalyzedInfo =
          '\n\n📁 **Files Analyzed:** The ${proposal.aiType} AI analyzed $fileCount files (${uniqueExtensions}) to create this proposal. This ensures the change is well-informed and considers the broader codebase context.';
    }

    // AI-specific reasoning, impact, urgency, risks, and future intent
    String aiReasoning = '';
    String expectedImpact = '';
    String aiFutureIntent = '';
    String urgency = '';
    String risks = '';
    List<String> keyPoints = [];

    switch (proposal.aiType.toLowerCase()) {
      case 'imperium':
        aiReasoning =
            'The Imperium AI analyzed system performance and identified an opportunity to improve $filePurpose.';
        expectedImpact =
            'Enhances system reliability, performance, or maintainability.';
        aiFutureIntent =
            'Aims to create a more robust and scalable system for future enhancements.';
        urgency =
            'Addressing this now will prevent technical debt and future bottlenecks.';
        risks = 'Minimal risk, but regression testing is recommended.';
        keyPoints = [
          'System-level improvement',
          'Focus on reliability and scalability',
          'Prevents future issues',
        ];
        break;
      case 'guardian':
        aiReasoning =
            'The Guardian AI detected potential security or stability issues in the $filePurpose.';
        expectedImpact = 'Improves security, error handling, or code quality.';
        aiFutureIntent =
            'Prevents vulnerabilities and ensures long-term system safety.';
        urgency = 'Timely fix reduces risk of exploitation or instability.';
        risks = 'Possible stricter validation may affect edge cases.';
        keyPoints = [
          'Security/stability focus',
          'Reduces risk of future incidents',
          'May require user testing',
        ];
        break;
      case 'sandbox':
        aiReasoning =
            'The Sandbox AI experimented with new approaches to improve the $filePurpose.';
        expectedImpact =
            'Introduces new features or experimental improvements.';
        aiFutureIntent =
            'Learns from this experiment to apply successful patterns in future innovations.';
        urgency = 'Experimenting now enables rapid iteration and learning.';
        risks = 'Experimental: may introduce instability or require rollback.';
        keyPoints = [
          'Experimental/innovative',
          'Potential for high reward',
          'Monitor for regressions',
        ];
        break;
      case 'conquest':
        aiReasoning =
            'The Conquest AI identified user experience improvements for the $filePurpose.';
        expectedImpact =
            'Enhances user interaction, accessibility, or visual design.';
        aiFutureIntent =
            'Continuously refines user experience and sets a foundation for future usability upgrades.';
        urgency = 'Improving UX now increases user satisfaction and retention.';
        risks = 'UI changes may require user adaptation.';
        keyPoints = [
          'User experience focus',
          'Accessibility and design improvements',
          'May impact user workflows',
        ];
        break;
      default:
        aiReasoning =
            'The ${proposal.aiType} AI analyzed the $filePurpose and identified potential improvements.';
        expectedImpact =
            'Enhances functionality, performance, or code quality.';
        aiFutureIntent =
            'Leads to more maintainable and adaptable code in the future.';
        urgency = 'Recommended to keep codebase healthy and up-to-date.';
        risks = 'Standard risk of code change; review recommended.';
        keyPoints = ['General improvement', 'Maintainability and adaptability'];
    }

    // Improvement type specific details
    String improvementDetails = '';
    switch (proposal.improvementType.toLowerCase()) {
      case 'performance':
        improvementDetails =
            'Performance optimization: makes the code run faster or use fewer resources.';
        break;
      case 'security':
        improvementDetails =
            'Security enhancement: protects against vulnerabilities or improves data safety.';
        break;
      case 'bugfix':
        improvementDetails =
            'Bug fix: resolves an issue that could cause problems in the application.';
        break;
      case 'refactor':
        improvementDetails =
            'Refactor: improves readability, maintainability, or structure.';
        break;
      case 'feature':
        improvementDetails = 'Feature: adds new functionality or capabilities.';
        break;
      case 'system':
        improvementDetails =
            'System improvement: enhances system-level functionality, integration, or architecture.';
        break;
      default:
        improvementDetails =
            'General improvement: enhances overall quality and functionality.';
    }

    // Confidence level explanation
    String confidenceExplanation = '';
    final confidence = proposal.confidence ?? 0.5;
    if (confidence >= 0.8) {
      confidenceExplanation =
          'The AI is highly confident this change will be beneficial.';
    } else if (confidence >= 0.6) {
      confidenceExplanation =
          'The AI is moderately confident this change will improve the code.';
    } else {
      confidenceExplanation =
          'The AI suggests this change but recommends careful review before applying.';
    }

    return '''
**${proposal.aiType} AI Proposal**

**File:** ${proposal.filePath.split('/').last}
**Type:** $fileType ($filePurpose)
**Change:** $changeType

$aiReasoning

**Expected Impact:** $expectedImpact
**AI Future Intent:** $aiFutureIntent
**Urgency:** $urgency
**Risks:** $risks

**Key Points:**
${keyPoints.map((point) => '• $point').join('\n')}

**Improvement Type:** ${proposal.improvementType}
**Confidence:** ${(proposal.confidence ?? 0.5) * 100}%$filesAnalyzedInfo

**Code Changes:**
\`\`\`diff
${proposal.oldCode.isNotEmpty ? '- ${proposal.oldCode.split('\n').join('\n- ')}' : ''}
${proposal.newCode.isNotEmpty ? '+ ${proposal.newCode.split('\n').join('\n+ ')}' : ''}
\`\`\`
''';
  }

  String _getAIRationale(AIProposal proposal) {
    // If the proposal has a rationale or chain-of-thought field in the future, use it.
    // For now, use the AI Reasoning and key points from the description logic.
    String aiReasoning = '';
    List<String> keyPoints = [];
    switch (proposal.aiType.toLowerCase()) {
      case 'imperium':
        aiReasoning =
            'The Imperium AI systematically analyzed the system, identified bottlenecks, and prioritized this change based on its impact on reliability and scalability.';
        keyPoints = [
          'Analyzed system logs and performance metrics',
          'Detected recurring issues or inefficiencies',
          'Prioritized based on long-term system health',
        ];
        break;
      case 'guardian':
        aiReasoning =
            'The Guardian AI scanned for vulnerabilities, reviewed recent incidents, and determined this change would most effectively improve security and stability.';
        keyPoints = [
          'Reviewed security logs and error reports',
          'Identified weak points in validation or error handling',
          'Chose this fix to proactively prevent future incidents',
        ];
        break;
      case 'sandbox':
        aiReasoning =
            'The Sandbox AI generated and tested multiple experimental solutions, selecting this one for its potential to drive innovation and learning.';
        keyPoints = [
          'Explored alternative approaches',
          'Tested outcomes in a safe environment',
          'Selected the most promising result for real-world use',
        ];
        break;
      case 'conquest':
        aiReasoning =
            'The Conquest AI gathered user feedback, analyzed interaction patterns, and proposed this change to maximize user satisfaction and accessibility.';
        keyPoints = [
          'Collected and analyzed user feedback',
          'Identified pain points in the user journey',
          'Designed this change to address top user needs',
        ];
        break;
      default:
        aiReasoning =
            'The AI used a combination of code analysis, historical data, and best practices to generate this proposal.';
        keyPoints = [
          'Analyzed code structure and history',
          'Compared with best practices',
          'Generated proposal based on likely impact',
        ];
    }
    final buffer = StringBuffer();
    buffer.writeln(aiReasoning);
    buffer.writeln();
    buffer.writeln('**Chain of Thought:**');
    for (final point in keyPoints) {
      buffer.writeln('- $point');
    }
    return buffer.toString();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      appBar: AppBar(
        title: const Text(
          'System Expansion',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1a365d), // Dark blue
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              Provider.of<ProposalProvider>(
                context,
                listen: false,
              ).fetchUserReadyProposals();
            },
          ),
        ],
      ),
      body: Consumer<ProposalProvider>(
        builder: (context, provider, child) {
          final proposals = _getFilteredProposals(provider);

          return Column(
            children: [
              // Proposals List
              Expanded(
                child:
                    proposals.isEmpty
                        ? _buildEmptyState()
                        : FadeTransition(
                          opacity: _fadeController,
                          child: SlideTransition(
                            position: Tween<Offset>(
                              begin: const Offset(0, 0.1),
                              end: Offset.zero,
                            ).animate(_slideController),
                            child: ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: proposals.length,
                              itemBuilder: (context, index) {
                                final proposal = proposals[index];
                                return _buildProposalCard(proposal, provider);
                              },
                            ),
                          ),
                        ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.inbox_outlined, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No proposals found',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Proposals will appear here when AI systems generate suggestions',
            style: TextStyle(color: Colors.grey[500]),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildProposalCard(AIProposal proposal, ProposalProvider provider) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _getAITypeColor(proposal.aiType).withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: _getAITypeColor(proposal.aiType),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    _getAITypeIcon(proposal.aiType),
                    color: Colors.white,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        proposal.aiType,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        proposal.filePath,
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getStatusColor(proposal.status),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    proposal.status.toString().split('.').last.toUpperCase(),
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

          // Content
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Improvement Type
                if (proposal.improvementType != 'general')
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      proposal.improvementType.toUpperCase(),
                      style: const TextStyle(
                        color: Colors.blue,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),

                const SizedBox(height: 8),

                // Confidence Indicator
                Row(
                  children: [
                    Icon(Icons.psychology, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text(
                      'AI Confidence:',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: LinearProgressIndicator(
                        value: (proposal.confidence ?? 0.5).clamp(0, 1),
                        backgroundColor: Colors.grey[300],
                        valueColor: AlwaysStoppedAnimation<Color>(
                          _getConfidenceColor(
                            (proposal.confidence ?? 0.5).clamp(0, 1),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Color-coded badge
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: _getConfidenceColor(
                          (proposal.confidence ?? 0.5).clamp(0, 1),
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${(((proposal.confidence ?? 0.5).clamp(0, 1)) * 100).toInt()}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                // Enhanced Description Section - Hide during testing
                if (proposal.status != ProposalStatus.testing)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Enhanced Description
                      if (proposal.description != null && proposal.description!.isNotEmpty)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Enhanced Proposal Description',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.green[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.green[200]!),
                              ),
                              child: Text(
                                proposal.description!,
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.green[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      
                      // AI Learning Summary
                      if (proposal.aiLearningSummary != null && proposal.aiLearningSummary!.isNotEmpty)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'What the AI Has Learned',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.purple[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.purple[200]!),
                              ),
                              child: Text(
                                proposal.aiLearningSummary!,
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.purple[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      
                      // Change Type and Scope
                      if (proposal.changeType != null || proposal.changeScope != null)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Change Details',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.orange[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.orange[200]!),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  if (proposal.changeType != null)
                                    Text(
                                      'Type: ${proposal.changeType!.toUpperCase()}',
                                      style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.orange[800],
                                      ),
                                    ),
                                  if (proposal.changeScope != null) ...[
                                    const SizedBox(height: 4),
                                    Text(
                                      'Scope: ${proposal.changeScope!.toUpperCase()}',
                                      style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.orange[800],
                                      ),
                                    ),
                                  ],
                                  if (proposal.expectedImpact != null) ...[
                                    const SizedBox(height: 8),
                                    Text(
                                      'Expected Impact:',
                                      style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.orange[800],
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      proposal.expectedImpact!,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.orange[800],
                                        height: 1.4,
                                      ),
                                    ),
                                  ],
                                  if (proposal.riskAssessment != null) ...[
                                    const SizedBox(height: 8),
                                    Text(
                                      'Risk Assessment:',
                                      style: TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.w600,
                                        color: Colors.orange[800],
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      proposal.riskAssessment!,
                                      style: TextStyle(
                                        fontSize: 13,
                                        color: Colors.orange[800],
                                        height: 1.4,
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      
                      // Application Response (if applied)
                      if (proposal.applicationResponse != null && proposal.applicationResponse!.isNotEmpty)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Application Response',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.green[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.green[200]!),
                              ),
                              child: Text(
                                proposal.applicationResponse!,
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.green[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      
                      // Post Application Analysis (if applied)
                      if (proposal.postApplicationAnalysis != null && proposal.postApplicationAnalysis!.isNotEmpty)
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Post-Application Analysis',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.blue[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.blue[200]!),
                              ),
                              child: Text(
                                proposal.postApplicationAnalysis!,
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.blue[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      
                      // Fallback to old description if no enhanced description
                      if ((proposal.description == null || proposal.description!.isEmpty) &&
                          (proposal.aiLearningSummary == null || proposal.aiLearningSummary!.isEmpty))
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Proposal Description',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.blue[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.blue[200]!),
                              ),
                              child: Text(
                                _generateDescription(proposal),
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.blue[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            // AI Rationale Section
                            const Text(
                              'AI Rationale',
                              style: TextStyle(
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.yellow[50],
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: Colors.yellow[200]!),
                              ),
                              child: Text(
                                _getAIRationale(proposal),
                                style: TextStyle(
                                  fontSize: 13,
                                  color: Colors.brown[800],
                                  height: 1.4,
                                ),
                              ),
                            ),
                            const SizedBox(height: 12),
                          ],
                        ),
                      const SizedBox(height: 12),
                      // Before/After Code Comparison
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Before
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Before',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.red,
                                  ),
                                ),
                                Container(
                                  margin: const EdgeInsets.only(
                                    top: 4,
                                    right: 4,
                                  ),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: Colors.grey[100],
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(color: Colors.red[200]!),
                                  ),
                                  child: SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Text(
                                      proposal.oldCode.trim().isEmpty
                                          ? '// No previous code'
                                          : proposal.oldCode,
                                      style: const TextStyle(
                                        fontFamily: 'monospace',
                                        fontSize: 12,
                                        color: Colors.red,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          // After
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'After',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green,
                                  ),
                                ),
                                Container(
                                  margin: const EdgeInsets.only(
                                    top: 4,
                                    left: 4,
                                  ),
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(
                                    color: Colors.grey[100],
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                      color: Colors.green[200]!,
                                    ),
                                  ),
                                  child: SingleChildScrollView(
                                    scrollDirection: Axis.horizontal,
                                    child: Text(
                                      proposal.newCode.trim().isEmpty
                                          ? '// No new code'
                                          : proposal.newCode,
                                      style: const TextStyle(
                                        fontFamily: 'monospace',
                                        fontSize: 12,
                                        color: Colors.green,
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      // Feedback UI
                      Row(
                        children: [
                          const Text(
                            'Your Feedback:',
                            style: TextStyle(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(width: 8),
                          IconButton(
                            icon: const Icon(
                              Icons.thumb_up,
                              color: Colors.green,
                            ),
                            tooltip: 'AI reasoning is helpful',
                            onPressed: () {
                              print(
                                '👍 Feedback: User liked proposal ${proposal.id}',
                              );
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Thank you for your feedback!'),
                                ),
                              );
                            },
                          ),
                          IconButton(
                            icon: const Icon(
                              Icons.thumb_down,
                              color: Colors.red,
                            ),
                            tooltip: 'AI reasoning is not helpful',
                            onPressed: () {
                              print(
                                '👎 Feedback: User disliked proposal ${proposal.id}',
                              );
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('Thank you for your feedback!'),
                                ),
                              );
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      TextField(
                        decoration: InputDecoration(
                          labelText: 'Additional comments (optional)',
                          border: OutlineInputBorder(),
                          isDense: true,
                        ),
                        minLines: 1,
                        maxLines: 3,
                        onSubmitted: (value) {
                          if (value.trim().isNotEmpty) {
                            print(
                              '📝 Feedback comment for proposal ${proposal.id}: $value',
                            );
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Thank you for your feedback!'),
                              ),
                            );
                          }
                        },
                      ),
                      const SizedBox(height: 12),
                      // Documentation/Reference Links
                      if (proposal.tags != null &&
                          proposal.tags!.any(
                            (tag) => tag.startsWith('http'),
                          )) ...[
                        const Text(
                          'References:',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        const SizedBox(height: 4),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children:
                              proposal.tags!
                                  .where((tag) => tag.startsWith('http'))
                                  .map(
                                    (url) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: InkWell(
                                        onTap: () async {
                                          // ignore: deprecated_member_use
                                          await launchUrl(Uri.parse(url));
                                        },
                                        child: Text(
                                          url,
                                          style: const TextStyle(
                                            color: Colors.blue,
                                            decoration:
                                                TextDecoration.underline,
                                            fontSize: 13,
                                          ),
                                        ),
                                      ),
                                    ),
                                  )
                                  .toList(),
                        ),
                        const SizedBox(height: 12),
                      ],
                    ],
                  ),

                // Testing Status Indicator
                if (proposal.status == ProposalStatus.testing)
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue[200]!),
                    ),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Colors.blue[700]!,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Testing in Progress',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 14,
                                  color: Colors.blue,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                'The proposal is being tested to ensure it works correctly...',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.blue[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                // Code Preview
                if (proposal.oldCode.isNotEmpty || proposal.newCode.isNotEmpty)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Code Changes',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (proposal.oldCode.isNotEmpty) ...[
                              const Text(
                                'Before:',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                  color: Colors.red,
                                ),
                              ),
                              Text(
                                proposal.oldCode,
                                style: const TextStyle(fontSize: 12),
                                maxLines: 3,
                                overflow: TextOverflow.ellipsis,
                              ),
                              const SizedBox(height: 8),
                            ],
                            if (proposal.newCode.isNotEmpty) ...[
                              const Text(
                                'After:',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 12,
                                  color: Colors.green,
                                ),
                              ),
                              Text(
                                proposal.newCode,
                                style: const TextStyle(fontSize: 12),
                                maxLines: 3,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),

                const SizedBox(height: 16),

                // Action Buttons - For pending and test-passed proposals
                if (proposal.status == ProposalStatus.pending ||
                    proposal.status == ProposalStatus.testPassed)
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () async {
                            await provider.approveProposal(proposal.id);
                            // Remove proposal from UI immediately
                            if (mounted) {
                              setState(
                                () {},
                              ); // Triggers rebuild, proposals getter will update
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Row(
                                    children: [
                                      const Icon(
                                        Icons.check_circle,
                                        color: Colors.white,
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          '✅ Proposal applied to ${proposal.aiType} backend!',
                                          style: const TextStyle(
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  backgroundColor: Colors.green,
                                  duration: const Duration(seconds: 4),
                                  behavior: SnackBarBehavior.floating,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                ),
                              );
                              // If all proposals are cleared, refresh
                              final proposals = _getFilteredProposals(provider);
                              if (proposals.isEmpty) {
                                await provider.fetchAllProposals();
                                setState(() {});
                              }
                            }
                          },
                          icon: const Icon(Icons.check, size: 18),
                          label: const Text('Approve'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => provider.rejectProposal(proposal.id),
                          icon: const Icon(Icons.close, size: 18),
                          label: const Text('Reject'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                // Testing Status Message
                if (proposal.status == ProposalStatus.testing)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue[200]!),
                    ),
                    child: const Text(
                      'This proposal is currently being tested',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.blue,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),

                // Test Passed Success Message
                if (proposal.status == ProposalStatus.testPassed)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    decoration: BoxDecoration(
                      color: Colors.green[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green[200]!),
                    ),
                    child: const Text(
                      '✅ Tests passed! This proposal is ready for approval',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.w500,
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
