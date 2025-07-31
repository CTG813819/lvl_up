enum ProposalStatus {
  pending,
  approved,
  testing,
  rejected,
  applied,
  testPassed,
  testFailed,
}

class AIProposal {
  final String id;
  final String aiType;
  final String filePath;
  final String oldCode;
  final String newCode;
  final DateTime timestamp;
  ProposalStatus status = ProposalStatus.pending;
  final String? testStatus;
  final String? testOutput;
  final String? description;
  final List<String>? tags;
  final String improvementType;
  final double? confidence;
  final List<String>? filesAnalyzed;
  
  /// Enhanced fields
  final String? aiLearningSummary;
  final String? changeType;
  final String? changeScope;
  final List<String>? affectedComponents;
  final List<String>? learningSources;
  final String? expectedImpact;
  final String? riskAssessment;
  final String? applicationResponse;
  final String? applicationResult;
  final String? postApplicationAnalysis;

  AIProposal({
    required this.id,
    required this.aiType,
    required this.filePath,
    required this.oldCode,
    required this.newCode,
    required this.timestamp,
    this.status = ProposalStatus.pending,
    this.testStatus,
    this.testOutput,
    this.description,
    this.tags,
    this.improvementType = 'general',
    this.confidence,
    this.filesAnalyzed,
    /// Enhanced fields
    this.aiLearningSummary,
    this.changeType,
    this.changeScope,
    this.affectedComponents,
    this.learningSources,
    this.expectedImpact,
    this.riskAssessment,
    this.applicationResponse,
    this.applicationResult,
    this.postApplicationAnalysis,
  });

