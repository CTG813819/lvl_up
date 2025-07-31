import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/ai_guardian_analytics_screen.dart';
import 'package:the_codex/mission_widget.dart';
import 'package:the_codex/screens/notification_center_screen.dart';
import 'package:the_codex/screens/proposal_approval_screen.dart';
import 'package:the_codex/screens/conquest_screen.dart';
import 'package:the_codex/screens/conquest_apps_screen.dart';
import 'package:the_codex/screens/ai_growth_analytics_screen.dart';
import 'package:the_codex/screens/dynamic_island_settings_screen.dart';
import 'dart:async';
import 'models/entry.dart';
import 'loading_screen.dart';
import 'home_page.dart';

import 'mission.dart'
    show MissionProvider; // Use MissionProvider from mission.dart
import 'entries/add_entry.dart';
import 'entries/list_entries.dart';
import 'entries/view_entry.dart';
import 'entries/edit_entry.dart';
import 'mastery_list.dart';
import 'tally.dart';
import 'summary_page.dart';
import 'screens/app_history_screen.dart';
import 'providers/app_history_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/proposal_provider.dart';
import 'providers/ai_learning_provider.dart';
import 'providers/conquest_ai_provider.dart';
import 'providers/system_status_provider.dart';
import 'providers/theme_provider.dart';
import 'services/notification_service.dart';
import 'services/app_logger.dart';
import 'services/websocket_service.dart';
import 'services/ai_progress_notification_service.dart';
import 'package:pinput/pinput.dart';
import 'package:workmanager/workmanager.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import './mechanicum.dart';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'theme.dart';
import 'providers/oath_papers_provider.dart';
import 'providers/ai_growth_analytics_provider.dart';
import 'providers/ai_customization_provider.dart';
import 'app_pin_entry_screen.dart';
import 'package:the_codex/screens/oath_papers_screen.dart';
import 'package:the_codex/screens/book_of_lorgar_screen.dart';
import 'test_home_page.dart';
import 'widgets/front_view.dart';
import 'guardian_service.dart';
import 'services/network_config.dart';
import 'side_menu.dart' show DynamicIslandManager;

// Global Key for Navigator
final navigatorKey = GlobalKey<NavigatorState>();

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    // Initialize notifications for background
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    final InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);
    await flutterLocalNotificationsPlugin.initialize(initializationSettings);

    // Run both AIs in the background
    await Mechanicum.backgroundGuardianAndSandbox();
    return Future.value(true);
  });
}

