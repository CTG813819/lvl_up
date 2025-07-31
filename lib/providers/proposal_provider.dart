import 'dart:collection';
import 'package:flutter/material.dart';
import 'package:the_codex/main.dart';
import '../models/ai_proposal.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'dart:io';
import 'dart:async';
import 'package:provider/provider.dart';
import '../providers/ai_learning_provider.dart';
import 'package:flutter/foundation.dart';
import '../services/network_config.dart';
import '../services/endpoint_fallback_service.dart';

class ProposalProvider extends ChangeNotifier {
  final List<AIProposal> _proposals = [];
  
  WebSocketChannel? _websocketChannel;
  bool _isWebSocketConnected = false;

  // Flag to prevent multiple initializations
  bool _isInitialized = false;

  // Use network configuration service
  String get _backendUrl => NetworkConfig.backendUrl;

  // Public getter for backend URL
  static String get backendUrl => NetworkConfig.backendUrl;

  // Connection state tracking
  bool _isBackendAvailable = false;
  int _consecutiveFailures = 0;

  // Public getter for backend availability
  bool get isBackendAvailable => _isBackendAvailable;

  // Connection notification tracking
  static const int _fourHoursMs = 4 * 60 * 60 * 1000;
  int _lastConnectionNotification = 0;
  List<Map<String, dynamic>> _connectionErrorBuffer = [];

  // Timer for periodic polling
  Timer? _pollingTimer;

  bool get isOperating {
    return true;
  }

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

  // Add this getter to filter only user-ready proposals
  List<AIProposal> get userReadyProposals =>
      _proposals.where((p) => p.status == ProposalStatus.testPassed).toList();

  // Method to fetch user-ready proposals (test-passed and test_status=passed)
  Future<void> fetchUserReadyProposals() async {
    final imperiumUrl = Uri.parse('$_backendUrl/api/proposals/all');

    try {
      final imperiumResponse = await http.get(
        imperiumUrl,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'LVL_UP_Flutter_App',
        },
      );

      if (imperiumResponse.statusCode == 200) {
        final imperiumData = jsonDecode(imperiumResponse.body);
        print(
          '[PROPOSAL_PROVIDER] 📥 Imperium response type: ${imperiumData.runtimeType}',
        );
        print('[PROPOSAL_PROVIDER] 📥 Imperium response: $imperiumData');

        // Backend returns a list directly, not an object with 'proposals' field
        final proposals = imperiumData is List ? imperiumData : [];
        print(
          '[PROPOSAL_PROVIDER] 📋 Found ${proposals.length} imperium proposals',
        );

        final List<AIProposal> pendingProposals = [];
        pendingProposals.addAll(
          proposals
              .map<AIProposal?>((json) {
                try {
                  return AIProposal.fromImperium(json);
                } catch (e) {
                  print(
                    '[PROPOSAL_PROVIDER] ❌ Error parsing imperium proposal: $e',
                  );
                  print('[PROPOSAL_PROVIDER] ❌ Problematic JSON: $json');
                  return null;
                }
              })
              .where((p) => p != null)
              .cast<AIProposal>(),
        );

        // Only show pending and test-passed proposals to users
        final userReadyProposals = pendingProposals.where((p) => 
          p.status == ProposalStatus.pending || 
          p.status == ProposalStatus.testPassed
        ).toList();

        _proposals.clear();
        _proposals.addAll(userReadyProposals);

        print('[DEBUG] User-ready proposals fetched: ${_proposals.length}');
        for (final p in _proposals) {
          print('[DEBUG] User-ready proposal: ${p.id} ${p.status}');
        }

        notifyListeners();
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error fetching user-ready proposals: $e');
      _handleBackendFailure(e.toString());
    }
  }

  void _disposeSocket() {
    // Remove all Socket.IO code and replace with native WebSocket logic
    if (_websocketChannel != null) {
      _websocketChannel!.sink.close();
      _websocketChannel = null;
    }
    _isWebSocketConnected = false;
  }