  factory AIProposal.fromBackend(Map<String, dynamic> json) {
    /// Handle both 'id' and '_id' fields from backend
    final id = json['id']?.toString() ?? json['_id']?.toString() ?? 'unknown';

    return AIProposal(
      id: id,
      aiType:
          json['ai_type']?.toString() ??
          json['aiType']?.toString() ??
          'Unknown',
      filePath:
          json['file_path']?.toString() ?? json['filePath']?.toString() ?? '',
      oldCode:
          json['code_before']?.toString() ??
          json['codeBefore']?.toString() ??
          '',
      newCode:
          json['code_after']?.toString() ?? json['codeAfter']?.toString() ?? '',
      timestamp:
          json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString()) ??
                  DateTime.now()
              : json['createdAt'] != null
              ? DateTime.tryParse(json['createdAt'].toString()) ??
                  DateTime.now()
              : DateTime.now(),
      status: _statusFromString(json['status']?.toString()),
      testStatus:
          json['test_status']?.toString() ?? json['testStatus']?.toString(),
      testOutput:
          json['test_output']?.toString() ?? json['testOutput']?.toString(),
      description: json['description']?.toString(),
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      improvementType:
          json['improvement_type']?.toString() ??
          json['improvementType']?.toString() ??
          'general',
      confidence: json['confidence']?.toDouble(),
      filesAnalyzed:
          json['files_analyzed'] != null
              ? List<String>.from(json['files_analyzed'])
              : null,
      /// Enhanced fields
      aiLearningSummary: json['ai_learning_summary']?.toString(),
      changeType: json['change_type']?.toString(),
      changeScope: json['change_scope']?.toString(),
      affectedComponents: json['affected_components'] != null
          ? List<String>.from(json['affected_components'])
          : null,
      learningSources: json['learning_sources'] != null
          ? List<String>.from(json['learning_sources'])
          : null,
      expectedImpact: json['expected_impact']?.toString(),
      riskAssessment: json['risk_assessment']?.toString(),
      applicationResponse: json['application_response']?.toString(),
      applicationResult: json['application_result']?.toString(),
      postApplicationAnalysis: json['post_application_analysis']?.toString(),
    );
  }

  factory AIProposal.fromJson(Map<String, dynamic> json) {
    return AIProposal(
      id: json['id'] ?? '',
      aiType: json['aiType'] ?? '',
      filePath: json['filePath'] ?? '',
      oldCode: json['oldCode'] ?? '',
      newCode: json['newCode'] ?? '',
      timestamp: DateTime.parse(json['timestamp']),
      status: _statusFromString(json['status']),
      testStatus: json['testStatus'],
      testOutput: json['testOutput'],
      description: json['description'],
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      improvementType: json['improvementType'] ?? 'general',
      confidence: json['confidence']?.toDouble(),
      filesAnalyzed:
          json['filesAnalyzed'] != null
              ? List<String>.from(json['filesAnalyzed'])
              : null,
      /// Enhanced fields
      aiLearningSummary: json['aiLearningSummary']?.toString(),
      changeType: json['changeType']?.toString(),
      changeScope: json['changeScope']?.toString(),
      affectedComponents: json['affectedComponents'] != null
          ? List<String>.from(json['affectedComponents'])
          : null,
      learningSources: json['learningSources'] != null
          ? List<String>.from(json['learningSources'])
          : null,
      expectedImpact: json['expectedImpact']?.toString(),
      riskAssessment: json['riskAssessment']?.toString(),
      applicationResponse: json['applicationResponse']?.toString(),
      applicationResult: json['applicationResult']?.toString(),
      postApplicationAnalysis: json['postApplicationAnalysis']?.toString(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'aiType': aiType,
      'filePath': filePath,
      'oldCode': oldCode,
      'newCode': newCode,
      'timestamp': timestamp.toIso8601String(),
      'status': _statusToString(status),
      'testStatus': testStatus,
      'testOutput': testOutput,
      'description': description,
      'tags': tags,
      'improvementType': improvementType,
      'confidence': confidence,
      'filesAnalyzed': filesAnalyzed,
      /// Enhanced fields
      'aiLearningSummary': aiLearningSummary,
      'changeType': changeType,
      'changeScope': changeScope,
      'affectedComponents': affectedComponents,
      'learningSources': learningSources,
      'expectedImpact': expectedImpact,
      'riskAssessment': riskAssessment,
      'applicationResponse': applicationResponse,
      'applicationResult': applicationResult,
      'postApplicationAnalysis': postApplicationAnalysis,
    };
  }

  static ProposalStatus _statusFromString(String? s) {
    switch (s) {
      case 'approved':
        return ProposalStatus.approved;
      case 'accepted':
        /// Backend sets accepted after successful testing
        return ProposalStatus.testPassed;
      case 'testing':
        return ProposalStatus.testing;
      case 'rejected':
        return ProposalStatus.rejected;
      case 'applied':
        return ProposalStatus.applied;
      case 'test-passed':
        return ProposalStatus.testPassed;
      case 'test-failed':
        return ProposalStatus.testFailed;
      case 'pending':
        return ProposalStatus.pending;
      default:
        return ProposalStatus.pending;
    }
  }

  static String _statusToString(ProposalStatus status) {
    switch (status) {
      case ProposalStatus.approved:
        return 'approved';
      case ProposalStatus.testing:
        return 'testing';
      case ProposalStatus.rejected:
        return 'rejected';
      case ProposalStatus.applied:
        return 'applied';
      case ProposalStatus.testPassed:
        return 'test-passed';
      case ProposalStatus.testFailed:
        return 'test-failed';
      default:
        return 'pending';
    }
  }

  /// For Guardian suggestions
  factory AIProposal.fromGuardian(Map<String, dynamic> json) {
    return AIProposal(
      id:
          json['id']?.toString() ??
          'guardian_ 2${DateTime.now().millisecondsSinceEpoch}',
      aiType: 'Guardian',
      filePath: json['file_path']?.toString() ?? '',
      oldCode: json['code_before']?.toString() ?? '',
      newCode: json['code_after']?.toString() ?? '',
      timestamp:
          json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString()) ??
                  DateTime.now()
              : DateTime.now(),
      status: _statusFromString(json['status']?.toString()),
      description: json['description']?.toString(),
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      improvementType: json['improvement_type']?.toString() ?? 'general',
      confidence: json['confidence']?.toDouble(),
      filesAnalyzed:
          json['filesAnalyzed'] != null
              ? List<String>.from(json['filesAnalyzed'])
              : null,
      /// Enhanced fields
      aiLearningSummary: json['ai_learning_summary']?.toString(),
      changeType: json['change_type']?.toString(),
      changeScope: json['change_scope']?.toString(),
      affectedComponents: json['affected_components'] != null
          ? List<String>.from(json['affected_components'])
          : null,
      learningSources: json['learning_sources'] != null
          ? List<String>.from(json['learning_sources'])
          : null,
      expectedImpact: json['expected_impact']?.toString(),
      riskAssessment: json['risk_assessment']?.toString(),
      applicationResponse: json['application_response']?.toString(),
      applicationResult: json['application_result']?.toString(),
      postApplicationAnalysis: json['post_application_analysis']?.toString(),
    );
  }

  /// For Imperium proposals
  factory AIProposal.fromImperium(Map<String, dynamic> json) {
    return AIProposal(
      id:
          json['id']?.toString() ??
          'imperium_${DateTime.now().millisecondsSinceEpoch}',
      aiType: 'Imperium',
      filePath: json['file_path']?.toString() ?? '',
      oldCode: json['code_before']?.toString() ?? '',
      newCode: json['code_after']?.toString() ?? '',
      timestamp:
          json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString()) ??
                  DateTime.now()
              : DateTime.now(),
      status: _statusFromString(json['status']?.toString()),
      description: json['description']?.toString(),
      tags: json['tags'] != null ? List<String>.from(json['tags']) : null,
      improvementType: json['improvement_type']?.toString() ?? 'general',
      confidence: json['confidence']?.toDouble(),
      filesAnalyzed:
          json['filesAnalyzed'] != null
              ? List<String>.from(json['filesAnalyzed'])
              : null,
      /// Enhanced fields
      aiLearningSummary: json['ai_learning_summary']?.toString(),
      changeType: json['change_type']?.toString(),
      changeScope: json['change_scope']?.toString(),
      affectedComponents: json['affected_components'] != null
          ? List<String>.from(json['affected_components'])
          : null,
      learningSources: json['learning_sources'] != null
          ? List<String>.from(json['learning_sources'])
          : null,
      expectedImpact: json['expected_impact']?.toString(),
      riskAssessment: json['risk_assessment']?.toString(),
      applicationResponse: json['application_response']?.toString(),
      applicationResult: json['application_result']?.toString(),
      postApplicationAnalysis: json['post_application_analysis']?.toString(),
    );
  }

  /// For Sandbox experiments
  factory AIProposal.fromSandbox(Map<String, dynamic> json) {
    return AIProposal(
      id:
          json['id']?.toString() ??
          'sandbox_${DateTime.now().millisecondsSinceEpoch}',
      aiType: 'Sandbox',
      filePath: json['name']?.toString() ?? '',
      oldCode: '', // Not provided
      newCode: '', // Not provided
      timestamp:
          json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString()) ??
                  DateTime.now()
              : DateTime.now(),
      status: _statusFromString(json['status']?.toString()),
      description: json['description']?.toString() ?? json['name']?.toString(),
      tags: null,
      improvementType: json['type']?.toString() ?? 'experiment',
      confidence: json['success_rate']?.toDouble(),
      filesAnalyzed:
          json['filesAnalyzed'] != null
              ? List<String>.from(json['filesAnalyzed'])
              : null,
      /// Enhanced fields
      aiLearningSummary: json['ai_learning_summary']?.toString(),
      changeType: json['change_type']?.toString(),
      changeScope: json['change_scope']?.toString(),
      affectedComponents: json['affected_components'] != null
          ? List<String>.from(json['affected_components'])
          : null,
      learningSources: json['learning_sources'] != null
          ? List<String>.from(json['learning_sources'])
          : null,
      expectedImpact: json['expected_impact']?.toString(),
      riskAssessment: json['risk_assessment']?.toString(),
      applicationResponse: json['application_response']?.toString(),
      applicationResult: json['application_result']?.toString(),
      postApplicationAnalysis: json['post_application_analysis']?.toString(),
    );
  }
}
