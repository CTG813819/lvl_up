import 'package:flutter/material.dart';
import 'package:the_codex/mission.dart'
    show MissionProvider; // Use MissionProvider from mission.dart
import './screens/oath_papers_screen.dart';
import 'entries/entry_pin_screen.dart';
import 'package:provider/provider.dart';
import '../providers/notification_provider.dart';
import '../providers/proposal_provider.dart';
import 'codex_screen.dart';
import './summary_page.dart';
import 'screens/audit_results_screen.dart';
import 'screens/proposal_approval_screen.dart';
import 'ai_guardian_analytics_screen.dart';
import 'terra_extension_screen.dart';
import 'dynamic_extension_screen.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
// import 'package:flutter_eval/flutter_eval.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:async';
import './screens/the_warp_screen.dart';
import './screens/training_ground_screen.dart';
import './screens/scheduling_management_screen.dart';
import './screens/project_berserk_screen.dart';
import './widgets/universal_warmaster_hub.dart';

class DynamicIslandManager extends ChangeNotifier {
  //// Set of AI names with active islands
  final Set<String> _activeIslands = {};
  Set<String> get activeIslands => _activeIslands;
  int get count => _activeIslands.length;

  void setActiveIslands(Set<String> ais) {
    _activeIslands.clear();
    _activeIslands.addAll(ais);
    notifyListeners();
  }

  void addIsland(String ai) {
    _activeIslands.add(ai);
    notifyListeners();
  }

  void removeIsland(String ai) {
    _activeIslands.remove(ai);
    notifyListeners();
  }
}

Future<List<Map<String, dynamic>>> fetchApprovedExtensions() async {
  try {
    final resp = await http
        .get(Uri.parse('http://34.202.215.209:8000/api/terra/extensions'))
        .timeout(
          const Duration(seconds: 10),
          onTimeout: () {
            throw TimeoutException(
              'Request timed out',
              const Duration(seconds: 10),
            );
          },
        );

    if (resp.statusCode == 200) {
      return List<Map<String, dynamic>>.from(json.decode(resp.body));
    } else {
      print('Error fetching approved extensions: HTTP ${resp.statusCode}');
      return [];
    }
  } catch (e) {
    print('Error fetching approved extensions: $e');
    return [];
  }
}

Widget buildExtensionMenuItem(BuildContext context, Map<String, dynamic> ext) {
  return ListTile(
    leading: Icon(
      _getIconFromString(ext['icon_name'] ?? 'Icons.star'),
      color: Colors.purple,
    ),
    title: Text(ext['menu_title'] ?? 'Extension'),
    trailing: IconButton(
      icon: Icon(Icons.delete, color: Colors.red),
      onPressed: () => _showDeleteDialog(context, ext),
      tooltip: 'Delete Extension',
    ),
    onTap: () {
      Navigator.pop(context);
      Navigator.push(
        context,
        MaterialPageRoute(
          builder:
              (context) => DynamicExtensionScreen(
                code: ext['dart_code'] ?? '',
                title: ext['menu_title'] ?? 'Extension',
              ),
        ),
      );
    },
  );
}

void _showDeleteDialog(BuildContext context, Map<String, dynamic> ext) {
  showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        title: Text('Delete Extension'),
        content: Text(
          'Are you sure you want to delete "${ext['menu_title'] ?? 'Extension'}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              _deleteExtension(context, ext['id']);
            },
            child: Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      );
    },
  );
}

Future<void> _deleteExtension(BuildContext context, String extensionId) async {
  try {
    final response = await http.delete(
      Uri.parse('http://34.202.215.209:8000/api/terra/extensions/$extensionId'),
    );

    if (response.statusCode == 200) {
      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Extension deleted successfully'),
          backgroundColor: Colors.green,
        ),
      );

      /// Close the dialog and refresh the side menu
      Navigator.of(context).pushNamedAndRemoveUntil('/home', (route) => false);

      /// If we're in a SideMenu widget, refresh it
      if (context.findAncestorStateOfType<_SideMenuState>() != null) {
        final sideMenuState =
            context.findAncestorStateOfType<_SideMenuState>()!;
        await sideMenuState._refreshExtensionCards();
      }
    } else {
      /// Show error message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to delete extension'),
          backgroundColor: Colors.red,
        ),
      );
    }
  } catch (e) {
    /// Show error message
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Error deleting extension: $e'),
        backgroundColor: Colors.red,
      ),
    );
  }
}

