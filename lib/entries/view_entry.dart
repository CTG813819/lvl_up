import 'package:flutter/material.dart';

import '../models/entry.dart';
import '../entry_manager.dart';
import 'edit_entry.dart';
import 'entry_pin_screen.dart';

class ViewEntry extends StatefulWidget {
  static const routeName = '/view-entry';
  final Entry entry;
  const ViewEntry({Key? key, required this.entry}) : super(key: key);

  @override
  _ViewEntryState createState() => _ViewEntryState();
}

class _ViewEntryState extends State<ViewEntry>
    with SingleTickerProviderStateMixin {
  late AnimationController _optionsAnimationController;
  late Animation<Offset> _optionsAnimation, _optionsDelayedAnimation;
  bool _optionsIsOpen = false;

  @override
  void initState() {
    super.initState();
    _optionsAnimationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _optionsAnimation =
        Tween<Offset>(
            begin: const Offset(100, 0),
            end: const Offset(0, 0),
          ).animate(
            CurvedAnimation(
              parent: _optionsAnimationController,
              curve: Curves.easeOutBack,
            ),
          )
          ..addListener(() {
            setState(() {});
          })
          ..addStatusListener(_setOptionsStatus);
    _optionsDelayedAnimation = Tween<Offset>(
      begin: const Offset(100, 0),
      end: const Offset(0, 0),
    ).animate(
      CurvedAnimation(
        parent: _optionsAnimationController,
        curve: const Interval(0.2, 1.0, curve: Curves.easeOutBack),
      ),
    );
  }

  void _setOptionsStatus(AnimationStatus status) {
    setState(() {
      _optionsIsOpen =
          status == AnimationStatus.forward ||
          status == AnimationStatus.completed;
    });
  }

  void _openOptions() {
    _optionsAnimationController.forward();
  }

  void _closeOptions() {
    _optionsAnimationController.reverse();
  }

  void _onEditClicked() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder:
            (context) => EntryPinScreen(
              title: 'Edit Entry',
              onPinEntered: (pin, context) {
                Navigator.of(context).pushReplacementNamed(
                  EditEntry.routeName,
                  arguments: widget.entry,
                );
              },
            ),
      ),
    );
  }

  void _onDeleteClicked(int entryId) {
    showDialog(
      context: context,
      builder:
          (_) => AlertDialog(
            title: const Text('Delete Entry'),
            content: const Text('Are you sure you want to delete this?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  Navigator.of(context).push(
                    MaterialPageRoute(
                      builder:
                          (context) => EntryPinScreen(
                            title: 'Confirm Delete',
                            onPinEntered: (pin, context) async {
                              try {
                                final success = await EntryManager()
                                    .deleteEntry(entryId);
                                Navigator.of(context).pop(); // Close PIN screen
                                if (success) {
                                  Navigator.of(
                                    context,
                                  ).pop(); // Return to ListEntries
                                } else {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                      content: Text('Failed to delete entry'),
                                    ),
                                  );
                                }
                              } catch (e) {
                                Navigator.of(context).pop(); // Close PIN screen
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('Error deleting entry: $e'),
                                  ),
                                );
                              }
                            },
                          ),
                    ),
                  );
                },
                child: const Text('Delete'),
              ),
            ],
          ),
    );
  }

  @override
  void dispose() {
    _optionsAnimationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final entry = widget.entry;

    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          ListView(
            padding: const EdgeInsets.only(top: 0.0),
            physics: const ClampingScrollPhysics(),
            children: [
              Stack(
                children: [
                  Image.asset(
                    entry.imageUrl,
                    height: 340.0,
                    width: MediaQuery.of(context).size.width,
                    fit: BoxFit.cover,
                    errorBuilder:
                        (context, error, stackTrace) => Image.asset(
                          'images/entry_placeholder_image.jpg',
                          height: 340.0,
                          width: MediaQuery.of(context).size.width,
                          fit: BoxFit.cover,
                        ),
                  ),
                  Positioned(
                    top: 200.0,
                    child: Container(
                      width: MediaQuery.of(context).size.width,
                      padding: const EdgeInsets.symmetric(horizontal: 30),
                      alignment: Alignment.center,
                      child: Text(
                        entry.title,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 32,
                          letterSpacing: 0.8,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 300.0,
                    width: MediaQuery.of(context).size.width,
                    child: Container(
                      height: 40,
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: const BorderRadius.only(
                          topRight: Radius.circular(100.0),
                          topLeft: Radius.circular(100.0),
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.red.withOpacity(.4),
                            offset: const Offset(0.0, -8),
                            blurRadius: 6,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.fromLTRB(20.0, 40.0, 20.0, 50.0),
                alignment: Alignment.center,
                child: Text(
                  entry.content,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 24.0,
                    height: 1.4,
                    color: Colors.white,
                  ),
                ),
              ),
            ],
          ),
          Positioned(
            bottom: 20.0,
            right: 20.0,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                InkResponse(
                  onTap: _optionsIsOpen ? _closeOptions : _openOptions,
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    margin: const EdgeInsets.only(bottom: 10),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border.all(color: Colors.black12),
                      borderRadius: BorderRadius.circular(100),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF3C4858).withOpacity(.5),
                          offset: const Offset(1.0, 10.0),
                          blurRadius: 10.0,
                        ),
                      ],
                    ),
                    child: Icon(
                      _optionsIsOpen ? Icons.close : Icons.more_vert,
                      color: const Color(0xFF3C4858),
                    ),
                  ),
                ),
                Transform.translate(
                  offset: _optionsAnimation.value,
                  child: InkResponse(
                    onTap: _onEditClicked,
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      margin: const EdgeInsets.only(bottom: 10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        border: Border.all(color: Colors.black12),
                        borderRadius: BorderRadius.circular(100),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF3C4858).withOpacity(.5),
                            offset: const Offset(1.0, 10.0),
                            blurRadius: 10.0,
                          ),
                        ],
                      ),
                      child: const Icon(
                        Icons.edit,
                        color: Color(0xFF3C4858),
                        semanticLabel: 'Edit',
                      ),
                    ),
                  ),
                ),
                Transform.translate(
                  offset: _optionsDelayedAnimation.value,
                  child: InkResponse(
                    onTap: () => _onDeleteClicked(entry.id),
                    child: Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        border: Border.all(color: Colors.black12),
                        borderRadius: BorderRadius.circular(100),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF3C4858).withOpacity(.5),
                            offset: const Offset(1.0, 10.0),
                            blurRadius: 10.0,
                          ),
                        ],
                      ),
                      child: Icon(
                        Icons.delete_outline,
                        color: Colors.red.shade400,
                        semanticLabel: 'Delete',
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
