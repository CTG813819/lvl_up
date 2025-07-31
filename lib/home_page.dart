import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:the_codex/ai_brain.dart';
import 'package:the_codex/entries/add_entry.dart';
import 'package:the_codex/entries/entry_pin_screen.dart';
import 'package:the_codex/side_menu.dart';
import './widgets/front_view.dart';
import './widgets/system_status_indicator.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import './mission.dart'
    show MissionProvider; // Use MissionProvider from mission.dart
import 'package:image_picker/image_picker.dart';
import 'package:palette_generator/palette_generator.dart';
import './entry_manager.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'dart:async';
import './ai_brain.dart';
import './widgets/notification_bell.dart';
import './providers/system_status_provider.dart';

import './providers/proposal_provider.dart';
import './providers/ai_learning_provider.dart';
import './providers/app_history_provider.dart';
import './providers/theme_provider.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'services/network_config.dart';

class Homepage extends StatefulWidget {
  const Homepage({super.key});

  @override
  State<Homepage> createState() => _HomepageState();
}

class _HomepageState extends State<Homepage> with TickerProviderStateMixin {
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  Color dominantColor = Colors.white;
  Color contrastingColor = Colors.black;
  bool _isInitialized = false;
  bool _hasError = false;
  String? _errorMessage;

  Future<void> _refreshData() async {
    try {
  // Refresh date/time
      setState(() {
        _updateDateTime();
      });

  // Refresh missions
      try {
        await Provider.of<MissionProvider>(
          context,
          listen: false,
        ).refreshMissions();
      } catch (e) {
        print('Error refreshing missions: $e');
      }

  // Refresh proposals
      try {
        await Provider.of<ProposalProvider>(
          context,
          listen: false,
        ).fetchAllProposals?.call();
      } catch (e) {
        print('Error refreshing proposals: $e');
      }

  // Refresh AI learning
      try {
        await Provider.of<AILearningProvider>(
          context,
          listen: false,
        ).fetchAIStatus?.call();
        await Provider.of<AILearningProvider>(
          context,
          listen: false,
        ).fetchLearningData?.call();
        await Provider.of<AILearningProvider>(
          context,
          listen: false,
        ).fetchLearningMetrics?.call();
      } catch (e) {
        print('Error refreshing AI learning: $e');
      }

  // Refresh app history
      try {
        await Provider.of<AppHistoryProvider>(
          context,
          listen: false,
        ).loadHistory();
      } catch (e) {
        print('Error refreshing app history: $e');
      }
    } catch (e) {
      print('Error in _refreshData: $e');
      setState(() {
        _hasError = true;
        _errorMessage = 'Error refreshing data: $e';
      });
    }
  }