IconData _getIconFromString(String iconString) {
  /// Convert string like "Icons.star" to actual IconData
  switch (iconString.toLowerCase()) {
    case 'icons.star':
      return Icons.star;
    case 'icons.favorite':
      return Icons.favorite;
    case 'icons.home':
      return Icons.home;
    case 'icons.settings':
      return Icons.settings;
    case 'icons.person':
      return Icons.person;
    case 'icons.analytics':
      return Icons.analytics;
    case 'icons.code':
      return Icons.code;
    case 'icons.extension':
      return Icons.extension;
    default:
      return Icons.star;
  }
}

class MenuCardData {
  final String id; // unique key for persistence
  final String title;
  final VoidCallback onTap;
  String? imagePath; // nullable, can be set by user
  Map<String, dynamic>? extensionData; // for Terra extensions
  MenuCardData({
    required this.id,
    required this.title,
    required this.onTap,
    this.imagePath,
    this.extensionData,
  });
}

class SideMenu extends StatefulWidget {
  final BuildContext parentContext;
  const SideMenu({Key? key, required this.parentContext}) : super(key: key);

  @override
  State<SideMenu> createState() => _SideMenuState();
}

class _SideMenuState extends State<SideMenu> {
  List<MenuCardData> menuCards = [];
  bool _loadingExtensions = true;
  List<MenuCardData> extensionCards = [];

  @override
  void initState() {
    super.initState();
    _initMenuCards();
    _loadExtensionCards();
  }

  @override
  void dispose() {
    /// Clean up any resources
    super.dispose();
  }

  Future<void> _initMenuCards() async {
    final prefs = await SharedPreferences.getInstance();
    print('Initializing menu cards...'); // Debug print
    setState(() {
      menuCards = [
        MenuCardData(
          id: 'missions',
          title: 'Missions',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/mission'),
          imagePath: prefs.getString('menu_missions'),
        ),
        MenuCardData(
          id: 'summary',
          title: 'Summary',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/summary'),
          imagePath: prefs.getString('menu_summary'),
        ),
        MenuCardData(
          id: 'judgement',
          title: 'Judgement',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/judgement'),
          imagePath: prefs.getString('menu_judgement'),
        ),
        MenuCardData(
          id: 'entries',
          title: 'Entries',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/entries'),
          imagePath: prefs.getString('menu_entries'),
        ),
        MenuCardData(
          id: 'masteries',
          title: 'Masteries',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/masteries'),
          imagePath: prefs.getString('menu_masteries'),
        ),
        MenuCardData(
          id: 'proposals',
          title: 'Imperium Proposals',
          onTap:
              () => Navigator.pushNamed(
                widget.parentContext,
                '/proposal_approval',
              ),
          imagePath: prefs.getString('menu_proposals'),
        ),
        MenuCardData(
          id: 'oath_papers',
          title: 'Oath Papers',
          onTap:
              () => Navigator.pushNamed(widget.parentContext, '/oath_papers'),
          imagePath: prefs.getString('menu_oath_papers'),
        ),
        MenuCardData(
          id: 'mechanicum',
          title: 'Mechanicum',
          onTap: () => Navigator.pushNamed(widget.parentContext, '/conquest'),
          imagePath: prefs.getString('menu_mechanicum'),
        ),
        MenuCardData(
          id: 'ai_growth',
          title: 'AI Growth Analytics',
          onTap:
              () => Navigator.pushNamed(
                widget.parentContext,
                '/ai_growth_analytics',
              ),
          imagePath: prefs.getString('menu_ai_growth'),
        ),
        MenuCardData(
          id: 'book_of_lorgar',
          title: 'Book of Lorgar',
          onTap:
              () =>
                  Navigator.pushNamed(widget.parentContext, '/book_of_lorgar'),
          imagePath: prefs.getString('menu_book_of_lorgar'),
        ),
        MenuCardData(
          id: 'project_berserk',
          title: 'Warmaster',
          onTap: () async {
            Navigator.pop(widget.parentContext);

            // Show loading indicator
            ScaffoldMessenger.of(widget.parentContext).showSnackBar(
              const SnackBar(
                content: Text('Connecting to Project Warmaster...'),
                duration: Duration(seconds: 2),
              ),
            );

            // Always navigate to Project Warmaster screen - it will handle offline mode
            Navigator.push(
              widget.parentContext,
              MaterialPageRoute(
                builder:
                    (context) => ProjectWarmasterScreen(
                      baseUrl:
                          'http://ec2-34-202-215-209.compute-1.amazonaws.com:8003',
                    ),
              ),
            );
          },
          imagePath: prefs.getString('menu_project_berserk'),
        ),
        MenuCardData(
          id: 'universal_hub',
          title: 'Universal Hub',
          onTap: () async {
            // Show password dialog for Universal Hub access
            final bool? authenticated = await _showPasswordDialog(
              widget.parentContext,
            );
            if (authenticated == true) {
              Navigator.pop(widget.parentContext);
              Navigator.push(
                widget.parentContext,
                MaterialPageRoute(
                  builder: (context) => const UniversalWarmasterHub(),
                ),
              );
            }
          },
          imagePath: prefs.getString('menu_universal_hub'),
        ),
        MenuCardData(
          id: 'terra',
          title: 'Terra',
          onTap: () {
            Navigator.pop(widget.parentContext);
            Navigator.push(
              widget.parentContext,
              MaterialPageRoute(builder: (context) => TerraExtensionScreen()),
            );
          },
          imagePath: prefs.getString('menu_terra'),
        ),
        MenuCardData(
          id: 'the_warp',
          title: 'The Warp',
          onTap: () {
            Navigator.pop(widget.parentContext);
            Navigator.push(
              widget.parentContext,
              MaterialPageRoute(builder: (context) => TheWarpScreen()),
            );
          },
          imagePath: prefs.getString('menu_the_warp'),
        ),
        MenuCardData(
          id: 'training_ground',
          title: 'Training Ground',
          onTap: () {
            Navigator.pop(widget.parentContext);
            Navigator.push(
              widget.parentContext,
              MaterialPageRoute(builder: (context) => TrainingGroundScreen()),
            );
          },
          imagePath: prefs.getString('menu_training_ground'),
        ),
        MenuCardData(
          id: 'scheduling',
          title: 'Dashboard',
          onTap: () {
            Navigator.pop(widget.parentContext);
            Navigator.push(
              widget.parentContext,
              MaterialPageRoute(
                builder: (context) => const SchedulingManagementScreen(),
              ),
            );
          },
          imagePath: prefs.getString('menu_scheduling'),
        ),
      ];
    });
  }

