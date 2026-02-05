import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/client_provider.dart';

final _paymentStatsProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.getDashboardStats();
});

class AdminPaymentsScreen extends ConsumerWidget {
  const AdminPaymentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final statsAsync = ref.watch(_paymentStatsProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Payments',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                onPressed: () => ref.invalidate(_paymentStatsProvider),
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh',
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Revenue summary cards
          statsAsync.when(
            data: (stats) {
              return Wrap(
                spacing: 16,
                runSpacing: 16,
                children: [
                  _RevenueCard(
                    icon: Icons.attach_money,
                    label: 'Total Revenue',
                    value: '\$${stats['totalRevenue'] ?? 0}',
                    color: Colors.green,
                  ),
                  _RevenueCard(
                    icon: Icons.today,
                    label: 'Revenue Today',
                    value: '\$${stats['revenueToday'] ?? 0}',
                    color: Colors.blue,
                  ),
                  _RevenueCard(
                    icon: Icons.people,
                    label: 'Active Subscriptions',
                    value: '${stats['activeSubscriptions'] ?? 0}',
                    color: Colors.purple,
                  ),
                  _RevenueCard(
                    icon: Icons.receipt,
                    label: 'Total Transactions',
                    value: '${stats['totalPayments'] ?? 0}',
                    color: Colors.orange,
                  ),
                ],
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Card(
              color: colorScheme.errorContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Failed to load: $error'),
              ),
            ),
          ),
          const SizedBox(height: 32),
          Text(
            'Recent Transactions',
            style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Center(
                child: Column(
                  children: [
                    Icon(Icons.payment, size: 48, color: colorScheme.outline),
                    const SizedBox(height: 12),
                    Text('Transaction list', style: theme.textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Text(
                      'Detailed transaction listing with filters and export will be available soon.',
                      style: TextStyle(color: colorScheme.onSurfaceVariant),
                      textAlign: TextAlign.center,
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

class _RevenueCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _RevenueCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 220,
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
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
