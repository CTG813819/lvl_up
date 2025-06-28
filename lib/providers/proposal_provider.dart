import 'dart:collection';
import 'package:flutter/material.dart';
import 'package:the_codex/main.dart';
import '../models/ai_proposal.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io';
import 'dart:async';
import 'package:provider/provider.dart';
import '../providers/ai_learning_provider.dart';
import '../services/notification_service.dart';
import 'package:flutter/foundation.dart';
import '../services/network_config.dart';

class ProposalProvider extends ChangeNotifier {
  final List<AIProposal> _proposals = [];
  late IO.Socket _socket;
  final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  // AI Learning integration
  AILearningProvider? _aiLearningProvider;

  // Use network configuration service
  static String get _backendUrl => NetworkConfig.backendUrl;
  
  // Public getter for backend URL
  static String get backendUrl => _backendUrl;

  // Mock mode for testing when backend is not available
  static const bool _useMockMode =
      false; // Set to false when backend is running

  UnmodifiableListView<AIProposal> get proposals {
    final seen = <String>{};
    final unique = <AIProposal>[];
    for (final p in _proposals) {
      final key = '${p.filePath}|${p.aiType}|${p.status}';
      if (!seen.contains(key)) {
        seen.add(key);
        unique.add(p);
      }
    }
    return UnmodifiableListView(unique);
  }

  List<AIProposal> get pendingProposals =>
      proposals.where((p) => p.status == ProposalStatus.pending).toList();

  ProposalProvider() {
    fetchProposals();
    _initSocket();
    _initNotifications();
  }

