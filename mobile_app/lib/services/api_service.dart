// lib/services/api_service.dart
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:supabase_flutter/supabase_flutter.dart'; // To get the auth token

import '../models/workout_log.dart'; // Import your Workout model

class ApiService {
  // --- Singleton Pattern ---
  // Makes sure we only have one instance of Dio and ApiService
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal() {
    _initializeDio();
  }

  late Dio _dio; // Dio instance

  // --- Base URL ---
  // Ensure VITE_ prefix isn't used here (that's for Vite frontend)
  // Just use the key defined in mobile_app/.env
  // Set a default fallback for safety.
  final String _baseUrl = dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';


  void _initializeDio() {
    final options = BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 20), // 10 seconds
      receiveTimeout: const Duration(seconds: 40), // 10 seconds
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    );

    _dio = Dio(options);

    // --- IMPORTANT: Add Supabase Auth Token Interceptor ---
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Get the current Supabase session
        final session = Supabase.instance.client.auth.currentSession;

        if (session != null) {
          // Add the Authorization header if user is logged in
          options.headers['Authorization'] = 'Bearer ${session.accessToken}';
          print('>>> [Dio Request] Added Auth Token'); // Debug print
        } else {
           print('>>> [Dio Request] No active session, token not added.'); // Debug print
        }
        print('>>> [Dio Request] ${options.method} ${options.uri}'); // Debug print
        return handler.next(options); // Continue with the request
      },
      onResponse: (response, handler) {
         print('<<< [Dio Response] ${response.statusCode} ${response.requestOptions.uri}'); // Debug print
        // Optionally process response data globally
        return handler.next(response); // Continue with the response
      },
      onError: (DioException e, handler) {
         print('<<< [Dio Error] ${e.response?.statusCode} ${e.requestOptions.uri}'); // Debug print
         print('<<< [Dio Error] Message: ${e.message}'); // Debug print
         if (e.response?.statusCode == 401) {
            // Handle unauthorized errors globally if needed
            // e.g., trigger logout, refresh token (more complex)
            print('<<< [Dio Error] Unauthorized (401) detected.');
            // Consider navigating user to login or showing a message
         }
        return handler.next(e); // Continue with the error
      },
    ));
  }

  // --- API Methods ---

  /// Saves a workout log to the backend.
  Future<WorkoutLog> saveWorkout(WorkoutLog workout) async {
    try {
      // Convert the WorkoutLog object to JSON using its toJson method
      final workoutJson = workout.toJson();

      final response = await _dio.post(
        '/workouts/', // Endpoint defined in FastAPI router
        data: workoutJson,
      );

      if (response.statusCode == 201) {
         // Assuming the backend returns the created workout (with ID, timestamps etc.)
         // We need a fromJson factory constructor in WorkoutLog model
         // For now, let's just return the original log as confirmation
         // TODO: Add WorkoutLog.fromJson and parse response.data
         print("Workout saved successfully (Backend response): ${response.data}");
         return workout; // Or ideally WorkoutLog.fromJson(response.data);
      } else {
        // Handle non-201 success codes if necessary
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          error: 'Failed to save workout: Status code ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      // Handle Dio specific errors (network, timeout, 4xx, 5xx)
       print("API Error saving workout: ${e.response?.data ?? e.message}");
      // Re-throw a more specific or user-friendly error if needed
      throw Exception('Failed to save workout: ${e.response?.data?['detail'] ?? e.message}');
    } catch (e) {
       // Handle other potential errors
        print("Unexpected error saving workout: $e");
       throw Exception('An unexpected error occurred while saving the workout.');
    }
  }

  // --- Add methods for GET /workouts, GET /moods, POST /moods, etc. later ---
  /*
  Future<List<WorkoutLog>> fetchWorkouts() async {
     try {
       final response = await _dio.get('/workouts/');
       if (response.statusCode == 200 && response.data is List) {
          // TODO: Implement WorkoutLog.fromJson and map the list
          // return (response.data as List).map((item) => WorkoutLog.fromJson(item)).toList();
          print("Fetched workouts (raw): ${response.data}");
          return []; // Placeholder
       } else {
          throw DioException(requestOptions: response.requestOptions, response: response);
       }
     } catch (e) {
        print("Error fetching workouts: $e");
        throw Exception('Failed to fetch workouts');
     }
  }
  */

}