// lib/widgets/common/error_display.dart
import 'package:flutter/material.dart';

class ErrorDisplay extends StatelessWidget {
  final String errorMessage;
  const ErrorDisplay({super.key, required this.errorMessage});

  @override
  Widget build(BuildContext context) {
    return Center(
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
}