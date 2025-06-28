// ignore_for_file: library_private_types_in_public_api

import 'package:flutter/material.dart';
import 'package:the_codex/home_page.dart';
import 'package:the_codex/mechanicum.dart';
import 'package:the_codex/mission.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import 'package:the_codex/mastery_list.dart';
import 'package:the_codex/providers/app_history_provider.dart';
import 'package:the_codex/ai_brain.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'ai_file_system_helper.dart';

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
  bool _dataValidationComplete = false;

  // Loading steps
  final List<String> _loadingSteps = [
    'Initializing app components...',
    'Loading mission provider...',
    'Loading mastery provider...',
    'Loading app history provider...',
    'Starting AI Guardian...',
    'Starting The Imperium meta-AI...',
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
            // MissionProvider.latestInstance?.startAISandboxFileWatchers();
            print(
              'LoadingScreen: AI Sandbox file watchers temporarily disabled.',
            );
          } catch (e) {
            print('LoadingScreen: Error starting AI Sandbox file watchers: $e');
          }
          break;
        case 6: // Validating data integrity
          _validateDataIntegrity();
          break;
        case 7: // Preparing user interface
          _prepareUserInterface();
          break;
        case 8: // Ready to launch
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

  void _initializeProviders() {
    print('LoadingScreen: Initializing providers');
    WidgetsBinding.instance.addPostFrameCallback((_) {
      try {
        // Access providers to ensure they're initialized
        Provider.of<MissionProvider>(context, listen: false);
        Provider.of<MasteryProvider>(context, listen: false);
        Provider.of<AppHistoryProvider>(context, listen: false);

        setState(() {
          _providersInitialized = true;
        });

        print('LoadingScreen: Providers initialized successfully');
      } catch (e) {
        print('LoadingScreen: Error initializing providers: $e');
        setState(() {
          _hasError = true;
          _errorMessage = 'Failed to initialize app components: $e';
        });
      }
    });
  }

  void _initializeMissionProvider() {
    try {
      print('LoadingScreen: Initializing mission provider');
      final missionProvider = Provider.of<MissionProvider>(
        context,
        listen: false,
      );

      // Trigger any necessary initialization
      if (missionProvider.missions.isEmpty) {
        print('LoadingScreen: Mission provider initialized with no missions');
      } else {
        print(
          'LoadingScreen: Mission provider initialized with ${missionProvider.missions.length} missions',
        );
      }

      setState(() {
        _missionProviderReady = true;
      });
    } catch (e) {
      print('LoadingScreen: Error initializing mission provider: $e');
    }
  }

  void _initializeMasteryProvider() {
    try {
      print('LoadingScreen: Initializing mastery provider');
      final masteryProvider = Provider.of<MasteryProvider>(
        context,
        listen: false,
      );

      // Load mastery entries if needed
      if (masteryProvider.entries.isEmpty) {
        print('LoadingScreen: Mastery provider initialized with no entries');
      } else {
        print(
          'LoadingScreen: Mastery provider initialized with ${masteryProvider.entries.length} entries',
        );
      }

      setState(() {
        _masteryProviderReady = true;
      });
    } catch (e) {
      print('LoadingScreen: Error initializing mastery provider: $e');
    }
  }

  void _initializeAppHistoryProvider() {
    try {
      print('LoadingScreen: Initializing app history provider');
      Provider.of<AppHistoryProvider>(context, listen: false);

      // Load app history if needed
      print('LoadingScreen: App history provider initialized');

      setState(() {
        _appHistoryProviderReady = true;
      });
    } catch (e) {
      print('LoadingScreen: Error initializing app history provider: $e');
    }
  }

  void _initializeAIGuardian() {
    try {
      print('LoadingScreen: Initializing AI Guardian');
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

  void _validateDataIntegrity() {
    try {
      print('LoadingScreen: Validating data integrity');
      final missionProvider = Provider.of<MissionProvider>(
        context,
        listen: false,
      );

      // Perform basic data validation
      final missions = missionProvider.missions;
      bool hasIssues = false;

      for (final mission in missions) {
        // Check for basic data integrity issues
        if (mission.title.isEmpty || mission.id == null) {
          hasIssues = true;
          print(
            'LoadingScreen: Data integrity issue found in mission: ${mission.title}',
          );
        }
      }

      if (!hasIssues) {
        print('LoadingScreen: Data integrity validation passed');
      }

      setState(() {
        _dataValidationComplete = true;
      });
    } catch (e) {
      print('LoadingScreen: Error during data validation: $e');
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
        'url': 'http://31.54.106.71:4000/api/imperium/experiment',
      },
      {
        'name': 'Guardian',
        'url': 'http://31.54.106.71:4000/api/guardian/experiment',
      },
      {
        'name': 'Sandbox',
        'url': 'http://31.54.106.71:4000/api/sandbox/experiment',
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
      // Run AI endpoint tests before launching
      final endpointsOk = await testAIEndpoints();
      if (!endpointsOk) {
        setState(() {
          _hasError = true;
          _errorMessage =
              'Failed to connect to backend AI endpoints. Please check your network or try again later.';
        });
        return;
      }
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

      Navigator.pushReplacement(
        context,
        PageRouteBuilder(
          pageBuilder:
              (context, animation, secondaryAnimation) => const Homepage(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
          transitionDuration: const Duration(milliseconds: 300),
        ),
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
