// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

// Import other screens for navigation
import 'log_workout_screen.dart';
import 'log_mood_screen.dart';
import 'timeline_screen.dart';         // <-- IMPORT TIMELINE SCREEN
import 'profile_settings_screen.dart'; // <-- IMPORT PROFILE SCREEN

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // Use Supabase client instance directly
  final _supabase = Supabase.instance.client;
  User? get _user => _supabase.auth.currentUser;

  Future<void> _signOut() async {
    try {
      await _supabase.auth.signOut();
      // AuthGate handles navigation implicitly
    } catch (e) {
       print("Sign out error: $e");
       if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
              content: Text('Sign out failed: ${e.toString()}'),
              backgroundColor: Theme.of(context).colorScheme.error));
       }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FMMT Home'),
        actions: [
          // --- PROFILE BUTTON ---
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Profile & Settings',
            onPressed: () {
               Navigator.push(
                 context,
                 MaterialPageRoute(builder: (context) => const ProfileSettingsScreen()),
               );
            },
          ),
          // --- LOGOUT BUTTON ---
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Sign Out',
            onPressed: _signOut,
          ),
        ],
      ),
      body: Center(
        child: SingleChildScrollView( // Allows scrolling if content overflows
           padding: const EdgeInsets.all(16.0),
           child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: <Widget>[
                // --- Welcome Message ---
                Text(
                  'Welcome!',
                  style: Theme.of(context).textTheme.headlineMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                Text(
                  'Logged in as: ${_user?.email ?? 'Unknown User'}',
                  style: Theme.of(context).textTheme.bodyMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 50), // Increased spacing

                 // --- Action Buttons using Wrap ---
                 Wrap(
                   spacing: 16.0, // Horizontal space
                   runSpacing: 16.0, // Vertical space
                   alignment: WrapAlignment.center, // Center buttons horizontally
                   children: [
                      // Log Workout Button
                      ElevatedButton.icon(
                         icon: const Icon(Icons.fitness_center),
                         label: const Text('Log Workout'),
                         style: ElevatedButton.styleFrom(
                             minimumSize: const Size(160, 45), // Give buttons minimum size
                             padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 18),
                          ),
                         onPressed: () {
                            Navigator.push(context, MaterialPageRoute(builder: (context) => const LogWorkoutScreen()));
                         },
                       ),

                      // Log Mood Button
                       ElevatedButton.icon(
                         icon: const Icon(Icons.sentiment_satisfied_alt),
                         label: const Text('Log Mood'),
                         style: ElevatedButton.styleFrom(
                              minimumSize: const Size(160, 45),
                              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 18),
                             backgroundColor: Colors.teal, // Example different color
                             foregroundColor: Colors.white,
                         ),
                         onPressed: () {
                             Navigator.push(context, MaterialPageRoute(builder: (context) => const LogMoodScreen()));
                         },
                       ),

                       // --- View Timeline Button ---
                       ElevatedButton.icon(
                         icon: const Icon(Icons.timeline),
                         label: const Text('View Timeline'),
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(160, 45),
                            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 18),
                          ),
                         onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(builder: (context) => const TimelineScreen()),
                            );
                         },
                       ),
                       // --- End View Timeline Button ---

                       // You can add Spotify button here later when ready
                       // ElevatedButton.icon( ... )
                   ],
                 )
              ],
            ),
        ),
      ),
    );
  }
}