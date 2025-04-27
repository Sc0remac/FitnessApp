// lib/models/workout_log.dart
import 'package:flutter/foundation.dart'; // For @required annotation

class SetLog {
  final int reps;
  final double weight; // Using double for flexibility (e.g., 2.5kg increments)

  SetLog({required this.reps, required this.weight});

  // Optional: Method to convert to JSON for API calls later
  Map<String, dynamic> toJson() => {
        'reps': reps,
        'weight': weight,
      };

  @override
  String toString() {
     return 'Reps: $reps, Weight: $weight kg'; // Adjust unit if needed
  }
}

class ExerciseLog {
  final String name;
  final List<SetLog> sets;

  ExerciseLog({required this.name, List<SetLog>? sets})
      : sets = sets ?? []; // Initialize with empty list if null

   // Optional: Method to convert to JSON for API calls later
   Map<String, dynamic> toJson() => {
         'name': name,
         'sets': sets.map((set) => set.toJson()).toList(),
       };

   @override
   String toString() {
      return '$name: ${sets.map((s) => s.toString()).join(" | ")}';
   }
}

class WorkoutLog {
  final String? id; // Optional ID from database later
  final DateTime timestamp;
  final List<ExerciseLog> exercises;
  // Add user ID later when saving to DB

  WorkoutLog({this.id, required this.timestamp, required this.exercises});

  // Optional: Method to convert to JSON for API calls later
   Map<String, dynamic> toJson() => {
         'timestamp': timestamp.toUtc().toIso8601String(), // Use UTC ISO8601 format
         'exercises': exercises.map((ex) => ex.toJson()).toList(),
         // Add user_id here later
       };

  @override
  String toString() {
    String exercisesStr = exercises.map((e) => e.toString()).join('\n  ');
    return '''
Workout Log (${timestamp.toLocal()}):
  $exercisesStr
''';
  }
}