import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../core/providers/course_provider.dart';
import '../../../core/providers/auth_provider.dart';

class CourseDetailScreen extends ConsumerWidget {
  final String slug;

  const CourseDetailScreen({super.key, required this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final courseAsync = ref.watch(courseDetailProvider(slug));
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    return courseAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: colorScheme.error),
            const SizedBox(height: 16),
            Text('Failed to load course', style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => ref.invalidate(courseDetailProvider(slug)),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (data) {
        if (data == null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.search_off, size: 64, color: colorScheme.outline),
                const SizedBox(height: 16),
                Text('Course not found', style: theme.textTheme.titleLarge),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => context.go('/courses'),
                  child: const Text('Browse Courses'),
                ),
              ],
            ),
          );
        }

        final course = data['course'] as Map<String, dynamic>? ?? {};
        final sections =
            (data['sections'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final reviews =
            (data['reviews'] as List?)?.cast<Map<String, dynamic>>() ?? [];

        return SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hero header
              _CourseHero(course: course, isWide: isWide),
              // Content
              Padding(
                padding: EdgeInsets.symmetric(
                    horizontal: isWide ? 64 : 16, vertical: 24),
                child: isWide
                    ? Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            flex: 3,
                            child: _CourseContent(
                              course: course,
                              sections: sections,
                              reviews: reviews,
                            ),
                          ),
                          const SizedBox(width: 32),
                          SizedBox(
                            width: 320,
                            child: _CourseSidebar(
                                course: course, slug: slug),
                          ),
                        ],
                      )
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _CourseSidebar(course: course, slug: slug),
                          const SizedBox(height: 24),
                          _CourseContent(
                            course: course,
                            sections: sections,
                            reviews: reviews,
                          ),
                        ],
                      ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _CourseHero extends StatelessWidget {
  final Map<String, dynamic> course;
  final bool isWide;

  const _CourseHero({required this.course, required this.isWide});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final title = course['title'] as String? ?? 'Untitled Course';
    final description = course['description'] as String? ?? '';
    final difficulty = course['difficulty'] as String? ?? '';
    final avgRating = (course['avgRating'] as num?)?.toDouble() ?? 0;
    final reviewCount = course['reviewCount'] as int? ?? 0;
    final enrollmentCount = course['enrollmentCount'] as int? ?? 0;

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 64 : 24,
        vertical: isWide ? 48 : 24,
      ),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colorScheme.primaryContainer,
            colorScheme.secondaryContainer,
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Breadcrumb
          Row(
            children: [
              InkWell(
                onTap: () => context.go('/courses'),
                child: Text('Courses',
                    style: theme.textTheme.bodyMedium
                        ?.copyWith(color: colorScheme.primary)),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 8),
                child: Icon(Icons.chevron_right, size: 18),
              ),
              Flexible(
                child: Text(title,
                    style: theme.textTheme.bodyMedium,
                    overflow: TextOverflow.ellipsis),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ConstrainedBox(
            constraints: BoxConstraints(maxWidth: isWide ? 700 : double.infinity),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (difficulty.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Chip(
                      label: Text(difficulty[0].toUpperCase() +
                          difficulty.substring(1)),
                      visualDensity: VisualDensity.compact,
                    ),
                  ),
                Text(title,
                    style: (isWide
                            ? theme.textTheme.headlineLarge
                            : theme.textTheme.headlineMedium)
                        ?.copyWith(fontWeight: FontWeight.bold)),
                if (description.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(description,
                      style: theme.textTheme.bodyLarge
                          ?.copyWith(color: colorScheme.onSurfaceVariant),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis),
                ],
                const SizedBox(height: 16),
                Wrap(
                  spacing: 24,
                  runSpacing: 8,
                  children: [
                    if (avgRating > 0)
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.star, size: 20, color: Colors.amber[700]),
                          const SizedBox(width: 4),
                          Text('${avgRating.toStringAsFixed(1)} ($reviewCount reviews)',
                              style: theme.textTheme.bodyMedium),
                        ],
                      ),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.people, size: 20),
                        const SizedBox(width: 4),
                        Text('$enrollmentCount students',
                            style: theme.textTheme.bodyMedium),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _CourseSidebar extends ConsumerWidget {
  final Map<String, dynamic> course;
  final String slug;

  const _CourseSidebar({required this.course, required this.slug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final auth = ref.watch(authProvider);

    final price = (course['price'] as num?)?.toDouble() ?? 0;
    final totalLectures = course['totalLectures'] as int? ?? 0;
    final totalSections = course['totalSections'] as int? ?? 0;
    final durationMinutes = course['durationMinutes'] as int? ?? 0;
    final thumbnailUrl = course['thumbnailUrl'] as String?;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Thumbnail
            if (thumbnailUrl != null && thumbnailUrl.isNotEmpty)
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(thumbnailUrl, fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                            color: colorScheme.surfaceContainerHighest,
                            child: Icon(Icons.school,
                                size: 48, color: colorScheme.outline),
                          )),
                ),
              ),
            const SizedBox(height: 16),
            // Price
            Text(
              price > 0 ? '\$${price.toStringAsFixed(2)}' : 'Free',
              style: theme.textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: price > 0 ? null : Colors.green,
              ),
            ),
            const SizedBox(height: 16),
            // CTA button
            ElevatedButton.icon(
              onPressed: () {
                if (auth.isAuthenticated) {
                  context.go('/courses/$slug/learn');
                } else {
                  context.go('/login?redirect=/courses/$slug');
                }
              },
              icon: const Icon(Icons.play_arrow),
              label: Text(auth.isAuthenticated
                  ? 'Start Learning'
                  : 'Login to Enroll'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
            const SizedBox(height: 20),
            // Course info
            _InfoRow(
                icon: Icons.library_books,
                label: '$totalSections sections'),
            const SizedBox(height: 8),
            _InfoRow(
                icon: Icons.play_lesson, label: '$totalLectures lectures'),
            if (durationMinutes > 0) ...[
              const SizedBox(height: 8),
              _InfoRow(
                  icon: Icons.access_time,
                  label: _formatDuration(durationMinutes)),
            ],
            const SizedBox(height: 8),
            _InfoRow(
                icon: Icons.verified, label: 'Certificate of completion'),
            const SizedBox(height: 8),
            _InfoRow(icon: Icons.all_inclusive, label: 'Lifetime access'),
          ],
        ),
      ),
    );
  }

  String _formatDuration(int minutes) {
    if (minutes < 60) return '$minutes minutes';
    final hours = minutes ~/ 60;
    final mins = minutes % 60;
    return mins > 0 ? '$hours hours $mins minutes' : '$hours hours';
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoRow({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Theme.of(context).colorScheme.primary),
        const SizedBox(width: 8),
        Expanded(
            child:
                Text(label, style: Theme.of(context).textTheme.bodyMedium)),
      ],
    );
  }
}

