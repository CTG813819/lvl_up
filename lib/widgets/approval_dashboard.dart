import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/network_config.dart';

class ApprovalDashboard extends StatefulWidget {
  @override
  _ApprovalDashboardState createState() => _ApprovalDashboardState();
}

class _ApprovalDashboardState extends State<ApprovalDashboard> {
  List<Map<String, dynamic>> pendingApprovals = [];
  Map<String, dynamic> approvalStats = {};
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _loadApprovalData();
  }

  Future<void> _loadApprovalData() async {
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
  // Load pending approvals
      final approvalsResponse = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/approval/pending'),
      );

      if (approvalsResponse.statusCode == 200) {
        final approvalsData = json.decode(approvalsResponse.body);
        setState(() {
          pendingApprovals = List<Map<String, dynamic>>.from(
            approvalsData['approvals'],
          );
        });
      }

  // Load approval statistics
      final statsResponse = await http.get(
        Uri.parse('${NetworkConfig.backendUrl}/api/approval/pending'),
      );

      if (statsResponse.statusCode == 200) {
        final statsData = json.decode(statsResponse.body);
        setState(() {
          approvalStats = statsData['stats'];
        });
      }

      setState(() {
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        error = e.toString();
      });
    }
  }

  Future<void> _approveImprovement(String approvalId) async {
    try {
      final response = await http.post(
        Uri.parse(
          '${NetworkConfig.backendUrl}/api/approval/pending',
        ),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'userId': 'flutter-user',
          'comments': 'Approved via Flutter app',
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Improvement approved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        _loadApprovalData(); // Refresh data
      } else {
        throw Exception('Failed to approve improvement');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error approving improvement: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _rejectImprovement(String approvalId) async {
    final reasonController = TextEditingController();

    final reason = await showDialog<String>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text('Reject Improvement'),
            content: TextField(
              controller: reasonController,
              decoration: InputDecoration(
                labelText: 'Reason for rejection',
                hintText: 'Enter reason for rejecting this improvement...',
              ),
              maxLines: 3,
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text('Cancel'),
              ),
              ElevatedButton(
                onPressed:
                    () => Navigator.of(context).pop(reasonController.text),
                child: Text('Reject'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              ),
            ],
          ),
    );

    if (reason != null) {
      try {
        final response = await http.post(
          Uri.parse(
            '${NetworkConfig.backendUrl}/api/approval/pending',
          ),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({'userId': 'flutter-user', 'reason': reason}),
        );

        if (response.statusCode == 200) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Improvement rejected'),
              backgroundColor: Colors.orange,
            ),
          );
          _loadApprovalData(); // Refresh data
        } else {
          throw Exception('Failed to reject improvement');
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error rejecting improvement: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('AI Approval Dashboard'),
        backgroundColor: Colors.deepPurple,
        actions: [
          IconButton(icon: Icon(Icons.refresh), onPressed: _loadApprovalData),
        ],
      ),
      body:
          isLoading
              ? Center(child: CircularProgressIndicator())
              : error != null
              ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.error, size: 64, color: Colors.red),
                    SizedBox(height: 16),
                    Text('Error: $error'),
                    SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: _loadApprovalData,
                      child: Text('Retry'),
                    ),
                  ],
                ),
              )
              : SingleChildScrollView(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
  // Statistics Card
                    Card(
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Approval Statistics',
                              style: Theme.of(context).textTheme.headlineSmall,
                            ),
                            SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _buildStatItem(
                                  'Total',
                                  approvalStats['total']?.toString() ?? '0',
                                  Colors.blue,
                                ),
                                _buildStatItem(
                                  'Pending',
                                  approvalStats['pending']?.toString() ?? '0',
                                  Colors.orange,
                                ),
                                _buildStatItem(
                                  'Approved',
                                  approvalStats['approved']?.toString() ?? '0',
                                  Colors.green,
                                ),
                                _buildStatItem(
                                  'Rejected',
                                  approvalStats['rejected']?.toString() ?? '0',
                                  Colors.red,
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    SizedBox(height: 24),

  // Pending Approvals
                    Text(
                      'Pending Approvals (${pendingApprovals.length})',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    SizedBox(height: 16),

                    if (pendingApprovals.isEmpty)
                      Card(
                        child: Padding(
                          padding: EdgeInsets.all(32),
                          child: Center(
                            child: Column(
                              children: [
                                Icon(
                                  Icons.check_circle,
                                  size: 64,
                                  color: Colors.green,
                                ),
                                SizedBox(height: 16),
                                Text(
                                  'No pending approvals',
                                  style:
                                      Theme.of(context).textTheme.headlineSmall,
                                ),
                                SizedBox(height: 8),
                                Text(
                                  'All AI improvements have been reviewed',
                                  style: Theme.of(context).textTheme.bodyMedium
                                      ?.copyWith(color: Colors.grey[600]),
                                ),
                              ],
                            ),
                          ),
                        ),
                      )
                    else
                      ...pendingApprovals.map(
                        (approval) => _buildApprovalCard(approval),
                      ),
                  ],
                ),
              ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Container(
          padding: EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
        SizedBox(height: 8),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildApprovalCard(Map<String, dynamic> approval) {
    return Card(
      margin: EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getAIColor(approval['aiType']),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    approval['aiType'],
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
                Spacer(),
                Text(
                  'ID: ${approval['id']}',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
            SizedBox(height: 12),
            Text(
              'Updates: ${approval['updates']?.length ?? 0} improvements',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            SizedBox(height: 8),
            if (approval['filePath'] != null)
              Text(
                'File: ${approval['filePath']}',
                style: TextStyle(color: Colors.grey[600]),
              ),
            SizedBox(height: 8),
            if (approval['isNewFile'] == true)
              Container(
                padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'New File',
                  style: TextStyle(
                    color: Colors.blue,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _approveImprovement(approval['id']),
                    icon: Icon(Icons.check, color: Colors.white),
                    label: Text('Approve'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _rejectImprovement(approval['id']),
                    icon: Icon(Icons.close, color: Colors.white),
                    label: Text('Reject'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 12),
            if (approval['prUrl'] != null)
              InkWell(
                onTap: () {
  // Open PR URL in browser
                },
                child: Text(
                  'View Pull Request',
                  style: TextStyle(
                    color: Colors.blue,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Color _getAIColor(String aiType) {
    switch (aiType?.toLowerCase()) {
      case 'imperium':
        return Colors.purple;
      case 'guardian':
        return Colors.blue;
      case 'sandbox':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}
