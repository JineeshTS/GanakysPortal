import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/client_provider.dart';

class _UsersFilter {
  final String? search;
  final String? role;
  final String? subscriptionStatus;
  final int page;

  const _UsersFilter({this.search, this.role, this.subscriptionStatus, this.page = 1});

  _UsersFilter copyWith({
    String? search,
    String? role,
    String? subscriptionStatus,
    int? page,
    bool clearSearch = false,
    bool clearRole = false,
    bool clearSubscription = false,
  }) {
    return _UsersFilter(
      search: clearSearch ? null : (search ?? this.search),
      role: clearRole ? null : (role ?? this.role),
      subscriptionStatus: clearSubscription ? null : (subscriptionStatus ?? this.subscriptionStatus),
      page: page ?? this.page,
    );
  }
}

final _usersFilterProvider = StateProvider.autoDispose<_UsersFilter>(
  (ref) => const _UsersFilter(),
);

final _usersProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  final filter = ref.watch(_usersFilterProvider);
  return await client.admin.adminListUsers(
    filter.search,
    filter.role,
    filter.subscriptionStatus,
    filter.page,
    20,
  );
});

class AdminUsersScreen extends ConsumerStatefulWidget {
  const AdminUsersScreen({super.key});

  @override
  ConsumerState<AdminUsersScreen> createState() => _AdminUsersScreenState();
}

