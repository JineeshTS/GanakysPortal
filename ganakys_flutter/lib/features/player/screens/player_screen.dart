import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:chewie/chewie.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../../../core/providers/player_provider.dart';
import '../widgets/lecture_sidebar.dart';
import '../widgets/notes_panel.dart';
import '../widgets/bookmarks_panel.dart';

class PlayerScreen extends ConsumerStatefulWidget {
  final String courseSlug;
  final int? lectureId;

  const PlayerScreen({super.key, required this.courseSlug, this.lectureId});

  @override
  ConsumerState<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends ConsumerState<PlayerScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    // Load curriculum after first frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(playerStateProvider.notifier).loadCurriculum(
            widget.courseSlug,
            initialLectureId: widget.lectureId,
          );
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _onWillPop() async {
    await ref.read(playerStateProvider.notifier).onLeave();
    if (mounted) {
      context.go('/courses/${widget.courseSlug}');
    }
  }

  @override
  Widget build(BuildContext context) {
    final playerState = ref.watch(playerStateProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 1000;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, _) async {
        if (!didPop) {
          await _onWillPop();
        }
      },
      child: Scaffold(
        appBar: AppBar(
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: _onWillPop,
          ),
          title: Text(
            playerState.courseTitle.isNotEmpty
                ? playerState.courseTitle
                : widget.courseSlug,
            style: theme.textTheme.titleMedium,
            overflow: TextOverflow.ellipsis,
          ),
          actions: [
            if (playerState.isEnrolled && playerState.totalCount > 0)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8),
                child: Center(
                  child: Text(
                    '${playerState.completedCount}/${playerState.totalCount}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
          ],
        ),
        body: _buildBody(playerState, theme, colorScheme, isWide),
      ),
    );
  }

  Widget _buildBody(
    PlayerState playerState,
    ThemeData theme,
    ColorScheme colorScheme,
    bool isWide,
  ) {
    if (playerState.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (playerState.error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: colorScheme.error),
              const SizedBox(height: 16),
              Text(
                playerState.error!,
                style: theme.textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  ref.read(playerStateProvider.notifier).loadCurriculum(
                        widget.courseSlug,
                        initialLectureId: widget.lectureId,
                      );
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (!playerState.isEnrolled) {
      return _EnrollPrompt(
        courseSlug: widget.courseSlug,
        theme: theme,
        colorScheme: colorScheme,
      );
    }

    if (isWide) {
      return Row(
        children: [
          Expanded(
            flex: 7,
            child: Column(
              children: [
                _VideoArea(playerState: playerState, theme: theme, colorScheme: colorScheme),
                const Divider(height: 1),
                Expanded(
                  child: _DesktopBottomTabs(
                    tabController: _tabController,
                    theme: theme,
                    colorScheme: colorScheme,
                  ),
                ),
              ],
            ),
          ),
          const VerticalDivider(width: 1),
          SizedBox(
            width: 340,
            child: LectureSidebar(courseSlug: widget.courseSlug),
          ),
        ],
      );
    }

    // Mobile layout
    return Column(
      children: [
        _VideoArea(playerState: playerState, theme: theme, colorScheme: colorScheme),
        const Divider(height: 1),
        Expanded(
          child: _MobileTabSection(
            tabController: _tabController,
            courseSlug: widget.courseSlug,
            theme: theme,
            colorScheme: colorScheme,
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Video area
// ---------------------------------------------------------------------------

class _VideoArea extends ConsumerWidget {
  final PlayerState playerState;
  final ThemeData theme;
  final ColorScheme colorScheme;

  const _VideoArea({
    required this.playerState,
    required this.theme,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lecture = playerState.currentLecture;

    if (lecture == null) {
      return _placeholder('Select a lecture to begin');
    }

    // Text/article content
    if (lecture.type == 'text' || lecture.type == 'article') {
      return ConstrainedBox(
        constraints: const BoxConstraints(maxHeight: 400),
        child: Markdown(
          data: lecture.content ?? 'No content available.',
          padding: const EdgeInsets.all(16),
        ),
      );
    }

    // Video
    if (playerState.videoReady && playerState.chewieController != null) {
      return AspectRatio(
        aspectRatio:
            playerState.videoController?.value.aspectRatio ?? 16 / 9,
        child: Chewie(controller: playerState.chewieController!),
      );
    }

    // Video loading or no URL
    if (lecture.type == 'video') {
      if (lecture.videoUrl == null || lecture.videoUrl!.isEmpty) {
        return _placeholder('Video not available for this lecture');
      }
      return AspectRatio(
        aspectRatio: 16 / 9,
        child: Container(
          color: Colors.black,
          child: const Center(child: CircularProgressIndicator()),
        ),
      );
    }

    return _placeholder('Unsupported lecture type: ${lecture.type}');
  }

  Widget _placeholder(String msg) {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: Container(
        color: colorScheme.surfaceContainerHighest,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.play_circle_outline, size: 64, color: colorScheme.outline),
              const SizedBox(height: 12),
              Text(msg, style: theme.textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              )),
            ],
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Enroll prompt
// ---------------------------------------------------------------------------

class _EnrollPrompt extends ConsumerWidget {
  final String courseSlug;
  final ThemeData theme;
  final ColorScheme colorScheme;

  const _EnrollPrompt({
    required this.courseSlug,
    required this.theme,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school_outlined, size: 80, color: colorScheme.primary),
            const SizedBox(height: 24),
            Text(
              'Enroll to access course content',
              style: theme.textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'You need to be enrolled in this course to watch lectures, take notes, and track your progress.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              onPressed: () async {
                final success =
                    await ref.read(playerStateProvider.notifier).enroll();
                if (success && context.mounted) {
                  ref.read(playerStateProvider.notifier).loadCurriculum(
                        courseSlug,
                      );
                }
              },
              icon: const Icon(Icons.how_to_reg),
              label: const Text('Enroll Now'),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Desktop bottom tabs (Notes / Bookmarks under video)
// ---------------------------------------------------------------------------

class _DesktopBottomTabs extends StatelessWidget {
  final TabController tabController;
  final ThemeData theme;
  final ColorScheme colorScheme;

  const _DesktopBottomTabs({
    required this.tabController,
    required this.theme,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: tabController,
          tabs: const [
            Tab(text: 'Notes'),
            Tab(text: 'Bookmarks'),
            Tab(text: 'Overview'),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: tabController,
            children: const [
              NotesPanel(),
              BookmarksPanel(),
              _OverviewTab(),
            ],
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Mobile tabs (Lectures / Notes / Bookmarks)
// ---------------------------------------------------------------------------

class _MobileTabSection extends StatelessWidget {
  final TabController tabController;
  final String courseSlug;
  final ThemeData theme;
  final ColorScheme colorScheme;

  const _MobileTabSection({
    required this.tabController,
    required this.courseSlug,
    required this.theme,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: tabController,
          tabs: const [
            Tab(text: 'Lectures'),
            Tab(text: 'Notes'),
            Tab(text: 'Bookmarks'),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: tabController,
            children: [
              LectureSidebar(courseSlug: courseSlug),
              const NotesPanel(),
              const BookmarksPanel(),
            ],
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Overview tab
// ---------------------------------------------------------------------------

class _OverviewTab extends ConsumerWidget {
  const _OverviewTab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final playerState = ref.watch(playerStateProvider);
    final lecture = playerState.currentLecture;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    if (lecture == null) {
      return Center(
        child: Text(
          'Select a lecture',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lecture.title,
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(
                lecture.type == 'video'
                    ? Icons.videocam
                    : lecture.type == 'text'
                        ? Icons.article
                        : Icons.headphones,
                size: 16,
                color: colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Text(
                lecture.type.toUpperCase(),
                style: theme.textTheme.labelSmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(width: 16),
              Icon(Icons.timer_outlined,
                  size: 16, color: colorScheme.onSurfaceVariant),
              const SizedBox(width: 4),
              Text(
                '${lecture.durationMinutes} min',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              if (lecture.isCompleted) ...[
                const SizedBox(width: 16),
                Icon(Icons.check_circle, size: 16, color: colorScheme.primary),
                const SizedBox(width: 4),
                Text(
                  'Completed',
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: colorScheme.primary,
                  ),
                ),
              ],
            ],
          ),
          if (lecture.content != null && lecture.content!.isNotEmpty) ...[
            const SizedBox(height: 16),
            MarkdownBody(data: lecture.content!),
          ],
        ],
      ),
    );
  }
}
