import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/client_provider.dart';

final _userDetailProvider = FutureProvider.autoDispose.family<Map<String, dynamic>?, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminGetUser(userId);
});

class AdminUserDetailScreen extends ConsumerWidget {
  final int userId;

  const AdminUserDetailScreen({super.key, required this.userId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final userAsync = ref.watch(_userDetailProvider(userId));

    return userAsync.when(
      data: (user) {
        if (user == null) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.error, size: 64, color: colorScheme.error),
                const SizedBox(height: 16),
                Text('User not found', style: theme.textTheme.titleLarge),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => context.go('/admin/users'),
                  child: const Text('Back to Users'),
                ),
              ],
            ),
          );
        }

        final name = user['name'] as String? ?? 'Unknown';
        final email = user['email'] as String? ?? '';
        final role = user['role'] as String? ?? 'student';
        final subscriptionStatus = user['subscriptionStatus'] as String?;
        final isBanned = user['isActive'] == false;
        final createdAt = user['createdAt'] as String?;
        final enrollments = (user['enrollments'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final payments = (user['payments'] as List?)?.cast<Map<String, dynamic>>() ?? [];

        return SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(
                children: [
                  IconButton(
                    onPressed: () => context.go('/admin/users'),
                    icon: const Icon(Icons.arrow_back),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      name,
                      style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              // User info card
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          CircleAvatar(
                            radius: 32,
                            backgroundColor: isBanned ? colorScheme.errorContainer : colorScheme.primaryContainer,
                            child: Text(
                              name.isNotEmpty ? name[0].toUpperCase() : '?',
                              style: TextStyle(
                                fontSize: 24,
                                color: isBanned ? colorScheme.onErrorContainer : colorScheme.onPrimaryContainer,
                              ),
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(name, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                                Text(email, style: theme.textTheme.bodyMedium),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    Chip(
                                      label: Text(role[0].toUpperCase() + role.substring(1)),
                                      visualDensity: VisualDensity.compact,
                                    ),
                                    if (subscriptionStatus != null) ...[
                                      const SizedBox(width: 8),
                                      Chip(
                                        label: Text(subscriptionStatus),
                                        visualDensity: VisualDensity.compact,
                                      ),
                                    ],
                                    if (isBanned) ...[
                                      const SizedBox(width: 8),
                                      Chip(
                                        label: const Text('Banned', style: TextStyle(color: Colors.white)),
                                        backgroundColor: colorScheme.error,
                                        visualDensity: VisualDensity.compact,
                                      ),
                                    ],
                                  ],
                                ),
                                if (createdAt != null)
                                  Text('Joined: $createdAt', style: theme.textTheme.bodySmall),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 8),
                      // Action buttons
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          OutlinedButton.icon(
                            onPressed: () => _changeRole(context, ref, userId, role),
                            icon: const Icon(Icons.admin_panel_settings, size: 18),
                            label: const Text('Change Role'),
                          ),
                          OutlinedButton.icon(
                            onPressed: () => _toggleBan(context, ref, userId, isBanned),
                            icon: Icon(
                              isBanned ? Icons.check_circle : Icons.block,
                              size: 18,
                              color: isBanned ? Colors.green : colorScheme.error,
                            ),
                            label: Text(isBanned ? 'Unban' : 'Ban'),
                          ),
                          OutlinedButton.icon(
                            onPressed: () => _forcePasswordReset(context, ref, userId),
                            icon: const Icon(Icons.lock_reset, size: 18),
                            label: const Text('Force Password Reset'),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              // Enrolled courses
              Text(
                'Enrolled Courses (${enrollments.length})',
                style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              if (enrollments.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Text('No enrollments', style: TextStyle(color: colorScheme.onSurfaceVariant)),
                    ),
                  ),
                )
              else
                ...enrollments.map((e) {
                  final courseName = e['courseTitle'] as String? ?? 'Unknown Course';
                  final progress = (e['progressPercent'] as num?)?.toDouble() ?? 0;
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: const Icon(Icons.book),
                      title: Text(courseName),
                      subtitle: LinearProgressIndicator(
                        value: progress / 100,
                        backgroundColor: colorScheme.surfaceContainerHighest,
                      ),
                      trailing: Text('${progress.toStringAsFixed(0)}%'),
                    ),
                  );
                }),
              const SizedBox(height: 24),
              // Payment history
              Text(
                'Payment History (${payments.length})',
                style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              if (payments.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Text('No payments', style: TextStyle(color: colorScheme.onSurfaceVariant)),
                    ),
                  ),
                )
              else
                ...payments.map((p) {
                  final amount = p['amount'] ?? 0;
                  final status = p['status'] as String? ?? 'unknown';
                  final createdDate = p['createdAt'] as String? ?? '';
                  final planName = p['planName'] as String? ?? 'N/A';
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: const Icon(Icons.payment),
                      title: Text('\$$amount - $planName'),
                      subtitle: Text(createdDate),
                      trailing: Chip(
                        label: Text(status, style: const TextStyle(fontSize: 11)),
                        visualDensity: VisualDensity.compact,
                      ),
                    ),
                  );
                }),
            ],
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error, size: 48, color: colorScheme.error),
            const SizedBox(height: 12),
            Text('Failed to load user: $error'),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () => ref.invalidate(_userDetailProvider(userId)),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _changeRole(BuildContext context, WidgetRef ref, int userId, String currentRole) async {
    final roles = ['student', 'instructor', 'admin'];
    final newRole = await showDialog<String>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Change Role'),
        children: roles
            .map((r) => SimpleDialogOption(
                  onPressed: () => Navigator.pop(ctx, r),
                  child: Row(
                    children: [
                      if (r == currentRole) const Icon(Icons.check, size: 18) else const SizedBox(width: 18),
                      const SizedBox(width: 8),
                      Text(r[0].toUpperCase() + r.substring(1)),
                    ],
                  ),
                ))
            .toList(),
      ),
    );
    if (newRole == null || newRole == currentRole) return;
    if (!context.mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateUserRole(userId, newRole);
      ref.invalidate(_userDetailProvider(userId));
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Role changed to $newRole')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  Future<void> _toggleBan(BuildContext context, WidgetRef ref, int userId, bool isBanned) async {
    final action = isBanned ? 'unban' : 'ban';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('${action[0].toUpperCase()}${action.substring(1)} User'),
        content: Text('Are you sure you want to $action this user?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: Text(action[0].toUpperCase() + action.substring(1))),
        ],
      ),
    );
    if (confirmed != true) return;
    if (!context.mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminBanUser(userId, !isBanned);
      ref.invalidate(_userDetailProvider(userId));
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _forcePasswordReset(BuildContext context, WidgetRef ref, int userId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Force Password Reset'),
        content: const Text('This will force the user to reset their password.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Reset')),
        ],
      ),
    );
    if (confirmed != true) return;
    if (!context.mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminForcePasswordReset(userId);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Password reset initiated')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }
}
