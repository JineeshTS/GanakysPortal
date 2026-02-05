import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/client_provider.dart';

final _courseDetailProvider = FutureProvider.autoDispose.family<Map<String, dynamic>?, int>((ref, courseId) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminGetCourse(courseId);
});

class AdminCourseDetailScreen extends ConsumerStatefulWidget {
  final int courseId;

  const AdminCourseDetailScreen({super.key, required this.courseId});

  @override
  ConsumerState<AdminCourseDetailScreen> createState() => _AdminCourseDetailScreenState();
}

class _AdminCourseDetailScreenState extends ConsumerState<AdminCourseDetailScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 6, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final courseAsync = ref.watch(_courseDetailProvider(widget.courseId));

    return courseAsync.when(
      data: (course) {
        if (course == null) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.error, size: 64, color: colorScheme.error),
                const SizedBox(height: 16),
                Text('Course not found', style: theme.textTheme.titleLarge),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => context.go('/admin/courses'),
                  child: const Text('Back to Courses'),
                ),
              ],
            ),
          );
        }

        return Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => context.go('/admin/courses'),
                    icon: const Icon(Icons.arrow_back),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      course['title'] as String? ?? 'Untitled',
                      style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Chip(
                    label: Text(
                      course['isPublished'] == true ? 'Published' : 'Draft',
                      style: TextStyle(
                        color: course['isPublished'] == true ? Colors.green.shade800 : Colors.orange.shade800,
                        fontSize: 12,
                      ),
                    ),
                    backgroundColor: course['isPublished'] == true
                        ? Colors.green.shade50
                        : Colors.orange.shade50,
                  ),
                ],
              ),
            ),
            TabBar(
              controller: _tabController,
              isScrollable: true,
              tabs: const [
                Tab(text: 'Overview'),
                Tab(text: 'Content'),
                Tab(text: 'Quizzes'),
                Tab(text: 'Media'),
                Tab(text: 'Enrollments'),
                Tab(text: 'Analytics'),
              ],
            ),
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _OverviewTab(course: course, courseId: widget.courseId),
                  _ContentTab(course: course, courseId: widget.courseId),
                  _PlaceholderTab(icon: Icons.quiz, label: 'Quizzes', description: 'Quiz management coming soon'),
                  _PlaceholderTab(icon: Icons.image, label: 'Media', description: 'Media management coming soon'),
                  _PlaceholderTab(icon: Icons.people, label: 'Enrollments', description: 'Enrollment management coming soon'),
                  _PlaceholderTab(icon: Icons.analytics, label: 'Analytics', description: 'Course analytics coming soon'),
                ],
              ),
            ),
          ],
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error, size: 48, color: colorScheme.error),
            const SizedBox(height: 12),
            Text('Failed to load course: $error'),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () => ref.invalidate(_courseDetailProvider(widget.courseId)),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _OverviewTab extends ConsumerStatefulWidget {
  final Map<String, dynamic> course;
  final int courseId;

  const _OverviewTab({required this.course, required this.courseId});

  @override
  ConsumerState<_OverviewTab> createState() => _OverviewTabState();
}

