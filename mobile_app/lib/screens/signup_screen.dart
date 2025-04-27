// lib/screens/signup_screen.dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

// Import login screen if needed for fallback navigation (though pop is primary)
// import 'login_screen.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _fullNameController = TextEditingController(); // Controller for Full Name
  bool _isLoading = false;
  String? _errorMessage;

  // Use Supabase client instance directly
  final _supabase = Supabase.instance.client;

  Future<void> _signUp() async {
    // Validate all form fields
    final isValid = _formKey.currentState?.validate();
    if (isValid != true) {
      return;
    }
    // Password match is already checked by the validator

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // Attempt signup with Supabase
      final AuthResponse res = await _supabase.auth.signUp(
        email: _emailController.text.trim(),
        password: _passwordController.text.trim(),
        data: {
          'full_name': _fullNameController.text.trim(),
        },
      );

      final session = res.session;
      final user = res.user;

      // Use 'mounted' check before showing Snackbar or navigating
      if (!mounted) return;

      if (user != null && session == null) {
        // Email confirmation likely required
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please check your email for confirmation link!'),
            backgroundColor: Colors.orange,
          ),
        );
        // Go back to login screen after showing message
        if (Navigator.canPop(context)) {
           Navigator.pop(context);
        }

      } else if (user != null && session != null) {
        // Signup successful & user is logged in (auto-confirm is likely ON)
        // AuthGate will detect the session and navigate to HomeScreen automatically.
        // Optionally show a success message before AuthGate navigates.
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Signup successful! Redirecting...'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2), // Shorter duration
          ),
        );
        // No explicit navigation needed here, AuthGate handles it.
      } else {
        // Less likely scenario
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
                'Signup status unclear. Please check email or try logging in.'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } on AuthException catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "Sign up failed: ${e.message}";
        });
      }
      print("Sign up error: ${e.message}");
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "An unexpected error occurred.";
        });
      }
      print("Sign up unexpected error: $e");
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _fullNameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Added a subtle background color variation
      backgroundColor: Theme.of(context).colorScheme.surfaceContainerLowest,
      appBar: AppBar(
          title: const Text('Sign Up'),
          // Optional: remove elevation for a flatter look matching body
          // elevation: 0,
          // backgroundColor: Colors.transparent,
          ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                const Icon(Icons.person_add_alt_1,
                    size: 80, color: Colors.deepPurple),
                const SizedBox(height: 20),
                Text(
                  'Create Account',
                  style: Theme.of(context).textTheme.headlineMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 30),

                // Full Name Field
                TextFormField(
                  controller: _fullNameController,
                  decoration: const InputDecoration(labelText: 'Full Name'),
                  textCapitalization: TextCapitalization.words,
                  textInputAction: TextInputAction.next,
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return 'Please enter your name';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Email Field
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'Email'),
                  keyboardType: TextInputType.emailAddress,
                  autocorrect: false,
                  textInputAction: TextInputAction.next,
                  validator: (value) {
                    if (value == null ||
                        value.trim().isEmpty ||
                        !value.contains('@')) {
                      return 'Please enter a valid email';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Password Field
                TextFormField(
                  controller: _passwordController,
                  decoration: const InputDecoration(labelText: 'Password'),
                  obscureText: true,
                  textInputAction: TextInputAction.next,
                  validator: (value) {
                    if (value == null || value.isEmpty || value.length < 6) {
                      return 'Password must be at least 6 characters';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Confirm Password Field
                TextFormField(
                  controller: _confirmPasswordController,
                  decoration:
                      const InputDecoration(labelText: 'Confirm Password'),
                  obscureText: true,
                   textInputAction: TextInputAction.done, // Submit form on done
                   onFieldSubmitted: (_) => _isLoading ? null : _signUp(), // Allow submitting
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please confirm your password';
                    }
                    if (value != _passwordController.text) {
                      return 'Passwords do not match';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                // Error Message Display
                if (_errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Text(
                      _errorMessage!,
                      style: TextStyle(
                          color: Theme.of(context).colorScheme.error),
                      textAlign: TextAlign.center,
                    ),
                  ),

                // Sign Up Button
                _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: _signUp,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: const Text('Sign Up'),
                      ),
                const SizedBox(height: 16),

                // Link back to Sign In
                TextButton(
                  onPressed: _isLoading
                      ? null
                      : () {
                          // Use Navigator.pop to go back to the Login screen
                          if (Navigator.canPop(context)) {
                            Navigator.pop(context);
                          }
                        },
                  child: const Text('Already have an account? Sign In'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}