  void _disposeNotifications() {
    // Stop any notification timers or listeners
  }

  ProposalProvider() {
    _startPeriodicRefresh();
  }

  void _startPeriodicRefresh() {
    // Refresh proposals every 30 seconds to keep UI in sync
    Timer.periodic(const Duration(seconds: 30), (timer) {
      if (isOperating) {
        fetchUserReadyProposals();
      }
    });
  }

  Future<void> initialize() async {
    if (_isInitialized) {
      print('[PROPOSAL_PROVIDER] Already initialized, skipping...');
      return;
    }

    print(
      '[PROPOSAL_PROVIDER] 🚀 Initializing autonomous proposal provider...',
    );
    _isInitialized = true;

    // Always start autonomous operation - don't depend on user interaction
    _initWebSocket();
    await fetchUserReadyProposals();
    _startAutonomousPolling();

    print(
      '[PROPOSAL_PROVIDER] ✅ Autonomous proposal provider initialized and running',
    );
  }

  void _startAutonomousPolling() {
    if (_pollingTimer != null) return; // Already polling
    _pollingTimer = Timer.periodic(const Duration(seconds: 60), (_) {
      // Check operational hours but still run autonomously
      if (isOperating) {
        fetchUserReadyProposals(); // Changed from fetchAllProposals to fetchUserReadyProposals
      } else {
        print(
          '[PROPOSAL_PROVIDER] ⏸️ Autonomous polling paused - outside operational hours',
        );
      }
    });
    print(
      '[PROPOSAL_PROVIDER] 🔄 Started autonomous polling for user-ready proposals (every 60 seconds)',
    );
  }

  Future<void> fetchAllProposals() async {
    await fetchUserReadyProposals();
  }



  // Show notification method
  void _showNotification(
    String title,
    String body, {
    String? channelId,
    int? id,
  }) {
    final notificationId =
        id ?? (DateTime.now().millisecondsSinceEpoch & 0x7FFFFFFF);
    final channel = channelId ?? 'ai_processes';

    // FlutterLocalNotificationsPlugin is no longer used for WebSocket notifications
    // _notifications.show(
    //   notificationId,
    //   title,
    //   body,
    //   NotificationDetails(
    //     android: AndroidNotificationDetails(
    //       channel,
    //       'AI Processes',
    //       channelDescription: 'Notifications for AI proposal processing',
    //       importance: Importance.high,
    //       priority: Priority.high,
    //       showWhen: true,
    //       enableVibration: true,
    //       playSound: true,
    //       icon: '@mipmap/ic_launcher',
    //       color: const Color(0xFF2196F3),
    //     ),
    //   ),
    // );
    
    print('[PROPOSAL_PROVIDER] 📢 Notification: $title - $body');
  }

  // Initialize WebSocket connection
  void _initWebSocket() {
    print('[PROPOSAL_PROVIDER] Initializing WebSocket connection...');
    try {
      _websocketChannel = WebSocketChannel.connect(
        Uri.parse('ws://34.202.215.209:8000/api/imperium/status'),
      );
      _isWebSocketConnected = true;
      _websocketChannel!.stream.listen(
        (data) {
          print('[WEBSOCKET] Received: $data');
          // Handle incoming messages as needed
          // Example: parse and act on proposal updates
          try {
            final message = jsonDecode(data.toString());
            // Handle different message types here
          } catch (e) {
            print('[WEBSOCKET] Error parsing message: $e');
          }
        },
        onError: (error) {
          print('[WEBSOCKET] Error: $error');
          _isWebSocketConnected = false;
        },
        onDone: () {
          print('[WEBSOCKET] Connection closed');
          _isWebSocketConnected = false;
        },
      );
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ WebSocket initialization failed: $e');
      _isWebSocketConnected = false;
    }
  }

  // Get connection status for UI
  Map<String, dynamic> getConnectionStatus() {
    return {
      'backendAvailable': _isBackendAvailable,
      'consecutiveFailures': _consecutiveFailures,
      'backendUrl': _backendUrl,
      'websocketConnected': _isWebSocketConnected,
      'isOperating': isOperating,
    };
  }

