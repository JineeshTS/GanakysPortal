import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:intl/intl.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/client_provider.dart';

// --- Providers ---

final _subscriptionProvider =
    FutureProvider.family<Map<String, dynamic>?, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.payment.getSubscription(userId);
});

final _billingHistoryProvider =
    FutureProvider.family<List<Payment>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.payment.getBillingHistory(userId);
});

// --- Screen ---

class BillingScreen extends ConsumerWidget {
  const BillingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final userId = auth.user?.id;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    if (userId == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final subscriptionAsync = ref.watch(_subscriptionProvider(userId));
    final historyAsync = ref.watch(_billingHistoryProvider(userId));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(_subscriptionProvider(userId));
        ref.invalidate(_billingHistoryProvider(userId));
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.symmetric(
          horizontal: isWide ? 48 : 16,
          vertical: 24,
        ),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 800),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Billing & Subscription',
                  style: theme.textTheme.headlineMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),

                // Subscription card
                _SubscriptionCard(
                  subscriptionAsync: subscriptionAsync,
                  userId: userId,
                ),
                const SizedBox(height: 32),

                // Billing history
                Text(
                  'Billing History',
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                _BillingHistorySection(
                  historyAsync: historyAsync,
                  colorScheme: colorScheme,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// --- Subscription Card ---

class _SubscriptionCard extends ConsumerWidget {
  final AsyncValue<Map<String, dynamic>?> subscriptionAsync;
  final int userId;

  const _SubscriptionCard({
    required this.subscriptionAsync,
    required this.userId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return subscriptionAsync.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Center(child: CircularProgressIndicator()),
        ),
      ),
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              Icon(Icons.error_outline, size: 48, color: colorScheme.error),
              const SizedBox(height: 16),
              Text('Failed to load subscription: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () =>
                    ref.invalidate(_subscriptionProvider(userId)),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (subscription) {
        if (subscription == null) {
          return _NoSubscription(colorScheme: colorScheme);
        }
        return _ActiveSubscription(
          subscription: subscription,
          userId: userId,
        );
      },
    );
  }
}

class _NoSubscription extends StatelessWidget {
  final ColorScheme colorScheme;

  const _NoSubscription({required this.colorScheme});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Icon(Icons.credit_card_off,
                size: 64, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'No active subscription',
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Subscribe to a plan to unlock all courses and features',
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: colorScheme.onSurfaceVariant),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => context.go('/pricing'),
              icon: const Icon(Icons.star),
              label: const Text('View Plans'),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActiveSubscription extends ConsumerStatefulWidget {
  final Map<String, dynamic> subscription;
  final int userId;

  const _ActiveSubscription({
    required this.subscription,
    required this.userId,
  });

  @override
  ConsumerState<_ActiveSubscription> createState() =>
      _ActiveSubscriptionState();
}

class _ActiveSubscriptionState extends ConsumerState<_ActiveSubscription> {
  bool _isCancelling = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final dateFormat = DateFormat.yMMMd();

    final planName = widget.subscription['plan'] as String? ?? 'Unknown';
    final status = widget.subscription['status'] as String? ?? 'unknown';
    final currentPeriodEnd = widget.subscription['currentPeriodEnd'];

    String? endDateStr;
    if (currentPeriodEnd is String) {
      try {
        endDateStr = dateFormat.format(DateTime.parse(currentPeriodEnd));
      } catch (_) {
        endDateStr = currentPeriodEnd;
      }
    } else if (currentPeriodEnd is DateTime) {
      endDateStr = dateFormat.format(currentPeriodEnd);
    }

    final isActive = status == 'active';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isActive ? Icons.check_circle : Icons.info_outline,
                  color: isActive ? Colors.green : colorScheme.outline,
                ),
                const SizedBox(width: 12),
                Text(
                  'Current Subscription',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _InfoRow(label: 'Plan', value: planName),
            const SizedBox(height: 8),
            _InfoRow(
              label: 'Status',
              value: status[0].toUpperCase() + status.substring(1),
              valueColor: isActive ? Colors.green : colorScheme.error,
            ),
            if (endDateStr != null) ...[
              const SizedBox(height: 8),
              _InfoRow(label: 'Next billing date', value: endDateStr),
            ],
            const SizedBox(height: 20),
            if (isActive)
              OutlinedButton.icon(
                onPressed: _isCancelling
                    ? null
                    : () => _showCancelDialog(context),
                icon: _isCancelling
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.cancel),
                label: Text(
                    _isCancelling ? 'Cancelling...' : 'Cancel Subscription'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: colorScheme.error,
                  side: BorderSide(color: colorScheme.error),
                ),
              ),
          ],
        ),
      ),
    );
  }

  void _showCancelDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancel Subscription'),
        content: const Text(
          'Are you sure you want to cancel your subscription? '
          'You will still have access until the end of the current billing period.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Keep Subscription'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              _cancelSubscription();
            },
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Cancel Subscription'),
          ),
        ],
      ),
    );
  }

  Future<void> _cancelSubscription() async {
    setState(() => _isCancelling = true);
    try {
      final client = ref.read(clientProvider);
      final result =
          await client.payment.cancelSubscription(widget.userId);
      if (mounted) {
        setState(() => _isCancelling = false);
        if (result['success'] == true) {
          ref.invalidate(_subscriptionProvider(widget.userId));
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Subscription cancelled successfully')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
                content: Text('Failed to cancel subscription')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isCancelling = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;

  const _InfoRow({
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: theme.textTheme.bodyMedium
              ?.copyWith(color: theme.colorScheme.onSurfaceVariant),
        ),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: valueColor,
          ),
        ),
      ],
    );
  }
}

