import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/course_provider.dart';
import '../../../core/providers/auth_provider.dart';

class PricingScreen extends ConsumerWidget {
  const PricingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final plansAsync = ref.watch(subscriptionPlansProvider);
    final auth = ref.watch(authProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    return SingleChildScrollView(
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 64 : 16,
        vertical: 48,
      ),
      child: Column(
        children: [
          Text(
            'Simple, Transparent Pricing',
            style: (isWide
                    ? theme.textTheme.headlineLarge
                    : theme.textTheme.headlineMedium)
                ?.copyWith(fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 500),
            child: Text(
              'Choose the plan that works for you. Upgrade, downgrade, or cancel anytime.',
              style: theme.textTheme.bodyLarge
                  ?.copyWith(color: colorScheme.onSurfaceVariant),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 48),
          plansAsync.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, _) => Center(
              child: Column(
                children: [
                  Icon(Icons.error_outline,
                      size: 48, color: colorScheme.error),
                  const SizedBox(height: 16),
                  Text('Failed to load plans',
                      style: theme.textTheme.titleMedium),
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
              if (plans.isEmpty) {
                return _buildFreePlanOnly(theme, colorScheme, auth, context);
              }
              return Wrap(
                spacing: 24,
                runSpacing: 24,
                alignment: WrapAlignment.center,
                children: [
                  // Free plan card (always shown)
                  _PlanCard(
                    name: 'Free',
                    price: 0,
                    period: '/month',
                    features: const [
                      'Access to free courses',
                      'Community discussions',
                      'Basic quizzes',
                    ],
                    isHighlighted: false,
                    ctaLabel: auth.isAuthenticated
                        ? 'Current Plan'
                        : 'Get Started',
                    onTap: auth.isAuthenticated
                        ? null
                        : () => context.go('/register'),
                  ),
                  // Dynamic plans from server
                  ...plans.map((plan) {
                    final features = _parseFeatures(plan.features);
                    return _PlanCard(
                      name: plan.name,
                      price: plan.priceMonthly,
                      yearlyPrice: plan.priceYearly,
                      period: '/month',
                      features: features,
                      isHighlighted: true,
                      ctaLabel: auth.isAuthenticated
                          ? 'Subscribe'
                          : 'Sign Up & Subscribe',
                      onTap: () {
                        if (auth.isAuthenticated) {
                          context.go('/checkout/${plan.slug}');
                        } else {
                          context.go('/register');
                        }
                      },
                    );
                  }),
                ],
              );
            },
          ),
          const SizedBox(height: 64),
          // FAQ section
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 700),
            child: Column(
              children: [
                Text(
                  'Frequently Asked Questions',
                  style: theme.textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                const _FaqTile(
                  question: 'Can I cancel anytime?',
                  answer:
                      'Yes, you can cancel your subscription at any time. '
                      'You\'ll continue to have access until the end of your billing period.',
                ),
                const _FaqTile(
                  question: 'Do I get a certificate?',
                  answer:
                      'Yes! Upon completing a course, you receive a verifiable certificate '
                      'with a unique number that can be shared with employers.',
                ),
                const _FaqTile(
                  question: 'What payment methods are accepted?',
                  answer:
                      'We accept all major credit cards, debit cards, UPI, and net banking '
                      'through Razorpay (India) and Stripe (international).',
                ),
                const _FaqTile(
                  question: 'Is there a free trial?',
                  answer:
                      'Many of our courses offer free preview lectures. '
                      'You can browse all course curriculums before subscribing.',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFreePlanOnly(
      ThemeData theme, ColorScheme colorScheme, AuthState auth, BuildContext context) {
    return _PlanCard(
      name: 'Free',
      price: 0,
      period: '',
      features: const [
        'Access to free courses',
        'Community discussions',
        'Basic quizzes',
        'Course certificates',
      ],
      isHighlighted: true,
      ctaLabel:
          auth.isAuthenticated ? 'Start Learning' : 'Get Started Free',
      onTap: () {
        if (auth.isAuthenticated) {
          context.go('/courses');
        } else {
          context.go('/register');
        }
      },
    );
  }

  List<String> _parseFeatures(String? featuresJson) {
    if (featuresJson == null || featuresJson.isEmpty) {
      return ['All courses included', 'Certificates', 'Priority support'];
    }
    // Features stored as JSON array string
    try {
      // Simple comma-separated fallback
      return featuresJson
          .replaceAll('[', '')
          .replaceAll(']', '')
          .replaceAll('"', '')
          .split(',')
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList();
    } catch (_) {
      return ['All courses included', 'Certificates', 'Priority support'];
    }
  }
}

class _PlanCard extends StatelessWidget {
  final String name;
  final double price;
  final double? yearlyPrice;
  final String period;
  final List<String> features;
  final bool isHighlighted;
  final String ctaLabel;
  final VoidCallback? onTap;

  const _PlanCard({
    required this.name,
    required this.price,
    this.yearlyPrice,
    required this.period,
    required this.features,
    required this.isHighlighted,
    required this.ctaLabel,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return SizedBox(
      width: 320,
      child: Card(
        elevation: isHighlighted ? 4 : 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: isHighlighted
              ? BorderSide(color: colorScheme.primary, width: 2)
              : BorderSide(color: colorScheme.outlineVariant),
        ),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (isHighlighted)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: colorScheme.primary,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Popular',
                    style: theme.textTheme.labelSmall
                        ?.copyWith(color: colorScheme.onPrimary),
                  ),
                ),
              if (isHighlighted) const SizedBox(height: 12),
              Text(name,
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    price > 0 ? '\$${price.toStringAsFixed(0)}' : 'Free',
                    style: theme.textTheme.displaySmall
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  if (price > 0)
                    Text(period,
                        style: theme.textTheme.bodyMedium
                            ?.copyWith(color: colorScheme.onSurfaceVariant)),
                ],
              ),
              if (yearlyPrice != null && yearlyPrice! > 0) ...[
                const SizedBox(height: 4),
                Text(
                  '\$${yearlyPrice!.toStringAsFixed(0)}/year (save ${((1 - yearlyPrice! / (price * 12)) * 100).toStringAsFixed(0)}%)',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: colorScheme.primary),
                ),
              ],
              const SizedBox(height: 24),
              ...features.map((f) => Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle,
                            size: 20, color: colorScheme.primary),
                        const SizedBox(width: 8),
                        Expanded(
                            child: Text(f,
                                style: theme.textTheme.bodyMedium)),
                      ],
                    ),
                  )),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: isHighlighted
                    ? ElevatedButton(
                        onPressed: onTap,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: Text(ctaLabel),
                      )
                    : OutlinedButton(
                        onPressed: onTap,
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: Text(ctaLabel),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _FaqTile extends StatelessWidget {
  final String question;
  final String answer;

  const _FaqTile({required this.question, required this.answer});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        title: Text(question,
            style: Theme.of(context)
                .textTheme
                .titleSmall
                ?.copyWith(fontWeight: FontWeight.w600)),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Text(answer,
                style: Theme.of(context).textTheme.bodyMedium),
          ),
        ],
      ),
    );
  }
}
