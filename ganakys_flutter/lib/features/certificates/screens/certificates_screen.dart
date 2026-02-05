import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:share_plus/share_plus.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/client_provider.dart';

// --- Provider ---

final _certificatesProvider =
    FutureProvider.family<List<Certificate>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.certificate.getCertificates(userId);
});

// --- Screen ---

class CertificatesScreen extends ConsumerWidget {
  const CertificatesScreen({super.key});

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

    final certsAsync = ref.watch(_certificatesProvider(userId));

    return SingleChildScrollView(
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 48 : 16,
        vertical: 24,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'My Certificates',
            style: theme.textTheme.headlineMedium
                ?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Certificates earned upon course completion',
            style: theme.textTheme.bodyLarge
                ?.copyWith(color: colorScheme.onSurfaceVariant),
          ),
          const SizedBox(height: 24),
          certsAsync.when(
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(48),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, _) => Center(
              child: Padding(
                padding: const EdgeInsets.all(48),
                child: Column(
                  children: [
                    Icon(Icons.error_outline,
                        size: 48, color: colorScheme.error),
                    const SizedBox(height: 16),
                    Text('Failed to load certificates: $error'),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () =>
                          ref.invalidate(_certificatesProvider(userId)),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
            data: (certificates) {
              if (certificates.isEmpty) {
                return _EmptyCertificates(colorScheme: colorScheme);
              }
              return _CertificateGrid(
                certificates: certificates,
                isWide: isWide,
              );
            },
          ),
        ],
      ),
    );
  }
}

// --- Empty State ---

class _EmptyCertificates extends StatelessWidget {
  final ColorScheme colorScheme;

  const _EmptyCertificates({required this.colorScheme});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 64),
        child: Column(
          children: [
            Icon(Icons.workspace_premium_outlined,
                size: 80, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'No certificates yet',
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Complete a course to earn your first certificate',
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: colorScheme.onSurfaceVariant),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => context.go('/courses'),
              icon: const Icon(Icons.explore),
              label: const Text('Browse Courses'),
            ),
          ],
        ),
      ),
    );
  }
}

// --- Certificate Grid ---

class _CertificateGrid extends StatelessWidget {
  final List<Certificate> certificates;
  final bool isWide;

  const _CertificateGrid({
    required this.certificates,
    required this.isWide,
  });

  @override
  Widget build(BuildContext context) {
    final crossAxisCount = isWide ? 3 : 1;

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: isWide ? 1.3 : 1.8,
      ),
      itemCount: certificates.length,
      itemBuilder: (context, index) {
        return _CertificateCard(certificate: certificates[index]);
      },
    );
  }
}

// --- Certificate Card ---

class _CertificateCard extends StatelessWidget {
  final Certificate certificate;

  const _CertificateCard({required this.certificate});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final dateFormat = DateFormat.yMMMd();

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => _openPdf(context),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.workspace_premium,
                    color: colorScheme.primary,
                    size: 32,
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.share, size: 20),
                    tooltip: 'Share certificate',
                    onPressed: () => _shareCertificate(),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'Course #${certificate.courseId}',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Text(
                'Certificate: ${certificate.certificateNumber}',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const Spacer(),
              Row(
                children: [
                  Icon(Icons.calendar_today,
                      size: 14, color: colorScheme.onSurfaceVariant),
                  const SizedBox(width: 4),
                  Text(
                    dateFormat.format(certificate.issuedAt),
                    style: theme.textTheme.bodySmall
                        ?.copyWith(color: colorScheme.onSurfaceVariant),
                  ),
                  const Spacer(),
                  if (certificate.pdfUrl != null)
                    Icon(Icons.picture_as_pdf,
                        size: 18, color: colorScheme.primary),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openPdf(BuildContext context) async {
    final pdfUrl = certificate.pdfUrl;
    if (pdfUrl != null && pdfUrl.isNotEmpty) {
      final uri = Uri.parse(pdfUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not open certificate PDF')),
        );
      }
    } else if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('PDF not available for this certificate')),
      );
    }
  }

  void _shareCertificate() {
    final url = certificate.pdfUrl ?? '';
    final text = url.isNotEmpty
        ? 'Check out my certificate (${certificate.certificateNumber}): $url'
        : 'I earned certificate ${certificate.certificateNumber}!';
    Share.share(text);
  }
}