class _AdminUsersScreenState extends ConsumerState<AdminUsersScreen> {
  final _searchController = TextEditingController();
  Timer? _debounce;

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 400), () {
      ref.read(_usersFilterProvider.notifier).state =
          ref.read(_usersFilterProvider).copyWith(
                search: value.isEmpty ? null : value,
                clearSearch: value.isEmpty,
                page: 1,
              );
    });
  }

  Future<void> _changeRole(int userId, String currentRole) async {
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
    if (newRole == null || newRole == currentRole || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateUserRole(userId, newRole);
      ref.invalidate(_usersProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Role changed to $newRole')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  Future<void> _toggleBan(int userId, bool currentlyBanned) async {
    final action = currentlyBanned ? 'unban' : 'ban';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('${action[0].toUpperCase()}${action.substring(1)} User'),
        content: Text('Are you sure you want to $action this user?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(action[0].toUpperCase() + action.substring(1)),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminBanUser(userId, !currentlyBanned);
      ref.invalidate(_usersProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('User ${currentlyBanned ? 'unbanned' : 'banned'}')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  Future<void> _forcePasswordReset(int userId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Force Password Reset'),
        content: const Text('This will force the user to reset their password and invalidate all active sessions.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Reset')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminForcePasswordReset(userId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Password reset initiated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final usersAsync = ref.watch(_usersProvider);
    final filter = ref.watch(_usersFilterProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Users', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          // Filters
          Wrap(
            spacing: 12,
            runSpacing: 12,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                width: 300,
                child: TextField(
                  controller: _searchController,
                  onChanged: _onSearchChanged,
                  decoration: InputDecoration(
                    hintText: 'Search users...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                ),
              ),
              DropdownButton<String>(
                value: filter.role,
                hint: const Text('Role'),
                items: const [
                  DropdownMenuItem(value: 'student', child: Text('Student')),
                  DropdownMenuItem(value: 'instructor', child: Text('Instructor')),
                  DropdownMenuItem(value: 'admin', child: Text('Admin')),
                ],
                onChanged: (v) {
                  ref.read(_usersFilterProvider.notifier).state =
                      filter.copyWith(role: v, clearRole: v == null, page: 1);
                },
              ),
              if (filter.role != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_usersFilterProvider.notifier).state =
                        filter.copyWith(clearRole: true, page: 1);
                  },
                ),
              DropdownButton<String>(
                value: filter.subscriptionStatus,
                hint: const Text('Subscription'),
                items: const [
                  DropdownMenuItem(value: 'active', child: Text('Active')),
                  DropdownMenuItem(value: 'expired', child: Text('Expired')),
                  DropdownMenuItem(value: 'none', child: Text('None')),
                ],
                onChanged: (v) {
                  ref.read(_usersFilterProvider.notifier).state =
                      filter.copyWith(subscriptionStatus: v, clearSubscription: v == null, page: 1);
                },
              ),
              if (filter.subscriptionStatus != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_usersFilterProvider.notifier).state =
                        filter.copyWith(clearSubscription: true, page: 1);
                  },
                ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: usersAsync.when(
              data: (data) {
                final users = (data['users'] as List?)?.cast<Map<String, dynamic>>() ?? [];
                final totalPages = data['totalPages'] as int? ?? 1;
                final currentPage = data['page'] as int? ?? 1;

                if (users.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.people_outline, size: 64, color: colorScheme.outline),
                        const SizedBox(height: 16),
                        Text('No users found', style: theme.textTheme.titleMedium),
                      ],
                    ),
                  );
                }

                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        itemCount: users.length,
                        itemBuilder: (context, index) {
                          final user = users[index];
                          final id = user['id'] as int;
                          final name = user['name'] as String? ?? 'Unknown';
                          final email = user['email'] as String? ?? '';
                          final role = user['role'] as String? ?? 'student';
                          final subscriptionStatus = user['subscriptionStatus'] as String?;
                          final enrollmentCount = user['enrollmentCount'] ?? 0;
                          final isBanned = user['isActive'] == false;

                          return Card(
                            margin: const EdgeInsets.only(bottom: 4),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: isBanned ? colorScheme.errorContainer : colorScheme.primaryContainer,
                                child: Text(
                                  name.isNotEmpty ? name[0].toUpperCase() : '?',
                                  style: TextStyle(
                                    color: isBanned ? colorScheme.onErrorContainer : colorScheme.onPrimaryContainer,
                                  ),
                                ),
                              ),
                              title: Row(
                                children: [
                                  Expanded(child: Text(name, maxLines: 1, overflow: TextOverflow.ellipsis)),
                                  _RoleChip(role: role),
                                ],
                              ),
                              subtitle: Row(
                                children: [
                                  Expanded(child: Text(email, style: theme.textTheme.bodySmall)),
                                  if (subscriptionStatus != null) ...[
                                    _SubscriptionChip(status: subscriptionStatus),
                                    const SizedBox(width: 8),
                                  ],
                                  Icon(Icons.school, size: 14, color: colorScheme.outline),
                                  const SizedBox(width: 2),
                                  Text('$enrollmentCount', style: theme.textTheme.bodySmall),
                                  if (isBanned) ...[
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: const Text('Banned', style: TextStyle(fontSize: 10, color: Colors.white)),
                                      backgroundColor: colorScheme.error,
                                      padding: EdgeInsets.zero,
                                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                      visualDensity: VisualDensity.compact,
                                    ),
                                  ],
                                ],
                              ),
                              trailing: PopupMenuButton<String>(
                                onSelected: (action) {
                                  switch (action) {
                                    case 'view':
                                      context.go('/admin/users/$id');
                                      break;
                                    case 'role':
                                      _changeRole(id, role);
                                      break;
                                    case 'ban':
                                      _toggleBan(id, isBanned);
                                      break;
                                    case 'reset':
                                      _forcePasswordReset(id);
                                      break;
                                  }
                                },
                                itemBuilder: (ctx) => [
                                  const PopupMenuItem(value: 'view', child: Text('View Details')),
                                  const PopupMenuItem(value: 'role', child: Text('Change Role')),
                                  PopupMenuItem(
                                    value: 'ban',
                                    child: Text(isBanned ? 'Unban User' : 'Ban User'),
                                  ),
                                  const PopupMenuItem(value: 'reset', child: Text('Force Password Reset')),
                                ],
                              ),
                              onTap: () => context.go('/admin/users/$id'),
                            ),
                          );
                        },
                      ),
                    ),
                    if (totalPages > 1)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            IconButton(
                              onPressed: currentPage > 1
                                  ? () {
                                      ref.read(_usersFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage - 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_left),
                            ),
                            Text('Page $currentPage of $totalPages'),
                            IconButton(
                              onPressed: currentPage < totalPages
                                  ? () {
                                      ref.read(_usersFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage + 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_right),
                            ),
                          ],
                        ),
                      ),
                  ],
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.error, size: 48, color: colorScheme.error),
                    const SizedBox(height: 12),
                    Text('Failed to load users: $error'),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => ref.invalidate(_usersProvider),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _RoleChip extends StatelessWidget {
  final String role;

  const _RoleChip({required this.role});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    switch (role) {
      case 'admin':
        bg = Colors.red.shade50;
        fg = Colors.red.shade800;
        break;
      case 'instructor':
        bg = Colors.blue.shade50;
        fg = Colors.blue.shade800;
        break;
      default:
        bg = Colors.grey.shade100;
        fg = Colors.grey.shade800;
    }
    return Chip(
      label: Text(role[0].toUpperCase() + role.substring(1), style: TextStyle(fontSize: 11, color: fg)),
      backgroundColor: bg,
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      visualDensity: VisualDensity.compact,
    );
  }
}

class _SubscriptionChip extends StatelessWidget {
  final String status;

  const _SubscriptionChip({required this.status});

  @override
  Widget build(BuildContext context) {
    final isActive = status == 'active';
    return Chip(
      label: Text(
        status[0].toUpperCase() + status.substring(1),
        style: TextStyle(fontSize: 10, color: isActive ? Colors.green.shade800 : Colors.grey.shade800),
      ),
      backgroundColor: isActive ? Colors.green.shade50 : Colors.grey.shade100,
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      visualDensity: VisualDensity.compact,
    );
  }
}
