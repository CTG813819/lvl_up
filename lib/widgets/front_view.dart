import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:fast_noise/fast_noise.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:provider/provider.dart';
import '../widgets/animated_progress_bar.dart';
import '../providers/ai_customization_provider.dart';
import '../../services/network_config.dart';
import '../providers/ai_growth_analytics_provider.dart';

class Node {
  final String id;
  final String type;
  Offset? position;
  Offset? velocity; // Add velocity for neural network movement
  Offset? drift; // Add drift for continuous wandering
  Node(this.id, this.type, this.position)
    : velocity = Offset.zero,
      drift = Offset.zero;
}

class Edge {
  final Node from;
  final Node to;
  Edge(this.from, this.to);
}

// Widget that creates a reflection effect under a node
class NodeWithReflection extends StatelessWidget {
  final Widget node;
  final double reflectionOpacity;
  final double reflectionHeight;

  const NodeWithReflection({
    Key? key,
    required this.node,
    this.reflectionOpacity = 0.3,
    this.reflectionHeight = 0.5,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        node,
        Transform(
          alignment: Alignment.center,
          transform: Matrix4.rotationX(3.14159),
          child: Opacity(
            opacity: reflectionOpacity,
            child: ClipRect(
              child: Align(
                alignment: Alignment.topCenter,
                heightFactor: reflectionHeight,
                child: node,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class SpatialHypergraphView extends StatefulWidget {
  final bool isDarkMode;
  const SpatialHypergraphView({Key? key, required this.isDarkMode})
    : super(key: key);

  @override
  State<SpatialHypergraphView> createState() => _SpatialHypergraphViewState();
}

class _SpatialHypergraphViewState extends State<SpatialHypergraphView>
    with SingleTickerProviderStateMixin {
  final List<Node> nodes = [];
  final List<Edge> edges = [];
  late AnimationController _controller;
  WebSocketChannel? _channel;
  Random random = Random();
  bool _isLoading = true;
  String? _errorMessage;

  // Consistent AI color map
  final Map<String, Color> _aiColorMap = {};
  final List<Color> _colorPalette = [
    Colors.blueAccent,
    Colors.redAccent,
    Colors.greenAccent,
    Colors.amberAccent,
    Colors.purpleAccent,
    Colors.orangeAccent,
    Colors.tealAccent,
    Colors.pinkAccent,
    Colors.cyanAccent,
    Colors.limeAccent,
    Colors.indigoAccent,
    Colors.deepOrangeAccent,
    Colors.lightBlueAccent,
    Colors.deepPurpleAccent,
    Colors.yellowAccent,
  ];
  int _colorIndex = 0;

  // --- WebSocket fallback timer ---
  Timer? _wsDataTimeout;
  bool _receivedRealData = false;

  // For constant synapse firing
  List<_EdgeFiringState> _edgeFiringStates = [];
  bool _firingStatesInitialized = false;

  // Auto-refresh timer for live data
  Timer? _autoRefreshTimer;

  Map<String, double> _aiProgress = {}; // {aiName: progress 0.0-1.0}
  Map<String, ProgressBarAnimationStyle> _aiAnimationStyles = {};
  Color _defaultBarColor = Colors.deepPurple;

  // Add these helper functions at the top-level (outside the class) to match dashboard logic:
  List<num> _getLevelThresholdsList(String aiType) {
    final normalizedType = aiType.toLowerCase();
    return [
      0,
      2000,
      10000,
      20000,
      50000,
      100000,
      200000,
      500000,
      1000000,
      2000000,
      10000000, // New highest threshold
    ];
  }

  Map<String, num> _getLevelThresholds(double score, String aiType) {
    final thresholds = _getLevelThresholdsList(aiType);
    num current = thresholds[0];
    num next = thresholds.last;
    for (int i = 1; i < thresholds.length; i++) {
      if (score < thresholds[i]) {
        current = thresholds[i - 1];
        next = thresholds[i];
        break;
      }
    }
    return {'current': current, 'next': next};
  }

  // --- Add: Dynamic growth score calculation (copied from dashboard) ---
  double _calculateDynamicGrowthScore(double baseScore, String aiType) {
    final normalizedType = aiType.toLowerCase();
    final level = _getAgentLevelAndTitle(baseScore, aiType);
    double difficultyMultiplier = 1.0;
    if (normalizedType == 'conquest' || normalizedType == 'sandbox') {
      switch (level) {
        case 'Fabricator General':
          difficultyMultiplier = 10000.0;
          break;
        case 'Archmagos':
          difficultyMultiplier = 5000.0;
          break;
        case 'Tech Priest Dominus':
          difficultyMultiplier = 2500.0;
          break;
        case 'Magos':
          difficultyMultiplier = 1000.0;
          break;
        case 'Tech Priest (Engineer)':
        case 'Tech Priest (Cogitator)':
          difficultyMultiplier = 500.0;
          break;
        case 'Initiate/Apprentice':
          difficultyMultiplier = 250.0;
          break;
        case 'Skitarii':
          difficultyMultiplier = 100.0;
          break;
        case 'Servitor':
          difficultyMultiplier = 50.0;
          break;
        case 'Menial':
          difficultyMultiplier = 20.0;
          break;
        default:
          difficultyMultiplier = 10.0;
      }
    } else if (normalizedType == 'imperium' || normalizedType == 'guardian') {
      switch (level) {
        case 'Emperor':
        case 'Chapter Master':
          difficultyMultiplier = 10000.0;
          break;
        case 'Master of the Forge':
          difficultyMultiplier = 5000.0;
          break;
        case 'Librarian':
        case 'Techmarine':
          difficultyMultiplier = 2500.0;
          break;
        case 'Lieutenant':
          difficultyMultiplier = 1000.0;
          break;
        case 'Sergeant':
          difficultyMultiplier = 500.0;
          break;
        case 'Veteran':
          difficultyMultiplier = 250.0;
          break;
        case 'Battle Brother':
          difficultyMultiplier = 100.0;
          break;
        case 'Neophyte':
          difficultyMultiplier = 50.0;
          break;
        case 'Aspirant':
          difficultyMultiplier = 20.0;
          break;
        default:
          difficultyMultiplier = 10.0;
      }
    }
    return (baseScore / difficultyMultiplier).clamp(0.0, 100.0);
  }

  // Add a listener for SharedPreferences changes to update bars/graph immediately
  Timer? _settingsCheckTimer;

  // Helper to get emoji for each AI type (copied from ai_growth_analytics_dashboard.dart)
  String _getAIEmoji(String aiType) {
    switch (aiType.toLowerCase()) {
      case 'imperium':
        return '👑';
      case 'conquest':
        return '⚔️';
      case 'guardian':
        return '🛡️';
      case 'sandbox':
        return '🧪';
      default:
        return '🤖';
    }
  }

  // --- Add: Helper to get level name/title (copied from dashboard) ---
  String _getAgentLevelAndTitle(double learningScore, String aiType) {
    final normalizedType = aiType.toLowerCase();
    if (normalizedType == 'conquest') {
      if (learningScore >= 10000000) {
        return 'Overlord';
      } else if (learningScore >= 1000000) {
        return 'Fabricator General';
      } else if (learningScore >= 500000) {
        return 'Archmagos';
      } else if (learningScore >= 250000) {
        return 'Tech Priest Dominus';
      } else if (learningScore >= 100000) {
        return 'Magos';
      } else if (learningScore >= 50000) {
        return 'Tech Priest (Cogitator)';
      } else if (learningScore >= 25000) {
        return 'Initiate/Apprentice';
      } else if (learningScore >= 10000) {
        return 'Skitarii';
      } else if (learningScore >= 5000) {
        return 'Servitor';
      } else if (learningScore >= 1000) {
        return 'Menial';
      } else {
        return 'Cadet';
      }
    } else if (normalizedType == 'sandbox') {
      if (learningScore >= 10000000) {
        return 'Archmagos Prime';
      } else if (learningScore >= 1000000) {
        return 'Fabricator General';
      } else if (learningScore >= 500000) {
        return 'Archmagos';
      } else if (learningScore >= 250000) {
        return 'Tech Priest Dominus';
      } else if (learningScore >= 100000) {
        return 'Magos';
      } else if (learningScore >= 50000) {
        return 'Tech Priest (Cogitator)';
      } else if (learningScore >= 25000) {
        return 'Initiate/Apprentice';
      } else if (learningScore >= 10000) {
        return 'Skitarii';
      } else if (learningScore >= 5000) {
        return 'Servitor';
      } else if (learningScore >= 1000) {
        return 'Menial';
      } else {
        return 'Cadet';
      }
    } else if (normalizedType == 'guardian') {
      if (learningScore >= 10000000) {
        return 'Supreme Grandmaster';
      } else if (learningScore >= 1000000) {
        return 'Chapter Master';
      } else if (learningScore >= 500000) {
        return 'Master of the Forge';
      } else if (learningScore >= 250000) {
        return 'Techmarine';
      } else if (learningScore >= 100000) {
        return 'Lieutenant';
      } else if (learningScore >= 50000) {
        return 'Sergeant';
      } else if (learningScore >= 25000) {
        return 'Veteran';
      } else if (learningScore >= 10000) {
        return 'Battle Brother';
      } else if (learningScore >= 5000) {
        return 'Neophyte';
      } else if (learningScore >= 1000) {
        return 'Aspirant';
      } else {
        return 'Recruit';
      }
    } else if (normalizedType == 'imperium') {
      if (learningScore >= 10000000) {
        return 'Emperor';
      } else if (learningScore >= 1000000) {
        return 'Emperor';
      } else if (learningScore >= 500000) {
        return 'Master of the Forge';
      } else if (learningScore >= 250000) {
        return 'Librarian';
      } else if (learningScore >= 100000) {
        return 'Lieutenant';
      } else if (learningScore >= 50000) {
        return 'Sergeant';
      } else if (learningScore >= 25000) {
        return 'Veteran';
      } else if (learningScore >= 10000) {
        return 'Battle Brother';
      } else if (learningScore >= 5000) {
        return 'Neophyte';
      } else if (learningScore >= 1000) {
        return 'Aspirant';
      } else {
        return 'Recruit';
      }
    }
    return 'Cadet';
  }

  @override
  void initState() {
    super.initState();
    _controller =
        AnimationController(
            vsync: this,
            duration: Duration(
              seconds: 3,
            ), // Slower animation for smoother movement
          )
          ..addListener(_onTick)
          ..repeat();

    // Load existing graph state first
    _loadGraphState();

    // --- Always load saved progress before backend fetch for persistence ---
    _loadSavedProgressBars();

    connectWebSocket();
    _edgeFiringStates = [];

    // Start auto-refresh timer for live data
    _autoRefreshTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      if (mounted && !_isLoading) {
        fetchGraphData();
      }
    });

    // Start analytics refresh timer
    Timer.periodic(const Duration(seconds: 10), (_) {
      if (mounted) {
        final analyticsProvider = Provider.of<AIGrowthAnalyticsProvider>(
          context,
          listen: false,
        );
        analyticsProvider.refresh();
      }
    });
    // --- Ensure provider customizations are loaded for persistent color ---
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final aiCustomization = Provider.of<AICustomizationProvider>(
        context,
        listen: false,
      );
      // This will reload customizations from SharedPreferences
      aiCustomization.notifyListeners();
    });
    _loadAIBarSettings();
    // Listen for SharedPreferences changes (simulate with periodic check)
    _settingsCheckTimer = Timer.periodic(const Duration(seconds: 2), (_) async {
      await _loadAIBarSettings();
      setState(() {}); // Force rebuild if settings changed
    });

    // --- Ensure analytics provider is initialized ---
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final analyticsProvider = Provider.of<AIGrowthAnalyticsProvider>(
        context,
        listen: false,
      );
      analyticsProvider.initialize();

      // Force a refresh to ensure data is loaded
      analyticsProvider.refresh();
    });
  }

  void _onTick() {
    setState(() {}); // Trigger repaint for continuous movement
  }

  void _updateNodeDrift() {}
  void _applyForceDirectedLayout() {}

  @override
  void dispose() {
    _controller.dispose();
    _channel?.sink.close();
    _wsDataTimeout?.cancel();
    _autoRefreshTimer?.cancel(); // Dispose the auto-refresh timer
    _settingsCheckTimer?.cancel();
    super.dispose();
  }

  void connectWebSocket() {
    // WebSocket endpoints are not working on the server, so skip WebSocket connection
    // and go directly to HTTP fallback
    print(
      '[FRONT_VIEW] WebSocket endpoints not available, using HTTP fallback',
    );
    fetchGraphData();
  }

  Future<void> fetchGraphData() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
          _errorMessage = null;
        });
      }

      print('[FRONT_VIEW] Fetching graph data from working endpoints...');

      // Try multiple working endpoints to get rich data
      List<dynamic> allData = [];

      // Get agents data from working endpoint
      try {
        final agentsResponse = await http.get(
          Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/agents'),
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'LVL_UP_Flutter_App',
          },
        );
        if (agentsResponse.statusCode == 200) {
          final agentsData = json.decode(agentsResponse.body);
          if (agentsData is Map && agentsData.containsKey('agents')) {
            allData.addAll(agentsData['agents'].values);
            print(
              '[FRONT_VIEW] ✅ Loaded ${agentsData['agents'].length} agents',
            );
          }
        }
      } catch (e) {
        print('[FRONT_VIEW] Error fetching agents: $e');
      }

      // Get trusted sources data
      try {
        final sourcesResponse = await http.get(
          Uri.parse('${NetworkConfig.apiBaseUrl}/api/imperium/trusted-sources'),
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'LVL_UP_Flutter_App',
          },
        );
        if (sourcesResponse.statusCode == 200) {
          final sourcesData = json.decode(sourcesResponse.body);
          if (sourcesData is Map &&
              sourcesData.containsKey('trusted_sources')) {
            for (var source in sourcesData['trusted_sources']) {
              allData.add({
                'agent_id': 'trusted_source',
                'agent_type': 'source',
                'topic': source,
                'learning_score': 85.0,
              });
            }
            print(
              '[FRONT_VIEW] ✅ Loaded ${sourcesData['trusted_sources'].length} trusted sources',
            );
          }
        }
      } catch (e) {
        print('[FRONT_VIEW] Error fetching trusted sources: $e');
      }

      // Get learning topics data from working endpoint
      try {
        final topicsResponse = await http.get(
          Uri.parse(
            '${NetworkConfig.apiBaseUrl}/api/imperium/internet-learning/topics',
          ),
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'LVL_UP_Flutter_App',
          },
        );
        if (topicsResponse.statusCode == 200) {
          final topicsData = json.decode(topicsResponse.body);
          if (topicsData is Map && topicsData.containsKey('topics')) {
            for (var agent in topicsData['topics'].keys) {
              for (var topic in topicsData['topics'][agent]) {
                allData.add({
                  'agent_id': agent,
                  'agent_type': agent,
                  'topic': topic,
                  'learning_score': 80.0,
                });
              }
            }
            print(
              '[FRONT_VIEW] ✅ Loaded learning topics for ${topicsData['topics'].length} agents',
            );
          }
        }
      } catch (e) {
        print('[FRONT_VIEW] Error fetching learning topics: $e');
      }

      // If we have data, use it; otherwise show waiting/error state
      if (allData.isNotEmpty) {
        print('[FRONT_VIEW] Building graph with ${allData.length} data points');
        buildGraphFromData(allData);

        // Extract AI progress for bars
        final Map<String, double> progressMap = {};
        for (var item in allData) {
          if (item is Map &&
              item.containsKey('agent_id') &&
              item.containsKey('learning_score')) {
            final ai = item['agent_id'].toString();
            final score = (item['learning_score'] as num?)?.toDouble() ?? 0.0;
            progressMap[ai] = (score / 100.0).clamp(0.0, 1.0);
          }
        }

        // Merge new progress with saved progress
        final mergedProgress = await _mergeWithSavedProgress(progressMap);
        setState(() {
          _aiProgress = mergedProgress;
        });

        // Save progress bars after update
        await _saveProgressBars();
        await _loadAIBarSettings();
      } else {
        // Show waiting or error state if no real data is available
        print('[FRONT_VIEW] No data from endpoints, waiting for backend data');
        setState(() {
          _errorMessage = 'Waiting for backend data...';
          _isLoading = false;
        });
      }
    } catch (e) {
      print('[FRONT_VIEW] Error fetching graph data: $e');
      if (mounted) {
        setState(() {
          _errorMessage = 'Error loading graph data: $e';
          _isLoading = false;
        });
      }
    }
  }

  // --- Update: Merge backend progress with last synced backend value ---
  Future<Map<String, double>> _mergeWithSavedProgress(
    Map<String, double> backend,
  ) async {
    final prefs = await SharedPreferences.getInstance();
    final str = prefs.getString('front_view_progress_bars');
    final lastSyncedStr = prefs.getString('front_view_last_synced_backend');
    Map<String, double> local = {};
    Map<String, double> lastSynced = {};
    if (str != null) {
      final saved = jsonDecode(str) as Map<String, dynamic>;
      local = saved.map((k, v) => MapEntry(k, (v as num).toDouble()));
    }
    if (lastSyncedStr != null) {
      final saved = jsonDecode(lastSyncedStr) as Map<String, dynamic>;
      lastSynced = saved.map((k, v) => MapEntry(k, (v as num).toDouble()));
    }
    final merged = <String, double>{};
    final newLastSynced = Map<String, double>.from(lastSynced);
    for (final k in backend.keys) {
      final localVal = local[k] ?? 0.0;
      final backendVal = backend[k]!;
      final lastSyncedVal = lastSynced[k] ?? 0.0;
      // Only update if backend > last synced value
      if (backendVal > lastSyncedVal) {
        merged[k] = backendVal > localVal ? backendVal : localVal;
        newLastSynced[k] = backendVal;
      } else {
        merged[k] = localVal;
        newLastSynced[k] = lastSyncedVal;
      }
    }
    // Keep any local-only keys
    for (final k in local.keys) {
      if (!merged.containsKey(k)) merged[k] = local[k]!;
    }
    // Save new last synced backend values
    await prefs.setString(
      'front_view_last_synced_backend',
      jsonEncode(newLastSynced),
    );
    return merged;
  }

  // --- SPATIAL GRAPH: Prevent node re-spacing on refresh ---
  void buildGraphFromData(dynamic data) {
    print('[FRONT_VIEW] Raw data received: $data');
    if (mounted) {
      setState(() {
        // Do NOT clear nodes/edges; preserve positions
        // Only add new nodes/edges if they do not exist
        final Map<String, Node> nodeMap = {for (var n in nodes) n.id: n};
        final Set<String> edgeSet = {
          for (var e in edges) '${e.from.id}->${e.to.id}',
        };
        final size = MediaQuery.of(context).size;
        final double margin = 0.1;
        final double width = size.width * (1 - 2 * margin);
        final double height = size.height * (1 - 2 * margin);
        final Offset center = Offset(size.width / 2, size.height / 2);
        Offset randomPosition() {
          // Use different distribution patterns to avoid clustering
          final double pattern = random.nextDouble();
          double x, y;
          if (pattern < 0.25) {
            x = margin * size.width + random.nextDouble() * (width / 2);
            y = margin * size.height + random.nextDouble() * (height / 2);
          } else if (pattern < 0.5) {
            x = center.dx + random.nextDouble() * (width / 2);
            y = margin * size.height + random.nextDouble() * (height / 2);
          } else if (pattern < 0.75) {
            x = margin * size.width + random.nextDouble() * (width / 2);
            y = center.dy + random.nextDouble() * (height / 2);
          } else {
            x = center.dx + random.nextDouble() * (width / 2);
            y = center.dy + random.nextDouble() * (height / 2);
          }
          return Offset(
            x.clamp(margin * size.width, (1 - margin) * size.width),
            y.clamp(margin * size.height, (1 - margin) * size.height),
          );
        }

        // Initialize firing states once if not already done
        if (!_firingStatesInitialized) {
          _edgeFiringStates = List.generate(100, (i) {
            // Pre-generate enough states
            return _EdgeFiringState(
              phase: (random.nextDouble() ?? 0.0),
              direction: ((random.nextBool() ? 1.0 : -1.0) ?? 1.0),
              speed: ((0.5 + random.nextDouble() * 1.0) ?? 1.0),
            );
          });
          _firingStatesInitialized = true;
        }
        // Handle both List and Map responses
        List<dynamic> dataList;
        if (data is List) {
          dataList = data;
        } else if (data is Map) {
          if (data.containsKey('data')) {
            dataList = data['data'] is List ? data['data'] : [];
          } else if (data.containsKey('items')) {
            dataList = data['items'] is List ? data['items'] : [];
          } else if (data.containsKey('results')) {
            dataList = data['results'] is List ? data['results'] : [];
          } else {
            dataList = [data];
          }
        } else {
          dataList = [];
        }
        print('[FRONT_VIEW] Data list length: ${dataList.length}');
        List<Edge> newEdges = [];
        for (var item in dataList) {
          if (item is Map) {
            final agent = item['agent_id'] ?? item['agent'] ?? 'Unknown';
            final topic = item['topic'] ?? item['subject'] ?? 'General';
            final type =
                (item['agent_type'] ?? item['type'] ?? '')
                    .toString()
                    .toLowerCase();
            if (!_aiColorMap.containsKey(agent)) {
              _aiColorMap[agent] =
                  _colorPalette[_colorIndex % _colorPalette.length];
              _colorIndex++;
            }
            if (_aiColorMap[agent] == null) {
              _aiColorMap[agent] =
                  _colorPalette[_colorIndex % _colorPalette.length];
              _colorIndex++;
            }
            // Only create node if it doesn't exist
            if (!nodeMap.containsKey(agent)) {
              nodeMap[agent] = Node(agent, type, randomPosition());
            }
            if (!nodeMap.containsKey(topic)) {
              nodeMap[topic] = Node(topic, 'topic', randomPosition());
            }
            final edgeKey = '${agent}->${topic}';
            if (!edgeSet.contains(edgeKey)) {
              newEdges.add(Edge(nodeMap[agent]!, nodeMap[topic]!));
              edgeSet.add(edgeKey);
            }
          }
        }
        // After node/edge creation, ensure all agent nodes have a color
        for (var node in nodeMap.values) {
          if (!_aiColorMap.containsKey(node.id)) {
            _aiColorMap[node.id] =
                _colorPalette[_colorIndex % _colorPalette.length];
            _colorIndex++;
          }
        }
        // ACCUMULATE nodes and edges instead of clearing
        // This prevents lines from disappearing
        final existingNodeIds = {for (var n in nodes) n.id};
        final existingEdgeKeys = {
          for (var e in edges) '${e.from.id}->${e.to.id}',
        };
        // Add only new nodes
        for (var node in nodeMap.values) {
          if (!existingNodeIds.contains(node.id)) {
            nodes.add(node);
          }
        }
        // Add only new edges
        for (var edge in newEdges) {
          final edgeKey = '${edge.from.id}->${edge.to.id}';
          if (!existingEdgeKeys.contains(edgeKey)) {
            edges.add(edge);
          }
        }
        // Save the updated graph state
        _saveGraphState();
        _isLoading = false;
        _errorMessage = null;
      });
    }
    print('[FRONT_VIEW] Nodes after build: ${nodes.length}');
    print('[FRONT_VIEW] Edges after build: ${edges.length}');
  }

  // Save graph state to SharedPreferences
  Future<void> _saveGraphState() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Save nodes
      final nodeData =
          nodes
              .map(
                (node) => {
                  'id': node.id,
                  'type': node.type,
                  'position': {
                    'dx': node.position?.dx ?? 0.0,
                    'dy': node.position?.dy ?? 0.0,
                  },
                },
              )
              .toList();

      // Save edges
      final edgeData =
          edges
              .map((edge) => {'from': edge.from.id, 'to': edge.to.id})
              .toList();

      // Save color map
      final colorData = _aiColorMap.map(
        (key, value) => MapEntry(key, value.value),
      );

      await prefs.setString('graph_nodes', jsonEncode(nodeData));
      await prefs.setString('graph_edges', jsonEncode(edgeData));
      await prefs.setString('graph_colors', jsonEncode(colorData));
      await prefs.setInt('graph_color_index', _colorIndex);

      print(
        '[FRONT_VIEW] Graph state saved: ${nodes.length} nodes, ${edges.length} edges',
      );
    } catch (e) {
      print('[FRONT_VIEW] Error saving graph state: $e');
    }
  }

  // Load graph state from SharedPreferences
  Future<void> _loadGraphState() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Load nodes
      final nodeDataString = prefs.getString('graph_nodes');
      if (nodeDataString != null) {
        final nodeData = jsonDecode(nodeDataString) as List;
        for (final nodeJson in nodeData) {
          final node = Node(
            nodeJson['id'],
            nodeJson['type'],
            Offset(
              nodeJson['position']['dx'].toDouble(),
              nodeJson['position']['dy'].toDouble(),
            ),
          );
          nodes.add(node);
        }
      }

      // Load edges
      final edgeDataString = prefs.getString('graph_edges');
      if (edgeDataString != null) {
        final edgeData = jsonDecode(edgeDataString) as List;
        for (final edgeJson in edgeData) {
          final fromNode = nodes.firstWhere(
            (node) => node.id == edgeJson['from'],
            orElse: () => Node(edgeJson['from'], 'unknown', Offset.zero),
          );
          final toNode = nodes.firstWhere(
            (node) => node.id == edgeJson['to'],
            orElse: () => Node(edgeJson['to'], 'unknown', Offset.zero),
          );
          edges.add(Edge(fromNode, toNode));
        }
      }

      // Load color map
      final colorDataString = prefs.getString('graph_colors');
      if (colorDataString != null) {
        final colorData = jsonDecode(colorDataString) as Map<String, dynamic>;
        for (final entry in colorData.entries) {
          _aiColorMap[entry.key] = Color(entry.value);
        }
      }

      // Load color index
      _colorIndex = prefs.getInt('graph_color_index') ?? 0;

      print(
        '[FRONT_VIEW] Graph state loaded: ${nodes.length} nodes, ${edges.length} edges',
      );
    } catch (e) {
      print('[FRONT_VIEW] Error loading graph state: $e');
    }
  }

  Future<void> _loadAIBarSettings() async {
    final prefs = await SharedPreferences.getInstance();
    // Load all AI animation styles and bar color
    setState(() {
      _aiAnimationStyles.clear();
      _defaultBarColor =
          prefs.getInt('selectedBarColor') != null
              ? Color(prefs.getInt('selectedBarColor')!)
              : Colors.deepPurple;
      for (final ai in _aiProgress.keys) {
        final styleIndex = prefs.getInt('ai_animation_style_$ai');
        if (styleIndex != null) {
          _aiAnimationStyles[ai] = ProgressBarAnimationStyle.values[styleIndex];
        } else {
          _aiAnimationStyles[ai] = ProgressBarAnimationStyle.waves;
        }
      }
    });
  }

  // Utility: Save progress bars to SharedPreferences
  Future<void> _saveProgressBars() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        'front_view_progress_bars',
        jsonEncode(_aiProgress),
      );
    } catch (e) {
      print('Error saving progress bars: $e');
    }
  }

  // Utility: Load progress bars from SharedPreferences
  Future<void> _loadSavedProgressBars() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString('front_view_progress_bars');
      if (str != null) {
        final saved = jsonDecode(str) as Map<String, dynamic>;
        setState(() {
          _aiProgress = saved.map((k, v) => MapEntry(k, (v as num).toDouble()));
        });
      }
    } catch (e) {
      print('Error loading saved progress bars: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final bgColor = widget.isDarkMode ? Colors.black : Colors.white;
    final edgeColor = widget.isDarkMode ? Colors.blueAccent : Colors.deepPurple;
    final nodeColor = widget.isDarkMode ? Colors.blueAccent : Colors.deepPurple;
    final aiCustomization = Provider.of<AICustomizationProvider>(
      context,
      listen: false,
    );

    // Filter out 'trusted_source' from AI progress bars
    final aiProgressEntries =
        _aiProgress.entries
            .where((entry) => entry.key != 'trusted_source')
            .toList();

    return Scaffold(
      backgroundColor: bgColor,
      body: Column(
        children: [
          // Graph visualization (top)
          Expanded(
            flex: 3,
            child: Padding(
              padding: const EdgeInsets.only(top: 16.0, left: 8, right: 8),
              child: Stack(
                children: [
                  // Always show the graph, even when loading
                  AnimatedBuilder(
                    animation: _controller,
                    builder: (context, child) {
                      return CustomPaint(
                        size: MediaQuery.of(context).size,
                        painter: _HypergraphPainter(
                          nodes: nodes,
                          edges: edges,
                          animationValue: _controller.value,
                          edgeColor: edgeColor,
                          nodeColor: nodeColor,
                          aiColorMap: _aiColorMap,
                          edgeFiringStates: _edgeFiringStates,
                          context: context, // Pass context to painter
                        ),
                      );
                    },
                  ),
                  if (_errorMessage != null)
                    Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.error_outline,
                            color: Colors.red,
                            size: 48,
                          ),
                          SizedBox(height: 16),
                          Text(
                            _errorMessage!,
                            style: TextStyle(color: Colors.red),
                            textAlign: TextAlign.center,
                          ),
                          SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: fetchGraphData,
                            child: Text('Retry'),
                          ),
                        ],
                      ),
                    )
                  else if (nodes.isEmpty)
                    Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.account_tree,
                            color:
                                widget.isDarkMode
                                    ? Colors.white70
                                    : Colors.black54,
                            size: 48,
                          ),
                          SizedBox(height: 16),
                          Text(
                            'No graph data available',
                            style: TextStyle(
                              color:
                                  widget.isDarkMode
                                      ? Colors.white70
                                      : Colors.black54,
                            ),
                          ),
                        ],
                      ),
                    )
                  else
                    AnimatedBuilder(
                      animation: _controller,
                      builder: (context, child) {
                        return CustomPaint(
                          size: MediaQuery.of(context).size,
                          painter: _HypergraphPainter(
                            nodes: nodes,
                            edges: edges,
                            animationValue: _controller.value,
                            edgeColor: edgeColor,
                            nodeColor: nodeColor,
                            aiColorMap: _aiColorMap,
                            edgeFiringStates: _edgeFiringStates,
                            context: context, // Pass context to painter
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
          ),
          // Animated Progress Bars (bottom, 2 columns)
          Consumer2<AIGrowthAnalyticsProvider, AICustomizationProvider>(
            builder: (context, analytics, aiCustomization, _) {
              final aiTypes = ['Imperium', 'Guardian', 'Sandbox', 'Conquest'];
              final aiProgressEntries =
                  aiTypes.map((ai) {
                    // Use the analytics provider's level progress (0-100 per level)
                    final double levelProgress =
                        analytics.getLevelProgressForAI(ai) /
                        100.0; // Convert to 0.0-1.0
                    final double growthScore =
                        analytics.getGrowthScoreForAI(ai) ?? 0.0;

                    // Always use provider's getColorForAI for persistent color
                    final Color color = aiCustomization.getColorForAI(ai);
                    final ProgressBarAnimationStyle style =
                        _aiAnimationStyles[ai.toLowerCase()] ??
                        ProgressBarAnimationStyle.waves;
                    final String emoji = _getAIEmoji(ai);
                    final String displayName =
                        ai[0].toUpperCase() + ai.substring(1);
                    final String levelName = _getAgentLevelAndTitle(
                      growthScore,
                      ai,
                    );
                    final int aiLevel = analytics.getAILevel(ai);
                    return {
                      'ai': displayName,
                      'growthScore': growthScore,
                      'levelProgress': levelProgress,
                      'color': color,
                      'style': style,
                      'emoji': emoji,
                      'levelName': levelName,
                      'aiLevel': aiLevel,
                    };
                  }).toList();

              return Padding(
                padding: const EdgeInsets.symmetric(
                  vertical: 16.0,
                  horizontal: 12.0,
                ),
                child: GridView.builder(
                  shrinkWrap: true,
                  physics: NeverScrollableScrollPhysics(),
                  itemCount: aiProgressEntries.length,
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    mainAxisSpacing: 16,
                    crossAxisSpacing: 16,
                    childAspectRatio: 2.8,
                  ),
                  itemBuilder: (context, index) {
                    final entry = aiProgressEntries[index];
                    final String ai = entry['ai'] as String;
                    final double growthScore = entry['growthScore'] as double;
                    final double levelProgress =
                        entry['levelProgress'] as double;
                    final Color color = entry['color'] as Color;
                    final ProgressBarAnimationStyle style =
                        entry['style'] as ProgressBarAnimationStyle;
                    final String emoji = entry['emoji'] as String;
                    final String levelName = entry['levelName'] as String;
                    final int aiLevel = entry['aiLevel'] as int;
                    return Card(
                      color: Colors.black.withOpacity(0.7),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          alignment: Alignment.centerLeft,
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(emoji, style: TextStyle(fontSize: 24)),
                              SizedBox(width: 6),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    ai + '  |  ' + levelName,
                                    style: TextStyle(
                                      color: color,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                    ),
                                  ),
                                  SizedBox(
                                    width: 130,
                                    height: 16,
                                    child: LayoutBuilder(
                                      builder: (context, constraints) {
                                        return AnimatedProgressBar(
                                          progress: levelProgress,
                                          color: color,
                                          style: style,
                                          height: 16,
                                          width: constraints.maxWidth,
                                          showPercent: true,
                                        );
                                      },
                                    ),
                                  ),
                                  Row(
                                    children: [
                                      Text(
                                        'Lvl: $aiLevel',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.white,
                                          fontWeight: FontWeight.w600,
                                          shadows: [
                                            Shadow(
                                              blurRadius: 2,
                                              color: Colors.black26,
                                            ),
                                          ],
                                        ),
                                      ),
                                      SizedBox(width: 8),
                                      Text(
                                        'Progress: ${(levelProgress * 100).toStringAsFixed(0)}%',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.greenAccent,
                                          fontWeight: FontWeight.w600,
                                          shadows: [
                                            Shadow(
                                              blurRadius: 2,
                                              color: Colors.black26,
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

class _EdgeFiringState {
  final double phase; // 0.0 to 1.0
  final double direction; // 1.0 or -1.0
  final double speed; // Speed multiplier for firing
  _EdgeFiringState({
    required this.phase,
    required this.direction,
    required this.speed,
  });
}

class _HypergraphPainter extends CustomPainter {
  final List<Node> nodes;
  final List<Edge> edges;
  final double animationValue;
  final Color edgeColor;
  final Color nodeColor;
  final Map<String, Color> aiColorMap;
  final List<_EdgeFiringState> edgeFiringStates;
  final BuildContext context; // Add context parameter

  _HypergraphPainter({
    required this.nodes,
    required this.edges,
    required this.animationValue,
    required this.edgeColor,
    required this.nodeColor,
    required this.aiColorMap,
    required this.edgeFiringStates,
    required this.context, // Add context parameter
  });

  Color getNodeColor(String id, String type) {
    if (type == 'topic') return Colors.grey;
    if (aiColorMap.containsKey(id) && aiColorMap[id] != null)
      return aiColorMap[id]!;
    switch (type) {
      case 'imperium':
        return Colors.amberAccent;
      case 'guardian':
        return Colors.blueAccent;
      case 'sandbox':
        return Colors.greenAccent;
      case 'conquest':
        return Colors.redAccent;
      default:
        return Colors.grey;
    }
  }

  Offset _getNeuralPosition(Node node, double animationValue) {
    // Use a monotonically increasing time for continuous, non-looping movement
    final double time = DateTime.now().millisecondsSinceEpoch / 1000.0;
    final int hash = node.id.hashCode;
    final double baseX = (node.position?.dx ?? 0.0); // REMOVE drift
    final double baseY = (node.position?.dy ?? 0.0); // REMOVE drift

    // Per-node unique parameters with better distribution
    final double amplitude =
        40.0 + (hash % 25); // Increased amplitude for more movement
    final double freq1 = 0.8 + ((hash % 5) / 10.0);
    final double freq2 = 1.5 + ((hash % 8) / 10.0);

    final perlin = PerlinNoise(seed: 1337 + hash);

    // Layered Perlin noise for richer movement
    final double noiseX = perlin.getNoise2(hash.toDouble(), time * freq1);
    final double noiseY = perlin.getNoise2(
      hash.toDouble() + 1000,
      time * freq1,
    );
    final double noiseX2 = perlin.getNoise2(
      hash.toDouble() + 2000,
      time * freq2,
    );
    final double noiseY2 = perlin.getNoise2(
      hash.toDouble() + 3000,
      time * freq2,
    );

    // Add a gentle orbit for wandering
    final double orbitRadius = 20.0 + (hash % 12); // Larger orbit radius
    final double orbitSpeed =
        0.08 + ((hash % 3) / 80.0); // Slightly faster orbit
    final double angle = time * orbitSpeed + (hash % 360);

    final double orbitX = cos(angle) * orbitRadius;
    final double orbitY = sin(angle) * orbitRadius;

    final double finalX =
        baseX + noiseX * amplitude + noiseX2 * (amplitude / 2) + orbitX;
    final double finalY =
        baseY + noiseY * amplitude + noiseY2 * (amplitude / 2) + orbitY;

    // Constrain to screen bounds with better margins
    final size = MediaQuery.of(context).size;
    final double margin = 0.1; // Reduced margin for more space

    return Offset(
      finalX.clamp(margin * size.width, (1 - margin) * size.width),
      finalY.clamp(margin * size.height, (1 - margin) * size.height),
    );
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Draw edges with the color of the source node
    for (final edge in edges) {
      final fromPos = _getNeuralPosition(edge.from, animationValue);
      final toPos = _getNeuralPosition(edge.to, animationValue);
      final Paint coloredEdgePaint =
          Paint()
            ..color = getNodeColor(
              edge.from.id,
              edge.from.type,
            ).withOpacity(0.85)
            ..strokeWidth = 1.1;
      canvas.drawLine(fromPos, toPos, coloredEdgePaint);
    }
    // Synapse firing effect: animate a glowing dot along each edge
    for (int i = 0; i < edges.length; i++) {
      final edge = edges[i];
      final firing =
          (edgeFiringStates.length > i)
              ? edgeFiringStates[i]
              : _EdgeFiringState(phase: 0.0, direction: 1.0, speed: 1.0);
      // Each edge has its own random phase and direction with speed
      final double time = DateTime.now().millisecondsSinceEpoch / 1000.0;
      double t = ((time * (firing.speed ?? 1.0)) + (firing.phase ?? 0.0)) % 1.0;
      if ((firing.direction ?? 1.0) < 0) t = 1.0 - t;

      // Apply neural network movement to node positions
      final Offset from = _getNeuralPosition(edge.from, animationValue ?? 0.0);
      final Offset to = _getNeuralPosition(edge.to, animationValue ?? 0.0);

      final Offset dotPos = Offset(
        (from.dx ?? 0.0) + ((to.dx ?? 0.0) - (from.dx ?? 0.0)) * t,
        (from.dy ?? 0.0) + ((to.dy ?? 0.0) - (from.dy ?? 0.0)) * t,
      );
      final Paint dotPaint =
          Paint()
            ..color = Color.fromARGB(220, 180, 220, 255)
            ..maskFilter = MaskFilter.blur(BlurStyle.normal, 4);
      canvas.drawCircle(dotPos, 4, dotPaint);

      // Add a trailing effect for more neural network feel
      final Paint trailPaint =
          Paint()
            ..color = Color.fromARGB(100, 180, 220, 255)
            ..maskFilter = MaskFilter.blur(BlurStyle.normal, 2);
      final Offset trailPos = Offset(
        (from.dx ?? 0.0) +
            ((to.dx ?? 0.0) - (from.dx ?? 0.0)) * (t - 0.1).clamp(0.0, 1.0),
        (from.dy ?? 0.0) +
            ((to.dy ?? 0.0) - (from.dy ?? 0.0)) * (t - 0.1).clamp(0.0, 1.0),
      );
      canvas.drawCircle(trailPos, 2, trailPaint);
    }
    // Draw nodes with neural network movement and reflection effects
    for (final node in nodes) {
      final neuralPos = _getNeuralPosition(node, animationValue);

      // Draw reflection first (below the main node)
      final reflectionPos = Offset(
        neuralPos.dx,
        neuralPos.dy + 8,
      ); // Offset below
      final reflectionColor = getNodeColor(node.id, node.type).withOpacity(0.2);

      // Reflection glow
      final reflectionGlowPaint =
          Paint()
            ..color = reflectionColor.withOpacity(0.1)
            ..maskFilter = MaskFilter.blur(BlurStyle.normal, 6);
      canvas.drawCircle(reflectionPos, 10, reflectionGlowPaint);

      // Reflection main circle
      final reflectionPaint =
          Paint()
            ..color = reflectionColor
            ..style = PaintingStyle.fill;
      canvas.drawCircle(reflectionPos, 5, reflectionPaint);

      // Add glow effect for main node
      final glowPaint =
          Paint()
            ..color = getNodeColor(node.id, node.type).withOpacity(0.3)
            ..maskFilter = MaskFilter.blur(BlurStyle.normal, 8);
      canvas.drawCircle(neuralPos, 12, glowPaint);

      // Main node
      final nodePaint =
          Paint()
            ..color = getNodeColor(node.id, node.type).withOpacity(0.9)
            ..style = PaintingStyle.fill;
      canvas.drawCircle(
        neuralPos,
        6, // Static, fixed size (no pulse)
        nodePaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _HypergraphPainter oldDelegate) => true;
}
