import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/course_provider.dart';
import '../../courses/widgets/course_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;
    final featuredCourses = ref.watch(featuredCoursesProvider);

    return SingleChildScrollView(
      child: Column(
        children: [
          // Hero Section
          Container(
            width: double.infinity,
            padding: EdgeInsets.symmetric(
              horizontal: isWide ? 64 : 24,
              vertical: isWide ? 80 : 48,
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
              children: [
                Text(
                  'Learn Without Limits',
                  style: (isWide
                          ? theme.textTheme.displayMedium
                          : theme.textTheme.headlineLarge)
                      ?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 600),
                  child: Text(
                    'AI-powered courses designed to take your skills to the next level. '
                    'Learn at your own pace with video lessons, quizzes, and certificates.',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 32),
                Wrap(
                  spacing: 16,
                  runSpacing: 12,
                  alignment: WrapAlignment.center,
                  children: [
                    ElevatedButton.icon(
                      onPressed: () => context.go('/courses'),
                      icon: const Icon(Icons.explore),
                      label: const Text('Explore Courses'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 32, vertical: 16),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => context.go('/register'),
                      icon: const Icon(Icons.person_add),
                      label: const Text('Get Started Free'),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 32, vertical: 16),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Featured Courses Section
          featuredCourses.when(
            data: (courses) {
              if (courses.isEmpty) return const SizedBox.shrink();
              return Padding(
                padding: EdgeInsets.symmetric(
                  horizontal: isWide ? 64 : 16,
                  vertical: 48,
                ),
                child: Column(
                  children: [
                    Text(
                      'Featured Courses',
                      style: theme.textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Hand-picked courses to get you started',
                      style: theme.textTheme.bodyLarge
                          ?.copyWith(color: colorScheme.onSurfaceVariant),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    SizedBox(
                      height: 340,
                      child: ListView.separated(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        itemCount: courses.length,
                        separatorBuilder: (_, __) => const SizedBox(width: 16),
                        itemBuilder: (context, index) {
                          final course = courses[index];
                          return SizedBox(
                            width: 280,
                            child: CourseCard(
                              course: {
                                'title': course.title,
                                'slug': course.slug,
                                'shortDescription': course.shortDescription,
                                'thumbnailUrl': course.thumbnailUrl,
                                'difficulty': course.difficulty,
                                'avgRating': course.avgRating,
                                'reviewCount': course.reviewCount,
                                'enrollmentCount': course.enrollmentCount,
                                'totalLectures': course.totalLectures,
                                'durationMinutes': course.durationMinutes,
                                'price': course.price,
                                'isFeatured': course.isFeatured,
                              },
                              onTap: () =>
                                  context.go('/courses/${course.slug}'),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextButton.icon(
                      onPressed: () => context.go('/courses'),
                      icon: const Text('View All Courses'),
                      label: const Icon(Icons.arrow_forward, size: 18),
                    ),
                  ],
                ),
              );
            },
            loading: () => const Padding(
              padding: EdgeInsets.symmetric(vertical: 48),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (_, __) => const SizedBox.shrink(),
          ),

          // Features Section
          Padding(
            padding: EdgeInsets.symmetric(
              horizontal: isWide ? 64 : 24,
              vertical: 48,
            ),
            child: Column(
              children: [
                Text(
                  'Why Choose Ganakys Academy?',
                  style: theme.textTheme.headlineSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),
                Wrap(
                  spacing: 24,
                  runSpacing: 24,
                  alignment: WrapAlignment.center,
                  children: [
                    _FeatureCard(
                      icon: Icons.auto_awesome,
                      title: 'AI-Powered Content',
                      description:
                          'Courses generated with cutting-edge AI for comprehensive, up-to-date learning.',
                      colorScheme: colorScheme,
                    ),
                    _FeatureCard(
                      icon: Icons.play_circle_outline,
                      title: 'Video Lessons',
                      description:
                          'Watch engaging video lectures with narration, slides, and illustrations.',
                      colorScheme: colorScheme,
                    ),
                    _FeatureCard(
                      icon: Icons.quiz,
                      title: 'Quizzes & Assessments',
                      description:
                          'Test your knowledge with section quizzes and final assessments.',
                      colorScheme: colorScheme,
                    ),
                    _FeatureCard(
                      icon: Icons.verified,
                      title: 'Certificates',
                      description:
                          'Earn verifiable certificates upon course completion.',
                      colorScheme: colorScheme,
                    ),
                    _FeatureCard(
                      icon: Icons.note_alt,
                      title: 'Notes & Bookmarks',
                      description:
                          'Take timestamped notes and bookmark important moments in lectures.',
                      colorScheme: colorScheme,
                    ),
                    _FeatureCard(
                      icon: Icons.forum,
                      title: 'Discussions',
                      description:
                          'Ask questions and engage in course discussions with other learners.',
                      colorScheme: colorScheme,
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Footer
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
            color: colorScheme.surfaceContainerHighest,
            child: Column(
              children: [
                Wrap(
                  spacing: 24,
                  runSpacing: 8,
                  alignment: WrapAlignment.center,
                  children: [
                    TextButton(
                      onPressed: () => context.go('/about'),
                      child: const Text('About'),
                    ),
                    TextButton(
                      onPressed: () => context.go('/pricing'),
                      child: const Text('Pricing'),
                    ),
                    TextButton(
                      onPressed: () => context.go('/privacy'),
                      child: const Text('Privacy Policy'),
                    ),
                    TextButton(
                      onPressed: () => context.go('/terms'),
                      child: const Text('Terms of Service'),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  '\u00a9 2026 Ganakys Academy. All rights reserved.',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: colorScheme.onSurfaceVariant),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final ColorScheme colorScheme;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.description,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 300,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colorScheme.primaryContainer,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: colorScheme.primary, size: 28),
              ),
              const SizedBox(height: 16),
              Text(
                title,
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                description,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
