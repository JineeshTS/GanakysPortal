import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:ganakys_client/ganakys_client.dart';
import '../../../core/client_provider.dart';

final pageProvider =
    FutureProvider.family<ContentPage?, String>((ref, slug) async {
  final client = ref.watch(clientProvider);
  return await client.page.getPage(slug);
});

class StaticPageScreen extends ConsumerWidget {
  final String slug;

  const StaticPageScreen({super.key, required this.slug});

  String get _fallbackTitle {
    switch (slug) {
      case 'privacy':
        return 'Privacy Policy';
      case 'terms':
        return 'Terms of Service';
      case 'about':
        return 'About Us';
      default:
        return slug;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pageAsync = ref.watch(pageProvider(slug));
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    return pageAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (_, __) => _buildFallback(theme, colorScheme, isWide),
      data: (page) {
        if (page == null) {
          return _buildFallback(theme, colorScheme, isWide);
        }

        return SingleChildScrollView(
          padding: EdgeInsets.symmetric(
              horizontal: isWide ? 64 : 24, vertical: 32),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 800),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(page.title,
                      style: theme.textTheme.headlineMedium
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(
                    'Last updated: ${_formatDate(page.updatedAt)}',
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: colorScheme.onSurfaceVariant),
                  ),
                  const SizedBox(height: 24),
                  const Divider(),
                  const SizedBox(height: 16),
                  MarkdownBody(
                    data: page.content,
                    styleSheet: MarkdownStyleSheet(
                      h1: theme.textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                      h2: theme.textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.bold),
                      h3: theme.textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.bold),
                      p: theme.textTheme.bodyLarge,
                      listBullet: theme.textTheme.bodyLarge,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildFallback(ThemeData theme, ColorScheme colorScheme, bool isWide) {
    return SingleChildScrollView(
      padding:
          EdgeInsets.symmetric(horizontal: isWide ? 64 : 24, vertical: 32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_fallbackTitle,
                  style: theme.textTheme.headlineMedium
                      ?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              Text(
                'This page content will be available soon.',
                style: theme.textTheme.bodyLarge
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[date.month - 1]} ${date.day}, ${date.year}';
  }
}
