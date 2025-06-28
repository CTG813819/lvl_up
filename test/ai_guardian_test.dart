import 'package:flutter_test/flutter_test.dart';
import '../lib/mechanicum.dart';
import 'package:the_codex/mission_widget.dart';

void main() {
  group('AIGuardian Tests', () {
    late Mechanicum aiGuardian;

    setUp(() {
      aiGuardian = Mechanicum();
    });

    tearDown(() {
      aiGuardian.dispose();
    });

    test('should initialize correctly', () {
      expect(aiGuardian.isAIActive, false);
      expect(aiGuardian.isRunning, false);
    });

    test('should log repairs correctly', () {
      aiGuardian.logRepair(
        'Test Issue',
        'Test Action',
        missionId: 'test-mission',
      );

      final summary = aiGuardian.getRepairLogSummary();
      expect(summary['Test Issue'], 1);
    });

    test('should detect known issues', () {
      aiGuardian.logRepair(
        'Duplicate ID',
        'Fixed duplicate',
        missionId: 'mission-1',
      );

      expect(aiGuardian.wouldCauseKnownIssue('Duplicate ID'), true);
      expect(
        aiGuardian.wouldCauseKnownIssue('Duplicate ID', missionId: 'mission-1'),
        true,
      );
      expect(aiGuardian.wouldCauseKnownIssue('Different Issue'), false);
    });

    test('should start and stop continuous health check', () async {
      bool healthCheckCalled = false;

      aiGuardian.startContinuousHealthCheck(() async {
        healthCheckCalled = true;
      }, interval: const Duration(milliseconds: 100));

      expect(aiGuardian.isRunning, true);

      // Wait for health check to be called
      await Future.delayed(const Duration(milliseconds: 150));

      aiGuardian.stopContinuousHealthCheck();

      expect(aiGuardian.isRunning, false);
      expect(healthCheckCalled, true);
    });

    test('should perform immediate health check', () async {
      bool immediateCheckCalled = false;

      await aiGuardian.performImmediateHealthCheck(() async {
        immediateCheckCalled = true;
      });

      expect(immediateCheckCalled, true);
    });

    test('should handle errors gracefully', () async {
      aiGuardian.startContinuousHealthCheck(() async {
        throw Exception('Test error');
      }, interval: const Duration(milliseconds: 100));

      // Should not crash
      await Future.delayed(const Duration(milliseconds: 150));

      expect(aiGuardian.isRunning, true);
    });
  });
}