// --- Billing History ---

class _BillingHistorySection extends StatelessWidget {
  final AsyncValue<List<Payment>> historyAsync;
  final ColorScheme colorScheme;

  const _BillingHistorySection({
    required this.historyAsync,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return historyAsync.when(
      loading: () => const Center(
        child: Padding(
          padding: EdgeInsets.all(48),
          child: CircularProgressIndicator(),
        ),
      ),
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text('Failed to load billing history: $error'),
        ),
      ),
      data: (payments) {
        if (payments.isEmpty) {
          return _EmptyBillingHistory(colorScheme: colorScheme);
        }
        return _BillingTable(payments: payments);
      },
    );
  }
}

class _EmptyBillingHistory extends StatelessWidget {
  final ColorScheme colorScheme;

  const _EmptyBillingHistory({required this.colorScheme});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.receipt_long_outlined,
                  size: 48, color: colorScheme.outline),
              const SizedBox(height: 16),
              Text(
                'No billing history',
                style: theme.textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Your payment history will appear here',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _BillingTable extends StatelessWidget {
  final List<Payment> payments;

  const _BillingTable({required this.payments});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final dateFormat = DateFormat.yMMMd();

    return Card(
      clipBehavior: Clip.antiAlias,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          columns: const [
            DataColumn(label: Text('Date')),
            DataColumn(label: Text('Amount')),
            DataColumn(label: Text('Status')),
            DataColumn(label: Text('Gateway')),
          ],
          rows: payments.map((payment) {
            final statusColor = switch (payment.status) {
              'completed' || 'succeeded' => Colors.green,
              'pending' => Colors.orange,
              'failed' => colorScheme.error,
              _ => colorScheme.onSurfaceVariant,
            };

            return DataRow(cells: [
              DataCell(Text(dateFormat.format(payment.createdAt))),
              DataCell(Text(
                '${payment.currency} ${payment.amount.toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              )),
              DataCell(
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: statusColor.withAlpha(25),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    payment.status[0].toUpperCase() +
                        payment.status.substring(1),
                    style: TextStyle(
                      color: statusColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              DataCell(Text(
                payment.paymentGateway[0].toUpperCase() +
                    payment.paymentGateway.substring(1),
              )),
            ]);
          }).toList(),
        ),
      ),
    );
  }
}
