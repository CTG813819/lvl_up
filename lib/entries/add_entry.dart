import 'package:flutter/material.dart';
import '../entry_manager.dart';
import 'entry_pin_screen.dart';

class AddEntry extends StatefulWidget {
  static const routeName = '/add-entry';
  const AddEntry({Key? key}) : super(key: key);

  @override
  _AddEntryState createState() => _AddEntryState();
}

class _AddEntryState extends State<AddEntry> {
  final _formKey = GlobalKey<FormState>();
  String _content = '';
  bool _isLoading = false;

  Future<void> _saveEntry() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      _formKey.currentState!.save();
      try {
        final success = await EntryManager().addEntry(_content);
        setState(() => _isLoading = false);
        if (success) {
          Navigator.of(context).pop();
        } else {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('Failed to add entry')));
        }
      } catch (e) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error adding entry: $e')));
      }
    }
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
                    TextFormField(
                      keyboardType: TextInputType.multiline,
                      maxLines: null,
                      decoration: const InputDecoration(
                        hintText: 'Begin...',
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
              Positioned(
                bottom: 0,
                right: 0,
                child: FloatingActionButton(
                  heroTag: 'add_entry_save',
                  onPressed:
                      _isLoading
                          ? null
                          : () {
                            if (_formKey.currentState!.validate()) {
                              _formKey.currentState!.save();
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder:
                                      (context) => EntryPinScreen(
                                        title: 'Confirm Entry',
                                        onPinEntered: (pin, context) {
                                          Navigator.of(context).pop();
                                          _saveEntry();
                                        },
                                      ),
                                ),
                              );
                            }
                          },
                  backgroundColor: Colors.black,
                  child:
                      _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Icon(Icons.check, color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
