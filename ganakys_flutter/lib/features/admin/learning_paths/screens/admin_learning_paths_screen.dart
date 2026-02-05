import 'package:flutter/material.dart';

class AdminLearningPathsScreen extends StatelessWidget {
  const AdminLearningPathsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.route, size: 80, color: colorScheme.outline),
            const SizedBox(height: 24),
            Text('Learning Paths', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text(
              'This feature will be available soon.\nYou will be able to create curated learning paths, sequence courses, and guide students through structured curricula.',
              style: TextStyle(color: colorScheme.onSurfaceVariant, fontSize: 16),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
