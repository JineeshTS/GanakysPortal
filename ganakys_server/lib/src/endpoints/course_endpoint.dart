import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class CourseEndpoint extends Endpoint {
  @override
  bool get requireLogin => false;

  // List published courses with search and filters
  Future<Map<String, dynamic>> listCourses(
    Session session, {
    String? search,
    int? categoryId,
    String? difficulty,
    String sortBy = 'newest',
    int page = 1,
    int pageSize = 20,
  }) async {
    final offset = (page - 1) * pageSize;
    var whereClause = '"isPublished" = true';
    final params = <String, dynamic>{
      'limit': pageSize,
      'offset': offset,
    };

    if (search != null && search.isNotEmpty) {
      whereClause += ' AND (title ILIKE @search OR description ILIKE @search)';
      params['search'] = '%$search%';
    }
    if (categoryId != null) {
      whereClause += ' AND "categoryId" = @categoryId';
      params['categoryId'] = categoryId;
    }
    if (difficulty != null) {
      whereClause += ' AND difficulty = @difficulty';
      params['difficulty'] = difficulty;
    }

    String orderBy;
    switch (sortBy) {
      case 'popular':
        orderBy = '"enrollmentCount" DESC';
        break;
      case 'rating':
        orderBy = '"avgRating" DESC';
        break;
      case 'title':
        orderBy = 'title ASC';
        break;
      default:
        orderBy = '"createdAt" DESC';
    }

    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM courses WHERE $whereClause',
      parameters: QueryParameters.named(params),
    );
    final totalCount = countResult.first[0] as int;

    final results = await session.db.unsafeQuery(
      'SELECT id, title, slug, "shortDescription", "categoryId", difficulty, "durationMinutes", '
      '"thumbnailUrl", "isPublished", "isFeatured", price, "totalLectures", "totalSections", '
      '"avgRating", "reviewCount", "enrollmentCount", "createdAt" '
      'FROM courses WHERE $whereClause ORDER BY $orderBy LIMIT @limit OFFSET @offset',
      parameters: QueryParameters.named(params),
    );

    return {
      'courses': results.map((row) => <String, dynamic>{
        'id': row[0],
        'title': row[1],
        'slug': row[2],
        'shortDescription': row[3],
        'categoryId': row[4],
        'difficulty': row[5],
        'durationMinutes': row[6],
        'thumbnailUrl': row[7],
        'isPublished': row[8],
        'isFeatured': row[9],
        'price': row[10],
        'totalLectures': row[11],
        'totalSections': row[12],
        'avgRating': row[13],
        'reviewCount': row[14],
        'enrollmentCount': row[15],
        'createdAt': (row[16] as DateTime?)?.toIso8601String(),
      }).toList(),
      'totalCount': totalCount,
      'page': page,
      'pageSize': pageSize,
      'totalPages': (totalCount / pageSize).ceil(),
    };
  }

  // Get course by slug (public detail page)
  Future<Map<String, dynamic>?> getCourseBySlug(
    Session session,
    String slug,
  ) async {
    final results = await session.db.unsafeQuery(
      'SELECT * FROM courses WHERE slug = @slug AND "isPublished" = true LIMIT 1',
      parameters: QueryParameters.named({'slug': slug}),
    );

    if (results.isEmpty) return null;

    final course = await Course.db.findFirstRow(session,
      where: (t) => t.slug.equals(slug) & t.isPublished.equals(true),
    );
    if (course == null) return null;

    // Get sections with lectures
    final sections = await CourseSection.db.find(session,
      where: (t) => t.courseId.equals(course.id!),
      orderBy: (t) => t.sortOrder,
    );

    final sectionData = <Map<String, dynamic>>[];
    for (final section in sections) {
      final lectures = await Lecture.db.find(session,
        where: (t) => t.sectionId.equals(section.id!),
        orderBy: (t) => t.sortOrder,
      );
      sectionData.add({
        'id': section.id,
        'title': section.title,
        'description': section.description,
        'lectures': lectures.map((l) => <String, dynamic>{
          'id': l.id,
          'title': l.title,
          'type': l.type,
          'durationMinutes': l.durationMinutes,
          'isFreePreview': l.isFreePreview,
        }).toList(),
      });
    }

    // Get reviews
    final reviews = await Review.db.find(session,
      where: (t) => t.courseId.equals(course.id!) & t.isApproved.equals(true),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
      limit: 10,
    );

    return {
      'course': course.toJson(),
      'sections': sectionData,
      'reviews': reviews.map((r) => r.toJson()).toList(),
    };
  }

  // Get course by ID (for enrolled users)
  Future<Course?> getCourse(Session session, int courseId) async {
    return await Course.db.findById(session, courseId);
  }

  // Get categories
  Future<List<Category>> getCategories(Session session) async {
    return await Category.db.find(session,
      orderBy: (t) => t.sortOrder,
    );
  }

  // Get featured courses
  Future<List<Course>> getFeaturedCourses(Session session) async {
    return await Course.db.find(session,
      where: (t) => t.isPublished.equals(true) & t.isFeatured.equals(true),
      limit: 10,
    );
  }

  // Get course curriculum (sections + lectures) for enrolled user
  Future<Map<String, dynamic>?> getCourseCurriculum(
    Session session,
    int courseId,
    int userId,
  ) async {
    // Verify enrollment
    final enrollment = await Enrollment.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );
    if (enrollment == null) {
      return {'error': 'Not enrolled in this course'};
    }

    final course = await Course.db.findById(session, courseId);
    if (course == null) return null;

    final sections = await CourseSection.db.find(session,
      where: (t) => t.courseId.equals(courseId),
      orderBy: (t) => t.sortOrder,
    );

    final sectionData = <Map<String, dynamic>>[];
    for (final section in sections) {
      final lectures = await Lecture.db.find(session,
        where: (t) => t.sectionId.equals(section.id!),
        orderBy: (t) => t.sortOrder,
      );

      // Get progress for each lecture
      final lectureData = <Map<String, dynamic>>[];
      for (final lecture in lectures) {
        final progress = await LectureProgress.db.findFirstRow(session,
          where: (t) => t.userId.equals(userId) & t.lectureId.equals(lecture.id!),
        );
        lectureData.add({
          'id': lecture.id,
          'title': lecture.title,
          'type': lecture.type,
          'durationMinutes': lecture.durationMinutes,
          'videoUrl': lecture.videoUrl,
          'audioUrl': lecture.audioUrl,
          'content': lecture.content,
          'isFreePreview': lecture.isFreePreview,
          'isCompleted': progress?.isCompleted ?? false,
          'lastPositionSeconds': progress?.lastPositionSeconds ?? 0,
          'watchTimeSeconds': progress?.watchTimeSeconds ?? 0,
        });
      }

      sectionData.add({
        'id': section.id,
        'title': section.title,
        'description': section.description,
        'lectures': lectureData,
      });
    }

    return {
      'course': course.toJson(),
      'sections': sectionData,
      'enrollment': enrollment.toJson(),
    };
  }
}