  @override
  void initState() {
    super.initState();
    print('HomePage: initState called');

    try {
  // Initialize providers and UI
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _initializeProviders();
        }
      });
    } catch (e) {
      print('Error in initState: $e');
      setState(() {
        _hasError = true;
        _errorMessage = 'Error initializing: $e';
      });
    }
  }

  Future<void> _initializeProviders() async {
    try {
      print('HomePage: Initializing providers...');

  // Wait a bit for providers to be available
      await Future.delayed(const Duration(milliseconds: 100));

  // Initialize all providers with individual error handling
      try {
        final missionProvider = Provider.of<MissionProvider>(
          context,
          listen: false,
        );
        print('HomePage: MissionProvider initialized');

  // Start AI Sandbox
        print('HomePage: Starting AI Sandbox');
        missionProvider.startAISandbox();
      } catch (e) {
        print('HomePage: Error with MissionProvider: $e');
  // Retry after a delay
        await Future.delayed(const Duration(seconds: 1));
        try {
          final missionProvider = Provider.of<MissionProvider>(
            context,
            listen: false,
          );
          print('HomePage: MissionProvider initialized on retry');
          missionProvider.startAISandbox();
        } catch (e2) {
          print('HomePage: MissionProvider retry failed: $e2');
        }
      }

      try {
        final proposalProvider = Provider.of<ProposalProvider>(
          context,
          listen: false,
        );
        print('HomePage: ProposalProvider initialized');
      } catch (e) {
        print('HomePage: Error with ProposalProvider: $e');
      }

      try {
        final aiLearningProvider = Provider.of<AILearningProvider>(
          context,
          listen: false,
        );
        print('HomePage: AILearningProvider initialized');
      } catch (e) {
        print('HomePage: Error with AILearningProvider: $e');
      }

      try {
        final appHistoryProvider = Provider.of<AppHistoryProvider>(
          context,
          listen: false,
        );
        print('HomePage: AppHistoryProvider initialized');
      } catch (e) {
        print('HomePage: Error with AppHistoryProvider: $e');
      }

      try {
        final systemStatusProvider = Provider.of<SystemStatusProvider>(
          context,
          listen: false,
        );
        print('HomePage: SystemStatusProvider initialized');
      } catch (e) {
        print('HomePage: Error with SystemStatusProvider: $e');
      }

  // Start AI progress monitoring for Dynamic Island notifications

      setState(() {
        _isInitialized = true;
      });

      print('HomePage: All providers initialized successfully');
    } catch (e) {
      print('HomePage: Error in _initializeProviders: $e');
      setState(() {
        _hasError = true;
        _errorMessage = 'Error initializing providers: $e';
      });
    }
  }

  Future<void> _initializeNotifications() async {
    try {
      print('HomePage: Initializing notifications...');

  // Wait a bit for providers to be available
      await Future.delayed(const Duration(milliseconds: 100));

      final missionProvider = Provider.of<MissionProvider>(
        context,
        listen: false,
      );

  // Start notifications with proper error handling
      await missionProvider.startNotifications();

      print('HomePage: Notifications initialized successfully');
    } catch (e) {
      print('HomePage: Error initializing notifications: $e');
  // Retry after a delay if there's an error
      Timer(const Duration(seconds: 2), () {
        if (mounted) {
          _initializeNotifications();
        }
      });
    }
  }

  void _updateDateTime() {
  // This method is kept for potential future use but simplified
    final now = DateTime.now();
    setState(() {
  // Update any time-dependent UI elements here if needed
    });
  }

  void _showThemeDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Theme Settings'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.dark_mode),
                title: const Text('Dark Theme'),
                onTap: () async {
                  Navigator.of(context).pop();
                  await _setThemeMode(ThemeMode.dark);
                },
              ),
              ListTile(
                leading: const Icon(Icons.light_mode),
                title: const Text('Light Theme'),
                onTap: () async {
                  Navigator.of(context).pop();
                  await _setThemeMode(ThemeMode.light);
                },
              ),
              ListTile(
                leading: const Icon(Icons.settings_system_daydream),
                title: const Text('System Theme'),
                onTap: () async {
                  Navigator.of(context).pop();
                  await _setThemeMode(ThemeMode.system);
                },
              ),
            ],
          ),
          actions: <Widget>[
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
              },
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _setThemeMode(ThemeMode mode) async {
    try {
      final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
      await themeProvider.setThemeMode(mode);

  // Show a snackbar to indicate the theme change
      if (mounted) {
        String themeName;
        switch (mode) {
          case ThemeMode.dark:
            themeName = 'Dark';
            break;
          case ThemeMode.light:
            themeName = 'Light';
            break;
          case ThemeMode.system:
            themeName = 'System';
            break;
        }

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Theme changed to $themeName mode.'),
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      print('Error setting theme mode: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );

  // Show loading state if not initialized
    if (!_isInitialized) {
      return Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
              const SizedBox(height: 20),
              const Text(
                'Initializing...',
                style: TextStyle(color: Colors.white, fontSize: 18),
              ),
            ],
          ),
        ),
      );
    }

  // Show error state if there's an error
    if (_hasError) {
      return Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, color: Colors.red, size: 64),
              const SizedBox(height: 20),
              Text(
                'Error: $_errorMessage',
                style: const TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _hasError = false;
                    _errorMessage = null;
                    _isInitialized = false;
                  });
                  _initializeProviders();
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: const Color.fromARGB(0, 255, 255, 255),
        leading: IconButton(
          icon: Icon(
            Icons.menu,
            color:
                Theme.of(context).brightness == Brightness.dark
                    ? Colors.white
                    : Colors.black,
          ),
          onPressed: () {
            _scaffoldKey.currentState?.openDrawer();
          },
        ),
        title: Row(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
  // System Status Indicator
            Consumer<SystemStatusProvider>(
              builder: (context, statusProvider, child) {
                return SystemStatusIndicator(showText: false, size: 20);
              },
            ),
            const SizedBox(width: 12),
  // Theme toggle button in the center of the AppBar
            Consumer<ThemeProvider>(
              builder: (context, themeProvider, child) {
                return IconButton(
                  icon: Icon(
                    themeProvider.themeMode == ThemeMode.dark
                        ? Icons.dark_mode
                        : Icons.light_mode,
                    color:
                        Theme.of(context).brightness == Brightness.dark
                            ? Colors.white
                            : Colors.black,
                    size: 28,
                  ),
                  onPressed: () async {
                    await themeProvider.toggleTheme();
                  },
                  tooltip: 'Toggle Theme',
                );
              },
            ),
          ],
        ),
        actions: [
  // Imperium Dashboard Web Icon
          IconButton(
            icon: Icon(Icons.language, color: contrastingColor, size: 28),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder:
                      (context) => Scaffold(
                        appBar: AppBar(title: const Text('Imperium Dashboard')),
                        body: WebViewWidget(
                          controller:
                              WebViewController()
                                ..setJavaScriptMode(JavaScriptMode.unrestricted)
                                ..loadRequest(
                                  Uri.parse(
                                    '${NetworkConfig.apiBaseUrl}/api/imperium/dashboard',
                                  ),
                                ),
                        ),
                      ),
                ),
              );
            },
          ),
        ],
      ),
      extendBodyBehindAppBar: true,
      drawer: Consumer<MissionProvider>(
        builder: (context, missionProvider, child) {
          return SideMenu(parentContext: context);
        },
      ),
      body: Stack(
        children: [
          RefreshIndicator(
            onRefresh: _refreshData,
            color: Theme.of(context).primaryColor,
            child: Column(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 24.0),
                    child: SpatialHypergraphView(
                      isDarkMode:
                          Theme.of(context).brightness == Brightness.dark,
                    ),
                  ),
                ),
                const SizedBox(height: 30.0),
              ],
            ),
          ),
  // Dynamic Island notifications are now handled by the DynamicIslandProvider
        ],
      ),
    );
  }
}
