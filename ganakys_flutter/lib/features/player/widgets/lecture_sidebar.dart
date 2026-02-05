import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/player_provider.dart';

class LectureSidebar extends ConsumerWidget {
  final String courseSlug;

  const LectureSidebar({super.key, required this.courseSlug});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final playerState = ref.watch(playerStateProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    if (playerState.sections.isEmpty) {
      return Center(
        child: Text(
          'No lectures available',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  'Course Content',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (playerState.totalCount > 0)
                Text(
                  '${playerState.completedCount}/${playerState.totalCount}',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: colorScheme.primary,
                  ),
                ),
            ],
          ),
        ),
        if (playerState.totalCount > 0)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: playerState.progressPercent,
                minHeight: 4,
                backgroundColor: colorScheme.surfaceContainerHighest,
                valueColor: AlwaysStoppedAnimation(colorScheme.primary),
              ),
            ),
          ),
        const SizedBox(height: 8),
        const Divider(height: 1),
        Expanded(
          child: ListView.builder(
            padding: EdgeInsets.zero,
            itemCount: playerState.sections.length,
            itemBuilder: (context, index) {
              final section = playerState.sections[index];
              return _SectionExpansionTile(
                section: section,
                currentLectureId: playerState.currentLectureId,
                initiallyExpanded: section.lectures.any(
                  (l) => l.id == playerState.currentLectureId,
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _SectionExpansionTile extends ConsumerWidget {
  final SectionItem section;
  final int? currentLectureId;
  final bool initiallyExpanded;

  const _SectionExpansionTile({
    required this.section,
    required this.currentLectureId,
    this.initiallyExpanded = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final completedInSection =
        section.lectures.where((l) => l.isCompleted).length;

    return ExpansionTile(
      initiallyExpanded: initiallyExpanded,
      tilePadding: const EdgeInsets.symmetric(horizontal: 16),
      childrenPadding: EdgeInsets.zero,
      title: Text(
        section.title,
        style: theme.textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(
        '$completedInSection/${section.lectures.length} lectures',
        style: theme.textTheme.bodySmall?.copyWith(
          color: colorScheme.onSurfaceVariant,
        ),
      ),
      children: section.lectures.map((lecture) {
        final isCurrent = lecture.id == currentLectureId;
        return _LectureTile(
          lecture: lecture,
          isCurrent: isCurrent,
          onTap: () {
            ref.read(playerStateProvider.notifier).selectLecture(lecture.id);
          },
        );
      }).toList(),
    );
  }
}

class _LectureTile extends StatelessWidget {
  final LectureItem lecture;
  final bool isCurrent;
  final VoidCallback onTap;

  const _LectureTile({
    required this.lecture,
    required this.isCurrent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Material(
      color: isCurrent
          ? colorScheme.primaryContainer.withValues(alpha: 0.3)
          : Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            children: [
              // Completion / type icon
              SizedBox(
                width: 24,
                child: lecture.isCompleted
                    ? Icon(Icons.check_circle,
                        size: 20, color: colorScheme.primary)
                    : Icon(
                        lecture.type == 'video'
                            ? Icons.play_circle_outline
                            : lecture.type == 'text'
                                ? Icons.article_outlined
                                : Icons.headphones_outlined,
                        size: 20,
                        color: isCurrent
                            ? colorScheme.primary
                            : colorScheme.onSurfaceVariant,
                      ),
              ),
              const SizedBox(width: 12),
              // Title + duration
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lecture.title,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: isCurrent ? FontWeight.w600 : null,
                        color: isCurrent
                            ? colorScheme.primary
                            : colorScheme.onSurface,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${lecture.durationMinutes} min',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              // Free preview badge
              if (lecture.isFreePreview)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: colorScheme.tertiaryContainer,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'Free',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: colorScheme.onTertiaryContainer,
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
