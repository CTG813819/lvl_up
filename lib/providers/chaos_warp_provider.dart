import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'proposal_provider.dart';

class ChaosWarpProvider with ChangeNotifier {
  bool _chaosMode = false;
  bool _warpMode = false;
  DateTime? _chaosStartTime;
  DateTime? _chaosEndTime;
  bool _isLoading = false;

  bool get chaosMode => _chaosMode;
  bool get warpMode => _warpMode;
  DateTime? get chaosStartTime => _chaosStartTime;
  DateTime? get chaosEndTime => _chaosEndTime;
  bool get isLoading => _isLoading;

  // Check if Chaos mode should still be active based on time
  bool get isChaosActive {
    if (!_chaosMode || _chaosEndTime == null) return false;
    return DateTime.now().isBefore(_chaosEndTime!);
  }

  // Get remaining time for Chaos mode
  Duration? get chaosRemainingTime {
    if (!_chaosMode || _chaosEndTime == null) return null;
    final remaining = _chaosEndTime!.difference(DateTime.now());
    return remaining.isNegative ? Duration.zero : remaining;
  }

  // Format remaining time as string
  String get chaosRemainingTimeFormatted {
    final remaining = chaosRemainingTime;
    if (remaining == null) return '';
    
    final hours = remaining.inHours;
    final minutes = remaining.inMinutes % 60;
    return '${hours}h ${minutes}m';
  }

  Future<void> activateChaos() async {
    if (_warpMode) {
      throw Exception('Cannot activate Chaos while Warp mode is active');
    }

    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('${ProposalProvider.backendUrl}/api/chaos/activate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _chaosMode = true;
        _chaosStartTime = DateTime.now();
        _chaosEndTime = DateTime.parse(data['chaosEndTime']);
        
        // Schedule deactivation check
        _scheduleChaosDeactivation();
        
        notifyListeners();
      } else {
        throw Exception('Failed to activate Chaos mode');
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> activateWarp() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('${ProposalProvider.backendUrl}/api/warp/activate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _warpMode = true;
        _chaosMode = false; // Chaos mode is overridden by Warp
        _chaosStartTime = null;
        _chaosEndTime = null;
        notifyListeners();
      } else {
        throw Exception('Failed to activate Warp mode');
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deactivateWarp() async {
    if (!_warpMode) return;

    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('${ProposalProvider.backendUrl}/api/warp/deactivate'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        _warpMode = false;
        notifyListeners();
      } else {
        throw Exception('Failed to deactivate Warp mode');
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> getStatus() async {
    try {
      final response = await http.get(
        Uri.parse('${ProposalProvider.backendUrl}/api/chaos-warp/status'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _chaosMode = data['chaosMode'] ?? false;
        _warpMode = data['warpMode'] ?? false;
        _chaosStartTime = data['chaosStartTime'] != null 
            ? DateTime.parse(data['chaosStartTime']) 
            : null;
        _chaosEndTime = data['chaosEndTime'] != null 
            ? DateTime.parse(data['chaosEndTime']) 
            : null;
        
        // If Chaos mode is active, schedule deactivation check
        if (_chaosMode && _chaosEndTime != null) {
          _scheduleChaosDeactivation();
        }
        
        notifyListeners();
      }
    } catch (e) {
      print('[CHAOS_WARP_PROVIDER] Error fetching status: $e');
    }
  }

  void _scheduleChaosDeactivation() {
    if (_chaosEndTime == null) return;
    
    final remaining = _chaosEndTime!.difference(DateTime.now());
    if (remaining.isNegative) {
      // Chaos mode should already be deactivated
      _chaosMode = false;
      _chaosStartTime = null;
      _chaosEndTime = null;
      notifyListeners();
      return;
    }

    // Schedule deactivation
    Future.delayed(remaining, () {
      if (_chaosMode && !_warpMode) {
        _chaosMode = false;
        _chaosStartTime = null;
        _chaosEndTime = null;
        notifyListeners();
      }
    });
  }

  // Check status periodically
  void startStatusPolling() {
    // Check status every 30 seconds
    Future.delayed(Duration(seconds: 30), () {
      if (!_warpMode) { // Don't poll if Warp mode is active
        getStatus();
        startStatusPolling();
      }
    });
  }
} 