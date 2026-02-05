import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/player_provider.dart';

class BookmarksPanel extends ConsumerStatefulWidget {
  const BookmarksPanel({super.key});

  @override
  ConsumerState<BookmarksPanel> createState() => _BookmarksPanelState();
}

class _BookmarksPanelState extends ConsumerState<BookmarksPanel> {
  bool _isAdding = false;
  final _labelController = TextEditingController();

  @override
  void dispose() {
    _labelController.dispose();
    super.dispose();
  }

  String _formatTimestamp(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final playerState = ref.watch(playerStateProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final bookmarks = playerState.bookmarks;

    return Column(
      children: [
        // Add bookmark bar
        Padding(
          padding: const EdgeInsets.all(12),
          child: _isAdding
              ? _BookmarkEditor(
                  controller: _labelController,
                  onSave: () async {
                    final label = _labelController.text.trim();
                    await ref.read(playerStateProvider.notifier).addBookmark(
                          label.isEmpty ? null : label,
                        );
                    _labelController.clear();
                    setState(() => _isAdding = false);
                  },
                  onCancel: () {
                    _labelController.clear();
                    setState(() => _isAdding = false);
                  },
                )
              : SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      setState(() => _isAdding = true);
                    },
                    icon: const Icon(Icons.bookmark_add_outlined, size: 18),
                    label: const Text('Add Bookmark'),
                  ),
                ),
        ),
        const Divider(height: 1),
        // Bookmarks list
        Expanded(
          child: bookmarks.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.bookmark_border,
                          size: 48, color: colorScheme.outline),
                      const SizedBox(height: 12),
                      Text(
                        'No bookmarks yet',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Bookmark important moments in your lectures',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: bookmarks.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final bookmark = bookmarks[index];
                    // Find the lecture name for this bookmark
                    String lectureName = 'Lecture';
                    for (final section in playerState.sections) {
                      for (final lecture in section.lectures) {
                        if (lecture.id == bookmark.lectureId) {
                          lectureName = lecture.title;
                          break;
                        }
                      }
                    }

                    return ListTile(
                      onTap: () {
                        // If the bookmark is for a different lecture, switch to it first
                        if (bookmark.lectureId !=
                            playerState.currentLectureId) {
                          ref
                              .read(playerStateProvider.notifier)
                              .selectLecture(bookmark.lectureId);
                          // Wait a bit for the video to initialize before seeking
                          Future.delayed(const Duration(milliseconds: 500), () {
                            ref
                                .read(playerStateProvider.notifier)
                                .seekTo(bookmark.timestampSeconds);
                          });
                        } else {
                          ref
                              .read(playerStateProvider.notifier)
                              .seekTo(bookmark.timestampSeconds);
                        }
                      },
                      leading: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: colorScheme.primaryContainer,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          _formatTimestamp(bookmark.timestampSeconds),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: colorScheme.onPrimaryContainer,
                            fontFamily: 'monospace',
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      title: Text(
                        bookmark.label ?? 'Bookmark',
                        style: theme.textTheme.bodyMedium,
                      ),
                      subtitle: Text(
                        lectureName,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      trailing: IconButton(
                        icon: Icon(Icons.delete_outline,
                            size: 20, color: colorScheme.error),
                        onPressed: () {
                          if (bookmark.id != null) {
                            ref
                                .read(playerStateProvider.notifier)
                                .deleteBookmark(bookmark.id!);
                          }
                        },
                        tooltip: 'Delete bookmark',
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}

class _BookmarkEditor extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSave;
  final VoidCallback onCancel;

  const _BookmarkEditor({
    required this.controller,
    required this.onSave,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(
            hintText: 'Bookmark label (optional)',
            border: OutlineInputBorder(),
            isDense: true,
          ),
          onSubmitted: (_) => onSave(),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            TextButton(onPressed: onCancel, child: const Text('Cancel')),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: onSave,
              child: const Text('Save Bookmark'),
            ),
          ],
        ),
      ],
    );
  }
}
