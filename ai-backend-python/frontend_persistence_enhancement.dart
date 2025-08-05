// Enhanced AI Growth Analytics Provider with better persistence
// Add this to lib/providers/ai_growth_analytics_provider.dart

import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

const String backendUrl =
    'http://localhost:8000'; // Replace with your actual backend URL
const String _lastUpdatedKey =
    'last_updated_key'; // Use your actual key if different

class AIGrowthAnalyticsProvider extends ChangeNotifier {
  Map<String, dynamic> _agentsData = {};
  // ... existing code ...

  Future<void> _saveAgentsData() async {
    // Implement your save logic here, or leave empty if not needed
  }

  // Enhanced persistence methods
  Future<void> _enhancedLoadAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Load cached data first
      final cachedDataString = prefs.getString('agents_data');
      if (cachedDataString != null) {
        final cachedData = jsonDecode(cachedDataString);
        _agentsData = Map<String, dynamic>.from(cachedData);
        print('[AI_GROWTH_ANALYTICS_PROVIDER] Loaded cached agents data');
      }

      // Try to load from backend
      try {
        final response = await http
            .get(
              Uri.parse('$backendUrl/api/agents/status'),
              headers: {'Content-Type': 'application/json'},
            )
            .timeout(const Duration(seconds: 10));

        if (response.statusCode == 200) {
          final backendData = jsonDecode(response.body);

          // Merge backend data with cached data, preserving higher values
          if (backendData.containsKey('agents')) {
            final backendAgents = backendData['agents'] as Map<String, dynamic>;

            for (final agentId in backendAgents.keys) {
              final backendAgent =
                  backendAgents[agentId] as Map<String, dynamic>;

              if (_agentsData.containsKey(agentId)) {
                final cachedAgent =
                    _agentsData[agentId] as Map<String, dynamic>;

                // Preserve higher learning scores and cycle counts
                final cachedScore =
                    (cachedAgent['learning_score'] ?? 0.0).toDouble();
                final backendScore =
                    (backendAgent['learning_score'] ?? 0.0).toDouble();

                if (backendScore > cachedScore || cachedScore == 0) {
                  cachedAgent['learning_score'] = backendScore;
                }

                final cachedCycles =
                    (cachedAgent['total_learning_cycles'] ?? 0).toInt();
                final backendCycles =
                    (backendAgent['total_learning_cycles'] ?? 0).toInt();

                if (backendCycles > cachedCycles || cachedCycles == 0) {
                  cachedAgent['total_learning_cycles'] = backendCycles;
                }

                // Update other fields from backend
                cachedAgent.addAll(backendAgent);
                _agentsData[agentId] = cachedAgent;
              } else {
                _agentsData[agentId] = backendAgent;
              }
            }
          }

          print(
            '[AI_GROWTH_ANALYTICS_PROVIDER] Merged backend and cached data',
          );
        }
      } catch (e) {
        print(
          '[AI_GROWTH_ANALYTICS_PROVIDER] Backend load failed, using cached data: $e',
        );
      }

      // Save the merged data
      await _saveAgentsData();
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Error in enhanced load: $e');
    }
  }

  // Enhanced save method with backup
  Future<void> _enhancedSaveAgentsData() async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Save current data
      await prefs.setString('agents_data', jsonEncode(_agentsData));

      // Create backup with timestamp
      final backupKey =
          'agents_data_backup_${DateTime.now().millisecondsSinceEpoch}';
      await prefs.setString(backupKey, jsonEncode(_agentsData));

      // Keep only last 5 backups
      final keys = prefs.getKeys();
      final backupKeys =
          keys.where((key) => key.startsWith('agents_data_backup_')).toList();
      backupKeys.sort();

      if (backupKeys.length > 5) {
        for (int i = 0; i < backupKeys.length - 5; i++) {
          await prefs.remove(backupKeys[i]);
        }
      }

      await prefs.setString(_lastUpdatedKey, DateTime.now().toIso8601String());
      print(
        '[AI_GROWTH_ANALYTICS_PROVIDER] Enhanced save completed with backup',
      );
    } catch (e) {
      print('[AI_GROWTH_ANALYTICS_PROVIDER] Error in enhanced save: $e');
    }
  }
}
