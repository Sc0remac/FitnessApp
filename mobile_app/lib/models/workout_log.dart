// lib/models/workout_log.dart
import 'package:flutter/foundation.dart';

// --- Set Log (No changes needed) ---
class SetLog {
  final int reps;
  final double weight;
  SetLog({required this.reps, required this.weight});
  factory SetLog.fromJson(Map<String, dynamic> json) {
    return SetLog(
      reps: json['reps'] as int? ?? 0,
      weight: (json['weight'] as num?)?.toDouble() ?? 0.0,
    );
  }
  Map<String, dynamic> toJson() => {'reps': reps, 'weight': weight};
  @override String toString() => 'Reps: $reps, Weight: $weight kg';
}

// --- Exercise Log (No changes needed) ---
class ExerciseLog {
  final String name;
  final List<SetLog> sets;
  ExerciseLog({required this.name, List<SetLog>? sets}) : sets = sets ?? [];
  factory ExerciseLog.fromJson(Map<String, dynamic> json) {
    var setsList = <SetLog>[];
    if (json['sets'] != null && json['sets'] is List) {
      setsList = (json['sets'] as List)
          .map((setJson) => SetLog.fromJson(setJson as Map<String, dynamic>))
          .toList();
    }
    return ExerciseLog(
      name: json['exercise_name'] as String? ?? 'Unknown Exercise',
      sets: setsList,
    );
  }
  Map<String, dynamic> toJson() => {
        'exercise_name': name,
        'sets': sets.map((set) => set.toJson()).toList(),
      };
  @override String toString() => '$name: ${sets.map((s) => s.toString()).join(" | ")}';
}

// --- Workout Log (UPDATED) ---
class WorkoutLog {
  // Make fields nullable that won't exist before saving
  final String? id;
  final String? userId;
  final DateTime timestamp; // When workout occurred/logged (set by client for create)
  final DateTime? createdAt; // When DB record was created (set by server)
  final List<ExerciseLog> exercises;

  WorkoutLog({
    // Remove required for id, userId, createdAt in constructor
    this.id,
    this.userId,
    required this.timestamp, // Keep required
    this.createdAt,
    required this.exercises, // Keep required
  });

  // fromJson factory expects fields from the backend/DB response
  factory WorkoutLog.fromJson(Map<String, dynamic> json) {
    var exercisesList = <ExerciseLog>[];
    if (json['exercises'] != null && json['exercises'] is List) {
      exercisesList = (json['exercises'] as List)
          .map((exJson) => ExerciseLog.fromJson(exJson as Map<String, dynamic>))
          .toList();
    }
    // Parse dates safely, provide fallbacks
    final timestampFromJson = DateTime.tryParse(json['timestamp'] as String? ?? '') ?? DateTime.now();
    final createdAtFromJson = DateTime.tryParse(json['created_at'] as String? ?? '') ?? DateTime.now(); // createdAt is expected from DB

    return WorkoutLog(
      id: json['id'] as String? ?? '', // ID should always be returned
      userId: json['user_id'] as String? ?? '', // user_id should always be returned
      timestamp: timestampFromJson, // timestamp should always be returned
      createdAt: createdAtFromJson, // createdAt should always be returned
      exercises: exercisesList,
    );
  }

  // toJson method ONLY includes fields needed for CREATE request
  // Backend handles id, user_id, created_at, and timestamp (as per current backend code)
  Map<String, dynamic> toJson() => {
        // Backend workout router currently sets timestamp on creation,
        // so we don't *need* to send it, but sending client time might be useful later.
        // Let's remove it for now to exactly match backend expectation.
        // 'timestamp': timestamp.toUtc().toIso8601String(),
        'exercises': exercises.map((ex) => ex.toJson()).toList(),
      };

  @override
  String toString() {
    String exercisesStr = exercises.isNotEmpty
        ? exercises.map((e) => '  ${e.toString()}').join('\n')
        : '  No exercises logged.';
    // Use createdAt for primary display if available, otherwise timestamp
    final displayTime = createdAt ?? timestamp;
    return '''
Workout Log (${displayTime.toLocal()}):
  ID: ${id ?? 'N/A'}
  User: ${userId ?? 'N/A'}
$exercisesStr
''';
  }
}