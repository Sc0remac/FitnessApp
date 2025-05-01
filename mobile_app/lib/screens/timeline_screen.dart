// lib/screens/timeline_screen.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/workout_log.dart';
import '../models/mood_log.dart';
import '../services/api_service.dart';
import '../widgets/common/loading_indicator.dart';
import '../widgets/common/error_display.dart';

// Combined item type for the timeline
class TimelineItem implements Comparable<TimelineItem> {
  final DateTime timestamp; // Common NON-NULLABLE timestamp for sorting/display
  final dynamic data;
  final String type;

  TimelineItem({required this.timestamp, required this.data, required this.type});

  @override
  int compareTo(TimelineItem other) => other.timestamp.compareTo(timestamp);
}

class TimelineScreen extends StatefulWidget {
  const TimelineScreen({super.key});

  @override
  State<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends State<TimelineScreen> {
  late Future<List<TimelineItem>> _fetchTimelineFuture;
  final DateFormat _listDateFormat = DateFormat.yMMMd().add_jm();

  @override
  void initState() {
    super.initState();
    _fetchTimelineFuture = _loadTimelineData();
  }

  Future<List<TimelineItem>> _loadTimelineData() async {
    print("TimelineScreen: Loading timeline data...");
    try {
      final results = await Future.wait([
        ApiService().fetchWorkouts(limit: 100),
        ApiService().fetchMoods(limit: 100),
      ]);

      final List<WorkoutLog> workouts = results[0] as List<WorkoutLog>? ?? [];
      final List<MoodLog> moods = results[1] as List<MoodLog>? ?? [];
      print("TimelineScreen: Fetched ${workouts.length} workouts, ${moods.length} moods.");

      List<TimelineItem> combinedItems = [];

      // --- UPDATED “Process Workouts” LOOP ---
      for (var workout in workouts) {
        // Use createdAt if available, otherwise timestamp; assert non-null
        final DateTime itemTimestamp = (workout.createdAt ?? workout.timestamp)!;
        combinedItems.add(TimelineItem(
          timestamp: itemTimestamp,
          data: workout,
          type: 'workout',
        ));
      }
      // --- END UPDATED SECTION ---

      // Process Moods
      for (var mood in moods) {
        final DateTime itemTimestamp = (mood.createdAt ?? mood.timestamp)!;
        combinedItems.add(TimelineItem(
          timestamp: itemTimestamp,
          data: mood,
          type: 'mood',
        ));
      }

      print("TimelineScreen: Combined ${combinedItems.length} items.");
      combinedItems.sort();
      print("TimelineScreen: Items sorted.");

      return combinedItems;
    } catch (e, stackTrace) {
      print("Error loading timeline data: $e\n$stackTrace");
      throw Exception("Failed to load timeline data: ${e.toString()}");
    }
  }

  Future<void> _refreshTimeline() async {
    print("TimelineScreen: Refresh triggered.");
    setState(() {
      _fetchTimelineFuture = _loadTimelineData();
    });
    await _fetchTimelineFuture;
    print("TimelineScreen: Refresh complete.");
  }

  // --- Widget building methods ---

  Widget _buildWorkoutItem(WorkoutLog workout) {
    String summary = workout.exercises
        .map((ex) => '${ex.name} (${ex.sets.length} set${ex.sets.length != 1 ? 's' : ''})')
        .join(', ');
    if (summary.length > 60) {
      summary = '${summary.substring(0, 57)}...';
    }

    final DateTime displayTimestamp = (workout.createdAt ?? workout.timestamp)!;
    final String tsText = _listDateFormat.format(displayTimestamp.toLocal());

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
      elevation: 1.5,
      color: Colors.blueGrey.shade50,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.blueGrey.shade100,
          child: const Icon(
            Icons.fitness_center,
            size: 20,
            color: Colors.blueGrey,
          ),
          radius: 20,
        ),
        title: Text("Workout Logged", style: Theme.of(context).textTheme.titleMedium),
        subtitle: Text(summary.isEmpty ? 'Details unavailable' : summary),
        trailing: Text(tsText, style: Theme.of(context).textTheme.bodySmall),
        onTap: () { /* ... */ },
      ),
    );
  }

  Widget _buildMoodItem(MoodLog mood) {
    final sentimentColor = _getSentimentColor(mood.sentimentLabel);
    final sentimentIcon = _getSentimentIcon(mood.sentimentLabel);

    final DateTime displayTimestamp = (mood.createdAt ?? mood.timestamp)!;
    final String tsText = _listDateFormat.format(displayTimestamp.toLocal());

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
      elevation: 1.5,
      color: Colors.teal.shade50,
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: sentimentColor.withOpacity(0.1),
          child: Icon(sentimentIcon, color: sentimentColor),
          radius: 20,
        ),
        title: Text(
          mood.sentimentSummary ?? mood.journalText ?? 'Mood Logged',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        subtitle: Text(
          'Score: ${mood.moodScore}/10'
          '${mood.sentimentLabel != null ? " | ${mood.sentimentLabel}" : ""}',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: Text(tsText, style: Theme.of(context).textTheme.bodySmall),
        onTap: () {
          showDialog(
            context: context,
            builder: (alertDialogContext) => AlertDialog(
              title: Text('Mood Entry Details ($tsText)'),
              content: SingleChildScrollView(
                /* ... Details ... */
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(alertDialogContext),
                  child: const Text('Close'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Color _getSentimentColor(String? sentiment) {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return Colors.green.shade600;
      case 'negative':
        return Colors.red.shade600;
      case 'neutral':
        return Colors.grey.shade600;
      default:
        return Colors.grey.shade400;
    }
  }

  IconData _getSentimentIcon(String? sentiment) {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return Icons.sentiment_very_satisfied;
      case 'negative':
        return Icons.sentiment_dissatisfied;
      case 'neutral':
        return Icons.sentiment_neutral;
      default:
        return Icons.radio_button_unchecked;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Timeline / History')),
      body: RefreshIndicator(
        onRefresh: _refreshTimeline,
        child: FutureBuilder<List<TimelineItem>>(
          future: _fetchTimelineFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const LoadingIndicator();
            }
            if (snapshot.hasError) {
              return ErrorDisplay(errorMessage: snapshot.error.toString());
            }
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return const Center(
                child: Text(
                  'No activity logged yet.\nTry logging a workout or mood!',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, color: Colors.grey),
                ),
              );
            }

            final items = snapshot.data!;
            return ListView.separated(
              padding: const EdgeInsets.symmetric(vertical: 8.0),
              itemCount: items.length,
              separatorBuilder: (context, index) =>
                  const Divider(height: 1, thickness: 0.5, indent: 16, endIndent: 16),
              itemBuilder: (context, index) {
                final item = items[index];
                if (item.type == 'workout' && item.data is WorkoutLog) {
                  return _buildWorkoutItem(item.data as WorkoutLog);
                } else if (item.type == 'mood' && item.data is MoodLog) {
                  return _buildMoodItem(item.data as MoodLog);
                } else {
                  print(
                    "TimelineScreen: Encountered unknown item type '${item.type}' at index $index",
                  );
                  return ListTile(title: Text('Unknown item type: ${item.type}'));
                }
              },
            );
          },
        ),
      ),
    );
  }
}

// --- Reusable Widgets ---
class LoadingIndicator extends StatelessWidget {
  const LoadingIndicator({super.key});
  @override
  Widget build(BuildContext context) => const Center(child: CircularProgressIndicator());
}

class ErrorDisplay extends StatelessWidget {
  final String errorMessage;
  const ErrorDisplay({super.key, required this.errorMessage});
  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(
            'Error: $errorMessage',
            style: TextStyle(color: Theme.of(context).colorScheme.error, fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ),
      );
}
