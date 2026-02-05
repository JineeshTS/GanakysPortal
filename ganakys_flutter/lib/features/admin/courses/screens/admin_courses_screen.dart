import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/client_provider.dart';

class _CoursesFilter {
  final String? search;
  final String? status;
  final int? categoryId;
  final String? difficulty;
  final int page;

  const _CoursesFilter({
    this.search,
    this.status,
    this.categoryId,
    this.difficulty,
    this.page = 1,
  });

  _CoursesFilter copyWith({
    String? search,
    String? status,
    int? categoryId,
    String? difficulty,
    int? page,
    bool clearSearch = false,
    bool clearStatus = false,
    bool clearCategory = false,
    bool clearDifficulty = false,
  }) {
    return _CoursesFilter(
      search: clearSearch ? null : (search ?? this.search),
      status: clearStatus ? null : (status ?? this.status),
      categoryId: clearCategory ? null : (categoryId ?? this.categoryId),
      difficulty: clearDifficulty ? null : (difficulty ?? this.difficulty),
      page: page ?? this.page,
    );
  }
}

final _coursesFilterProvider = StateProvider.autoDispose<_CoursesFilter>(
  (ref) => const _CoursesFilter(),
);

final _coursesProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  final filter = ref.watch(_coursesFilterProvider);
  return await client.admin.adminListCourses(
    filter.search,
    filter.status,
    filter.categoryId,
    filter.difficulty,
    filter.page,
    20,
  );
});

final _categoriesProvider = FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminListCategories();
});

class AdminCoursesScreen extends ConsumerStatefulWidget {
  const AdminCoursesScreen({super.key});

  @override
  ConsumerState<AdminCoursesScreen> createState() => _AdminCoursesScreenState();
}

