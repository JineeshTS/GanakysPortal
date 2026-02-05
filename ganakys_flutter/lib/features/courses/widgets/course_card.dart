import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

class CourseCard extends StatelessWidget {
  final Map<String, dynamic> course;
  final VoidCallback? onTap;

  const CourseCard({super.key, required this.course, this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final title = course['title'] as String? ?? 'Untitled';
    final shortDescription = course['shortDescription'] as String? ?? '';
    final thumbnailUrl = course['thumbnailUrl'] as String?;
    final difficulty = course['difficulty'] as String? ?? '';
    final avgRating = (course['avgRating'] as num?)?.toDouble() ?? 0;
    final reviewCount = course['reviewCount'] as int? ?? 0;
    final enrollmentCount = course['enrollmentCount'] as int? ?? 0;
    final totalLectures = course['totalLectures'] as int? ?? 0;
    final durationMinutes = course['durationMinutes'] as int? ?? 0;
    final price = (course['price'] as num?)?.toDouble() ?? 0;
    final isFeatured = course['isFeatured'] as bool? ?? false;

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Thumbnail
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (thumbnailUrl != null && thumbnailUrl.isNotEmpty)
                    CachedNetworkImage(
                      imageUrl: thumbnailUrl,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: colorScheme.surfaceContainerHighest,
                        child: const Center(
                            child: CircularProgressIndicator(strokeWidth: 2)),
                      ),
                      errorWidget: (_, __, ___) => _placeholderImage(colorScheme),
                    )
                  else
                    _placeholderImage(colorScheme),
                  // Difficulty badge
                  if (difficulty.isNotEmpty)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: _DifficultyBadge(difficulty: difficulty),
                    ),
                  // Featured badge
                  if (isFeatured)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.amber,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.star, size: 14, color: Colors.black87),
                            SizedBox(width: 2),
                            Text('Featured',
                                style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.black87)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
            // Content
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
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    if (shortDescription.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        shortDescription,
                        style: theme.textTheme.bodySmall
                            ?.copyWith(color: colorScheme.onSurfaceVariant),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    const Spacer(),
                    // Rating row
                    if (avgRating > 0)
                      Row(
                        children: [
                          Icon(Icons.star, size: 16, color: Colors.amber[700]),
                          const SizedBox(width: 4),
                          Text(avgRating.toStringAsFixed(1),
                              style: theme.textTheme.bodySmall
                                  ?.copyWith(fontWeight: FontWeight.bold)),
                          Text(' ($reviewCount)',
                              style: theme.textTheme.bodySmall?.copyWith(
                                  color: colorScheme.onSurfaceVariant)),
                        ],
                      ),
                    const SizedBox(height: 6),
                    // Meta row
                    Row(
                      children: [
                        Icon(Icons.people_outline,
                            size: 14, color: colorScheme.onSurfaceVariant),
                        const SizedBox(width: 4),
                        Text('$enrollmentCount',
                            style: theme.textTheme.bodySmall?.copyWith(
                                color: colorScheme.onSurfaceVariant)),
                        const SizedBox(width: 12),
                        Icon(Icons.play_lesson_outlined,
                            size: 14, color: colorScheme.onSurfaceVariant),
                        const SizedBox(width: 4),
                        Text('$totalLectures',
                            style: theme.textTheme.bodySmall?.copyWith(
                                color: colorScheme.onSurfaceVariant)),
                        if (durationMinutes > 0) ...[
                          const SizedBox(width: 12),
                          Icon(Icons.access_time,
                              size: 14, color: colorScheme.onSurfaceVariant),
                          const SizedBox(width: 4),
                          Text(_formatDuration(durationMinutes),
                              style: theme.textTheme.bodySmall?.copyWith(
                                  color: colorScheme.onSurfaceVariant)),
                        ],
                        const Spacer(),
                        Text(
                          price > 0 ? '\$${price.toStringAsFixed(0)}' : 'Free',
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: price > 0
                                ? colorScheme.primary
                                : Colors.green,
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
    );
  }

  Widget _placeholderImage(ColorScheme colorScheme) {
    return Container(
      color: colorScheme.surfaceContainerHighest,
      child: Center(
        child: Icon(Icons.school, size: 40, color: colorScheme.outline),
      ),
    );
  }

  String _formatDuration(int minutes) {
    if (minutes < 60) return '${minutes}m';
    final hours = minutes ~/ 60;
    final mins = minutes % 60;
    return mins > 0 ? '${hours}h ${mins}m' : '${hours}h';
  }
}

class _DifficultyBadge extends StatelessWidget {
  final String difficulty;

  const _DifficultyBadge({required this.difficulty});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        color = Colors.green;
      case 'intermediate':
        color = Colors.orange;
      case 'advanced':
        color = Colors.red;
      default:
        color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        difficulty[0].toUpperCase() + difficulty.substring(1),
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    );
  }
}
