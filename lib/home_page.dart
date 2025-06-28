import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:the_codex/ai_brain.dart';
import 'package:the_codex/entries/add_entry.dart';
import 'package:the_codex/entries/entry_pin_screen.dart';
import 'package:the_codex/side_menu.dart';
import './widgets/front_view.dart';
import './widgets/back_view.dart';
import 'dart:math';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import './mission.dart';
import 'package:image_picker/image_picker.dart';
import 'package:palette_generator/palette_generator.dart';
import './entry_manager.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'dart:async';
import './ai_brain.dart';
import './widgets/notification_bell.dart';

class Homepage extends StatefulWidget {
  const Homepage({super.key});

  @override
  State<Homepage> createState() => _HomepageState();
}

class _HomepageState extends State<Homepage> with TickerProviderStateMixin {
  bool isFrontview = true;
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  late AnimationController controller;
  String currentDate = '';
  IconData weatherIcon = Icons.wb_sunny;
  int selectedYear = DateTime.now().year;
  Color dominantColor = Colors.white;
  Color contrastingColor = Colors.black;

  // List of banner GIFs
  List<String> bannerGifs = [
    'assets/gif/mad_uchiha.gif',
    'assets/gif/guts.gif',
    'assets/gif/adventure_time.gif',
    'assets/gif/codex.gif',
  ];
  late String selectedBannerGif;

  Future<void> _refreshData() async {
    setState(() {
      _updateDateTime();
    });
  }

  Future<void> _updateDominantColor() async {
    try {
      final PaletteGenerator palette = await PaletteGenerator.fromImageProvider(
        selectedBannerGif.startsWith('assets/')
            ? AssetImage(selectedBannerGif)
            : FileImage(File(selectedBannerGif)) as ImageProvider,
      );
      setState(() {
        dominantColor = palette.dominantColor?.color ?? Colors.white;
        // Calculate contrasting color
        final luminance = dominantColor.computeLuminance();
        contrastingColor = luminance > 0.5 ? Colors.black : Colors.white;
      });
    } catch (e) {
      print('Error getting dominant color: $e');
    }
  }

  void switchView() {
    setState(() {
      if (isFrontview) {
        controller.forward();
      } else {
        controller.reverse();
      }
    });
  }

