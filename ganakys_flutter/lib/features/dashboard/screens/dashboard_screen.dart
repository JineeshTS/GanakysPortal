import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/client_provider.dart';

// --- Providers ---

final _enrollmentsProvider =
    FutureProvider.family<List<Map<String, dynamic>>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.enrollment.getMyEnrollments(userId);
});

final _continueLearningProvider =
    FutureProvider.family<List<Map<String, dynamic>>, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  return await client.enrollment.getContinueLearning(userId);
});

final _certificateCountProvider =
    FutureProvider.family<int, int>((ref, userId) async {
  final client = ref.watch(clientProvider);
  final certs = await client.certificate.getCertificates(userId);
  return certs.length;
});

// --- Screen ---

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

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

    final enrollmentsAsync = ref.watch(_enrollmentsProvider(userId));
    final continueAsync = ref.watch(_continueLearningProvider(userId));
    final certCountAsync = ref.watch(_certificateCountProvider(userId));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(_enrollmentsProvider(userId));
        ref.invalidate(_continueLearningProvider(userId));
        ref.invalidate(_certificateCountProvider(userId));
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.symmetric(
          horizontal: isWide ? 48 : 16,
          vertical: 24,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome
            Text(
              'Welcome back, ${auth.user?.name ?? 'Student'}!',
              style: theme.textTheme.headlineMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),

            // Stats row
            _StatsRow(
              enrollmentsAsync: enrollmentsAsync,
              certCountAsync: certCountAsync,
              colorScheme: colorScheme,
            ),
            const SizedBox(height: 32),

            // Continue Learning
            Text(
              'Continue Learning',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _ContinueLearningSection(continueAsync: continueAsync),
            const SizedBox(height: 32),

            // My Courses
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'My Courses',
                  style: theme.textTheme.titleLarge
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                TextButton(
                  onPressed: () => context.go('/my-courses'),
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _MyCoursesSection(enrollmentsAsync: enrollmentsAsync),
          ],
        ),
      ),
    );
  }
}

// --- Stats Row ---

class _StatsRow extends StatelessWidget {
  final AsyncValue<List<Map<String, dynamic>>> enrollmentsAsync;
  final AsyncValue<int> certCountAsync;
  final ColorScheme colorScheme;

