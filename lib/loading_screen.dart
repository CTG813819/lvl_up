  // ignore_for_file: library_private_types_in_public_api

import 'package:flutter/material.dart';
import 'package:the_codex/home_page.dart';
import 'package:the_codex/mechanicum.dart';
import 'package:the_codex/mission.dart'
    show MissionProvider; // Use MissionProvider from mission.dart
import 'package:provider/provider.dart';
import 'dart:async';
import 'package:the_codex/mastery_list.dart';
import 'package:the_codex/providers/app_history_provider.dart';
import 'package:the_codex/ai_brain.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'ai_file_system_helper.dart';
import 'package:the_codex/providers/proposal_provider.dart';
import 'dart:io';
import 'package:the_codex/services/conquest_ai_service.dart';
import 'providers/ai_learning_provider.dart';
import 'package:the_codex/services/notification_service.dart';
import 'package:the_codex/services/ai_progress_notification_service.dart';
import 'services/network_config.dart';
import 'package:the_codex/providers/notification_provider.dart';
import 'package:the_codex/services/websocket_service.dart';

class LoadingScreen extends StatefulWidget {
  const LoadingScreen({super.key, required void Function() onVideoComplete});

  @override
  _LoadingScreenState createState() => _LoadingScreenState();
}

class _LoadingScreenState extends State<LoadingScreen>
    with TickerProviderStateMixin {
  bool _isLoading = true;
  bool _hasError = false;
  bool _hasNavigated = false;
  String? _errorMessage;
  double _loadingProgress = 0.0;
  late AnimationController _progressAnimationController;
  late AnimationController _fadeAnimationController;
  Timer? _loadingTimer;

  // Component loading states
  bool _providersInitialized = false;
  bool _missionProviderReady = false;
  bool _masteryProviderReady = false;
  bool _appHistoryProviderReady = false;
  bool _aiGuardianReady = false;
  bool _imperiumReady = false;
  bool _conquestAIReady = false;
  bool _dataValidationComplete = false;

  // Loading steps
  final List<String> _loadingSteps = [
    'Initializing app components...',
    'Loading mission provider...',
    'Loading mastery provider...',
    'Loading app history provider...',
    'Starting AI Guardian...',
    'Starting The Imperium meta-AI...',
    'Starting Conquest AI...',
    'Validating data integrity...',
    'Preparing user interface...',
    'Ready to launch!',
  ];

  int _currentStep = 0;
  String _currentStepText = '';

  @override
  void initState() {
    super.initState();
    print('LoadingScreen: initState called');
    _initializeAnimations();
    _startLoadingProcess();
  // Automatically trigger AI scan on startup
  // scanAndSendLibFilesToAIs();
  // Set up periodic scan every 10 minutes
  // Timer.periodic(Duration(minutes: 10), (timer) {
  //   scanAndSendLibFilesToAIs();
  // });
  }

  void _initializeAnimations() {
    print('LoadingScreen: Initializing animations');
    _progressAnimationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
  }

  void _startLoadingProcess() {
    print('LoadingScreen: Starting loading process');
    _currentStepText = _loadingSteps[0];

  // Start progress animation
    _progressAnimationController.forward();

  // Simulate loading steps with realistic timing
    _loadingTimer = Timer.periodic(const Duration(milliseconds: 800), (timer) {
      if (_currentStep < _loadingSteps.length - 1) {
        setState(() {
          _currentStep++;
          _currentStepText = _loadingSteps[_currentStep];
          _loadingProgress = (_currentStep + 1) / _loadingSteps.length;
        });

        print('LoadingScreen: Step $_currentStep - $_currentStepText');

  // Perform actual component initialization based on step
        _performStepAction(_currentStep);
      } else {
  // Loading complete
        print('LoadingScreen: Loading complete');
        timer.cancel();
        _onLoadingComplete();
      }
    });
  }

  void _performStepAction(int step) {
    try {
      switch (step) {
        case 0: // Initializing app components
          _initializeProviders();
          break;
        case 1: // Loading mission provider
          _initializeMissionProvider();
          break;
        case 2: // Loading mastery provider
          _initializeMasteryProvider();
          break;
        case 3: // Loading app history provider
          _initializeAppHistoryProvider();
          break;
        case 4: // Starting AI Guardian
          _initializeAIGuardian();
          break;
        case 5: // Starting The Imperium
          _initializeImperium();
          break;
        case 6: // Starting Conquest AI
          _initializeConquestAI();
  // Start all AI file watchers after all providers are initialized
          try {
            TheImperium.instance.startFileWatchers();
            print('LoadingScreen: The Imperium file watchers started');
          } catch (e) {
            print(
              'LoadingScreen: Error starting The Imperium file watchers: $e',
            );
          }
          try {
            print('LoadingScreen: Mechanicum file watchers started');
          } catch (e) {
            print('LoadingScreen: Error starting Mechanicum file watchers: $e');
          }
          try {
  // AI Sandbox file watchers are handled by the MissionProvider from mission.dart
            print(
              'LoadingScreen: AI Sandbox file watchers handled by MissionProvider.',
            );
          } catch (e) {
            print('LoadingScreen: Error with AI Sandbox file watchers: $e');
          }
          break;
        case 7: // Validating data integrity
          _validateDataIntegrity();
          break;
        case 8: // Preparing user interface
          _prepareUserInterface();
          break;
        case 9: // Ready to launch
          _setReadyToLaunch();
          break;
      }
    } catch (e) {
      print('LoadingScreen: Error in step $step: $e');
      setState(() {
        _hasError = true;
        _errorMessage = 'Error in step $step: $e';
      });
    }
  }

  void _initializeProviders() async {
    print('LoadingScreen: Initializing providers');
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      try {
  // Wait a bit to ensure providers are fully initialized
        await Future.delayed(const Duration(milliseconds: 100));

  // Access providers to ensure they're initialized with error handling
        try {
          Provider.of<MissionProvider>(context, listen: false);
          print('LoadingScreen: MissionProvider accessed successfully');
        } catch (e) {
          print('LoadingScreen: MissionProvider not available yet: $e');
        }

        try {
          Provider.of<MasteryProvider>(context, listen: false);
          print('LoadingScreen: MasteryProvider accessed successfully');
        } catch (e) {
          print('LoadingScreen: MasteryProvider not available yet: $e');
        }

        try {
          Provider.of<AppHistoryProvider>(context, listen: false);
          print('LoadingScreen: AppHistoryProvider accessed successfully');
        } catch (e) {
          print('LoadingScreen: AppHistoryProvider not available yet: $e');
        }

  // Initialize ProposalProvider and AILearningProvider and wait for both
        try {
          final proposalProvider = Provider.of<ProposalProvider>(
            context,
            listen: false,
          );
          final aiLearningProvider = Provider.of<AILearningProvider>(
            context,
            listen: false,
          );
          print(
            'LoadingScreen: Initializing ProposalProvider and AILearningProvider...',
          );

  // Both providers now start autonomously - no need to wait for user interaction
          await proposalProvider.initialize();
          aiLearningProvider.initialize();

  // Initialize Conquest AI service
          final conquestService = ConquestAIService();
          conquestService.initialize();

  // Start autonomous AI learning tasks
          try {
            conquestService.learnFromOtherAIs();
          } catch (e) {
            print(
              'LoadingScreen: Conquest AI learning error (non-critical): $e',
            );
          }

          print(
            'LoadingScreen: All providers initialized and running autonomously',
          );

  // Start AI Sandbox file watchers
          try {
            final missionProvider = Provider.of<MissionProvider>(
              context,
              listen: false,
            );
  // AI Sandbox file watchers are handled by the MissionProvider from mission.dart
            print(
              'LoadingScreen: AI Sandbox file watchers handled by MissionProvider.',
            );
          } catch (e) {
            print('LoadingScreen: Error with AI Sandbox file watchers: $e');
          }
        } catch (e) {
          print('LoadingScreen: Error initializing advanced providers: $e');
        }

  // All systems are now autonomous - proceed to main app
        _navigateToMainApp();
      } catch (e) {
        print('LoadingScreen: Error initializing providers: $e');
  // Even if there's an error, proceed to main app
        _navigateToMainApp();
      }
    });
  }

  void _initializeMissionProvider() {
    try {
      print('LoadingScreen: Initializing mission provider');

  // Wait a bit to ensure provider is available
      Future.delayed(const Duration(milliseconds: 200), () {
        try {
          final missionProvider = Provider.of<MissionProvider>(
            context,
            listen: false,
          );

  // Trigger any necessary initialization
          if (missionProvider.missions.isEmpty) {
            print(
              'LoadingScreen: Mission provider initialized with no missions',
            );
          } else {
            print(
              'LoadingScreen: Mission provider initialized with ${missionProvider.missions.length} missions',
            );
          }

          setState(() {
            _missionProviderReady = true;
          });
        } catch (e) {
          print('LoadingScreen: Error accessing mission provider: $e');
  // Retry after a delay
          Future.delayed(const Duration(milliseconds: 500), () {
            _initializeMissionProvider();
          });
        }
      });
    } catch (e) {
      print('LoadingScreen: Error initializing mission provider: $e');
    }
  }

  void _initializeMasteryProvider() {
    try {
      print('LoadingScreen: Initializing mastery provider');

  // Wait a bit to ensure provider is available
      Future.delayed(const Duration(milliseconds: 300), () {
        try {
          final masteryProvider = Provider.of<MasteryProvider>(
            context,
            listen: false,
          );

  // Load mastery entries if needed
          if (masteryProvider.entries.isEmpty) {
            print(
              'LoadingScreen: Mastery provider initialized with no entries',
            );
          } else {
            print(
              'LoadingScreen: Mastery provider initialized with ${masteryProvider.entries.length} entries',
            );
          }

          setState(() {
            _masteryProviderReady = true;
          });
        } catch (e) {
          print('LoadingScreen: Error accessing mastery provider: $e');
  // Retry after a delay
          Future.delayed(const Duration(milliseconds: 500), () {
            _initializeMasteryProvider();
          });
        }
      });
    } catch (e) {
      print('LoadingScreen: Error initializing mastery provider: $e');
    }
  }

  void _initializeAppHistoryProvider() {
    try {
      print('LoadingScreen: Initializing app history provider');

  // Wait a bit to ensure provider is available
      Future.delayed(const Duration(milliseconds: 400), () {
        try {
          Provider.of<AppHistoryProvider>(context, listen: false);

  // Load app history if needed
          print('LoadingScreen: App history provider initialized');

          setState(() {
            _appHistoryProviderReady = true;
          });
        } catch (e) {
          print('LoadingScreen: Error accessing app history provider: $e');
  // Retry after a delay
          Future.delayed(const Duration(milliseconds: 500), () {
            _initializeAppHistoryProvider();
          });
        }
      });
    } catch (e) {
      print('LoadingScreen: Error initializing app history provider: $e');
    }
  }

  void _initializeAIGuardian() {
    try {
      print('LoadingScreen: Initializing AI Guardian');

  // Wait a bit to ensure provider is available
      Future.delayed(const Duration(milliseconds: 500), () {
        try {
          final missionProvider = Provider.of<MissionProvider>(
            context,
            listen: false,
          );

  // Initialize AI Guardian
          if (!missionProvider.isAIGuardianRunning) {
            print('LoadingScreen: Starting AI Guardian...');
  // Trigger AI Guardian initialization
            missionProvider.initializeAIGuardian();
          } else {
            print('LoadingScreen: AI Guardian already running');
          }

          setState(() {
            _aiGuardianReady = true;
          });
        } catch (e) {
          print(
            'LoadingScreen: Error accessing mission provider for AI Guardian: $e',
          );
  // Retry after a delay
          Future.delayed(const Duration(milliseconds: 500), () {
            _initializeAIGuardian();
          });
        }
      });
    } catch (e) {
      print('LoadingScreen: Error initializing AI Guardian: $e');
    }
  }

  void _initializeImperium() {
    try {
      print('LoadingScreen: Initializing The Imperium meta-AI');
  // Start The Imperium
      TheImperium.ensureStarted();
      setState(() {
        _imperiumReady = true;
      });
      print('LoadingScreen: The Imperium meta-AI started');
    } catch (e) {
      print('LoadingScreen: Error initializing The Imperium: $e');
    }
  }

  void _initializeConquestAI() {
    try {
      print('LoadingScreen: Initializing Conquest AI');
  // Start Conquest AI
      TheImperium.ensureConquestStarted();
      setState(() {
        _conquestAIReady = true;
      });
      print('LoadingScreen: Conquest AI started');
    } catch (e) {
      print('LoadingScreen: Error initializing Conquest AI: $e');
    }
  }

  void _validateDataIntegrity() {
    try {
      print('LoadingScreen: Validating data integrity');

  // Perform basic data validation without depending on providers
  // This is a simple validation that doesn't require provider access
      bool hasIssues = false;

  // Check if basic app directories exist
      final currentDir = Directory.current.path;
      final libExists = Directory('$currentDir/lib').existsSync();
      final assetsExists = Directory('$currentDir/assets').existsSync();

      if (!libExists || !assetsExists) {
        hasIssues = true;
        print('LoadingScreen: Missing required directories (lib or assets)');
      }

  // Check if main.dart exists
      final mainDartExists = File('$currentDir/lib/main.dart').existsSync();
      if (!mainDartExists) {
        hasIssues = true;
        print('LoadingScreen: Missing main.dart file');
      }

      if (!hasIssues) {
        print('LoadingScreen: Data integrity validation passed');
      } else {
        print('LoadingScreen: Data integrity issues found but continuing...');
      }

      setState(() {
        _dataValidationComplete = true;
      });
    } catch (e) {
      print('LoadingScreen: Error during data validation: $e');
  // Continue anyway - don't let validation errors stop the app
      setState(() {
        _dataValidationComplete = true;
      });
    }
  }

  void _prepareUserInterface() {
    try {
      print('LoadingScreen: Preparing user interface');
  // Prepare UI components
      print('LoadingScreen: User interface prepared');

  // Start fade animation
      _fadeAnimationController.forward();
    } catch (e) {
      print('LoadingScreen: Error preparing user interface: $e');
    }
  }

  Future<bool> testAIEndpoints() async {
    final testCode = 'void main() { print("Hello"); }';
    final testFile = 'lib/main.dart';
    bool allSuccess = true;
    final endpoints = [
      {
        'name': 'Imperium',
        'url':
            '${NetworkConfig.apiBaseUrl}/api/learning/data',
      },
      {
        'name': 'Guardian',
        'url':
            '${NetworkConfig.apiBaseUrl}/api/learning/data',
      },
      {
        'name': 'Sandbox',
        'url':
            '${NetworkConfig.apiBaseUrl}/api/learning/data',
      },
    ];
    for (final ep in endpoints) {
      try {
        final response = await http.post(
          Uri.parse(ep['url']!),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'filePath': testFile, 'code': testCode}),
        );
        if (response.statusCode == 200) {
          print('${ep['name']} AI test success: ${response.body}');
        } else {
          print('${ep['name']} AI test failed: ${response.body}');
          allSuccess = false;
        }
      } catch (e) {
        print('${ep['name']} AI test error: $e');
        allSuccess = false;
      }
    }
    return allSuccess;
  }

  void _setReadyToLaunch() async {
    try {
      print('LoadingScreen: App ready to launch');
  // Small delay to show "Ready to launch!" message
      Timer(const Duration(milliseconds: 500), () {
        if (mounted && !_hasNavigated) {
          _navigateToMainScreen();
        }
      });
    } catch (e) {
      print('LoadingScreen: Error setting ready to launch: $e');
    }
  }

  void _onLoadingComplete() {
    print('LoadingScreen: Loading complete, navigating to main screen');
    if (mounted && !_hasNavigated) {
      setState(() {
        _isLoading = false;
        _loadingProgress = 1.0;
      });

  // Navigate after a short delay to show completion
      Timer(const Duration(milliseconds: 1000), () {
        if (!_hasNavigated) {
          _navigateToMainScreen();
        }
      });
    }
  }

  void _navigateToMainScreen() {
    if (mounted && !_hasNavigated) {
      print('LoadingScreen: Navigating to main screen');
      _hasNavigated = true;

  // Cancel loading timer
      _loadingTimer?.cancel();

  // Allow notifications after loading screen
      NotificationService.suppressNotifications = false;

      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  void _navigateToMainApp() {
    if (mounted && !_hasNavigated) {
      print('LoadingScreen: Navigating to main app');
      _hasNavigated = true;
      _loadingTimer?.cancel();
      NotificationService.suppressNotifications = false;
      try {
        final missionProvider = Provider.of<MissionProvider>(
          context,
          listen: false,
        );
        missionProvider.startNotifications();
      } catch (e) {
        print('Error initializing mission notifications: $e');
      }
      try {
        AIProgressNotificationService.instance.startMonitoring(context);
      } catch (e) {
        print('Error initializing AI progress notifications: $e');
      }
  // Start notification and AI leveling listeners
      _startNotificationListeners(context);
      Navigator.pushReplacementNamed(context, '/home');
    }
  }

  void _startNotificationListeners(BuildContext context) {
    final notificationProvider = Provider.of<NotificationProvider>(
      context,
      listen: false,
    );
    final aiLearningProvider = Provider.of<AILearningProvider>(
      context,
      listen: false,
    );
  // Listen for AI notifications from WebSocket
    WebSocketService.instance.notificationStream.listen((notification) {
      notificationProvider.addNotification(
        notification.title,
        notification.body,
        notification.aiSource,
        notification.timestamp,
      );
    });
  // Listen for AI leveling/learning updates
    WebSocketService.instance.learningStream.listen((data) {
      aiLearningProvider.updateFromWebSocket(data);
    });
  // Listen for mission notifications (optional: if mission notifications are not already added)
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    for (final mission in missionProvider.missions.where(
      (m) => !m.isCompleted,
    )) {
      notificationProvider.addNotification(
        mission.title,
        mission.description,
        'mission',
        DateTime.now(),
      );
    }
  }

  @override
  void dispose() {
    print('LoadingScreen: Disposing');
    _loadingTimer?.cancel();
    _progressAnimationController.dispose();
    _fadeAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
  // Background gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0xFF1a1a1a), Color(0xFF000000)],
              ),
            ),
          ),

  // Main content
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
  // App logo or title
                const Text(
                  'LVL UP',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 48,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 4,
                  ),
                ),

                const SizedBox(height: 40),

  // Loading indicator
                SizedBox(
                  width: 300,
                  child: Column(
                    children: [
  // Progress bar
                      AnimatedBuilder(
                        animation: _progressAnimationController,
                        builder: (context, child) {
                          return LinearProgressIndicator(
                            value: _loadingProgress,
                            backgroundColor: Colors.grey[800],
                            valueColor: const AlwaysStoppedAnimation<Color>(
                              Colors.blue,
                            ),
                            minHeight: 6,
                          );
                        },
                      ),

                      const SizedBox(height: 20),

  // Current step text
                      Text(
                        _currentStepText,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 16,
                        ),
                        textAlign: TextAlign.center,
                      ),

                      const SizedBox(height: 8),

  // Progress percentage
                      Text(
                        '${(_loadingProgress * 100).toInt()}%',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

  // Error message
                if (_hasError) ...[
                  const SizedBox(height: 30),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.withOpacity(0.3)),
                    ),
                    child: Text(
                      _errorMessage ?? 'An error occurred',
                      style: const TextStyle(color: Colors.red, fontSize: 14),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],

  // Component status indicators
                const SizedBox(height: 40),

  // Status grid
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.white.withOpacity(0.1)),
                  ),
                  child: Column(
                    children: [
                      const Text(
                        'Component Status',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),

  // Provider status
                      _buildStatusRow('App Components', _providersInitialized),
                      _buildStatusRow(
                        'Mission Provider',
                        _missionProviderReady,
                      ),
                      _buildStatusRow(
                        'Mastery Provider',
                        _masteryProviderReady,
                      ),
                      _buildStatusRow('App History', _appHistoryProviderReady),
                      _buildStatusRow('AI Guardian', _aiGuardianReady),
                      _buildStatusRow('The Imperium', _imperiumReady),
                      _buildStatusRow('Conquest AI', _conquestAIReady),
                      _buildStatusRow(
                        'Data Validation',
                        _dataValidationComplete,
                      ),
                    ],
                  ),
                ),

  // Loading animation
                if (_isLoading) ...[
                  const SizedBox(height: 30),
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusRow(String label, bool isReady) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
          Icon(
            isReady ? Icons.check_circle : Icons.pending,
            color: isReady ? Colors.green : Colors.orange,
            size: 16,
          ),
        ],
      ),
    );
  }
}
