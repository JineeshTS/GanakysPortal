import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:intl/intl.dart';

import '../../../core/client_provider.dart';
import '../../../core/providers/auth_provider.dart';
import 'discussion_detail_screen.dart';

class DiscussionListScreen extends ConsumerStatefulWidget {
  final int courseId;
  final int? lectureId;
  final String courseTitle;

  const DiscussionListScreen({
    super.key,
    required this.courseId,
    this.lectureId,
    this.courseTitle = 'Discussions',
  });

  @override
  ConsumerState<DiscussionListScreen> createState() =>
      _DiscussionListScreenState();
}

class _DiscussionListScreenState extends ConsumerState<DiscussionListScreen> {
  List<Map<String, dynamic>> _discussions = [];
  int _totalCount = 0;
  int _page = 1;
  bool _isLoading = false;
  String? _error;
  static const _pageSize = 20;

  @override
  void initState() {
    super.initState();
    _loadDiscussions();
  }

  Future<void> _loadDiscussions({bool append = false}) async {
    if (_isLoading) return;
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final client = ref.read(clientProvider);
      final result = await client.discussion.getDiscussions(
        widget.courseId,
        widget.lectureId,
        append ? _page + 1 : 1,
        _pageSize,
      );

      final discussions =
          (result['discussions'] as List?)?.cast<Map<String, dynamic>>() ?? [];

      setState(() {
        if (append) {
          _discussions = [..._discussions, ...discussions];
          _page = _page + 1;
        } else {
          _discussions = discussions;
          _page = 1;
        }
        _totalCount = result['totalCount'] as int? ?? 0;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Failed to load discussions: $e';
      });
    }
  }

  void _showNewDiscussionDialog() {
    final titleCtrl = TextEditingController();
    final contentCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) {
        return AlertDialog(
          title: const Text('New Discussion'),
          content: SizedBox(
            width: 400,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: titleCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Title',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: contentCtrl,
                  maxLines: 4,
                  decoration: const InputDecoration(
                    labelText: 'Content',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                final title = titleCtrl.text.trim();
                final content = contentCtrl.text.trim();
                if (title.isEmpty || content.isEmpty) return;

                final userId = ref.read(authProvider).user?.id ?? 0;
                if (userId <= 0) return;

                try {
                  final client = ref.read(clientProvider);
                  await client.discussion.createDiscussion(
                    userId,
                    widget.courseId,
                    widget.lectureId,
                    title,
                    content,
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  _loadDiscussions();
                } catch (e) {
                  if (ctx.mounted) {
                    ScaffoldMessenger.of(ctx).showSnackBar(
                      SnackBar(content: Text('Error: $e')),
                    );
                  }
                }
              },
              child: const Text('Post'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.courseTitle, style: theme.textTheme.titleMedium),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showNewDiscussionDialog,
        tooltip: 'New Discussion',
        child: const Icon(Icons.add),
      ),
      body: _buildBody(theme, colorScheme),
    );
  }

  Widget _buildBody(ThemeData theme, ColorScheme colorScheme) {
    if (_isLoading && _discussions.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null && _discussions.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: colorScheme.error),
              const SizedBox(height: 16),
              Text(_error!, style: theme.textTheme.bodyLarge,
                  textAlign: TextAlign.center),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loadDiscussions,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (_discussions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.forum_outlined, size: 64, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'No discussions yet',
              style: theme.textTheme.titleMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Start a conversation by tapping the + button',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => _loadDiscussions(),
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: _discussions.length + (_hasMore ? 1 : 0),
        separatorBuilder: (_, __) => const Divider(height: 1),
        itemBuilder: (context, index) {
          if (index == _discussions.length) {
            // Load more
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (!_isLoading) _loadDiscussions(append: true);
            });
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }

          final d = _discussions[index];
          return _DiscussionTile(
            discussion: d,
            onTap: () => _openDiscussion(d),
          );
        },
      ),
    );
  }

  bool get _hasMore => _discussions.length < _totalCount;

  void _openDiscussion(Map<String, dynamic> discussion) {
    final id = discussion['id'] as int;
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => DiscussionDetailScreen(
          discussionId: id,
          discussionData: discussion,
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Discussion tile
// ---------------------------------------------------------------------------

class _DiscussionTile extends StatelessWidget {
  final Map<String, dynamic> discussion;
  final VoidCallback onTap;

  const _DiscussionTile({required this.discussion, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final title = discussion['title'] as String? ?? 'Untitled';
    final replyCount = discussion['replyCount'] as int? ?? 0;
    final isResolved = discussion['isResolved'] as bool? ?? false;
    final isPinned = discussion['isPinned'] as bool? ?? false;
    final createdAtRaw = discussion['createdAt'];
    String dateStr = '';
    if (createdAtRaw is DateTime) {
      dateStr = DateFormat.yMMMd().format(createdAtRaw);
    } else if (createdAtRaw is String) {
      final parsed = DateTime.tryParse(createdAtRaw);
      if (parsed != null) dateStr = DateFormat.yMMMd().format(parsed);
    }

    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        backgroundColor: isResolved
            ? Colors.green.withValues(alpha: 0.15)
            : colorScheme.primaryContainer,
        child: Icon(
          isResolved ? Icons.check : Icons.forum_outlined,
          color: isResolved ? Colors.green : colorScheme.primary,
          size: 20,
        ),
      ),
      title: Row(
        children: [
          if (isPinned)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Icon(Icons.push_pin,
                  size: 14, color: colorScheme.onSurfaceVariant),
            ),
          Expanded(
            child: Text(
              title,
              style: theme.textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.w500,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
      subtitle: Row(
        children: [
          if (dateStr.isNotEmpty) ...[
            Text(dateStr, style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            )),
            const SizedBox(width: 12),
          ],
          Icon(Icons.reply, size: 14, color: colorScheme.onSurfaceVariant),
          const SizedBox(width: 2),
          Text(
            '$replyCount',
            style: theme.textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
          if (isResolved) ...[
            const SizedBox(width: 12),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
              decoration: BoxDecoration(
                color: Colors.green.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Resolved',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: Colors.green,
                ),
              ),
            ),
          ],
        ],
      ),
      trailing: const Icon(Icons.chevron_right),
    );
  }
}