class _OverviewTabState extends ConsumerState<_OverviewTab> {
  late TextEditingController _titleController;
  late TextEditingController _descriptionController;
  late TextEditingController _priceController;
  late String _difficulty;
  late bool _isPublished;
  late bool _isFeatured;
  int? _categoryId;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _titleController = TextEditingController(text: widget.course['title'] as String? ?? '');
    _descriptionController = TextEditingController(text: widget.course['description'] as String? ?? '');
    _priceController = TextEditingController(text: '${widget.course['price'] ?? 0}');
    _difficulty = widget.course['difficulty'] as String? ?? 'beginner';
    _isPublished = widget.course['isPublished'] == true;
    _isFeatured = widget.course['isFeatured'] == true;
    _categoryId = widget.course['categoryId'] as int?;
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    _priceController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateCourse(
        widget.courseId,
        _titleController.text.trim(),
        _descriptionController.text.trim().isEmpty ? null : _descriptionController.text.trim(),
        _categoryId,
        _difficulty,
        _isPublished,
        _isFeatured,
        double.tryParse(_priceController.text) ?? 0,
      );
      ref.invalidate(_courseDetailProvider(widget.courseId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course updated successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Course Metadata', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(
              labelText: 'Title',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _descriptionController,
            decoration: const InputDecoration(
              labelText: 'Description',
              border: OutlineInputBorder(),
            ),
            maxLines: 5,
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _difficulty,
                  decoration: const InputDecoration(
                    labelText: 'Difficulty',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'beginner', child: Text('Beginner')),
                    DropdownMenuItem(value: 'intermediate', child: Text('Intermediate')),
                    DropdownMenuItem(value: 'advanced', child: Text('Advanced')),
                  ],
                  onChanged: (v) {
                    if (v != null) setState(() => _difficulty = v);
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextField(
                  controller: _priceController,
                  decoration: const InputDecoration(
                    labelText: 'Price',
                    border: OutlineInputBorder(),
                    prefixText: '\$ ',
                  ),
                  keyboardType: TextInputType.number,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              SwitchListTile(
                title: const Text('Published'),
                value: _isPublished,
                onChanged: (v) => setState(() => _isPublished = v),
                contentPadding: EdgeInsets.zero,
              ),
              const SizedBox(width: 24),
              SwitchListTile(
                title: const Text('Featured'),
                value: _isFeatured,
                onChanged: (v) => setState(() => _isFeatured = v),
                contentPadding: EdgeInsets.zero,
              ),
            ].map((e) => Expanded(child: e)).toList(),
          ),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Save Changes'),
          ),
          const SizedBox(height: 32),
          // Course stats summary
          Text('Statistics', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 24,
            runSpacing: 8,
            children: [
              _StatChip(label: 'Enrollments', value: '${widget.course['enrollmentCount'] ?? 0}'),
              _StatChip(label: 'Sections', value: '${(widget.course['sections'] as List?)?.length ?? 0}'),
              _StatChip(label: 'Rating', value: '${widget.course['averageRating'] ?? 'N/A'}'),
              _StatChip(label: 'Reviews', value: '${widget.course['reviewCount'] ?? 0}'),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;

  const _StatChip({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _ContentTab extends ConsumerStatefulWidget {
  final Map<String, dynamic> course;
  final int courseId;

  const _ContentTab({required this.course, required this.courseId});

  @override
  ConsumerState<_ContentTab> createState() => _ContentTabState();
}

class _ContentTabState extends ConsumerState<_ContentTab> {
  List<Map<String, dynamic>> _sections = [];

  @override
  void initState() {
    super.initState();
    _sections = List<Map<String, dynamic>>.from(
      (widget.course['sections'] as List?)?.cast<Map<String, dynamic>>() ?? [],
    );
  }

  Future<void> _addSection() async {
    final titleCtrl = TextEditingController();
    final title = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Section'),
        content: TextField(
          controller: titleCtrl,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Section Title', border: OutlineInputBorder()),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, titleCtrl.text.trim()),
            child: const Text('Add'),
          ),
        ],
      ),
    );
    titleCtrl.dispose();
    if (title == null || title.isEmpty || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminCreateSection(widget.courseId, title, _sections.length);
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _deleteSection(int sectionId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Section'),
        content: const Text('Delete this section and all its lectures?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(backgroundColor: Theme.of(ctx).colorScheme.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminDeleteSection(sectionId);
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _editSection(int sectionId, String currentTitle, int sortOrder) async {
    final titleCtrl = TextEditingController(text: currentTitle);
    final newTitle = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Section'),
        content: TextField(
          controller: titleCtrl,
          autofocus: true,
          decoration: const InputDecoration(labelText: 'Section Title', border: OutlineInputBorder()),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, titleCtrl.text.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    titleCtrl.dispose();
    if (newTitle == null || newTitle.isEmpty || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateSection(sectionId, newTitle, null, sortOrder);
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _addLecture(int sectionId, int lectureCount) async {
    final titleCtrl = TextEditingController();
    String type = 'video';

    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlgState) => AlertDialog(
          title: const Text('Add Lecture'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                autofocus: true,
                decoration: const InputDecoration(labelText: 'Lecture Title', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: type,
                decoration: const InputDecoration(labelText: 'Type', border: OutlineInputBorder()),
                items: const [
                  DropdownMenuItem(value: 'video', child: Text('Video')),
                  DropdownMenuItem(value: 'text', child: Text('Text')),
                  DropdownMenuItem(value: 'quiz', child: Text('Quiz')),
                ],
                onChanged: (v) {
                  if (v != null) setDlgState(() => type = v);
                },
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, {'title': titleCtrl.text.trim(), 'type': type}),
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
    titleCtrl.dispose();
    if (result == null || result['title']!.isEmpty || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminCreateLecture(sectionId, widget.courseId, result['title']!, result['type']!, lectureCount);
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _deleteLecture(int lectureId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Lecture'),
        content: const Text('Delete this lecture?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(backgroundColor: Theme.of(ctx).colorScheme.error),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminDeleteLecture(lectureId);
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _editLecture(int lectureId, String currentTitle, bool isFreePreview) async {
    final titleCtrl = TextEditingController(text: currentTitle);
    bool freePreview = isFreePreview;

    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlgState) => AlertDialog(
          title: const Text('Edit Lecture'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleCtrl,
                autofocus: true,
                decoration: const InputDecoration(labelText: 'Lecture Title', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              SwitchListTile(
                title: const Text('Free Preview'),
                value: freePreview,
                onChanged: (v) => setDlgState(() => freePreview = v),
                contentPadding: EdgeInsets.zero,
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, {'title': titleCtrl.text.trim(), 'freePreview': freePreview}),
              child: const Text('Save'),
            ),
          ],
        ),
      ),
    );
    titleCtrl.dispose();
    if (result == null || result['title'].toString().isEmpty || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateLecture(
        lectureId,
        result['title'] as String,
        null,
        null,
        result['freePreview'] as bool,
      );
      ref.invalidate(_courseDetailProvider(widget.courseId));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));
      }
    }
  }

  Future<void> _reorderSections() async {
    final orderList = _sections.asMap().entries.map((e) => {'id': e.value['id'], 'sortOrder': e.key}).toList();
    try {
      final client = ref.read(clientProvider);
      await client.admin.adminReorderSections(widget.courseId, jsonEncode(orderList));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Reorder failed: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    // Re-read sections from latest course data
    final courseAsync = ref.watch(_courseDetailProvider(widget.courseId));
    final sections = courseAsync.when(
      data: (c) => List<Map<String, dynamic>>.from(
        (c?['sections'] as List?)?.cast<Map<String, dynamic>>() ?? [],
      ),
      loading: () => _sections,
      error: (_, __) => _sections,
    );

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
          child: Row(
            children: [
              Text('Course Content', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
              const Spacer(),
              FilledButton.tonalIcon(
                onPressed: _addSection,
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Add Section'),
              ),
            ],
          ),
        ),
        Expanded(
          child: sections.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.playlist_add, size: 64, color: colorScheme.outline),
                      const SizedBox(height: 16),
                      Text('No sections yet', style: theme.textTheme.titleMedium),
                      const SizedBox(height: 8),
                      const Text('Add your first section to get started'),
                    ],
                  ),
                )
              : ReorderableListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
                  itemCount: sections.length,
                  onReorder: (oldIndex, newIndex) {
                    setState(() {
                      if (newIndex > oldIndex) newIndex--;
                      final item = _sections.removeAt(oldIndex);
                      _sections.insert(newIndex, item);
                    });
                    _reorderSections();
                  },
                  itemBuilder: (context, index) {
                    final section = sections[index];
                    final sectionId = section['id'] as int;
                    final sectionTitle = section['title'] as String? ?? 'Untitled Section';
                    final lectures = List<Map<String, dynamic>>.from(
                      (section['lectures'] as List?)?.cast<Map<String, dynamic>>() ?? [],
                    );

                    return Card(
                      key: ValueKey(sectionId),
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ExpansionTile(
                        leading: const Icon(Icons.drag_handle),
                        title: Text(sectionTitle, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text('${lectures.length} lecture${lectures.length == 1 ? '' : 's'}'),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.edit, size: 18),
                              onPressed: () => _editSection(sectionId, sectionTitle, section['sortOrder'] as int? ?? index),
                            ),
                            IconButton(
                              icon: Icon(Icons.delete, size: 18, color: colorScheme.error),
                              onPressed: () => _deleteSection(sectionId),
                            ),
                            IconButton(
                              icon: const Icon(Icons.add, size: 18),
                              tooltip: 'Add Lecture',
                              onPressed: () => _addLecture(sectionId, lectures.length),
                            ),
                          ],
                        ),
                        children: [
                          ...lectures.asMap().entries.map((entry) {
                            final lecture = entry.value;
                            final lectureId = lecture['id'] as int;
                            final lectureTitle = lecture['title'] as String? ?? 'Untitled';
                            final lectureType = lecture['type'] as String? ?? 'video';
                            final isFreePreview = lecture['isFreePreview'] == true;

                            return ListTile(
                              contentPadding: const EdgeInsets.only(left: 56, right: 16),
                              leading: Icon(
                                lectureType == 'video'
                                    ? Icons.play_circle_outline
                                    : lectureType == 'quiz'
                                        ? Icons.quiz
                                        : Icons.article,
                                size: 20,
                              ),
                              title: Text(lectureTitle, style: const TextStyle(fontSize: 14)),
                              subtitle: Row(
                                children: [
                                  Text(lectureType, style: theme.textTheme.bodySmall),
                                  if (isFreePreview) ...[
                                    const SizedBox(width: 8),
                                    Chip(
                                      label: const Text('Free', style: TextStyle(fontSize: 10)),
                                      padding: EdgeInsets.zero,
                                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                      visualDensity: VisualDensity.compact,
                                      backgroundColor: Colors.green.shade50,
                                    ),
                                  ],
                                ],
                              ),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.edit, size: 16),
                                    onPressed: () => _editLecture(lectureId, lectureTitle, isFreePreview),
                                  ),
                                  IconButton(
                                    icon: Icon(Icons.delete, size: 16, color: colorScheme.error),
                                    onPressed: () => _deleteLecture(lectureId),
                                  ),
                                ],
                              ),
                            );
                          }),
                          if (lectures.isEmpty)
                            const Padding(
                              padding: EdgeInsets.all(16),
                              child: Text('No lectures in this section'),
                            ),
                        ],
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}

class _PlaceholderTab extends StatelessWidget {
  final IconData icon;
  final String label;
  final String description;

  const _PlaceholderTab({
    required this.icon,
    required this.label,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 64, color: colorScheme.outline),
          const SizedBox(height: 16),
          Text(label, style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 8),
          Text(description, style: TextStyle(color: colorScheme.onSurfaceVariant)),
        ],
      ),
    );
  }
}
