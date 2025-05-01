// lib/models/mood_log.dart
class MoodLog {
  final String? id; // Nullable for creation, non-null when read from DB
  final String userId; // Non-null when reading/creating associated with user
  final int moodScore; // 1-10
  final String? journalText;
  final String? sentimentLabel;
  final int? sentimentIntensity;
  final String? sentimentSummary;
  final DateTime timestamp; // When logged
  final DateTime? createdAt; // When DB record was created

  MoodLog({
    this.id,
    required this.userId, // Required when creating representation
    required this.moodScore,
    this.journalText,
    this.sentimentLabel,
    this.sentimentIntensity,
    this.sentimentSummary,
    required this.timestamp,
    this.createdAt,
  });

  // Factory constructor for parsing JSON from API/DB
  factory MoodLog.fromJson(Map<String, dynamic> json) {
    return MoodLog(
      id: json['id'] as String?, // Should exist in read context
      userId: json['user_id'] as String? ?? '', // Should exist in read context
      moodScore: json['mood_score'] as int? ?? 0, // Default or throw needed
      journalText: json['journal_text'] as String?,
      sentimentLabel: json['sentiment_label'] as String?,
      sentimentIntensity: json['sentiment_intensity'] as int?,
      sentimentSummary: json['sentiment_summary'] as String?,
      timestamp: DateTime.tryParse(json['timestamp'] as String? ?? '') ?? DateTime.now(),
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? ''),
    );
  }

  // Method to convert to JSON for sending TO API (Create)
  // Note: Excludes fields set by backend/db (id, userId, createdAt, timestamp if server sets it)
  // Also excludes sentiment fields, as analysis happens on backend
  Map<String, dynamic> toJsonForCreate() => {
        'mood_score': moodScore,
        'journal_text': journalText,
         // Optionally send timestamp if client determines it, otherwise backend sets it
         // 'timestamp': timestamp.toUtc().toIso8601String(),
      };
}