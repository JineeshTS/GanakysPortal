import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/client_provider.dart';

final _categoriesProvider = FutureProvider.autoDispose<List<Map<String, dynamic>>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminListCategories();
});

class AdminCategoriesScreen extends ConsumerWidget {
  const AdminCategoriesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final categoriesAsync = ref.watch(_categoriesProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Categories',
                  style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
                ),
              ),
              FilledButton.icon(
                onPressed: () => _showCategoryDialog(context, ref, null),
                icon: const Icon(Icons.add),
                label: const Text('Add Category'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Expanded(
            child: categoriesAsync.when(
              data: (categories) {
                if (categories.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.category_outlined, size: 64, color: colorScheme.outline),
                        const SizedBox(height: 16),
                        Text('No categories yet', style: theme.textTheme.titleMedium),
                        const SizedBox(height: 8),
                        const Text('Create your first category'),
                      ],
                    ),
                  );
                }

                return ReorderableListView.builder(
                  itemCount: categories.length,
                  onReorder: (oldIndex, newIndex) {
                    // Reorder handled via sortOrder update
                  },
                  itemBuilder: (context, index) {
                    final cat = categories[index];
                    final id = cat['id'] as int;
                    final name = cat['name'] as String? ?? 'Unnamed';
                    final slug = cat['slug'] as String? ?? '';
                    final courseCount = cat['courseCount'] ?? 0;
                    final sortOrder = cat['sortOrder'] ?? index;
                    final icon = cat['icon'] as String?;
                    final description = cat['description'] as String?;

                    return Card(
                      key: ValueKey(id),
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.drag_handle, size: 20),
                            const SizedBox(width: 8),
                            CircleAvatar(
                              radius: 20,
                              backgroundColor: colorScheme.primaryContainer,
                              child: Text(
                                icon ?? name[0].toUpperCase(),
                                style: TextStyle(color: colorScheme.onPrimaryContainer),
                              ),
                            ),
                          ],
                        ),
                        title: Text(name, style: const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Row(
                          children: [
                            Text(slug, style: theme.textTheme.bodySmall),
                            const SizedBox(width: 12),
                            Icon(Icons.book, size: 14, color: colorScheme.outline),
                            const SizedBox(width: 2),
                            Text('$courseCount courses', style: theme.textTheme.bodySmall),
                            const SizedBox(width: 12),
                            Text('Order: $sortOrder', style: theme.textTheme.bodySmall),
                            if (description != null && description.isNotEmpty) ...[
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  description,
                                  style: theme.textTheme.bodySmall?.copyWith(color: colorScheme.outline),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
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
                              onPressed: () => _showCategoryDialog(context, ref, cat),
                            ),
                            IconButton(
                              icon: Icon(Icons.delete, size: 20, color: colorScheme.error),
                              tooltip: 'Delete',
                              onPressed: () => _deleteCategory(context, ref, id, name),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.error, size: 48, color: colorScheme.error),
                    const SizedBox(height: 12),
                    Text('Failed to load categories: $error'),
                    const SizedBox(height: 12),
                    FilledButton(
                      onPressed: () => ref.invalidate(_categoriesProvider),
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

  Future<void> _showCategoryDialog(BuildContext context, WidgetRef ref, Map<String, dynamic>? existing) async {
    final isEdit = existing != null;
    final nameCtrl = TextEditingController(text: existing?['name'] as String? ?? '');
    final descCtrl = TextEditingController(text: existing?['description'] as String? ?? '');
    final iconCtrl = TextEditingController(text: existing?['icon'] as String? ?? '');
    final sortCtrl = TextEditingController(text: '${existing?['sortOrder'] ?? 0}');

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(isEdit ? 'Edit Category' : 'Create Category'),
        content: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                autofocus: true,
                decoration: const InputDecoration(labelText: 'Name', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: descCtrl,
                decoration: const InputDecoration(labelText: 'Description (optional)', border: OutlineInputBorder()),
                maxLines: 2,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: iconCtrl,
                      decoration: const InputDecoration(labelText: 'Icon (optional)', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      controller: sortCtrl,
                      decoration: const InputDecoration(labelText: 'Sort Order', border: OutlineInputBorder()),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(isEdit ? 'Save' : 'Create'),
          ),
        ],
      ),
    );

    if (result != true) {
      nameCtrl.dispose();
      descCtrl.dispose();
      iconCtrl.dispose();
      sortCtrl.dispose();
      return;
    }
    if (!context.mounted) return;

    final nameVal = nameCtrl.text.trim();
    final descVal = descCtrl.text.trim().isEmpty ? null : descCtrl.text.trim();
    final iconVal = iconCtrl.text.trim().isEmpty ? null : iconCtrl.text.trim();
    final sortVal = int.tryParse(sortCtrl.text) ?? 0;

    nameCtrl.dispose();
    descCtrl.dispose();
    iconCtrl.dispose();
    sortCtrl.dispose();

    if (nameVal.isEmpty) return;

    try {
      final client = ref.read(clientProvider);
      if (isEdit) {
        await client.admin.adminUpdateCategory(
          existing['id'] as int,
          nameVal,
          descVal,
          iconVal,
          sortVal,
        );
      } else {
        final slug = nameVal
            .toLowerCase()
            .replaceAll(RegExp(r'[^a-z0-9\s-]'), '')
            .replaceAll(RegExp(r'\s+'), '-')
            .replaceAll(RegExp(r'-+'), '-');
        await client.admin.adminCreateCategory(nameVal, slug, descVal, iconVal, sortVal);
      }
      ref.invalidate(_categoriesProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(isEdit ? 'Category updated' : 'Category created')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }

  Future<void> _deleteCategory(BuildContext context, WidgetRef ref, int id, String name) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Category'),
        content: Text('Delete "$name"? Courses in this category will be uncategorized.'),
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
    if (confirmed != true) return;
    if (!context.mounted) return;

    try {
      final client = ref.read(clientProvider);
      await client.admin.adminDeleteCategory(id);
      ref.invalidate(_categoriesProvider);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Category deleted')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    }
  }
}
