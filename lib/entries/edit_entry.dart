import 'package:flutter/material.dart';
import '../models/entry.dart';
import '../entry_manager.dart';

class EditEntry extends StatefulWidget {
  static const routeName = '/edit-entry';
  final Entry entry;
  const EditEntry({Key? key, required this.entry}) : super(key: key);

  @override
  _EditEntryState createState() => _EditEntryState();
}

class _EditEntryState extends State<EditEntry> {
  final _formKey = GlobalKey<FormState>();
  String _content = '';
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _content = widget.entry.content;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Container(
          padding: const EdgeInsets.only(left: 20, right: 20, bottom: 10),
          child: Stack(
            children: [
              Form(
                key: _formKey,
                child: ListView(
                  children: [
                    const SizedBox(height: 45),
                    Padding(
                      padding: const EdgeInsets.only(bottom: 20),
                      child: Text(
                        widget.entry.title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF3C4858),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    TextFormField(
                      keyboardType: TextInputType.multiline,
                      maxLines: null,
                      initialValue: _content,
                      decoration: const InputDecoration(
                        hintText: '',
                        border: InputBorder.none,
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter some text';
                        }
                        return null;
                      },
                      onSaved: (value) => _content = value!,
                    ),
                  ],
                ),
              ),
              Row(
                children: [
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.arrow_downward),
                    padding: const EdgeInsets.all(10),
                    style: ButtonStyle(
                      backgroundColor: WidgetStateProperty.all(Colors.white),
                      shape: WidgetStateProperty.all(const CircleBorder()),
                      shadowColor: WidgetStateProperty.all(
                        Color(0xFF3C4858).withOpacity(0.5),
                      ),
                      elevation: WidgetStateProperty.all(10),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: const Color(0xFF3C4858),
        onPressed:
            _isLoading
                ? null
                : () async {
                  if (_formKey.currentState!.validate()) {
                    setState(() => _isLoading = true);
                    _formKey.currentState!.save();
                    try {
                      final success = await EntryManager().updateEntry(
                        widget.entry.id,
                        _content,
                      );
                      setState(() => _isLoading = false);
                      if (success) {
                        Navigator.of(context).pop(); // Return to ViewEntry
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Failed to update entry'),
                          ),
                        );
                      }
                    } catch (e) {
                      setState(() => _isLoading = false);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error updating entry: $e')),
                      );
                    }
                  }
                },
        child:
            _isLoading
                ? const CircularProgressIndicator(color: Colors.white)
                : const Icon(Icons.check),
      ),
    );
  }
}