  const _StatsRow({
    required this.enrollmentsAsync,
    required this.certCountAsync,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    final enrollments = enrollmentsAsync.valueOrNull ?? [];
    final inProgress =
        enrollments.where((e) => e['status'] == 'active').length;
    final completed =
        enrollments.where((e) => e['status'] == 'completed').length;
    final certCount = certCountAsync.valueOrNull ?? 0;

    return Wrap(
      spacing: 16,
      runSpacing: 16,
      children: [
        _StatCard(
          icon: Icons.book,
          label: 'In Progress',
          value: '$inProgress',
          colorScheme: colorScheme,
        ),
        _StatCard(
          icon: Icons.check_circle,
          label: 'Completed',
          value: '$completed',
          colorScheme: colorScheme,
        ),
        _StatCard(
          icon: Icons.verified,
          label: 'Certificates',
          value: '$certCount',
          colorScheme: colorScheme,
        ),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final ColorScheme colorScheme;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: colorScheme.primary),
              const SizedBox(height: 12),
              Text(
                value,
                style: Theme.of(context)
                    .textTheme
                    .headlineMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- Continue Learning Section ---

class _ContinueLearningSection extends StatelessWidget {
  final AsyncValue<List<Map<String, dynamic>>> continueAsync;

  const _ContinueLearningSection({required this.continueAsync});

  @override
  Widget build(BuildContext context) {
    return continueAsync.when(
      loading: () => const SizedBox(
        height: 180,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text('Failed to load: $error'),
        ),
      ),
      data: (items) {
        if (items.isEmpty) {
          return _EmptyState(
            icon: Icons.school_outlined,
            title: 'No courses in progress',
            subtitle: 'Enroll in a course to get started',
            buttonLabel: 'Browse Courses',
            onPressed: () => context.go('/courses'),
          );
        }
        return SizedBox(
          height: 200,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: items.length,
            separatorBuilder: (_, __) => const SizedBox(width: 16),
            itemBuilder: (context, index) {
              final item = items[index];
              return _ContinueLearningCard(item: item);
            },
          ),
        );
      },
    );
  }
}

class _ContinueLearningCard extends StatelessWidget {
  final Map<String, dynamic> item;

  const _ContinueLearningCard({required this.item});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final title = item['title'] as String? ?? 'Untitled';
    final slug = item['slug'] as String? ?? '';
    final thumbnailUrl = item['thumbnailUrl'] as String?;
    final progress = (item['progressPercent'] as num?)?.toDouble() ?? 0;
    final lastLectureTitle = item['lastLectureTitle'] as String? ?? '';
    final lastLectureId = item['lastLectureId'] as int?;

    return SizedBox(
      width: 280,
      child: Card(
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: () {
            if (slug.isNotEmpty) {
              final query =
                  lastLectureId != null ? '?lecture=$lastLectureId' : '';
              context.go('/courses/$slug/learn$query');
            }
          },
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Thumbnail
              SizedBox(
                height: 90,
                width: double.infinity,
                child: thumbnailUrl != null && thumbnailUrl.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: thumbnailUrl,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          color: colorScheme.surfaceContainerHighest,
                          child: const Center(
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        ),
                        errorWidget: (_, __, ___) => Container(
                          color: colorScheme.surfaceContainerHighest,
                          child: Icon(Icons.school,
                              size: 32, color: colorScheme.outline),
                        ),
                      )
                    : Container(
                        color: colorScheme.surfaceContainerHighest,
                        child: Center(
                          child: Icon(Icons.school,
                              size: 32, color: colorScheme.outline),
                        ),
                      ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.titleSmall
                            ?.copyWith(fontWeight: FontWeight.bold),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (lastLectureTitle.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Text(
                          lastLectureTitle,
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      const Spacer(),
                      // Progress bar
                      Row(
                        children: [
                          Expanded(
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: LinearProgressIndicator(
                                value: progress / 100,
                                minHeight: 6,
                                backgroundColor:
                                    colorScheme.surfaceContainerHighest,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            '${progress.toStringAsFixed(0)}%',
                            style: theme.textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// --- My Courses Section ---

class _MyCoursesSection extends StatelessWidget {
  final AsyncValue<List<Map<String, dynamic>>> enrollmentsAsync;

  const _MyCoursesSection({required this.enrollmentsAsync});

  @override
  Widget build(BuildContext context) {
    return enrollmentsAsync.when(
      loading: () => const SizedBox(
        height: 100,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text('Failed to load enrollments: $error'),
        ),
      ),
      data: (enrollments) {
        if (enrollments.isEmpty) {
          return _EmptyState(
            icon: Icons.school_outlined,
            title: 'No courses yet',
            subtitle: 'Enroll in a course to get started',
            buttonLabel: 'Browse Courses',
            onPressed: () => context.go('/courses'),
          );
        }
        // Show first 5 enrollments
        final displayList = enrollments.take(5).toList();
        return Column(
          children: displayList.map((enrollment) {
            return _EnrollmentListTile(enrollment: enrollment);
          }).toList(),
        );
      },
    );
  }
}

class _EnrollmentListTile extends StatelessWidget {
  final Map<String, dynamic> enrollment;

  const _EnrollmentListTile({required this.enrollment});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final title = enrollment['title'] as String? ?? 'Untitled';
    final slug = enrollment['slug'] as String? ?? '';
    final thumbnailUrl = enrollment['thumbnailUrl'] as String?;
    final progress =
        (enrollment['progressPercent'] as num?)?.toDouble() ?? 0;
    final status = enrollment['status'] as String? ?? 'active';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: SizedBox(
            width: 56,
            height: 40,
            child: thumbnailUrl != null && thumbnailUrl.isNotEmpty
                ? CachedNetworkImage(
                    imageUrl: thumbnailUrl,
                    fit: BoxFit.cover,
                    errorWidget: (_, __, ___) => Container(
                      color: colorScheme.surfaceContainerHighest,
                      child: Icon(Icons.school,
                          size: 20, color: colorScheme.outline),
                    ),
                  )
                : Container(
                    color: colorScheme.surfaceContainerHighest,
                    child: Icon(Icons.school,
                        size: 20, color: colorScheme.outline),
                  ),
          ),
        ),
        title: Text(
          title,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Row(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progress / 100,
                  minHeight: 4,
                  backgroundColor: colorScheme.surfaceContainerHighest,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${progress.toStringAsFixed(0)}%',
              style: theme.textTheme.bodySmall,
            ),
            if (status == 'completed') ...[
              const SizedBox(width: 8),
              Icon(Icons.check_circle, size: 16, color: colorScheme.primary),
            ],
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          if (slug.isNotEmpty) {
            context.go('/courses/$slug');
          }
        },
      ),
    );
  }
}

// --- Empty State ---

class _EmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String buttonLabel;
  final VoidCallback onPressed;

  const _EmptyState({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.buttonLabel,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 48),
        child: Column(
          children: [
            Icon(icon, size: 64, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text(title, style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(
              subtitle,
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: colorScheme.onSurfaceVariant),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: onPressed,
              icon: const Icon(Icons.explore),
              label: Text(buttonLabel),
            ),
          ],
        ),
      ),
    );
  }
}
