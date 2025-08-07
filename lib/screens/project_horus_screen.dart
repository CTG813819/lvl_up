import 'package:flutter/material.dart';
import 'dart:math';
import '../services/project_horus_service.dart';
import '../widgets/horus_brain_visualization.dart';
import '../widgets/chaos_code_stream_widget.dart';

/// Screen for Project Horus and Berserk control and visualization
class ProjectHorusScreen extends StatefulWidget {
  const ProjectHorusScreen({Key? key}) : super(key: key);

  @override
  State<ProjectHorusScreen> createState() => _ProjectHorusScreenState();
}

class _ProjectHorusScreenState extends State<ProjectHorusScreen> {
  bool _isLoading = false;
  Map<String, dynamic>? _lastHorusResponse;
  Map<String, dynamic>? _lastBerserkResponse;
  Map<String, bool> _connectivity = {};
  Set<String> _selectedDevices = {};

  @override
  void initState() {
    super.initState();
    _checkConnectivity();
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

  void _showSuccessSnackbar(String message) {
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
      // Show attack progress dialog
      _showAttackProgressDialog();

      // Step 1: Perform stealth assimilation
      final stealthResponse =
          await ProjectHorusService.instance.performStealthAssimilation();

      // Update progress
      _updateAttackProgress('Stealth Assimilation', stealthResponse != null);

      // Step 2: Perform data extraction
      final extractionResponse =
          await ProjectHorusService.instance.performDataExtraction();

      // Update progress
      _updateAttackProgress('Data Extraction', extractionResponse != null);

      // Step 3: Generate backdoor chaos code
      final backdoorResponse = await ProjectHorusService.instance
          .generateChaosCode(
            targetContext: 'Backdoor Access - ${_selectedDevices.join(', ')}',
          );

      // Update progress
      _updateAttackProgress('Backdoor Creation', backdoorResponse != null);

      // Close progress dialog
      Navigator.of(context).pop();

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
        // Close progress dialog if open
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
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: Colors.grey[900],
          title: Row(
            children: [
              Icon(Icons.security, color: Colors.red),
              const SizedBox(width: 8),
              Text(
                '$attackType Results',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          content: Column(
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
      await _executeDeploymentOption(deploymentOption);
    }
  }

  /// Execute the chosen deployment option
  Future<void> _executeDeploymentOption(String deploymentOption) async {
    if (mounted) setState(() => _isLoading = true);

    try {
      String attackDescription;
      Map<String, dynamic> response;

      switch (deploymentOption) {
        case 'data_extraction_only':
          attackDescription = 'Data Extraction (Stealth Mode)';
          response = await _performStealthDataExtraction();
          break;

        case 'data_extraction_with_synthetic':
          attackDescription = 'Data Extraction + Synthetic Code Deployment';
          response = await _performSyntheticCodeDeployment();
          break;

        case 'hybrid_ai_enhanced':
          attackDescription = 'Hybrid AI-Enhanced Attack';
          response = await _performHybridAIAttack();
          break;

        default:
          attackDescription = 'Unknown Deployment';
          response = {'success': false, 'message': 'Unknown deployment option'};
      }

      if (mounted) {
        setState(() {
          _lastHorusResponse = response;
          _isLoading = false;
        });
      }

      if (response['success'] == true) {
        _showSuccessSnackbar('$attackDescription completed successfully!');
        _showAttackResultsDialog(attackDescription, response);
      } else {
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
    // For hybrid attacks, automatically select best options based on AI learning
    final aiRecommendation = await ProjectHorusService.instance
        .getAIRecommendedStrategy(_selectedDevices.toList());

    _showSuccessSnackbar('AI analyzing targets for optimal strategy...');

    // Use AI-recommended chaos code and weapon
    if (aiRecommendation['recommended_chaos_code'] != null) {
      final chaosResult = ProjectHorusService.instance.executeChaosCodeOffline(
        aiRecommendation['recommended_chaos_code'],
        'hybrid_attack',
      );

      if (chaosResult['success'] == true) {
        _showSuccessSnackbar('AI-selected chaos code deployed!');
      }
    }

    if (aiRecommendation['recommended_weapon'] != null) {
      final weaponResult = ProjectHorusService.instance.executeWeaponOffline(
        aiRecommendation['recommended_weapon'],
        'hybrid_attack',
      );

      if (weaponResult['success'] == true) {
        _showSuccessSnackbar('AI-selected weapon deployed!');
      }
    }

    return await ProjectHorusService.instance.performHybridAIAttack();
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
}