void main() async {
  print('HELLO FROM MAIN');

  try {
    WidgetsFlutterBinding.ensureInitialized();
    print('Flutter binding initialized');

    // Initialize AppLogger early to capture all logs
    AppLogger.instance.initialize();
    print('AppLogger initialized');

    // Add global error handler to catch stack overflow and other errors
    FlutterError.onError = (FlutterErrorDetails details) {
      FlutterError.dumpErrorToConsole(details);
      if (details.exceptionAsString().contains('Stack Overflow')) {
        print('🚨 STACK OVERFLOW DETECTED 🚨');
        print('Exception: ${details.exception}');
        print('Stack trace: ${details.stack}');
      }
    };

    print('Initializing Hive...');
    // Initialize Hive
    await Hive.initFlutter();

    // Register adapters with error handling to prevent duplicate registration
    try {
      Hive.registerAdapter(EntryAdapter());
    } catch (e) {
      print('EntryAdapter already registered: $e');
    }

    await Hive.openBox<Entry>('entries');
    await Hive.openBox<String>('images');

    // Initialize notification service with error handling
    try {
      await NotificationService.instance.initialize();
      print('NotificationService initialized successfully');
    } catch (e) {
      print('NotificationService initialization failed: $e');
      // Continue without notifications
    }

    // Initialize WebSocket service for real-time updates
    try {
      await WebSocketService.instance.initialize();
      print('WebSocketService initialized successfully');
    } catch (e) {
      print('WebSocketService initialization failed: $e');
      // Continue without WebSocket
    }

    // Initialize AI Progress Notification Service
    try {
      await AIProgressNotificationService.instance.initialize();
      print('AIProgressNotificationService initialized successfully');
    } catch (e) {
      print('AIProgressNotificationService initialization failed: $e');
      // Continue without AI progress notifications
    }

    print('Hive initialized successfully');

    // Set system UI overlay style
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );

    print('Initializing notifications...');
    // Initialize notifications for foreground with error handling
    try {
      const AndroidInitializationSettings initializationSettingsAndroid =
          AndroidInitializationSettings('@drawable/notification_icon');
      final InitializationSettings initializationSettings =
          InitializationSettings(android: initializationSettingsAndroid);
      await flutterLocalNotificationsPlugin.initialize(initializationSettings);
      print('Notifications initialized');
    } catch (e) {
      print('Notifications initialization failed: $e');
      // Continue without notifications
    }

    print('Initializing Workmanager...');
    // Initialize Workmanager
    Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
    Workmanager().registerPeriodicTask(
      "ai_background_task",
      "aiBackgroundTask",
      frequency: Duration(minutes: 30), // 30 min interval
    );
    print('Workmanager initialized');

    print('Starting app...');

    // Initialize WebSocket client for real-time notifications
    try {
      final channel = WebSocketChannel.connect(
        Uri.parse('ws://34.202.215.209:8000/api/imperium/status'),
      );

      channel.stream.listen(
        (data) {
          print('[WEBSOCKET] Received: $data');
          try {
            final message = jsonDecode(data.toString());
            if (message['type'] == 'proposal:applied') {
              final aiType = message['aiType'] ?? 'AI';
              final filePath = message['filePath'] ?? 'unknown file';
              final prUrl = message['prUrl'] ?? '';
              NotificationService.instance.showNotification(
                aiSource: aiType,
                message: 'Proposal applied to $filePath. PR: $prUrl',
                iconChar: '🚀',
              );
            }
          } catch (e) {
            print('[WEBSOCKET] Error parsing message: $e');
          }
        },
        onError: (error) {
          print('[WEBSOCKET] Error: $error');
        },
        onDone: () {
          print('[WEBSOCKET] Connection closed');
        },
      );

      print('[WEBSOCKET] Connected to backend');
    } catch (e) {
      print('[WEBSOCKET] Connection failed: $e');
    }

    // Initialize shared preferences
    await SharedPreferences.getInstance();

    // Enable notifications after app is ready
    NotificationService.enableNotifications();

    runApp(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => AppHistoryProvider()),
          ChangeNotifierProvider(create: (_) => NotificationProvider()),
          ChangeNotifierProvider(create: (_) => MasteryProvider()),
          ChangeNotifierProvider(create: (_) => OathPapersProvider()),
          ChangeNotifierProvider(create: (_) => SystemStatusProvider()),
          ChangeNotifierProvider<MissionProvider>(
            create: (_) => MissionProvider(),
            lazy: false,
          ),
          ChangeNotifierProvider<ProposalProvider>(
            create: (_) => ProposalProvider(),
            lazy: false,
          ),
          ChangeNotifierProvider<AILearningProvider>(
            create: (_) => AILearningProvider(),
            lazy: false,
          ),
          ChangeNotifierProvider<AIGrowthAnalyticsProvider>(
            create: (_) {
              final provider = AIGrowthAnalyticsProvider();
              provider.initialize();
              return provider;
            },
            lazy: false,
          ),
          ChangeNotifierProvider<ConquestAIProvider>(
            create: (_) => ConquestAIProvider(),
            lazy: false,
          ),

          ChangeNotifierProvider<AICustomizationProvider>(
            create: (_) => AICustomizationProvider(),
            lazy: false,
          ),
          ChangeNotifierProvider<ThemeProvider>(
            create: (_) => ThemeProvider(),
            lazy: false,
          ),
        ],
        child: Consumer<ThemeProvider>(
          builder: (context, themeProvider, child) {
            return MaterialApp(
              title: 'Imperium Growth Matrix',
              navigatorKey: navigatorKey,
              theme: ThemeData(
                brightness:
                    themeProvider.themeMode == ThemeMode.dark
                        ? Brightness.dark
                        : Brightness.light,
                primarySwatch: Colors.blue,
                scaffoldBackgroundColor:
                    themeProvider.themeMode == ThemeMode.dark
                        ? Colors.black
                        : Colors.white,
                floatingActionButtonTheme: FloatingActionButtonThemeData(
                  backgroundColor:
                      themeProvider.themeMode == ThemeMode.dark
                          ? Colors.white
                          : Colors.black,
                ),
              ),
              darkTheme: ThemeData(
                brightness: Brightness.dark,
                primarySwatch: Colors.blue,
                scaffoldBackgroundColor: Colors.black,
                floatingActionButtonTheme: FloatingActionButtonThemeData(
                  backgroundColor: Colors.white,
                ),
              ),
              themeMode: themeProvider.themeMode,
              home: HomeScreen(
                isDarkMode: themeProvider.themeMode == ThemeMode.dark,
                onToggleTheme: () {
                  themeProvider.toggleTheme();
                },
              ),
              debugShowCheckedModeBanner: false,
              routes: {
                '/home': (context) => const Homepage(),
                AddEntry.routeName: (context) => const AddEntry(),
                ListEntries.routeName: (context) => const ListEntries(),
                ViewEntry.routeName:
                    (context) => ViewEntry(
                      entry:
                          ModalRoute.of(context)!.settings.arguments as Entry,
                    ),
                EditEntry.routeName:
                    (context) => EditEntry(
                      entry:
                          ModalRoute.of(context)!.settings.arguments as Entry,
                    ),
                '/tally': (context) => const Tally(),
                '/summary': (context) => const SummaryPage(),
                '/mastery': (context) => const MasteryList(),
                '/mission': (context) => const Mission(),
                '/app_history': (context) => const AppHistoryScreen(),
                '/mechanicum_analytics':
                    (context) => const MechanicumAnalyticsScreen(),
                '/ai_growth_analytics':
                    (context) => const AIGrowthAnalyticsScreen(),
                '/dynamic_island_settings':
                    (context) => const DynamicIslandSettingsScreen(),
                OathPapersScreen.routeName:
                    (context) => const OathPapersScreen(),
                '/notification_center':
                    (context) => const NotificationCenterScreen(),
                '/proposal_approval':
                    (context) => const ProposalApprovalScreen(),
                '/conquest': (context) => const ConquestScreen(),
                '/conquest-apps': (context) => const ConquestAppsScreen(),
                '/book_of_lorgar': (context) => const BookOfLorgarScreen(),
                '/test': (context) => const TestHomePage(),
              },
              onGenerateRoute: (settings) {
                // Handle dynamic routes or routes with arguments
                if (settings.name == OathPapersScreen.routeName) {
                  return MaterialPageRoute(
                    builder: (context) => const OathPapersScreen(),
                    settings: settings,
                  );
                }
                return null;
              },
              builder: (context, child) {
                // Initialize GuardianService with context
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  GuardianService.initialize(context);
                });
                // Initialize MissionProvider
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  final missionProvider = Provider.of<MissionProvider>(
                    context,
                    listen: false,
                  );
                  // missionProvider.getStatus(); // Removed as per edit hint
                  // missionProvider.startStatusPolling(); // Removed as per edit hint
                });

                // Initialize AI Progress Notification Service monitoring
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  AIProgressNotificationService.instance.startMonitoring(
                    context,
                  );
                });
                return child!;
              },
            );
          },
        ),
      ),
    );
    print('App started successfully');
  } catch (e, stackTrace) {
    print('ERROR IN MAIN: $e');
    print('Stack trace: $stackTrace');

    // Fallback app in case of error
    runApp(
      MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text('App Error', style: TextStyle(fontSize: 24)),
                const SizedBox(height: 16),
                Text('Error: $e', style: const TextStyle(fontSize: 16)),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    // Restart the app
                    main();
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;
  const HomeScreen({
    Key? key,
    required this.isDarkMode,
    required this.onToggleTheme,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return _AppPinGate();
  }
}

class _AppPinGate extends StatefulWidget {
  @override
  State<_AppPinGate> createState() => _AppPinGateState();
}

class _AppPinGateState extends State<_AppPinGate> {
  bool _pinVerified = false;
  bool _loadingComplete = false;

  void _onPinEntered(String pin, BuildContext context) {
    setState(() {
      _pinVerified = true;
    });
  }

  void _onLoadingComplete() {
    setState(() {
      _loadingComplete = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_pinVerified) {
      return AppPinEntryScreen(
        onPinEntered: _onPinEntered,
        title: 'Enter App PIN',
      );
    }
    if (!_loadingComplete) {
      return LoadingScreen(onVideoComplete: _onLoadingComplete);
    }
    // After loading is complete, show the homepage
    return const Homepage();
  }
}

// SetPinScreen and PinEntryScreen remain unchanged
class SetPinScreen extends StatefulWidget {
  final Function(String) onPinSet;
  const SetPinScreen({required this.onPinSet, super.key});
  @override
  _SetPinScreenState createState() => _SetPinScreenState();
}

class _SetPinScreenState extends State<SetPinScreen> {
  String newPin = '';
  String confirmPin = '';
  bool isConfirming = false;
  String errorMessage = '';
  final pinController = TextEditingController();

  final defaultPinTheme = PinTheme(
    width: 56,
    height: 56,
    textStyle: const TextStyle(fontSize: 20, color: Colors.black),
    decoration: BoxDecoration(
      color: Colors.white,
      border: Border.all(color: Colors.white),
      borderRadius: BorderRadius.circular(8),
    ),
  );

  @override
  void dispose() {
    pinController.dispose();
    super.dispose();
  }

  void _clearPinInput() {
    pinController.clear();
    setState(() {
      confirmPin = '';
      errorMessage = '';
    });
  }

  @override
  Widget build(BuildContext context) {
    final focusedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.green,
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final submittedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.green,
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final errorPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.red,
        border: Border.all(color: Colors.red),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                isConfirming ? 'Confirm Your PIN' : 'Set Your PIN',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'PIN must be 6 digits',
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              Pinput(
                controller: pinController,
                length: 6,
                defaultPinTheme: defaultPinTheme,
                focusedPinTheme: focusedPinTheme,
                submittedPinTheme: submittedPinTheme,
                errorPinTheme: errorMessage.isNotEmpty ? errorPinTheme : null,
                obscureText: true,
                keyboardType: TextInputType.number,
                onChanged: (value) {
                  setState(() {
                    errorMessage = '';
                    if (isConfirming) {
                      confirmPin = value;
                    } else {
                      newPin = value;
                    }
                    debugPrint(
                      'Pinput changed: $value, isConfirming: $isConfirming',
                    );
                  });
                },
                onCompleted: (value) {
                  debugPrint('Pinput completed: $value');
                  if (!isConfirming) {
                    if (value.length == 6 && RegExp(r'^\d+$').hasMatch(value)) {
                      setState(() {
                        newPin = value;
                        isConfirming = true;
                        debugPrint('New PIN set, switching to confirm mode');
                      });
                      _clearPinInput();
                    } else {
                      setState(() {
                        errorMessage = 'PIN must be 6 digits';
                        debugPrint('Invalid PIN: $value');
                      });
                    }
                  } else {
                    if (value == newPin) {
                      debugPrint('PIN confirmed, calling onPinSet');
                      widget.onPinSet(value);
                    } else {
                      setState(() {
                        errorMessage = 'PINs do not match';
                        debugPrint('PINs do not match');
                      });
                      _clearPinInput();
                    }
                  }
                },
              ),
              if (errorMessage.isNotEmpty) ...[
                const SizedBox(height: 16),
                Text(
                  errorMessage,
                  style: const TextStyle(color: Colors.red, fontSize: 16),
                ),
              ],
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  debugPrint(
                    'Button pressed, isConfirming: $isConfirming, newPin: $newPin, confirmPin: $confirmPin',
                  );
                  if (!isConfirming && newPin.length == 6) {
                    setState(() {
                      isConfirming = true;
                      debugPrint('Switching to confirm mode');
                    });
                    _clearPinInput();
                  } else if (isConfirming && confirmPin.length == 6) {
                    if (newPin == confirmPin) {
                      debugPrint('PIN confirmed, calling onPinSet');
                      widget.onPinSet(newPin);
                    } else {
                      setState(() {
                        errorMessage = 'PINs do not match';
                        debugPrint('PINs do not match');
                      });
                      _clearPinInput();
                    }
                  } else {
                    setState(() {
                      errorMessage = 'Please enter a 6-digit PIN';
                      debugPrint('Invalid PIN length');
                    });
                  }
                },
                child: Text(isConfirming ? 'Confirm PIN' : 'Set PIN'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class PinEntryScreen extends StatefulWidget {
  final Function(String, BuildContext) onPinEntered;
  const PinEntryScreen({required this.onPinEntered, super.key});
  @override
  _PinEntryScreenState createState() => _PinEntryScreenState();
}

class _PinEntryScreenState extends State<PinEntryScreen> {
  String enteredPin = '';
  String errorMessage = '';
  final pinController = TextEditingController();

  final defaultPinTheme = PinTheme(
    width: 56,
    height: 56,
    textStyle: const TextStyle(fontSize: 20, color: Colors.black),
    decoration: BoxDecoration(
      color: Colors.white,
      border: Border.all(color: Colors.white),
      borderRadius: BorderRadius.circular(8),
    ),
  );

  @override
  void dispose() {
    pinController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final focusedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.green,
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final submittedPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.green,
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    final errorPinTheme = defaultPinTheme.copyWith(
      decoration: BoxDecoration(
        color: Colors.red,
        border: Border.all(color: Colors.red),
        borderRadius: BorderRadius.circular(8),
      ),
    );

    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Builder(
            builder: (BuildContext dialogContext) {
              return Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text(
                    'Enter PIN',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Pinput(
                    controller: pinController,
                    length: 6,
                    defaultPinTheme: defaultPinTheme,
                    focusedPinTheme: focusedPinTheme,
                    submittedPinTheme: submittedPinTheme,
                    errorPinTheme:
                        errorMessage.isNotEmpty ? errorPinTheme : null,
                    obscureText: true,
                    keyboardType: TextInputType.number,
                    onChanged: (value) {
                      setState(() {
                        enteredPin = value;
                        errorMessage = '';
                        debugPrint('PinEntry Pinput changed: $value');
                      });
                    },
                    onCompleted: (value) {
                      debugPrint('PinEntry Pinput completed: $value');
                      widget.onPinEntered(value, dialogContext);
                    },
                  ),
                  if (errorMessage.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      errorMessage,
                      style: const TextStyle(color: Colors.red, fontSize: 16),
                    ),
                  ],
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      debugPrint(
                        'Submit button pressed, enteredPin: $enteredPin',
                      );
                      if (enteredPin.length == 6) {
                        widget.onPinEntered(enteredPin, dialogContext);
                      } else {
                        setState(() {
                          errorMessage = 'PIN must be 6 digits';
                          debugPrint('Invalid PIN length on submit');
                        });
                      }
                    },
                    child: const Text('Submit'),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}
