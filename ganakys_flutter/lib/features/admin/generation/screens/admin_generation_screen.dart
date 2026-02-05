import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/client_provider.dart';
import '../../../../core/providers/auth_provider.dart';

class _GenerationFilter {
  final String? status;
  final int page;

  const _GenerationFilter({this.status, this.page = 1});

  _GenerationFilter copyWith({String? status, int? page, bool clearStatus = false}) {
    return _GenerationFilter(
      status: clearStatus ? null : (status ?? this.status),
      page: page ?? this.page,
    );
  }
}

final _genFilterProvider = StateProvider.autoDispose<_GenerationFilter>(
  (ref) => const _GenerationFilter(),
);

final _genJobsProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  final filter = ref.watch(_genFilterProvider);
  return await client.generation.listJobs(
    status: filter.status,
    page: filter.page,
    pageSize: 20,
  );
});

final _genCategoriesProvider = FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminListCategories();
});

class AdminGenerationScreen extends ConsumerWidget {
  const AdminGenerationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final jobsAsync = ref.watch(_genJobsProvider);
    final filter = ref.watch(_genFilterProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Course Generation',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                onPressed: () => ref.invalidate(_genJobsProvider),
                icon: const Icon(Icons.refresh),
                tooltip: 'Refresh',
              ),
              const SizedBox(width: 8),
              FilledButton.icon(
                onPressed: () => _showGenerateWizard(context, ref),
                icon: const Icon(Icons.auto_awesome),
                label: const Text('Generate New Course'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Status filter
          Wrap(
            spacing: 8,
            children: [
              FilterChip(
                label: const Text('All'),
                selected: filter.status == null,
                onSelected: (_) {
                  ref.read(_genFilterProvider.notifier).state =
                      filter.copyWith(clearStatus: true, page: 1);
                },
              ),
              for (final status in ['pending', 'running', 'completed', 'failed'])
                FilterChip(
                  label: Text(status[0].toUpperCase() + status.substring(1)),
                  selected: filter.status == status,
                  onSelected: (selected) {
                    ref.read(_genFilterProvider.notifier).state =
                        filter.copyWith(status: selected ? status : null, clearStatus: !selected, page: 1);
                  },
                ),
            ],
          ),
          const SizedBox(height: 16),
          Expanded(
            child: jobsAsync.when(
              data: (data) {
                final jobs = (data['jobs'] as List?)?.cast<Map<String, dynamic>>() ?? [];
                final totalPages = data['totalPages'] as int? ?? 1;
                final currentPage = data['page'] as int? ?? 1;

                if (jobs.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.auto_awesome_outlined, size: 64, color: colorScheme.outline),
                        const SizedBox(height: 16),
                        Text('No generation jobs', style: theme.textTheme.titleMedium),
                        const SizedBox(height: 8),
                        const Text('Generate your first course using AI'),
                      ],
                    ),
                  );
                }

                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        itemCount: jobs.length,
                        itemBuilder: (context, index) {
                          final job = jobs[index];
                          final topic = job['topic'] as String? ?? 'Unknown';
                          final status = job['status'] as String? ?? 'unknown';
                          final progress = (job['progress'] as num?)?.toDouble() ?? 0;
                          final createdAt = job['createdAt'] as String? ?? '';
                          final difficulty = job['difficulty'] as String? ?? '';

                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: _StatusIcon(status: status),
                              title: Text(topic, maxLines: 1, overflow: TextOverflow.ellipsis),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      _StatusChip(status: status),
                                      const SizedBox(width: 8),
                                      if (difficulty.isNotEmpty) ...[
                                        Text(difficulty, style: theme.textTheme.bodySmall),
                                        const SizedBox(width: 8),
                                      ],
                                      Text(createdAt, style: theme.textTheme.bodySmall),
                                    ],
                                  ),
                                  if (status == 'running') ...[
                                    const SizedBox(height: 4),
                                    LinearProgressIndicator(
                                      value: progress / 100,
                                      backgroundColor: colorScheme.surfaceContainerHighest,
                                    ),
                                    const SizedBox(height: 2),
                                    Text('${progress.toStringAsFixed(0)}%', style: theme.textTheme.bodySmall),
                                  ],
                                ],
                              ),
                              isThreeLine: status == 'running',
                            ),
                          );
                        },
                      ),
                    ),
                    if (totalPages > 1)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            IconButton(
                              onPressed: currentPage > 1
                                  ? () {
                                      ref.read(_genFilterProvider.notifier).state =
                                          filter.copyWith(page: currentPage - 1);
                                    }
                                  : null,
                              icon: const Icon(Icons.chevron_left),
                            ),
                            Text('Page $currentPage of $totalPages'),
                            IconButton(
                              onPressed: currentPage < totalPages
                                  ? () {
                                      ref.read(_genFilterProvider.notifier).state =
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
                    Text('Failed to load jobs: $error'),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => ref.invalidate(_genJobsProvider),
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

  Future<void> _showGenerateWizard(BuildContext context, WidgetRef ref) async {
    final categoriesAsync = ref.read(_genCategoriesProvider);
    final categories = categoriesAsync.valueOrNull ?? [];

    final topicCtrl = TextEditingController();
    String difficulty = 'beginner';
    int? categoryId;
    int duration = 60;

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDlgState) => AlertDialog(
          title: const Text('Generate New Course'),
          content: SizedBox(
            width: 450,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: topicCtrl,
                  autofocus: true,
                  decoration: const InputDecoration(
                    labelText: 'Topic',
                    hintText: 'e.g., Introduction to Machine Learning',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<int>(
                  value: categoryId,
                  decoration: const InputDecoration(labelText: 'Category (optional)', border: OutlineInputBorder()),
                  items: categories
                      .map((c) => DropdownMenuItem<int>(
                            value: c['id'] as int,
                            child: Text(c['name'] as String? ?? 'Unknown'),
                          ))
                      .toList(),
                  onChanged: (v) => setDlgState(() => categoryId = v),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: difficulty,
                        decoration: const InputDecoration(labelText: 'Difficulty', border: OutlineInputBorder()),
                        items: const [
                          DropdownMenuItem(value: 'beginner', child: Text('Beginner')),
                          DropdownMenuItem(value: 'intermediate', child: Text('Intermediate')),
                          DropdownMenuItem(value: 'advanced', child: Text('Advanced')),
                        ],
                        onChanged: (v) {
                          if (v != null) setDlgState(() => difficulty = v);
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: DropdownButtonFormField<int>(
                        value: duration,
                        decoration: const InputDecoration(labelText: 'Duration (min)', border: OutlineInputBorder()),
                        items: const [
                          DropdownMenuItem(value: 30, child: Text('30 min')),
                          DropdownMenuItem(value: 60, child: Text('60 min')),
                          DropdownMenuItem(value: 120, child: Text('120 min')),
                          DropdownMenuItem(value: 180, child: Text('180 min')),
                        ],
                        onChanged: (v) {
                          if (v != null) setDlgState(() => duration = v);
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            FilledButton.icon(
              onPressed: () => Navigator.pop(ctx, true),
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Generate'),
            ),
          ],
        ),
      ),
    );

    if (result != true) {
      topicCtrl.dispose();
      return;
    }
    if (!context.mounted) return;

    final topic = topicCtrl.text.trim();
    topicCtrl.dispose();
    if (topic.isEmpty) return;

    try {
      final client = ref.read(clientProvider);
      final auth = ref.read(authProvider);
      final userId = auth.user?.id ?? 0;
      await client.generation.startGeneration(topic, categoryId, difficulty, duration, userId);
      ref.invalidate(_genJobsProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Generation started!')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to start generation: $e')),
        );
      }
    }
  }
}

class _StatusIcon extends StatelessWidget {
  final String status;

  const _StatusIcon({required this.status});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color color;
    switch (status) {
      case 'completed':
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case 'running':
        icon = Icons.play_circle;
        color = Colors.blue;
        break;
      case 'failed':
        icon = Icons.error;
        color = Colors.red;
        break;
      case 'pending':
      default:
        icon = Icons.schedule;
        color = Colors.orange;
        break;
    }
    return Icon(icon, color: color, size: 32);
  }
}

class _StatusChip extends StatelessWidget {
  final String status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    switch (status) {
      case 'completed':
        bg = Colors.green.shade50;
        fg = Colors.green.shade800;
        break;
      case 'running':
        bg = Colors.blue.shade50;
        fg = Colors.blue.shade800;
        break;
      case 'failed':
        bg = Colors.red.shade50;
        fg = Colors.red.shade800;
        break;
      case 'pending':
      default:
        bg = Colors.orange.shade50;
        fg = Colors.orange.shade800;
        break;
    }
    return Chip(
      label: Text(
        status[0].toUpperCase() + status.substring(1),
        style: TextStyle(fontSize: 11, color: fg),
      ),
      backgroundColor: bg,
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      visualDensity: VisualDensity.compact,
    );
  }
}
