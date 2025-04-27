// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

// Import other screen for navigation
import 'log_workout_screen.dart';
// Import main.dart only if you absolutely need the global `supabase` helper,
// otherwise use Supabase.instance.client directly. Less coupling is better.
// import '../main.dart'; // Avoid if possible

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Use Supabase client instance directly for better encapsulation
  final _supabase = Supabase.instance.client;

  // Get current user (will be available since AuthGate protects this screen)
  User? get _user => _supabase.auth.currentUser;

  Future<void> _signOut() async {
    try {
      await _supabase.auth.signOut();
      // No need to navigate, AuthGate's StreamBuilder handles the state change
      // and will show the LoginScreen automatically.
    } on AuthException catch (e) {
      // Use mounted check before showing ScaffoldMessenger
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('Sign out failed: ${e.message}'),
            backgroundColor: Theme.of(context).colorScheme.error));
      }
      print("Sign out error: ${e.message}");
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: const Text('An unexpected error occurred during sign out.'),
            backgroundColor: Theme.of(context).colorScheme.error));
      }
      print("Sign out unexpected error: $e");
    }
  }

  // --- Placeholder state/functions for future features ---
  // String _backendMessage = "Loading data from backend...";
  // bool _isFetching = false;
  // String? _fetchError;

  // Future<void> _fetchProtectedData() async { /* ... API call logic ... */ }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FMMT Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sign Out',
            onPressed: _signOut, // Call the sign out method
          ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Text(
                'Welcome!',
                style: Theme.of(context).textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),

              // Display user email safely
              Text(
                'Logged in as: ${_user?.email ?? 'Unknown User'}',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 60), // More space before actions

              const Text(
                'Your Fitness, Mood & Music dashboard will be here.',
                 style: TextStyle(fontSize: 16),
                 textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),

              // Button to navigate to Log Workout Screen
              ElevatedButton.icon(
                icon: const Icon(Icons.fitness_center), // Changed icon
                label: const Text('Log New Workout'),
                style: ElevatedButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(vertical: 12, horizontal: 24),
                  textStyle: const TextStyle(fontSize: 16) // Slightly larger text
                ),
                onPressed: () {
                  // Use Navigator.push to go to the LogWorkoutScreen
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const LogWorkoutScreen()),
                  );
                },
              ),
              const SizedBox(height: 20), // Spacing

              // --- Optional: Add button placeholders for other features later ---
              // ElevatedButton.icon(
              //   icon: const Icon(Icons.sentiment_satisfied_alt),
              //   label: const Text('Log Mood'),
              //   onPressed: () { /* Navigate to Log Mood Screen */ },
              // ),
              // const SizedBox(height: 12),
              // ElevatedButton.icon(
              //   icon: const Icon(Icons.music_note),
              //   label: const Text('Connect Spotify'),
              //   onPressed: () { /* Trigger Spotify Connect Flow */ },
              // ),
            ],
          ),
        ),
      ),
    );
  }
}