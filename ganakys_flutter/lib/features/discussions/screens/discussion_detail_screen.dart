import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:intl/intl.dart';

import '../../../core/client_provider.dart';
import '../../../core/providers/auth_provider.dart';

class DiscussionDetailScreen extends ConsumerStatefulWidget {
  final int discussionId;
  final Map<String, dynamic>? discussionData;

  const DiscussionDetailScreen({
    super.key,
    required this.discussionId,
    this.discussionData,
  });

  @override
  ConsumerState<DiscussionDetailScreen> createState() =>
      _DiscussionDetailScreenState();
}

class _DiscussionDetailScreenState
    extends ConsumerState<DiscussionDetailScreen> {
  List<DiscussionReply> _replies = [];
  bool _isLoading = false;
  String? _error;
  bool _isSending = false;
  bool _isResolved = false;
  int _userId = 0;
  int _authorId = 0;
  final _replyController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _isResolved =
        widget.discussionData?['isResolved'] as bool? ?? false;
    _authorId = widget.discussionData?['userId'] as int? ?? 0;
    _loadReplies();
  }

  @override
  void dispose() {
    _replyController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadReplies() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final client = ref.read(clientProvider);
      final replies =
          await client.discussion.getDiscussionReplies(widget.discussionId);
      _userId = ref.read(authProvider).user?.id ?? 0;
      setState(() {
        _replies = replies;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'Failed to load replies: $e';
      });
    }
  }

  Future<void> _sendReply() async {
    final content = _replyController.text.trim();
    if (content.isEmpty || _isSending) return;
    final userId = ref.read(authProvider).user?.id ?? 0;
    if (userId <= 0) return;

    setState(() => _isSending = true);
    try {
      final client = ref.read(clientProvider);
      final reply = await client.discussion.createReply(
        userId,
        widget.discussionId,
        content,
      );
      _replyController.clear();
      setState(() {
        _replies = [..._replies, reply];
        _isSending = false;
      });
      // Scroll to bottom
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    } catch (e) {
      setState(() => _isSending = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send reply: $e')),
        );
      }
    }
  }

  Future<void> _resolveDiscussion() async {
    if (_userId <= 0) return;
    try {
      final client = ref.read(clientProvider);
      await client.discussion.resolveDiscussion(widget.discussionId, _userId);
      setState(() => _isResolved = true);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Discussion marked as resolved')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to resolve: $e')),
        );
      }
    }
  }

  String _formatDate(DateTime? dt) {
    if (dt == null) return '';
    return DateFormat.yMMMd().add_jm().format(dt);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final title = widget.discussionData?['title'] as String? ?? 'Discussion';
    final content = widget.discussionData?['content'] as String? ?? '';
    final isAuthor = _userId > 0 && _userId == _authorId;

    return Scaffold(
      appBar: AppBar(
        title: Text(title, style: theme.textTheme.titleMedium),
        actions: [
          if (isAuthor && !_isResolved)
            TextButton.icon(
              onPressed: _resolveDiscussion,
              icon: const Icon(Icons.check_circle_outline, size: 18),
              label: const Text('Resolve'),
            ),
          if (_isResolved)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Chip(
                label: const Text('Resolved'),
                backgroundColor: Colors.green.withValues(alpha: 0.15),
                side: BorderSide.none,
                labelStyle: theme.textTheme.labelSmall?.copyWith(
                  color: Colors.green,
                ),
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _buildContent(theme, colorScheme, title, content),
          ),
          _ReplyInput(
            controller: _replyController,
            isSending: _isSending,
            onSend: _sendReply,
          ),
        ],
      ),
    );
  }

  Widget _buildContent(
    ThemeData theme,
    ColorScheme colorScheme,
    String title,
    String content,
  ) {
    if (_isLoading && _replies.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null && _replies.isEmpty) {
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
                onPressed: _loadReplies,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: 1 + _replies.length, // original post + replies
      itemBuilder: (context, index) {
        if (index == 0) {
          // Original post
          return _OriginalPost(
            title: title,
            content: content,
            authorId: _authorId,
            createdAt: _parseDate(widget.discussionData?['createdAt']),
            theme: theme,
            colorScheme: colorScheme,
          );
        }

        final reply = _replies[index - 1];
        return _ReplyCard(
          reply: reply,
          theme: theme,
          colorScheme: colorScheme,
          formatDate: _formatDate,
        );
      },
    );
  }

  DateTime? _parseDate(dynamic raw) {
    if (raw is DateTime) return raw;
    if (raw is String) return DateTime.tryParse(raw);
    return null;
  }
}

// ---------------------------------------------------------------------------
// Original post
// ---------------------------------------------------------------------------

class _OriginalPost extends StatelessWidget {
  final String title;
  final String content;
  final int authorId;
  final DateTime? createdAt;
  final ThemeData theme;
  final ColorScheme colorScheme;

  const _OriginalPost({
    required this.title,
    required this.content,
    required this.authorId,
    this.createdAt,
    required this.theme,
    required this.colorScheme,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
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
                  child: Icon(Icons.person,
                      size: 16, color: colorScheme.onPrimaryContainer),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'User #$authorId',
                        style: theme.textTheme.labelMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (createdAt != null)
                        Text(
                          DateFormat.yMMMd().add_jm().format(createdAt!),
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'OP',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: colorScheme.onPrimaryContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(content, style: theme.textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Reply card
// ---------------------------------------------------------------------------

class _ReplyCard extends StatelessWidget {
  final DiscussionReply reply;
  final ThemeData theme;
  final ColorScheme colorScheme;
  final String Function(DateTime?) formatDate;

  const _ReplyCard({
    required this.reply,
    required this.theme,
    required this.colorScheme,
    required this.formatDate,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 14,
                  backgroundColor: reply.isInstructorReply
                      ? colorScheme.tertiaryContainer
                      : colorScheme.surfaceContainerHighest,
                  child: Icon(
                    reply.isInstructorReply ? Icons.school : Icons.person,
                    size: 14,
                    color: reply.isInstructorReply
                        ? colorScheme.onTertiaryContainer
                        : colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  'User #${reply.userId}',
                  style: theme.textTheme.labelMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (reply.isInstructorReply) ...[
                  const SizedBox(width: 6),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                    decoration: BoxDecoration(
                      color: colorScheme.tertiaryContainer,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'Instructor',
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: colorScheme.onTertiaryContainer,
                      ),
                    ),
                  ),
                ],
                const Spacer(),
                Text(
                  formatDate(reply.createdAt),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(reply.content, style: theme.textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Reply input
// ---------------------------------------------------------------------------

class _ReplyInput extends StatelessWidget {
  final TextEditingController controller;
  final bool isSending;
  final VoidCallback onSend;

  const _ReplyInput({
    required this.controller,
    required this.isSending,
    required this.onSend,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        border: Border(
          top: BorderSide(color: colorScheme.outlineVariant),
        ),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                maxLines: null,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => onSend(),
                decoration: const InputDecoration(
                  hintText: 'Write a reply...',
                  border: OutlineInputBorder(),
                  isDense: true,
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: isSending ? null : onSend,
              icon: isSending
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.send, size: 20),
            ),
          ],
        ),
      ),
    );
  }
}
