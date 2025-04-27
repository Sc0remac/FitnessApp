import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart'; // Will add later if needed for non-auth state
import 'package:supabase_flutter/supabase_flutter.dart';

// Import your screen/widget files (will create these next)
import 'auth_gate.dart'; // Handles deciding which screen to show
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/signup_screen.dart';

Future<void> main() async {
  // Ensure Flutter bindings are initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Load environment variables
  await dotenv.load(fileName: ".env");

  // Initialize Supabase
  // Use null checks or assertions for environment variables
  final supabaseUrl = dotenv.env['SUPABASE_URL'];
  final supabaseAnonKey = dotenv.env['SUPABASE_ANON_KEY'];

  if (supabaseUrl == null || supabaseAnonKey == null) {
    // Handle error appropriately - maybe show an error screen or log
    print("Error: Supabase URL or Anon Key not found in .env file.");
    return; // Don't run the app if Supabase isn't configured
  }

  await Supabase.initialize(
    url: supabaseUrl,
    anonKey: supabaseAnonKey,
    // Optional: Specify auth options like storage if needed
    // authOptions: const FlutterAuthClientOptions(
    //   authFlowType: AuthFlowType.pkce, // PKCE is default and recommended
    // ),
  );

  runApp(const MyApp());
}

// Helper to access Supabase client instance easily
final supabase = Supabase.instance.client;

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FMMT App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
        // Optional: Define input decoration theme globally
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      darkTheme: ThemeData.dark().copyWith(
         colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple, brightness: Brightness.dark),
         inputDecorationTheme: InputDecorationTheme(
           border: OutlineInputBorder(
             borderRadius: BorderRadius.circular(8),
           ),
         ),
         useMaterial3: true,
      ),
      themeMode: ThemeMode.system, // Or ThemeMode.light / ThemeMode.dark
      // Use AuthGate as the home widget
      home: const AuthGate(),
      // Define routes for navigation (optional if using AuthGate only initially)
      // routes: {
      //   '/login': (context) => const LoginScreen(),
      //   '/signup': (context) => const SignupScreen(),
      //   '/home': (context) => const HomeScreen(),
      // },
    );
  }
}