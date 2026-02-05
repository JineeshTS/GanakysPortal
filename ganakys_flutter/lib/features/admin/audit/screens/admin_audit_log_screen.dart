import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/client_provider.dart';

class _AuditFilter {
  final int? userId;
  final String? action;
  final String? entityType;
  final int page;

  const _AuditFilter({this.userId, this.action, this.entityType, this.page = 1});

  _AuditFilter copyWith({
    int? userId,
    String? action,
    String? entityType,
    int? page,
    bool clearUserId = false,
    bool clearAction = false,
    bool clearEntityType = false,
  }) {
    return _AuditFilter(
      userId: clearUserId ? null : (userId ?? this.userId),
      action: clearAction ? null : (action ?? this.action),
      entityType: clearEntityType ? null : (entityType ?? this.entityType),
      page: page ?? this.page,
    );
  }
}

final _auditFilterProvider = StateProvider.autoDispose<_AuditFilter>(
  (ref) => const _AuditFilter(),
);

final _auditLogProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  final filter = ref.watch(_auditFilterProvider);
  return await client.admin.adminGetAuditLog(
    filter.userId,
    filter.action,
    filter.entityType,
    filter.page,
    30,
  );
});

class AdminAuditLogScreen extends ConsumerWidget {
  const AdminAuditLogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final auditAsync = ref.watch(_auditLogProvider);
    final filter = ref.watch(_auditFilterProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Audit Log',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                onPressed: () => ref.invalidate(_auditLogProvider),
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh',
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Filters
          Wrap(
            spacing: 12,
            runSpacing: 12,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              DropdownButton<String>(
                value: filter.action,
                hint: const Text('Action'),
                items: const [
                  DropdownMenuItem(value: 'create', child: Text('Create')),
                  DropdownMenuItem(value: 'update', child: Text('Update')),
                  DropdownMenuItem(value: 'delete', child: Text('Delete')),
                  DropdownMenuItem(value: 'login', child: Text('Login')),
                  DropdownMenuItem(value: 'logout', child: Text('Logout')),
                  DropdownMenuItem(value: 'ban', child: Text('Ban')),
                  DropdownMenuItem(value: 'role_change', child: Text('Role Change')),
                ],
                onChanged: (v) {
                  ref.read(_auditFilterProvider.notifier).state =
                      filter.copyWith(action: v, clearAction: v == null, page: 1);
                },
              ),
              if (filter.action != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_auditFilterProvider.notifier).state =
                        filter.copyWith(clearAction: true, page: 1);
                  },
                ),
              DropdownButton<String>(
                value: filter.entityType,
                hint: const Text('Entity Type'),
                items: const [
                  DropdownMenuItem(value: 'user', child: Text('User')),
                  DropdownMenuItem(value: 'course', child: Text('Course')),
                  DropdownMenuItem(value: 'section', child: Text('Section')),
                  DropdownMenuItem(value: 'lecture', child: Text('Lecture')),
                  DropdownMenuItem(value: 'category', child: Text('Category')),
                  DropdownMenuItem(value: 'setting', child: Text('Setting')),
                  DropdownMenuItem(value: 'enrollment', child: Text('Enrollment')),
                ],
                onChanged: (v) {
                  ref.read(_auditFilterProvider.notifier).state =
                      filter.copyWith(entityType: v, clearEntityType: v == null, page: 1);
                },
              ),
              if (filter.entityType != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_auditFilterProvider.notifier).state =
                        filter.copyWith(clearEntityType: true, page: 1);
                  },
                ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: auditAsync.when(
              data: (data) {
                final logs = (data['logs'] as List?)?.cast<Map<String, dynamic>>() ?? [];
                final totalCount = data['totalCount'] as int? ?? 0;
                final currentPage = filter.page;
                final totalPages = (totalCount / 30).ceil().clamp(1, 9999);

                if (logs.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.history, size: 64, color: colorScheme.outline),
                        const SizedBox(height: 16),
                        Text('No audit log entries', style: theme.textTheme.titleMedium),
                      ],
                    ),
                  );
                }

                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        itemCount: logs.length,
                        itemBuilder: (context, index) {
                          final log = logs[index];
                          final userName = log['userName'] as String? ?? 'System';
                          final action = log['action'] as String? ?? 'unknown';
                          final entityType = log['entityType'] as String? ?? '';
                          final entityId = log['entityId'];
                          final timestamp = log['createdAt'] as String? ?? '';
                          final oldValues = log['oldValues'];
                          final newValues = log['newValues'];
                          final hasDetails = oldValues != null || newValues != null;

                          return Card(
                            margin: const EdgeInsets.only(bottom: 4),
                            child: ExpansionTile(
                              leading: _ActionIcon(action: action),
                              title: Text(
                                '$userName - $action',
                                style: const TextStyle(fontWeight: FontWeight.w500),
                              ),
                              subtitle: Row(
                                children: [
                                  if (entityType.isNotEmpty) ...[
                                    Chip(
                                      label: Text(entityType, style: const TextStyle(fontSize: 10)),
                                      padding: EdgeInsets.zero,
                                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                      visualDensity: VisualDensity.compact,
                                    ),
                                    const SizedBox(width: 4),
                                  ],
                                  if (entityId != null) ...[
                                    Text('#$entityId', style: theme.textTheme.bodySmall),
                                    const SizedBox(width: 8),
                                  ],
                                  Text(timestamp, style: theme.textTheme.bodySmall),
                                ],
                              ),
                              trailing: hasDetails ? null : const SizedBox.shrink(),
                              children: [
                                if (hasDetails)
                                  Padding(
                                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        if (oldValues != null) ...[
                                          Text('Previous Values:', style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold)),
                                          const SizedBox(height: 4),
                                          Container(
                                            width: double.infinity,
                                            padding: const EdgeInsets.all(8),
                                            decoration: BoxDecoration(
                                              color: colorScheme.surfaceContainerHighest,
                                              borderRadius: BorderRadius.circular(4),
                                            ),
                                            child: Text(
                                              '$oldValues',
                                              style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
                                            ),
                                          ),
                                        ],
                                        if (newValues != null) ...[
                                          const SizedBox(height: 8),
                                          Text('New Values:', style: theme.textTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold)),
                                          const SizedBox(height: 4),
                                          Container(
                                            width: double.infinity,
                                            padding: const EdgeInsets.all(8),
                                            decoration: BoxDecoration(
                                              color: colorScheme.surfaceContainerHighest,
                                              borderRadius: BorderRadius.circular(4),
                                            ),
                                            child: Text(
                                              '$newValues',
                                              style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
                                            ),
                                          ),
                                        ],
                                      ],
                                    ),
                                  ),
                              ],
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
                                      ref.read(_auditFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage - 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_left),
                            ),
                            Text('Page $currentPage of $totalPages'),
                            IconButton(
                              onPressed: currentPage < totalPages
                                  ? () {
                                      ref.read(_auditFilterProvider.notifier).state =
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
                    Text('Failed to load audit log: $error'),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => ref.invalidate(_auditLogProvider),
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

class _ActionIcon extends StatelessWidget {
  final String action;

  const _ActionIcon({required this.action});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color color;
    switch (action) {
      case 'create':
        icon = Icons.add_circle;
        color = Colors.green;
        break;
      case 'update':
        icon = Icons.edit;
        color = Colors.blue;
        break;
      case 'delete':
        icon = Icons.delete;
        color = Colors.red;
        break;
      case 'login':
        icon = Icons.login;
        color = Colors.teal;
        break;
      case 'logout':
        icon = Icons.logout;
        color = Colors.grey;
        break;
      case 'ban':
        icon = Icons.block;
        color = Colors.red;
        break;
      case 'role_change':
        icon = Icons.admin_panel_settings;
        color = Colors.purple;
        break;
      default:
        icon = Icons.info;
        color = Colors.grey;
        break;
    }
    return CircleAvatar(
      radius: 18,
      backgroundColor: color.withValues(alpha: 0.1),
      child: Icon(icon, color: color, size: 20),
    );
  }
}
