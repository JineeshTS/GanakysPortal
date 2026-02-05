import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/player_provider.dart';

class NotesPanel extends ConsumerStatefulWidget {
  const NotesPanel({super.key});

  @override
  ConsumerState<NotesPanel> createState() => _NotesPanelState();
}

class _NotesPanelState extends ConsumerState<NotesPanel> {
  final _noteController = TextEditingController();
  int? _editingNoteId;
  bool _isAdding = false;

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  String _formatTimestamp(int? seconds) {
    if (seconds == null) return '';
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final playerState = ref.watch(playerStateProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final notes = playerState.notes;
    final lecture = playerState.currentLecture;

    if (lecture == null) {
      return Center(
        child: Text(
          'Select a lecture to view notes',
          style: theme.textTheme.bodyMedium?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }

    return Column(
      children: [
        // Add note bar
        Padding(
          padding: const EdgeInsets.all(12),
          child: _isAdding || _editingNoteId != null
              ? _NoteEditor(
                  controller: _noteController,
                  isEditing: _editingNoteId != null,
                  onSave: () async {
                    final text = _noteController.text.trim();
                    if (text.isEmpty) return;
                    final notifier = ref.read(playerStateProvider.notifier);
                    if (_editingNoteId != null) {
                      await notifier.updateNote(_editingNoteId!, text);
                    } else {
                      final vc = playerState.videoController;
                      final ts = vc?.value.position.inSeconds;
                      await notifier.addNote(text, ts);
                    }
                    _noteController.clear();
                    setState(() {
                      _isAdding = false;
                      _editingNoteId = null;
                    });
                  },
                  onCancel: () {
                    _noteController.clear();
                    setState(() {
                      _isAdding = false;
                      _editingNoteId = null;
                    });
                  },
                )
              : SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      setState(() => _isAdding = true);
                    },
                    icon: const Icon(Icons.add, size: 18),
                    label: const Text('Add Note'),
                  ),
                ),
        ),
        const Divider(height: 1),
        // Notes list
        Expanded(
          child: notes.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.note_alt_outlined,
                          size: 48, color: colorScheme.outline),
                      const SizedBox(height: 12),
                      Text(
                        'No notes yet',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Add a note to remember key points',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: notes.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final note = notes[index];
                    return ListTile(
                      leading: note.timestampSeconds != null
                          ? InkWell(
                              onTap: () {
                                ref
                                    .read(playerStateProvider.notifier)
                                    .seekTo(note.timestampSeconds!);
                              },
                              borderRadius: BorderRadius.circular(4),
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: colorScheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  _formatTimestamp(note.timestampSeconds),
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: colorScheme.onPrimaryContainer,
                                    fontFamily: 'monospace',
                                  ),
                                ),
                              ),
                            )
                          : null,
                      title: Text(
                        note.content,
                        style: theme.textTheme.bodyMedium,
                      ),
                      trailing: PopupMenuButton<String>(
                        itemBuilder: (_) => [
                          const PopupMenuItem(
                              value: 'edit', child: Text('Edit')),
                          const PopupMenuItem(
                              value: 'delete', child: Text('Delete')),
                        ],
                        onSelected: (action) {
                          if (action == 'edit') {
                            _noteController.text = note.content;
                            setState(() {
                              _editingNoteId = note.id;
                              _isAdding = false;
                            });
                          } else if (action == 'delete' && note.id != null) {
                            ref
                                .read(playerStateProvider.notifier)
                                .deleteNote(note.id!);
                          }
                        },
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}

class _NoteEditor extends StatelessWidget {
  final TextEditingController controller;
  final bool isEditing;
  final VoidCallback onSave;
  final VoidCallback onCancel;

  const _NoteEditor({
    required this.controller,
    required this.isEditing,
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
          maxLines: 3,
          autofocus: true,
          decoration: InputDecoration(
            hintText: isEditing ? 'Edit note...' : 'Write a note...',
            border: const OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            TextButton(onPressed: onCancel, child: const Text('Cancel')),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: onSave,
              child: Text(isEditing ? 'Update' : 'Save'),
            ),
          ],
        ),
      ],
    );
  }
}