class _AdminCoursesScreenState extends ConsumerState<AdminCoursesScreen> {
  final _searchController = TextEditingController();
  Timer? _debounce;
  final Set<int> _selected = {};

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String value) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 400), () {
      ref.read(_coursesFilterProvider.notifier).state =
          ref.read(_coursesFilterProvider).copyWith(
                search: value.isEmpty ? null : value,
                clearSearch: value.isEmpty,
                page: 1,
              );
    });
  }

  Future<void> _createCourse() async {
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => const _CreateCourseDialog(),
    );
    if (result == null || !mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminCreateCourse(
        result['title']!,
        result['slug']!,
        result['description'],
        null,
        result['difficulty'] ?? 'beginner',
      );
      ref.invalidate(_coursesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course created successfully')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create course: $e')),
        );
      }
    }
  }

  Future<void> _deleteCourse(int courseId, String title) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Course'),
        content: Text('Are you sure you want to delete "$title"? This action cannot be undone.'),
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
      await client.admin.adminDeleteCourse(courseId);
      _selected.remove(courseId);
      ref.invalidate(_coursesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course deleted')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete: $e')),
        );
      }
    }
  }

  Future<void> _duplicateCourse(int courseId) async {
    try {
      final client = ref.read(clientProvider);
      await client.admin.adminDuplicateCourse(courseId);
      ref.invalidate(_coursesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Course duplicated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to duplicate: $e')),
        );
      }
    }
  }

  Future<void> _bulkAction(String action) async {
    if (_selected.isEmpty) return;
    final client = ref.read(clientProvider);

    try {
      for (final id in _selected) {
        switch (action) {
          case 'publish':
            await client.admin.adminUpdateCourse(id, '', null, null, 'beginner', true, false, 0);
            break;
          case 'unpublish':
            await client.admin.adminUpdateCourse(id, '', null, null, 'beginner', false, false, 0);
            break;
          case 'delete':
            await client.admin.adminDeleteCourse(id);
            break;
        }
      }
      setState(() => _selected.clear());
      ref.invalidate(_coursesProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Bulk $action completed')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Bulk action failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final coursesAsync = ref.watch(_coursesProvider);
    final filter = ref.watch(_coursesFilterProvider);
    final categoriesAsync = ref.watch(_categoriesProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Expanded(
                child: Text(
                  'Courses',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              FilledButton.icon(
                onPressed: _createCourse,
                icon: const Icon(Icons.add),
                label: const Text('Create Course'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Filters
          Wrap(
            spacing: 12,
            runSpacing: 12,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                width: 300,
                child: TextField(
                  controller: _searchController,
                  onChanged: _onSearchChanged,
                  decoration: InputDecoration(
                    hintText: 'Search courses...',
                    prefixIcon: const Icon(Icons.search),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                ),
              ),
              DropdownButton<String>(
                value: filter.status,
                hint: const Text('Status'),
                items: const [
                  DropdownMenuItem(value: 'published', child: Text('Published')),
                  DropdownMenuItem(value: 'draft', child: Text('Draft')),
                ],
                onChanged: (v) {
                  ref.read(_coursesFilterProvider.notifier).state =
                      filter.copyWith(status: v, clearStatus: v == null, page: 1);
                },
              ),
              if (filter.status != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_coursesFilterProvider.notifier).state =
                        filter.copyWith(clearStatus: true, page: 1);
                  },
                  tooltip: 'Clear status filter',
                ),
              DropdownButton<String>(
                value: filter.difficulty,
                hint: const Text('Difficulty'),
                items: const [
                  DropdownMenuItem(value: 'beginner', child: Text('Beginner')),
                  DropdownMenuItem(value: 'intermediate', child: Text('Intermediate')),
                  DropdownMenuItem(value: 'advanced', child: Text('Advanced')),
                ],
                onChanged: (v) {
                  ref.read(_coursesFilterProvider.notifier).state =
                      filter.copyWith(difficulty: v, clearDifficulty: v == null, page: 1);
                },
              ),
              if (filter.difficulty != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_coursesFilterProvider.notifier).state =
                        filter.copyWith(clearDifficulty: true, page: 1);
                  },
                  tooltip: 'Clear difficulty filter',
                ),
              categoriesAsync.when(
                data: (cats) => DropdownButton<int>(
                  value: filter.categoryId,
                  hint: const Text('Category'),
                  items: cats
                      .map((c) => DropdownMenuItem<int>(
                            value: c['id'] as int,
                            child: Text(c['name'] as String? ?? 'Unknown'),
                          ))
                      .toList(),
                  onChanged: (v) {
                    ref.read(_coursesFilterProvider.notifier).state =
                        filter.copyWith(categoryId: v, clearCategory: v == null, page: 1);
                  },
                ),
                loading: () => const SizedBox.shrink(),
                error: (_, __) => const SizedBox.shrink(),
              ),
              if (filter.categoryId != null)
                IconButton(
                  icon: const Icon(Icons.clear, size: 18),
                  onPressed: () {
                    ref.read(_coursesFilterProvider.notifier).state =
                        filter.copyWith(clearCategory: true, page: 1);
                  },
                  tooltip: 'Clear category filter',
                ),
            ],
          ),
          // Bulk actions
          if (_selected.isNotEmpty) ...[
            const SizedBox(height: 12),
            Card(
              color: colorScheme.primaryContainer,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    Text('${_selected.length} selected', style: TextStyle(color: colorScheme.onPrimaryContainer)),
                    const Spacer(),
                    TextButton(onPressed: () => _bulkAction('publish'), child: const Text('Publish')),
                    TextButton(onPressed: () => _bulkAction('unpublish'), child: const Text('Unpublish')),
                    TextButton(
                      onPressed: () => _bulkAction('delete'),
                      style: TextButton.styleFrom(foregroundColor: colorScheme.error),
                      child: const Text('Delete'),
                    ),
                    TextButton(
                      onPressed: () => setState(() => _selected.clear()),
                      child: const Text('Clear'),
                    ),
                  ],
                ),
              ),
            ),
          ],
          const SizedBox(height: 16),
          // Courses list
          Expanded(
            child: coursesAsync.when(
              data: (data) {
                final courses = (data['courses'] as List?)?.cast<Map<String, dynamic>>() ?? [];
                final totalPages = data['totalPages'] as int? ?? 1;
                final currentPage = data['page'] as int? ?? 1;

                if (courses.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.book_outlined, size: 64, color: colorScheme.outline),
                        const SizedBox(height: 16),
                        Text('No courses found', style: theme.textTheme.titleMedium),
                      ],
                    ),
                  );
                }

                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        itemCount: courses.length,
                        itemBuilder: (context, index) {
                          final course = courses[index];
                          final id = course['id'] as int;
                          final title = course['title'] as String? ?? 'Untitled';
                          final isPublished = course['isPublished'] == true;
                          final difficulty = course['difficulty'] as String? ?? '';
                          final categoryName = course['categoryName'] as String?;
                          final enrollments = course['enrollmentCount'] ?? 0;
                          final rating = course['averageRating'];
                          final isChecked = _selected.contains(id);

                          return Card(
                            margin: const EdgeInsets.only(bottom: 4),
                            child: ListTile(
                              leading: Checkbox(
                                value: isChecked,
                                onChanged: (v) {
                                  setState(() {
                                    if (v == true) {
                                      _selected.add(id);
                                    } else {
                                      _selected.remove(id);
                                    }
                                  });
                                },
                              ),
                              title: Text(title, maxLines: 1, overflow: TextOverflow.ellipsis),
                              subtitle: Row(
                                children: [
                                  Chip(
                                    label: Text(
                                      isPublished ? 'Published' : 'Draft',
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: isPublished ? Colors.green.shade800 : Colors.orange.shade800,
                                      ),
                                    ),
                                    backgroundColor: isPublished
                                        ? Colors.green.shade50
                                        : Colors.orange.shade50,
                                    padding: EdgeInsets.zero,
                                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                    visualDensity: VisualDensity.compact,
                                  ),
                                  const SizedBox(width: 8),
                                  if (categoryName != null) ...[
                                    Text(categoryName, style: theme.textTheme.bodySmall),
                                    const SizedBox(width: 8),
                                  ],
                                  Text(difficulty, style: theme.textTheme.bodySmall),
                                  const SizedBox(width: 8),
                                  Icon(Icons.people, size: 14, color: colorScheme.outline),
                                  const SizedBox(width: 2),
                                  Text('$enrollments', style: theme.textTheme.bodySmall),
                                  if (rating != null) ...[
                                    const SizedBox(width: 8),
                                    Icon(Icons.star, size: 14, color: Colors.amber.shade600),
                                    const SizedBox(width: 2),
                                    Text(
                                      (rating as num).toStringAsFixed(1),
                                      style: theme.textTheme.bodySmall,
                                    ),
                                  ],
                                ],
                              ),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  IconButton(
                                    icon: const Icon(Icons.edit, size: 20),
                                    tooltip: 'Edit',
                                    onPressed: () => context.go('/admin/courses/$id'),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.copy, size: 20),
                                    tooltip: 'Duplicate',
                                    onPressed: () => _duplicateCourse(id),
                                  ),
                                  IconButton(
                                    icon: Icon(Icons.delete, size: 20, color: colorScheme.error),
                                    tooltip: 'Delete',
                                    onPressed: () => _deleteCourse(id, title),
                                  ),
                                ],
                              ),
                              onTap: () => context.go('/admin/courses/$id'),
                            ),
                          );
                        },
                      ),
                    ),
                    // Pagination
                    if (totalPages > 1)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            IconButton(
                              onPressed: currentPage > 1
                                  ? () {
                                      ref.read(_coursesFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage - 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_left),
                            ),
                            Text('Page $currentPage of $totalPages'),
                            IconButton(
                              onPressed: currentPage < totalPages
                                  ? () {
                                      ref.read(_coursesFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage + 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_right),
                            ),
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
                    Text('Failed to load courses: $error'),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => ref.invalidate(_coursesProvider),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _CreateCourseDialog extends StatefulWidget {
  const _CreateCourseDialog();

  @override
  State<_CreateCourseDialog> createState() => _CreateCourseDialogState();
}

class _CreateCourseDialogState extends State<_CreateCourseDialog> {
  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();
  String _difficulty = 'beginner';

  String _generateSlug(String title) {
    return title
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9\s-]'), '')
        .replaceAll(RegExp(r'\s+'), '-')
        .replaceAll(RegExp(r'-+'), '-');
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Create Course'),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _titleController,
              decoration: const InputDecoration(
                labelText: 'Title',
                border: OutlineInputBorder(),
              ),
              autofocus: true,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description (optional)',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
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
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: () {
            if (_titleController.text.trim().isEmpty) return;
            Navigator.pop(context, {
              'title': _titleController.text.trim(),
              'slug': _generateSlug(_titleController.text.trim()),
              'description': _descriptionController.text.trim().isEmpty
                  ? null
                  : _descriptionController.text.trim(),
              'difficulty': _difficulty,
            });
          },
          child: const Text('Create'),
        ),
      ],
    );
  }
}
