// lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart'; // for kDebugMode
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:supabase_flutter/supabase_flutter.dart'; // To get the auth token

// Import models
import '../models/workout_log.dart';
import '../models/mood_log.dart';

class ApiService {
  // --- Singleton Pattern ---
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() {
    _initializeDio();
  }

  late Dio _dio; // Dio instance

  // --- Base URL ---
  // Read from .env, provide sensible fallback for local dev
  final String _baseUrl = dotenv.env['API_BASE_URL'] ??
      (defaultTargetPlatform == TargetPlatform.android
          ? 'http://10.0.2.2:8000/api/v1' // Android Emulator
          : 'http://localhost:8000/api/v1'); // iOS Simulator / Other

  // --- Initialize Dio with Interceptors ---
  void _initializeDio() {
    final options = BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      // Ensure Dio throws errors for non-2xx status codes
      validateStatus: (status) {
        return status != null && status >= 200 && status < 300;
      },
    );

    _dio = Dio(options);

    // --- Auth Token & Logging Interceptor ---
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final session = Supabase.instance.client.auth.currentSession;
        if (session != null) {
          options.headers['Authorization'] = 'Bearer ${session.accessToken}';
          if (kDebugMode) { // Only print in debug mode
             print('>>> [Dio Request] Added Auth Token');
          }
        } else {
           if (kDebugMode) {
             print('>>> [Dio Request] No active session, token not added.');
          }
        }
        if (kDebugMode) {
           print('>>> [Dio Request] ${options.method} ${options.uri}');
           // Optionally log request data (be careful with sensitive info)
           // if (options.data != null) { print('>>> [Dio Request] Data: ${options.data}'); }
        }
        return handler.next(options); // Continue
      },
      onResponse: (response, handler) {
         if (kDebugMode) {
            print('<<< [Dio Response] ${response.statusCode} ${response.requestOptions.uri}');
            // Optionally log response data for debugging
            // print('<<< [Dio Response] Data: ${response.data}');
         }
        return handler.next(response); // Continue
      },
      onError: (DioException e, handler) {
         if (kDebugMode) {
            print('<<< [Dio Error] ${e.response?.statusCode} ${e.requestOptions.uri}');
            print('<<< [Dio Error] Message: ${e.message}');
            if (e.response?.data != null) { print('<<< [Dio Error] Data: ${e.response?.data}'); }
            if (e.response?.statusCode == 401) {
              print('<<< [Dio Error] Unauthorized (401) detected.');
              // TODO: Consider global logout trigger / refresh token logic here later
            }
         }
        // Let the error propagate to be handled by the calling code
        return handler.next(e);
      },
    ));
  }

  // --- Helper to Extract Detail from Dio Error ---
  String _extractDetailFromDioError(DioException e, [String defaultMessage = "An API error occurred."]) {
     if (e.response?.data is Map && (e.response!.data as Map).containsKey('detail')) {
       return (e.response!.data as Map)['detail'].toString();
     }
     // Fallback to Dio error message or default
     return e.message ?? defaultMessage;
  }


  // --- API Methods ---

  /// Saves a workout log to the backend.
  Future<WorkoutLog> saveWorkout(WorkoutLog workout) async {
    const String endpoint = '/workouts/';
    try {
      final workoutJson = workout.toJson(); // Assuming toJson handles only needed fields for CREATE
      if (kDebugMode) { print(">>> Saving Workout Data: $workoutJson"); }

      final response = await _dio.post(endpoint, data: workoutJson);

      // Dio with validateStatus ensures statusCode is 2xx here
      if (response.data != null) {
         print("Workout saved successfully (Backend response received)");
         // Parse the response back into a fully populated WorkoutLog object
         return WorkoutLog.fromJson(response.data as Map<String, dynamic>);
      } else {
         // Should not happen with validateStatus if backend returns valid JSON on 201
         throw Exception('Workout saved, but backend returned no data.');
      }
    } on DioException catch (e) {
      final detail = _extractDetailFromDioError(e, "Could not save workout");
      print("API Error POST $endpoint: $detail");
      throw Exception('Failed to save workout: $detail');
    } catch (e) {
      print("Unexpected error POST $endpoint: $e");
      throw Exception('An unexpected error occurred while saving the workout.');
    }
  }

  /// Fetches a list of workout logs from the backend.
  Future<List<WorkoutLog>> fetchWorkouts({
    int skip = 0,
    int limit = 50,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
     const String endpoint = '/workouts/';
     try {
       final queryParams = <String, dynamic>{'skip': skip, 'limit': limit};
       if (startDate != null) { queryParams['start_date'] = startDate.toUtc().toIso8601String();}
       if (endDate != null) { queryParams['end_date'] = endDate.toUtc().toIso8601String(); }
       if (kDebugMode) { print(">>> Fetching workouts with params: $queryParams"); }

       final response = await _dio.get(endpoint, queryParameters: queryParams);

       // Dio with validateStatus ensures statusCode is 2xx
       if (response.data is List) {
         final workouts = (response.data as List)
             .map((item) {
                try { return WorkoutLog.fromJson(item as Map<String, dynamic>); }
                catch(e) { print("Error parsing workout item: $item, Error: $e"); return null; }
             })
             .whereType<WorkoutLog>()
             .toList();
         print("Fetched and parsed ${workouts.length} workouts successfully.");
         return workouts;
       } else {
         throw Exception('Invalid response format: Expected a list.');
       }
     } on DioException catch (e) {
       final detail = _extractDetailFromDioError(e, "Could not retrieve workout history");
       print("API Error GET $endpoint: $detail");
       throw Exception('Failed to fetch workouts: $detail');
     } catch (e) {
       print("Unexpected error GET $endpoint: $e");
       throw Exception('An unexpected error occurred while fetching workouts.');
     }
  }

  /// Saves a mood log (score + optional journal) to the backend.
  Future<MoodLog> saveMood(MoodLog moodLog) async {
    const String endpoint = '/moods/';
    try {
      final moodJson = moodLog.toJsonForCreate(); // Sends only needed fields
       if (kDebugMode) { print(">>> Sending Mood Data: $moodJson"); }

      final response = await _dio.post(endpoint, data: moodJson);

      if (response.data != null) {
        print("Mood saved successfully (Backend response received)");
        return MoodLog.fromJson(response.data as Map<String, dynamic>);
      } else {
         throw Exception('Mood saved, but backend returned no data.');
      }
    } on DioException catch (e) {
      final detail = _extractDetailFromDioError(e, "Could not save mood entry");
      print("API Error POST $endpoint: $detail");
      throw Exception('Failed to save mood: $detail');
    } catch (e) {
       print("Unexpected error POST $endpoint: $e");
       throw Exception('An unexpected error occurred while saving the mood entry.');
    }
  }

  /// Fetches mood history from the backend.
  Future<List<MoodLog>> fetchMoods({
    int skip = 0,
    int limit = 50,
  }) async {
    const String endpoint = '/moods/';
    try {
      final queryParams = <String, dynamic>{ 'skip': skip, 'limit': limit };
      if (kDebugMode) { print(">>> Fetching moods with params: $queryParams"); }

      final response = await _dio.get(endpoint, queryParameters: queryParams);

      if (response.data is List) {
        final moods = (response.data as List)
            .map((item) {
                try { return MoodLog.fromJson(item as Map<String, dynamic>); }
                catch (e) { print("Error parsing mood item: $item, Error: $e"); return null; }
            })
            .whereType<MoodLog>()
            .toList();
        print("Fetched and parsed ${moods.length} mood entries successfully.");
        return moods;
      } else {
         throw Exception('Invalid response format: Expected a list.');
      }
    } on DioException catch (e) {
       final detail = _extractDetailFromDioError(e, "Could not retrieve mood history");
       print("API Error GET $endpoint: $detail");
       throw Exception('Failed to fetch mood history: $detail');
    } catch (e) {
       print("Unexpected error GET $endpoint: $e");
       throw Exception('An unexpected error occurred while fetching mood history.');
    }
  }

  // --- TODO: Add methods for Spotify and Insights later ---
  // Future<String> getSpotifyAuthUrl() async { ... }
  // Future<void> handleSpotifyCallback(String code, String state) async { ... }
  // Future<List<SpotifyTrack>> fetchSpotifyTracks() async { ... }
  // Future<InsightData> fetchInsights() async { ... }

} // End ApiService class