  Future<void> fetchProposals() async {
    print('[PROPOSAL_PROVIDER] 🔍 Fetching proposals from backend...');

    if (_useMockMode) {
      print(
        '[PROPOSAL_PROVIDER] 🎭 Using mock mode - creating sample proposals',
      );
      _createMockProposals();
      return;
    }

    final url = Uri.parse('$_backendUrl/api/proposals');
    print('[PROPOSAL_PROVIDER] 📡 Making request to: $url');

    try {
      print('[PROPOSAL_PROVIDER] ⏳ Sending HTTP GET request...');
      final response = await http
          .get(url)
          .timeout(
            const Duration(seconds: 10),
            onTimeout: () {
              print('[PROPOSAL_PROVIDER] ⏰ Request timed out after 10 seconds');
              throw TimeoutException(
                'Request timed out',
                const Duration(seconds: 10),
              );
            },
          );
      print('[PROPOSAL_PROVIDER] 📥 Backend response received');
      print('[PROPOSAL_PROVIDER] 📊 Response status: ${response.statusCode}');
      print('[PROPOSAL_PROVIDER] 📄 Response headers: ${response.headers}');

    if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Success response from backend');
        final responseBody = response.body;
        print(
          '[PROPOSAL_PROVIDER] 📝 Response body length: ${responseBody.length}',
        );
        print(
          '[PROPOSAL_PROVIDER] 📝 Response body preview: ${responseBody.substring(0, responseBody.length > 200 ? 200 : responseBody.length)}...',
        );

        final List data = jsonDecode(responseBody);
        print(
          '[PROPOSAL_PROVIDER] 📊 Parsed ${data.length} proposals from JSON',
        );

        if (data.isNotEmpty) {
          print('[PROPOSAL_PROVIDER] 📋 First proposal data: ${data.first}');
        }

      _proposals.clear();
        _proposals.addAll(
          data.map((json) {
            print(
              '[PROPOSAL_PROVIDER] 🔄 Converting proposal: ${json['_id']} - ${json['aiType']} - ${json['status']}',
            );
            return AIProposal.fromBackend(json);
          }),
        );

        final pendingCount =
            _proposals.where((p) => p.status == ProposalStatus.pending).length;
        final approvedCount =
            _proposals.where((p) => p.status == ProposalStatus.approved).length;
        final appliedCount =
            _proposals.where((p) => p.status == ProposalStatus.applied).length;

        print('[PROPOSAL_PROVIDER] 📊 Final proposal counts:');
        print('[PROPOSAL_PROVIDER]   - Total: ${_proposals.length}');
        print('[PROPOSAL_PROVIDER]   - Pending: $pendingCount');
        print('[PROPOSAL_PROVIDER]   - Approved: $approvedCount');
        print('[PROPOSAL_PROVIDER]   - Applied: $appliedCount');

        // Show notification if there are new pending proposals
        if (pendingCount > 0) {
          print(
            '[PROPOSAL_PROVIDER] 🔔 Showing notification for $pendingCount pending proposals',
          );
          _showNotification(
            '📋 Proposals Available',
            'You have $pendingCount pending AI proposals to review',
            channelId: 'ai_proposals',
          );
        } else {
          print(
            '[PROPOSAL_PROVIDER] ℹ️ No pending proposals to show notification for',
          );
        }

      notifyListeners();
        print('[PROPOSAL_PROVIDER] 📢 Notified listeners of proposal update');
      } else {
        print(
          '[PROPOSAL_PROVIDER] ❌ Failed to fetch proposals: ${response.statusCode}',
        );
        print('[PROPOSAL_PROVIDER] 📄 Full response body: ${response.body}');
        _showNotification(
          '⚠️ Backend Error',
          'Backend returned status ${response.statusCode}',
          channelId: 'ai_processes',
        );
      }
    } on SocketException catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Network connectivity error: $e');
      print(
        '[PROPOSAL_PROVIDER] 🌐 This usually means the backend server is not running or not accessible',
      );
      _showNotification(
        '🌐 Network Unreachable',
        'Cannot connect to AI backend. Please check your internet connection.',
        channelId: 'ai_processes',
      );
    } on TimeoutException catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Request timeout: $e');
      print(
        '[PROPOSAL_PROVIDER] ⏰ The backend server took too long to respond',
      );
      _showNotification(
        '⏱️ Connection Timeout',
        'Backend request timed out. The server may be busy.',
        channelId: 'ai_processes',
      );
    } catch (error) {
      print(
        '[PROPOSAL_PROVIDER] ❌ Unexpected error fetching proposals: $error',
      );
      print('[PROPOSAL_PROVIDER] 🔍 Error type: ${error.runtimeType}');
      print('[PROPOSAL_PROVIDER] 📚 Error details: ${error.toString()}');
      _showNotification(
        '❌ Connection Error',
        'Failed to connect to AI backend: ${error.toString().substring(0, 50)}...',
        channelId: 'ai_processes',
      );
    }
  }

  Future<void> approveProposal(String id) async {
    print('[PROPOSAL_PROVIDER] Approving proposal: $id');

    if (_useMockMode) {
      print('[PROPOSAL_PROVIDER] 🎭 Mock mode - approving proposal locally');
      final proposal = _proposals.firstWhere((p) => p.id == id);
      proposal.status = ProposalStatus.approved;
      _proposals.removeWhere((p) => p.id == id);
      notifyListeners();

      _showNotification(
        '✅ Mock Proposal Approved',
        'Proposal for ${proposal.filePath.split('/').last} has been approved (Mock Mode)',
        channelId: 'ai_proposals',
      );
      return;
    }

    try {
      final url = Uri.parse('$_backendUrl/api/proposals/$id/approve');
      print('[PROPOSAL_PROVIDER] 📡 Approving proposal at: $url');

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userFeedback': 'approved',
          'userFeedbackReason': 'User approved the proposal',
        }),
      ).timeout(const Duration(seconds: 15));

      print('[PROPOSAL_PROVIDER] 📥 Approval response: ${response.statusCode}');
      print('[PROPOSAL_PROVIDER] 📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Proposal approved successfully');
        
        // Remove the proposal from the list
        _proposals.removeWhere((p) => p.id == id);
        notifyListeners();

        // Get the proposal data for learning
        final proposal = _proposals.firstWhere((p) => p.id == id, orElse: () => 
          AIProposal(
            id: id,
            aiType: 'Unknown',
            filePath: 'unknown',
            oldCode: '',
            newCode: '',
            timestamp: DateTime.now(),
            status: ProposalStatus.approved,
          )
        );

        // Learn from the approval
        try {
          final learningProvider = Provider.of<AILearningProvider>(navigatorKey.currentContext!, listen: false);
          await learningProvider.learnFromProposal(proposal, 'approved', 'User approved the proposal');
          print('[PROPOSAL_PROVIDER] ✅ Learned from proposal approval');
        } catch (e) {
          print('[PROPOSAL_PROVIDER] ⚠️ Could not learn from approval: $e');
        }

        _showNotification(
          '✅ Proposal Approved',
          'Proposal has been approved and applied',
          channelId: 'ai_proposals',
        );
      } else if (response.statusCode == 403) {
        final errorMsg = jsonDecode(response.body)['error'] ?? 'Action blocked: AI is learning.';
        print('[PROPOSAL_PROVIDER] ⏸️ Approval blocked: $errorMsg');
        _showNotification(
          '⏸️ Action Blocked',
          errorMsg,
          channelId: 'ai_proposals',
        );
      } else {
        print('[PROPOSAL_PROVIDER] ❌ Failed to approve proposal: ${response.statusCode}');
        print('[PROPOSAL_PROVIDER] 📄 Error response: ${response.body}');
        _showNotification(
          '❌ Approval Failed',
          'Backend returned status ${response.statusCode}',
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error approving proposal: $e');
      _showNotification(
        '❌ Approval Error',
        'Failed to approve proposal: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_proposals',
      );
    }
  }

  Future<void> rejectProposal(String id) async {
    print('[PROPOSAL_PROVIDER] Rejecting proposal: $id');

    if (_useMockMode) {
      print('[PROPOSAL_PROVIDER] 🎭 Mock mode - rejecting proposal locally');
      final proposal = _proposals.firstWhere((p) => p.id == id);
      proposal.status = ProposalStatus.rejected;
      _proposals.removeWhere((p) => p.id == id);
      notifyListeners();

      _showNotification(
        '❌ Mock Proposal Rejected',
        'Proposal for ${proposal.filePath.split('/').last} has been rejected (Mock Mode)',
        channelId: 'ai_proposals',
      );
      return;
    }

    try {
      final url = Uri.parse('$_backendUrl/api/proposals/$id/reject');
      print('[PROPOSAL_PROVIDER] 📡 Rejecting proposal at: $url');

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userFeedback': 'rejected',
          'userFeedbackReason': 'User rejected the proposal',
        }),
      ).timeout(const Duration(seconds: 15));

      print('[PROPOSAL_PROVIDER] 📥 Rejection response: ${response.statusCode}');
      print('[PROPOSAL_PROVIDER] 📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Proposal rejected successfully');
        
        // Remove the proposal from the list
        _proposals.removeWhere((p) => p.id == id);
        notifyListeners();

        // Get the proposal data for learning
        final proposal = _proposals.firstWhere((p) => p.id == id, orElse: () => 
          AIProposal(
            id: id,
            aiType: 'Unknown',
            filePath: 'unknown',
            oldCode: '',
            newCode: '',
            timestamp: DateTime.now(),
            status: ProposalStatus.rejected,
          )
        );

        // Learn from the rejection
        try {
          final learningProvider = Provider.of<AILearningProvider>(navigatorKey.currentContext!, listen: false);
          await learningProvider.learnFromProposal(proposal, 'rejected', 'User rejected the proposal');
          print('[PROPOSAL_PROVIDER] ✅ Learned from proposal rejection');
        } catch (e) {
          print('[PROPOSAL_PROVIDER] ⚠️ Could not learn from rejection: $e');
        }

        _showNotification(
          '❌ Proposal Rejected',
          'Proposal has been rejected and removed',
          channelId: 'ai_proposals',
        );
      } else if (response.statusCode == 403) {
        final errorMsg = jsonDecode(response.body)['error'] ?? 'Action blocked: AI is learning.';
        print('[PROPOSAL_PROVIDER] ⏸️ Rejection blocked: $errorMsg');
        _showNotification(
          '⏸️ Action Blocked',
          errorMsg,
          channelId: 'ai_proposals',
        );
      } else {
        print('[PROPOSAL_PROVIDER] ❌ Failed to reject proposal: ${response.statusCode}');
        print('[PROPOSAL_PROVIDER] 📄 Error response: ${response.body}');
        _showNotification(
          '❌ Rejection Failed',
          'Backend returned status ${response.statusCode}',
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error rejecting proposal: $e');
      _showNotification(
        '❌ Rejection Error',
        'Failed to reject proposal: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_proposals',
      );
    }
  }

  Future<void> approveAllProposals() async {
    print('[PROPOSAL_PROVIDER] Approving all pending proposals');

    final pendingProposals =
        _proposals.where((p) => p.status == ProposalStatus.pending).toList();

    if (pendingProposals.isEmpty) {
      print('[PROPOSAL_PROVIDER] No pending proposals to approve');
      _showNotification(
        'ℹ️ No Pending Proposals',
        'There are no pending proposals to approve.',
        channelId: 'ai_proposals',
      );
      return;
    }

    print(
      '[PROPOSAL_PROVIDER] Found ${pendingProposals.length} pending proposals to approve',
    );

    if (_useMockMode) {
      print(
        '[PROPOSAL_PROVIDER] 🎭 Mock mode - approving all proposals locally',
      );
      _proposals.removeWhere((p) => p.status == ProposalStatus.pending);
      notifyListeners();

      _showNotification(
        '✅ All Mock Proposals Approved',
        '${pendingProposals.length} proposals have been approved (Mock Mode)',
        channelId: 'ai_proposals',
      );
      return;
    }

    int successCount = 0;
    int failureCount = 0;

    for (final proposal in pendingProposals) {
      try {
        print('[PROPOSAL_PROVIDER] Approving proposal: ${proposal.id}');

        final url = Uri.parse(
          '$_backendUrl/api/proposals/${proposal.id}/approve',
        );
        final response = await http.post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'feedbackReason': 'Approved via bulk approval'}),
        );

        if (response.statusCode == 200) {
          successCount++;
          print(
            '[PROPOSAL_PROVIDER] ✅ Successfully approved proposal: ${proposal.id}',
          );
        } else {
          failureCount++;
          print(
            '[PROPOSAL_PROVIDER] ❌ Failed to approve proposal: ${proposal.id} - Status: ${response.statusCode}',
          );
        }
      } catch (error) {
        failureCount++;
        print(
          '[PROPOSAL_PROVIDER] ❌ Error approving proposal: ${proposal.id} - $error',
        );
      }
    }

    // Refresh proposals to get updated status
    await fetchProposals();

    // Show summary notification
    if (successCount > 0) {
      _showNotification(
        '✅ Bulk Approval Complete',
        'Successfully approved $successCount proposals${failureCount > 0 ? ', $failureCount failed' : ''}',
        channelId: 'ai_proposals',
      );
    } else {
      _showNotification(
        '❌ Bulk Approval Failed',
        'Failed to approve any proposals. Please try individual approvals.',
        channelId: 'ai_proposals',
      );
    }

    print(
      '[PROPOSAL_PROVIDER] Bulk approval complete: $successCount successful, $failureCount failed',
    );
  }

  void _initNotifications() {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    final InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);
    _notifications.initialize(initializationSettings);
    print('[PROPOSAL_PROVIDER] Notifications initialized');
  }

  void _showNotification(
    String title,
    String body, {
    String? channelId,
    int? id,
  }) {
    final notificationId = id ?? DateTime.now().millisecondsSinceEpoch % 100000;
    final channel = channelId ?? 'ai_processes';

    _notifications.show(
      notificationId,
      title,
      body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          channel,
          'AI Processes',
          channelDescription: 'Notifications for AI proposal processing',
          importance: Importance.high,
          priority: Priority.high,
          showWhen: true,
          enableVibration: true,
          playSound: true,
          icon: '@mipmap/ic_launcher',
          color: const Color(0xFF2196F3),
          largeIcon: const DrawableResourceAndroidBitmap('@mipmap/ic_launcher'),
          styleInformation: BigTextStyleInformation(body),
        ),
      ),
    );
    print('[PROPOSAL_PROVIDER] 📱 Notification shown: $title - $body');
  }

  void _initSocket() {
    print('[PROPOSAL_PROVIDER] Initializing Socket.IO connection...');
    _socket = IO.io('$_backendUrl', <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': true,
    });

    _socket.onConnect((_) {
      print('[PROPOSAL_PROVIDER] ✅ Socket.IO connected to backend');
      _showNotification(
        '🔗 Connected to AI Backend',
        'Real-time AI updates are now active',
        channelId: 'ai_processes',
        id: 1, // Use fixed ID for connection status
      );
    });

    _socket.onDisconnect((_) {
      print('[PROPOSAL_PROVIDER] ⚠️ Socket.IO disconnected from backend');
    });

    _socket.onConnectError((error) {
      print('[PROPOSAL_PROVIDER] ❌ Socket.IO connection error: $error');
      _showNotification(
        '❌ Backend Connection Failed',
        'Cannot connect to AI backend: $error',
        channelId: 'ai_processes',
      );
    });

    _socket.on('proposal:created', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:created event');
      fetchProposals();
      final aiType = data['aiType'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      _showNotification(
        '🤖 New AI Proposal',
        '$aiType has created a new proposal for ${filePath.split('/').last}',
        channelId: 'ai_proposals',
      );
    });

    _socket.on('proposal:approved', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:approved event');
      fetchProposals();
      final filePath = data['filePath'] ?? 'unknown file';
      _showNotification(
        '✅ Proposal Approved',
        'Proposal for ${filePath.split('/').last} has been approved and will be tested',
        channelId: 'ai_proposals',
      );
    });

    _socket.on('proposal:rejected', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:rejected event');
      fetchProposals();
      final filePath = data['filePath'] ?? 'unknown file';
      _showNotification(
        '❌ Proposal Rejected',
        'Proposal for ${filePath.split('/').last} has been rejected',
        channelId: 'ai_proposals',
      );
    });

    _socket.on('proposal:applied', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:applied event');
      print('[PROPOSAL_PROVIDER] Applied proposal data: $data');
      fetchProposals();
      final filePath = data['filePath'] ?? 'unknown file';
      final aiType = data['aiType'] ?? 'AI';
      final prUrl = data['prUrl'] ?? '';
      _showNotification(
        '🚀 Proposal Applied to GitHub',
        '$aiType proposal for ${filePath.split('/').last} has been successfully applied and pushed to GitHub',
        channelId: 'ai_proposals',
      );
    });

    _socket.on('proposal:test-started', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:test-started event');
      final filePath = data['filePath'] ?? 'unknown file';
      _showNotification(
        '🧪 Running Tests',
        'Testing proposal for ${filePath.split('/').last}...',
        channelId: 'ai_tests',
      );
    });

    _socket.on('proposal:test-finished', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:test-finished event');
      print('[PROPOSAL_PROVIDER] Test finished data: $data');
      fetchProposals();
      final status = data['testStatus'] ?? '';
      final filePath = data['filePath'] ?? 'unknown file';
      final fileName = filePath.split('/').last;

      if (status == 'passed') {
        _showNotification(
          '✅ Tests Passed',
          'Tests for $fileName passed successfully. Proposal will be applied to GitHub.',
          channelId: 'ai_tests',
        );
      } else {
        _showNotification(
          '⚠️ Tests Completed',
          'Tests for $fileName completed with status: $status',
          channelId: 'ai_tests',
        );
      }
    });

    _socket.on('proposal:test-failed', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received proposal:test-failed event');
      print('[PROPOSAL_PROVIDER] Test failed data: $data');
      fetchProposals();
      final filePath = data['filePath'] ?? 'unknown file';
      final fileName = filePath.split('/').last;
      _showNotification(
        '❌ Tests Failed',
        'Tests for $fileName failed. Proposal will not be applied to GitHub.',
        channelId: 'ai_tests',
      );
    });

    _socket.on('apk:built', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received apk:built event');
      print('[PROPOSAL_PROVIDER] APK built data: $data');
      final apkUrl = data['apkUrl'] ?? '';
      _showNotification(
        '📱 New APK Available',
        'A new APK build is ready! Your app has been updated with the latest AI improvements.',
        channelId: 'apk_builds',
      );
    });

    _socket.on('ai:pull', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:pull event');
      final ai = data['ai'] ?? 'AI';
      final message = data['message'] ?? 'AI is working...';
      _showNotification('🔄 $ai Working', message, channelId: 'ai_processes');
    });

    _socket.on('ai:experiment-start', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:experiment-start event');
      final ai = data['ai'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      final message = data['message'] ?? 'AI is working...';
      final fileName = filePath.split('/').last;
      _showNotification(
        '🤖 $ai Working',
        '$message on $fileName',
        channelId: 'ai_processes',
      );
    });

    _socket.on('ai:experiment-complete', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:experiment-complete event');
      final ai = data['ai'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      final message = data['message'] ?? 'AI completed work';
      final fileName = filePath.split('/').last;
      _showNotification(
        '✅ $ai Complete',
        '$message for $fileName',
        channelId: 'ai_processes',
      );
    });

    _socket.on('backend:startup', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received backend:startup event');
      final message = data['message'] ?? 'Backend is starting up...';
      _showNotification(
        '🚀 AI Backend Starting',
        message,
        channelId: 'ai_processes',
      );
    });

    _socket.on('backend:code-pulled', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received backend:code-pulled event');
      final message = data['message'] ?? 'Code pulled successfully';
      _showNotification('📥 Code Updated', message, channelId: 'ai_processes');
    });

    _socket.on('backend:scan-complete', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received backend:scan-complete event');
      final fileCount = data['fileCount'] ?? 0;
      final message = data['message'] ?? 'Scan complete';
      _showNotification(
        '🔍 Code Scan Complete',
        '$message - $fileCount files found',
        channelId: 'ai_processes',
      );
    });

    _socket.on('ai:periodic-start', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:periodic-start event');
      final ai = data['ai'] ?? 'AI';
      final message = data['message'] ?? 'AI starting periodic work...';
      _showNotification(
        '🔄 $ai Periodic Job',
        message,
        channelId: 'ai_processes',
      );
    });

    _socket.on('ai:periodic-complete', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:periodic-complete event');
      final ai = data['ai'] ?? 'AI';
      final message = data['message'] ?? 'AI completed periodic work';
      _showNotification(
        '✅ $ai Job Complete',
        message,
        channelId: 'ai_processes',
      );
    });

    _socket.on('ai:periodic-error', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:periodic-error event');
      final ai = data['ai'] ?? 'AI';
      final message = data['message'] ?? 'AI encountered an error';
      _showNotification('❌ $ai Error', message, channelId: 'ai_processes');
    });

    _socket.on('ai:learning-updated', (data) {
      print('[PROPOSAL_PROVIDER] 📨 Received ai:learning-updated event');
      print('[PROPOSAL_PROVIDER] Learning data: $data');
      final aiType = data['aiType'] ?? 'AI';
      final learningKey = data['learningKey'] ?? 'unknown';
      final learningValue = data['learningValue'] ?? 'unknown lesson';
      final filePath = data['filePath'] ?? 'unknown file';
      final status = data['status'] ?? 'unknown';

      String title, body;
      if (status == 'rejected' || status == 'test-failed') {
        title = '🧠 $aiType Learned from Failure';
        body = 'Learned: ${learningValue.substring(0, 50)}...';
      } else {
        title = '✅ $aiType Learned from Success';
        body = 'Successfully applied changes to ${filePath.split('/').last}';
      }

      _showNotification(title, body, channelId: 'ai_learning');
    });

    print('[PROPOSAL_PROVIDER] Socket.IO event handlers registered');
  }

  void connect() {
    print('[PROPOSAL_PROVIDER] Connecting to Socket.IO backend...');
    _socket.connect();
    _showNotification(
      '🔗 Connecting to AI Backend',
      'Establishing connection to AI system...',
      channelId: 'ai_processes',
      id: 0, // Use fixed ID for connection status
    );

    // Add retry logic for connection failures
    _socket.onConnectError((error) {
      print('[PROPOSAL_PROVIDER] ❌ Socket.IO connection error: $error');
      _showNotification(
        '🔌 Connection Failed',
        'Failed to connect to AI backend. Retrying in 30 seconds...',
        channelId: 'ai_processes',
      );

      // Retry connection after 30 seconds
      Future.delayed(const Duration(seconds: 30), () {
        if (!_socket.connected) {
          print('[PROPOSAL_PROVIDER] 🔄 Retrying Socket.IO connection...');
          _socket.connect();
        }
      });
    });
  }

  @override
  void dispose() {
    _socket.dispose();
    super.dispose();
  }

  // Check if backend is reachable
  Future<bool> checkBackendConnectivity() async {
    try {
      final url = Uri.parse('$_backendUrl/health');
      final response = await http
          .get(url)
          .timeout(
            const Duration(seconds: 5),
            onTimeout: () {
              throw TimeoutException(
                'Health check timed out',
                const Duration(seconds: 5),
              );
            },
          );

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Backend is healthy and responding');
        return true;
      } else {
        print(
          '[PROPOSAL_PROVIDER] ⚠️ Backend responded with status: ${response.statusCode}',
        );
        return false;
      }
    } catch (error) {
      print('[PROPOSAL_PROVIDER] ❌ Backend connectivity check failed: $error');
      return false;
    }
  }

  Future<void> testBackendConnection() async {
    print('[PROPOSAL_PROVIDER] 🔍 Testing backend connection...');

    // Test health endpoint first
    try {
      final healthUrl = Uri.parse('$_backendUrl/health');
      print('[PROPOSAL_PROVIDER] 📡 Testing health endpoint: $healthUrl');

      final healthResponse = await http
          .get(healthUrl)
          .timeout(const Duration(seconds: 5));
      print(
        '[PROPOSAL_PROVIDER] ✅ Health endpoint response: ${healthResponse.statusCode}',
      );
      print(
        '[PROPOSAL_PROVIDER] 📄 Health response body: ${healthResponse.body}',
      );

      if (healthResponse.statusCode == 200) {
        _showNotification(
          '✅ Backend Connected',
          'Backend is running and accessible',
          channelId: 'ai_processes',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Health endpoint failed: $e');
      _showNotification(
        '❌ Backend Unreachable',
        'Cannot reach backend health endpoint: $e',
        channelId: 'ai_processes',
      );
      return;
    }

    // Test proposals endpoint
    try {
      final proposalsUrl = Uri.parse('$_backendUrl/api/proposals');
      print('[PROPOSAL_PROVIDER] 📡 Testing proposals endpoint: $proposalsUrl');

      final proposalsResponse = await http
          .get(proposalsUrl)
          .timeout(const Duration(seconds: 10));
      print(
        '[PROPOSAL_PROVIDER] 📊 Proposals endpoint response: ${proposalsResponse.statusCode}',
      );

      if (proposalsResponse.statusCode == 200) {
        final data = jsonDecode(proposalsResponse.body);
        print(
          '[PROPOSAL_PROVIDER] 📋 Found ${data.length} proposals in backend',
        );

        final pendingCount = data.where((p) => p['status'] == 'pending').length;
        final approvedCount =
            data.where((p) => p['status'] == 'approved').length;

        _showNotification(
          '📊 Backend Data',
          'Found ${data.length} total proposals ($pendingCount pending, $approvedCount approved)',
          channelId: 'ai_processes',
        );
      } else {
        print(
          '[PROPOSAL_PROVIDER] ❌ Proposals endpoint failed: ${proposalsResponse.statusCode}',
        );
        print(
          '[PROPOSAL_PROVIDER] 📄 Error response: ${proposalsResponse.body}',
        );
        _showNotification(
          '❌ Proposals Error',
          'Backend returned ${proposalsResponse.statusCode}',
          channelId: 'ai_processes',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Proposals endpoint failed: $e');
      _showNotification(
        '❌ Proposals Unreachable',
        'Cannot reach proposals endpoint: $e',
        channelId: 'ai_processes',
      );
    }
  }

  // Get backend status for UI
  bool get isBackendConnected => _socket.connected;

  Future<void> createTestProposal() async {
    print('[PROPOSAL_PROVIDER] 🧪 Creating test proposal...');

    if (_useMockMode) {
      print('[PROPOSAL_PROVIDER] 🎭 Mock mode - creating local test proposal');
      final testProposal = AIProposal(
        id: 'test-${DateTime.now().millisecondsSinceEpoch}',
        aiType: 'Test AI',
        filePath: 'lib/test_file.dart',
        oldCode: '// Old code\nvoid oldFunction() {\n  print("old");\n}',
        newCode: '// New code\nvoid newFunction() {\n  print("new");\n}',
        timestamp: DateTime.now(),
        status: ProposalStatus.pending,
      );

      _proposals.add(testProposal);
      notifyListeners();

      _showNotification(
        '✅ Test Proposal Created',
        'Created test proposal in mock mode',
        channelId: 'ai_proposals',
      );
      return;
    }

    // Create test proposal on backend
    try {
      final url = Uri.parse('$_backendUrl/api/proposals');
      final testData = {
        'aiType': 'Test AI',
        'filePath': 'lib/test_file.dart',
        'codeBefore': '// Old code\nvoid oldFunction() {\n  print("old");\n}',
        'codeAfter': '// New code\nvoid newFunction() {\n  print("new");\n}',
        'status': 'pending',
      };

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(testData),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Test proposal created successfully');
        await fetchProposals(); // Refresh the list
        _showNotification(
          '✅ Test Proposal Created',
          'Test proposal created on backend',
          channelId: 'ai_proposals',
        );
      } else {
        print(
          '[PROPOSAL_PROVIDER] ❌ Failed to create test proposal: ${response.statusCode}',
        );
        _showNotification(
          '❌ Test Proposal Failed',
          'Backend returned ${response.statusCode}',
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error creating test proposal: $e');
      _showNotification(
        '❌ Test Proposal Error',
        'Failed to create test proposal: $e',
        channelId: 'ai_proposals',
      );
    }
  }

  void _createMockProposals() {
    _proposals.clear();

    // Mock Imperium proposal
    _proposals.add(
      AIProposal(
        id: 'mock-1',
        aiType: 'Imperium',
        filePath: 'lib/main.dart',
        oldCode: '''void main() {
  runApp(MyApp());
}''',
        newCode: '''void main() {
  runApp(MyApp());
  // Added error handling and logging
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
  };
}''',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        status: ProposalStatus.pending,
      ),
    );

    // Mock Sandbox proposal
    _proposals.add(
      AIProposal(
        id: 'mock-2',
        aiType: 'Sandbox',
        filePath: 'lib/mission.dart',
        oldCode: '''class Mission {
  String title;
  Mission(this.title);
}''',
        newCode: '''class Mission {
  String title;
  String? description;
  DateTime? dueDate;
  
  Mission(this.title, {this.description, this.dueDate});
  
  Map<String, dynamic> toJson() => {
    'title': title,
    'description': description,
    'dueDate': dueDate?.toIso8601String(),
  };
}''',
        timestamp: DateTime.now().subtract(const Duration(hours: 1)),
        status: ProposalStatus.pending,
      ),
    );

    // Mock Guardian proposal
    _proposals.add(
      AIProposal(
        id: 'mock-3',
        aiType: 'Guardian',
        filePath: 'lib/providers/proposal_provider.dart',
        oldCode: '''Future<void> fetchProposals() async {
  // Basic implementation
}''',
        newCode: '''Future<void> fetchProposals() async {
  try {
    // Enhanced implementation with error handling
    final response = await http.get(url);
    if (response.statusCode == 200) {
      // Process response
    } else {
      throw Exception('Failed to fetch proposals');
    }
  } catch (error) {
    print('Error: \$error');
    rethrow;
  }
}''',
        timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
        status: ProposalStatus.pending,
      ),
    );

    // Mock approved proposal
    _proposals.add(
      AIProposal(
        id: 'mock-4',
        aiType: 'Imperium',
        filePath: 'lib/theme.dart',
        oldCode: '''ThemeData get lightTheme => ThemeData(
  primarySwatch: Colors.blue,
);''',
        newCode: '''ThemeData get lightTheme => ThemeData(
  primarySwatch: Colors.blue,
  brightness: Brightness.light,
  useMaterial3: true,
);''',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        status: ProposalStatus.approved,
      ),
    );

    print('[PROPOSAL_PROVIDER] 🎭 Created ${_proposals.length} mock proposals');
    print('[PROPOSAL_PROVIDER] 📊 Mock proposal counts:');
    print('[PROPOSAL_PROVIDER]   - Total: ${_proposals.length}');
    print(
      '[PROPOSAL_PROVIDER]   - Pending: ${_proposals.where((p) => p.status == ProposalStatus.pending).length}',
    );
    print(
      '[PROPOSAL_PROVIDER]   - Approved: ${_proposals.where((p) => p.status == ProposalStatus.approved).length}',
    );

    notifyListeners();

    // Show notification for mock proposals
    final pendingCount =
        _proposals.where((p) => p.status == ProposalStatus.pending).length;
    if (pendingCount > 0) {
      _showNotification(
        '🎭 Mock Proposals Available',
        'You have $pendingCount mock AI proposals to review (Mock Mode)',
        channelId: 'ai_proposals',
      );
    }
  }

  /// Initialize the provider with AI learning integration
  Future<void> initialize({AILearningProvider? aiLearningProvider}) async {
    _aiLearningProvider = aiLearningProvider;
    // Optionally, add any other initialization logic here
    return Future.value();
  }
}
