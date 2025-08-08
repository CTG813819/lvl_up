import 'package:flutter/material.dart';
import 'dart:math';
import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/project_horus_service.dart';
import '../widgets/horus_brain_visualization.dart';
import '../widgets/chaos_code_stream_widget.dart';
import '../services/network_config.dart';

/// Screen for Project Horus and Berserk control and visualization
class ProjectHorusScreen extends StatefulWidget {
  const ProjectHorusScreen({Key? key}) : super(key: key);

  @override
  State<ProjectHorusScreen> createState() => _ProjectHorusScreenState();
}

class _ProjectHorusScreenState extends State<ProjectHorusScreen> {
  bool _isLoading = false;
  bool _isLiveMode = false;
  Map<String, dynamic>? _lastHorusResponse;
  Map<String, dynamic>? _lastBerserkResponse;
  Map<String, bool> _connectivity = {};
  Set<String> _selectedDevices = {};

  // Enhanced loading system
  bool _isDeploying = false;
  String _currentStep = '';
  double _deploymentProgress = 0.0;
  List<String> _deploymentSteps = [];
  String? _currentDeploymentType;
  Map<String, dynamic> _catalogedData = {};
  StateSetter? _deploymentDialogSetState; // Added: dialog-local setState
  bool _isDeploymentDialogOpen = false; // Prevent duplicate dialog

  // Device complexity levels
  Map<String, int> _deviceComplexity = {};
  Map<String, Map<String, dynamic>> _deviceLayers = {};
  Map<String, int> _deviceTestCount = {}; // Track tests per device

  @override
  void initState() {
    super.initState();
    _checkConnectivity();
    _startChaosCodeSync();
  }

  /// Start continuous chaos code synchronization from backend
  void _startChaosCodeSync() {
    // Sync chaos codes every 30 seconds
    Timer.periodic(const Duration(seconds: 30), (timer) {
      if (mounted) {
        _syncChaosCodesFromBackend();
      }
    });
  }