  // Handle backend failure
  void _handleBackendFailure(String error) {
    _consecutiveFailures++;
    _isBackendAvailable = false;
    
    // Add to error buffer for notifications
    _connectionErrorBuffer.add({
      'error': error,
      'timestamp': DateTime.now().toIso8601String(),
    });
    
    // Keep only last 10 errors
    if (_connectionErrorBuffer.length > 10) {
      _connectionErrorBuffer.removeAt(0);
    }
    
    _handleConnectionNotification();
    notifyListeners();
  }

  // Handle connection notification with rate limiting
  void _handleConnectionNotification() {
    final now = DateTime.now().millisecondsSinceEpoch;
    if (now - _lastConnectionNotification < _fourHoursMs) return;
    
    _lastConnectionNotification = now;
    
    if (_connectionErrorBuffer.isNotEmpty) {
      _showNotification(
        '⚠️ Connection Issues',
        'Backend connection problems detected.\n${_connectionErrorBuffer.length} connection errors/timeouts occurred in the last 4 hours.',
        channelId: 'ai_processes',
      );
    } else {
      _showNotification(
        '✅ Connection Restored',
        'Successfully connected to backend',
        channelId: 'ai_processes',
      );
    }
  }

  // Clear connection error buffer
  void _clearConnectionErrors() {
    _connectionErrorBuffer.clear();
  }