  Future<void> _loadExtensionCards() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final extensions = await fetchApprovedExtensions();

      /// Check if widget is still mounted before calling setState
      if (mounted) {
        setState(() {
          extensionCards =
              extensions
                  .map(
                    (ext) => MenuCardData(
                      id: 'ext_${ext['id']}',
                      title: ext['menu_title'] ?? 'Extension',
                      onTap: () {
                        /// Check if context is still valid before navigation
                        if (mounted) {
                          Navigator.pop(context);
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder:
                                  (context) => DynamicExtensionScreen(
                                    code: ext['dart_code'] ?? '',
                                    title: ext['menu_title'] ?? 'Extension',
                                  ),
                            ),
                          );
                        }
                      },
                      imagePath: prefs.getString('menu_ext_${ext['id']}'),

                      /// Store extension data for delete functionality
                      extensionData: ext,
                    ),
                  )
                  .toList();
          _loadingExtensions = false;
        });
      }
    } catch (e) {
      print('Error loading extension cards: $e');

      /// Only call setState if widget is still mounted
      if (mounted) {
        setState(() {
          _loadingExtensions = false;
        });
      }
    }
  }

  Future<void> _refreshExtensionCards() async {
    await _loadExtensionCards();
  }

  void _showServiceUnavailableDialog(
    String serviceName,
    String message, {
    bool showFallback = false,
    bool showRetry = false,
  }) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('$serviceName Unavailable'),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            if (showRetry)
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  // Retry the Project Warmaster connection
                  _retryProjectWarmasterConnection();
                },
                child: const Text('Retry'),
              ),
            if (showFallback)
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  // Navigate to main screen where user can access other features
                  Navigator.pushNamedAndRemoveUntil(
                    widget.parentContext,
                    '/home',
                    (route) => false,
                  );
                },
                child: const Text('Go to Main App'),
              ),
          ],
        );
      },
    );
  }

  Future<void> _retryProjectWarmasterConnection() async {
    // Show loading indicator
    ScaffoldMessenger.of(widget.parentContext).showSnackBar(
      const SnackBar(
        content: Text('Retrying connection to Project Warmaster...'),
        duration: Duration(seconds: 2),
      ),
    );

    try {
      final response = await http
          .get(
            Uri.parse(
              'http://ec2-34-202-215-209.compute-1.amazonaws.com:8003/api/project-warmaster/status',
            ),
            headers: {'Content-Type': 'application/json'},
          )
          .timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        // Service is available, navigate to Project Warmaster
        Navigator.push(
          widget.parentContext,
          MaterialPageRoute(
            builder:
                (context) => ProjectWarmasterScreen(
                  baseUrl:
                      'http://ec2-34-202-215-209.compute-1.amazonaws.com:8003',
                ),
          ),
        );
      } else {
        // Service still not responding
        ScaffoldMessenger.of(widget.parentContext).showSnackBar(
          SnackBar(
            content: Text(
              'Project Warmaster still unavailable (HTTP ${response.statusCode})',
            ),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      // Connection still failed
      ScaffoldMessenger.of(widget.parentContext).showSnackBar(
        const SnackBar(
          content: Text('Project Warmaster service is still unavailable'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _pickImageForCard(MenuCardData card) async {
    try {
      final picker = ImagePicker();
      final picked = await picker.pickImage(source: ImageSource.gallery);
      if (picked != null) {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('menu_${card.id}', picked.path);

        /// Check if widget is still mounted before calling setState
        if (mounted) {
          setState(() {
            card.imagePath = picked.path;
          });
        }
      }
    } catch (e) {
      print('Error picking image for card: $e');
    }
  }

  Future<bool?> _showPasswordDialog(BuildContext context) async {
    final TextEditingController passwordController = TextEditingController();
    final TextEditingController oldPasswordController = TextEditingController();
    bool isPasswordVisible = false;
    bool isOldPasswordVisible = false;
    bool showOldPasswordField = false;

    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: const Color(0xFF1a1a2e),
              title: const Text(
                '🔐 Universal Hub Access',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Enter rolling security clearance password:',
                    style: TextStyle(color: Colors.white70, fontSize: 16),
                  ),
                  const SizedBox(height: 20),
                  TextField(
                    controller: passwordController,
                    obscureText: !isPasswordVisible,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Enter current password',
                      hintStyle: const TextStyle(color: Colors.white54),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(color: Colors.blue),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(color: Colors.blue),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(
                          color: Colors.cyan,
                          width: 2,
                        ),
                      ),
                      suffixIcon: IconButton(
                        icon: Icon(
                          isPasswordVisible
                              ? Icons.visibility
                              : Icons.visibility_off,
                          color: Colors.white70,
                        ),
                        onPressed: () {
                          setState(() {
                            isPasswordVisible = !isPasswordVisible;
                          });
                        },
                      ),
                    ),
                    onSubmitted: (value) {
                      _validateRollingPassword(
                        context,
                        value,
                        oldPasswordController.text,
                      );
                    },
                  ),
                  if (showOldPasswordField) ...[
                    const SizedBox(height: 12),
                    TextField(
                      controller: oldPasswordController,
                      obscureText: !isOldPasswordVisible,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText: 'Enter old password (if inactive)',
                        hintStyle: const TextStyle(color: Colors.white54),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: const BorderSide(color: Colors.orange),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: const BorderSide(color: Colors.orange),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: const BorderSide(
                            color: Colors.orange,
                            width: 2,
                          ),
                        ),
                        suffixIcon: IconButton(
                          icon: Icon(
                            isOldPasswordVisible
                                ? Icons.visibility
                                : Icons.visibility_off,
                            color: Colors.white70,
                          ),
                          onPressed: () {
                            setState(() {
                              isOldPasswordVisible = !isOldPasswordVisible;
                            });
                          },
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 10),
                  const Text(
                    '⚠️ Rolling password changes every hour. Unauthorized access attempts will be logged',
                    style: TextStyle(color: Colors.orange, fontSize: 12),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(false),
                  child: const Text(
                    'Cancel',
                    style: TextStyle(color: Colors.white70),
                  ),
                ),
                ElevatedButton(
                  onPressed:
                      () => _validateRollingPassword(
                        context,
                        passwordController.text,
                        oldPasswordController.text,
                      ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Access'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _validateRollingPassword(
    BuildContext context,
    String password,
    String oldPassword,
  ) async {
    try {
      final response = await http
          .post(
            Uri.parse(
              'http://localhost:8003/api/offline-chaos/rolling-password/verify',
            ),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'current_password': password,
              'old_password': oldPassword.isNotEmpty ? oldPassword : null,
            }),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        if (data['data']['authenticated'] == true) {
          Navigator.of(context).pop(true);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(data['data']['message']),
              backgroundColor: Colors.green,
            ),
          );

          // Show new password if provided
          if (data['data']['new_password'] != null) {
            _showNewPasswordDialog(context, data['data']['new_password']);
          }
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(data['data']['message']),
              backgroundColor: Colors.red,
            ),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('❌ Access denied. Invalid password.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      // Fallback to offline password validation
      _validatePasswordOffline(context, password, oldPassword);
    }
  }

  void _validatePasswordOffline(
    BuildContext context,
    String password,
    String oldPassword,
  ) {
    // Simulate offline password validation
    final currentTime = DateTime.now();
    final hourTimestamp =
        (currentTime.millisecondsSinceEpoch ~/ 3600000) * 3600000;

    // Generate password based on hour timestamp
    final passwordSeed = "CHAOS_SECRET_${hourTimestamp}";
    final expectedPassword = _generatePasswordFromSeed(passwordSeed);

    if (password == expectedPassword) {
      Navigator.of(context).pop(true);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('🔓 Access granted to Universal Hub (offline mode)'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('❌ Access denied. Invalid password.'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  String _generatePasswordFromSeed(String seed) {
    // Simple hash-based password generation for offline mode
    final hash = seed.codeUnits.fold(0, (a, b) => a + b);
    final password = (hash % 100000000).toString().padLeft(8, '0');
    return '${password.substring(0, 4)}-${password.substring(4, 8)}';
  }

  void _showNewPasswordDialog(BuildContext context, String newPassword) {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: const Color(0xFF1a1a2e),
            title: const Text(
              '🔐 New Password Generated',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Your new rolling password:',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.withOpacity(0.5)),
                  ),
                  child: Text(
                    newPassword,
                    style: const TextStyle(
                      color: Colors.green,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  '⚠️ This password will be valid for the next hour only',
                  style: TextStyle(color: Colors.orange, fontSize: 12),
                ),
              ],
            ),
            actions: [
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Got it'),
              ),
            ],
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final allCards = [...menuCards, ...extensionCards];
    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            /// Dynamic Island settings icon with badge
            Padding(
              padding: const EdgeInsets.only(top: 8.0, bottom: 8.0),
              child: Stack(
                children: [
                  IconButton(
                    icon: Icon(
                      Icons.widgets_rounded,
                      size: 32,
                      color: Colors.deepPurple,
                    ),
                    tooltip: 'Dynamic Island Settings',
                    onPressed: () {
                      Navigator.pop(context);
                      Navigator.pushNamed(
                        widget.parentContext,
                        '/dynamic_island_settings',
                      );
                    },
                  ),

                  /// Note: Dynamic Island count will be handled by the provider when implemented
                ],
              ),
            ),

            /// The rest of the menu as a ListView
            Expanded(
              child: ListView.builder(
                itemCount: allCards.length,
                itemBuilder: (context, index) {
                  final card = allCards[index];
                  return GestureDetector(
                    onTap: () {
                      Navigator.pop(context);
                      card.onTap();
                    },
                    child: Card(
                      margin: EdgeInsets.symmetric(
                        vertical: 10,
                        horizontal: 16,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      elevation: 6,
                      child: Stack(
                        children: [
                          ClipRRect(
                            borderRadius: BorderRadius.circular(20),
                            child:
                                card.imagePath != null
                                    ? Image.file(
                                      File(card.imagePath!),
                                      fit: BoxFit.cover,
                                      height: 120,
                                      width: double.infinity,
                                    )
                                    : Container(
                                      height: 120,
                                      color: Colors.grey[300],
                                    ),
                          ),
                          Container(
                            height: 120,
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(20),
                              color: Colors.black.withOpacity(0.4),
                            ),
                          ),
                          Positioned(
                            left: 24,
                            bottom: 24,
                            child: Text(
                              card.title,
                              style: TextStyle(
                                fontSize: 22,
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                shadows: [
                                  Shadow(blurRadius: 6, color: Colors.black),
                                ],
                              ),
                            ),
                          ),
                          Positioned(
                            right: 16,
                            top: 16,
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                if (card.extensionData != null)
                                  IconButton(
                                    icon: Icon(Icons.delete, color: Colors.red),
                                    onPressed:
                                        () => _showDeleteDialog(
                                          context,
                                          card.extensionData!,
                                        ),
                                    tooltip: 'Delete Extension',
                                  ),
                                IconButton(
                                  icon: Icon(Icons.photo, color: Colors.white),
                                  onPressed: () => _pickImageForCard(card),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
