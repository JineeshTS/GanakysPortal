import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';
import '../client_provider.dart';

// Course list state
class CourseListState {
  final List<Map<String, dynamic>> courses;
  final int totalCount;
  final int page;
  final int totalPages;
  final bool isLoading;
  final String? error;
  final String searchQuery;
  final int? categoryId;
  final String? difficulty;
  final String sortBy;

  const CourseListState({
    this.courses = const [],
    this.totalCount = 0,
    this.page = 1,
    this.totalPages = 0,
    this.isLoading = false,
    this.error,
    this.searchQuery = '',
    this.categoryId,
    this.difficulty,
    this.sortBy = 'newest',
  });

  CourseListState copyWith({
    List<Map<String, dynamic>>? courses,
    int? totalCount,
    int? page,
    int? totalPages,
    bool? isLoading,
    String? error,
    String? searchQuery,
    int? categoryId,
    String? difficulty,
    String? sortBy,
    bool clearError = false,
    bool clearCategory = false,
    bool clearDifficulty = false,
  }) {
    return CourseListState(
      courses: courses ?? this.courses,
      totalCount: totalCount ?? this.totalCount,
      page: page ?? this.page,
      totalPages: totalPages ?? this.totalPages,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      searchQuery: searchQuery ?? this.searchQuery,
      categoryId: clearCategory ? null : (categoryId ?? this.categoryId),
      difficulty: clearDifficulty ? null : (difficulty ?? this.difficulty),
      sortBy: sortBy ?? this.sortBy,
    );
  }
}

class CourseListNotifier extends StateNotifier<CourseListState> {
  final Client _client;

  CourseListNotifier(this._client) : super(const CourseListState()) {
    loadCourses();
  }

  Future<void> loadCourses({bool append = false}) async {
    if (state.isLoading) return;
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final result = await _client.course.listCourses(
        search: state.searchQuery.isEmpty ? null : state.searchQuery,
        categoryId: state.categoryId,
        difficulty: state.difficulty,
        sortBy: state.sortBy,
        page: append ? state.page + 1 : 1,
        pageSize: 20,
      );
      final courses = (result['courses'] as List?)?.cast<Map<String, dynamic>>() ?? [];
      state = state.copyWith(
        courses: append ? [...state.courses, ...courses] : courses,
        totalCount: result['totalCount'] as int? ?? 0,
        page: result['page'] as int? ?? 1,
        totalPages: result['totalPages'] as int? ?? 0,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load courses. Please try again.',
      );
    }
  }

  void setSearch(String query) {
    state = state.copyWith(searchQuery: query);
    loadCourses();
  }

  void setCategory(int? categoryId) {
    if (categoryId == null) {
      state = state.copyWith(clearCategory: true);
    } else {
      state = state.copyWith(categoryId: categoryId);
    }
    loadCourses();
  }

  void setDifficulty(String? difficulty) {
    if (difficulty == null || difficulty.isEmpty) {
      state = state.copyWith(clearDifficulty: true);
    } else {
      state = state.copyWith(difficulty: difficulty);
    }
    loadCourses();
  }

  void setSortBy(String sortBy) {
    state = state.copyWith(sortBy: sortBy);
    loadCourses();
  }

  void loadNextPage() {
    if (state.page < state.totalPages && !state.isLoading) {
      loadCourses(append: true);
    }
  }
}

final courseListProvider =
    StateNotifierProvider<CourseListNotifier, CourseListState>((ref) {
  final client = ref.watch(clientProvider);
  return CourseListNotifier(client);
});

// Categories
final categoriesProvider = FutureProvider<List<Category>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.course.getCategories();
});

// Featured courses
final featuredCoursesProvider = FutureProvider<List<Course>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.course.getFeaturedCourses();
});

// Course detail by slug
final courseDetailProvider =
    FutureProvider.family<Map<String, dynamic>?, String>((ref, slug) async {
  final client = ref.watch(clientProvider);
  return await client.course.getCourseBySlug(slug);
});

// Subscription plans (for pricing page)
final subscriptionPlansProvider =
    FutureProvider<List<SubscriptionPlan>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.payment.getPlans();
});