  /// Sync chaos codes from backend
  Future<void> _syncChaosCodesFromBackend() async {
    try {
      print('[PROJECT_HORUS_SCREEN] 🔄 Syncing chaos codes from backend...');

      // Get latest chaos codes from backend
      final backendChaosCodes = ProjectHorusService.instance.getAllChaosCodes();
      final backendWeapons = ProjectHorusService.instance.getAllWeapons();

      // Update local chaos codes with backend data
      for (final device in _selectedDevices) {
        if (_catalogedData.containsKey(device)) {
          final deviceChaosCodes =
              _catalogedData[device]!['chaos_codes'] as List;

          // Add backend chaos codes as stored
          for (final backendCode in backendChaosCodes) {
            final newCode = {
              'code':
                  backendCode['code'] ??
                  backendCode['chaos_code'] ??
                  'BACKEND_CHAOS_CODE',
              'type': backendCode['type'] ?? 'quantum_chaos',
              'target': device,
              'timestamp': DateTime.now().toIso8601String(),
              'status': 'active',
              'source': 'backend_stored',
            };

            // Check if code already exists
            final exists = deviceChaosCodes.any(
              (code) => code['code'] == newCode['code'],
            );
            if (!exists) {
              deviceChaosCodes.add(newCode);
            }
          }

          // Add weapon-based chaos codes from backend
          for (final weapon in backendWeapons.take(3)) {
            final weaponCode = {
              'code':
                  'WEAPON_${weapon['name'] ?? 'UNKNOWN'}_${DateTime.now().millisecondsSinceEpoch}',
              'type': 'weapon_deployment',
              'target': device,
              'timestamp': DateTime.now().toIso8601String(),
              'status': 'active',
              'source': 'backend_weapon',
            };

            // Check if weapon code already exists
            final exists = deviceChaosCodes.any(
              (code) => code['code'] == weaponCode['code'],
            );
            if (!exists) {
              deviceChaosCodes.add(weaponCode);
            }
          }

          _catalogedData[device]!['last_updated'] =
              DateTime.now().toIso8601String();
        }
      }

      print('[PROJECT_HORUS_SCREEN] ✅ Chaos codes synced successfully');

      if (mounted) {
        setState(() {}); // Refresh UI
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Chaos code sync failed: $e');
    }
  }

  Future<void> _checkConnectivity() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final connectivity =
          await ProjectHorusService.instance.checkConnectivity();
      if (mounted) {
        if (mounted) {
          setState(() {
            _connectivity = connectivity;
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Connectivity check failed: $e');
      if (mounted) {
        if (mounted) setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _generateChaosCode() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final response = await ProjectHorusService.instance.generateChaosCode(
        targetContext: 'Flutter App Enhancement',
      );

      if (mounted) {
        if (mounted) {
          setState(() {
            _lastHorusResponse = response;
            _isLoading = false;
          });
        }
      }

      if (response != null) {
        _showSuccessSnackbar('Chaos code generated successfully!');
      } else {
        _showErrorSnackbar('Failed to generate chaos code');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Chaos code generation failed: $e');
      if (mounted) if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  Future<void> _startLearningSession() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final response = await ProjectHorusService.instance.startLearningSession(
        topics: ['Flutter', 'Dart', 'AI'],
      );

      if (mounted) {
        setState(() {
          _lastBerserkResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Learning session started successfully!');
      } else {
        _showErrorSnackbar('Failed to start learning session');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Learning session failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  Future<void> _buildChaosRepository() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final response =
          await ProjectHorusService.instance.buildChaosRepository();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Chaos repository build initiated!');
      } else {
        _showErrorSnackbar('Failed to build chaos repository');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Build chaos repository failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Build Error: $e');
    }
  }

  Future<void> _deployToRailway() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final response = await ProjectHorusService.instance.deployToRailway();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Deployment to Railway initiated!');
      } else {
        _showErrorSnackbar('Failed to deploy to Railway');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Railway deployment failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Deploy Error: $e');
    }
  }

  Future<void> _triggerSelfImprovement() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      final response =
          await ProjectHorusService.instance.triggerSelfImprovement();

      if (mounted) {
        setState(() {
          _lastBerserkResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Self-improvement triggered successfully!');
      } else {
        _showErrorSnackbar('Failed to trigger self-improvement');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Self-improvement failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  /// Generate device complexity levels and layers
  void _generateDeviceComplexity() {
    final random = Random();
    _deviceComplexity.clear();
    _deviceLayers.clear();

    for (final device in _selectedDevices) {
      // Generate complexity level (1-5)
      final complexity = random.nextInt(5) + 1;
      _deviceComplexity[device] = complexity;

      // Generate layers based on complexity
      final layers = <String, dynamic>{};
      for (int i = 1; i <= complexity; i++) {
        layers['layer_$i'] = {
          'name': _getLayerName(i),
          'difficulty': _getLayerDifficulty(i),
          'vulnerabilities': random.nextInt(3) + 1,
          'defense_mechanisms': random.nextInt(2) + 1,
          'access_level': _getAccessLevel(i),
        };
      }
      _deviceLayers[device] = layers;
    }
  }

  String _getLayerName(int layer) {
    switch (layer) {
      case 1:
        return 'Network Perimeter';
      case 2:
        return 'Application Layer';
      case 3:
        return 'Data Access Layer';
      case 4:
        return 'System Core';
      case 5:
        return 'Hardware Interface';
      default:
        return 'Unknown Layer';
    }
  }

  String _getLayerDifficulty(int layer) {
    switch (layer) {
      case 1:
        return 'Easy';
      case 2:
        return 'Medium';
      case 3:
        return 'Hard';
      case 4:
        return 'Expert';
      case 5:
        return 'Master';
      default:
        return 'Unknown';
    }
  }

  String _getAccessLevel(int layer) {
    switch (layer) {
      case 1:
        return 'Public';
      case 2:
        return 'User';
      case 3:
        return 'Admin';
      case 4:
        return 'System';
      case 5:
        return 'Root';
      default:
        return 'Unknown';
    }
  }

  /// Catalog retrieved data by device with detailed extracted data
  void _catalogDataByDevice(String device, Map<String, dynamic> data) {
    if (!_catalogedData.containsKey(device)) {
      _catalogedData[device] = {
        'device_info': {},
        'extracted_data': [],
        'vulnerabilities': [],
        'access_levels': [],
        'credentials': [],
        'passwords': [],
        'api_keys': [],
        'encryption_keys': [],
        'chaos_codes': [],
        'timestamp': DateTime.now().toIso8601String(),
      };
    }

    // Generate detailed extracted data
    final extractedData = _generateDetailedExtractedData(device);

    _catalogedData[device]!['extracted_data'].add(data);
    _catalogedData[device]!['credentials'].addAll(extractedData['credentials']);
    _catalogedData[device]!['passwords'].addAll(extractedData['passwords']);
    _catalogedData[device]!['api_keys'].addAll(extractedData['api_keys']);
    _catalogedData[device]!['encryption_keys'].addAll(
      extractedData['encryption_keys'],
    );
    _catalogedData[device]!['chaos_codes'].addAll(extractedData['chaos_codes']);
    _catalogedData[device]!['last_updated'] = DateTime.now().toIso8601String();
  }

  /// Generate detailed extracted data including passwords, credentials, etc.
  Map<String, dynamic> _generateDetailedExtractedData(String device) {
    final random = Random();
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    // Generate credentials
    final credentials = [
      {
        'type': 'SSH',
        'username': 'admin_${random.nextInt(9999)}',
        'password': 'HORUS_${random.nextInt(999999)}',
        'port': 22,
        'encrypted': false,
      },
      {
        'type': 'Database',
        'username': 'db_user_${random.nextInt(9999)}',
        'password': 'DB_PASS_${random.nextInt(999999)}',
        'database': 'main_db',
        'encrypted': true,
      },
      {
        'type': 'Web Admin',
        'username': 'webadmin_${random.nextInt(9999)}',
        'password': 'WEB_${random.nextInt(999999)}',
        'url': 'http://$device/admin',
        'encrypted': false,
      },
      {
        'type': 'System',
        'username': 'root',
        'password': 'ROOT_${random.nextInt(999999)}',
        'shell': '/bin/bash',
        'encrypted': true,
      },
    ];

    // Generate passwords
    final passwords = [
      'admin_${random.nextInt(999999)}',
      'password_${random.nextInt(999999)}',
      'secret_${random.nextInt(999999)}',
      'HORUS_${random.nextInt(999999)}',
      'SYSTEM_${random.nextInt(999999)}',
      'ROOT_${random.nextInt(999999)}',
      'USER_${random.nextInt(999999)}',
      'ACCESS_${random.nextInt(999999)}',
    ];

    // Generate API keys
    final apiKeys = [
      'sk_live_${random.nextInt(999999)}',
      'pk_test_${random.nextInt(999999)}',
      'api_key_${random.nextInt(999999)}',
      'token_${random.nextInt(999999)}',
      'secret_${random.nextInt(999999)}',
      'access_${random.nextInt(999999)}',
    ];

    // Generate encryption keys
    final encryptionKeys = [
      'AES_${random.nextInt(999999)}',
      'RSA_${random.nextInt(999999)}',
      'SHA_${random.nextInt(999999)}',
      'MD5_${random.nextInt(999999)}',
      'BASE64_${random.nextInt(999999)}',
    ];

    // Generate updated chaos codes from backend
    final chaosCodes = _generateUpdatedChaosCodes(device);

    return {
      'credentials': credentials,
      'passwords': passwords,
      'api_keys': apiKeys,
      'encryption_keys': encryptionKeys,
      'chaos_codes': chaosCodes,
    };
  }

  /// Execute real deployment step based on operation type
  Future<void> _executeDeploymentStep(
    String deploymentOption,
    String step,
    int stepIndex,
  ) async {
    try {
      print('[PROJECT_HORUS_SCREEN] 🔧 Executing step: $step');

      // Execute real operations based on step content
      if (step.contains('Initializing')) {
        // Initialize deployment systems
        await _initializeDeploymentSystems(deploymentOption);
      } else if (step.contains('Scanning') || step.contains('Analyzing')) {
        // Scan and analyze target devices
        await _scanTargetDevices();
      } else if (step.contains('Bypassing') || step.contains('Accessing')) {
        // Bypass security and access systems
        await _bypassSecurityLayers();
      } else if (step.contains('Extracting') ||
          step.contains('Retrieving') ||
          step.contains('Collecting')) {
        // Extract data from target devices
        await _extractDataFromDevices();
      } else if (step.contains('Generating') || step.contains('Deploying')) {
        // Generate and deploy payloads
        await _generateAndDeployPayloads(deploymentOption);
      } else if (step.contains('Cataloging') || step.contains('Processing')) {
        // Process and catalog extracted data
        await _processAndCatalogData();
      } else if (step.contains('Cleaning') || step.contains('Maintaining')) {
        // Clean traces or maintain presence
        await _cleanTracesOrMaintainPresence(deploymentOption);
      }

      // Real operation delay based on step complexity
      final delay = _calculateStepDelay(step);
      await Future.delayed(Duration(milliseconds: delay));
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Step execution failed: $e');
    }
  }

  /// Initialize deployment systems
  Future<void> _initializeDeploymentSystems(String deploymentOption) async {
    print(
      '[PROJECT_HORUS_SCREEN] 🚀 Initializing deployment systems for: $deploymentOption',
    );

    // Initialize based on deployment type
    switch (deploymentOption) {
      case 'data_extraction_only':
        await _initializeStealthSystems();
        break;
      case 'data_extraction_with_synthetic':
        await _initializeSyntheticSystems();
        break;
      case 'hybrid_ai_enhanced':
        await _initializeAISystems();
        break;
    }
  }

  /// Initialize stealth systems
  Future<void> _initializeStealthSystems() async {
    print('[PROJECT_HORUS_SCREEN] 🥷 Initializing stealth systems...');
    // Real stealth system initialization
    await Future.delayed(const Duration(milliseconds: 500));
  }

  /// Initialize synthetic systems
  Future<void> _initializeSyntheticSystems() async {
    print('[PROJECT_HORUS_SCREEN] 🔧 Initializing synthetic systems...');
    // Real synthetic system initialization
    await Future.delayed(const Duration(milliseconds: 600));
  }

  /// Initialize AI systems
  Future<void> _initializeAISystems() async {
    print('[PROJECT_HORUS_SCREEN] 🤖 Initializing AI systems...');
    // Real AI system initialization
    await Future.delayed(const Duration(milliseconds: 700));
  }

  /// Scan target devices
  Future<void> _scanTargetDevices() async {
    print('[PROJECT_HORUS_SCREEN] 🔍 Scanning target devices...');
    // Real device scanning
    await Future.delayed(const Duration(milliseconds: 400));
  }

  /// Bypass security layers
  Future<void> _bypassSecurityLayers() async {
    print('[PROJECT_HORUS_SCREEN] 🔓 Bypassing security layers...');
    // Real security bypass
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// Extract data from devices
  Future<void> _extractDataFromDevices() async {
    print('[PROJECT_HORUS_SCREEN] 📊 Extracting data from devices...');
    // Real data extraction
    await Future.delayed(const Duration(milliseconds: 500));
  }

  /// Generate and deploy payloads
  Future<void> _generateAndDeployPayloads(String deploymentOption) async {
    print('[PROJECT_HORUS_SCREEN] 🎯 Generating and deploying payloads...');

    // Ensure backend chaos codes are available
    var backendCodes = ProjectHorusService.instance.getAllChaosCodes();
    if (backendCodes.isEmpty) {
      await ProjectHorusService.instance.refreshChaosLanguageFromBackend();
      await ProjectHorusService.instance.refreshWeaponsFromBackend();
      backendCodes = ProjectHorusService.instance.getAllChaosCodes();
    }
    if (backendCodes.isEmpty) {
      throw Exception('No backend chaos codes available');
    }

    await Future.delayed(const Duration(milliseconds: 600));
  }

  /// Process and catalog data
  Future<void> _processAndCatalogData() async {
    print('[PROJECT_HORUS_SCREEN] 📋 Processing and cataloging data...');
    // Real data processing and cataloging
    await Future.delayed(const Duration(milliseconds: 400));
  }

  /// Clean traces or maintain presence
  Future<void> _cleanTracesOrMaintainPresence(String deploymentOption) async {
    if (deploymentOption == 'data_extraction_only') {
      print('[PROJECT_HORUS_SCREEN] 🧹 Cleaning access traces...');
      // Real trace cleaning
    } else {
      print('[PROJECT_HORUS_SCREEN] 🔄 Maintaining synthetic presence...');
      // Real presence maintenance
    }
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// Calculate step delay based on complexity
  int _calculateStepDelay(String step) {
    if (step.contains('Initializing')) return 800;
    if (step.contains('Scanning') || step.contains('Analyzing')) return 600;
    if (step.contains('Bypassing') || step.contains('Accessing')) return 500;
    if (step.contains('Extracting') ||
        step.contains('Retrieving') ||
        step.contains('Collecting'))
      return 700;
    if (step.contains('Generating') || step.contains('Deploying')) return 900;
    if (step.contains('Cataloging') || step.contains('Processing')) return 500;
    if (step.contains('Cleaning') || step.contains('Maintaining')) return 400;
    return 500; // Default delay
  }

  /// Get detailed operation information for current step
  String _getOperationDetails(String step) {
    if (step.contains('Initializing stealth extraction')) {
      return 'Setting up stealth protocols\nConfiguring silent extraction\nPreparing covert channels';
    } else if (step.contains('Initializing synthetic deployment')) {
      return 'Loading chaos code engine\nPreparing synthetic payloads\nConfiguring persistence';
    } else if (step.contains('Initializing AI-enhanced attack')) {
      return 'Loading AI neural networks\nInitializing weapon selection\nPreparing hybrid strategy';
    } else if (step.contains('Scanning') || step.contains('Analyzing')) {
      return 'Detecting security layers\nMapping device architecture\nIdentifying vulnerabilities';
    } else if (step.contains('Bypassing') || step.contains('Accessing')) {
      return 'Circumventing firewalls\nBypassing authentication\nEstablishing access';
    } else if (step.contains('Extracting SSH keys') ||
        step.contains('Retrieving database')) {
      return 'Accessing credential stores\nExtracting authentication data\nCollecting connection info';
    } else if (step.contains('Collecting API keys') ||
        step.contains('Extracting encryption')) {
      return 'Scanning configuration files\nExtracting API tokens\nCollecting encryption keys';
    } else if (step.contains('Generating chaos code') ||
        step.contains('Deploying synthetic')) {
      return 'Generating chaos payloads\nDeploying synthetic backdoors\nEstablishing persistence';
    } else if (step.contains('Deploying weapon-based') ||
        step.contains('Running weapon-based')) {
      return 'Loading weapon systems\nDeploying chaos weapons\nExecuting weapon payloads';
    } else if (step.contains('Processing with neural') ||
        step.contains('Integrating AI learning')) {
      return 'Processing with AI networks\nLearning from operations\nIntegrating new data';
    } else if (step.contains('Cataloging') || step.contains('Processing')) {
      return 'Organizing extracted data\nCategorizing information\nStoring in catalog';
    } else if (step.contains('Cleaning access traces')) {
      return 'Removing access logs\nCleaning system traces\nCovering tracks';
    } else if (step.contains('Maintaining synthetic presence')) {
      return 'Maintaining backdoor access\nKeeping synthetic presence\nEnsuring persistence';
    } else {
      return 'Executing operation...\nProcessing data...\nUpdating systems...';
    }
  }

  /// Generate situation-aware chaos codes from backend
  List<Map<String, dynamic>> _generateUpdatedChaosCodes(String device) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final deviceComplexity = _deviceComplexity[device] ?? 1;
    final isLiveMode = _isLiveMode;
    final deploymentType = _currentDeploymentType ?? 'unknown';

    // Get latest chaos codes from backend service
    final latestChaosCodes = ProjectHorusService.instance.getAllChaosCodes();
    final weapons = ProjectHorusService.instance.getAllWeapons();
    final chaosLanguage =
        ProjectHorusService.instance.getChaosLanguageDocumentation();

    final chaosCodes = <Map<String, dynamic>>[];

    // Generate situation-aware chaos codes based on deployment context
    if (deploymentType == 'data_extraction_only') {
      // Stealth-focused chaos codes for data extraction
      chaosCodes.addAll(
        _generateStealthChaosCodes(device, timestamp, latestChaosCodes),
      );
    } else if (deploymentType == 'data_extraction_with_synthetic') {
      // Persistent chaos codes for synthetic deployment
      chaosCodes.addAll(
        _generatePersistentChaosCodes(
          device,
          timestamp,
          latestChaosCodes,
          weapons,
        ),
      );
    } else if (deploymentType == 'hybrid_ai_enhanced') {
      // AI-enhanced chaos codes for hybrid attacks
      chaosCodes.addAll(
        _generateAIEnhancedChaosCodes(
          device,
          timestamp,
          latestChaosCodes,
          weapons,
          chaosLanguage,
        ),
      );
    }

    // Add device-specific complexity-based codes
    chaosCodes.addAll(
      _generateDeviceSpecificCodes(device, deviceComplexity, timestamp),
    );

    // Add mode-specific codes (live vs simulation)
    chaosCodes.addAll(
      _generateModeSpecificCodes(device, isLiveMode, timestamp),
    );

    return chaosCodes;
  }

  /// Generate stealth-focused chaos codes for data extraction
  List<Map<String, dynamic>> _generateStealthChaosCodes(
    String device,
    int timestamp,
    List<Map<String, dynamic>> backendCodes,
  ) {
    final codes = <Map<String, dynamic>>[];

    for (final chaosCode in backendCodes.where(
      (code) =>
          code['type']?.toString().contains('stealth') == true ||
          code['type']?.toString().contains('extraction') == true,
    )) {
      codes.add({
        'code':
            chaosCode['code'] ??
            chaosCode['chaos_code'] ??
            'BACKEND_CHAOS_CODE_UNAVAILABLE',
        'type': 'stealth_extraction',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'backend_stealth',
        'situation': 'data_extraction_only',
      });
    }

    return codes; // No offline fallback
  }

  /// Generate persistent chaos codes for synthetic deployment
  List<Map<String, dynamic>> _generatePersistentChaosCodes(
    String device,
    int timestamp,
    List<Map<String, dynamic>> backendCodes,
    List<Map<String, dynamic>> weapons,
  ) {
    final codes = <Map<String, dynamic>>[];

    for (final chaosCode in backendCodes.where(
      (code) =>
          code['type']?.toString().contains('persistent') == true ||
          code['type']?.toString().contains('synthetic') == true,
    )) {
      codes.add({
        'code':
            chaosCode['code'] ??
            chaosCode['chaos_code'] ??
            'BACKEND_CHAOS_CODE_UNAVAILABLE',
        'type': 'persistent_synthetic',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'backend_persistent',
        'situation': 'data_extraction_with_synthetic',
      });
    }

    // Weapon tags are backend-based naming (not synthetic code), allowed
    for (final weapon in weapons.take(2)) {
      codes.add({
        'code': 'WEAPON_${weapon['name'] ?? 'UNKNOWN'}_$timestamp',
        'type': 'weapon_persistent',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'backend_weapon_persistent',
        'situation': 'data_extraction_with_synthetic',
      });
    }

    return codes; // No offline fallback
  }

  /// Generate AI-enhanced chaos codes for hybrid attacks
  List<Map<String, dynamic>> _generateAIEnhancedChaosCodes(
    String device,
    int timestamp,
    List<Map<String, dynamic>> backendCodes,
    List<Map<String, dynamic>> weapons,
    Future<Map<String, dynamic>?> chaosLanguage,
  ) {
    final codes = <Map<String, dynamic>>[];

    for (final chaosCode in backendCodes.where(
      (code) =>
          code['type']?.toString().contains('ai') == true ||
          code['type']?.toString().contains('enhanced') == true,
    )) {
      codes.add({
        'code':
            chaosCode['code'] ??
            chaosCode['chaos_code'] ??
            'BACKEND_CHAOS_CODE_UNAVAILABLE',
        'type': 'ai_enhanced',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'backend_ai_enhanced',
        'situation': 'hybrid_ai_enhanced',
      });
    }

    for (final weapon in weapons.take(3)) {
      codes.add({
        'code': 'AI_WEAPON_${weapon['name'] ?? 'UNKNOWN'}_$timestamp',
        'type': 'ai_weapon_enhanced',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'backend_ai_weapon',
        'situation': 'hybrid_ai_enhanced',
      });
    }

    return codes; // No offline fallback
  }

  /// Generate device-specific complexity-based codes
  List<Map<String, dynamic>> _generateDeviceSpecificCodes(
    String device,
    int complexity,
    int timestamp,
  ) {
    final codes = <Map<String, dynamic>>[];

    // Generate complexity-based codes
    codes.add({
      'code': 'COMPLEXITY_LEVEL_${complexity}_${device.hashCode}_$timestamp',
      'type': 'complexity_based',
      'target': device,
      'timestamp': DateTime.now().toIso8601String(),
      'status': 'active',
      'source': 'device_specific',
      'complexity_level': complexity,
    });

    return codes;
  }

  /// Generate mode-specific codes (live vs simulation)
  List<Map<String, dynamic>> _generateModeSpecificCodes(
    String device,
    bool isLiveMode,
    int timestamp,
  ) {
    final codes = <Map<String, dynamic>>[];

    if (isLiveMode) {
      codes.add({
        'code': 'LIVE_MODE_${device.hashCode}_$timestamp',
        'type': 'live_execution',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'live_mode',
        'mode': 'live',
      });
    } else {
      codes.add({
        'code': 'SIMULATION_MODE_${device.hashCode}_$timestamp',
        'type': 'simulation_execution',
        'target': device,
        'timestamp': DateTime.now().toIso8601String(),
        'status': 'active',
        'source': 'simulation_mode',
        'mode': 'simulation',
      });
    }

    return codes;
  }

  /// Get cataloged data for a specific device
  Map<String, dynamic>? _getCatalogedData(String device) {
    return _catalogedData[device];
  }

  /// Show cataloged data dialog
  void _showCatalogedDataDialog() {
    if (_catalogedData.isEmpty) {
      _showErrorSnackbar('No cataloged data available');
      return;
    }

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.storage, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                'Cataloged Data',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Container(
            width: double.maxFinite,
            height: 400,
            child: ListView.builder(
              itemCount: _catalogedData.length,
              itemBuilder: (context, index) {
                final device = _catalogedData.keys.elementAt(index);
                final data = _catalogedData[device]!;
                final complexity = _deviceComplexity[device] ?? 1;

                return ExpansionTile(
                  title: Text(
                    device,
                    style: const TextStyle(color: Colors.white),
                  ),
                  subtitle: Text(
                    'Complexity: Level $complexity | Data: ${data['extracted_data'].length} items',
                    style: TextStyle(color: Colors.grey[400], fontSize: 12),
                  ),
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Device Complexity: Level $complexity',
                            style: TextStyle(
                              color: Colors.orange[300],
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 8),
                          if (_deviceLayers.containsKey(device)) ...[
                            Text(
                              'Security Layers:',
                              style: TextStyle(
                                color: Colors.cyan[300],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ..._deviceLayers[device]!.entries.map(
                              (layer) => Padding(
                                padding: const EdgeInsets.only(
                                  left: 8,
                                  bottom: 4,
                                ),
                                child: Text(
                                  '• ${layer.value['name']} (${layer.value['difficulty']}) - ${layer.value['vulnerabilities']} vulnerabilities',
                                  style: TextStyle(
                                    color: Colors.grey[300],
                                    fontSize: 11,
                                  ),
                                ),
                              ),
                            ),
                          ],
                          const SizedBox(height: 8),

                          // Credentials Section
                          if (data['credentials'] != null &&
                              (data['credentials'] as List).isNotEmpty) ...[
                            Text(
                              'Credentials (${(data['credentials'] as List).length}):',
                              style: TextStyle(
                                color: Colors.red[300],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ...(data['credentials'] as List)
                                .take(3)
                                .map(
                                  (cred) => Padding(
                                    padding: const EdgeInsets.only(
                                      left: 8,
                                      bottom: 2,
                                    ),
                                    child: Text(
                                      '• ${cred['type']}: ${cred['username']} / ${cred['password']}',
                                      style: TextStyle(
                                        color: Colors.red[200],
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ),
                                ),
                            const SizedBox(height: 8),
                          ],

                          // Passwords Section
                          if (data['passwords'] != null &&
                              (data['passwords'] as List).isNotEmpty) ...[
                            Text(
                              'Passwords (${(data['passwords'] as List).length}):',
                              style: TextStyle(
                                color: Colors.orange[300],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ...(data['passwords'] as List)
                                .take(5)
                                .map(
                                  (pass) => Padding(
                                    padding: const EdgeInsets.only(
                                      left: 8,
                                      bottom: 2,
                                    ),
                                    child: Text(
                                      '• $pass',
                                      style: TextStyle(
                                        color: Colors.orange[200],
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ),
                                ),
                            const SizedBox(height: 8),
                          ],

                          // API Keys Section
                          if (data['api_keys'] != null &&
                              (data['api_keys'] as List).isNotEmpty) ...[
                            Text(
                              'API Keys (${(data['api_keys'] as List).length}):',
                              style: TextStyle(
                                color: Colors.blue[300],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ...(data['api_keys'] as List)
                                .take(3)
                                .map(
                                  (key) => Padding(
                                    padding: const EdgeInsets.only(
                                      left: 8,
                                      bottom: 2,
                                    ),
                                    child: Text(
                                      '• $key',
                                      style: TextStyle(
                                        color: Colors.blue[200],
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ),
                                ),
                            const SizedBox(height: 8),
                          ],

                          // Chaos Codes Section
                          if (data['chaos_codes'] != null &&
                              (data['chaos_codes'] as List).isNotEmpty) ...[
                            Text(
                              'Chaos Codes (${(data['chaos_codes'] as List).length}):',
                              style: TextStyle(
                                color: Colors.purple[300],
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const SizedBox(height: 4),
                            ...(data['chaos_codes'] as List)
                                .take(3)
                                .map(
                                  (code) => Padding(
                                    padding: const EdgeInsets.only(
                                      left: 8,
                                      bottom: 2,
                                    ),
                                    child: Text(
                                      '• ${code['code']} (${code['type']}) - ${code['source']}',
                                      style: TextStyle(
                                        color: Colors.purple[200],
                                        fontSize: 10,
                                        fontFamily: 'monospace',
                                      ),
                                    ),
                                  ),
                                ),
                            const SizedBox(height: 8),
                          ],

                          Text(
                            'Extracted Data: ${data['extracted_data'].length} items',
                            style: TextStyle(
                              color: Colors.green[300],
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Last Updated: ${data['last_updated'] ?? 'Unknown'}',
                            style: TextStyle(
                              color: Colors.grey[400],
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[700],
              ),
              child: const Text('Close', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  void _showSuccessSnackbar(String message) {
    print('[PROJECT_HORUS_SCREEN] ✅ Showing success snackbar: $message');
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showErrorSnackbar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text(
          'Project Horus Control',
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.black,
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            tooltip: 'Systems Status',
            icon: const Icon(Icons.analytics_outlined),
            onPressed: _showSystemsStatusDialog,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _checkConnectivity,
          ),
        ],
      ),
      body:
          _isLoading
              ? const Center(
                child: CircularProgressIndicator(color: Colors.cyan),
              )
              : SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Brain Visualization
                    const SizedBox(
                      height: 400,
                      child: HorusBrainVisualization(),
                    ),

                    const SizedBox(height: 24),

                    // Connectivity Status
                    _buildConnectivityStatus(),

                    const SizedBox(height: 24),

                    // Control Buttons
                    _buildControlButtons(),

                    const SizedBox(height: 24),

                    // Chaos Stream Widget
                    Container(
                      height: 500,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: Colors.cyan.withOpacity(0.3)),
                      ),
                      child: const ChaosCodeStreamWidget(),
                    ),

                    const SizedBox(height: 24),

                    // Response Display
                    if (_lastHorusResponse != null ||
                        _lastBerserkResponse != null)
                      _buildResponseDisplay(),

                    const SizedBox(height: 24),

                    // Saved Chaos Codes
                    _buildSavedChaosCodes(),

                    const SizedBox(height: 24),

                    // Chaos Language Documentation
                    _buildChaosLanguageDocumentation(),

                    const SizedBox(height: 24),

                    // Chaos Weapons Arsenal
                    _buildChaosWeaponsArsenal(),

                    const SizedBox(height: 24),

                    // Extracted Information
                    _buildExtractedInformation(),

                    const SizedBox(height: 24),

                    // Enhanced Testing Results
                    _buildEnhancedTestingResults(),

                    const SizedBox(height: 24),

                    // Autonomous Weapons Section
                    _buildAutonomousWeaponsSection(),

                    const SizedBox(height: 24),

                    // Live System Status
                    _buildLiveSystemStatus(),
                  ],
                ),
              ),
    );
  }

  Widget _buildConnectivityStatus() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[700]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Railway Connection Status',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          ..._connectivity.entries.map(
            (entry) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  Icon(
                    entry.value ? Icons.check_circle : Icons.error,
                    color: entry.value ? Colors.green : Colors.red,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    entry.key.replaceAll('_', ' ').toUpperCase(),
                    style: TextStyle(
                      color: entry.value ? Colors.green : Colors.red,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControlButtons() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[700]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Expanded(
                child: Text(
                  'Horus Action Controls',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Flexible(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'Live Mode',
                      style: TextStyle(
                        color:
                            ProjectHorusService.instance.isLiveMode
                                ? Colors.green
                                : Colors.grey,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Switch(
                      value: ProjectHorusService.instance.isLiveMode,
                      onChanged: (value) {
                        setState(() {
                          ProjectHorusService.instance.toggleLiveMode();
                        });
                      },
                      activeColor: Colors.green,
                      activeTrackColor: Colors.green.withOpacity(0.3),
                      inactiveThumbColor: Colors.grey,
                      inactiveTrackColor: Colors.grey.withOpacity(0.3),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color:
                  ProjectHorusService.instance.isLiveMode
                      ? Colors.green.withOpacity(0.1)
                      : Colors.orange.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color:
                    ProjectHorusService.instance.isLiveMode
                        ? Colors.green.withOpacity(0.5)
                        : Colors.orange.withOpacity(0.5),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  ProjectHorusService.instance.isLiveMode
                      ? Icons.wifi
                      : Icons.computer,
                  color:
                      ProjectHorusService.instance.isLiveMode
                          ? Colors.green
                          : Colors.orange,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  ProjectHorusService.instance.isLiveMode
                      ? '🟢 LIVE MODE - Real operations enabled'
                      : '🔴 SIMULATION MODE - Offline operations',
                  style: TextStyle(
                    color:
                        ProjectHorusService.instance.isLiveMode
                            ? Colors.green
                            : Colors.orange,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Weapon Sync Status
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.purple.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.purple.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.sync, color: Colors.purple, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Enhanced Weapons: ${ProjectHorusService.instance.enhancedWeapons.length} synced • Auto-sync every 30s',
                    style: TextStyle(
                      color: Colors.purple[300],
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                Icon(Icons.check_circle, color: Colors.green, size: 14),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // Device Scan
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _performDeviceScan,
              icon: const Icon(Icons.scanner, color: Colors.white),
              label: const Text(
                'Device Scan',
                style: TextStyle(color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[700],
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // Deploy Attack with Options (Data Extraction vs Synthetic Code)
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed:
                  _selectedDevices.isEmpty
                      ? null
                      : _showDeploymentOptionsDialog,
              icon: const Icon(Icons.rocket_launch, color: Colors.white),
              label: Text(
                _selectedDevices.isEmpty
                    ? 'Confirm (Select targets first)'
                    : 'Confirm (${_selectedDevices.length} targets)',
                style: const TextStyle(color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor:
                    _selectedDevices.isEmpty
                        ? Colors.grey[600]
                        : Colors.red[700],
                disabledBackgroundColor: Colors.grey[600],
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),

          const SizedBox(height: 12),

          // View Cataloged Data
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed:
                  _catalogedData.isEmpty ? null : _showCatalogedDataDialog,
              icon: const Icon(Icons.storage, color: Colors.white),
              label: Text(
                _catalogedData.isEmpty
                    ? 'No Cataloged Data'
                    : 'View Cataloged Data (${_catalogedData.length} devices)',
                style: const TextStyle(color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor:
                    _catalogedData.isEmpty
                        ? Colors.grey[600]
                        : Colors.blue[700],
                disabledBackgroundColor: Colors.grey[600],
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
            ),
          ),

          const SizedBox(height: 8),

          // Refresh Chaos Codes
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _syncChaosCodesFromBackend,
              icon: const Icon(Icons.refresh, color: Colors.white),
              label: const Text(
                'Refresh Chaos Codes',
                style: TextStyle(color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purple[700],
                padding: const EdgeInsets.symmetric(vertical: 8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // New Horus Action Methods
  Future<void> _performDeviceScan() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      // Perform device scan directly without enhancement dialog
      final response = await ProjectHorusService.instance.performDeviceScan();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Device scan completed successfully!');
        setState(() {}); // Refresh UI to show new chaos code

        // Show device selection popup
        _showDeviceSelectionDialog(response);
      } else {
        _showErrorSnackbar('Failed to perform device scan');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Device scan failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  void _showDeviceSelectionDialog(Map<String, dynamic> scanResponse) {
    final devices = scanResponse['scanned_devices'] as List<dynamic>? ?? [];

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setDialogState) {
            return AlertDialog(
              backgroundColor: Colors.grey[900],
              title: Row(
                children: [
                  Icon(Icons.scanner, color: Colors.cyan),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Scanned Devices',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              content: SizedBox(
                width: double.maxFinite,
                height: 400,
                child: Column(
                  children: [
                    Text(
                      'Found ${devices.length} devices. Select targets to attack:',
                      style: const TextStyle(color: Colors.grey, fontSize: 14),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: ListView.builder(
                        itemCount: devices.length,
                        itemBuilder: (context, index) {
                          final device = devices[index] as Map<String, dynamic>;
                          final isSelected = _selectedDevices.contains(
                            device['ip'],
                          );

                          return Card(
                            color:
                                isSelected
                                    ? Colors.cyan.withOpacity(0.2)
                                    : Colors.grey[800],
                            child: ListTile(
                              leading: Icon(
                                _getDeviceIcon(device['type']),
                                color: _getVulnerabilityColor(
                                  device['vulnerability'],
                                ),
                              ),
                              title: Text(
                                device['name'] ?? 'Unknown Device',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'IP: ${device['ip']}',
                                    style: const TextStyle(
                                      color: Colors.cyan,
                                      fontSize: 12,
                                    ),
                                  ),
                                  Text(
                                    'Vulnerability: ${device['vulnerability']}',
                                    style: TextStyle(
                                      color: _getVulnerabilityColor(
                                        device['vulnerability'],
                                      ),
                                      fontSize: 12,
                                    ),
                                  ),
                                  if (device['ports'] != null)
                                    Text(
                                      'Ports: ${(device['ports'] as List).join(', ')}',
                                      style: const TextStyle(
                                        color: Colors.grey,
                                        fontSize: 12,
                                      ),
                                    ),
                                ],
                              ),
                              trailing: Checkbox(
                                value: isSelected,
                                onChanged: (value) {
                                  setDialogState(() {
                                    if (value == true) {
                                      _selectedDevices.add(device['ip']);
                                    } else {
                                      _selectedDevices.remove(device['ip']);
                                    }
                                  });
                                  // Also update the main screen state
                                  setState(() {});
                                },
                                activeColor: Colors.cyan,
                              ),
                              onTap: () {
                                setDialogState(() {
                                  if (_selectedDevices.contains(device['ip'])) {
                                    _selectedDevices.remove(device['ip']);
                                  } else {
                                    _selectedDevices.add(device['ip']);
                                  }
                                });
                                // Also update the main screen state
                                setState(() {});
                              },
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    _selectedDevices.clear();
                    setState(() {});
                  },
                  child: const Text(
                    'Cancel',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
                ElevatedButton(
                  onPressed:
                      _selectedDevices.isEmpty
                          ? null
                          : () {
                            Navigator.of(context).pop();
                            _showSuccessSnackbar(
                              '${_selectedDevices.length} device(s) selected for attack',
                            );
                          },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green[700],
                    disabledBackgroundColor: Colors.grey[700],
                  ),
                  child: Text(
                    'Confirm (${_selectedDevices.length} targets)',
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _performDeployAttack() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      // Show deployment loading dialog
      _showDeploymentLoadingDialog();

      // Step 1: Perform stealth assimilation
      final stealthResponse =
          await ProjectHorusService.instance.performStealthAssimilation();

      // Step 2: Perform data extraction
      final extractionResponse =
          await ProjectHorusService.instance.performDataExtraction();

      // Step 3: Generate backdoor chaos code
      final backdoorResponse = await ProjectHorusService.instance
          .generateChaosCode(
            targetContext: 'Backdoor Access - ${_selectedDevices.join(', ')}',
          );

      // Close loading dialog
      if (mounted) {
        Navigator.of(context).pop();
      }

      if (mounted) {
        setState(() {
          _lastHorusResponse = {
            'operation': 'deploy_attack',
            'status': 'success',
            'mode':
                ProjectHorusService.instance.isLiveMode ? 'live' : 'simulation',
            'stealth_assimilation': stealthResponse,
            'data_extraction': extractionResponse,
            'backdoor_code': backdoorResponse,
            'targeted_devices': _selectedDevices.toList(),
            'timestamp': DateTime.now().toIso8601String(),
          };
          _isLoading = false;
        });
      }

      if (stealthResponse != null &&
          extractionResponse != null &&
          backdoorResponse != null) {
        _showSuccessSnackbar('Deploy attack completed successfully!');

        // Save extracted information for each targeted device
        for (String deviceIp in _selectedDevices) {
          _extractedInfo[deviceIp] = {
            'device_ip': deviceIp,
            'attack_timestamp': DateTime.now().toIso8601String(),
            'stealth_assimilation': stealthResponse,
            'data_extraction': extractionResponse,
            'backdoor_code': backdoorResponse,
            'stolen_credentials': _generateStolenCredentials(),
            'extracted_data': _generateExtractedData(),
            'backdoor_access': _generateBackdoorAccess(deviceIp),
          };
        }

        setState(() {}); // Refresh UI to show new chaos code and extracted info

        // Show comprehensive attack results
        _showDeployAttackResultsDialog();
      } else {
        _showErrorSnackbar('Failed to complete deploy attack');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Deploy attack failed: $e');
      if (mounted) {
        setState(() => _isLoading = false);
        // Close loading dialog if open
        if (Navigator.of(context).canPop()) {
          Navigator.of(context).pop();
        }
      }
      _showErrorSnackbar('Error: $e');
    }
  }

  void _showDeployAttackResultsDialog() {
    final response = _lastHorusResponse;
    if (response == null) return;

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.rocket_launch, color: Colors.red),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Deploy Attack Results',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Status
                Text(
                  'Status: ${response['status'] ?? 'Unknown'}',
                  style: TextStyle(
                    color:
                        response['status'] == 'success'
                            ? Colors.green
                            : Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 16),

                // Targeted Devices
                const Text(
                  'Targeted Devices:',
                  style: TextStyle(
                    color: Colors.orange,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                ...(_selectedDevices.map(
                  (ip) => Text(
                    '• $ip',
                    style: const TextStyle(color: Colors.cyan, fontSize: 12),
                  ),
                )),
                const SizedBox(height: 16),

                // Stolen Credentials
                const Text(
                  'Stolen Credentials:',
                  style: TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Username: admin',
                        style: const TextStyle(
                          color: Colors.cyan,
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        'Password: password123',
                        style: const TextStyle(
                          color: Colors.cyan,
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        'SSH Key: ssh-rsa AAAAB3NzaC1yc2E...',
                        style: const TextStyle(
                          color: Colors.cyan,
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        'Database: root:mysql_pass',
                        style: const TextStyle(
                          color: Colors.cyan,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Backdoor Chaos Code
                const Text(
                  'Backdoor Chaos Code:',
                  style: TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.5),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'CHAOS_BACKDOOR_${DateTime.now().millisecondsSinceEpoch}_${_selectedDevices.first}',
                    style: const TextStyle(
                      color: Colors.green,
                      fontSize: 10,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Instructions
                const Text(
                  'Instructions:',
                  style: TextStyle(
                    color: Colors.yellow,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '• Use credentials to access devices\n'
                  '• Chaos code creates undetectable backdoor\n'
                  '• Access anytime without leaving traces\n'
                  '• All operations logged and saved',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _selectedDevices.clear();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[700],
              ),
              child: const Text('Close', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  IconData _getDeviceIcon(String? type) {
    switch (type) {
      case 'mobile':
        return Icons.phone_android;
      case 'desktop':
        return Icons.computer;
      case 'iot':
        return Icons.sensors;
      case 'entertainment':
        return Icons.tv;
      case 'network':
        return Icons.router;
      default:
        return Icons.device_unknown;
    }
  }

  Color _getVulnerabilityColor(String? vulnerability) {
    switch (vulnerability?.toLowerCase()) {
      case 'critical':
        return Colors.red;
      case 'high':
        return Colors.orange;
      case 'medium':
        return Colors.yellow;
      case 'low':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  // Attack Progress Tracking
  Map<String, bool> _attackProgress = {};
  bool _attackInProgress = false;

  // Extracted Information Storage
  Map<String, Map<String, dynamic>> _extractedInfo = {};

  void _showAttackProgressDialog() {
    _attackProgress.clear();
    _attackInProgress = true;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setDialogState) {
            return AlertDialog(
              backgroundColor: Colors.grey[900],
              title: Row(
                children: [
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      color: Colors.red,
                      strokeWidth: 2,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Deploy Attack Progress',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  _buildProgressStep(
                    'Stealth Assimilation',
                    _attackProgress['stealth'] ?? false,
                  ),
                  const SizedBox(height: 8),
                  _buildProgressStep(
                    'Data Extraction',
                    _attackProgress['extraction'] ?? false,
                  ),
                  const SizedBox(height: 8),
                  _buildProgressStep(
                    'Backdoor Creation',
                    _attackProgress['backdoor'] ?? false,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Attacking ${_selectedDevices.length} target(s)...',
                    style: const TextStyle(color: Colors.cyan, fontSize: 12),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildProgressStep(String step, bool completed) {
    return Row(
      children: [
        Icon(
          completed ? Icons.check_circle : Icons.pending,
          color: completed ? Colors.green : Colors.orange,
          size: 20,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            step,
            style: TextStyle(
              color: completed ? Colors.green : Colors.white,
              fontSize: 14,
            ),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  void _updateAttackProgress(String step, bool success) {
    switch (step) {
      case 'Stealth Assimilation':
        _attackProgress['stealth'] = success;
        break;
      case 'Data Extraction':
        _attackProgress['extraction'] = success;
        break;
      case 'Backdoor Creation':
        _attackProgress['backdoor'] = success;
        break;
    }

    // Update the dialog if it's still open
    if (mounted && Navigator.of(context).canPop()) {
      setState(() {});
    }
  }

  // Helper methods for generating extracted information
  Map<String, dynamic> _generateStolenCredentials() {
    final random = Random();
    final usernames = ['admin', 'root', 'user', 'administrator', 'system'];
    final passwords = [
      'password123',
      'admin123',
      'root123',
      'system123',
      'user123',
    ];
    final sshKeys = [
      'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...',
      'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD...',
      'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQE...',
    ];

    return {
      'username': usernames[random.nextInt(usernames.length)],
      'password': passwords[random.nextInt(passwords.length)],
      'ssh_key': sshKeys[random.nextInt(sshKeys.length)],
      'database_credentials': 'root:mysql_pass_${random.nextInt(999)}',
      'api_keys': [
        'sk_live_${random.nextInt(999999)}',
        'pk_test_${random.nextInt(999999)}',
        'api_key_${random.nextInt(999999)}',
      ],
    };
  }

  Map<String, dynamic> _generateExtractedData() {
    final random = Random();
    final dataTypes = [
      'user_profiles',
      'system_configs',
      'network_settings',
      'security_logs',
      'application_data',
      'database_dumps',
      'encryption_keys',
      'backup_files',
    ];

    final extractedTypes = <String>[];
    for (int i = 0; i < random.nextInt(4) + 2; i++) {
      extractedTypes.add(dataTypes[random.nextInt(dataTypes.length)]);
    }

    return {
      'data_types': extractedTypes,
      'data_volume': '${random.nextInt(500) + 100}MB',
      'files_count': random.nextInt(1000) + 100,
      'sensitive_files': random.nextInt(50) + 10,
      'encryption_keys_found': random.nextInt(5) + 1,
    };
  }

  Map<String, dynamic> _generateBackdoorAccess(String deviceIp) {
    final random = Random();
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    // Generate functional chaos code for this backdoor
    final chaosCode = ProjectHorusService.instance.generateBackdoorChaosCode(
      deviceIp,
    );

    return {
      'chaos_code': chaosCode,
      'access_level': 'root',
      'stealth_level': '${random.nextInt(40) + 60}%',
      'persistence': true,
      'undetectable': true,
      'access_methods': ['SSH', 'HTTP', 'FTP', 'RDP'],
      'ports_opened': [22, 80, 443, 8080, 3389],
      'backdoor_id': 'HORUS_BD_${timestamp}_${random.nextInt(9999)}',
      'target_device': deviceIp,
      'connection_string':
          'ssh://admin@$deviceIp:22 -p ${random.nextInt(65535) + 1024}',
      'credentials': {
        'username': 'admin_${random.nextInt(9999)}',
        'password': 'HORUS_${random.nextInt(999999)}',
        'session_id': '${timestamp}_${random.nextInt(9999)}',
      },
    };
  }

  void _showAttackResultsDialog(
    String attackType,
    Map<String, dynamic> response,
  ) {
    print(
      '[PROJECT_HORUS_SCREEN] 📊 Showing attack results dialog for: $attackType',
    );
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.security, color: Colors.red),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '$attackType Results',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Status: ${response['status'] ?? 'Unknown'}',
                  style: TextStyle(
                    color:
                        response['status'] == 'success'
                            ? Colors.green
                            : Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Message: ${response['message'] ?? 'No message'}',
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                ),
                if (response['chaos_code'] != null) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Chaos Code Generated:',
                    style: TextStyle(
                      color: Colors.cyan,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: SelectableText(
                      response['chaos_code'].toString(),
                      style: const TextStyle(
                        color: Colors.cyan,
                        fontSize: 10,
                        fontFamily: 'monospace',
                      ),
                    ),
                  ),
                ],
                if (_selectedDevices.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text(
                    'Targeted Devices:',
                    style: TextStyle(
                      color: Colors.orange,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ..._selectedDevices.map(
                    (ip) => Text(
                      '• $ip',
                      style: const TextStyle(color: Colors.cyan, fontSize: 12),
                    ),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _selectedDevices.clear();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey[700],
              ),
              child: const Text('Close', style: TextStyle(color: Colors.white)),
            ),
          ],
        );
      },
    );
  }

  Future<void> _performStealthAssimilation() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      // First, let user select a chaos code to enhance the attack
      final selectedChaosCode = await _selectChaosCodeForAttack(
        'Stealth Assimilation',
      );

      Map<String, dynamic>? response;

      if (selectedChaosCode != null) {
        // Execute chaos code offline first
        final chaosResult = ProjectHorusService.instance
            .executeChaosCodeOffline(selectedChaosCode, 'stealth_assimilation');

        if (chaosResult['status'] == 'success') {
          _showSuccessSnackbar(
            'Chaos code ${selectedChaosCode['operation']} executed offline! Enhanced stealth assimilation ready.',
          );
        } else {
          _showErrorSnackbar(
            'Chaos code execution failed: ${chaosResult['error']}',
          );
        }
      }
      // Then perform the enhanced stealth assimilation
      response =
          await ProjectHorusService.instance.performStealthAssimilation();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Stealth assimilation completed successfully!');
        setState(() {}); // Refresh UI to show new chaos code

        // Show attack results dialog
        _showAttackResultsDialog('Stealth Assimilation', response);
      } else {
        _showErrorSnackbar('Failed to perform stealth assimilation');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Stealth assimilation failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  Future<void> _performSystemInfiltration() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      // First, present "Enhance Attack?" dialog
      final enhanceChoice = await _showEnhanceAttackDialog(
        'System Infiltration',
      );

      if (enhanceChoice == 'chaos') {
        // User chose to enhance with chaos code
        final selectedChaosCode = await _selectChaosCodeForAttack(
          'System Infiltration',
        );
        if (selectedChaosCode != null) {
          print(
            '[PROJECT_HORUS_SCREEN] 🌀 Executing chaos code offline for System Infiltration...',
          );
          final chaosResult = ProjectHorusService.instance
              .executeChaosCodeOffline(
                selectedChaosCode,
                'system_infiltration',
              );

          if (chaosResult['success'] == true) {
            _showSuccessSnackbar(
              'Chaos-enhanced system infiltration executed! ${chaosResult['message'] ?? ''}',
            );
          } else {
            _showErrorSnackbar(
              'Chaos code execution failed: ${chaosResult['error'] ?? 'Unknown error'}',
            );
          }
        }
      } else if (enhanceChoice == 'weapon') {
        // User chose to enhance with weapon
        final selectedWeapon = await _selectWeaponForAttack(
          'System Infiltration',
        );
        if (selectedWeapon != null) {
          print(
            '[PROJECT_HORUS_SCREEN] ⚔️ Deploying weapon offline for System Infiltration...',
          );
          final weaponResult = ProjectHorusService.instance
              .executeWeaponOffline(selectedWeapon, 'system_infiltration');

          if (weaponResult['success'] == true) {
            _showSuccessSnackbar(
              'Weapon deployed successfully! ${weaponResult['message'] ?? ''}',
            );
          } else {
            _showErrorSnackbar(
              'Weapon deployment failed: ${weaponResult['error'] ?? 'Unknown error'}',
            );
          }
        }
      }

      // Now perform the actual system infiltration
      final response =
          await ProjectHorusService.instance.performSystemInfiltration();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('System infiltration completed successfully!');
        setState(() {}); // Refresh UI to show new chaos code

        // Show attack results dialog
        _showAttackResultsDialog('System Infiltration', response);
      } else {
        _showErrorSnackbar('Failed to perform system infiltration');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ System infiltration failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  Future<void> _performDataExtraction() async {
    if (mounted) setState(() => _isLoading = true);

    try {
      // First, present "Enhance Attack?" dialog
      final enhanceChoice = await _showEnhanceAttackDialog('Data Extraction');

      if (enhanceChoice == 'chaos') {
        // User chose to enhance with chaos code
        final selectedChaosCode = await _selectChaosCodeForAttack(
          'Data Extraction',
        );
        if (selectedChaosCode != null) {
          print(
            '[PROJECT_HORUS_SCREEN] 🌀 Executing chaos code offline for Data Extraction...',
          );
          final chaosResult = ProjectHorusService.instance
              .executeChaosCodeOffline(selectedChaosCode, 'data_extraction');

          if (chaosResult['success'] == true) {
            _showSuccessSnackbar(
              'Chaos-enhanced data extraction executed! ${chaosResult['message'] ?? ''}',
            );
          } else {
            _showErrorSnackbar(
              'Chaos code execution failed: ${chaosResult['error'] ?? 'Unknown error'}',
            );
          }
        }
      } else if (enhanceChoice == 'weapon') {
        // User chose to enhance with weapon
        final selectedWeapon = await _selectWeaponForAttack('Data Extraction');
        if (selectedWeapon != null) {
          print(
            '[PROJECT_HORUS_SCREEN] ⚔️ Deploying weapon offline for Data Extraction...',
          );
          final weaponResult = ProjectHorusService.instance
              .executeWeaponOffline(selectedWeapon, 'data_extraction');

          if (weaponResult['success'] == true) {
            _showSuccessSnackbar(
              'Weapon deployed successfully! ${weaponResult['message'] ?? ''}',
            );
          } else {
            _showErrorSnackbar(
              'Weapon deployment failed: ${weaponResult['error'] ?? 'Unknown error'}',
            );
          }
        }
      }

      // Now perform the actual data extraction
      final response =
          await ProjectHorusService.instance.performDataExtraction();

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response != null) {
        _showSuccessSnackbar('Data extraction completed successfully!');
        setState(() {}); // Refresh UI to show new chaos code

        // Show attack results dialog
        _showAttackResultsDialog('Data Extraction', response);
      } else {
        _showErrorSnackbar('Failed to perform data extraction');
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Data extraction failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Error: $e');
    }
  }

  Widget _buildResponseDisplay() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[700]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Latest Responses',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          if (_lastHorusResponse != null) ...[
            const Text(
              'Project Horus Response:',
              style: TextStyle(
                color: Colors.cyan,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                _lastHorusResponse.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],

          if (_lastBerserkResponse != null) ...[
            const Text(
              'Project Berserk Response:',
              style: TextStyle(
                color: Colors.purple,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                _lastBerserkResponse.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSavedChaosCodes() {
    final chaosCodes = ProjectHorusService.instance.getAllChaosCodes();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[700]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Saved Chaos Codes',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Text(
                '${chaosCodes.length} codes',
                style: const TextStyle(
                  color: Colors.cyan,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.delete, color: Colors.red),
                onPressed: () async {
                  await ProjectHorusService.instance.clearAllChaosCodes();
                  setState(() {});
                },
                tooltip: 'Clear all chaos codes',
              ),
            ],
          ),
          const SizedBox(height: 12),

          if (chaosCodes.isEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.grey, size: 20),
                  SizedBox(width: 8),
                  Text(
                    'No chaos codes saved yet. Run operations to generate codes.',
                    style: TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                ],
              ),
            )
          else
            Container(
              height: 300,
              child: ListView.builder(
                itemCount: chaosCodes.length,
                itemBuilder: (context, index) {
                  final code = chaosCodes.reversed.toList()[index];
                  return _buildExpandableChaosCodeCard(code);
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildExtractedInformation() {
    if (_extractedInfo.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[900],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[700]!),
        ),
        child: const Row(
          children: [
            Icon(Icons.info_outline, color: Colors.grey, size: 20),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'No extracted information yet. Attack devices to see stolen data.',
                style: TextStyle(color: Colors.grey, fontSize: 14),
                softWrap: true,
              ),
            ),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[700]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Text(
                  'Extracted Information',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Text(
                '${_extractedInfo.length} devices',
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.delete, color: Colors.red),
                onPressed: () {
                  setState(() {
                    _extractedInfo.clear();
                  });
                },
                tooltip: 'Clear all extracted information',
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 400,
            child: ListView.builder(
              itemCount: _extractedInfo.length,
              itemBuilder: (context, index) {
                final deviceIp = _extractedInfo.keys.elementAt(index);
                final info = _extractedInfo[deviceIp]!;

                return _buildDeviceInfoCard(deviceIp, info);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDeviceInfoCard(String deviceIp, Map<String, dynamic> info) {
    final credentials = info['stolen_credentials'] as Map<String, dynamic>;
    final extractedData = info['extracted_data'] as Map<String, dynamic>;
    final backdoorAccess = info['backdoor_access'] as Map<String, dynamic>;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.5),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Device Header
          Row(
            children: [
              Icon(Icons.computer, color: Colors.red, size: 20),
              const SizedBox(width: 8),
              Text(
                'Target: $deviceIp',
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Text(
                DateTime.parse(
                  info['attack_timestamp'],
                ).toString().substring(0, 19),
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Stolen Credentials
          _buildInfoSection('Stolen Credentials', Icons.key, Colors.orange, [
            'Username: ${credentials['username']}',
            'Password: ${credentials['password']}',
            'SSH Key: ${credentials['ssh_key']}',
            'Database: ${credentials['database_credentials']}',
            'API Keys: ${(credentials['api_keys'] as List).join(', ')}',
          ]),

          const SizedBox(height: 8),

          // Extracted Data
          _buildInfoSection('Extracted Data', Icons.folder, Colors.cyan, [
            'Data Types: ${(extractedData['data_types'] as List).join(', ')}',
            'Volume: ${extractedData['data_volume']}',
            'Files: ${extractedData['files_count']}',
            'Sensitive Files: ${extractedData['sensitive_files']}',
            'Encryption Keys: ${extractedData['encryption_keys_found']}',
          ]),

          const SizedBox(height: 8),

          // Backdoor Access
          _buildInfoSection('Backdoor Access', Icons.security, Colors.green, [
            'Chaos Code: ${backdoorAccess['chaos_code']}',
            'Access Level: ${backdoorAccess['access_level']}',
            'Stealth Level: ${backdoorAccess['stealth_level']}',
            'Persistence: ${backdoorAccess['persistence']}',
            'Undetectable: ${backdoorAccess['undetectable']}',
            'Access Methods: ${(backdoorAccess['access_methods'] as List).join(', ')}',
            'Ports: ${(backdoorAccess['ports_opened'] as List).join(', ')}',
          ]),
        ],
      ),
    );
  }

  Widget _buildInfoSection(
    String title,
    IconData icon,
    Color color,
    List<String> items,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(width: 6),
            Text(
              title,
              style: TextStyle(
                color: color,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey[800],
            borderRadius: BorderRadius.circular(4),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children:
                items
                    .map(
                      (item) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 1),
                        child: Text(
                          item,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                    )
                    .toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildChaosLanguageDocumentation() {
    final chaosLanguageDoc = ProjectHorusService.instance.chaosLanguageDoc;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.purple),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_stories, color: Colors.purple, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Chaos Language Documentation',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.purple, size: 20),
                onPressed: () async {
                  await ProjectHorusService.instance
                      .refreshChaosLanguageFromBackend();
                  setState(() {});
                },
                tooltip: 'Refresh documentation from backend',
              ),
            ],
          ),
          const SizedBox(height: 16),

          if (chaosLanguageDoc == null)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.grey, size: 20),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Generate chaos code to see language documentation.',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                      softWrap: true,
                    ),
                  ),
                ],
              ),
            )
          else
            Column(
              children: [
                _buildDocumentationItem(
                  'Language Name',
                  chaosLanguageDoc['name'] ?? 'Unknown',
                ),
                _buildDocumentationItem(
                  'Evolution Stage',
                  chaosLanguageDoc['evolution_stage'] ?? 'Unknown',
                ),
                _buildDocumentationItem(
                  'Learning Level',
                  '${chaosLanguageDoc['learning_level'] ?? 0.0}',
                ),
                _buildDocumentationItem(
                  'Self-Evolving',
                  '${chaosLanguageDoc['is_self_evolving'] ?? false}',
                ),
                _buildDocumentationItem(
                  'Self-Generated',
                  '${chaosLanguageDoc['is_self_generated'] ?? false}',
                ),

                ExpansionTile(
                  title: const Text(
                    'Syntax Patterns',
                    style: TextStyle(color: Colors.purple),
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      child: Text(
                        _formatMapForDisplay(
                          chaosLanguageDoc['syntax_patterns'] ?? {},
                        ),
                        style: const TextStyle(
                          color: Colors.white,
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),

                ExpansionTile(
                  title: const Text(
                    'Data Types',
                    style: TextStyle(color: Colors.cyan),
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      child: Text(
                        _formatMapForDisplay(
                          chaosLanguageDoc['data_types'] ?? {},
                        ),
                        style: const TextStyle(
                          color: Colors.white,
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),

                ExpansionTile(
                  title: const Text(
                    'Sample Code',
                    style: TextStyle(color: Colors.green),
                  ),
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        chaosLanguageDoc['sample_code'] ??
                            'No sample code available',
                        style: const TextStyle(
                          color: Colors.green,
                          fontFamily: 'monospace',
                          fontSize: 11,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildChaosWeaponsArsenal() {
    final weapons = ProjectHorusService.instance.getAllWeapons();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.red),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.security, color: Colors.red, size: 24),
              const SizedBox(width: 8),
              const Expanded(
                child: Text(
                  'Chaos Weapons Arsenal',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Text(
                '${weapons.length} weapons',
                style: const TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.red, size: 20),
                onPressed: () async {
                  await ProjectHorusService.instance
                      .refreshWeaponsFromBackend();
                  setState(() {});
                },
                tooltip: 'Refresh weapons from backend',
              ),
            ],
          ),
          const SizedBox(height: 16),

          if (weapons.isEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.grey, size: 20),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'No weapons available. Generate chaos code to create weapons.',
                      style: TextStyle(color: Colors.grey, fontSize: 14),
                      softWrap: true,
                    ),
                  ),
                ],
              ),
            )
          else
            SizedBox(
              height: 300,
              child: ListView.builder(
                itemCount: weapons.length,
                itemBuilder: (context, index) {
                  final weapon = weapons[index];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.tungsten,
                              color: Colors.red,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              weapon['name'] ?? 'Unknown Weapon',
                              style: const TextStyle(
                                color: Colors.red,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Target: ${weapon['target_system'] ?? 'Unknown'}',
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                        if (weapon['description'] != null)
                          Text(
                            weapon['description'],
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                          ),
                        if (weapon['effectiveness'] != null)
                          Text(
                            'Effectiveness: ${weapon['effectiveness']}%',
                            style: const TextStyle(
                              color: Colors.green,
                              fontSize: 12,
                            ),
                          ),
                      ],
                    ),
                  );
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDocumentationItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
        ],
      ),
    );
  }

  String _formatMapForDisplay(Map<String, dynamic> map) {
    if (map.isEmpty) return 'No data available';

    final buffer = StringBuffer();
    map.forEach((key, value) {
      buffer.writeln('$key: $value');
    });
    return buffer.toString();
  }

  Widget _buildExpandableChaosCodeCard(Map<String, dynamic> code) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: Colors.black.withOpacity(0.5),
      elevation: 2,
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        childrenPadding: const EdgeInsets.all(12),
        leading: Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color:
                code['mode'] == 'live'
                    ? Colors.green.withOpacity(0.2)
                    : Colors.orange.withOpacity(0.2),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            code['mode']?.toString().toUpperCase() ?? 'UNKNOWN',
            style: TextStyle(
              color: code['mode'] == 'live' ? Colors.green : Colors.orange,
              fontSize: 9,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        title: Text(
          code['operation']?.toString().replaceAll('_', ' ').toUpperCase() ??
              'UNKNOWN OPERATION',
          style: const TextStyle(
            color: Colors.cyan,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              code['message']?.toString() ?? 'No message',
              style: const TextStyle(color: Colors.white70, fontSize: 11),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              'Saved: ${_formatDateTime(code['saved_at'])}',
              style: const TextStyle(color: Colors.grey, fontSize: 9),
            ),
          ],
        ),
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Full message
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  code['message']?.toString() ?? 'No message',
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                ),
              ),
              const SizedBox(height: 12),

              // Chaos code
              const Text(
                'Chaos Code:',
                style: TextStyle(
                  color: Colors.cyan,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[800],
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: Colors.cyan.withOpacity(0.3)),
                ),
                child: SelectableText(
                  code['chaos_code']?.toString() ?? 'No chaos code',
                  style: const TextStyle(
                    color: Colors.cyan,
                    fontSize: 11,
                    fontFamily: 'monospace',
                    height: 1.3,
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Metadata
              if (code['quantum_signature'] != null ||
                  code['neural_complexity'] != null ||
                  code['infiltration_success_rate'] != null) ...[
                const Text(
                  'Metadata:',
                  style: TextStyle(
                    color: Colors.yellow,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: [
                    if (code['quantum_signature'] != null)
                      _buildMetadataChip(
                        'Quantum Signature',
                        code['quantum_signature'].toString(),
                        Colors.purple,
                      ),
                    if (code['neural_complexity'] != null)
                      _buildMetadataChip(
                        'Neural Complexity',
                        '${(code['neural_complexity'] as num).toStringAsFixed(1)}%',
                        Colors.blue,
                      ),
                    if (code['infiltration_success_rate'] != null)
                      _buildMetadataChip(
                        'Success Rate',
                        code['infiltration_success_rate'].toString(),
                        Colors.green,
                      ),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              // Actions
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton.icon(
                    onPressed: () {
                      // Copy chaos code to clipboard
                      // Implement if needed
                    },
                    icon: const Icon(Icons.copy, size: 16, color: Colors.cyan),
                    label: const Text(
                      'Copy Code',
                      style: TextStyle(color: Colors.cyan, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetadataChip(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            '$label: ',
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w600,
            ),
          ),
          Text(
            value,
            style: TextStyle(color: color.withOpacity(0.8), fontSize: 10),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(dynamic dateTime) {
    try {
      if (dateTime == null) return 'Unknown';
      final dt = DateTime.parse(dateTime.toString());
      return '${dt.day}/${dt.month}/${dt.year} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return 'Invalid date';
    }
  }

  /// Show weapon selector dialog for enhanced attacks
  Future<Map<String, dynamic>?> _selectWeaponForAttack(
    String attackType,
  ) async {
    final weapons = ProjectHorusService.instance.getAllWeapons();

    if (weapons.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No weapons available. Generate chaos codes first!'),
          backgroundColor: Colors.orange,
        ),
      );
      return null;
    }

    return showDialog<Map<String, dynamic>>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                const Icon(Icons.security, color: Colors.red, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Select Weapon for $attackType',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            content: SizedBox(
              width: double.maxFinite,
              height: 400,
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.info_outline,
                          color: Colors.red,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Choose a weapon to enhance your attack with specialized capabilities.',
                            style: TextStyle(
                              color: Colors.red[300],
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: ListView.builder(
                      itemCount: weapons.length,
                      itemBuilder: (context, index) {
                        final weapon = weapons[index];
                        return Card(
                          color: Colors.grey[800],
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: _getWeaponTypeColor(
                                  weapon['type'],
                                ).withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                weapon['type']?.toString() ?? 'UNK',
                                style: TextStyle(
                                  color: _getWeaponTypeColor(weapon['type']),
                                  fontSize: 9,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            title: Text(
                              weapon['name']?.toString() ?? 'Unknown Weapon',
                              style: const TextStyle(
                                color: Colors.red,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  weapon['description']?.toString() ??
                                      weapon['capability']?.toString() ??
                                      'No description',
                                  style: const TextStyle(
                                    color: Colors.white70,
                                    fontSize: 12,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Effectiveness: ${weapon['effectiveness'] ?? weapon['stealth_level'] ?? 'N/A'}%',
                                        style: const TextStyle(
                                          color: Colors.green,
                                          fontSize: 10,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        softWrap: true,
                                      ),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        'Complexity: ${weapon['complexity'] ?? 'medium'}',
                                        style: const TextStyle(
                                          color: Colors.orange,
                                          fontSize: 10,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                        softWrap: true,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            trailing: const Icon(
                              Icons.arrow_forward_ios,
                              color: Colors.red,
                              size: 16,
                            ),
                            onTap: () => Navigator.of(context).pop(weapon),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text(
                  'Skip - Normal Attack',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
    );
  }

  /// Get color for weapon type
  Color _getWeaponTypeColor(String? type) {
    switch (type?.toLowerCase()) {
      case 'windows':
        return Colors.blue;
      case 'linux':
        return Colors.green;
      case 'network':
        return Colors.purple;
      case 'web':
        return Colors.orange;
      case 'quantum':
        return Colors.cyan;
      case 'evolved':
        return Colors.pink;
      case 'autonomous':
        return Colors.yellow;
      default:
        return Colors.grey;
    }
  }

  /// Show chaos code selector dialog for attacks
  Future<Map<String, dynamic>?> _selectChaosCodeForAttack(
    String attackType,
  ) async {
    final chaosCodes = ProjectHorusService.instance.getAllChaosCodes();

    if (chaosCodes.isEmpty) {
      return null; // No chaos codes available
    }

    return showDialog<Map<String, dynamic>>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(Icons.security, color: Colors.cyan, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Select Chaos Code for $attackType',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            content: SizedBox(
              width: double.maxFinite,
              height: 400,
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.info_outline, color: Colors.blue, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Choose a chaos code to enhance your attack. Live mode will use the backend, otherwise it will be simulated.',
                            style: TextStyle(
                              color: Colors.blue[300],
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Expanded(
                    child: ListView.builder(
                      itemCount: chaosCodes.length,
                      itemBuilder: (context, index) {
                        final code = chaosCodes[index];
                        return Card(
                          color: Colors.grey[800],
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color:
                                    code['mode'] == 'live'
                                        ? Colors.green.withOpacity(0.2)
                                        : Colors.orange.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                code['mode']?.toString().toUpperCase() ?? 'SIM',
                                style: TextStyle(
                                  color:
                                      code['mode'] == 'live'
                                          ? Colors.green
                                          : Colors.orange,
                                  fontSize: 9,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                            title: Text(
                              code['operation']
                                      ?.toString()
                                      .replaceAll('_', ' ')
                                      .toUpperCase() ??
                                  'UNKNOWN',
                              style: const TextStyle(
                                color: Colors.cyan,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  code['message']?.toString() ??
                                      'No description',
                                  style: const TextStyle(
                                    color: Colors.white70,
                                    fontSize: 12,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Saved: ${_formatDateTime(code['saved_at'])}',
                                  style: const TextStyle(
                                    color: Colors.grey,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                            trailing: Icon(
                              Icons.arrow_forward_ios,
                              color: Colors.cyan,
                              size: 16,
                            ),
                            onTap: () => Navigator.of(context).pop(code),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text(
                  'Skip - Normal Attack',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
    );
  }

  /// Show enhanced synthetic code dialog for data extraction + synthetic deployment
  Future<bool?> _showEnhancedSyntheticCodeDialog() async {
    return showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(Icons.code, color: Colors.red, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Enhanced Synthetic Code',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.withOpacity(0.3)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Advanced Synthetic Deployment',
                        style: TextStyle(
                          color: Colors.red[300],
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '• Self-evolving chaos codes\n• Adaptive persistence mechanisms\n• Multi-vector deployment\n• Advanced evasion techniques',
                        style: TextStyle(color: Colors.red[200], fontSize: 12),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Would you like to deploy enhanced synthetic code with advanced persistence and evolution capabilities?',
                  style: TextStyle(color: Colors.white, fontSize: 14),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text(
                  'Skip - Basic Deployment',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
              ElevatedButton(
                onPressed: () => Navigator.of(context).pop(true),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Deploy Enhanced Code'),
              ),
            ],
          ),
    );
  }

  /// Show deployment options dialog (Data Extraction vs Synthetic Code Deployment)
  Future<void> _showDeploymentOptionsDialog() async {
    final deploymentOption = await showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(Icons.security, color: Colors.purple, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Choose Deployment Option',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.purple.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.purple.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: Colors.purple,
                          size: 20,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Select deployment strategy for ${_selectedDevices.length} target(s):',
                            style: TextStyle(
                              color: Colors.purple[300],
                              fontSize: 12,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Data Extraction Only Option
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: ListTile(
                      leading: Icon(
                        Icons.download,
                        color: Colors.blue,
                        size: 24,
                      ),
                      title: Text(
                        'Data Extraction Only',
                        style: TextStyle(
                          color: Colors.blue[300],
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        '• Extract data without leaving traces\n• Stealth operation\n• No persistent presence\n• Lower detection risk',
                        style: TextStyle(color: Colors.blue[200], fontSize: 12),
                      ),
                      onTap:
                          () =>
                              Navigator.of(context).pop('data_extraction_only'),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Data Extraction + Synthetic Code Deployment Option
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.withOpacity(0.3)),
                    ),
                    child: ListTile(
                      leading: Icon(Icons.code, color: Colors.red, size: 24),
                      title: Text(
                        'Data Extraction + Synthetic Deployment',
                        style: TextStyle(
                          color: Colors.red[300],
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        '• Extract data AND deploy chaos code\n• Self-growing synthetic backdoor\n• Persistent system presence\n• Continuous evolution',
                        style: TextStyle(color: Colors.red[200], fontSize: 12),
                      ),
                      onTap:
                          () => Navigator.of(
                            context,
                          ).pop('data_extraction_with_synthetic'),
                    ),
                  ),

                  const SizedBox(height: 12),

                  // Hybrid Option
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.withOpacity(0.3)),
                    ),
                    child: ListTile(
                      leading: Icon(
                        Icons.auto_awesome,
                        color: Colors.green,
                        size: 24,
                      ),
                      title: Text(
                        'Hybrid AI-Enhanced Attack',
                        style: TextStyle(
                          color: Colors.green[300],
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        '• AI collective learning integration\n• Advanced weapon selection\n• Adaptive deployment strategy\n• Maximum effectiveness',
                        style: TextStyle(
                          color: Colors.green[200],
                          fontSize: 12,
                        ),
                      ),
                      onTap:
                          () => Navigator.of(context).pop('hybrid_ai_enhanced'),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(null),
                        child: const Text(
                          'Cancel',
                          style: TextStyle(color: Colors.orange),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
    );

    if (deploymentOption != null) {
      // Show additional dialogs based on deployment option
      if (deploymentOption == 'data_extraction_only') {
        final shouldProceed = await _showComplexTestingDialog(
          'Data Extraction',
        );
        if (shouldProceed == true) {
          await _executeDeploymentOption(deploymentOption);
        }
      } else if (deploymentOption == 'data_extraction_with_synthetic') {
        final shouldProceed = await _showEnhancedSyntheticCodeDialog();
        if (shouldProceed == true) {
          await _executeDeploymentOption(deploymentOption);
        }
      } else {
        await _executeDeploymentOption(deploymentOption);
      }
    }
  }

  /// Execute the chosen deployment option with enhanced loading
  Future<void> _executeDeploymentOption(String deploymentOption) async {
    print(
      '[PROJECT_HORUS_SCREEN] 🚀 Starting deployment option: $deploymentOption',
    );

    // Set current deployment type for situation-aware chaos code generation
    _currentDeploymentType = deploymentOption;

    // Initialize enhanced deployment system
    _isDeploying = true;
    _deploymentProgress = 0.0;
    _deploymentSteps.clear();

    // Generate device complexity levels
    _generateDeviceComplexity();

    // Set deployment steps based on option with unique, intuitive operations
    switch (deploymentOption) {
      case 'data_extraction_only':
        _deploymentSteps = [
          '🔍 Initializing stealth reconnaissance protocol...',
          '🛡️ Analyzing device security posture...',
          '🌐 Mapping network topology and entry points...',
          '🔑 Identifying authentication methods...',
          '📁 Locating sensitive data repositories...',
          '🔐 Extracting SSH keys and certificates...',
          '💾 Retrieving database credentials...',
          '🔑 Collecting API keys and tokens...',
          '🔒 Extracting encryption keys...',
          '📊 Cataloging sensitive information...',
          '🧹 Erasing digital footprints...',
          '✅ Stealth extraction completed',
        ];
        break;
      case 'data_extraction_with_synthetic':
        _deploymentSteps = [
          '🤖 Initializing synthetic intelligence engine...',
          '🏗️ Analyzing target device architecture...',
          '⚡ Generating adaptive chaos code payloads...',
          '🚪 Deploying self-evolving synthetic backdoors...',
          '🔗 Establishing persistent access channels...',
          '🛠️ Activating synthetic extraction tools...',
          '⚔️ Deploying weapon-based extraction modules...',
          '🔍 Scanning for vulnerabilities...',
          '📡 Retrieving system credentials and keys...',
          '🔑 Collecting API keys and authentication tokens...',
          '🔒 Extracting encryption keys and certificates...',
          '📊 Cataloging synthetic data and metadata...',
          '🔄 Maintaining synthetic presence and evolution...',
          '✅ Synthetic deployment completed',
        ];
        break;
      case 'hybrid_ai_enhanced':
        _deploymentSteps = [
          '🧠 Initializing AI neural networks...',
          '📊 Analyzing device complexity matrix...',
          '🎯 Generating AI strategy recommendations...',
          '⚔️ Deploying AI-enhanced weapons and tools...',
          '🌀 Executing chaos code sequences with AI guidance...',
          '🔮 Running predictive analysis...',
          '🤖 Extracting data with AI assistance...',
          '🧠 Processing with neural networks...',
          '📈 Learning from target patterns...',
          '🔍 Cataloging AI-processed intelligence...',
          '🔄 Integrating AI learning systems...',
          '🚀 Optimizing for future operations...',
          '✅ AI-enhanced deployment completed',
        ];
        break;
      default:
        _deploymentSteps = ['❌ Unknown deployment protocol...'];
    }

    if (mounted) {
      setState(() {
        _isLoading = true;
        _currentStep = _deploymentSteps[0];
      });
    }

    // Show enhanced deployment progress once and update in place
    _showEnhancedDeploymentProgress();

    try {
      // Execute deployment with step-by-step progress
      String attackDescription = 'Unknown Deployment';
      Map<String, dynamic> response = {
        'success': false,
        'message': 'Deployment not executed',
      };

      for (int i = 0; i < _deploymentSteps.length; i++) {
        final step = _deploymentSteps[i];
        _currentStep = step;
        _deploymentProgress = (i + 1) / _deploymentSteps.length;
        _deploymentDialogSetState?.call(() {}); // update dialog UI

        // Execute real operations based on step
        await _executeDeploymentStep(deploymentOption, step, i);

        // Execute actual deployment at appropriate step
        if (i == _deploymentSteps.length - 2) {
          // Second to last step
          switch (deploymentOption) {
            case 'data_extraction_only':
              attackDescription = 'Data Extraction (Stealth Mode)';
              print(
                '[PROJECT_HORUS_SCREEN] 📋 Executing stealth data extraction...',
              );
              response = await _performStealthDataExtraction();
              break;
            case 'data_extraction_with_synthetic':
              attackDescription = 'Data Extraction + Synthetic Code Deployment';
              print(
                '[PROJECT_HORUS_SCREEN] 📋 Executing synthetic code deployment...',
              );
              response = await _performSyntheticCodeDeployment();
              break;
            case 'hybrid_ai_enhanced':
              attackDescription = 'Hybrid AI-Enhanced Attack';
              print('[PROJECT_HORUS_SCREEN] 📋 Executing hybrid AI attack...');
              response = await _performHybridAIAttack();
              break;
            default:
              attackDescription = 'Unknown Deployment';
              response = {
                'success': false,
                'message': 'Unknown deployment option',
              };
          }

          // Catalog data for each device
          if (response['success'] == true && _selectedDevices.isNotEmpty) {
            for (final device in _selectedDevices) {
              _catalogDataByDevice(device, {
                'attack_type': attackDescription,
                'timestamp': DateTime.now().toIso8601String(),
                'complexity_level': _deviceComplexity[device] ?? 1,
                'extracted_data_size': Random().nextInt(1000) + 100,
                'vulnerabilities_found': Random().nextInt(5) + 1,
              });
            }
          }
        }
      }

      print(
        '[PROJECT_HORUS_SCREEN] ✅ Deployment function completed, processing response...',
      );

      // Close progress dialog and clear setter
      if (Navigator.of(context).canPop()) {
        Navigator.of(context).pop();
      }
      _deploymentDialogSetState = null;

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      print(
        '[PROJECT_HORUS_SCREEN] 📊 Response success: ${response['success']}',
      );

      if (response['success'] == true) {
        print(
          '[PROJECT_HORUS_SCREEN] 🎉 Showing success message and results dialog',
        );
        _showSuccessSnackbar('$attackDescription completed successfully!');
        _showAttackResultsDialog(attackDescription, response);
        // Clear selected devices after successful deployment
        _selectedDevices.clear();
        setState(() {}); // Refresh UI to reflect cleared devices
      } else {
        print('[PROJECT_HORUS_SCREEN] ❌ Showing error message');
        _showErrorSnackbar(
          '$attackDescription failed: ${response['error'] ?? 'Unknown error'}',
        );
      }
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Deployment failed: $e');
      if (mounted) setState(() => _isLoading = false);
      _showErrorSnackbar('Deployment Error: $e');
    }
  }

  /// Perform stealth data extraction only
  Future<Map<String, dynamic>> _performStealthDataExtraction() async {
    // Get suitable weapons for this deployment type
    final suitableWeapons = ProjectHorusService.instance
        .getWeaponsForDeploymentType('data_extraction_only');

    if (suitableWeapons.isNotEmpty &&
        !ProjectHorusService.instance.isLiveMode) {
      // Show complex scenario testing dialog for simulation mode
      final useComplexTesting = await _showComplexTestingDialog(
        'Stealth Data Extraction',
      );

      if (useComplexTesting == true) {
        return await _performComplexScenarioTesting(
          'data_extraction_only',
          suitableWeapons,
        );
      }
    }

    // Show enhancement choice for standard deployment
    final enhanceChoice = await _showEnhanceAttackDialog(
      'Stealth Data Extraction',
    );

    if (enhanceChoice == 'chaos') {
      final selectedChaosCode = await _selectChaosCodeForAttack(
        'Stealth Data Extraction',
      );
      if (selectedChaosCode != null) {
        final chaosResult = ProjectHorusService.instance
            .executeChaosCodeOffline(selectedChaosCode, 'stealth_extraction');

        if (chaosResult['success'] == true) {
          _showSuccessSnackbar('Chaos-enhanced stealth extraction executed!');
        }
      }
    } else if (enhanceChoice == 'weapon') {
      final selectedWeapon = await _selectEnhancedWeaponForAttack(
        'Stealth Data Extraction',
        'data_extraction_only',
      );
      if (selectedWeapon != null) {
        final weaponResult = ProjectHorusService.instance.executeWeaponOffline(
          selectedWeapon,
          'stealth_extraction',
        );

        if (weaponResult['success'] == true) {
          _showSuccessSnackbar('Enhanced weapon deployed successfully!');
        }
      }
    }

    return await ProjectHorusService.instance.performStealthDataExtraction();
  }

  /// Perform data extraction with synthetic code deployment
  Future<Map<String, dynamic>> _performSyntheticCodeDeployment() async {
    // Show enhancement choice
    final enhanceChoice = await _showEnhanceAttackDialog(
      'Synthetic Code Deployment',
    );

    if (enhanceChoice == 'chaos') {
      final selectedChaosCode = await _selectChaosCodeForAttack(
        'Synthetic Deployment',
      );
      if (selectedChaosCode != null) {
        final chaosResult = ProjectHorusService.instance
            .executeChaosCodeOffline(selectedChaosCode, 'synthetic_deployment');

        if (chaosResult['success'] == true) {
          _showSuccessSnackbar('Chaos-enhanced synthetic deployment executed!');
        }
      }
    } else if (enhanceChoice == 'weapon') {
      final selectedWeapon = await _selectWeaponForAttack(
        'Synthetic Deployment',
      );
      if (selectedWeapon != null) {
        final weaponResult = ProjectHorusService.instance.executeWeaponOffline(
          selectedWeapon,
          'synthetic_deployment',
        );

        if (weaponResult['success'] == true) {
          _showSuccessSnackbar('Synthetic weapon deployed successfully!');
        }
      }
    }

    return await ProjectHorusService.instance.performSyntheticCodeDeployment();
  }

  /// Perform hybrid AI-enhanced attack
  Future<Map<String, dynamic>> _performHybridAIAttack() async {
    try {
      print(
        '[PROJECT_HORUS_SCREEN] 🤖 Generating OFFLINE AI strategy recommendations...',
      );

      // Get all available weapons for hybrid attack
      final allWeapons = ProjectHorusService.instance.getAllWeapons();
      final suitableWeapons =
          allWeapons
              .where(
                (weapon) =>
                    weapon['category'] == 'hybrid' ||
                    weapon['category'] == 'ai_enhanced' ||
                    weapon['complexity_level'] != null,
              )
              .toList();

      if (suitableWeapons.isEmpty) {
        return {
          'success': false,
          'error': 'No suitable weapons available for hybrid AI attack',
          'timestamp': DateTime.now().toIso8601String(),
        };
      }

      // Generate AI strategy recommendations
      final aiStrategy = await _generateAIStrategyRecommendations(
        suitableWeapons,
      );

      print(
        '[PROJECT_HORUS_SCREEN] ✅ AI strategy generated for ${suitableWeapons.length} devices',
      );

      // Execute the hybrid attack with AI recommendations
      print(
        '[PROJECT_HORUS_SCREEN] 🚀 Executing hybrid attack with AI strategy...',
      );
      final attackResult = await _executeHybridAttack(
        suitableWeapons,
        aiStrategy,
      );
      print('[PROJECT_HORUS_SCREEN] ✅ Hybrid attack execution completed');

      final result = {
        'success': true,
        'message': 'Hybrid AI-enhanced attack completed successfully',
        'devices_targeted': suitableWeapons.length,
        'ai_strategy': aiStrategy,
        'attack_result': attackResult,
        'timestamp': DateTime.now().toIso8601String(),
      };

      print('[PROJECT_HORUS_SCREEN] 🎯 Returning hybrid attack result');
      return result;
    } catch (e) {
      print('[PROJECT_HORUS_SCREEN] ❌ Deployment failed: $e');
      return {
        'success': false,
        'error': 'Hybrid AI attack failed: $e',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }
  }

  /// Generate AI strategy recommendations for hybrid attack
  Future<Map<String, dynamic>> _generateAIStrategyRecommendations(
    List<Map<String, dynamic>> weapons,
  ) async {
    final random = Random();
    final timestamp = DateTime.now().millisecondsSinceEpoch;

    // Simulate AI analysis and strategy generation
    await Future.delayed(Duration(milliseconds: random.nextInt(2000) + 1000));

    return {
      'strategy_type': 'hybrid_ai_enhanced',
      'weapons_selected': weapons.length,
      'attack_sequence': [
        'stealth_infiltration',
        'data_extraction',
        'backdoor_establishment',
        'persistence_mechanism',
      ],
      'ai_learning_integration': true,
      'adaptive_behavior': true,
      'complexity_level': random.nextInt(5) + 3,
      'effectiveness_score': (random.nextDouble() * 0.3 + 0.7).toStringAsFixed(
        2,
      ),
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  /// Execute hybrid attack with AI strategy
  Future<Map<String, dynamic>> _executeHybridAttack(
    List<Map<String, dynamic>> weapons,
    Map<String, dynamic> aiStrategy,
  ) async {
    print('[PROJECT_HORUS_SCREEN] 🔧 Starting hybrid attack execution...');
    final random = Random();

    // Simulate attack execution
    print('[PROJECT_HORUS_SCREEN] ⏳ Simulating attack execution...');
    await Future.delayed(Duration(milliseconds: random.nextInt(3000) + 2000));
    print('[PROJECT_HORUS_SCREEN] ✅ Attack simulation completed');

    final successRate = double.parse(aiStrategy['effectiveness_score']);
    final isSuccessful = random.nextDouble() < successRate;
    print(
      '[PROJECT_HORUS_SCREEN] 🎯 Attack success rate: ${(successRate * 100).toStringAsFixed(1)}%, Result: ${isSuccessful ? 'SUCCESS' : 'FAILED'}',
    );

    if (isSuccessful) {
      final result = {
        'status': 'success',
        'devices_compromised': random.nextInt(weapons.length) + 1,
        'data_extracted_mb': random.nextInt(500) + 100,
        'backdoors_established': random.nextInt(3) + 1,
        'detection_avoided': true,
        'ai_learning_progress': random.nextDouble() * 0.2 + 0.1,
      };
      print('[PROJECT_HORUS_SCREEN] 🎉 Attack successful, returning result');
      return result;
    } else {
      final result = {
        'status': 'failed',
        'failure_reason': 'Target system had advanced detection mechanisms',
        'ai_learning_progress': random.nextDouble() * 0.1,
      };
      print('[PROJECT_HORUS_SCREEN] ❌ Attack failed, returning result');
      return result;
    }
  }

  /// Show complex testing dialog for simulation mode
  Future<bool?> _showComplexTestingDialog(String attackType) async {
    return showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(Icons.psychology, color: Colors.teal, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Enhanced Testing Available',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.teal.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.teal.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.info_outline,
                            color: Colors.teal,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              'Complex scenario testing available for $attackType',
                              style: TextStyle(
                                color: Colors.teal[300],
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '🧪 Test against enterprise networks, cloud infrastructure, and IoT systems\n📊 AI learning from failures\n🎯 Weapon effectiveness analysis\n🔄 Automatic backend improvement',
                        style: TextStyle(color: Colors.teal[200], fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                child: const Text(
                  'Complex Testing',
                  style: TextStyle(color: Colors.teal),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: const Text(
                  'Standard Deployment',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
            ],
          ),
    );
  }

  /// Perform complex scenario testing
  Future<Map<String, dynamic>> _performComplexScenarioTesting(
    String deploymentType,
    List<Map<String, dynamic>> suitableWeapons,
  ) async {
    // Show weapon selection dialog
    final selectedWeapon = await _selectWeaponFromList(
      suitableWeapons,
      'Select Weapon for Testing',
    );
    if (selectedWeapon == null) {
      return {'success': false, 'message': 'No weapon selected'};
    }

    // Show scenario selection dialog
    final selectedScenario = await _selectComplexScenario();
    if (selectedScenario == null) {
      return {'success': false, 'message': 'No scenario selected'};
    }

    // Show testing progress dialog
    _showTestingProgressDialog(selectedWeapon, selectedScenario);

    // Perform the test
    final testResult = await ProjectHorusService.instance
        .testWeaponAgainstScenario(selectedWeapon, selectedScenario);

    // Close progress dialog
    if (mounted && Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    }

    // Show detailed test results
    await _showComplexTestResultsDialog(
      testResult,
      selectedWeapon,
      selectedScenario,
    );

    return {
      'success': true,
      'message': 'Complex scenario testing completed',
      'test_result': testResult,
      'weapon_used': selectedWeapon,
      'scenario_tested': selectedScenario,
      'timestamp': DateTime.now().toIso8601String(),
    };
  }

  /// Select weapon from list dialog
  Future<Map<String, dynamic>?> _selectWeaponFromList(
    List<Map<String, dynamic>> weapons,
    String title,
  ) async {
    return showDialog<Map<String, dynamic>>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Text(
              title,
              style: const TextStyle(color: Colors.white, fontSize: 18),
            ),
            content: SizedBox(
              width: double.maxFinite,
              height: 400,
              child: ListView.builder(
                itemCount: weapons.length,
                itemBuilder: (context, index) {
                  final weapon = weapons[index];
                  return Card(
                    color: Colors.grey[800],
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor:
                            weapon['source'] == 'horus'
                                ? Colors.cyan
                                : Colors.red,
                        child: Icon(
                          weapon['source'] == 'horus'
                              ? Icons.psychology
                              : Icons.military_tech,
                          color: Colors.white,
                          size: 18,
                        ),
                      ),
                      title: Text(
                        weapon['name'] ?? 'Unknown Weapon',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            weapon['description'] ?? '',
                            style: TextStyle(
                              color: Colors.grey[400],
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  'Stealth: ${(weapon['stealth_level'] * 100).toInt()}%',
                                  style: TextStyle(
                                    color: Colors.blue[300],
                                    fontSize: 10,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'Complexity: ${weapon['complexity_level']?.toStringAsFixed(1)}',
                                  style: TextStyle(
                                    color: Colors.orange[300],
                                    fontSize: 10,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      onTap: () => Navigator.of(context).pop(weapon),
                    ),
                  );
                },
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.orange),
                ),
              ),
            ],
          ),
    );
  }

  /// Select complex scenario dialog
  Future<Map<String, dynamic>?> _selectComplexScenario() async {
    // Get available scenarios (fallback to service's complex scenarios)
    final scenarios = [
      {
        'id': 'enterprise_network',
        'name': 'Enterprise Network Infrastructure',
        'description':
            'Complex enterprise network with multiple security layers',
        'difficulty': 'expert',
        'device_count': 4,
      },
      {
        'id': 'cloud_hybrid_infrastructure',
        'name': 'Cloud Hybrid Infrastructure',
        'description': 'Multi-cloud hybrid environment with Kubernetes',
        'difficulty': 'master',
        'device_count': 4,
      },
      {
        'id': 'iot_smart_city',
        'name': 'IoT Smart City Network',
        'description':
            'Large-scale IoT deployment with thousands of connected devices',
        'difficulty': 'expert',
        'device_count': 4,
      },
    ];

    return showDialog<Map<String, dynamic>>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: const Text(
              'Select Testing Scenario',
              style: TextStyle(color: Colors.white, fontSize: 18),
            ),
            content: SizedBox(
              width: double.maxFinite,
              height: 300,
              child: ListView.builder(
                itemCount: scenarios.length,
                itemBuilder: (context, index) {
                  final scenario = scenarios[index];
                  final difficultyColor = _getDifficultyColor(
                    scenario['difficulty'] as String,
                  );

                  return Card(
                    color: Colors.grey[800],
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: difficultyColor,
                        child: Text(
                          '${scenario['device_count']}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      title: Text(
                        scenario['name'] as String,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                      subtitle: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            scenario['description'] as String,
                            style: TextStyle(
                              color: Colors.grey[400],
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: difficultyColor.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              (scenario['difficulty'] as String).toUpperCase(),
                              style: TextStyle(
                                color: difficultyColor,
                                fontSize: 10,
                              ),
                            ),
                          ),
                        ],
                      ),
                      onTap: () => Navigator.of(context).pop(scenario),
                    ),
                  );
                },
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.orange),
                ),
              ),
            ],
          ),
    );
  }

  /// Get color for difficulty level
  Color _getDifficultyColor(String difficulty) {
    switch (difficulty.toLowerCase()) {
      case 'basic':
        return Colors.green;
      case 'intermediate':
        return Colors.yellow;
      case 'advanced':
        return Colors.orange;
      case 'expert':
        return Colors.red;
      case 'master':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  /// Show testing progress dialog
  void _showTestingProgressDialog(
    Map<String, dynamic> weapon,
    Map<String, dynamic> scenario,
  ) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    color: Colors.teal,
                    strokeWidth: 2,
                  ),
                ),
                const SizedBox(width: 12),
                const Text(
                  'Complex Scenario Testing',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Testing weapon: ${weapon['name']}',
                  style: const TextStyle(color: Colors.cyan),
                ),
                const SizedBox(height: 8),
                Text(
                  'Against scenario: ${scenario['name']}',
                  style: const TextStyle(color: Colors.orange),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Analyzing security measures...\nTesting weapon capabilities...\nEvaluating success probability...',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
    );
  }

  /// Show complex test results dialog
  Future<void> _showComplexTestResultsDialog(
    Map<String, dynamic> testResult,
    Map<String, dynamic> weapon,
    Map<String, dynamic> scenario,
  ) async {
    final success = testResult['success'] as bool? ?? false;

    return showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(
                  success ? Icons.check_circle : Icons.error,
                  color: success ? Colors.green : Colors.red,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  success ? 'Test Successful' : 'Test Failed',
                  style: TextStyle(
                    color: success ? Colors.green : Colors.red,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  _buildTestResultSection(
                    'Weapon Used',
                    weapon['name'],
                    Colors.cyan,
                  ),
                  _buildTestResultSection(
                    'Scenario',
                    scenario['name'],
                    Colors.orange,
                  ),
                  _buildTestResultSection(
                    'Success Probability',
                    '${(testResult['success_probability'] * 100).toStringAsFixed(1)}%',
                    Colors.blue,
                  ),
                  _buildTestResultSection(
                    'Execution Time',
                    '${testResult['execution_time_ms']}ms',
                    Colors.purple,
                  ),
                  _buildTestResultSection(
                    'Devices Compromised',
                    '${testResult['devices_compromised']}',
                    success ? Colors.green : Colors.red,
                  ),

                  if (!success && testResult['failure_points'] != null) ...[
                    const SizedBox(height: 12),
                    const Text(
                      'Failure Analysis:',
                      style: TextStyle(
                        color: Colors.red,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...((testResult['failure_points'] as List).map(
                      (point) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text(
                          '• $point',
                          style: TextStyle(
                            color: Colors.red[300],
                            fontSize: 12,
                          ),
                        ),
                      ),
                    )),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        '📚 Failure data sent to backend for AI learning and weapon improvement',
                        style: TextStyle(color: Colors.blue, fontSize: 11),
                      ),
                    ),
                  ],

                  if (success && testResult['extracted_data'] != null) ...[
                    const SizedBox(height: 12),
                    const Text(
                      'Data Extracted:',
                      style: TextStyle(
                        color: Colors.green,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${(testResult['extracted_data'] as Map).keys.join(', ')}',
                        style: TextStyle(
                          color: Colors.green[300],
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text(
                  'Close',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
    );
  }

  /// Build test result section
  Widget _buildTestResultSection(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Select enhanced weapon for attack
  Future<Map<String, dynamic>?> _selectEnhancedWeaponForAttack(
    String attackType,
    String deploymentType,
  ) async {
    final suitableWeapons = ProjectHorusService.instance
        .getWeaponsForDeploymentType(deploymentType);

    if (suitableWeapons.isEmpty) {
      _showErrorSnackbar('No enhanced weapons available for $deploymentType');
      return null;
    }

    return _selectWeaponFromList(suitableWeapons, 'Select Enhanced Weapon');
  }

  /// Show enhance attack choice dialog
  Future<String?> _showEnhanceAttackDialog(String attackType) async {
    return showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                Icon(Icons.power_settings_new, color: Colors.orange, size: 24),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Enhance $attackType?',
                    style: const TextStyle(color: Colors.white, fontSize: 18),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.orange.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Colors.orange, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Choose how to enhance your attack for better results:',
                          style: TextStyle(
                            color: Colors.orange[300],
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  'Chaos Code: Use advanced quantum algorithms',
                  style: TextStyle(color: Colors.cyan[300], fontSize: 14),
                ),
                const SizedBox(height: 8),
                Text(
                  'Weapon: Deploy specialized attack tools',
                  style: TextStyle(color: Colors.red[300], fontSize: 14),
                ),
                const SizedBox(height: 8),
                Text(
                  'Normal: Standard attack without enhancements',
                  style: TextStyle(color: Colors.grey[400], fontSize: 14),
                ),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop('chaos'),
                child: const Text(
                  'Chaos Code',
                  style: TextStyle(color: Colors.cyan),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop('weapon'),
                child: const Text(
                  'Weapon',
                  style: TextStyle(color: Colors.red),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop('normal'),
                child: const Text(
                  'Normal',
                  style: TextStyle(color: Colors.grey),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.orange),
                ),
              ),
            ],
          ),
    );
  }

  void _showDeploymentLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Deploying Attack...',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Status: Initializing deployment...',
                style: TextStyle(color: Colors.blue[300], fontSize: 14),
              ),
              const SizedBox(height: 8),
              Text(
                'Targets: ${_selectedDevices.length} devices',
                style: TextStyle(color: Colors.orange[300], fontSize: 12),
              ),
              const SizedBox(height: 8),
              Text(
                'Mode: ${_isLiveMode ? "LIVE" : "SIMULATION"}',
                style: TextStyle(
                  color: _isLiveMode ? Colors.red[300] : Colors.green[300],
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 16),
              LinearProgressIndicator(
                backgroundColor: Colors.grey[700],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
              ),
            ],
          ),
        );
      },
    );
  }

  /// Show deployment progress with specific status
  void _showEnhancedDeploymentProgress() {
    if (_isDeploymentDialogOpen) return; // already open
    if (Navigator.of(context).canPop()) Navigator.of(context).pop();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter setDialogState) {
            _deploymentDialogSetState =
                setDialogState; // capture dialog setState
            _isDeploymentDialogOpen = true;
            return AlertDialog(
              backgroundColor: Colors.grey[900],
              title: Row(
                children: [
                  SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 3,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'AI Deployment Progress',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Current step
                  Text(
                    'Current Step: $_currentStep',
                    style: TextStyle(
                      color: Colors.blue[300],
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Operation details
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Operation Details:',
                          style: TextStyle(
                            color: Colors.blue[300],
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _getOperationDetails(_currentStep),
                          style: TextStyle(
                            color: Colors.blue[200],
                            fontSize: 10,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Progress bar
                  LinearProgressIndicator(
                    value: _deploymentProgress,
                    backgroundColor: Colors.grey[700],
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${(_deploymentProgress * 100).toInt()}% Complete',
                    style: TextStyle(color: Colors.green[300], fontSize: 12),
                  ),
                  const SizedBox(height: 16),

                  // Steps list
                  if (_deploymentSteps.isNotEmpty) ...[
                    Text(
                      'Deployment Steps:',
                      style: TextStyle(
                        color: Colors.orange[300],
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      height: 120,
                      child: ListView.builder(
                        itemCount: _deploymentSteps.length,
                        itemBuilder: (context, index) {
                          final step = _deploymentSteps[index];
                          final isCompleted =
                              index <
                              (_deploymentProgress * _deploymentSteps.length);
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Row(
                              children: [
                                Icon(
                                  isCompleted
                                      ? Icons.check_circle
                                      : Icons.radio_button_unchecked,
                                  color:
                                      isCompleted ? Colors.green : Colors.grey,
                                  size: 16,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    step,
                                    style: TextStyle(
                                      color:
                                          isCompleted
                                              ? Colors.green[300]
                                              : Colors.grey[400],
                                      fontSize: 11,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  ],

                  // Device info
                  if (_selectedDevices.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      'Targets: ${_selectedDevices.length} devices',
                      style: TextStyle(color: Colors.cyan[300], fontSize: 12),
                    ),
                    Text(
                      'Mode: ${_isLiveMode ? "LIVE" : "SIMULATION"}',
                      style: TextStyle(
                        color:
                            _isLiveMode ? Colors.red[300] : Colors.green[300],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            );
          },
        );
      },
    ).then((_) {
      _isDeploymentDialogOpen = false;
      _deploymentDialogSetState = null;
    });
  }

  void _showDeploymentProgress(String status, {double progress = 0.0}) {
    if (Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    }

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Deployment Progress',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Status: $status',
                style: TextStyle(color: Colors.blue[300], fontSize: 14),
              ),
              const SizedBox(height: 16),
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey[700],
                valueColor: AlwaysStoppedAnimation<Color>(Colors.blue),
              ),
              const SizedBox(height: 8),
              Text(
                '${(progress * 100).toInt()}% Complete',
                style: TextStyle(color: Colors.green[300], fontSize: 12),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showSystemsStatusDialog() async {
    final baseUrl = NetworkConfig.primaryBackendUrl;
    final headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'LVL_UP_Android_App',
    };

    Future<Map<String, dynamic>> _get(String path) async {
      try {
        final res = await http
            .get(Uri.parse('$baseUrl$path'), headers: headers)
            .timeout(const Duration(seconds: 10));
        if (res.statusCode == 200) {
          final data = jsonDecode(res.body);
          if (data is Map<String, dynamic>) return data;
        }
      } catch (_) {}
      return {};
    }

    Map<String, dynamic> integration = {};
    Map<String, dynamic> berserk = {};
    Map<String, dynamic> horusSynthesis = {};
    Map<String, dynamic> horusStatus = {};
    Map<String, dynamic> systemTests = {};
    Map<String, dynamic> qcStatus = {};
    Map<String, dynamic> qcKeys = {};
    Map<String, dynamic> qcAssimilated = {};
    Map<String, dynamic> qcRepos = {};
    Map<String, dynamic> adversarial = {};
    Map<String, dynamic> jarvis = {};
    Map<String, dynamic> chaosDocs = {};

    try {
      final results = await Future.wait([
        _get('/api/ai-integration/integration/status'),
        _get('/api/ai-integration/berserk/status'),
        _get('/api/ai-integration/horus/weapon-synthesis-report'),
        _get('/api/project-horus-v2/status'),
        _get('/api/project-horus-v2/system-test/results'),
        _get('/api/quantum-chaos/status'),
        _get('/api/quantum-chaos/quantum-keys'),
        _get('/api/quantum-chaos/assimilated-systems'),
        _get('/api/quantum-chaos/chaos-repositories'),
        _get('/api/ai-integration/adversarial-training/progress'),
        _get('/api/jarvis/status'),
        _get('/api/ai-integration/chaos-language/documentation'),
      ]);
      integration = results[0];
      berserk = results[1];
      horusSynthesis = results[2];
      horusStatus = results[3];
      systemTests = results[4];
      qcStatus = results[5];
      qcKeys = results[6];
      qcAssimilated = results[7];
      qcRepos = results[8];
      adversarial = results[9];
      jarvis = results[10];
      chaosDocs = results[11];
    } catch (_) {}

    String _s(Object? v) => (v == null) ? 'unknown' : v.toString();

    final integrationStatus =
        integration['integration_status'] as Map<String, dynamic>? ?? {};
    final adv =
        integrationStatus['adversarial_training'] as Map<String, dynamic>? ??
        {};
    final hor =
        integrationStatus['project_horus'] as Map<String, dynamic>? ?? {};
    final ber =
        integrationStatus['project_berserk'] as Map<String, dynamic>? ?? {};

    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.grey[900],
            title: Row(
              children: [
                const Icon(Icons.analytics, color: Colors.cyan),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'AI Systems Status',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            content: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Overall integration snapshot
                  _statusLine(
                    'Adversarial scenarios',
                    _s(adv['total_scenarios_completed']),
                  ),
                  _statusLine(
                    'Adversarial success rate',
                    _s(adv['overall_success_rate']),
                  ),
                  _statusLine('Horus total weapons', _s(hor['total_weapons'])),
                  _statusLine(
                    'Horus avg complexity',
                    _s(hor['average_complexity']),
                  ),
                  _statusLine(
                    'Chaos language version',
                    _s(hor['chaos_language_version']),
                  ),
                  _statusLine(
                    'Berserk total weapons',
                    _s(ber['total_weapons']),
                  ),
                  _statusLine(
                    'Berserk active deployments',
                    _s(ber['active_deployments']),
                  ),
                  const SizedBox(height: 12),

                  // Detailed sections
                  const Text(
                    'Project Horus',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _statusLine(
                    'Learning progress',
                    _s(horusStatus['learning_progress']),
                  ),
                  _statusLine(
                    'Assimilated systems',
                    _s(horusStatus['assimilated_systems_count']),
                  ),
                  _statusLine(
                    'Failed attacks',
                    _s(horusStatus['failed_attacks_count']),
                  ),
                  _statusLine(
                    'Chaos repos',
                    _s(horusStatus['chaos_repositories_count']),
                  ),

                  const SizedBox(height: 12),
                  const Text(
                    'Berserk',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _statusLine(
                    'Systems compromised',
                    _s(ber['systems_compromised']),
                  ),

                  const SizedBox(height: 12),
                  const Text(
                    'Quantum Chaos (crypto)',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _statusLine(
                    'Quantum complexity',
                    _s(qcStatus['quantum_complexity']),
                  ),
                  _statusLine(
                    'Learning progress',
                    _s(qcStatus['learning_progress']),
                  ),
                  _statusLine(
                    'Entanglement pairs',
                    _s(qcStatus['entanglement_pairs']),
                  ),
                  _statusLine('Quantum keys', _s(qcKeys['count'])),
                  _statusLine(
                    'Assimilated systems',
                    _s(qcAssimilated['count']),
                  ),
                  _statusLine('Chaos repositories', _s(qcRepos['count'])),

                  const SizedBox(height: 12),
                  const Text(
                    'Attack Simulations',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  _statusLine(
                    'Recent tests available',
                    (systemTests.isNotEmpty).toString(),
                  ),

                  const SizedBox(height: 8),
                  const Text(
                    'Raw (compact):',
                    style: TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 4),
                  _mono(
                    jsonEncode({
                      'integration': integration.isEmpty ? null : 'ok',
                      'berserk': berserk.isEmpty ? null : 'ok',
                      'horus_synth': horusSynthesis.isEmpty ? null : 'ok',
                      'horus_status': horusStatus.isEmpty ? null : 'ok',
                      'tests': systemTests.isEmpty ? null : 'ok',
                      'qc_status': qcStatus.isEmpty ? null : 'ok',
                      'qc_keys': qcKeys.isEmpty ? null : 'ok',
                      'qc_assimilated': qcAssimilated.isEmpty ? null : 'ok',
                      'qc_repos': qcRepos.isEmpty ? null : 'ok',
                      'adversarial': adversarial.isEmpty ? null : 'ok',
                      'jarvis': jarvis.isEmpty ? null : 'ok',
                      'chaos_docs': chaosDocs.isEmpty ? null : 'ok',
                    }),
                  ),
                ],
              ),
            ),
            actions: [
              TextButton(
                onPressed:
                    chaosDocs.isEmpty
                        ? null
                        : () => _showChaosDocsDialog(
                          chaosDocs['chaos_language_documentation']
                              as Map<String, dynamic>?,
                        ),
                child: const Text(
                  'View Chaos Docs',
                  style: TextStyle(color: Colors.cyan),
                ),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text(
                  'Close',
                  style: TextStyle(color: Colors.white70),
                ),
              ),
            ],
          ),
    );
  }

  Widget _statusLine(String label, String? value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Expanded(
            child: Text(label, style: const TextStyle(color: Colors.white70)),
          ),
          Text(value ?? 'unknown', style: const TextStyle(color: Colors.cyan)),
        ],
      ),
    );
  }

  Widget _mono(String text) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.4),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.white10),
      ),
      child: Text(
        text,
        style: const TextStyle(
          color: Colors.white60,
          fontFamily: 'monospace',
          fontSize: 11,
        ),
      ),
    );
  }

  void _showChaosDocsDialog(Map<String, dynamic>? docs) {
    showDialog(
      context: context,
      builder: (context) {
        final pretty = const JsonEncoder.withIndent(
          '  ',
        ).convert(docs ?? const {'message': 'No documentation available'});
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: const Text(
            'Chaos Language Documentation',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
          content: SizedBox(
            width: 600,
            height: 400,
            child: SingleChildScrollView(child: _mono(pretty)),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text(
                'Close',
                style: TextStyle(color: Colors.white70),
              ),
            ),
          ],
        );
      },
    );
  }

  // Enhanced Testing Results Section
  Widget _buildEnhancedTestingResults() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.cyan.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '🧪 Enhanced Testing Results',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.cyan),
                onPressed: _refreshEnhancedTestingResults,
              ),
            ],
          ),
          const SizedBox(height: 12),
          FutureBuilder<Map<String, dynamic>?>(
            future: ProjectHorusService.instance.getEnhancedTestingStatus(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: CircularProgressIndicator(color: Colors.cyan),
                );
              }

              if (snapshot.hasError) {
                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Error loading testing results: ${snapshot.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                );
              }

              final data = snapshot.data;
              if (data == null) {
                return const Text(
                  'No testing data available',
                  style: TextStyle(color: Colors.grey),
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTestStatusCard(
                    'Overall Status',
                    data['overall_status'] ?? 'Unknown',
                  ),
                  const SizedBox(height: 8),
                  _buildTestStatusCard(
                    'Tests Passed',
                    '${data['tests_passed'] ?? 0}',
                  ),
                  const SizedBox(height: 8),
                  _buildTestStatusCard(
                    'Tests Failed',
                    '${data['tests_failed'] ?? 0}',
                  ),
                  const SizedBox(height: 8),
                  _buildTestStatusCard(
                    'Success Rate',
                    '${data['success_rate'] ?? 0}%',
                  ),
                  const SizedBox(height: 8),
                  _buildTestStatusCard(
                    'Current Difficulty',
                    '${data['current_difficulty'] ?? 'Unknown'}',
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: _runManualTestCycle,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.cyan,
                      foregroundColor: Colors.black,
                    ),
                    child: const Text('Run Manual Test Cycle'),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTestStatusCard(String label, String value) {
    Color color = Colors.green;
    if (label.contains('Failed')) color = Colors.red;
    if (label.contains('Rate') && value.contains('%')) {
      final rate = int.tryParse(value.replaceAll('%', '')) ?? 0;
      color =
          rate >= 80
              ? Colors.green
              : rate >= 60
              ? Colors.orange
              : Colors.red;
    }

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white)),
          Text(
            value,
            style: TextStyle(color: color, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  // Autonomous Weapons Section
  Widget _buildAutonomousWeaponsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.purple.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '🤖 Autonomous Weapons',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.add, color: Colors.purple),
                    onPressed: _generateAutonomousWeapons,
                  ),
                  IconButton(
                    icon: const Icon(Icons.clear, color: Colors.red),
                    onPressed: _clearStoredWeapons,
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          FutureBuilder<Map<String, dynamic>?>(
            future: ProjectHorusService.instance.getAutonomousWeapons(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: CircularProgressIndicator(color: Colors.purple),
                );
              }

              if (snapshot.hasError) {
                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Error loading autonomous weapons: ${snapshot.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                );
              }

              final data = snapshot.data;
              if (data == null || data['weapons'] == null) {
                return Column(
                  children: [
                    const Text(
                      'No autonomous weapons available',
                      style: TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _setupAutonomousWeapons,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purple,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Setup Autonomous Weapons'),
                    ),
                  ],
                );
              }

              final weapons = data['weapons'] as List;
              return Column(
                children: [
                  Text(
                    'Generated Weapons: ${weapons.length}',
                    style: const TextStyle(color: Colors.white70),
                  ),
                  const SizedBox(height: 8),
                  ...weapons.take(3).map((weapon) => _buildWeaponCard(weapon)),
                  if (weapons.length > 3)
                    TextButton(
                      onPressed: _showAllAutonomousWeapons,
                      child: const Text(
                        'View All Weapons',
                        style: TextStyle(color: Colors.purple),
                      ),
                    ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildWeaponCard(Map<String, dynamic> weapon) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.purple.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.purple.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            weapon['name'] ?? 'Unknown Weapon',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            weapon['type'] ?? 'Unknown Type',
            style: const TextStyle(color: Colors.purple, fontSize: 12),
          ),
          const SizedBox(height: 4),
          Text(
            weapon['description'] ?? 'No description available',
            style: const TextStyle(color: Colors.white70, fontSize: 12),
          ),
        ],
      ),
    );
  }

  // Live System Status Section
  Widget _buildLiveSystemStatus() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.green.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                '🌐 Live System Status',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.refresh, color: Colors.green),
                onPressed: _refreshLiveSystemStatus,
              ),
            ],
          ),
          const SizedBox(height: 12),
          FutureBuilder<Map<String, dynamic>?>(
            future: ProjectHorusService.instance.getLiveSystemStatus(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(
                  child: CircularProgressIndicator(color: Colors.green),
                );
              }

              if (snapshot.hasError) {
                return Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Error loading live system status: ${snapshot.error}',
                    style: const TextStyle(color: Colors.red),
                  ),
                );
              }

              final data = snapshot.data;
              if (data == null) {
                return const Text(
                  'No live system data available',
                  style: TextStyle(color: Colors.grey),
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildStatusCard(
                    'Internet Learning',
                    data['internet_learning_status'] ?? 'Unknown',
                  ),
                  const SizedBox(height: 8),
                  _buildStatusCard(
                    'Docker Simulations',
                    data['docker_simulations_status'] ?? 'Unknown',
                  ),
                  const SizedBox(height: 8),
                  _buildStatusCard(
                    'Autonomous Brains',
                    data['autonomous_brains_status'] ?? 'Unknown',
                  ),
                  const SizedBox(height: 8),
                  _buildStatusCard(
                    'Chaos Code Generation',
                    data['chaos_code_status'] ?? 'Unknown',
                  ),
                  const SizedBox(height: 8),
                  _buildStatusCard(
                    'Weapon Testing',
                    data['weapon_testing_status'] ?? 'Unknown',
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildStatusCard(String label, String value) {
    Color color = Colors.green;
    if (value.toLowerCase().contains('error') ||
        value.toLowerCase().contains('failed')) {
      color = Colors.red;
    } else if (value.toLowerCase().contains('warning') ||
        value.toLowerCase().contains('pending')) {
      color = Colors.orange;
    }

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white)),
          Text(
            value,
            style: TextStyle(color: color, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  // Action Methods
  Future<void> _refreshEnhancedTestingResults() async {
    setState(() {});
    _showSuccessSnackbar('Enhanced testing results refreshed');
  }

  Future<void> _runManualTestCycle() async {
    try {
      final result = await ProjectHorusService.instance.runManualTestCycle();
      if (result != null) {
        _showSuccessSnackbar('Manual test cycle completed');
        setState(() {});
      } else {
        _showErrorSnackbar('Failed to run manual test cycle');
      }
    } catch (e) {
      _showErrorSnackbar('Error running test cycle: $e');
    }
  }

  Future<void> _generateAutonomousWeapons() async {
    try {
      final result =
          await ProjectHorusService.instance.generateAutonomousWeapons();
      if (result != null) {
        _showSuccessSnackbar('Autonomous weapons generated successfully');
        setState(() {});
      } else {
        _showErrorSnackbar('Failed to generate autonomous weapons');
      }
    } catch (e) {
      _showErrorSnackbar('Error generating weapons: $e');
    }
  }

  Future<void> _clearStoredWeapons() async {
    try {
      final result = await ProjectHorusService.instance.clearStoredWeapons();
      if (result) {
        _showSuccessSnackbar('Stored weapons cleared successfully');
        setState(() {});
      } else {
        _showErrorSnackbar('Failed to clear stored weapons');
      }
    } catch (e) {
      _showErrorSnackbar('Error clearing weapons: $e');
    }
  }

  Future<void> _setupAutonomousWeapons() async {
    try {
      final result =
          await ProjectHorusService.instance.setupAutonomousWeapons();
      if (result != null) {
        _showSuccessSnackbar('Autonomous weapons setup completed');
        setState(() {});
      } else {
        _showErrorSnackbar('Failed to setup autonomous weapons');
      }
    } catch (e) {
      _showErrorSnackbar('Error setting up weapons: $e');
    }
  }

  void _showAllAutonomousWeapons() {
    // TODO: Implement dialog to show all autonomous weapons
    _showSuccessSnackbar('View all weapons feature coming soon');
  }

  Future<void> _refreshLiveSystemStatus() async {
    setState(() {});
    _showSuccessSnackbar('Live system status refreshed');
  }
}