  // Add connection error
  void _addConnectionError(String error) {
    _connectionErrorBuffer.add({
      'error': error,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }





  // Remove all Socket.IO code and replace with native WebSocket logic
  // Remove: IO.Socket? _socket; and all references to _socket


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
        _handleBackendSuccess();
        return true;
      } else {
        print(
          '[PROPOSAL_PROVIDER] ⚠️ Backend responded with status: ${response.statusCode}',
        );
        _handleBackendFailure('HTTP ${response.statusCode}');
        return false;
      }
    } catch (error) {
      print('[PROPOSAL_PROVIDER] ❌ Backend connectivity check failed: $error');
      _handleBackendFailure(error.toString());
      return false;
    }
  }

  // Handle successful backend connection
  void _handleBackendSuccess() {
    _consecutiveFailures = 0;
    _isBackendAvailable = true;
  }



  // Manual retry connection (public method)
  Future<void> retryConnection() async {
    print('[PROPOSAL_PROVIDER] 🔄 Manual retry requested');

    // Reset failure count for manual retry
    _consecutiveFailures = 0;

    // In retryConnection, remove all references to ChaosWarpProvider and chaos/warp state. Always attempt backend connection and fetch proposals.
    // Remove any logic or notifications about operational hours or chaos/warp.
    try {
      // Test backend connectivity
      final isHealthy = await checkBackendConnectivity();
      if (isHealthy) {
        print('[PROPOSAL_PROVIDER] ✅ Backend is healthy');
        _isBackendAvailable = true;

        // Fetch fresh proposals from backend
        await fetchUserReadyProposals();

        _showNotification(
          '✅ Connection Restored',
          'Successfully connected to backend',
          channelId: 'ai_processes',
        );
      } else {
        print('[PROPOSAL_PROVIDER] ❌ Backend still unavailable');
        _showNotification(
          '❌ Connection Failed',
          'Backend is still unavailable',
          channelId: 'ai_processes',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error during retry connection: $e');
      _showNotification(
        '❌ Connection Error',
        'Failed to establish connection to backend: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_processes',
      );
    }

    notifyListeners();
  }

  Future<void> testBackendConnection() async {
    print('[PROPOSAL_PROVIDER] 🔍 Testing backend connection...');
    print('[PROPOSAL_PROVIDER] 📊 Backend available: $_isBackendAvailable');
    print('[PROPOSAL_PROVIDER] 📊 Consecutive failures: $_consecutiveFailures');

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
          'Backend is healthy and responding',
          channelId: 'ai_processes',
        );
      } else {
        _showNotification(
          '⚠️ Backend Warning',
          'Backend responded with status: ${healthResponse.statusCode}',
          channelId: 'ai_processes',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Health check failed: $e');
      _showNotification(
        '❌ Backend Error',
        'Failed to connect to backend: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_processes',
      );
    }
  }

  // Notify successful backend connection (once every 4 hours)
  Future<void> _notifyBackendConnected() async {
    final now = DateTime.now().millisecondsSinceEpoch;
    if (now - _lastConnectionNotification < _fourHoursMs) return;

    _lastConnectionNotification = now;
    String errorSummary = '';

    if (_connectionErrorBuffer.isNotEmpty) {
      errorSummary =
          '\n${_connectionErrorBuffer.length} connection errors/timeouts occurred in the last 4 hours.';
    }

    // Send notification to backend
    try {
      final response = await http.post(
        Uri.parse('$_backendUrl/api/imperium/status'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'title': 'Connected to AI Backend',
          'body': 'The app is connected to the backend.$errorSummary',
          'type': 'system',
          'userId': 'proposal-provider',
        }),
      );
      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Connection notification sent');
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] Failed to send connection notification: $e');
    }

    // Clear error buffer after sending summary
    _connectionErrorBuffer.clear();
  }

  // Buffer connection errors (don't send immediately)
  void _bufferConnectionError(String errorType) {
    _connectionErrorBuffer.add({
      'timestamp': DateTime.now().millisecondsSinceEpoch,
      'errorType': errorType,
    });
    print('[PROPOSAL_PROVIDER] Connection error buffered: $errorType');
  }

  // Send oath paper to AI for learning
  Future<bool> sendOathPaperToAI(Map<String, dynamic> oathPaper) async {
    if (!isOperating) {
      print(
        '[PROPOSAL_PROVIDER] Blocked: AI operations not allowed (time, warp, or chaos state).',
      );
      return false;
    }

    print('[PROPOSAL_PROVIDER] 📜 Sending oath paper to AI for learning...');
    print('[PROPOSAL_PROVIDER] Subject: ${oathPaper['subject']}');
    print('[PROPOSAL_PROVIDER] Tags: ${oathPaper['tags']}');
    print(
      '[PROPOSAL_PROVIDER] Target AI: ${oathPaper['targetAI'] ?? 'All AIs'}',
    );
    print('[PROPOSAL_PROVIDER] AI Weights: ${oathPaper['aiWeights']}');

    try {
      // Enhanced oath paper data with keyword extraction and learning instructions
      final enhancedOathPaper = {
        ...oathPaper,
        'learningMode': 'enhanced',
        'extractKeywords': true,
        'internetSearch': true,
        'gitIntegration': true,
        'learningInstructions': {
          'scanDescription': true,
          'scanCode': true,
          'extractKeywords': true,
          'searchInternet': true,
          'learnFromResults': true,
          'updateCapabilities': true,
          'pushToGit': true,
        },
        'timestamp': DateTime.now().toIso8601String(),
      };

      final url = Uri.parse('$_backendUrl/api/oath-papers');
      print('[PROPOSAL_PROVIDER] 📡 Sending enhanced oath paper to: $url');

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(enhancedOathPaper),
          )
          .timeout(
            const Duration(seconds: 60),
          ); // Increased timeout for enhanced processing

      print(
        '[PROPOSAL_PROVIDER] 📥 Enhanced oath paper response: ${response.statusCode}',
      );

      if (response.statusCode == 200) {
        final result = jsonDecode(response.body);
        print(
          '[PROPOSAL_PROVIDER] ✅ Enhanced oath paper processed successfully',
        );
        print('[PROPOSAL_PROVIDER] Result: $result');

        // Show detailed notification with learning progress
        final learningProgress = result['learningProgress'] ?? {};
        final keywordsFound = learningProgress['keywordsFound'] ?? [];
        final internetSearches = learningProgress['internetSearches'] ?? [];
        final gitUpdates = learningProgress['gitUpdates'] ?? [];

        String notificationMessage =
            'AI learning from: ${oathPaper['subject']}';
        if (keywordsFound.isNotEmpty) {
          notificationMessage +=
              '\nKeywords: ${keywordsFound.take(3).join(', ')}';
        }
        if (internetSearches.isNotEmpty) {
          notificationMessage +=
              '\nSearched: ${internetSearches.length} sources';
        }
        if (gitUpdates.isNotEmpty) {
          notificationMessage += '\nGit: ${gitUpdates.length} updates';
        }

        _showNotification(
          '🧠 AI Learning Enhanced',
          notificationMessage,
          channelId: 'ai_proposals',
        );

        return true;
      } else {
        print(
          '[PROPOSAL_PROVIDER] ❌ Failed to process enhanced oath paper: ${response.statusCode}',
        );
        print('[PROPOSAL_PROVIDER] Error response: ${response.body}');

        // Fallback to basic processing
        return await _fallbackOathPaperProcessing(oathPaper);
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error processing enhanced oath paper: $e');

      // Fallback to basic processing
      return await _fallbackOathPaperProcessing(oathPaper);
    }
  }

  // Fallback processing for oath papers when enhanced processing fails
  Future<bool> _fallbackOathPaperProcessing(
    Map<String, dynamic> oathPaper,
  ) async {
    try {
      print(
        '[PROPOSAL_PROVIDER] 🔄 Attempting fallback oath paper processing...',
      );

      final url = Uri.parse('$_backendUrl/api/oath-papers');
      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(oathPaper),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        print(
          '[PROPOSAL_PROVIDER] ✅ Fallback oath paper processing successful',
        );
        _showNotification(
          '📜 Oath Paper Processed (Basic)',
          'AI will learn from: ${oathPaper['subject']}',
          channelId: 'ai_proposals',
        );
        return true;
      } else {
        print(
          '[PROPOSAL_PROVIDER] ❌ Fallback processing also failed: ${response.statusCode}',
        );
        return false;
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error in fallback processing: $e');
      return false;
    }
  }

  @override
  void dispose() {
    _disposeSocket();
    _disposeNotifications();
    _pollingTimer?.cancel();
    super.dispose();
  }

  // Fetch oath papers
  Future<void> fetchOathPapers() async {
    try {
      final url = Uri.parse('$_backendUrl/api/oath-papers');
      final response = await http.get(url);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('[PROPOSAL_PROVIDER] ✅ Oath papers fetched: ${data.length}');
      } else {
        print('[PROPOSAL_PROVIDER] ❌ Failed to fetch oath papers: ${response.statusCode}');
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error fetching oath papers: $e');
    }
  }

  // Create oath paper
  Future<void> createOathPaper(Map<String, dynamic> paperData) async {
    try {
      final url = Uri.parse('$_backendUrl/api/oath-papers');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(paperData),
      );
      
      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Oath paper created successfully');
        _showNotification(
          '✅ Oath Paper Created',
          'New oath paper has been created successfully',
          channelId: 'ai_proposals',
        );
      } else {
        print('[PROPOSAL_PROVIDER] ❌ Failed to create oath paper: ${response.statusCode}');
        _showNotification(
          '❌ Creation Failed',
          'Failed to create oath paper: ${response.statusCode}',
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      print('[PROPOSAL_PROVIDER] ❌ Error creating oath paper: $e');
      _showNotification(
        '❌ Creation Error',
        'Error creating oath paper: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_proposals',
      );
    }
  }

  // Approve a proposal
  Future<void> approveProposal(String id) async {
    if (!isOperating) {
      print(
        '[PROPOSAL_PROVIDER] Blocked: AI operations not allowed (time, warp, or chaos state).',
      );
      notifyListeners();
      return;
    }
    print('[PROPOSAL_PROVIDER] Approving proposal: $id');

    final proposalIndex = _proposals.indexWhere((p) => p.id == id);
    if (proposalIndex == -1) return;
    final proposal = _proposals[proposalIndex];

    // Optimistically remove proposal
    _proposals.removeAt(proposalIndex);
    notifyListeners();

    try {
      // First, show the proposal as testing
      proposal.status = ProposalStatus.testing;
      _proposals.insert(proposalIndex, proposal);
      notifyListeners();

      _showNotification(
        '🔄 Proposal Testing Started',
        'Proposal for ${proposal.filePath.split('/').last} is being tested...',
        channelId: 'ai_proposals',
      );

      // Wait a moment to show the testing status
      await Future.delayed(const Duration(seconds: 2));

      // Use imperium endpoint for agent approval
      final url = Uri.parse('$_backendUrl/api/proposals');
      print('[PROPOSAL_PROVIDER] 📡 Approving agent at: $url');

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'userFeedback': 'approved',
              'userFeedbackReason': 'User approved the agent',
            }),
          )
          .timeout(const Duration(seconds: 30)); // Increased timeout

      print('[PROPOSAL_PROVIDER] 📥 Approval response: ${response.statusCode}');
      print('[PROPOSAL_PROVIDER] 📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Proposal approved successfully');

        // Parse response to check test status
        final responseData = jsonDecode(response.body);
        final testStatus = responseData['test_status'];
        final testOutput = responseData['test_output'];
        final overallResult = responseData['overall_result'];

        if (overallResult == 'passed') {
          // Tests passed - remove proposal and show success
          print(
            '[PROPOSAL_PROVIDER] ✅ Tests passed - proposal applied successfully',
          );

          _showNotification(
            '✅ Proposal Applied Successfully',
            'Proposal has been approved and all tests passed',
            channelId: 'ai_proposals',
          );
        } else {
          // Tests failed - remove proposal and show failure
          print('[PROPOSAL_PROVIDER] ❌ Tests failed - proposal removed');
          _showNotification(
            '❌ Proposal Failed Testing',
            'Proposal was approved but failed testing and has been removed',
            channelId: 'ai_proposals',
          );
        }

        // Always fetch latest proposals after approval for real-time updates
        await fetchUserReadyProposals();

        // Force UI update
        notifyListeners();
      } else {
        // Restore proposal if backend call fails
        _proposals.insert(proposalIndex, proposal);
        notifyListeners();
        print(
          '[PROPOSAL_PROVIDER] ❌ Failed to approve proposal: ${response.statusCode}',
        );

        // Provide more specific error messages
        String errorMessage = 'Backend returned status ${response.statusCode}';
        if (response.statusCode == 500) {
          errorMessage = 'Backend server error - please try again';
        } else if (response.statusCode == 404) {
          errorMessage = 'Proposal not found on server';
        } else if (response.statusCode == 400) {
          errorMessage = 'Invalid request - proposal may already be processed';
        }

        _showNotification(
          '❌ Approval Failed',
          errorMessage,
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      // Restore proposal if backend call fails
      _proposals.insert(proposalIndex, proposal);
      notifyListeners();
      print('[PROPOSAL_PROVIDER] ❌ Error approving proposal: $e');

      // Provide more specific error messages
      String errorMessage =
          'Failed to approve proposal: ${e.toString().substring(0, 50)}...';
      if (e.toString().contains('timeout')) {
        errorMessage = 'Request timed out - please try again';
      } else if (e.toString().contains('connection')) {
        errorMessage = 'Connection error - please check your network';
      }

      _showNotification(
        '❌ Approval Error',
        errorMessage,
        channelId: 'ai_proposals',
      );
    }
  }

  // Reject a proposal
  Future<void> rejectProposal(String id) async {
    print('[PROPOSAL_PROVIDER] Rejecting proposal: $id');

    final proposalIndex = _proposals.indexWhere((p) => p.id == id);
    if (proposalIndex == -1) return;
    final proposal = _proposals[proposalIndex];

    // Optimistically remove proposal
    _proposals.removeAt(proposalIndex);
    notifyListeners();

    try {
      // Use imperium endpoint for agent rejection
      final url = Uri.parse('$_backendUrl/api/proposals');
      print('[PROPOSAL_PROVIDER] 📡 Rejecting agent at: $url');

      final response = await http
          .post(
            url,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'userFeedback': 'rejected',
              'userFeedbackReason': 'User rejected the agent',
            }),
          )
          .timeout(const Duration(seconds: 15));

      print(
        '[PROPOSAL_PROVIDER] 📥 Rejection response: ${response.statusCode}',
      );
      print('[PROPOSAL_PROVIDER] 📄 Response body: ${response.body}');

      if (response.statusCode == 200) {
        print('[PROPOSAL_PROVIDER] ✅ Proposal rejected successfully');
        // Always fetch latest proposals after rejection
        await fetchUserReadyProposals();
        _showNotification(
          '❌ Proposal Rejected',
          'Proposal has been rejected and removed',
          channelId: 'ai_proposals',
        );
      } else {
        // Restore proposal if backend call fails
        _proposals.insert(proposalIndex, proposal);
        notifyListeners();
        print(
          '[PROPOSAL_PROVIDER] ❌ Failed to reject proposal: ${response.statusCode}',
        );
        _showNotification(
          '❌ Rejection Failed',
          'Backend returned status ${response.statusCode}',
          channelId: 'ai_proposals',
        );
      }
    } catch (e) {
      // Restore proposal if backend call fails
      _proposals.insert(proposalIndex, proposal);
      notifyListeners();
      print('[PROPOSAL_PROVIDER] ❌ Error rejecting proposal: $e');
      _showNotification(
        '❌ Rejection Error',
        'Failed to reject proposal: ${e.toString().substring(0, 50)}...',
        channelId: 'ai_proposals',
      );
    }
  }

  // Approve all proposals
  Future<void> approveAllProposals() async {
    print('[PROPOSAL_PROVIDER] Approving all pending proposals');

    final userReadyProposals =
        _proposals.where((p) => p.status == ProposalStatus.pending).toList();

    if (userReadyProposals.isEmpty) {
      print('[PROPOSAL_PROVIDER] No pending proposals to approve');
      _showNotification(
        'ℹ️ No Pending Proposals',
        'There are no pending proposals to approve.',
        channelId: 'ai_proposals',
      );
      return;
    }

    print(
      '[PROPOSAL_PROVIDER] Found ${userReadyProposals.length} user-ready proposals to approve',
    );

    // Show testing status for all proposals first
    for (final proposal in userReadyProposals) {
      proposal.status = ProposalStatus.testing;
    }
    notifyListeners();

    _showNotification(
      '🔄 Bulk Testing Started',
      '${userReadyProposals.length} proposals are being tested...',
      channelId: 'ai_proposals',
    );

    // Wait a moment to show testing status
    await Future.delayed(const Duration(seconds: 2));

    int successCount = 0;
    int failureCount = 0;

    for (final proposal in userReadyProposals) {
      try {
        print('[PROPOSAL_PROVIDER] Approving proposal: ${proposal.id}');

        // Use imperium endpoint for agent approval
        final url = Uri.parse(
          '$_backendUrl/api/proposals',
        );
        final response = await http.post(
          url,
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({
            'userFeedbackReason': 'Approved via bulk approval',
          }),
        );

        if (response.statusCode == 200) {
          // Parse response to check test status
          final responseData = jsonDecode(response.body);
          final testStatus = responseData['test_status'];
          final testOutput = responseData['test_output'];

          if (testStatus == 'tested' && testOutput == 'All tests passed.') {
            successCount++;
            print(
              '[PROPOSAL_PROVIDER] ✅ Successfully approved proposal: ${proposal.id}',
            );
          } else {
            failureCount++;
            print(
              '[PROPOSAL_PROVIDER] ❌ Proposal failed testing: ${proposal.id}',
            );
          }
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
    await fetchUserReadyProposals();

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
}
