import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ganakys_client/ganakys_client.dart' hide Notification;
import 'package:ganakys_client/ganakys_client.dart' as proto show Notification;
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/theme_provider.dart';
import '../../../core/client_provider.dart';

// --- Providers ---

final _profileProvider =
    FutureProvider.family<Map<String, dynamic>?, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.profile.getProfile(userId);
});

final _notificationsProvider =
    FutureProvider.family<List<proto.Notification>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.profile.getNotifications(userId);
});

final _wishlistProvider =
    FutureProvider.family<List<Map<String, dynamic>>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.profile.getWishlist(userId);
});

// --- Screen ---

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _nameController = TextEditingController();
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _deletePasswordController = TextEditingController();
  bool _isEditingName = false;
  bool _isSavingName = false;
  bool _isChangingPassword = false;
  bool _isExporting = false;

  @override
  void dispose() {
    _nameController.dispose();
    _currentPasswordController.dispose();
    _newPasswordController.dispose();
    _deletePasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(authProvider);
    final userId = auth.user?.id;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    if (userId == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final notificationsAsync = ref.watch(_notificationsProvider(userId));
    final wishlistAsync = ref.watch(_wishlistProvider(userId));

    final unreadCount = notificationsAsync.whenOrNull(
          data: (list) => list.where((n) => !n.isRead).length,
        ) ??
        0;

    return SingleChildScrollView(
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 48 : 16,
        vertical: 24,
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Profile',
                style: theme.textTheme.headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),

              // Profile header card
              _ProfileHeader(auth: auth),
              const SizedBox(height: 16),

              // Edit Profile
              _EditProfileCard(
                auth: auth,
                nameController: _nameController,
                isEditing: _isEditingName,
                isSaving: _isSavingName,
                onEditToggle: () {
                  setState(() {
                    _isEditingName = !_isEditingName;
                    if (_isEditingName) {
                      _nameController.text = auth.user?.name ?? '';
                    }
                  });
                },
                onSave: () => _saveProfile(userId),
              ),
              const SizedBox(height: 16),

              // Theme selector
              Card(
                child: ListTile(
                  leading: const Icon(Icons.dark_mode),
                  title: const Text('Theme'),
                  trailing: SegmentedButton<ThemeMode>(
                    segments: const [
                      ButtonSegment(
                        value: ThemeMode.light,
                        icon: Icon(Icons.light_mode),
                      ),
                      ButtonSegment(
                        value: ThemeMode.system,
                        icon: Icon(Icons.auto_mode),
                      ),
                      ButtonSegment(
                        value: ThemeMode.dark,
                        icon: Icon(Icons.dark_mode),
                      ),
                    ],
                    selected: {ref.watch(themeProvider)},
                    onSelectionChanged: (modes) {
                      ref.read(themeProvider.notifier).setTheme(modes.first);
                    },
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Notifications
              Card(
                child: ListTile(
                  leading: Badge(
                    isLabelVisible: unreadCount > 0,
                    label: Text('$unreadCount'),
                    child: const Icon(Icons.notifications),
                  ),
                  title: const Text('Notifications'),
                  subtitle: unreadCount > 0
                      ? Text('$unreadCount unread')
                      : const Text('All caught up'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _showNotificationsSheet(
                    context,
                    notificationsAsync,
                    userId,
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Change Password
              _ChangePasswordCard(
                currentPasswordController: _currentPasswordController,
                newPasswordController: _newPasswordController,
                isChanging: _isChangingPassword,
                onSubmit: () => _changePassword(userId),
              ),
              const SizedBox(height: 16),

              // Wishlist
              _WishlistCard(wishlistAsync: wishlistAsync),
              const SizedBox(height: 16),

              // Data & Privacy
              Card(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                      child: Text(
                        'Data & Privacy',
                        style: theme.textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ),
                    ListTile(
                      leading: const Icon(Icons.download),
                      title: const Text('Export My Data'),
                      subtitle:
                          const Text('Download all your data as a file'),
                      trailing: _isExporting
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child:
                                  CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.chevron_right),
                      onTap: _isExporting
                          ? null
                          : () => _exportData(userId),
                    ),
                    const Divider(height: 1),
                    ListTile(
                      leading:
                          Icon(Icons.delete_forever, color: colorScheme.error),
                      title: Text(
                        'Delete Account',
                        style: TextStyle(color: colorScheme.error),
                      ),
                      subtitle: const Text(
                          'Permanently delete your account and data'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () =>
                          _showDeleteAccountDialog(context, userId),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Logout
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    ref.read(authProvider.notifier).logout();
                    context.go('/');
                  },
                  icon: const Icon(Icons.logout),
                  label: const Text('Sign Out'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: colorScheme.error,
                    side: BorderSide(color: colorScheme.error),
                  ),
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _saveProfile(int userId) async {
    setState(() => _isSavingName = true);
    try {
      final client = ref.read(clientProvider);
      await client.profile.updateProfile(
        userId,
        _nameController.text.trim(),
        null,
        null,
        null,
      );
      ref.invalidate(_profileProvider(userId));
      if (mounted) {
        setState(() {
          _isEditingName = false;
          _isSavingName = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isSavingName = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update profile: $e')),
        );
      }
    }
  }

  Future<void> _changePassword(int userId) async {
    if (_currentPasswordController.text.isEmpty ||
        _newPasswordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in both password fields')),
      );
      return;
    }
    if (_newPasswordController.text.length < 8) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('New password must be at least 8 characters')),
      );
      return;
    }
    setState(() => _isChangingPassword = true);
    try {
      final client = ref.read(clientProvider);
      final result = await client.profile.changePassword(
        userId,
        _currentPasswordController.text,
        _newPasswordController.text,
      );
      if (mounted) {
        setState(() => _isChangingPassword = false);
        if (result['success'] == true) {
          _currentPasswordController.clear();
          _newPasswordController.clear();
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Password changed successfully')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content:
                  Text(result['error'] as String? ?? 'Failed to change password'),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isChangingPassword = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  Future<void> _exportData(int userId) async {
    setState(() => _isExporting = true);
    try {
      final client = ref.read(clientProvider);
      final result = await client.profile.exportData(userId);
      if (mounted) {
        setState(() => _isExporting = false);
        if (result['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content:
                    Text('Data export prepared. Check your email for download link.')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to export data')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isExporting = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  void _showDeleteAccountDialog(BuildContext context, int userId) {
    _deletePasswordController.clear();
    showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('Delete Account'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'This action is irreversible. All your data will be permanently deleted.',
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _deletePasswordController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Enter your password to confirm',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(ctx).pop(),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                if (_deletePasswordController.text.isEmpty) return;
                final scaffoldMessenger = ScaffoldMessenger.of(context);
                final router = GoRouter.of(context);
                Navigator.of(ctx).pop();
                try {
                  final client = ref.read(clientProvider);
                  final result = await client.profile.requestDeletion(
                    userId,
                    _deletePasswordController.text,
                  );
                  if (mounted) {
                    if (result['success'] == true) {
                      ref.read(authProvider.notifier).logout();
                      router.go('/');
                    } else {
                      scaffoldMessenger.showSnackBar(
                        const SnackBar(
                            content: Text('Failed to delete account')),
                      );
                    }
                  }
                } catch (e) {
                  if (mounted) {
                    scaffoldMessenger.showSnackBar(
                      SnackBar(content: Text('Error: $e')),
                    );
                  }
                }
              },
              style: FilledButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
              child: const Text('Delete My Account'),
            ),
          ],
        );
      },
    );
  }

  void _showNotificationsSheet(
    BuildContext context,
    AsyncValue<List<proto.Notification>> notificationsAsync,
    int userId,
  ) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.6,
          maxChildSize: 0.9,
          builder: (_, scrollController) {
            return notificationsAsync.when(
              loading: () =>
                  const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('Error: $e')),
              data: (notifications) {
                if (notifications.isEmpty) {
                  return const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32),
                      child: Text('No notifications'),
                    ),
                  );
                }
                return ListView.separated(
                  controller: scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: notifications.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final n = notifications[index];
                    return ListTile(
                      leading: Icon(
                        n.isRead
                            ? Icons.notifications_none
                            : Icons.notifications_active,
                        color: n.isRead ? null : Theme.of(context).colorScheme.primary,
                      ),
                      title: Text(
                        n.title,
                        style: n.isRead
                            ? null
                            : const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      subtitle: Text(n.message, maxLines: 2, overflow: TextOverflow.ellipsis),
                      onTap: () {
                        if (!n.isRead && n.id != null) {
                          ref.read(clientProvider).profile.markNotificationRead(
                            userId,
                            n.id!,
                          );
                          ref.invalidate(_notificationsProvider(userId));
                        }
                      },
                    );
                  },
                );
              },
            );
          },
        );
      },
    );
  }
}

// --- Sub-widgets ---

class _ProfileHeader extends StatelessWidget {
  final AuthState auth;

  const _ProfileHeader({required this.auth});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Row(
          children: [
            CircleAvatar(
              radius: 32,
              backgroundColor: colorScheme.primaryContainer,
              backgroundImage: auth.user?.avatarUrl != null
                  ? NetworkImage(auth.user!.avatarUrl!)
                  : null,
              child: auth.user?.avatarUrl == null
                  ? Text(
                      auth.user?.name.isNotEmpty == true
                          ? auth.user!.name[0].toUpperCase()
                          : '?',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        color: colorScheme.onPrimaryContainer,
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    auth.user?.name ?? 'User',
                    style: theme.textTheme.titleLarge,
                  ),
                  Text(
                    auth.user?.email ?? '',
                    style: theme.textTheme.bodyMedium
                        ?.copyWith(color: colorScheme.onSurfaceVariant),
                  ),
                  const SizedBox(height: 4),
                  Chip(
                    label: Text(
                      (auth.user?.role ?? 'student').toUpperCase(),
                      style: theme.textTheme.labelSmall,
                    ),
                    visualDensity: VisualDensity.compact,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EditProfileCard extends StatelessWidget {
  final AuthState auth;
  final TextEditingController nameController;
  final bool isEditing;
  final bool isSaving;
  final VoidCallback onEditToggle;
  final VoidCallback onSave;

  const _EditProfileCard({
    required this.auth,
    required this.nameController,
    required this.isEditing,
    required this.isSaving,
    required this.onEditToggle,
    required this.onSave,
  });

  @override
  Widget build(BuildContext context) {
    if (!isEditing) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.edit),
          title: const Text('Edit Profile'),
          subtitle: const Text('Update your name and details'),
          trailing: const Icon(Icons.chevron_right),
          onTap: onEditToggle,
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Edit Profile',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: onEditToggle,
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: isSaving ? null : onSave,
                  child: isSaving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Save'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ChangePasswordCard extends StatefulWidget {
  final TextEditingController currentPasswordController;
  final TextEditingController newPasswordController;
  final bool isChanging;
  final VoidCallback onSubmit;

  const _ChangePasswordCard({
    required this.currentPasswordController,
    required this.newPasswordController,
    required this.isChanging,
    required this.onSubmit,
  });

  @override
  State<_ChangePasswordCard> createState() => _ChangePasswordCardState();
}

class _ChangePasswordCardState extends State<_ChangePasswordCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (!_expanded) {
      return Card(
        child: ListTile(
          leading: const Icon(Icons.lock),
          title: const Text('Change Password'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => setState(() => _expanded = true),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Change Password',
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: widget.currentPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Current Password',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: widget.newPasswordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'New Password',
                border: OutlineInputBorder(),
                helperText: 'At least 8 characters',
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => setState(() => _expanded = false),
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: widget.isChanging ? null : widget.onSubmit,
                  child: widget.isChanging
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Update Password'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _WishlistCard extends StatelessWidget {
  final AsyncValue<List<Map<String, dynamic>>> wishlistAsync;

  const _WishlistCard({required this.wishlistAsync});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: Row(
              children: [
                const Icon(Icons.favorite, size: 20),
                const SizedBox(width: 8),
                Text(
                  'Wishlist',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          wishlistAsync.when(
            loading: () => const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => Padding(
              padding: const EdgeInsets.all(16),
              child: Text('Failed to load wishlist: $e'),
            ),
            data: (items) {
              if (items.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(
                    child: Text('No courses in your wishlist'),
                  ),
                );
              }
              return ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: items.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final course = items[index];
                  final title =
                      course['title'] as String? ?? 'Untitled';
                  final slug = course['slug'] as String? ?? '';
                  return ListTile(
                    leading: const Icon(Icons.play_circle_outline),
                    title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () {
                      if (slug.isNotEmpty) {
                        context.go('/courses/$slug');
                      }
                    },
                  );
                },
              );
            },
          ),
        ],
      ),
    );
  }
}
