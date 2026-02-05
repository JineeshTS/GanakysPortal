import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/providers/course_provider.dart';
import '../widgets/course_card.dart';

class CourseCatalogScreen extends ConsumerStatefulWidget {
  const CourseCatalogScreen({super.key});

  @override
  ConsumerState<CourseCatalogScreen> createState() => _CourseCatalogScreenState();
}

class _CourseCatalogScreenState extends ConsumerState<CourseCatalogScreen> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(courseListProvider.notifier).loadNextPage();
    }
  }

  @override
  Widget build(BuildContext context) {
    final courseState = ref.watch(courseListProvider);
    final categories = ref.watch(categoriesProvider);
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isWide = MediaQuery.sizeOf(context).width > 800;

    return Padding(
      padding: EdgeInsets.symmetric(horizontal: isWide ? 48 : 16, vertical: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Courses',
              style: theme.textTheme.headlineMedium
                  ?.copyWith(fontWeight: FontWeight.bold)),
          if (courseState.totalCount > 0)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                '${courseState.totalCount} courses available',
                style: theme.textTheme.bodyMedium
                    ?.copyWith(color: colorScheme.onSurfaceVariant),
              ),
            ),
          const SizedBox(height: 16),
          // Search & Filters
          Wrap(
            spacing: 12,
            runSpacing: 12,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: [
              SizedBox(
                width: isWide ? 400 : double.infinity,
                child: TextField(
                  controller: _searchController,
                  onSubmitted: (v) =>
                      ref.read(courseListProvider.notifier).setSearch(v),
                  decoration: InputDecoration(
                    hintText: 'Search courses...',
                    prefixIcon: const Icon(Icons.search),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _searchController.clear();
                              ref
                                  .read(courseListProvider.notifier)
                                  .setSearch('');
                            },
                          )
                        : null,
                  ),
                ),
              ),
              // Category filter
              categories.when(
                data: (cats) => cats.isEmpty
                    ? const SizedBox.shrink()
                    : DropdownMenu<int?>(
                        label: const Text('Category'),
                        onSelected: (v) =>
                            ref.read(courseListProvider.notifier).setCategory(v),
                        dropdownMenuEntries: [
                          const DropdownMenuEntry(value: null, label: 'All'),
                          ...cats.map((c) => DropdownMenuEntry(
                                value: c.id,
                                label: c.name,
                              )),
                        ],
                      ),
                loading: () => const SizedBox(
                    width: 120,
                    child: LinearProgressIndicator()),
                error: (_, __) => const SizedBox.shrink(),
              ),
              // Difficulty filter
              DropdownMenu<String?>(
                label: const Text('Difficulty'),
                onSelected: (v) =>
                    ref.read(courseListProvider.notifier).setDifficulty(v),
                dropdownMenuEntries: const [
                  DropdownMenuEntry(value: null, label: 'All'),
                  DropdownMenuEntry(value: 'beginner', label: 'Beginner'),
                  DropdownMenuEntry(
                      value: 'intermediate', label: 'Intermediate'),
                  DropdownMenuEntry(value: 'advanced', label: 'Advanced'),
                ],
              ),
              // Sort
              DropdownMenu<String>(
                label: const Text('Sort by'),
                initialSelection: 'newest',
                onSelected: (v) {
                  if (v != null) {
                    ref.read(courseListProvider.notifier).setSortBy(v);
                  }
                },
                dropdownMenuEntries: const [
                  DropdownMenuEntry(value: 'newest', label: 'Newest'),
                  DropdownMenuEntry(value: 'popular', label: 'Most Popular'),
                  DropdownMenuEntry(value: 'rating', label: 'Highest Rated'),
                  DropdownMenuEntry(value: 'title', label: 'Title A-Z'),
                ],
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Course grid
          Expanded(
            child: _buildContent(courseState, colorScheme, theme, isWide),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(
    CourseListState courseState,
    ColorScheme colorScheme,
    ThemeData theme,
    bool isWide,
  ) {
    if (courseState.isLoading && courseState.courses.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (courseState.error != null && courseState.courses.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off, size: 64, color: colorScheme.error),
            const SizedBox(height: 16),
            Text(courseState.error!, style: theme.textTheme.titleMedium),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () =>
                  ref.read(courseListProvider.notifier).loadCourses(),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (courseState.courses.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school_outlined, size: 64, color: colorScheme.outline),
            const SizedBox(height: 16),
            Text('No courses found', style: theme.textTheme.titleMedium),
            const SizedBox(height: 8),
            Text(
              courseState.searchQuery.isNotEmpty
                  ? 'Try a different search term'
                  : 'Check back later for new courses',
              style: theme.textTheme.bodyMedium
                  ?.copyWith(color: colorScheme.onSurfaceVariant),
            ),
          ],
        ),
      );
    }

    final crossAxisCount = isWide
        ? (MediaQuery.sizeOf(context).width > 1200 ? 4 : 3)
        : (MediaQuery.sizeOf(context).width > 500 ? 2 : 1);

    return GridView.builder(
      controller: _scrollController,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: 0.75,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: courseState.courses.length +
          (courseState.page < courseState.totalPages ? 1 : 0),
      itemBuilder: (context, index) {
        if (index >= courseState.courses.length) {
          return const Center(child: CircularProgressIndicator());
        }
        final course = courseState.courses[index];
        return CourseCard(
          course: course,
          onTap: () {
            final slug = course['slug'] as String?;
            if (slug != null) {
              context.go('/courses/$slug');
            }
          },
        );
      },
    );
  }
}
