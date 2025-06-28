enum ProposalStatus { pending, approved, rejected, applied, testPassed, testFailed }

class AIProposal {
  final String id;
  final String aiType;
  final String filePath;
  final String oldCode;
  final String newCode;
  final DateTime timestamp;
  ProposalStatus status;
  final String? testStatus;
  final String? testOutput;

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
  });

  factory AIProposal.fromBackend(Map<String, dynamic> json) {
    return AIProposal(
      id: json['_id'],
      aiType: json['aiType'] ?? '',
      filePath: json['filePath'] ?? '',
      oldCode: json['codeBefore'] ?? '',
      newCode: json['codeAfter'] ?? '',
      timestamp: DateTime.parse(json['createdAt']),
      status: _statusFromString(json['status']),
      testStatus: json['testStatus'],
      testOutput: json['testOutput'],
    );
  }

  static ProposalStatus _statusFromString(String? s) {
    switch (s) {
      case 'approved':
        return ProposalStatus.approved;
      case 'rejected':
        return ProposalStatus.rejected;
      case 'applied':
        return ProposalStatus.applied;
      case 'test-passed':
        return ProposalStatus.testPassed;
      case 'test-failed':
        return ProposalStatus.testFailed;
      default:
        return ProposalStatus.pending;
    }
  }
} 