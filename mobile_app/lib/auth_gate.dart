import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
// Optionally import signup screen if you want a switcher widget
// import 'screens/signup_screen.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    // Use a StreamBuilder to listen to Supabase auth state changes
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (context, snapshot) {
        // Check if snapshot has data (stream has emitted an event)
        if (snapshot.hasData) {
          final session = snapshot.data?.session;

          // If session is null, user is logged out -> show Login/Signup
          if (session == null) {
            // Simple approach: Just show LoginScreen. User can navigate or
            // SignupScreen could be reached via a button on LoginScreen.
             // OR: Could use a stateful widget here to switch between Login and Signup
             return const LoginScreen();
             // Example stateful switcher idea (more complex):
             // return AuthScreenSwitcher(); // A widget managing Login/Signup display state
          } else {
            // If session exists, user is logged in -> show HomeScreen
            return const HomeScreen();
          }
        }

        // While waiting for the first auth event, show a loading indicator
        // This prevents flickering between login and home screens on app start
        return const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        );
      },
    );
  }
}

// --- Optional: Example State Management for Login/Signup Switch ---
// If you want a single screen area that switches between login and signup forms
// without using Navigator, you could use Provider or another state manager.

/*
// 1. Define a state notifier
class AuthScreenState extends ChangeNotifier {
  bool _showLogin = true;
  bool get showLogin => _showLogin;

  void toggleScreen() {
    _showLogin = !_showLogin;
    notifyListeners();
  }
}

// 2. Wrap Login/Signup area with ChangeNotifierProvider in main.dart or above AuthGate
//    ChangeNotifierProvider(create: (_) => AuthScreenState(), child: const AuthGate()),

// 3. Create a wrapper widget that listens and switches
class AuthScreenSwitcher extends StatelessWidget {
  const AuthScreenSwitcher({super.key});

  @override
  Widget build(BuildContext context) {
    final showLogin = context.watch<AuthScreenState>().showLogin;
    // You'd pass the toggle function down to buttons in Login/Signup screens
    if (showLogin) {
      return LoginScreen(); // Pass toggle callback: onGoToSignup: context.read<AuthScreenState>().toggleScreen
    } else {
      return SignupScreen(); // Pass toggle callback: onGoToSignin: context.read<AuthScreenState>().toggleScreen
    }
  }
}

// 4. Use this AuthScreenSwitcher instead of LoginScreen in AuthGate when session == null
*/