  @override
  void initState() {
    super.initState();
    print('HomePage: initState called');
    print('HomePage: TheImperium.instance.isRunning = \\${TheImperium.instance.isRunning}');
    controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    selectedBannerGif = bannerGifs[0]; // Initialize with first banner
    _loadBannerGifs();
    _updateDateTime();
    
    // Start notification initialization immediately since there's no video loading
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        print('HomePage: Starting notification initialization');
        _initializeNotifications();
        // Start AI Sandbox after user lands on home page
        final missionProvider = Provider.of<MissionProvider>(context, listen: false);
        print('HomePage: Starting AI Sandbox after landing on home page');
        missionProvider.initializeAISandbox();
      }
    });
  }

  Future<void> _initializeNotifications() async {
    try {
      print('HomePage: Initializing notifications...');
      final missionProvider = Provider.of<MissionProvider>(context, listen: false);
      
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

  Future<void> _loadBannerGifs() async {
    final prefs = await SharedPreferences.getInstance();
    final savedGifs = prefs.getStringList('bannerGifs');
    if (savedGifs != null && savedGifs.isNotEmpty) {
      setState(() {
        bannerGifs = savedGifs;
        selectedBannerGif = bannerGifs[Random().nextInt(bannerGifs.length)];
        _updateDominantColor();
      });
    } else {
      setState(() {
        selectedBannerGif = bannerGifs[Random().nextInt(bannerGifs.length)];
        _updateDominantColor();
      });
    }
  }

  Future<void> _saveBannerGifs() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('bannerGifs', bannerGifs);
  }

  Future<String> _copyGifToAppDirectory(String sourcePath) async {
    final appDir = await getApplicationDocumentsDirectory();
    final fileName = path.basename(sourcePath);
    final targetPath = path.join(appDir.path, 'banner_gifs', fileName);

    // Create directory if it doesn't exist
    await Directory(
      path.join(appDir.path, 'banner_gifs'),
    ).create(recursive: true);

    // Copy the file
    await File(sourcePath).copy(targetPath);
    return targetPath;
  }

  Future<void> _addBannerGif() async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);

    if (picked != null) {
      if (!picked.path.toLowerCase().endsWith('.gif')) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Please select a GIF file.')),
          );
        }
        return;
      }

      try {
        // Copy the GIF to app directory
        final savedPath = await _copyGifToAppDirectory(picked.path);

        setState(() {
          bannerGifs.add(savedPath);
          selectedBannerGif = savedPath;
        });

        await _saveBannerGifs();
        _updateDominantColor();
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to add banner GIF. Please try again.'),
            ),
          );
        }
      }
    }
  }

  Future<void> _removeBannerGif(String gifPath) async {
    if (bannerGifs.length <= 1) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Cannot remove the last banner GIF.')),
        );
      }
      return;
    }

    try {
      // Remove from list
      setState(() {
        bannerGifs.remove(gifPath);
        if (selectedBannerGif == gifPath) {
          selectedBannerGif = bannerGifs[0];
        }
      });

      // Delete file if it's not a default asset
      if (!gifPath.startsWith('assets/')) {
        final file = File(gifPath);
        if (await file.exists()) {
          await file.delete();
        }
      }

      await _saveBannerGifs();
      _updateDominantColor();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to remove banner GIF. Please try again.'),
          ),
        );
      }
    }
  }

  void _updateDateTime() {
    final now = DateTime.now();
    setState(() {
      currentDate = DateFormat('MMM dd/MM/yy').format(now);
      final hour = now.hour;
      if (hour >= 5 && hour < 12) {
        weatherIcon = Icons.wb_sunny_outlined; // Morning
      } else if (hour >= 12 && hour < 17) {
        weatherIcon = Icons.wb_sunny; // Afternoon
      } else if (hour >= 17 && hour < 20) {
        weatherIcon = Icons.wb_twilight; // Evening
      } else {
        weatherIcon = Icons.nightlight_round; // Night
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
      ),
    );
    return Scaffold(
      key: _scaffoldKey,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.menu),
          onPressed: () {
            _scaffoldKey.currentState?.openDrawer();
          },
        ),
      ),
      extendBodyBehindAppBar: true,
      drawer: Consumer<MissionProvider>(
        builder: (context, missionProvider, child) {
          return SideMenu(parentContext: context);
        },
      ),
      body: RefreshIndicator(
        onRefresh: _refreshData,
        color: Theme.of(context).primaryColor,
        child: Column(
          children: [
            Stack(
              children: [
                selectedBannerGif.startsWith('assets/')
                    ? Image.asset(
                      selectedBannerGif,
                      fit: BoxFit.cover,
                      height: 120.0 + MediaQuery.of(context).padding.top,
                      width: double.infinity,
                    )
                    : Image.file(
                      File(selectedBannerGif),
                      fit: BoxFit.cover,
                      height: 120.0 + MediaQuery.of(context).padding.top,
                      width: double.infinity,
                    ),
                Positioned(
                  left: 0,
                  top: MediaQuery.of(context).padding.top,
                  child: Container(
                    margin: const EdgeInsets.all(8.0),
                    decoration: BoxDecoration(
                      color: dominantColor.withOpacity(0.8),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: contrastingColor.withOpacity(0.2),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: IconButton(
                      onPressed: () {
                        _scaffoldKey.currentState?.openDrawer();
                      },
                      icon: Icon(Icons.menu_outlined, color: contrastingColor),
                      iconSize: 30.0,
                      padding: const EdgeInsets.all(8.0),
                    ),
                  ),
                ),
                Positioned(
                  right: 0,
                  top: MediaQuery.of(context).padding.top,
                  child: Container(
                    margin: const EdgeInsets.all(8.0),
                    decoration: BoxDecoration(
                      color: dominantColor.withOpacity(0.8),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: contrastingColor.withOpacity(0.2),
                          blurRadius: 4,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: IconButton(
                      icon: Icon(Icons.more_vert, color: contrastingColor),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder:
                              (context) => SimpleDialog(
                                title: const Text('Options'),
                                children: [
                                  SimpleDialogOption(
                                    child: const Text('Add Banner GIF'),
                                    onPressed: () async {
                                      Navigator.of(context).pop();
                                      await _addBannerGif();
                                    },
                                  ),
                                  SimpleDialogOption(
                                    child: const Text('Manage Banner GIFs'),
                                    onPressed: () async {
                                      Navigator.of(context).pop();
                                      showDialog(
                                        context: context,
                                        builder:
                                            (context) => AlertDialog(
                                              title: const Text(
                                                'Manage Banner GIFs',
                                              ),
                                              content: SizedBox(
                                                width: double.maxFinite,
                                                child: ListView.builder(
                                                  shrinkWrap: true,
                                                  itemCount: bannerGifs.length,
                                                  itemBuilder: (
                                                    context,
                                                    index,
                                                  ) {
                                                    final gifPath =
                                                        bannerGifs[index];
                                                    return ListTile(
                                                      title: Text(
                                                        path.basename(gifPath),
                                                        overflow:
                                                            TextOverflow
                                                                .ellipsis,
                                                      ),
                                                      trailing: IconButton(
                                                        icon: const Icon(
                                                          Icons.delete,
                                                        ),
                                                        onPressed:
                                                            () =>
                                                                _removeBannerGif(
                                                                  gifPath,
                                                                ),
                                                      ),
                                                    );
                                                  },
                                                ),
                                              ),
                                              actions: [
                                                TextButton(
                                                  onPressed:
                                                      () =>
                                                          Navigator.of(
                                                            context,
                                                          ).pop(),
                                                  child: const Text('Close'),
                                                ),
                                              ],
                                            ),
                                      );
                                    },
                                  ),
                                  SimpleDialogOption(
                                    child: const Text('Add Entry Image'),
                                    onPressed: () async {
                                      Navigator.of(context).pop();
                                      final picker = ImagePicker();
                                      final picked = await picker.pickImage(
                                        source: ImageSource.gallery,
                                      );
                                      if (picked != null) {
                                        try {
                                          await EntryManager().addCustomImage(
                                            picked.path,
                                          );
                                          if (mounted) {
                                            ScaffoldMessenger.of(
                                              context,
                                            ).showSnackBar(
                                              const SnackBar(
                                                content: Text(
                                                  'Image added for entries!',
                                                ),
                                              ),
                                            );
                                          }
                                        } catch (e) {
                                          if (mounted) {
                                            ScaffoldMessenger.of(
                                              context,
                                            ).showSnackBar(
                                              SnackBar(
                                                content: Text(
                                                  e.toString().contains(
                                                        'Invalid image format',
                                                      )
                                                      ? 'Invalid image format. Please select a valid image file.'
                                                      : 'Failed to add image. Please try again.',
                                                ),
                                                backgroundColor: Colors.red,
                                              ),
                                            );
                                          }
                                        }
                                      }
                                    },
                                  ),
                                ],
                              ),
                        );
                      },
                    ),
                  ),
                ),
                Positioned(
                  right: 56,
                  top: MediaQuery.of(context).padding.top,
                  child: Consumer<MissionProvider>(
                    builder: (context, provider, _) {
                      print('HomePage: Rebuilding build icon, isSandboxWorking: \\${provider.isSandboxWorking}');
                      return Container(
                        margin: const EdgeInsets.all(8.0),
                        decoration: BoxDecoration(
                          color: Colors.black.withOpacity(0.7),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: (provider.isSandboxWorking ?? false) ? Colors.redAccent.withOpacity(0.5) : Colors.grey.withOpacity(0.2),
                              blurRadius: 8,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.build, color: Colors.blueAccent),
                            const SizedBox(width: 8),
                            StreamBuilder<bool>(
                              stream: TheImperium.instance.runningStream,
                              initialData: TheImperium.instance.isRunning,
                              builder: (context, snapshot) {
                                final running = snapshot.data == true;
                                return AnimatedOpacity(
                                  opacity: running ? 1.0 : 0.3,
                                  duration: const Duration(milliseconds: 300),
                                  child: Container(
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      boxShadow: [
                                        if (running)
                                          BoxShadow(
                                            color: Colors.amberAccent.withOpacity(0.7),
                                            blurRadius: 16,
                                            spreadRadius: 4,
                                          ),
                                      ],
                                    ),
                                    child: Icon(
                                      Icons.fort,
                                      color: Colors.amberAccent,
                                      size: 32,
                                    ),
                                  ),
                                );
                              },
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 30.0),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              decoration: BoxDecoration(
                color: Theme.of(context).cardTheme.color?.withOpacity(0.8),
                borderRadius: BorderRadius.circular(15.0),
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.2),
                    spreadRadius: 1,
                    blurRadius: 3,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: DropdownButton<int>(
                value: selectedYear,
                underline: Container(),
                items: List.generate(21, (index) {
                  final year = DateTime.now().year + index - 10;
                  return DropdownMenuItem<int>(
                    value: year,
                    child: Text(
                      year.toString(),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  );
                }),
                onChanged: (value) {
                  if (value != null) {
                    setState(() {
                      selectedYear = value;
                      final now = DateTime.now();
                      currentDate = DateFormat(
                        'MMM dd/MM/yy',
                      ).format(DateTime(value, now.month, now.day));
                    });
                  }
                },
              ),
            ),
            const SizedBox(height: 10.0),
            Expanded(
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 24.0),
                child: PageView.builder(
                  controller: PageController(
                    initialPage: DateTime.now().month - 1,
                    viewportFraction: 0.8,
                  ),
                  scrollDirection: Axis.horizontal,
                  itemCount: 12,
                  itemBuilder:
                      (_, i) => AnimatedBuilder(
                        animation: controller,
                        builder: (_, child) {
                          if (controller.value >= 0.5) {
                            isFrontview = false;
                          } else {
                            isFrontview = true;
                          }
                          return Transform(
                            transform:
                                Matrix4.identity()
                                  ..setEntry(3, 2, 0.001)
                                  ..rotateY(controller.value * pi),
                            alignment: Alignment.center,
                            child:
                                isFrontview
                                    ? Frontview(monthIndex: i + 1)
                                    : Transform(
                                      transform: Matrix4.rotationY(pi),
                                      alignment: Alignment.center,
                                      child: Backview(
                                        monthIndex: i + 1,
                                        selectedYear: selectedYear,
                                      ),
                                    ),
                          );
                        },
                      ),
                ),
              ),
            ),
            const SizedBox(height: 30.0),
            Padding(
              padding: EdgeInsets.only(
                left: 20.0,
                right: 20.0,
                bottom:
                    MediaQuery.of(context).padding.bottom +
                    12.0, // Add safe area padding plus 12px
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 150.0,
                    height: 50.0,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white.withOpacity(0.1)),
                      borderRadius: BorderRadius.circular(30.0),
                    ),
                    alignment: Alignment.center,
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(width: 10.0),
                        Icon(weatherIcon, color: Colors.black),
                        const SizedBox(width: 10.0),
                        // AI/Robot icon for background activity
                        Consumer<MissionProvider>(
                          builder: (context, provider, _) {
                            return AnimatedOpacity(
                              opacity: provider.isAIActive ? 1.0 : 0.3,
                              duration: const Duration(milliseconds: 300),
                              child: Container(
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    if (provider.isAIActive)
                                      BoxShadow(
                                        color: Colors.green.withOpacity(0.7),
                                        blurRadius: 16,
                                        spreadRadius: 4,
                                      ),
                                  ],
                                ),
                                child: Icon(
                                  Icons.smart_toy,
                                  color: provider.isAIActive ? Colors.green : Colors.grey,
                                  size: 24,
                                ),
                              ),
                            );
                          },
                        ),
                        const SizedBox(width: 10.0),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                'Today',
                                style: Theme.of(context).textTheme.bodyMedium
                                    ?.copyWith(fontWeight: FontWeight.bold),
                              ),
                              Text(
                                currentDate,
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder:
                              (context) => EntryPinScreen(
                                title: 'Add New Entry',
                                onPinEntered: (pin, context) {
                                  Navigator.of(
                                    context,
                                  ).pushReplacementNamed(AddEntry.routeName);
                                },
                              ),
                        ),
                      );
                    },
                    child: Container(
                      width: 50.0,
                      height: 50.0,
                      decoration: BoxDecoration(
                        color: const Color.fromARGB(255, 0, 0, 0),
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Theme.of(
                              context,
                            ).primaryColor.withOpacity(0.4),
                            blurRadius: 5,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: const Icon(Icons.edit_square, color: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 10.0),
                  GestureDetector(
                    onTap: () => switchView(),
                    child: Container(
                      width: 50.0,
                      height: 50.0,
                      decoration: BoxDecoration(
                        color:
                            isFrontview
                                ? const Color.fromARGB(255, 13, 9, 218)
                                : Colors.black,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: Theme.of(
                              context,
                            ).primaryColor.withOpacity(0.3),
                            blurRadius: 5,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.swap_horiz,
                        color:
                            isFrontview
                                ? Colors.white
                                : const Color(0xFF17A1FA),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20.0),
          ],
        ),
      ),
    );
  }
}
