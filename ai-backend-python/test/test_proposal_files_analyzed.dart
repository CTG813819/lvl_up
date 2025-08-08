import 'package:flutter_test/flutter_test.dart';
import '../lib/models/ai_proposal.dart';

void main() {
  group('AIProposal files_analyzed field', () {
    test('should parse files_analyzed from backend JSON', () {
      final json = {
        'id': 'test-123',
        'ai_type': 'Imperium',
        'file_path': 'lib/test.dart',
        'code_before': 'old code',
        'code_after': 'new code',
        'timestamp': '2024-01-01T00:00:00Z',
        'status': 'pending',
        'files_analyzed': [
          'lib/file1.dart',
          'lib/file2.dart',
          'lib/file3.dart',
        ],
      };

      final proposal = AIProposal.fromBackend(json);

      expect(proposal.filesAnalyzed, isNotNull);
      expect(proposal.filesAnalyzed!.length, equals(3));
      expect(proposal.filesAnalyzed!, contains('lib/file1.dart'));
      expect(proposal.filesAnalyzed!, contains('lib/file2.dart'));
      expect(proposal.filesAnalyzed!, contains('lib/file3.dart'));
    });

    test('should handle null files_analyzed', () {
      final json = {
        'id': 'test-123',
        'ai_type': 'Guardian',
        'file_path': 'lib/test.dart',
        'code_before': 'old code',
        'code_after': 'new code',
        'timestamp': '2024-01-01T00:00:00Z',
        'status': 'pending',
      };

      final proposal = AIProposal.fromBackend(json);

      expect(proposal.filesAnalyzed, isNull);
    });

    test('should serialize files_analyzed to JSON', () {
      final proposal = AIProposal(
        id: 'test-123',
        aiType: 'Sandbox',
        filePath: 'lib/test.dart',
        oldCode: 'old code',
        newCode: 'new code',
        timestamp: DateTime.parse('2024-01-01T00:00:00Z'),
        filesAnalyzed: ['lib/file1.dart', 'lib/file2.dart'],
      );

      final json = proposal.toJson();

      expect(json['filesAnalyzed'], isNotNull);
      expect(json['filesAnalyzed'], isA<List<String>>());
      expect(json['filesAnalyzed'].length, equals(2));
      expect(json['filesAnalyzed'], contains('lib/file1.dart'));
      expect(json['filesAnalyzed'], contains('lib/file2.dart'));
    });
  });
}
