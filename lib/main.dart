import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:provider/provider.dart';
import 'package:the_codex/ai_guardian_analytics_screen.dart';
import 'package:the_codex/mission_widget.dart';
import 'package:the_codex/screens/notification_center_screen.dart';
import 'package:the_codex/screens/proposal_approval_screen.dart';
import 'dart:async';
import 'models/entry.dart';
import 'loading_screen.dart';
import 'home_page.dart';
import 'mission.dart' show MissionProvider, MasteryProvider;
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
import 'providers/chaos_warp_provider.dart';
import 'services/notification_service.dart';
import 'package:pinput/pinput.dart';
import 'package:workmanager/workmanager.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import './mechanicum.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:shared_preferences/shared_preferences.dart';
import 'theme.dart';

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
    Hive.registerAdapter(EntryAdapter());
    await Hive.openBox<Entry>('entries');
    await Hive.openBox<String>('images');
    await NotificationService.instance.initialize(); // Initialize notification service
    print('Hive initialized successfully');

    // Set system UI overlay style
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );

    print('Initializing notifications...');
    // Initialize notifications for foreground
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    final InitializationSettings initializationSettings =
        InitializationSettings(android: initializationSettingsAndroid);
    await flutterLocalNotificationsPlugin.initialize(initializationSettings);
    print('Notifications initialized');

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

    // Initialize Socket.IO client for real-time notifications
    final IO.Socket socket = IO.io(
      'http://31.54.106.71:4000',
      IO.OptionBuilder()
        .setTransports(['websocket'])
        .disableAutoConnect() // We'll connect manually
        .build(),
    );
    socket.connect();
    socket.onConnect((_) {
      print('Socket.IO connected!');
    });
    socket.onDisconnect((_) {
      print('Socket.IO disconnected!');
    });
    socket.on('proposal:applied', (data) {
      print('[SOCKET] Proposal applied: $data');
      final aiType = data['aiType'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      final prUrl = data['prUrl'] ?? '';
      NotificationService.instance.showNotification(
        aiSource: aiType,
        message: 'Proposal applied to $filePath. PR: $prUrl',
        iconChar: '🚀',
      );
    });

    socket.on('proposal:created', (data) {
      print('[SOCKET] Proposal created: $data');
      final aiType = data['aiType'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      NotificationService.instance.showNotification(
        aiSource: aiType,
        message: 'New proposal for $filePath.',
        iconChar: '💡',
      );
    });

    socket.on('proposal:approved', (data) {
      print('[SOCKET] Proposal approved: $data');
      final aiType = data['aiType'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      NotificationService.instance.showNotification(
        aiSource: aiType,
        message: 'Proposal for $filePath approved.',
        iconChar: '✅',
      );
    });

    socket.on('proposal:rejected', (data) {
      print('[SOCKET] Proposal rejected: $data');
      final aiType = data['aiType'] ?? 'AI';
      final filePath = data['filePath'] ?? 'unknown file';
      NotificationService.instance.showNotification(
        aiSource: aiType,
        message: 'Proposal for $filePath rejected.',
        iconChar: '❌',
      );
    });

    // Listen for AI pulling from GitHub
    socket.on('ai:pull', (data) {
      print('[SOCKET] AI Pull: $data');
      final ai = data['ai'] ?? 'AI';
      final message = data['message'] ?? 'AI is pulling latest code from GitHub.';
      NotificationService.instance.showNotification(
        aiSource: ai,
        message: message,
        iconChar: '🔄',
      );
    });

    // Initialize shared preferences
    await SharedPreferences.getInstance();

    runApp(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => MissionProvider(), lazy: false),
          ChangeNotifierProvider(create: (_) => MasteryProvider()),
          ChangeNotifierProvider(create: (_) => AppHistoryProvider()),
          ChangeNotifierProvider(create: (_) => NotificationProvider()),
          ChangeNotifierProvider(create: (_) => AILearningProvider()),
          ChangeNotifierProxyProvider<AILearningProvider, ProposalProvider>(
            create: (_) => ProposalProvider(),
            update: (_, aiLearningProvider, proposalProvider) {
              proposalProvider ??= ProposalProvider();
              proposalProvider.initialize(aiLearningProvider: aiLearningProvider);
              return proposalProvider;
            },
          ),
          ChangeNotifierProvider(create: (_) => ChaosWarpProvider()),
        ],
        child: MaterialApp(
          title: 'LVL UP',
          navigatorKey: navigatorKey,
          theme: ThemeData(
            primarySwatch: Colors.blue,
            brightness: Brightness.light,
          ),
          darkTheme: ThemeData(
            primarySwatch: Colors.blue,
            brightness: Brightness.dark,
          ),
          themeMode: ThemeMode.system,
          home: LoadingScreen(onVideoComplete: () {}),
          debugShowCheckedModeBanner: false,
          routes: {
            '/home': (context) => const Homepage(),
            AddEntry.routeName: (context) => const AddEntry(),
            ListEntries.routeName: (context) => const ListEntries(),
            ViewEntry.routeName:
                (context) => ViewEntry(
                  entry: ModalRoute.of(context)!.settings.arguments as Entry,
                ),
            EditEntry.routeName:
                (context) => EditEntry(
                  entry: ModalRoute.of(context)!.settings.arguments as Entry,
                ),
            '/tally': (context) => const Tally(),
            '/summary': (context) => const SummaryPage(),
            '/mastery': (context) => const MasteryList(),
            '/mission': (context) => const Mission(),
            '/app_history': (context) => const AppHistoryScreen(),
            '/mechanicum_analytics':
                (context) => const MechanicumAnalyticsScreen(),
            '/notification_center': (context) => const NotificationCenterScreen(),
            '/proposal_approval': (context) => const ProposalApprovalScreen(),
          },
          builder: (context, child) {
            // Initialize ChaosWarpProvider
            WidgetsBinding.instance.addPostFrameCallback((_) {
              final chaosWarpProvider = Provider.of<ChaosWarpProvider>(context, listen: false);
              chaosWarpProvider.getStatus();
              chaosWarpProvider.startStatusPolling();
            });
            return child!;
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
