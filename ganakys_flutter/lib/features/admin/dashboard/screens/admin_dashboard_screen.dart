import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/client_provider.dart';

final _dashboardStatsProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.getDashboardStats();
});

class AdminDashboardScreen extends ConsumerWidget {
  const AdminDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final statsAsync = ref.watch(_dashboardStatsProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(_dashboardStatsProvider);
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Dashboard',
                    style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                IconButton(
                  onPressed: () => ref.invalidate(_dashboardStatsProvider),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            const SizedBox(height: 24),
            // Stats cards
            statsAsync.when(
              data: (stats) => _StatsCards(stats: stats),
              loading: () => const _StatsCardsLoading(),
              error: (error, _) => Card(
                color: colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.error, color: colorScheme.onErrorContainer),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Failed to load stats: $error',
                          style: TextStyle(color: colorScheme.onErrorContainer),
                        ),
                      ),
                      TextButton(
                        onPressed: () => ref.invalidate(_dashboardStatsProvider),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),
            // Quick actions
            Text(
              'Quick Actions',
              style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                FilledButton.tonalIcon(
                  onPressed: () => context.go('/admin/generate'),
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Generate Course'),
                ),
                FilledButton.tonalIcon(
                  onPressed: () => context.go('/admin/users'),
                  icon: const Icon(Icons.person_add),
                  label: const Text('Manage Users'),
                ),
                FilledButton.tonalIcon(
                  onPressed: () => context.go('/admin/audit-log'),
                  icon: const Icon(Icons.history),
                  label: const Text('View Audit Log'),
                ),
                FilledButton.tonalIcon(
                  onPressed: () => context.go('/admin/courses'),
                  icon: const Icon(Icons.book),
                  label: const Text('Manage Courses'),
                ),
                FilledButton.tonalIcon(
                  onPressed: () => context.go('/admin/settings'),
                  icon: const Icon(Icons.settings),
                  label: const Text('Site Settings'),
                ),
              ],
            ),
            const SizedBox(height: 32),
            // Recent activity placeholder
            Text(
              'Recent Activity',
              style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            statsAsync.when(
              data: (stats) {
                final newUsers = stats['newUsersToday'] ?? 0;
                final newEnrollments = stats['newEnrollmentsToday'] ?? 0;
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _ActivityItem(
                          icon: Icons.person_add,
                          color: Colors.blue,
                          title: '$newUsers new user${newUsers == 1 ? '' : 's'} today',
                        ),
                        const Divider(),
                        _ActivityItem(
                          icon: Icons.school,
                          color: Colors.green,
                          title: '$newEnrollments new enrollment${newEnrollments == 1 ? '' : 's'} today',
                        ),
                        const Divider(),
                        _ActivityItem(
                          icon: Icons.trending_up,
                          color: Colors.orange,
                          title: 'Revenue: \$${stats['revenueToday'] ?? 0} today',
                        ),
                      ],
                    ),
                  ),
                );
              },
              loading: () => const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                ),
              ),
              error: (_, __) => Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Column(
                      children: [
                        Icon(Icons.history, size: 48, color: colorScheme.outline),
                        const SizedBox(height: 12),
                        Text('Activity data unavailable', style: theme.textTheme.bodyLarge),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatsCards extends StatelessWidget {
  final Map<String, dynamic> stats;

  const _StatsCards({required this.stats});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final cardWidth = constraints.maxWidth > 900
            ? (constraints.maxWidth - 48) / 4
            : constraints.maxWidth > 500
                ? (constraints.maxWidth - 16) / 2
                : constraints.maxWidth;
        return Wrap(
          spacing: 16,
          runSpacing: 16,
          children: [
            _StatCard(
              width: cardWidth,
              icon: Icons.people,
              label: 'Total Users',
              value: '${stats['totalUsers'] ?? 0}',
              color: Colors.blue,
            ),
            _StatCard(
              width: cardWidth,
              icon: Icons.book,
              label: 'Total Courses',
              value: '${stats['totalCourses'] ?? 0}',
              color: Colors.green,
            ),
            _StatCard(
              width: cardWidth,
              icon: Icons.school,
              label: 'Total Enrollments',
              value: '${stats['totalEnrollments'] ?? 0}',
              color: Colors.orange,
            ),
            _StatCard(
              width: cardWidth,
              icon: Icons.attach_money,
              label: 'Total Revenue',
              value: '\$${stats['totalRevenue'] ?? 0}',
              color: Colors.purple,
            ),
          ],
        );
      },
    );
  }
}

class _StatsCardsLoading extends StatelessWidget {
  const _StatsCardsLoading();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final cardWidth = constraints.maxWidth > 900
            ? (constraints.maxWidth - 48) / 4
            : constraints.maxWidth > 500
                ? (constraints.maxWidth - 16) / 2
                : constraints.maxWidth;
        return Wrap(
          spacing: 16,
          runSpacing: 16,
          children: List.generate(
            4,
            (_) => SizedBox(
              width: cardWidth,
              height: 120,
              child: const Card(
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  final double width;
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.width,
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return SizedBox(
      width: width,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 12),
              Text(
                value,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActivityItem extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;

  const _ActivityItem({
    required this.icon,
    required this.color,
    required this.title,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: color.withValues(alpha: 0.1),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(title, style: Theme.of(context).textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }
}
