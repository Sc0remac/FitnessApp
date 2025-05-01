// lib/screens/log_mood_screen.dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart'; // To get user ID

import '../models/mood_log.dart';
import '../services/api_service.dart';

class LogMoodScreen extends StatefulWidget {
  const LogMoodScreen({super.key});

  @override
  State<LogMoodScreen> createState() => _LogMoodScreenState();
}

class _LogMoodScreenState extends State<LogMoodScreen> {
  // State variables
  double _currentMoodScore = 5.0; // Default to middle score
  final _journalController = TextEditingController();
  bool _isSaving = false;
  String? _saveError;

  // --- Save Mood Logic ---
  Future<void> _saveMoodEntry() async {
    final userId = Supabase.instance.client.auth.currentUser?.id;
    if (userId == null) {
       if(mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
             const SnackBar(content: Text('Error: User not logged in.'), backgroundColor: Colors.red)
          );
       }
      return; // Should not happen if screen is protected
    }

    setState(() {
      _isSaving = true;
      _saveError = null;
    });

    final moodLogToSave = MoodLog(
      userId: userId, // Include userId although backend gets it from token
      moodScore: _currentMoodScore.round(), // Convert slider value to int
      journalText: _journalController.text.trim().isEmpty
          ? null // Send null if empty
          : _journalController.text.trim(),
      timestamp: DateTime.now(), // Client-side timestamp
    );

    try {
      await ApiService().saveMood(moodLogToSave);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Mood logged successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context); // Go back after saving
      }
    } catch (e) {
      print("Error caught in UI during saveMood: $e");
      if (mounted) {
        setState(() {
          _saveError = e.toString();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to log mood: $_saveError'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _journalController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Log Your Mood'),
         actions: [
            _isSaving
              ? const Padding(
                  padding: EdgeInsets.only(right: 16.0),
                  child: Center(child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))),
                )
              : IconButton(
                  icon: const Icon(Icons.save),
                  tooltip: 'Save Mood Entry',
                  onPressed: _saveMoodEntry,
                )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'How are you feeling right now?',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),

            // --- Mood Score Slider ---
            Text(
              'Mood Score: ${_currentMoodScore.round()}/10', // Display rounded value
              style: Theme.of(context).textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            Slider(
              value: _currentMoodScore,
              min: 1.0,
              max: 10.0,
              divisions: 9, // Creates 10 selectable points (1 to 10)
              label: _currentMoodScore.round().toString(),
              onChanged: (double value) {
                setState(() {
                  _currentMoodScore = value;
                });
              },
              activeColor: Colors.deepPurple,
              inactiveColor: Colors.deepPurple.shade100,
            ),
            const Row( // Add labels below slider
               mainAxisAlignment: MainAxisAlignment.spaceBetween,
               children: [Text('Awful (1)'), Text('Great (10)')],
            ),
            const SizedBox(height: 30),

            // --- Journal Entry ---
            Text(
              'Journal (Optional):',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _journalController,
              maxLines: 5, // Allow multiple lines
              textCapitalization: TextCapitalization.sentences,
              decoration: const InputDecoration(
                hintText: 'Add any thoughts or details here...',
                border: OutlineInputBorder(),
                alignLabelWithHint: true, // Better alignment for multiline
              ),
            ),
            const SizedBox(height: 30),

            // --- Save Button ---
             _isSaving
                 ? const Center(child: CircularProgressIndicator())
                 : ElevatedButton.icon(
                    icon: const Icon(Icons.save),
                    label: const Text('Save Mood Entry'),
                    style: ElevatedButton.styleFrom(
                       padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    onPressed: _saveMoodEntry,
                   ),

              // --- Error Display ---
             if (_saveError != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16.0),
                  child: Text(
                    'Save failed: $_saveError',
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                    textAlign: TextAlign.center,
                  ),
                ),
          ],
        ),
      ),
    );
  }
}