class _CourseContent extends StatelessWidget {
  final Map<String, dynamic> course;
  final List<Map<String, dynamic>> sections;
  final List<Map<String, dynamic>> reviews;

  const _CourseContent({
    required this.course,
    required this.sections,
    required this.reviews,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final description = course['description'] as String? ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Description
        if (description.isNotEmpty) ...[
          Text('About This Course',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          MarkdownBody(data: description),
          const SizedBox(height: 32),
        ],

        // Curriculum
        if (sections.isNotEmpty) ...[
          Text('Curriculum',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(
            '${sections.length} sections',
            style: theme.textTheme.bodyMedium
                ?.copyWith(color: colorScheme.onSurfaceVariant),
          ),
          const SizedBox(height: 12),
          ...sections.map((section) => _SectionTile(section: section)),
          const SizedBox(height: 32),
        ],

        // Reviews
        if (reviews.isNotEmpty) ...[
          Text('Student Reviews',
              style: theme.textTheme.titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          ...reviews.map((review) => _ReviewTile(review: review)),
        ],
      ],
    );
  }
}

class _SectionTile extends StatelessWidget {
  final Map<String, dynamic> section;

  const _SectionTile({required this.section});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final title = section['title'] as String? ?? 'Untitled Section';
    final lectures =
        (section['lectures'] as List?)?.cast<Map<String, dynamic>>() ?? [];

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        title: Text(title,
            style: theme.textTheme.titleSmall
                ?.copyWith(fontWeight: FontWeight.w600)),
        subtitle: Text('${lectures.length} lectures',
            style: theme.textTheme.bodySmall
                ?.copyWith(color: colorScheme.onSurfaceVariant)),
        children: lectures.map((lecture) {
          final lectureTitle =
              lecture['title'] as String? ?? 'Untitled Lecture';
          final type = lecture['type'] as String? ?? 'video';
          final duration = lecture['durationMinutes'] as int? ?? 0;
          final isFreePreview = lecture['isFreePreview'] as bool? ?? false;

          return ListTile(
            dense: true,
            leading: Icon(
              type == 'quiz'
                  ? Icons.quiz
                  : type == 'text'
                      ? Icons.article
                      : Icons.play_circle_outline,
              size: 20,
              color: colorScheme.onSurfaceVariant,
            ),
            title: Text(lectureTitle, style: theme.textTheme.bodyMedium),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (isFreePreview)
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: Chip(
                      label: const Text('Preview'),
                      visualDensity: VisualDensity.compact,
                      labelStyle: theme.textTheme.labelSmall,
                      padding: EdgeInsets.zero,
                    ),
                  ),
                if (duration > 0)
                  Text('${duration}m',
                      style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant)),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _ReviewTile extends StatelessWidget {
  final Map<String, dynamic> review;

  const _ReviewTile({required this.review});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final rating = review['rating'] as int? ?? 0;
    final comment = review['comment'] as String? ?? '';
    final userName = review['userName'] as String? ?? 'Anonymous';

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 16,
                  backgroundColor: colorScheme.primaryContainer,
                  child: Text(
                    userName.isNotEmpty ? userName[0].toUpperCase() : '?',
                    style: TextStyle(
                      color: colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Text(userName,
                    style: theme.textTheme.titleSmall
                        ?.copyWith(fontWeight: FontWeight.w600)),
                const Spacer(),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: List.generate(
                    5,
                    (i) => Icon(
                      i < rating ? Icons.star : Icons.star_border,
                      size: 16,
                      color: Colors.amber[700],
                    ),
                  ),
                ),
              ],
            ),
            if (comment.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(comment, style: theme.textTheme.bodyMedium),
            ],
          ],
        ),
      ),
    );
  }
}
