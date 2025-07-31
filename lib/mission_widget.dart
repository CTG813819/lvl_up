import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:the_codex/mastery_list.dart';
import './mission.dart'
    show
        MissionProvider,
        MissionData,
        MissionType,
        MissionSubtask; // Import all needed classes
import 'dart:math';
import './entry_manager.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';
import 'dart:async';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import './mechanicum.dart';

class Mission extends StatefulWidget {
  const Mission({super.key});

  @override
  State<Mission> createState() => _MissionState();
}

class MissionCompletionDialog extends StatelessWidget {
  final MissionData mission;
  final VoidCallback onComplete;
  final VoidCallback onCancel;

  const MissionCompletionDialog({
    super.key,
    required this.mission,
    required this.onComplete,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Complete Mission'),
      content: Text('Are you sure you want to complete "${mission.title}"?'),
      actions: [
        TextButton(onPressed: onCancel, child: const Text('Cancel')),
        TextButton(onPressed: onComplete, child: const Text('Complete')),
      ],
    );
  }
}

class _MissionState extends State<Mission> with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  final EntryManager _entryManager = EntryManager();
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();
  Timer? _debugMissionCheckTimer;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    )..forward();
    /// Debug: Periodically check for mission uniqueness and independence
    if (kDebugMode) {
      _debugMissionCheckTimer = Timer.periodic(
        const Duration(seconds: 10),
        (_) => _debugCheckMissions(context),
      );
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _debugMissionCheckTimer?.cancel();
    super.dispose();
  }

  Color _getRandomColor() {
    final random = Random();
    return Color.fromRGBO(
      random.nextInt(256), // Red: 0-255
      random.nextInt(256), // Green: 0-255
      random.nextInt(256), // Blue: 0-255
      1.0, // Full opacity
    );
  }

  String _getNextImage() {
    return _entryManager.getNextImage();
  }

  Future<void> _pickImage() async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        await _entryManager.addCustomImage(image.path);
        /// Refresh the UI to show the new image
        setState(() {});
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error picking image: $e');
      }
      /// Show error message to user
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error adding image: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _showAddDialog(
    BuildContext context,
    MissionProvider missionProvider,
    MasteryProvider masteryProvider,
  ) async {
    if (kDebugMode) {
      print('FAB tapped');
    }
    try {
      /// Ensure mastery entries are loaded
      await masteryProvider.loadEntries();

      final titleController = TextEditingController();
      final descriptionController = TextEditingController();
      MissionType selectedType = MissionType.daily;
      String? selectedMasteryId;
      final masteryValueController = TextEditingController(text: '');
      List<MissionSubtask> subtasks = [];
      bool isCounterBased = false;
      int targetCount = -1; // Start with -1 to ensure toggle is off
      bool missionCreated = false;
      String selectedImage = _getNextImage();

      /// Add validation function
      bool validateMissionData(String title, MissionType type) {
        /// Check for duplicate missions
        final now = DateTime.now();
        final isDuplicate = missionProvider.missions.any(
          (m) =>
              m.title == title &&
              m.type == type &&
              m.createdAt != null &&
              m.createdAt!.year == now.year &&
              m.createdAt!.month == now.month &&
              m.createdAt!.day == now.day,
        );

        if (isDuplicate) {
          if (kDebugMode) {
            print('Mission validation failed: Duplicate mission found');
          }
          return false;
        }

        /// Validate title
        if (title.isEmpty) {
          if (kDebugMode) {
            print('Mission validation failed: Empty title');
          }
          return false;
        }

        /// Validate subtasks if present
        if (subtasks.isNotEmpty) {
          for (var subtask in subtasks) {
            if (subtask.name.isEmpty) {
              if (kDebugMode) {
                print('Mission validation failed: Empty subtask name');
              }
              return false;
            }
            if (subtask.requiredCompletions < 0) {
              if (kDebugMode) {
                print(
                  'Mission validation failed: Invalid required completions',
                );
              }
              return false;
            }
          }
        }

        /// For simple missions, we don't need subtasks or counter
        /// For all other missions, allow creation even if there are no subtasks and not counter-based (completion-based)
        if (kDebugMode) {
          print('Mission validation passed');
        }
        return true;
      }

      await showDialog<bool>(
        /// ignore: use_build_context_synchronously
        context: context,
        builder:
            (context) => StatefulBuilder(
              builder:
                  (context, setState) => AlertDialog(
                    backgroundColor: Colors.black,
                    title: const Text(
                      'Add Mission',
                      style: TextStyle(color: Colors.white),
                    ),
                    content: SingleChildScrollView(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          /// Image selector: scrollable picker
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                height: 150,
                                width: double.infinity,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(10),
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(10),
                                  child: Stack(
                                    children: [
                                      Positioned.fill(
                                        child: SmartImage(
                                          imagePath: selectedImage,
                                          fit: BoxFit.cover,
                                          width: 800,
                                          height: 400,
                                        ),
                                      ),
                                      Positioned.fill(
                                        child: Container(
                                          decoration: BoxDecoration(
                                            color: Colors.black.withOpacity(
                                              0.5,
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  Expanded(
                                    child: SizedBox(
                                      height: 70,
                                      child: ListView.separated(
                                        scrollDirection: Axis.horizontal,
                                        itemCount:
                                            _entryManager.imageList.length,
                                        separatorBuilder:
                                            (context, idx) =>
                                                const SizedBox(width: 8),
                                        itemBuilder: (context, idx) {
                                          final imgPath =
                                              _entryManager.imageList[idx];
                                          return GestureDetector(
                                            onTap: () {
                                              setState(() {
                                                selectedImage = imgPath;
                                              });
                                            },
                                            child: Container(
                                              decoration: BoxDecoration(
                                                border: Border.all(
                                                  color:
                                                      selectedImage == imgPath
                                                          ? Colors.amber
                                                          : Colors.transparent,
                                                  width: 3,
                                                ),
                                                borderRadius:
                                                    BorderRadius.circular(8),
                                              ),
                                              child: ClipRRect(
                                                borderRadius:
                                                    BorderRadius.circular(8),
                                                child: SmartImage(
                                                  imagePath: imgPath,
                                                  width: 70,
                                                  height: 70,
                                                  fit: BoxFit.cover,
                                                ),
                                              ),
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  /// Add Image button
                                  GestureDetector(
                                    onTap: _pickImage,
                                    child: Container(
                                      width: 70,
                                      height: 70,
                                      decoration: BoxDecoration(
                                        border: Border.all(
                                          color: Colors.blue,
                                          width: 2,
                                        ),
                                        borderRadius: BorderRadius.circular(8),
                                        color: Colors.blue.withOpacity(0.1),
                                      ),
                                      child: const Icon(
                                        Icons.add_photo_alternate,
                                        color: Colors.blue,
                                        size: 32,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: titleController,
                            style: const TextStyle(color: Colors.white),
                            decoration: const InputDecoration(
                              labelText: 'Title',
                              labelStyle: TextStyle(color: Colors.white),
                            ),
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: descriptionController,
                            style: const TextStyle(color: Colors.white),
                            decoration: const InputDecoration(
                              labelText: 'Description (Optional)',
                              labelStyle: TextStyle(color: Colors.white),
                            ),
                            maxLines: 3,
                          ),
                          const SizedBox(height: 16),
                          DropdownButtonFormField<MissionType>(
                            value: selectedType,
                            dropdownColor: Colors.black,
                            style: const TextStyle(color: Colors.white),
                            decoration: const InputDecoration(
                              labelText: 'Mission Type',
                              labelStyle: TextStyle(color: Colors.white),
                            ),
                            items:
                                MissionType.values.map((type) {
                                  String displayName =
                                      type.toString().split('.').last;
                                  /// Capitalize first letter and add spaces before capital letters
                                  displayName =
                                      displayName[0].toUpperCase() +
                                      displayName
                                          .substring(1)
                                          .replaceAllMapped(
                                            RegExp(r'([A-Z])'),
                                            (match) => ' ${match.group(1)}',
                                          );
                                  return DropdownMenuItem<MissionType>(
                                    value: type,
                                    child: Text(displayName),
                                  );
                                }).toList(),
                            onChanged: (value) {
                              if (value != null) {
                                setState(() {
                                  selectedType = value;
                                });
                              }
                            },
                          ),
                          const SizedBox(height: 16),
                          /// Add Simple Mission switch
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Simple Mission',
                                style: TextStyle(color: Colors.white),
                              ),
                              Switch(
                                value:
                                    !isCounterBased &&
                                    targetCount == 0 &&
                                    subtasks.isEmpty &&
                                    selectedType == MissionType.simple,
                                onChanged: (value) {
                                  setState(() {
                                    if (value) {
                                      selectedType = MissionType.simple;
                                      isCounterBased = false;
                                      targetCount = 0;
                                      subtasks = [];
                                    }
                                  });
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          /// Add completion-based toggle if not a simple mission
                          if (!(selectedType == MissionType.simple &&
                              !isCounterBased &&
                              targetCount == 0)) ...[
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Completion Based',
                                  style: TextStyle(color: Colors.white),
                                ),
                                Switch(
                                  value: targetCount >= 0,
                                  onChanged: (value) {
                                    setState(() {
                                      if (value) {
                                        targetCount =
                                            0; // Start with empty field
                                      } else {
                                        targetCount =
                                            -1; // Use -1 to indicate toggle is off
                                      }
                                    });
                                  },
                                ),
                              ],
                            ),
                            if (targetCount >= 0) ...[
                              const SizedBox(height: 8),
                              TextField(
                                controller: TextEditingController(
                                  text:
                                      targetCount > 0
                                          ? targetCount.toString()
                                          : '',
                                ),
                                style: const TextStyle(color: Colors.white),
                                decoration: const InputDecoration(
                                  labelText: 'Required Completions',
                                  labelStyle: TextStyle(color: Colors.white),
                                  hintText:
                                      'Enter number of required completions',
                                ),
                                keyboardType: TextInputType.number,
                                onChanged: (value) {
                                  if (value.isEmpty) {
                                    setState(() {
                                      targetCount = 0;
                                    });
                                    return;
                                  }
                                  final newValue = int.tryParse(value);
                                  if (newValue != null) {
                                    setState(() {
                                      targetCount = newValue > 0 ? newValue : 0;
                                    });
                                  }
                                },
                              ),
                              const SizedBox(height: 16),
                              DropdownButtonFormField<String>(
                                value: selectedMasteryId,
                                dropdownColor: Colors.black,
                                style: const TextStyle(color: Colors.white),
                                decoration: const InputDecoration(
                                  labelText: 'Link to Mastery (Optional)',
                                  labelStyle: TextStyle(color: Colors.white),
                                ),
                                items: [
                                  const DropdownMenuItem<String>(
                                    value: null,
                                    child: Text('None'),
                                  ),
                                  ...masteryProvider.entries.map((entry) {
                                    return DropdownMenuItem<String>(
                                      value: entry.id,
                                      child: Text(entry.title),
                                    );
                                  }),
                                ],
                                onChanged: (value) {
                                  setState(() {
                                    selectedMasteryId = value;
                                  });
                                },
                              ),
                              const SizedBox(height: 8),
                              TextField(
                                controller: masteryValueController,
                                style: const TextStyle(color: Colors.white),
                                decoration: const InputDecoration(
                                  labelText:
                                      'Minutes Added Per Completion (Optional)',
                                  hintText:
                                      'Enter minutes (e.g., 30 for 30 minutes)',
                                  labelStyle: TextStyle(color: Colors.white),
                                  hintStyle: TextStyle(color: Colors.white54),
                                ),
                                keyboardType:
                                    const TextInputType.numberWithOptions(
                                      decimal: false,
                                    ),
                                onChanged: (value) {
                                  /// Validate input is a positive number
                                  final intValue = int.tryParse(value);
                                  if (intValue != null && intValue > 0) {
                                    setState(() {
                                      masteryValueController.text = value;
                                    });
                                  } else if (value.isNotEmpty) {
                                    /// If invalid input, revert to previous valid value
                                    masteryValueController.text =
                                        masteryValueController.text;
                                  }
                                },
                              ),
                            ],
                          ],
                          const SizedBox(height: 16),
                          if (isCounterBased) ...[
                            const SizedBox(height: 16),
                            DropdownButtonFormField<String>(
                              value: selectedMasteryId,
                              dropdownColor: Colors.black,
                              style: const TextStyle(color: Colors.white),
                              decoration: const InputDecoration(
                                labelText: 'Link to Mastery (Optional)',
                                labelStyle: TextStyle(color: Colors.white),
                              ),
                              items: [
                                const DropdownMenuItem<String>(
                                  value: null,
                                  child: Text('None'),
                                ),
                                ...masteryProvider.entries.map((entry) {
                                  return DropdownMenuItem<String>(
                                    value: entry.id,
                                    child: Text(entry.title),
                                  );
                                }),
                              ],
                              onChanged: (value) {
                                setState(() {
                                  selectedMasteryId = value;
                                });
                              },
                            ),
                            const SizedBox(height: 8),
                            TextField(
                              controller: masteryValueController,
                              style: const TextStyle(color: Colors.white),
                              decoration: const InputDecoration(
                                labelText:
                                    'Minutes Added Per Completion (Optional)',
                                hintText:
                                    'Enter minutes (e.g., 30 for 30 minutes)',
                                labelStyle: TextStyle(color: Colors.white),
                                hintStyle: TextStyle(color: Colors.white54),
                              ),
                              keyboardType:
                                  const TextInputType.numberWithOptions(
                                    decimal: false,
                                  ),
                              onChanged: (value) {
                                /// Validate input is a positive number
                                final intValue = int.tryParse(value);
                                if (intValue != null && intValue > 0) {
                                  setState(() {
                                    masteryValueController.text = value;
                                  });
                                } else if (value.isNotEmpty) {
                                  /// If invalid input, revert to previous valid value
                                  masteryValueController.text =
                                      masteryValueController.text;
                                }
                              },
                            ),
                          ],
                          if (!isCounterBased) ...[
                            const SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text(
                                  'Subtasks',
                                  style: TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                ElevatedButton(
                                  onPressed: () {
                                    setState(() {
                                      subtasks.add(
                                        MissionSubtask(
                                          name: '',
                                          requiredCompletions: 1,
                                          currentCompletions: 0,
                                          isCounterBased: false,
                                          currentCount: 0,
                                          createdAt: DateTime.now(),
                                        ),
                                      );
                                      targetCount =
                                          -1; // Ensure completion-based toggle is off for new subtask
                                    });
                                  },
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      const Text('Add Subtask'),
                                      const SizedBox(width: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 2,
                                        ),
                                        decoration: BoxDecoration(
                                          color: Colors.blue,
                                          borderRadius: BorderRadius.circular(
                                            12,
                                          ),
                                        ),
                                        child: Text(
                                          '${subtasks.length}',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 12,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            ...subtasks.asMap().entries.map((entry) {
                              final idx = entry.key;
                              final subtask = entry.value;
                              return Card(
                                color: Colors.grey[850],
                                margin: const EdgeInsets.symmetric(vertical: 8),
                                child: Padding(
                                  padding: const EdgeInsets.all(8.0),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      TextFormField(
                                        initialValue: subtask.name,
                                        decoration: const InputDecoration(
                                          labelText: 'Subtask Name',
                                          labelStyle: TextStyle(
                                            color: Colors.white,
                                          ),
                                        ),
                                        style: const TextStyle(
                                          color: Colors.white,
                                        ),
                                        onChanged: (v) {
                                          setState(() {
                                            subtasks[idx] = subtask.copyWith(
                                              name: v,
                                            );
                                          });
                                        },
                                      ),
                                      const SizedBox(height: 8),
                                      CheckboxListTile(
                                        title: const Text(
                                          'Counter Based',
                                          style: TextStyle(color: Colors.white),
                                        ),
                                        value: subtask.isCounterBased,
                                        onChanged: (value) {
                                          if (value != null) {
                                            setState(() {
                                              subtasks[idx] = subtask.copyWith(
                                                isCounterBased: value,
                                                currentCount: 0,
                                                boltColor:
                                                    value &&
                                                            subtask.boltColor ==
                                                                null
                                                        ? _getRandomColor()
                                                        : subtask.boltColor,
                                              );
                                            });
                                          }
                                        },
                                      ),
                                      if (!subtask.isCounterBased) ...[
                                        const SizedBox(height: 8),
                                        TextFormField(
                                          initialValue:
                                              subtask.requiredCompletions
                                                  .toString(),
                                          decoration: const InputDecoration(
                                            labelText: 'Required Completions',
                                            labelStyle: TextStyle(
                                              color: Colors.white,
                                            ),
                                          ),
                                          style: const TextStyle(
                                            color: Colors.white,
                                          ),
                                          keyboardType: TextInputType.number,
                                          onChanged: (v) {
                                            setState(() {
                                              subtasks[idx] = subtask.copyWith(
                                                requiredCompletions:
                                                    int.tryParse(v) ?? 0,
                                              );
                                            });
                                          },
                                        ),
                                      ],
                                      const SizedBox(height: 8),
                                      DropdownButtonFormField<String>(
                                        value: subtask.linkedMasteryId,
                                        dropdownColor: Colors.black,
                                        style: const TextStyle(
                                          color: Colors.white,
                                        ),
                                        decoration: const InputDecoration(
                                          labelText:
                                              'Link to Mastery (Optional)',
                                          labelStyle: TextStyle(
                                            color: Colors.white,
                                          ),
                                        ),
                                        items: [
                                          const DropdownMenuItem<String>(
                                            value: null,
                                            child: Text('None'),
                                          ),
                                          ...masteryProvider.entries.map((
                                            entry,
                                          ) {
                                            return DropdownMenuItem<String>(
                                              value: entry.id,
                                              child: Text(entry.title),
                                            );
                                          }),
                                        ],
                                        onChanged: (value) {
                                          setState(() {
                                            subtasks[idx] = subtask.copyWith(
                                              linkedMasteryId: value,
                                            );
                                          });
                                        },
                                      ),
                                      const SizedBox(height: 8),
                                      Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          const Text(
                                            'Mastery Value:',
                                            style: TextStyle(
                                              color: Colors.white,
                                            ),
                                          ),
                                          Row(
                                            children: [
                                              Expanded(
                                                child: Slider(
                                                  value: subtask.masteryValue
                                                      .clamp(1.0, 100.0),
                                                  min: 1,
                                                  max: 100,
                                                  divisions: 99,
                                                  label: subtask.masteryValue
                                                      .toStringAsFixed(0),
                                                  onChanged: (value) {
                                                    setState(() {
                                                      subtasks[idx] = subtask
                                                          .copyWith(
                                                            masteryValue: value,
                                                          );
                                                    });
                                                  },
                                                ),
                                              ),
                                              const SizedBox(width: 8),
                                              Text(
                                                '${subtask.masteryValue.toStringAsFixed(1)}',
                                                style: TextStyle(
                                                  color: Colors.white,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      Align(
                                        alignment: Alignment.centerRight,
                                        child: IconButton(
                                          icon: const Icon(
                                            Icons.delete,
                                            color: Colors.red,
                                          ),
                                          onPressed: () {
                                            setState(() {
                                              subtasks.removeAt(idx);
                                            });
                                          },
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            }),
                          ],
                        ],
                      ),
                    ),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('Cancel'),
                      ),
                      TextButton(
                        onPressed: () async {
                          if (titleController.text.isNotEmpty &&
                              !missionCreated) {
                            /// Validate mission data before creating
                            if (!validateMissionData(
                              titleController.text,
                              selectedType,
                            )) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Invalid mission data. Please check your inputs.',
                                  ),
                                  backgroundColor: Colors.red,
                                ),
                              );
                              return;
                            }

                            missionCreated = true;
                            final mission = MissionData(
                              id: MissionData.generateUniqueId(),
                              missionId: MissionData.generateUniqueId(),
                              title: titleController.text,
                              description: descriptionController.text,
                              type: selectedType,
                              subtasks:
                                  subtasks
                                      .map(
                                        (subtask) => subtask.copyWith(
                                          boltColor: _getRandomColor(),
                                        ),
                                      )
                                      .toList(),
                              linkedMasteryId: selectedMasteryId,
                              masteryValue:
                                  double.tryParse(
                                    masteryValueController.text,
                                  ) ??
                                  0.0,
                              subtaskMasteryValues: Map.fromEntries(
                                subtasks
                                    .where(
                                      (subtask) =>
                                          subtask.linkedMasteryId != null,
                                    )
                                    .map(
                                      (subtask) => MapEntry(
                                        subtask.name,
                                        subtask.masteryValue,
                                      ),
                                    ),
                              ),
                              isCounterBased: isCounterBased,
                              targetCount: targetCount,
                              notificationId:
                                  missionProvider.aiGuardian
                                      .generateValidNotificationId(),
                              boltColor: _getRandomColor(),
                              timelapseColor: _getRandomColor(),
                              imageUrl: selectedImage,
                              createdAt: DateTime.now(),
                            );

                            /// Validate the complete mission before adding
                            if (!_validateMissionState(mission)) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text(
                                    'Invalid mission configuration',
                                  ),
                                  backgroundColor: Colors.red,
                                ),
                              );
                              return;
                            }

                            /// Add mission and handle any errors
                            try {
                              print('Creating new mission: ${mission.title}');

                              /// Check for existing deleted mission with same title
                              MissionData? existingDeletedMission =
                                  missionProvider.deletedMissions
                                      .where((m) => m.title == mission.title)
                                      .firstOrNull;

                              if (existingDeletedMission != null) {
                                /// Clear any cached data from the deleted mission
                                await _clearMissionCache(
                                  existingDeletedMission.id!,
                                );
                              }

                              missionProvider.addMission(
                                mission,
                                title: titleController.text.trim(),
                                description: descriptionController.text.trim(),
                                type: selectedType,
                                subtasks:
                                    subtasks
                                        .map(
                                          (subtask) => subtask.copyWith(
                                            boltColor: _getRandomColor(),
                                            name: subtask.name.trim(),
                                          ),
                                        )
                                        .toList(),
                                linkedMasteryId: selectedMasteryId,
                                masteryValue:
                                    double.tryParse(
                                      masteryValueController.text,
                                    ) ??
                                    0.0,
                                subtaskMasteryValues: Map.fromEntries(
                                  subtasks
                                      .where(
                                        (subtask) =>
                                            subtask.linkedMasteryId != null,
                                      )
                                      .map(
                                        (subtask) => MapEntry(
                                          subtask.name,
                                          subtask.masteryValue,
                                        ),
                                      ),
                                ),
                                isCounterBased: isCounterBased,
                                targetCount: targetCount,
                                imageUrl: selectedImage,
                              );

                              /// Initialize mission state after creation
                              await _initializeMissionState();
                              print('Mission created successfully');
                              Navigator.of(context).pop(true);
                              /// After mission creation, show the popup in debug mode
                              if (kDebugMode) {
                                _showMissionListPopup(context);
                              }
                            } catch (e) {
                              missionCreated = false;
                              print('Error creating mission: $e');
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text('Error creating mission: $e'),
                                  backgroundColor: Colors.red,
                                ),
                              );
                            }
                          }
                        },
                        child: const Text('Add'),
                      ),
                    ],
                  ),
            ),
      );
    } catch (e, stack) {
      print('Error showing add mission dialog: $e');
      print(stack);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<MissionProvider>(
      builder: (context, missionProvider, child) {
        final activeMissions = missionProvider.missions;
        print('MissionWidget: Building with ${activeMissions.length} missions');

        return Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.black,
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.arrow_back, color: Colors.white),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              /// AI/Robot icon for background activity
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
                        size: 28,
                      ),
                    ),
                  );
                },
              ),
              /// Add science icon button for testing mode
              IconButton(
                icon: Icon(
                  Icons.science,
                  color:
                      missionProvider.isTestingMode
                          ? Colors.green
                          : Colors.white,
                ),
                onPressed: () {
                  missionProvider.toggleTestingMode();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        missionProvider.isTestingMode
                            ? 'Testing mode enabled'
                            : 'Testing mode disabled',
                      ),
                      duration: const Duration(seconds: 2),
                    ),
                  );
                },
              ),
              /// Update refresh button to work in testing mode
              IconButton(
                icon: Icon(
                  Icons.refresh,
                  color: missionProvider.refreshButtonColor,
                ),
                onPressed: () async {
                  try {
                    if (missionProvider.refreshButtonColor == Colors.red ||
                        missionProvider.refreshButtonColor == Colors.orange) {
                      /// Show confirmation dialog before refresh
                      final shouldRefresh = await showDialog<bool>(
                        context: context,
                        builder:
                            (context) => AlertDialog(
                              title: const Text('Refresh Missions'),
                              content: Text(
                                missionProvider.refreshButtonColor == Colors.red
                                    ? 'Are you sure you want to refresh daily missions?'
                                    : 'Are you sure you want to refresh weekly missions? This will also refresh daily missions.',
                              ),
                              actions: [
                                TextButton(
                                  onPressed:
                                      () => Navigator.of(context).pop(false),
                                  child: const Text('Cancel'),
                                ),
                                TextButton(
                                  onPressed:
                                      () => Navigator.of(context).pop(true),
                                  child: const Text('Refresh'),
                                ),
                              ],
                            ),
                      );

                      if (shouldRefresh == true) {
                        await missionProvider.refreshMissions();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                missionProvider.refreshButtonColor == Colors.red
                                    ? 'Daily missions refreshed'
                                    : 'Weekly and daily missions refreshed',
                              ),
                              backgroundColor: Colors.green,
                              duration: const Duration(seconds: 2),
                            ),
                          );
                        }
                      }
                    } else {
                      if (context.mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                              'No missions need refreshing at this time',
                            ),
                            duration: Duration(seconds: 2),
                          ),
                        );
                      }
                    }
                  } catch (e) {
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            'Error refreshing missions: ${e.toString()}',
                          ),
                          backgroundColor: Colors.red,
                          duration: const Duration(seconds: 3),
                        ),
                      );
                    }
                  }
                },
              ),
              /// Add shield icon button with integrated comprehensive cleanup
              Consumer<MissionProvider>(
                builder: (context, missionProvider, child) {
                  final isAIGuardianWorking =
                      missionProvider.isAIGuardianWorking;
                  final iconColor =
                      isAIGuardianWorking ? Colors.green : Colors.grey;

                  return IconButton(
                    icon: Icon(Icons.shield, color: iconColor, size: 32),
                    tooltip:
                        isAIGuardianWorking
                            ? 'AI Guardian: Active - Monitoring & Repairing (Long press for comprehensive cleanup)'
                            : 'AI Guardian: Inactive - Tap to activate (Long press for comprehensive cleanup)',
                    onPressed: () async {
                      final provider = Provider.of<MissionProvider>(
                        context,
                        listen: false,
                      );

                      /// If AI Guardian is not working, try to activate it
                      if (!isAIGuardianWorking) {
                        await provider.activateAIGuardian();
                      }

                      showDialog(
                        context: context,
                        barrierDismissible: false,
                        builder:
                            (context) =>
                                MissionHealthCheckDialog(provider: provider),
                      );
                    },
                    onLongPress: () async {
                      final provider = Provider.of<MissionProvider>(
                        context,
                        listen: false,
                      );

                      /// Show confirmation dialog for comprehensive cleanup
                      final confirmed = await showDialog<bool>(
                        context: context,
                        builder:
                            (context) => AlertDialog(
                              backgroundColor: Colors.black,
                              title: const Text(
                                'Comprehensive Cleanup',
                                style: TextStyle(color: Colors.white),
                              ),
                              content: const Text(
                                'This will perform a deep health check and fix all duplicate IDs, invalid mastery values, and other data issues. Continue?',
                                style: TextStyle(color: Colors.white),
                              ),
                              actions: [
                                TextButton(
                                  onPressed:
                                      () => Navigator.of(context).pop(false),
                                  child: const Text(
                                    'Cancel',
                                    style: TextStyle(color: Colors.grey),
                                  ),
                                ),
                                TextButton(
                                  onPressed:
                                      () => Navigator.of(context).pop(true),
                                  child: const Text(
                                    'Cleanup',
                                    style: TextStyle(color: Colors.orange),
                                  ),
                                ),
                              ],
                            ),
                      );

                      if (confirmed == true) {
                        /// Show progress dialog
                        showDialog(
                          context: context,
                          barrierDismissible: false,
                          builder:
                              (context) => AlertDialog(
                                backgroundColor: Colors.black,
                                title: const Text(
                                  'Comprehensive Cleanup',
                                  style: TextStyle(color: Colors.white),
                                ),
                                content: const Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    CircularProgressIndicator(
                                      color: Colors.orange,
                                    ),
                                    SizedBox(height: 16),
                                    Text(
                                      'Performing deep health check and cleanup...',
                                      style: TextStyle(color: Colors.white),
                                    ),
                                  ],
                                ),
                              ),
                        );

                        /// Perform comprehensive cleanup
                        await provider.performComprehensiveCleanup();

                        /// Close progress dialog
                        if (mounted) {
                          Navigator.of(context).pop();
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Comprehensive cleanup completed!'),
                              backgroundColor: Colors.green,
                              duration: Duration(seconds: 3),
                            ),
                          );
                        }
                      }
                    },
                  );
                },
              ),
            ],
          ),
          body: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Missions',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Row(
                          children: [
                            IconButton(
                              icon: Icon(Icons.sync, color: Colors.white),
                              onPressed: () async {
                                await missionProvider
                                    .validateAllMasteryProgress();
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Mastery progress validated'),
                                    duration: Duration(seconds: 2),
                                  ),
                                );
                              },
                            ),
                            Consumer2<MissionProvider, MasteryProvider>(
                              builder: (
                                context,
                                missionProvider,
                                masteryProvider,
                                child,
                              ) {
                                return IconButton(
                                  icon: const Icon(
                                    Icons.add,
                                    color: Colors.white,
                                  ),
                                  onPressed: () {
                                    _showAddDialog(
                                      context,
                                      missionProvider,
                                      masteryProvider,
                                    );
                                  },
                                );
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                    Text(
                      DateFormat('MMM d, yyyy').format(DateTime.now()),
                      style: TextStyle(color: Colors.grey[400], fontSize: 16),
                    ),
                    const SizedBox(height: 8),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  itemCount: activeMissions.length,
                  itemBuilder: (context, index) {
                    final mission = activeMissions[index];
                    print(
                      'Building mission card at index: $index for mission: ${mission.title}',
                    );
                    print(
                      'Mission details - isCounterBased: ${mission.isCounterBased}, subtasks: ${mission.subtasks.length}',
                    );

                    final counterSubtasks =
                        mission.subtasks
                            .where((s) => s.isCounterBased)
                            .toList();
                    final normalSubtasks =
                        mission.subtasks
                            .where((s) => !s.isCounterBased)
                            .toList();

                    print(
                      'MissionWidget: Mission has ${counterSubtasks.length} counter-based and ${normalSubtasks.length} normal subtasks',
                    );
                    print(
                      'Mission subtasks: ${mission.subtasks.map((s) => '${s.name} (counter: ${s.isCounterBased})').join(', ')}',
                    );

                    for (var subtask in mission.subtasks) {
                      print(
                        'MissionWidget: Subtask ${subtask.name} isCounterBased: ${subtask.isCounterBased}, currentCount: ${subtask.currentCount}, requiredCompletions: ${subtask.requiredCompletions}',
                      );
                    }

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 16.0),
                      child: Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: Stack(
                            children: [
                              Positioned.fill(
                                child: SmartImage(
                                  imagePath: mission.imageUrl,
                                  fit: BoxFit.cover,
                                  width: 800,
                                  height: 400,
                                ),
                              ),
                              Positioned.fill(
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: Colors.black.withOpacity(0.7),
                                  ),
                                ),
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Padding(
                                    padding: const EdgeInsets.all(16.0),
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.spaceBetween,
                                          children: [
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment:
                                                    CrossAxisAlignment.start,
                                                children: [
                                                  Row(
                                                    children: [
                                                      Text(
                                                        mission.title,
                                                        style: const TextStyle(
                                                          color: Colors.white,
                                                          fontSize: 20,
                                                          fontWeight:
                                                              FontWeight.bold,
                                                          shadows: [
                                                            Shadow(
                                                              offset: Offset(
                                                                1,
                                                                1,
                                                              ),
                                                              blurRadius: 3,
                                                              color:
                                                                  Colors.black,
                                                            ),
                                                          ],
                                                        ),
                                                      ),
                                                      if (mission.hasFailed &&
                                                          mission.type !=
                                                              MissionType
                                                                  .simple)
                                                        const Padding(
                                                          padding:
                                                              EdgeInsets.only(
                                                                left: 8.0,
                                                              ),
                                                          child: Icon(
                                                            Icons.flag,
                                                            color: Colors.red,
                                                            size: 20,
                                                          ),
                                                        ),
                                                      /// Exclamation mark for overdue daily or weekly mission
                                                      if ((mission.type ==
                                                                  MissionType
                                                                      .daily ||
                                                              mission.type ==
                                                                  MissionType
                                                                      .weekly) &&
                                                          !mission
                                                              .isCompleted) ...[
                                                        Builder(
                                                          builder: (context) {
                                                            final now =
                                                                DateTime.now();
                                                            DateTime endTime;
                                                            if (mission.type ==
                                                                MissionType
                                                                    .daily) {
                                                              endTime =
                                                                  DateTime(
                                                                    now.year,
                                                                    now.month,
                                                                    now.day,
                                                                    23,
                                                                    59,
                                                                    59,
                                                                  );
                                                            } else {
                                                              /// End of week: Sunday 23:59:59
                                                              final daysUntilSunday =
                                                                  (DateTime
                                                                          .sunday -
                                                                      now.weekday) %
                                                                  7;
                                                              endTime = DateTime(
                                                                now.year,
                                                                now.month,
                                                                now.day +
                                                                    daysUntilSunday,
                                                                23,
                                                                59,
                                                                59,
                                                              );
                                                            }
                                                            if (now.isAfter(
                                                              endTime,
                                                            )) {
                                                              return const Padding(
                                                                padding:
                                                                    EdgeInsets.only(
                                                                      left: 8.0,
                                                                    ),
                                                                child: Icon(
                                                                  Icons.error,
                                                                  color:
                                                                      Colors
                                                                          .orange,
                                                                  size: 20,
                                                                ),
                                                              );
                                                            }
                                                            return const SizedBox.shrink();
                                                          },
                                                        ),
                                                      ],
                                                    ],
                                                  ),
                                                  if (mission.hasFailed &&
                                                      !mission.isCompleted &&
                                                      mission.type !=
                                                          MissionType.simple)
                                                    Padding(
                                                      padding:
                                                          const EdgeInsets.only(
                                                            top: 8.0,
                                                          ),
                                                      child: Text(
                                                        'GET SHIT DONE !!!',
                                                        style: const TextStyle(
                                                          color: Colors.red,
                                                          fontSize: 16,
                                                          fontWeight:
                                                              FontWeight.bold,
                                                          shadows: [
                                                            Shadow(
                                                              offset: Offset(
                                                                1,
                                                                1,
                                                              ),
                                                              blurRadius: 3,
                                                              color:
                                                                  Colors.black,
                                                            ),
                                                          ],
                                                        ),
                                                      ),
                                                    ),
                                                  const SizedBox(height: 4),
                                                  Text(
                                                    mission.type ==
                                                            MissionType.daily
                                                        ? 'Daily Mission'
                                                        : mission.type ==
                                                            MissionType.weekly
                                                        ? 'Weekly Mission'
                                                        : 'Simple Mission',
                                                    style: TextStyle(
                                                      color: Colors.white
                                                          .withAlpha(230),
                                                      fontSize: 14,
                                                      shadows: const [
                                                        Shadow(
                                                          offset: Offset(1, 1),
                                                          blurRadius: 3,
                                                          color: Colors.black,
                                                        ),
                                                      ],
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                            Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.end,
                                              children: [
                                                IconButton(
                                                  icon: const Icon(
                                                    Icons.edit,
                                                    color: Colors.white,
                                                  ),
                                                  onPressed: () {
                                                    final missionProvider =
                                                        Provider.of<
                                                          MissionProvider
                                                        >(
                                                          context,
                                                          listen: false,
                                                        );
                                                    final masteryProvider =
                                                        Provider.of<
                                                          MasteryProvider
                                                        >(
                                                          context,
                                                          listen: false,
                                                        );
                                                    if (missionProvider
                                                            .isDailyLocked ||
                                                        missionProvider
                                                            .isWeeklyLocked) {
                                                      ScaffoldMessenger.of(
                                                        context,
                                                      ).showSnackBar(
                                                        const SnackBar(
                                                          content: Text(
                                                            'Missions are locked. Please refresh to unlock.',
                                                          ),
                                                          duration: Duration(
                                                            seconds: 2,
                                                          ),
                                                        ),
                                                      );
                                                      return;
                                                    }
                                                    _showEditMissionDialog(
                                                      context,
                                                      missionProvider,
                                                      masteryProvider,
                                                      mission,
                                                    );
                                                  },
                                                ),
                                                IconButton(
                                                  icon: const Icon(
                                                    Icons.delete,
                                                    color: Colors.red,
                                                  ),
                                                  onPressed: () {
                                                    final missionProvider =
                                                        Provider.of<
                                                          MissionProvider
                                                        >(
                                                          context,
                                                          listen: false,
                                                        );
                                                    if (missionProvider
                                                            .isDailyLocked ||
                                                        missionProvider
                                                            .isWeeklyLocked) {
                                                      ScaffoldMessenger.of(
                                                        context,
                                                      ).showSnackBar(
                                                        const SnackBar(
                                                          content: Text(
                                                            'Missions are locked. Please refresh to unlock.',
                                                          ),
                                                          duration: Duration(
                                                            seconds: 2,
                                                          ),
                                                        ),
                                                      );
                                                      return;
                                                    }
                                                    _showDeleteConfirmationDialog(
                                                      context,
                                                      missionProvider,
                                                      mission,
                                                    );
                                                  },
                                                ),
                                              ],
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        Text(
                                          mission.description,
                                          style: TextStyle(
                                            color: Colors.white.withAlpha(230),
                                            fontSize: 16,
                                            shadows: const [
                                              Shadow(
                                                offset: Offset(1, 1),
                                                blurRadius: 3,
                                                color: Colors.black,
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        /// Always show the progress bar for normal subtasks if any exist
                                        if (normalSubtasks.isNotEmpty) ...[
                                          Builder(
                                            builder: (context) {
                                              final totalCompletions =
                                                  normalSubtasks.fold<int>(
                                                    0,
                                                    (sum, s) =>
                                                        sum +
                                                        s.currentCompletions,
                                                  );
                                              final totalRequired =
                                                  normalSubtasks.fold<int>(
                                                    0,
                                                    (sum, s) =>
                                                        sum +
                                                        s.requiredCompletions,
                                                  );
                                              final progress =
                                                  (totalRequired == 0)
                                                      ? 0.0
                                                      : totalCompletions /
                                                          totalRequired;
                                              return Column(
                                                children: [
                                                  Row(
                                                    children: [
                                                      Expanded(
                                                        child: LinearProgressIndicator(
                                                          value: progress,
                                                          backgroundColor:
                                                              Colors.grey[800],
                                                          valueColor:
                                                              AlwaysStoppedAnimation<
                                                                Color
                                                              >(Colors.white),
                                                        ),
                                                      ),
                                                    ],
                                                  ),
                                                  Padding(
                                                    padding:
                                                        const EdgeInsets.only(
                                                          top: 4.0,
                                                          bottom: 8.0,
                                                        ),
                                                    child: Center(
                                                      child: Text(
                                                        '${(progress * 100).toInt()}%',
                                                        style: TextStyle(
                                                          color: Colors.white,
                                                          fontSize: 18,
                                                          fontWeight:
                                                              FontWeight.bold,
                                                          shadows: [
                                                            Shadow(
                                                              blurRadius: 2,
                                                              color: Colors
                                                                  .black
                                                                  .withOpacity(
                                                                    0.5,
                                                                  ),
                                                              offset: Offset(
                                                                1,
                                                                1,
                                                              ),
                                                            ),
                                                          ],
                                                        ),
                                                      ),
                                                    ),
                                                  ),
                                                ],
                                              );
                                            },
                                          ),
                                          /// Show each normal subtask as a tappable row
                                          ...normalSubtasks.map((subtask) {
                                            /// Find the actual index in the full mission's subtasks list
                                            final fullIndex = mission.subtasks
                                                .indexWhere(
                                                  (s) =>
                                                      s.name == subtask.name &&
                                                      s.requiredCompletions ==
                                                          subtask
                                                              .requiredCompletions &&
                                                      s.isCounterBased ==
                                                          subtask
                                                              .isCounterBased,
                                                );
                                            final progress =
                                                subtask.requiredCompletions == 0
                                                    ? (subtask.currentCompletions >
                                                            0
                                                        ? 1.0
                                                        : 0.0)
                                                    : subtask
                                                            .currentCompletions /
                                                        subtask
                                                            .requiredCompletions;
                                            return Padding(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    vertical: 4.0,
                                                  ),
                                              child: Row(
                                                children: [
                                                  SizedBox(
                                                    width: 20,
                                                    height: 20,
                                                    child: CircularProgressIndicator(
                                                      value: progress,
                                                      strokeWidth: 2,
                                                      backgroundColor: (subtask
                                                                  .boltColor ??
                                                              Colors.blue)
                                                          .withOpacity(0.2),
                                                      valueColor:
                                                          AlwaysStoppedAnimation<
                                                            Color
                                                          >(
                                                            subtask.boltColor ??
                                                                Colors.blue,
                                                          ),
                                                    ),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Expanded(
                                                    child: Text(
                                                      subtask.name,
                                                      style: const TextStyle(
                                                        color: Colors.white,
                                                      ),
                                                    ),
                                                  ),
                                                  _buildSubtaskCounter(
                                                    context,
                                                    mission,
                                                    subtask,
                                                    fullIndex,
                                                  ),
                                                  if (subtask.masteryValue >
                                                      0) ...[
                                                    const SizedBox(width: 8),
                                                    Text(
                                                      '+${subtask.masteryValue.toStringAsFixed(1)}',
                                                      style: TextStyle(
                                                        color:
                                                            subtask.boltColor ??
                                                            Colors.blue,
                                                        fontSize: 13,
                                                        fontWeight:
                                                            FontWeight.w500,
                                                      ),
                                                    ),
                                                  ],
                                                ],
                                              ),
                                            );
                                          }).toList(),
                                        ],
                                        /// Add increment button for counter-based missions with no subtasks
                                        if (mission.isCounterBased &&
                                            mission.subtasks.isEmpty) ...[
                                          Padding(
                                            padding: const EdgeInsets.symmetric(
                                              vertical: 4.0,
                                            ),
                                            child: GestureDetector(
                                              onTap: () async {
                                                final missionProvider =
                                                    Provider.of<
                                                      MissionProvider
                                                    >(context, listen: false);
                                                if (missionProvider
                                                        .isDailyLocked ||
                                                    missionProvider
                                                        .isWeeklyLocked) {
                                                  ScaffoldMessenger.of(
                                                    context,
                                                  ).showSnackBar(
                                                    const SnackBar(
                                                      content: Text(
                                                        'Missions are locked. Please refresh to unlock.',
                                                      ),
                                                      duration: Duration(
                                                        seconds: 2,
                                                      ),
                                                    ),
                                                  );
                                                  return;
                                                }
                                                /// Find the exact mission in the provider's list
                                                final missionIndex =
                                                    missionProvider.missions
                                                        .indexWhere(
                                                          (m) =>
                                                              m.notificationId ==
                                                              mission
                                                                  .notificationId,
                                                        );
                                                if (missionIndex == -1) {
                                                  print(
                                                    'Error: Mission not found in provider list',
                                                  );
                                                  return;
                                                }
                                                /// Get the current mission from the provider
                                                final currentMission =
                                                    missionProvider
                                                        .missions[missionIndex];
                                                /// Increment counter mission
                                                final updatedMission =
                                                    currentMission.copyWith(
                                                      currentCount:
                                                          currentMission
                                                              .currentCount +
                                                          1,
                                                      hasFailed: false,
                                                    );
                                                /// Update through provider
                                                await missionProvider
                                                    .editMission(
                                                      currentMission,
                                                      updatedMission,
                                                    );
                                                /// Add mastery progress if linked
                                                if (currentMission
                                                            .linkedMasteryId !=
                                                        null &&
                                                    currentMission
                                                            .masteryValue >
                                                        0) {
                                                  final masteryProvider =
                                                      Provider.of<
                                                        MasteryProvider
                                                      >(context, listen: false);
                                                  await masteryProvider.addProgress(
                                                    currentMission
                                                        .linkedMasteryId!,
                                                    'Mission: ${currentMission.title}',
                                                    currentMission.masteryValue,
                                                  );
                                                }
                                              },
                                              child: Row(
                                                children: [
                                                  Icon(
                                                    Icons.cyclone,
                                                    color:
                                                        mission.hasFailed
                                                            ? Colors.red
                                                            : mission
                                                                    .boltColor ??
                                                                _getRandomColor(),
                                                    size: 21,
                                                  ),
                                                  const SizedBox(width: 8),
                                                  Expanded(
                                                    child: Text(
                                                      'Count',
                                                      style: const TextStyle(
                                                        color: Colors.white,
                                                      ),
                                                    ),
                                                  ),
                                                  Container(
                                                    padding:
                                                        const EdgeInsets.symmetric(
                                                          horizontal: 12.6,
                                                          vertical: 4.2,
                                                        ),
                                                    decoration: BoxDecoration(
                                                      color: (mission
                                                                  .boltColor ??
                                                              Colors.blue)
                                                          .withAlpha(51),
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                            8,
                                                          ),
                                                      border: Border.all(
                                                        color:
                                                            mission.boltColor ??
                                                            Colors.blue,
                                                        width: 1,
                                                      ),
                                                    ),
                                                    child: Text(
                                                      '${mission.currentCount}',
                                                      style: TextStyle(
                                                        color:
                                                            mission.boltColor ??
                                                            Colors.blue,
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        fontSize: 15.75,
                                                      ),
                                                    ),
                                                  ),
                                                  if (mission.masteryValue >
                                                      0) ...[
                                                    const SizedBox(width: 8),
                                                    Text(
                                                      '+${mission.masteryValue.toStringAsFixed(1)}',
                                                      style: TextStyle(
                                                        color:
                                                            mission.boltColor ??
                                                            Colors.blue,
                                                        fontSize: 13,
                                                        fontWeight:
                                                            FontWeight.w500,
                                                      ),
                                                    ),
                                                  ],
                                                ],
                                              ),
                                            ),
                                          ),
                                        ],
                                        /// Show completion progress for completion-based missions without subtasks
                                        if (!mission.isCounterBased &&
                                            mission.subtasks.isEmpty) ...[
                                          if (mission.isCompleted) ...[
                                            Padding(
                                              padding: const EdgeInsets.all(
                                                16.0,
                                              ),
                                              child: Container(
                                                padding: const EdgeInsets.all(
                                                  12.0,
                                                ),
                                                decoration: BoxDecoration(
                                                  color: Colors.green
                                                      .withOpacity(0.2),
                                                  borderRadius:
                                                      BorderRadius.circular(12),
                                                ),
                                                child: Row(
                                                  mainAxisAlignment:
                                                      MainAxisAlignment.center,
                                                  children: const [
                                                    Icon(
                                                      Icons.check_circle,
                                                      color: Colors.green,
                                                    ),
                                                    SizedBox(width: 8),
                                                    Text(
                                                      'Mission Complete',
                                                      style: TextStyle(
                                                        color: Colors.green,
                                                        fontSize: 16,
                                                        fontWeight:
                                                            FontWeight.bold,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ] else ...[
                                            Builder(
                                              builder: (context) {
                                                final progress =
                                                    mission.targetCount == 0
                                                        ? (mission.currentCount >
                                                                0
                                                            ? 1.0
                                                            : 0.0)
                                                        : mission.currentCount /
                                                            mission.targetCount;
                                                return Column(
                                                  children: [
                                                    GestureDetector(
                                                      onTap: () async {
                                                        if (missionProvider
                                                                .isDailyLocked ||
                                                            missionProvider
                                                                .isWeeklyLocked) {
                                                          ScaffoldMessenger.of(
                                                            context,
                                                          ).showSnackBar(
                                                            const SnackBar(
                                                              content: Text(
                                                                'Missions are locked. Please refresh to unlock.',
                                                              ),
                                                              duration:
                                                                  Duration(
                                                                    seconds: 2,
                                                                  ),
                                                            ),
                                                          );
                                                          return;
                                                        }
                                                        if (!mission
                                                            .isCompleted) {
                                                          final updatedMission = mission.copyWith(
                                                            currentCount:
                                                                mission
                                                                    .currentCount +
                                                                1,
                                                            isCompleted:
                                                                mission.targetCount >
                                                                    0 &&
                                                                mission.currentCount +
                                                                        1 >=
                                                                    mission
                                                                        .targetCount,
                                                            lastCompleted:
                                                                mission.targetCount >
                                                                            0 &&
                                                                        mission.currentCount +
                                                                                1 >=
                                                                            mission.targetCount
                                                                    ? DateTime.now()
                                                                    : null,
                                                            hasFailed: false,
                                                          );
                                                          await missionProvider
                                                              .editMission(
                                                                mission,
                                                                updatedMission,
                                                              );
                                                          /// Add mastery progress if linked
                                                          if (updatedMission
                                                                      .linkedMasteryId !=
                                                                  null &&
                                                              updatedMission
                                                                      .masteryValue >
                                                                  0) {
                                                            final masteryProvider =
                                                                Provider.of<
                                                                  MasteryProvider
                                                                >(
                                                                  context,
                                                                  listen: false,
                                                                );
                                                            await masteryProvider
                                                                .addProgress(
                                                                  updatedMission
                                                                      .linkedMasteryId!,
                                                                  'Mission: ${updatedMission.title}',
                                                                  updatedMission
                                                                      .masteryValue,
                                                                );
                                                          }
                                                        }
                                                      },
                                                      child: Padding(
                                                        padding:
                                                            const EdgeInsets.symmetric(
                                                              vertical: 4.0,
                                                            ),
                                                        child: Row(
                                                          children: [
                                                            SizedBox(
                                                              width: 20,
                                                              height: 20,
                                                              child: CircularProgressIndicator(
                                                                value: progress,
                                                                strokeWidth: 2,
                                                                backgroundColor: (mission
                                                                            .boltColor ??
                                                                        Colors
                                                                            .blue)
                                                                    .withOpacity(
                                                                      0.2,
                                                                    ),
                                                                valueColor: AlwaysStoppedAnimation<
                                                                  Color
                                                                >(
                                                                  mission.boltColor ??
                                                                      Colors
                                                                          .blue,
                                                                ),
                                                              ),
                                                            ),
                                                            const SizedBox(
                                                              width: 8,
                                                            ),
                                                            Expanded(
                                                              child: Text(
                                                                mission.title,
                                                                style: const TextStyle(
                                                                  color:
                                                                      Colors
                                                                          .white,
                                                                ),
                                                              ),
                                                            ),
                                                            Container(
                                                              padding:
                                                                  const EdgeInsets.symmetric(
                                                                    horizontal:
                                                                        12.6,
                                                                    vertical:
                                                                        4.2,
                                                                  ),
                                                              decoration: BoxDecoration(
                                                                color: (mission
                                                                            .boltColor ??
                                                                        Colors
                                                                            .blue)
                                                                    .withAlpha(
                                                                      51,
                                                                    ),
                                                                borderRadius:
                                                                    BorderRadius.circular(
                                                                      8,
                                                                    ),
                                                                border: Border.all(
                                                                  color:
                                                                      mission
                                                                          .boltColor ??
                                                                      Colors
                                                                          .blue,
                                                                  width: 1,
                                                                ),
                                                              ),
                                                              child: Text(
                                                                mission.targetCount ==
                                                                        0
                                                                    ? '${mission.currentCount}'
                                                                    : '${mission.currentCount}',
                                                                style: TextStyle(
                                                                  color:
                                                                      mission
                                                                          .boltColor ??
                                                                      Colors
                                                                          .blue,
                                                                  fontWeight:
                                                                      FontWeight
                                                                          .bold,
                                                                  fontSize:
                                                                      15.75,
                                                                ),
                                                              ),
                                                            ),
                                                          ],
                                                        ),
                                                      ),
                                                    ),
                                                  ],
                                                );
                                              },
                                            ),
                                          ],
                                        ],
                                      ],
                                    ),
                                  ),
                                  if (counterSubtasks.isNotEmpty) ...[
                                    ...counterSubtasks.map((subtask) {
                                      /// Find the actual index in the full mission's subtasks list
                                      final fullIndex = mission.subtasks
                                          .indexWhere(
                                            (s) =>
                                                s.name == subtask.name &&
                                                s.requiredCompletions ==
                                                    subtask
                                                        .requiredCompletions &&
                                                s.isCounterBased ==
                                                    subtask.isCounterBased,
                                          );
                                      print(
                                        'Building counter for subtask: ${subtask.name} at index: $fullIndex',
                                      );
                                      return Padding(
                                        padding: const EdgeInsets.symmetric(
                                          vertical: 4.0,
                                          horizontal: 16.0,
                                        ),
                                        child: Row(
                                          children: [
                                            Icon(
                                              Icons.bolt,
                                              color:
                                                  subtask.boltColor ??
                                                  Colors.blue,
                                              size: 21,
                                            ),
                                            const SizedBox(width: 8),
                                            Expanded(
                                              child: Text(
                                                subtask.name,
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                  fontSize: 15.75,
                                                ),
                                              ),
                                            ),
                                            _buildSubtaskCounter(
                                              context,
                                              mission,
                                              subtask,
                                              fullIndex,
                                            ),
                                          ],
                                        ),
                                      );
                                    }).toList(),
                                  ],
                                  if (!mission.isCounterBased &&
                                      normalSubtasks.isNotEmpty &&
                                      normalSubtasks.every(
                                        (s) => s.isCompleted,
                                      ) &&
                                      (counterSubtasks.isEmpty ||
                                          counterSubtasks.every(
                                            (s) => s.currentCount > 0,
                                          ))) ...[
                                    /// Show Complete Mission button
                                    Padding(
                                      padding: const EdgeInsets.all(16.0),
                                      child: GestureDetector(
                                        onTap: () async {
                                          final missionProvider =
                                              Provider.of<MissionProvider>(
                                                context,
                                                listen: false,
                                              );
                                          if (missionProvider.isDailyLocked ||
                                              missionProvider.isWeeklyLocked) {
                                            ScaffoldMessenger.of(
                                              context,
                                            ).showSnackBar(
                                              const SnackBar(
                                                content: Text(
                                                  'Missions are locked. Please refresh to unlock.',
                                                ),
                                                duration: Duration(seconds: 2),
                                              ),
                                            );
                                            return;
                                          }
                                          if (!mission.isCompleted) {
                                            await missionProvider
                                                .completeMission(mission);
                                            /// Get the updated mission from the provider
                                            final updatedMission =
                                                missionProvider.missions
                                                    .firstWhere(
                                                      (m) =>
                                                          m.notificationId ==
                                                          mission
                                                              .notificationId,
                                                      orElse: () => mission,
                                                    );
                                            /// Add mastery progress if linked
                                            if (updatedMission
                                                        .linkedMasteryId !=
                                                    null &&
                                                updatedMission.masteryValue >
                                                    0) {
                                              final masteryProvider =
                                                  Provider.of<MasteryProvider>(
                                                    context,
                                                    listen: false,
                                                  );
                                              await masteryProvider.addProgress(
                                                updatedMission.linkedMasteryId!,
                                                'Mission: ${updatedMission.title}',
                                                updatedMission.masteryValue,
                                              );
                                            }
                                          }
                                        },
                                        child: Container(
                                          padding: const EdgeInsets.all(12.0),
                                          decoration: BoxDecoration(
                                            color: Colors.green.withOpacity(
                                              0.2,
                                            ),
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                          ),
                                          child: Row(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            children: [
                                              Icon(
                                                Icons.check_circle,
                                                color: Colors.green,
                                              ),
                                              const SizedBox(width: 8),
                                              Text(
                                                'Mission Completed',
                                                style: TextStyle(
                                                  color: Colors.green,
                                                  fontSize: 16,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ),
                                  ],
                                  /// Show warning for overdue missions with no counters or incomplete subtasks
                                  if (((!mission.isCounterBased &&
                                              mission.subtasks.isEmpty) ||
                                          (mission.subtasks.isNotEmpty &&
                                              mission.subtasks.any(
                                                (s) =>
                                                    !s.isCounterBased &&
                                                    s.currentCompletions <
                                                        s.requiredCompletions,
                                              ))) &&
                                      !mission.isCompleted &&
                                      ((mission.type == MissionType.daily &&
                                              DateTime.now().isAfter(
                                                DateTime(
                                                  DateTime.now().year,
                                                  DateTime.now().month,
                                                  DateTime.now().day,
                                                  23,
                                                  59,
                                                  59,
                                                ),
                                              )) ||
                                          (mission.type == MissionType.weekly &&
                                              DateTime.now().weekday ==
                                                  DateTime.sunday &&
                                              DateTime.now().hour >= 23 &&
                                              DateTime.now().minute >=
                                                  59))) ...[
                                    Padding(
                                      padding: const EdgeInsets.all(16.0),
                                      child: Row(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: const [
                                          Text(
                                            '⚠️ GET SHIT DONE !!',
                                            style: TextStyle(
                                              color: Colors.red,
                                              fontSize: 18,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                  /// Show UI for simple missions (MissionType.simple, no counter, no completion, no subtasks)
                                  if (mission.type == MissionType.simple &&
                                      !mission.isCounterBased &&
                                      mission.targetCount == 0 &&
                                      mission.subtasks.isEmpty) ...[
                                    if (mission.isCompleted) ...[
                                      Padding(
                                        padding: const EdgeInsets.all(16.0),
                                        child: Container(
                                          padding: const EdgeInsets.all(12.0),
                                          decoration: BoxDecoration(
                                            color: Colors.green.withOpacity(
                                              0.2,
                                            ),
                                            borderRadius: BorderRadius.circular(
                                              12,
                                            ),
                                          ),
                                          child: Row(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            children: const [
                                              Icon(
                                                Icons.check_circle,
                                                color: Colors.green,
                                              ),
                                              SizedBox(width: 8),
                                              Text(
                                                'Mission Complete',
                                                style: TextStyle(
                                                  color: Colors.green,
                                                  fontSize: 16,
                                                  fontWeight: FontWeight.bold,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ] else ...[
                                      Padding(
                                        padding: const EdgeInsets.all(16.0),
                                        child: GestureDetector(
                                          onTap: () async {
                                            if (missionProvider.isDailyLocked ||
                                                missionProvider
                                                    .isWeeklyLocked) {
                                              ScaffoldMessenger.of(
                                                context,
                                              ).showSnackBar(
                                                const SnackBar(
                                                  content: Text(
                                                    'Missions are locked. Please refresh to unlock.',
                                                  ),
                                                  duration: Duration(
                                                    seconds: 2,
                                                  ),
                                                ),
                                              );
                                              return;
                                            }
                                            if (!mission.isCompleted) {
                                              await missionProvider
                                                  .completeMission(mission);
                                              /// Add mastery progress if linked
                                              final updatedMission =
                                                  missionProvider.missions
                                                      .firstWhere(
                                                        (m) =>
                                                            m.notificationId ==
                                                            mission
                                                                .notificationId,
                                                        orElse: () => mission,
                                                      );
                                              if (updatedMission
                                                          .linkedMasteryId !=
                                                      null &&
                                                  updatedMission.masteryValue >
                                                      0) {
                                                final masteryProvider =
                                                    Provider.of<
                                                      MasteryProvider
                                                    >(context, listen: false);
                                                /// Add mastery value for each completion
                                                await masteryProvider.addProgress(
                                                  updatedMission
                                                      .linkedMasteryId!,
                                                  'Mission: ${updatedMission.title}',
                                                  updatedMission.masteryValue,
                                                );
                                              }
                                            }
                                          },
                                          child: Container(
                                            padding: const EdgeInsets.all(12.0),
                                            decoration: BoxDecoration(
                                              color: Colors.green.withOpacity(
                                                0.2,
                                              ),
                                              borderRadius:
                                                  BorderRadius.circular(12),
                                            ),
                                            child: Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment.center,
                                              children: const [
                                                Icon(
                                                  Icons.check_circle_outline,
                                                  color: Colors.green,
                                                ),
                                                SizedBox(width: 8),
                                                Text(
                                                  'Complete Mission',
                                                  style: TextStyle(
                                                    color: Colors.green,
                                                    fontSize: 16,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ],
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _showEditMissionDialog(
    BuildContext context,
    MissionProvider provider,
    MasteryProvider masteryProvider,
    MissionData mission,
  ) {
    final titleController = TextEditingController(text: mission.title);
    final descriptionController = TextEditingController(
      text: mission.description,
    );
    MissionType selectedType = mission.type;
    String? selectedMasteryId = mission.linkedMasteryId;
    final masteryValueController = TextEditingController(
      text: mission.masteryValue.toStringAsFixed(0),
    );
    List<MissionSubtask> subtasks = List<MissionSubtask>.from(mission.subtasks);
    bool isCounterBased = mission.isCounterBased;
    int counterValue = mission.currentCount;
    String selectedImage = mission.imageUrl;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: Colors.black,
              title: const Text(
                'Edit Mission',
                style: TextStyle(color: Colors.white),
              ),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    /// Image selector: scrollable picker
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          height: 150,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: Stack(
                              children: [
                                Positioned.fill(
                                  child: SmartImage(
                                    imagePath: selectedImage,
                                    fit: BoxFit.cover,
                                    width: 800,
                                    height: 400,
                                  ),
                                ),
                                Positioned.fill(
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: Colors.black.withOpacity(0.5),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(
                              child: SizedBox(
                                height: 70,
                                child: ListView.separated(
                                  scrollDirection: Axis.horizontal,
                                  itemCount: _entryManager.imageList.length,
                                  separatorBuilder:
                                      (context, idx) =>
                                          const SizedBox(width: 8),
                                  itemBuilder: (context, idx) {
                                    final imgPath =
                                        _entryManager.imageList[idx];
                                    return GestureDetector(
                                      onTap: () {
                                        setState(() {
                                          selectedImage = imgPath;
                                        });
                                      },
                                      child: Container(
                                        decoration: BoxDecoration(
                                          border: Border.all(
                                            color:
                                                selectedImage == imgPath
                                                    ? Colors.amber
                                                    : Colors.transparent,
                                            width: 3,
                                          ),
                                          borderRadius: BorderRadius.circular(
                                            8,
                                          ),
                                        ),
                                        child: ClipRRect(
                                          borderRadius: BorderRadius.circular(
                                            8,
                                          ),
                                          child: SmartImage(
                                            imagePath: imgPath,
                                            width: 70,
                                            height: 70,
                                            fit: BoxFit.cover,
                                          ),
                                        ),
                                      ),
                                    );
                                  },
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            /// Add Image button
                            GestureDetector(
                              onTap: _pickImage,
                              child: Container(
                                width: 70,
                                height: 70,
                                decoration: BoxDecoration(
                                  border: Border.all(
                                    color: Colors.blue,
                                    width: 2,
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                  color: Colors.blue.withOpacity(0.1),
                                ),
                                child: const Icon(
                                  Icons.add_photo_alternate,
                                  color: Colors.blue,
                                  size: 32,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: 'Title',
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      style: const TextStyle(color: Colors.white),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: descriptionController,
                      decoration: const InputDecoration(
                        labelText: 'Description (Optional)',
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      style: const TextStyle(color: Colors.white),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<MissionType>(
                      value: selectedType,
                      dropdownColor: Colors.black,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: 'Mission Type',
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      items:
                          MissionType.values.map((type) {
                            String displayName =
                                type.toString().split('.').last;
                            displayName =
                                displayName[0].toUpperCase() +
                                displayName
                                    .substring(1)
                                    .replaceAllMapped(
                                      RegExp(r'([A-Z])'),
                                      (match) => ' ${match.group(1)}',
                                    );
                            return DropdownMenuItem<MissionType>(
                              value: type,
                              child: Text(displayName),
                            );
                          }).toList(),
                      onChanged: (value) {
                        if (value != null) {
                          setState(() {
                            selectedType = value;
                          });
                        }
                      },
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: selectedMasteryId,
                      dropdownColor: Colors.black,
                      style: const TextStyle(color: Colors.white),
                      decoration: const InputDecoration(
                        labelText: 'Link to Mastery (Optional)',
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      items: [
                        const DropdownMenuItem<String>(
                          value: null,
                          child: Text('None'),
                        ),
                        ...masteryProvider.entries.map((entry) {
                          return DropdownMenuItem<String>(
                            value: entry.id,
                            child: Text(entry.title),
                          );
                        }),
                      ],
                      onChanged: (value) {
                        setState(() {
                          selectedMasteryId = value;
                        });
                      },
                    ),
                    const SizedBox(height: 8),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Mastery Value:',
                          style: TextStyle(color: Colors.white),
                        ),
                        Row(
                          children: [
                            Expanded(
                              child: Slider(
                                value:
                                    double.tryParse(
                                      masteryValueController.text,
                                    ) ??
                                    1.0,
                                min: 1,
                                max: 100,
                                divisions: 99,
                                label: (double.tryParse(
                                          masteryValueController.text,
                                        ) ??
                                        1.0)
                                    .toStringAsFixed(0),
                                onChanged: (value) {
                                  setState(() {
                                    masteryValueController.text = value
                                        .toStringAsFixed(0);
                                  });
                                },
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '${masteryValueController.text}',
                              style: TextStyle(color: Colors.white),
                            ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    SwitchListTile(
                      value: isCounterBased,
                      onChanged: (value) {
                        setState(() {
                          isCounterBased = value;
                          if (isCounterBased) {
                            subtasks = [];
                          } else {
                            counterValue = 0;
                          }
                        });
                      },
                      title: const Text(
                        'Counter-based Mission',
                        style: TextStyle(color: Colors.white),
                      ),
                      activeColor: Colors.blue,
                    ),
                    if (isCounterBased) ...[
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          const Text(
                            'Target Count:',
                            style: TextStyle(color: Colors.white),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: TextFormField(
                              initialValue: counterValue.toString(),
                              style: const TextStyle(color: Colors.white),
                              keyboardType: TextInputType.number,
                              onChanged: (value) {
                                final newValue = int.tryParse(value);
                                if (newValue != null) {
                                  setState(() {
                                    counterValue = newValue > 0 ? newValue : 0;
                                  });
                                }
                              },
                            ),
                          ),
                        ],
                      ),
                    ],
                    if (!isCounterBased) ...[
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Subtasks',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          ElevatedButton(
                            onPressed: () {
                              setState(() {
                                subtasks.add(
                                  MissionSubtask(
                                    name: '',
                                    requiredCompletions: 1,
                                    currentCompletions: 0,
                                    isCounterBased: false,
                                    currentCount: 0,
                                    createdAt: DateTime.now(),
                                  ),
                                );
                              });
                            },
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Text('Add Subtask'),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.blue,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    '${subtasks.length}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      ...subtasks.asMap().entries.map((entry) {
                        final idx = entry.key;
                        final subtask = entry.value;
                        return Card(
                          color: Colors.grey[850],
                          margin: const EdgeInsets.symmetric(vertical: 8),
                          child: Padding(
                            padding: const EdgeInsets.all(8.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                TextFormField(
                                  initialValue: subtask.name,
                                  style: const TextStyle(color: Colors.white),
                                  decoration: const InputDecoration(
                                    labelText: 'Subtask Name',
                                    labelStyle: TextStyle(color: Colors.white),
                                  ),
                                  onChanged: (value) {
                                    setState(() {
                                      subtasks[idx] = subtask.copyWith(
                                        name: value,
                                      );
                                    });
                                  },
                                ),
                                const SizedBox(height: 8),
                                Row(
                                  children: [
                                    const Text(
                                      'Required Completions:',
                                      style: TextStyle(color: Colors.white),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: TextFormField(
                                        initialValue:
                                            subtask.requiredCompletions
                                                .toString(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                        ),
                                        keyboardType: TextInputType.number,
                                        onChanged: (value) {
                                          final newValue = int.tryParse(value);
                                          if (newValue != null) {
                                            setState(() {
                                              subtasks[idx] = subtask.copyWith(
                                                requiredCompletions:
                                                    newValue > 0 ? newValue : 1,
                                              );
                                            });
                                          }
                                        },
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Mastery Value:',
                                      style: TextStyle(color: Colors.white),
                                    ),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Slider(
                                            value: subtask.masteryValue.clamp(
                                              1.0,
                                              100.0,
                                            ),
                                            min: 1,
                                            max: 100,
                                            divisions: 99,
                                            label: subtask.masteryValue
                                                .toStringAsFixed(0),
                                            onChanged: (value) {
                                              setState(() {
                                                subtasks[idx] = subtask
                                                    .copyWith(
                                                      masteryValue: value,
                                                    );
                                              });
                                            },
                                          ),
                                        ),
                                        const SizedBox(width: 8),
                                        Text(
                                          '${subtask.masteryValue.toStringAsFixed(1)}',
                                          style: TextStyle(color: Colors.white),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.end,
                                  children: [
                                    IconButton(
                                      icon: const Icon(
                                        Icons.delete,
                                        color: Colors.red,
                                      ),
                                      onPressed: () {
                                        setState(() {
                                          subtasks.removeAt(idx);
                                        });
                                      },
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                    ],
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () {
                          final masteryValue =
                              double.tryParse(masteryValueController.text) ??
                              1.0;
                          final Map<String, double> subtaskMasteryValues = {};
                          for (final subtask in subtasks) {
                            if (subtask.linkedMasteryId != null) {
                              subtaskMasteryValues[subtask.name] =
                                  subtask.masteryValue;
                            }
                          }
                          final updatedMission = mission.copyWith(
                            title: titleController.text,
                            description: descriptionController.text,
                            type: selectedType,
                            subtasks: List<MissionSubtask>.from(subtasks),
                            isCounterBased: isCounterBased,
                            currentCount: isCounterBased ? counterValue : 0,
                            targetCount:
                                isCounterBased
                                    ? (counterValue > 0 ? counterValue : 1)
                                    : 0,
                            masteryValue: masteryValue,
                            subtaskMasteryValues: subtaskMasteryValues,
                            imageUrl: selectedImage,
                            linkedMasteryId: selectedMasteryId,
                            /// Always preserve these:
                            id: mission.id,
                            notificationId: mission.notificationId,
                            createdAt: mission.createdAt,
                            lastCompleted: mission.lastCompleted,
                            hasFailed: mission.hasFailed,
                            boltColor: mission.boltColor,
                            timelapseColor: mission.timelapseColor,
                          );
                          provider.editMission(mission, updatedMission);
                          Navigator.pop(context);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: const Text(
                          'Update Mission',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  void _showDeleteConfirmationDialog(
    BuildContext context,
    MissionProvider provider,
    MissionData mission,
  ) {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            backgroundColor: Colors.black,
            title: const Text(
              'Delete Mission',
              style: TextStyle(color: Colors.white),
            ),
            content: Text(
              'Are you sure you want to delete "${mission.title}"?',
              style: const TextStyle(color: Colors.white),
            ),
            actions: [
              TextButton(
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: Colors.white),
                ),
                onPressed: () => Navigator.pop(context),
              ),
              TextButton(
                child: const Text(
                  'Delete',
                  style: TextStyle(color: Colors.red),
                ),
                onPressed: () {
                  provider.deleteMission(mission);
                  Navigator.pop(context);
                },
              ),
            ],
          ),
    );
  }

  Widget _buildSubtaskCounter(
    BuildContext context,
    MissionData mission,
    MissionSubtask subtask,
    int subtaskIndex,
  ) {
    print(
      'Building counter for subtask: ${subtask.name} at index: $subtaskIndex',
    );

    return Consumer<MissionProvider>(
      builder: (context, provider, child) {
        /// Get the current mission and subtask with proper error handling
        final currentMission = provider.missions.firstWhere(
          (m) => m.notificationId == mission.notificationId,
          orElse: () {
            print(
              'Warning: Mission not found in provider, using provided mission',
            );
            return mission;
          },
        );

        /// Validate mission state
        if (!_validateMissionState(currentMission)) {
          print('Error: Invalid mission state detected');
          return const SizedBox.shrink();
        }

        /// Validate subtask index
        if (subtaskIndex < 0 ||
            subtaskIndex >= currentMission.subtasks.length) {
          print('Error: Invalid subtask index: $subtaskIndex');
          return const SizedBox.shrink();
        }

        /// For counter-based missions without subtasks, use the mission's currentCount
        if (currentMission.isCounterBased && currentMission.subtasks.isEmpty) {
          return GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: () async {
              final missionProvider = Provider.of<MissionProvider>(
                context,
                listen: false,
              );
              if (missionProvider.isDailyLocked ||
                  missionProvider.isWeeklyLocked) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Missions are locked. Please refresh to unlock.',
                    ),
                    duration: Duration(seconds: 2),
                  ),
                );
                return;
              }
              print('Tap detected for counter-based mission without subtasks');
              try {
                /// Validate mission state before update
                if (!_validateMissionState(currentMission)) {
                  print('Mission state validation failed');
                  return;
                }

                /// Create updated mission with incremented count
                final updatedMission = currentMission.copyWith(
                  currentCount: currentMission.currentCount + 1,
                  hasFailed: false,
                );

                /// Log mission state change
                print('Mission state change:');
                print('  Title: ${currentMission.title}');
                print('  Previous count: ${currentMission.currentCount}');
                print('  New count: ${updatedMission.currentCount}');
                print('  Mission ID: ${currentMission.notificationId}');

                /// Add mastery progress if linked
                if (currentMission.linkedMasteryId != null &&
                    currentMission.masteryValue > 0) {
                  final masteryProvider = Provider.of<MasteryProvider>(
                    context,
                    listen: false,
                  );
                  /// Add mastery value for each increment
                  await masteryProvider.addProgress(
                    currentMission.linkedMasteryId!,
                    'Mission: ${currentMission.title}',
                    currentMission.masteryValue,
                  );
                  print(
                    'Added mastery progress for mission: ${currentMission.title}',
                  );
                }

                /// Update mission through provider
                print('Updating mission through provider');
                await missionProvider.editMission(
                  currentMission,
                  updatedMission,
                );
              } catch (e, stackTrace) {
                print('Error handling mission tap: $e');
                print('Stack trace: $stackTrace');
                /// Show error to user
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Error: ${e.toString()}'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: 12.6,
                vertical: 4.2,
              ),
              decoration: BoxDecoration(
                color: (currentMission.boltColor ?? Colors.blue).withAlpha(51),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: currentMission.boltColor ?? Colors.blue,
                  width: 1,
                ),
              ),
              child: Text(
                '${currentMission.currentCount}',
                style: TextStyle(
                  color: currentMission.boltColor ?? Colors.blue,
                  fontWeight: FontWeight.bold,
                  fontSize: 15.75,
                ),
              ),
            ),
          );
        }

        /// Use the index to get the correct subtask
        final currentSubtask = currentMission.subtasks[subtaskIndex];

        /// Validate subtask state
        if (!_validateSubtaskState(currentSubtask)) {
          print('Error: Invalid subtask state detected');
          return const SizedBox.shrink();
        }

        print(
          'Current subtask state - name: ${currentSubtask.name}, count: ${currentSubtask.currentCount}, completions: ${currentSubtask.currentCompletions}, index: $subtaskIndex',
        );

        return GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () async {
            final missionProvider = Provider.of<MissionProvider>(
              context,
              listen: false,
            );
            if (missionProvider.isDailyLocked ||
                missionProvider.isWeeklyLocked) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'Missions are locked. Please refresh to unlock.',
                  ),
                  duration: Duration(seconds: 2),
                ),
              );
              return;
            }
            print(
              'Tap detected for subtask: ${currentSubtask.name} at index: $subtaskIndex',
            );
            try {
              /// Create updated subtask with incremented count
              final updatedSubtask =
                  currentSubtask.isCounterBased
                      ? currentSubtask.copyWith(
                        currentCount: currentSubtask.currentCount + 1,
                      )
                      : currentSubtask.copyWith(
                        currentCompletions:
                            currentSubtask.currentCompletions + 1,
                      );
              print(
                'Created updated subtask - count: ${updatedSubtask.currentCount}, completions: ${updatedSubtask.currentCompletions}',
              );

              /// Create updated mission with new subtask
              final updatedSubtasks = List<MissionSubtask>.from(
                currentMission.subtasks,
              );
              updatedSubtasks[subtaskIndex] = updatedSubtask;

              /// Check if all subtasks are complete
              bool allSubtasksComplete = updatedSubtasks.every(
                (s) =>
                    s.isCounterBased
                        ? s.currentCount >=
                            (s.requiredCompletions > 0
                                ? s.requiredCompletions
                                : 1)
                        : s.currentCompletions >= s.requiredCompletions,
              );

              final updatedMission = currentMission.copyWith(
                isCompleted: allSubtasksComplete,
                lastCompleted: allSubtasksComplete ? DateTime.now() : null,
                hasFailed: false,
                subtasks: updatedSubtasks,
              );

              /// Update mission through provider
              await missionProvider.editMission(currentMission, updatedMission);

              /// Add mastery progress if linked
              if (currentSubtask.linkedMasteryId != null &&
                  currentSubtask.masteryValue > 0) {
                final masteryProvider = Provider.of<MasteryProvider>(
                  context,
                  listen: false,
                );
                /// Add mastery value for each increment
                await masteryProvider.addProgress(
                  currentSubtask.linkedMasteryId!,
                  'Mission: ${currentMission.title} - ${currentSubtask.name}',
                  currentSubtask.masteryValue,
                );
              }
            } catch (e, stackTrace) {
              print('Error handling subtask tap: $e');
              print('Stack trace: $stackTrace');
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Error: ${e.toString()}'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          },
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12.6,
                  vertical: 4.2,
                ),
                decoration: BoxDecoration(
                  color: (currentSubtask.boltColor ?? Colors.blue).withAlpha(
                    51,
                  ),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    width: 1,
                  ),
                ),
                child: Text(
                  currentSubtask.isCounterBased
                      ? '${currentSubtask.currentCount}'
                      : '${currentSubtask.currentCompletions}',
                  style: TextStyle(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    fontWeight: FontWeight.bold,
                    fontSize: 15.75,
                  ),
                ),
              ),
              if (currentSubtask.isCounterBased &&
                  currentSubtask.masteryValue > 0) ...[
                const SizedBox(width: 8),
                Text(
                  '+${currentSubtask.masteryValue.toStringAsFixed(1)}',
                  style: TextStyle(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  /// Add validation function for subtask state
  bool _validateSubtaskState(MissionSubtask subtask) {
    /// Validate subtask name
    if (subtask.name.isEmpty) {
      print('Subtask validation failed: Empty name');
      return false;
    }

    /// Validate counter-based subtask
    if (subtask.isCounterBased) {
      if (subtask.currentCount < 0) {
        print('Subtask validation failed: Invalid current count');
        return false;
      }
    }

    /// Validate completions
    if (subtask.currentCompletions < 0) {
      print('Subtask validation failed: Invalid current completions');
      return false;
    }
    if (subtask.requiredCompletions < 0) {
      print('Subtask validation failed: Invalid required completions');
      return false;
    }

    /// Validate mastery value if linked
    if (subtask.linkedMasteryId != null && subtask.masteryValue < 0) {
      print('Subtask validation failed: Invalid mastery value');
      return false;
    }

    print('Subtask state validation passed');
    return true;
  }

  /// Add validation function for mission state
  bool _validateMissionState(MissionData mission) {
    /// Validate mission ID
    if (mission.id == null || mission.missionId == null) {
      print('Mission validation failed: Missing ID');
      return false;
    }

    /// Validate mission title
    if (mission.title.trim().isEmpty) {
      print('Mission validation failed: Empty title');
      return false;
    }

    /// Validate subtasks if present
    if (mission.subtasks.isNotEmpty) {
      for (final subtask in mission.subtasks) {
        if (!_validateSubtaskState(subtask)) {
          print('Mission validation failed: Invalid subtask state');
          return false;
        }
      }
    }

    /// Validate counter configuration
    if (mission.isCounterBased) {
      if (mission.targetCount < 0) {
        print('Mission validation failed: Invalid target count');
        return false;
      }
      if (mission.currentCount < 0) {
        print('Mission validation failed: Invalid current count');
        return false;
      }
    }

    /// Validate mastery values
    if (mission.linkedMasteryId != null && mission.masteryValue <= 0) {
      print('Mission validation failed: Invalid mastery value');
      return false;
    }

    /// Validate subtask mastery values
    for (final entry in mission.subtaskMasteryValues.entries) {
      if (entry.value <= 0) {
        print('Mission validation failed: Invalid subtask mastery value');
        return false;
      }
    }

    return true;
  }

  Future<void> _clearMissionCache(String missionId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cacheKey = 'mission_cache_$missionId';
      await prefs.remove(cacheKey);
    } catch (e) {
      print('Error clearing mission cache: $e');
    }
  }

  Future<void> _initializeMissionState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastRefreshDate = prefs.getString('last_refresh_date');
      final currentDate = DateTime.now();

      if (lastRefreshDate != null) {
        final lastRefresh = DateTime.parse(lastRefreshDate);
        if (lastRefresh.year == currentDate.year &&
            lastRefresh.month == currentDate.month &&
            lastRefresh.day == currentDate.day) {
          /// Already refreshed today
          return;
        }
      }

      /// Check if it's the last day of the week
      final isLastDayOfWeek = currentDate.weekday == DateTime.sunday;

      /// Only refresh if it's a new day and not after midday
      if (currentDate.hour < 12 || isLastDayOfWeek) {
        await _refreshMissions();
        await prefs.setString(
          'last_refresh_date',
          currentDate.toIso8601String(),
        );
      }
    } catch (e) {
      print('Error initializing mission state: $e');
    }
  }

  Future<void> _refreshMissions() async {
    try {
      final missionProvider = Provider.of<MissionProvider>(
        navigatorKey.currentContext!,
        listen: false,
      );
      await missionProvider.refreshMissions();
    } catch (e) {
      print('Error refreshing missions: $e');
    }
  }

  /// Debug: Periodically check for uniqueness and independence
  Future<void> _debugCheckMissions(BuildContext context) async {
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final missions = missionProvider.missions;
    final ids = <String>{};
    final notificationIds = <int>{};
    bool hasDuplicate = false;
    bool hasLinked = false;
    for (final m in missions) {
      if (!ids.add(m.id ?? '')) hasDuplicate = true;
      if (!notificationIds.add(m.notificationId)) hasDuplicate = true;
      if (m.linkedMasteryId != null && m.linkedMasteryId!.isNotEmpty)
        hasLinked = true;
    }
    if (hasDuplicate || hasLinked) {
      await showDialog(
        context: context,
        builder:
            (context) => AlertDialog(
              title: const Text('Mission Integrity Warning'),
              content: Text(
                hasDuplicate
                    ? 'Duplicate mission IDs or notification IDs found!'
                    : 'Some missions are linked (linkedMasteryId is set).',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('OK'),
                ),
              ],
            ),
      );
    }
  }

  /// Debug: Show popup with current missions and their IDs after creation
  Future<void> _showMissionListPopup(BuildContext context) async {
    if (!kDebugMode) return;
    final missionProvider = Provider.of<MissionProvider>(
      context,
      listen: false,
    );
    final missions = missionProvider.missions;
    final missionList = missions
        .map(
          (m) =>
              'ID: ${m.id}\nTitle: ${m.title}\nNotificationID: ${m.notificationId}\nLinkedMasteryId: ${m.linkedMasteryId ?? "None"}',
        )
        .join('\n\n');
    await showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Current Missions'),
            content: SingleChildScrollView(
              child: Text(missionList.isEmpty ? 'No missions.' : missionList),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          ),
    );
  }
}

class _SubtaskCounterState extends State<_SubtaskCounter> {
  late ValueNotifier<MissionSubtask> _subtaskNotifier;

  @override
  void initState() {
    super.initState();
    _subtaskNotifier = ValueNotifier(widget.subtask);
  }

  @override
  void dispose() {
    _subtaskNotifier.dispose();
    super.dispose();
  }

  /// Add validation function for mission state
  bool _validateMissionState(MissionData mission) {
    /// Validate mission ID
    if (mission.notificationId == null) {
      print('Mission validation failed: Missing notification ID');
      return false;
    }

    /// Validate counter-based mission
    if (mission.isCounterBased) {
      if (mission.currentCount < 0) {
        print('Mission validation failed: Invalid current count');
        return false;
      }
      if (mission.targetCount < 0) {
        print('Mission validation failed: Invalid target count');
        return false;
      }
    }

    /// Validate subtasks if present
    if (mission.subtasks.isNotEmpty) {
      for (var subtask in mission.subtasks) {
        if (subtask.name.isEmpty) {
          print('Mission validation failed: Empty subtask name');
          return false;
        }
        if (subtask.currentCompletions < 0) {
          print('Mission validation failed: Invalid current completions');
          return false;
        }
        if (subtask.requiredCompletions < 0) {
          print('Mission validation failed: Invalid required completions');
          return false;
        }
      }
    }

    print('Mission state validation passed');
    return true;
  }

  /// Add validation function for subtask state
  bool _validateSubtaskState(MissionSubtask subtask) {
    /// Validate subtask name
    if (subtask.name.isEmpty) {
      print('Subtask validation failed: Empty name');
      return false;
    }

    /// Validate counter-based subtask
    if (subtask.isCounterBased) {
      if (subtask.currentCount < 0) {
        print('Subtask validation failed: Invalid current count');
        return false;
      }
    }

    /// Validate completions
    if (subtask.currentCompletions < 0) {
      print('Subtask validation failed: Invalid current completions');
      return false;
    }
    if (subtask.requiredCompletions < 0) {
      print('Subtask validation failed: Invalid required completions');
      return false;
    }

    /// Validate mastery value if linked
    if (subtask.linkedMasteryId != null && subtask.masteryValue < 0) {
      print('Subtask validation failed: Invalid mastery value');
      return false;
    }

    print('Subtask state validation passed');
    return true;
  }

  @override
  Widget build(BuildContext context) {
    print('Building counter for subtask: ${widget.subtask.name}');

    return Consumer<MissionProvider>(
      builder: (context, provider, child) {
        /// Get the current mission and subtask with proper error handling
        final currentMission = provider.missions.firstWhere(
          (m) => m.notificationId == widget.mission.notificationId,
          orElse: () {
            print(
              'Warning: Mission not found in provider, using provided mission',
            );
            return widget.mission;
          },
        );

        /// Validate mission state
        if (!_validateMissionState(currentMission)) {
          print('Error: Invalid mission state detected');
          return const SizedBox.shrink();
        }

        /// Validate subtask index
        if (widget.subtaskIndex < 0 ||
            widget.subtaskIndex >= currentMission.subtasks.length) {
          print('Error: Invalid subtask index: ${widget.subtaskIndex}');
          return const SizedBox.shrink();
        }

        /// Use the index to get the correct subtask
        final currentSubtask = currentMission.subtasks[widget.subtaskIndex];

        /// Validate subtask state
        if (!_validateSubtaskState(currentSubtask)) {
          print('Error: Invalid subtask state detected');
          return const SizedBox.shrink();
        }

        print(
          'Current subtask state - name: ${currentSubtask.name}, count: ${currentSubtask.currentCount}, completions: ${currentSubtask.currentCompletions}, index: ${widget.subtaskIndex}',
        );

        return GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTap: () async {
            final missionProvider = Provider.of<MissionProvider>(
              context,
              listen: false,
            );
            if (missionProvider.isDailyLocked ||
                missionProvider.isWeeklyLocked) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text(
                    'Missions are locked. Please refresh to unlock.',
                  ),
                  duration: Duration(seconds: 2),
                ),
              );
              return;
            }
            print(
              'Tap detected for subtask: ${currentSubtask.name} at index: ${widget.subtaskIndex}',
            );
            try {
              /// Create updated subtask with incremented count
              final updatedSubtask =
                  currentSubtask.isCounterBased
                      ? currentSubtask.copyWith(
                        currentCount: currentSubtask.currentCount + 1,
                      )
                      : currentSubtask.copyWith(
                        currentCompletions:
                            currentSubtask.currentCompletions + 1,
                      );
              print(
                'Created updated subtask - count: ${updatedSubtask.currentCount}, completions: ${updatedSubtask.currentCompletions}',
              );

              /// Create updated mission with new subtask
              final updatedSubtasks = List<MissionSubtask>.from(
                currentMission.subtasks,
              );
              updatedSubtasks[widget.subtaskIndex] = updatedSubtask;

              /// Check if all subtasks are complete
              bool allSubtasksComplete = updatedSubtasks.every(
                (s) =>
                    s.isCounterBased
                        ? s.currentCount >=
                            (s.requiredCompletions > 0
                                ? s.requiredCompletions
                                : 1)
                        : s.currentCompletions >= s.requiredCompletions,
              );

              final updatedMission = currentMission.copyWith(
                isCompleted: allSubtasksComplete,
                lastCompleted: allSubtasksComplete ? DateTime.now() : null,
                hasFailed: false,
                subtasks: updatedSubtasks,
              );

              /// Update mission through provider
              await missionProvider.editMission(currentMission, updatedMission);

              /// Add mastery progress if linked
              if (currentSubtask.linkedMasteryId != null &&
                  currentSubtask.masteryValue > 0) {
                final masteryProvider = Provider.of<MasteryProvider>(
                  context,
                  listen: false,
                );
                /// Add mastery value for each increment
                await masteryProvider.addProgress(
                  currentSubtask.linkedMasteryId!,
                  'Mission: ${currentMission.title} - ${currentSubtask.name}',
                  currentSubtask.masteryValue,
                );
              }
            } catch (e, stackTrace) {
              print('Error handling subtask tap: $e');
              print('Stack trace: $stackTrace');
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Error: ${e.toString()}'),
                  backgroundColor: Colors.red,
                ),
              );
            }
          },
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12.6,
                  vertical: 4.2,
                ),
                decoration: BoxDecoration(
                  color: (currentSubtask.boltColor ?? Colors.blue).withAlpha(
                    51,
                  ),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    width: 1,
                  ),
                ),
                child: Text(
                  currentSubtask.isCounterBased
                      ? '${currentSubtask.currentCount}'
                      : '${currentSubtask.currentCompletions}',
                  style: TextStyle(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    fontWeight: FontWeight.bold,
                    fontSize: 15.75,
                  ),
                ),
              ),
              if (currentSubtask.isCounterBased &&
                  currentSubtask.masteryValue > 0) ...[
                const SizedBox(width: 8),
                Text(
                  '+${currentSubtask.masteryValue.toStringAsFixed(1)}',
                  style: TextStyle(
                    color: currentSubtask.boltColor ?? Colors.blue,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}

class _SubtaskCounter extends StatefulWidget {
  final MissionData mission;
  final MissionSubtask subtask;
  final int subtaskIndex;

  const _SubtaskCounter({
    required this.mission,
    required this.subtask,
    required this.subtaskIndex,
  });

  @override
  State<_SubtaskCounter> createState() => _SubtaskCounterState();
}

/// Add this widget at the top-level (or near other widgets)
class MissionHealthCheckDialog extends StatefulWidget {
  final MissionProvider provider;
  const MissionHealthCheckDialog({super.key, required this.provider});

  @override
  State<MissionHealthCheckDialog> createState() =>
      _MissionHealthCheckDialogState();
}

class _MissionHealthCheckDialogState extends State<MissionHealthCheckDialog> {
  final List<String> checkTitles = [
    'AI Guardian Status',
    'Comprehensive Repair',
    'Unique IDs and Notification IDs',
    'Mission State Validity',
    'Refresh Logic (Manual & Automatic)',
    'Failure Logic',
    'Notification Scheduling',
    'UI Color State',
    'Editability',
    'Subtasks and Mastery Values',
    'Data Consistency',
  ];
  late List<int> checkStates; // 0: running, 1: pass, 2: fail
  late List<String> checkResults;
  late List<bool> isRepairing; // true if repair in progress for this check
  bool allDone = false;
  bool started = false;

  /// AI Guardian learning and repair tracking
  List<String> learningEvents = [];
  List<Map<String, dynamic>> repairEvents = [];
  List<HealthCheckResult> healthResults = [];
  List<RepairResult> repairResults = [];

  @override
  void initState() {
    super.initState();
    checkStates = List.filled(checkTitles.length, 0);
    checkResults = List.filled(checkTitles.length, '');
    isRepairing = List.filled(checkTitles.length, false);

    /// Listen to AI Guardian learning and repair events
    widget.provider.aiGuardian.learningStream.listen((event) {
      setState(() {
        learningEvents.add(
          '${DateTime.now().toString().substring(11, 19)}: $event',
        );
        if (learningEvents.length > 10) learningEvents.removeAt(0);
      });
    });

    widget.provider.aiGuardian.issueStream.listen((event) {
      setState(() {
        repairEvents.add(event);
        if (repairEvents.length > 10) repairEvents.removeAt(0);
      });
    });

    WidgetsBinding.instance.addPostFrameCallback((_) => runChecks());
  }

  Future<void> runChecks() async {
    if (started) return;
    started = true;
    print('Provider runtime type: ${widget.provider.runtimeType}');
    print('MissionHealthCheckDialog: Starting health checks...');

    /// Check AI Guardian status
    setState(() {
      checkResults[0] =
          'AI Guardian Status: ${widget.provider.aiGuardianStatus}';
      checkStates[0] = widget.provider.isAIGuardianRunning ? 1 : 2;
    });

    /// First pass: attempt comprehensive repairs using AI Guardian
    try {
      setState(() {
        checkStates[1] = 0; // Running
        checkResults[1] = 'Performing AI Guardian comprehensive repair...';
      });

      /// Use the enhanced AI Guardian repair system
      final healthResults =
          await widget.provider.aiGuardian.performComprehensiveHealthChecks();
      final repairResults =
          await widget.provider.aiGuardian.performComprehensiveRepairs();

      setState(() {
        this.healthResults = healthResults;
        this.repairResults = repairResults;
        checkResults[1] =
            '✅ AI Guardian repair completed - ${repairResults.where((r) => r.success).length} repairs successful';
        checkStates[1] = 1;
      });
    } catch (e) {
      setState(() {
        checkResults[1] = '❌ Repair failed: $e';
        checkStates[1] = 2;
      });
    }

    /// Second pass: validate all missions after repairs
    await widget.provider.validateAllMissions(
      attemptRepair: false,
      stepwise: true,
      onStep: (idx, result, passed) {
        print(
          'MissionHealthCheckDialog: VALIDATION onStep idx=$idx, passed=$passed, result=$result',
        );
        setState(() {
          isRepairing[idx + 2] = false;
          checkStates[idx + 2] =
              passed
                  ? 1
                  : 2; // Offset by 2 for AI Guardian status and repair status
          checkResults[idx + 2] = result;
        });
      },
      context: context,
      showUser: true,
    );

    setState(() {
      allDone = true;
    });
    print('MissionHealthCheckDialog: All checks done.');
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('AI Guardian Health Check'),
      content: SizedBox(
        width: 400,
        height: 600,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              /// AI Guardian Learning Status
              if (learningEvents.isNotEmpty) ...[
                const Text(
                  '🧠 AI Guardian Learning:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 100,
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView.builder(
                    itemCount: learningEvents.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text(
                          learningEvents[learningEvents.length - 1 - index],
                          style: const TextStyle(fontSize: 12),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 16),
              ],

              /// AI Guardian Repair Events
              if (repairEvents.isNotEmpty) ...[
                const Text(
                  '🛠️ Recent Repairs:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                Container(
                  height: 120,
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView.builder(
                    itemCount: repairEvents.length,
                    itemBuilder: (context, index) {
                      final event =
                          repairEvents[repairEvents.length - 1 - index];
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2),
                        child: Text(
                          '${event['timestamp']?.toString().substring(11, 19) ?? ''}: ${event['type']} - ${event['repairName'] ?? event['checkName'] ?? event['issue']}',
                          style: const TextStyle(fontSize: 12),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 16),
              ],

              /// Health Check Results
              if (healthResults.isNotEmpty) ...[
                const Text(
                  '🔍 Health Check Results:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                ...healthResults.map(
                  (result) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      children: [
                        Icon(
                          result.hasIssue ? Icons.error : Icons.check_circle,
                          color: result.hasIssue ? Colors.red : Colors.green,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${result.checkName}: ${result.hasIssue ? 'Issue detected' : 'OK'}',
                            style: TextStyle(
                              fontSize: 12,
                              color:
                                  result.hasIssue ? Colors.red : Colors.green,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              /// Repair Results
              if (repairResults.isNotEmpty) ...[
                const Text(
                  '🔧 Repair Results:',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                ...repairResults.map(
                  (result) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      children: [
                        Icon(
                          result.success ? Icons.check_circle : Icons.error,
                          color: result.success ? Colors.green : Colors.red,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${result.repairName}: ${result.success ? 'Success' : 'Failed'}',
                            style: TextStyle(
                              fontSize: 12,
                              color: result.success ? Colors.green : Colors.red,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              /// Traditional health checks
              const Text(
                '📋 System Health Checks:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 8),
              for (int i = 0; i < checkTitles.length; i++) ...[
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (checkStates[i] == 0)
                      const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    else if (checkStates[i] == 1)
                      const Icon(Icons.check_circle, color: Colors.green)
                    else ...[
                      const Icon(Icons.error, color: Colors.red),
                      if (isRepairing[i]) ...[
                        const SizedBox(width: 4),
                        const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        const SizedBox(width: 4),
                        const Text(
                          'resolving...',
                          style: TextStyle(fontSize: 12, color: Colors.blue),
                        ),
                      ],
                    ],
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            checkTitles[i],
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          if (checkResults[i].isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 2.0),
                              child: Text(
                                checkResults[i],
                                style: const TextStyle(fontSize: 13),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
              ],
            ],
          ),
        ),
      ),
      actions: [
        if (!widget.provider.isAIGuardianRunning && allDone)
          TextButton(
            onPressed: () async {
              await widget.provider.restartAIGuardian();
              if (mounted) {
                Navigator.of(context).pop();
              }
            },
            child: const Text('Restart AI Guardian'),
          ),
        TextButton(
          onPressed: allDone ? () => Navigator.of(context).pop() : null,
          child: const Text('OK'),
        ),
      ],
    );
  }
}

/// Helper widget to display both asset and file images
class SmartImage extends StatelessWidget {
  final String imagePath;
  final double? width;
  final double? height;
  final BoxFit fit;
  final Widget? errorWidget;

  const SmartImage({
    super.key,
    required this.imagePath,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
    this.errorWidget,
  });

  @override
  Widget build(BuildContext context) {
    /// Check if it's a file path (starts with / or contains file:/)
    if (imagePath.startsWith('/') || imagePath.startsWith('file:/')) {
      return Image.file(
        File(imagePath),
        width: width,
        height: height,
        fit: fit,
        errorBuilder: (context, error, stackTrace) {
          return errorWidget ??
              Container(
                width: width,
                height: height,
                color: Colors.grey[800],
                child: const Icon(
                  Icons.broken_image,
                  color: Colors.white,
                  size: 32,
                ),
              );
        },
      );
    } else {
      /// It's an asset image
      return Image.asset(
        imagePath,
        width: width,
        height: height,
        fit: fit,
        errorBuilder: (context, error, stackTrace) {
          return errorWidget ??
              Container(
                width: width,
                height: height,
                color: Colors.grey[800],
                child: const Icon(
                  Icons.broken_image,
                  color: Colors.white,
                  size: 32,
                ),
              );
        },
      );
    }
  }
}
