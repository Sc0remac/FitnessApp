// lib/screens/log_workout_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // For input formatters
import '../models/workout_log.dart'; // Import the models
import '../services/api_service.dart'; // Import the ApiService
import 'package:dio/dio.dart';

class LogWorkoutScreen extends StatefulWidget {
  const LogWorkoutScreen({super.key});

  @override
  State<LogWorkoutScreen> createState() => _LogWorkoutScreenState();
}

class _LogWorkoutScreenState extends State<LogWorkoutScreen> {
  final _formKey = GlobalKey<FormState>();

  final List<String> _availableExercises = [
    'Squat',
    'Bench Press',
    'Deadlift',
    'Overhead Press',
    'Barbell Row',
    'Pull Up',
    'Lat Pulldown',
    'Leg Press',
  ];

  String? _selectedExerciseName;
  final _repsController = TextEditingController();
  final _weightController = TextEditingController();
  final List<ExerciseLog> _loggedExercises = [];

  bool _isSaving = false;
  String? _saveError;

  ExerciseLog _findOrCreateExerciseLog(String name) {
    final existingLog = _loggedExercises.cast<ExerciseLog?>().firstWhere(
      (log) => log?.name == name,
      orElse: () => null,
    );
    if (existingLog != null) {
      return existingLog;
    } else {
      final newLog = ExerciseLog(name: name);
      setState(() {
        _loggedExercises.add(newLog);
      });
      return newLog;
    }
  }

  void _addSet() {
    final isValid = _formKey.currentState?.validate();
    if (isValid != true) return;

    if (_selectedExerciseName == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select an exercise first!'),
            backgroundColor: Colors.orange,
          ),
        );
      }
      return;
    }

    final reps = int.tryParse(_repsController.text);
    final weight = double.tryParse(_weightController.text);

    if (reps == null || weight == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Invalid number format for reps or weight.'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    final newSet = SetLog(reps: reps, weight: weight);
    final exerciseLog = _findOrCreateExerciseLog(_selectedExerciseName!);

    setState(() {
      exerciseLog.sets.add(newSet);
      _repsController.clear();
      _weightController.clear();
    });

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Set added to $_selectedExerciseName'),
          duration: const Duration(seconds: 1),
          backgroundColor: Colors.green,
        ),
      );
    }
    FocusScope.of(context).unfocus();
  }

  void _removeSet(ExerciseLog exercise, SetLog setToRemove) {
    setState(() {
      exercise.sets.remove(setToRemove);
    });
  }

  Future<void> _saveWorkout() async {
    if (_loggedExercises.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cannot save an empty workout.'),
            backgroundColor: Colors.orange,
          ),
        );
      }
      return;
    }

    setState(() {
      _isSaving = true;
      _saveError = null;
    });

    final workoutToSave = WorkoutLog(
      timestamp: DateTime.now(),
      exercises: _loggedExercises,
    );

    try {
      await ApiService().saveWorkout(workoutToSave);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Workout saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      print("Error caught in UI during saveWorkout: $e");
      String errorMessage = e.toString();
      if (e is DioException && e.response?.data?['detail'] != null) {
        errorMessage = e.response!.data['detail'].toString();
      }

      if (mounted) {
        setState(() {
          _saveError = errorMessage;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Save Failed: $errorMessage'),
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
    _repsController.dispose();
    _weightController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Log New Workout'),
        actions: [
          _isSaving
              ? const Padding(
                  padding: EdgeInsets.only(right: 16.0),
                  child: Center(
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    ),
                  ),
                )
              : IconButton(
                  icon: const Icon(Icons.save),
                  tooltip: 'Save Workout',
                  onPressed: _saveWorkout,
                ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              DropdownButtonFormField<String>(
                value: _selectedExerciseName,
                hint: const Text('Select Exercise'),
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.fitness_center),
                ),
                items: _availableExercises.map((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  setState(() {
                    _selectedExerciseName = newValue;
                    FocusScope.of(context).unfocus();
                  });
                },
                validator: (value) =>
                    value == null ? 'Please select an exercise' : null,
              ),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _repsController,
                      decoration: const InputDecoration(
                        labelText: 'Reps',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                      inputFormatters: <TextInputFormatter>[
                        FilteringTextInputFormatter.digitsOnly
                      ],
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Enter reps';
                        }
                        if (int.tryParse(value) == null ||
                            int.parse(value) <= 0) {
                          return 'Invalid number';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _weightController,
                      decoration: const InputDecoration(
                        labelText: 'Weight (kg)',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                      inputFormatters: <TextInputFormatter>[
                        FilteringTextInputFormatter.allow(
                          RegExp(r'^\d+\.?\d{0,2}'),
                        ),
                      ],
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Enter weight';
                        }
                        if (double.tryParse(value) == null ||
                            double.parse(value) < 0) {
                          return 'Invalid number';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                icon: const Icon(Icons.add),
                label: const Text('Add Set'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                onPressed: _addSet,
              ),
              const SizedBox(height: 16),
              if (_saveError != null)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Text(
                    'Save failed: $_saveError',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
              const SizedBox(height: 8),
              const Text(
                'Current Workout Log:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const Divider(),
              Expanded(
                child: _loggedExercises.isEmpty
                    ? const Center(
                        child: Text('No exercises logged yet.'),
                      )
                    : ListView.builder(
                        itemCount: _loggedExercises.length,
                        itemBuilder: (context, exerciseIndex) {
                          final exercise = _loggedExercises[exerciseIndex];
                          return Card(
                            margin: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Padding(
                              padding: const EdgeInsets.all(8.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    exercise.name,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  ListView.builder(
                                    shrinkWrap: true,
                                    physics:
                                        const NeverScrollableScrollPhysics(),
                                    itemCount: exercise.sets.length,
                                    itemBuilder: (context, setIndex) {
                                      final set = exercise.sets[setIndex];
                                      return ListTile(
                                        dense: true,
                                        contentPadding: EdgeInsets.zero,
                                        leading: CircleAvatar(
                                          radius: 12,
                                          child: Text('${setIndex + 1}'),
                                        ),
                                        title: Text(
                                          '${set.reps} reps @ ${set.weight} kg',
                                        ),
                                        trailing: IconButton(
                                          icon: const Icon(
                                            Icons.delete_outline,
                                            color: Colors.redAccent,
                                            size: 20,
                                          ),
                                          tooltip: 'Remove Set',
                                          onPressed: () =>
                                              _removeSet(exercise, set),
                                          padding: EdgeInsets.zero,
                                          constraints: const BoxConstraints(),
                                        ),
                                      );
                                    },
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
