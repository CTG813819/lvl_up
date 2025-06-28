import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:the_codex/entries/add_entry.dart';
import 'package:the_codex/models/entry.dart';
import '../entry_manager.dart';
import 'view_entry.dart';
import 'edit_entry.dart';
import 'entry_pin_screen.dart';

class ListEntries extends StatefulWidget {
  static const routeName = '/entries';
  const ListEntries({Key? key}) : super(key: key);

  @override
  _ListEntriesState createState() => _ListEntriesState();
}

class _ListEntriesState extends State<ListEntries>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final EntryManager _entryManager = EntryManager();

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  List<Animation<double>> _createAnimations(int count) {
    return List.generate(
      count,
      (index) => Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(
          parent: _controller,
          curve: Interval(
            (count - index - 1) * 0.1,
            1.0,
            curve: Curves.easeOut,
          ),
        ),
      ),
    );
  }

  void _navigateToAddEntry() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => EntryPinScreen(
          title: 'Add New Entry',
          onPinEntered: (pin, context) {
            Navigator.of(context).pushReplacementNamed(AddEntry.routeName);
          },
        ),
      ),
    );
  }

  void _navigateToViewEntry(Entry entry) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => EntryPinScreen(
          title: 'View Entry',
          isViewing: true,
          onPinEntered: (pin, context) {
            Navigator.of(context).pushReplacementNamed(
              ViewEntry.routeName,
              arguments: entry,
            );
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<Box<Entry>>(
      valueListenable: Hive.box<Entry>('entries').listenable(),
      builder: (context, box, _) {
        final entries = box.values.toList();
        final tabHeaders =
            entries
                .asMap()
                .entries
                .map((entry) => _entryManager.intToRoman(entry.key + 1))
                .toList();
        _createAnimations(entries.length);

        if (entries.isEmpty) {
          return Scaffold(
            appBar: AppBar(
              backgroundColor: Colors.black,
              title: const Text(
                'Entries',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              iconTheme: const IconThemeData(color: Colors.white),
            ),
            body: const Center(
              child: Text(
                'No entries yet. Add one!',
                style: TextStyle(color: Colors.white, fontSize: 20),
              ),
            ),
            floatingActionButton: FloatingActionButton(
              onPressed: _navigateToAddEntry,
              backgroundColor: Colors.black,
              child: const Icon(Icons.add, color: Colors.white),
            ),
          );
        }

        return Scaffold(
          appBar: AppBar(
            backgroundColor: Colors.black,
            title: const Text(
              'Entries',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            iconTheme: const IconThemeData(color: Colors.white),
          ),
          backgroundColor: Colors.black,
          body: Stack(
            alignment: Alignment.topCenter,
            children: [
              Positioned(
                top: 0,
                right: 0,
                child: IconButton(
                  icon: const Icon(Icons.delete_forever, color: Colors.red),
                  onPressed: () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (_) => AlertDialog(
                        title: const Text('Clear All Entries'),
                        content: const Text(
                          'Are you sure you want to delete all entries?',
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(false),
                            child: const Text('Cancel'),
                          ),
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(true),
                            child: const Text('Delete'),
                          ),
                        ],
                      ),
                    );
                    if (confirm == true) {
                      try {
                        await _entryManager.clearAllEntries();
                        setState(() {}); // Refresh UI
                      } catch (e) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('Failed to clear entries: $e'),
                          ),
                        );
                      }
                    }
                  },
                  tooltip: 'Clear all entries',
                ),
              ),
              ListView.builder(
                padding: const EdgeInsets.only(top: 40.0, bottom: 80.0),
                itemCount: entries.length,
                itemBuilder: (context, index) {
                  final entryItem = entries[index];
                  final tabHeader = tabHeaders[index];
                  final entryImage = entryItem.imageUrl;
                  final double offset = 15.0 * index;
                  return Transform.translate(
                    offset: Offset(0, offset),
                    child: Center(
                      child: Stack(
                        children: [
                          Container(
                            width: MediaQuery.of(context).size.width * 0.85,
                            height: 140.0,
                            margin: const EdgeInsets.symmetric(vertical: 8.0),
                            decoration: BoxDecoration(
                              image: DecorationImage(
                                image: AssetImage(entryImage),
                                fit: BoxFit.cover,
                                colorFilter: ColorFilter.mode(
                                  Colors.black.withOpacity(0.5),
                                  BlendMode.dstATop,
                                ),
                                onError: (exception, stackTrace) =>
                                    const AssetImage(
                                  'images/entry_placeholder_image.jpg',
                                ),
                              ),
                              borderRadius: BorderRadius.circular(18.0),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.3),
                                  blurRadius: 12.0,
                                  offset: const Offset(0, 6),
                                ),
                              ],
                            ),
                            child: Stack(
                              children: [
                                Positioned(
                                  top: 10.0,
                                  left: 10.0,
                                  child: Text(
                                    tabHeader,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 24,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                Positioned(
                                  top: 10.0,
                                  right: 10.0,
                                  child: IconButton(
                                    icon: const Icon(
                                      Icons.edit,
                                      color: Colors.white,
                                      size: 28,
                                    ),
                                    onPressed: () {
                                      Navigator.of(context).pushNamed(
                                        EditEntry.routeName,
                                        arguments: entryItem,
                                      );
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Positioned.fill(
                            child: Material(
                              color: Colors.transparent,
                              child: InkWell(
                                borderRadius: BorderRadius.circular(18.0),
                                onTap: () => _navigateToViewEntry(entryItem),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: _navigateToAddEntry,
            backgroundColor: Colors.black,
            child: const Icon(Icons.add, color: Colors.white),
          ),
        );
      },
    );
  }
}
