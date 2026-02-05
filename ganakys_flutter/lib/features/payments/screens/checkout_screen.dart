import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/client_provider.dart';
import '../../../core/providers/course_provider.dart';

// --- Screen ---

class CheckoutScreen extends ConsumerStatefulWidget {
  final String planSlug;

  const CheckoutScreen({super.key, required this.planSlug});

  @override
  ConsumerState<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends ConsumerState<CheckoutScreen> {
  String _selectedGateway = 'razorpay';
  final _couponController = TextEditingController();
  bool _isValidatingCoupon = false;
  bool _isProcessing = false;
  String? _couponError;
  double? _couponDiscount;
  bool _couponValid = false;

  @override
  void dispose() {
    _couponController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;
    final plansAsync = ref.watch(subscriptionPlansProvider);

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
              // Back button
              TextButton.icon(
                onPressed: () => context.go('/pricing'),
                icon: const Icon(Icons.arrow_back),
                label: const Text('Back to Plans'),
              ),
              const SizedBox(height: 16),
              Text(
                'Checkout',
                style: theme.textTheme.headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 24),
              plansAsync.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(48),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, _) => Center(
                  child: Column(
                    children: [
                      Icon(Icons.error_outline,
                          size: 48, color: colorScheme.error),
                      const SizedBox(height: 16),
                      Text('Failed to load plan details: $error'),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () =>
                            ref.invalidate(subscriptionPlansProvider),
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
                data: (plans) {
                  final plan = plans.cast<SubscriptionPlan?>().firstWhere(
                        (p) => p!.slug == widget.planSlug,
                        orElse: () => null,
                      );
                  if (plan == null) {
                    return Center(
                      child: Column(
                        children: [
                          Icon(Icons.error_outline,
                              size: 48, color: colorScheme.error),
                          const SizedBox(height: 16),
                          Text(
                            'Plan "${widget.planSlug}" not found',
                            style: theme.textTheme.titleMedium,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () => context.go('/pricing'),
                            child: const Text('View Plans'),
                          ),
                        ],
                      ),
                    );
                  }
                  return _buildCheckoutForm(plan, theme, colorScheme);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCheckoutForm(
    SubscriptionPlan plan,
    ThemeData theme,
    ColorScheme colorScheme,
  ) {
    final price = plan.priceMonthly;
    final discountAmount =
        _couponValid && _couponDiscount != null ? _couponDiscount! : 0.0;
    final finalPrice = (price - (price * discountAmount / 100)).clamp(0.0, price);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Plan details card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Selected Plan',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(plan.name, style: theme.textTheme.titleLarge),
                    Text(
                      '${plan.currency} ${price.toStringAsFixed(2)}/mo',
                      style: theme.textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                if (plan.priceYearly > 0) ...[
                  const SizedBox(height: 4),
                  Text(
                    'or ${plan.currency} ${plan.priceYearly.toStringAsFixed(2)}/year',
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: colorScheme.onSurfaceVariant),
                  ),
                ],
                if (plan.features.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 8),
                  ...plan.features
                      .replaceAll('[', '')
                      .replaceAll(']', '')
                      .replaceAll('"', '')
                      .split(',')
                      .map((f) => f.trim())
                      .where((f) => f.isNotEmpty)
                      .map(
                        (f) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              Icon(Icons.check,
                                  size: 16, color: colorScheme.primary),
                              const SizedBox(width: 8),
                              Expanded(child: Text(f)),
                            ],
                          ),
                        ),
                      ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),

        // Payment Gateway
        Text(
          'Payment Method',
          style:
              theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Card(
          child: Column(
            children: [
              RadioListTile<String>(
                value: 'razorpay',
                groupValue: _selectedGateway,
                onChanged: (v) => setState(() => _selectedGateway = v!),
                title: const Text('Razorpay'),
                subtitle: const Text('UPI, Cards, Net Banking (India)'),
                secondary: const Icon(Icons.account_balance),
              ),
              const Divider(height: 1),
              RadioListTile<String>(
                value: 'stripe',
                groupValue: _selectedGateway,
                onChanged: (v) => setState(() => _selectedGateway = v!),
                title: const Text('Stripe'),
                subtitle: const Text('Credit/Debit Cards (International)'),
                secondary: const Icon(Icons.credit_card),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Coupon code
        Text(
          'Coupon Code',
          style:
              theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _couponController,
                decoration: InputDecoration(
                  hintText: 'Enter coupon code',
                  border: const OutlineInputBorder(),
                  errorText: _couponError,
                  suffixIcon: _couponValid
                      ? const Icon(Icons.check_circle, color: Colors.green)
                      : null,
                ),
                textCapitalization: TextCapitalization.characters,
              ),
            ),
            const SizedBox(width: 12),
            FilledButton.tonal(
              onPressed: _isValidatingCoupon
                  ? null
                  : () => _validateCoupon(plan.id),
              child: _isValidatingCoupon
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Apply'),
            ),
          ],
        ),
        if (_couponValid && _couponDiscount != null) ...[
          const SizedBox(height: 8),
          Text(
            'Coupon applied! ${_couponDiscount!.toStringAsFixed(0)}% off',
            style: TextStyle(color: colorScheme.primary),
          ),
        ],
        const SizedBox(height: 24),

        // Price summary
        Card(
          color: colorScheme.surfaceContainerHighest,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Subtotal'),
                    Text('${plan.currency} ${price.toStringAsFixed(2)}'),
                  ],
                ),
                if (_couponValid && discountAmount > 0) ...[
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Discount (${discountAmount.toStringAsFixed(0)}%)',
                        style: TextStyle(color: colorScheme.primary),
                      ),
                      Text(
                        '-${plan.currency} ${(price - finalPrice).toStringAsFixed(2)}',
                        style: TextStyle(color: colorScheme.primary),
                      ),
                    ],
                  ),
                ],
                const Divider(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Total',
                      style: theme.textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    Text(
                      '${plan.currency} ${finalPrice.toStringAsFixed(2)}',
                      style: theme.textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),

        // Pay button
        SizedBox(
          width: double.infinity,
          height: 56,
          child: FilledButton.icon(
            onPressed: _isProcessing ? null : () => _processCheckout(plan),
            icon: _isProcessing
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.lock),
            label: Text(
              _isProcessing ? 'Processing...' : 'Pay Now',
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Future<void> _validateCoupon(int? planId) async {
    final code = _couponController.text.trim();
    if (code.isEmpty) {
      setState(() {
        _couponError = 'Please enter a coupon code';
        _couponValid = false;
        _couponDiscount = null;
      });
      return;
    }

    setState(() {
      _isValidatingCoupon = true;
      _couponError = null;
    });

    try {
      final client = ref.read(clientProvider);
      final result = await client.payment.validateCoupon(code, planId);
      if (mounted) {
        if (result['valid'] == true) {
          setState(() {
            _couponValid = true;
            _couponDiscount = (result['discount'] as num?)?.toDouble();
            _isValidatingCoupon = false;
          });
        } else {
          setState(() {
            _couponValid = false;
            _couponDiscount = null;
            _couponError = 'Invalid coupon code';
            _isValidatingCoupon = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isValidatingCoupon = false;
          _couponError = 'Failed to validate coupon';
        });
      }
    }
  }

  Future<void> _processCheckout(SubscriptionPlan plan) async {
    final auth = ref.read(authProvider);
    final userId = auth.user?.id;
    if (userId == null || plan.id == null) return;

    setState(() => _isProcessing = true);

    try {
      final client = ref.read(clientProvider);
      final coupon = _couponValid ? _couponController.text.trim() : null;
      final result = await client.payment.createCheckout(
        userId,
        plan.id!,
        _selectedGateway,
        coupon,
      );

      if (!mounted) return;
      setState(() => _isProcessing = false);

      if (result['success'] == true) {
        final checkoutUrl = result['checkoutUrl'] as String?;
        if (checkoutUrl != null && checkoutUrl.isNotEmpty) {
          final uri = Uri.parse(checkoutUrl);
          if (await canLaunchUrl(uri)) {
            await launchUrl(uri, mode: LaunchMode.externalApplication);
          }
        } else {
          // Show success inline
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Payment initiated successfully!'),
                backgroundColor: Colors.green,
              ),
            );
            context.go('/billing');
          }
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                  result['error'] as String? ?? 'Checkout failed. Please try again.'),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isProcessing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }
}
