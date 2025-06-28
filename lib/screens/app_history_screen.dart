import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_history_provider.dart';
import '../models/app_history.dart';
import 'dart:developer' as developer;

class AppHistoryScreen extends StatefulWidget {
  const AppHistoryScreen({Key? key}) : super(key: key);

  @override
  State<AppHistoryScreen> createState() => _AppHistoryScreenState();
}

class _AppHistoryScreenState extends State<AppHistoryScreen> {
  final _pinController = TextEditingController();
  final _searchController = TextEditingController();
  HistoryCategory _selectedCategory = HistoryCategory.system;
  bool _isSearching = false;
  bool _sortDescending = true;
  String _sortBy = 'timestamp';

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      if (!mounted) return;
      final provider = Provider.of<AppHistoryProvider>(context, listen: false);
      await provider.loadHistory();
      if (mounted) {
        setState(() {});
      }
      developer.log('History loaded successfully');
    } catch (e) {
      developer.log('Error loading history: $e');
    }
  }

  @override
  void dispose() {
    _pinController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  List<AppHistoryEntry> _sortEntries(List<AppHistoryEntry> entries) {
    switch (_sortBy) {
      case 'timestamp':
        entries.sort(
          (a, b) =>
              _sortDescending
                  ? b.timestamp.compareTo(a.timestamp)
                  : a.timestamp.compareTo(b.timestamp),
        );
        break;
      case 'title':
        entries.sort(
          (a, b) =>
              _sortDescending
                  ? b.title.compareTo(a.title)
                  : a.title.compareTo(b.title),
        );
        break;
      case 'category':
        entries.sort(
          (a, b) =>
              _sortDescending
                  ? b.category.toString().compareTo(a.category.toString())
                  : a.category.toString().compareTo(b.category.toString()),
        );
        break;
    }
    return entries;
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AppHistoryProvider>(
      builder: (context, provider, child) {
        developer.log(
          'Building AppHistoryScreen. IsAuthenticated: ${provider.isAuthenticated}, IsPinSet: ${provider.isPinSet}',
        );
        if (!provider.isAuthenticated) {
          return _buildPinScreen(provider);
        }
        return _buildHistoryScreen(provider);
      },
    );
  }

  Widget _buildPinScreen(AppHistoryProvider provider) {
    return Scaffold(
      appBar: AppBar(title: const Text('App History')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              provider.isPinSet
                  ? 'Enter PIN to view history'
                  : 'Set up PIN to protect history',
              style: const TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _pinController,
              decoration: const InputDecoration(
                labelText: 'PIN',
                border: OutlineInputBorder(),
                hintText: 'Enter 4-digit PIN',
              ),
              obscureText: true,
              keyboardType: TextInputType.number,
              maxLength: 4,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                if (_pinController.text.length != 4) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('PIN must be 4 digits')),
                  );
                  return;
                }
                final success = await provider.verifyPin(_pinController.text);
                if (!success) {
                  ScaffoldMessenger.of(
                    context,
                  ).showSnackBar(const SnackBar(content: Text('Invalid PIN')));
                } else {
                  await _loadHistory();
                }
              },
              child: Text(provider.isPinSet ? 'Submit' : 'Set PIN'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoryScreen(AppHistoryProvider provider) {
    List<AppHistoryEntry> entries =
        _isSearching
            ? provider.searchHistory(_searchController.text)
            : provider.getEntriesByCategory(_selectedCategory);

    entries = _sortEntries(entries);
    developer.log('Building history screen with ${entries.length} entries');

    return Scaffold(
      appBar: AppBar(
        title: const Text('App History'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            onSelected: (value) {
              setState(() {
                if (value == 'toggle') {
                  _sortDescending = !_sortDescending;
                } else {
                  _sortBy = value;
                }
              });
            },
            itemBuilder:
                (context) => [
                  const PopupMenuItem(
                    value: 'timestamp',
                    child: Text('Sort by Time'),
                  ),
                  const PopupMenuItem(
                    value: 'title',
                    child: Text('Sort by Title'),
                  ),
                  const PopupMenuItem(
                    value: 'category',
                    child: Text('Sort by Category'),
                  ),
                  const PopupMenuDivider(),
                  PopupMenuItem(
                    value: 'toggle',
                    child: Text(
                      _sortDescending ? 'Sort Ascending' : 'Sort Descending',
                    ),
                  ),
                ],
          ),
          IconButton(
            icon: Icon(_isSearching ? Icons.close : Icons.search),
            onPressed: () {
              setState(() {
                _isSearching = !_isSearching;
                if (!_isSearching) {
                  _searchController.clear();
                }
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              await _loadHistory();
              setState(() {});
            },
          ),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () => _showClearHistoryDialog(provider),
          ),
        ],
      ),
      body: Column(
        children: [
          if (_isSearching)
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: TextField(
                controller: _searchController,
                decoration: const InputDecoration(
                  labelText: 'Search history',
                  prefixIcon: Icon(Icons.search),
                ),
                onChanged: (value) => setState(() {}),
              ),
            ),
          if (!_isSearching)
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children:
                    HistoryCategory.values.map((category) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4.0),
                        child: ChoiceChip(
                          label: Text(category.toString().split('.').last),
                          selected: _selectedCategory == category,
                          onSelected: (selected) {
                            if (selected) {
                              setState(() => _selectedCategory = category);
                            }
                          },
                        ),
                      );
                    }).toList(),
              ),
            ),
          Expanded(
            child:
                entries.isEmpty
                    ? const Center(
                      child: Text(
                        'No history entries found',
                        style: TextStyle(fontSize: 16),
                      ),
                    )
                    : ListView.builder(
                      itemCount: entries.length,
                      itemBuilder: (context, index) {
                        final entry = entries[index];
                        developer.log('Building entry: ${entry.title}');
                        return Card(
                          margin: const EdgeInsets.symmetric(
                            horizontal: 8.0,
                            vertical: 4.0,
                          ),
                          child: ExpansionTile(
                            leading: _getCategoryIcon(entry.category),
                            title: Text(
                              entry.title,
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color:
                                    entry.errorCode != null ? Colors.red : null,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  _formatDate(entry.timestamp),
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                if (entry.errorCode != null)
                                  Text(
                                    'Error: ${entry.errorCode}',
                                    style: const TextStyle(
                                      color: Colors.red,
                                      fontSize: 12,
                                    ),
                                  ),
                              ],
                            ),
                            children: [
                              Padding(
                                padding: const EdgeInsets.all(16.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      entry.description,
                                      style: const TextStyle(fontSize: 16),
                                    ),
                                    if (entry.errorCode != null) ...[
                                      const SizedBox(height: 8),
                                      Container(
                                        padding: const EdgeInsets.all(8),
                                        decoration: BoxDecoration(
                                          color: Colors.red.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(
                                            4,
                                          ),
                                        ),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              'Error Code: ${entry.errorCode}',
                                              style: const TextStyle(
                                                color: Colors.red,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                            if (entry.errorType != null) ...[
                                              const SizedBox(height: 4),
                                              Text(
                                                'Error Type: ${entry.errorType}',
                                                style: const TextStyle(
                                                  color: Colors.orange,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ],
                                          ],
                                        ),
                                      ),
                                    ],
                                    if (entry.errorContext != null) ...[
                                      const SizedBox(height: 8),
                                      const Text(
                                        'Error Context:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.all(8),
                                        decoration: BoxDecoration(
                                          color: Colors.grey[200],
                                          borderRadius: BorderRadius.circular(
                                            4,
                                          ),
                                        ),
                                        child: Text(
                                          entry.errorContext.toString(),
                                          style: const TextStyle(
                                            fontFamily: 'monospace',
                                          ),
                                        ),
                                      ),
                                    ],
                                    if (entry.stackTrace != null) ...[
                                      const SizedBox(height: 8),
                                      const Text(
                                        'Stack Trace:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.all(8),
                                        decoration: BoxDecoration(
                                          color: Colors.grey[200],
                                          borderRadius: BorderRadius.circular(
                                            4,
                                          ),
                                        ),
                                        child: Text(
                                          entry.stackTrace!,
                                          style: const TextStyle(
                                            fontFamily: 'monospace',
                                            fontSize: 12,
                                          ),
                                        ),
                                      ),
                                    ],
                                    if (entry.metadata != null) ...[
                                      const SizedBox(height: 8),
                                      const Text(
                                        'Additional Info:',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.all(8),
                                        decoration: BoxDecoration(
                                          color: Colors.grey[200],
                                          borderRadius: BorderRadius.circular(
                                            4,
                                          ),
                                        ),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children:
                                              entry.metadata!.entries.map((
                                                entry,
                                              ) {
                                                return Padding(
                                                  padding:
                                                      const EdgeInsets.symmetric(
                                                        vertical: 2.0,
                                                      ),
                                                  child: Text(
                                                    '${entry.key}: ${entry.value}',
                                                    style: const TextStyle(
                                                      fontFamily: 'monospace',
                                                    ),
                                                  ),
                                                );
                                              }).toList(),
                                        ),
                                      ),
                                    ],
                                  ],
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

  Widget _getCategoryIcon(HistoryCategory category) {
    IconData iconData;
    Color iconColor;

    switch (category) {
      case HistoryCategory.mission:
        iconData = Icons.flag;
        iconColor = Colors.blue;
        break;
      case HistoryCategory.entry:
        iconData = Icons.note;
        iconColor = Colors.green;
        break;
      case HistoryCategory.system:
        iconData = Icons.settings;
        iconColor = Colors.grey;
        break;
      case HistoryCategory.error:
        iconData = Icons.error;
        iconColor = Colors.red;
        break;
      case HistoryCategory.security:
        iconData = Icons.security;
        iconColor = Colors.orange;
        break;
    }

    return CircleAvatar(
      backgroundColor: iconColor.withOpacity(0.2),
      child: Icon(iconData, color: iconColor),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }

  Future<void> _showClearHistoryDialog(AppHistoryProvider provider) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Clear History'),
            content: const Text('Are you sure you want to clear all history?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text('Clear'),
              ),
            ],
          ),
    );

    if (confirmed == true) {
      await provider.clearHistory();
      setState(() {});
    }
  }
}
