import 'dart:convert';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class AdminEndpoint extends Endpoint {
  @override
  bool get requireLogin => false;

  // ---------------------------------------------------------------------------
  // Helper: write an audit log entry
  // ---------------------------------------------------------------------------
  Future<void> _audit(
    Session session, {
    int? userId,
    required String action,
    required String entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
  }) async {
    await AuditLog.db.insertRow(
      session,
      AuditLog(
        userId: userId,
        action: action,
        entityType: entityType,
        entityId: entityId,
        oldValue: oldValue,
        newValue: newValue,
        createdAt: DateTime.now(),
      ),
    );
  }

  // ===========================================================================
  // DASHBOARD
  // ===========================================================================

  /// Returns aggregate dashboard statistics for the admin panel.
  Future<Map<String, dynamic>> getDashboardStats(Session session) async {
    final now = DateTime.now();
    final todayStart = DateTime(now.year, now.month, now.day);
    final weekStart = todayStart.subtract(Duration(days: now.weekday - 1));

    // Total users
    final usersResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM users',
    );
    final totalUsers = usersResult.first[0] as int;

    // Active subscriptions
    final activeSubs = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM subscriptions WHERE status = \'active\' AND "currentPeriodEnd" > NOW()',
    );
    final activeSubscriptions = activeSubs.first[0] as int;

    // Total revenue (completed payments)
    final revenueResult = await session.db.unsafeQuery(
      'SELECT COALESCE(SUM(amount), 0) FROM payments WHERE status = \'completed\'',
    );
    final totalRevenue = (revenueResult.first[0] as num?)?.toDouble() ?? 0.0;

    // Courses: published and draft counts
    final courseStats = await session.db.unsafeQuery(
      'SELECT '
      'COUNT(*) AS total, '
      'COUNT(*) FILTER (WHERE "isPublished" = true) AS published, '
      'COUNT(*) FILTER (WHERE "isPublished" = false) AS draft '
      'FROM courses',
    );
    final totalCourses = courseStats.first[0] as int;
    final publishedCourses = courseStats.first[1] as int;
    final draftCourses = courseStats.first[2] as int;

    // Enrollments today
    final enrollToday = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM enrollments WHERE "enrolledAt" >= @start',
      parameters: QueryParameters.named({'start': todayStart.toIso8601String()}),
    );
    final enrollmentsToday = enrollToday.first[0] as int;

    // Enrollments this week
    final enrollWeek = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM enrollments WHERE "enrolledAt" >= @start',
      parameters: QueryParameters.named({'start': weekStart.toIso8601String()}),
    );
    final enrollmentsThisWeek = enrollWeek.first[0] as int;

    // Completion rate
    final completionResult = await session.db.unsafeQuery(
      'SELECT '
      'COUNT(*) AS total, '
      'COUNT(*) FILTER (WHERE status = \'completed\') AS completed '
      'FROM enrollments',
    );
    final totalEnrollments = completionResult.first[0] as int;
    final completedEnrollments = completionResult.first[1] as int;
    final completionRate = totalEnrollments > 0
        ? (completedEnrollments / totalEnrollments * 100).roundToDouble()
        : 0.0;

    // Average rating
    final avgRatingResult = await session.db.unsafeQuery(
      'SELECT COALESCE(AVG(rating), 0) FROM reviews WHERE "isApproved" = true',
    );
    final avgRating = (avgRatingResult.first[0] as num?)?.toDouble() ?? 0.0;

    return {
      'totalUsers': totalUsers,
      'activeSubscriptions': activeSubscriptions,
      'totalRevenue': totalRevenue,
      'totalCourses': totalCourses,
      'publishedCourses': publishedCourses,
      'draftCourses': draftCourses,
      'enrollmentsToday': enrollmentsToday,
      'enrollmentsThisWeek': enrollmentsThisWeek,
      'completionRate': completionRate,
      'avgRating': double.parse(avgRating.toStringAsFixed(2)),
    };
  }

  // ===========================================================================
  // COURSE MANAGEMENT
  // ===========================================================================

  /// List courses with search, status, category, difficulty filters and paging.
  Future<Map<String, dynamic>> adminListCourses(
    Session session,
    String? search,
    String? status,
    int? categoryId,
    String? difficulty,
    int page,
    int pageSize,
  ) async {
    final offset = (page - 1) * pageSize;
    var whereClause = 'TRUE';
    final params = <String, dynamic>{
      'limit': pageSize,
      'offset': offset,
    };

    if (search != null && search.isNotEmpty) {
      whereClause += ' AND (title ILIKE @search OR description ILIKE @search)';
      params['search'] = '%$search%';
    }
    if (status != null) {
      if (status == 'published') {
        whereClause += ' AND "isPublished" = true';
      } else if (status == 'draft') {
        whereClause += ' AND "isPublished" = false';
      }
    }
    if (categoryId != null) {
      whereClause += ' AND "categoryId" = @categoryId';
      params['categoryId'] = categoryId;
    }
    if (difficulty != null && difficulty.isNotEmpty) {
      whereClause += ' AND difficulty = @difficulty';
      params['difficulty'] = difficulty;
    }

    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM courses WHERE $whereClause',
      parameters: QueryParameters.named(params),
    );
    final totalCount = countResult.first[0] as int;

    final results = await session.db.unsafeQuery(
      'SELECT id, title, slug, "categoryId", difficulty, "isPublished", "isFeatured", '
      'price, "enrollmentCount", "avgRating", "reviewCount", "totalLectures", '
      '"totalSections", "createdAt", "updatedAt" '
      'FROM courses WHERE $whereClause '
      'ORDER BY "createdAt" DESC LIMIT @limit OFFSET @offset',
      parameters: QueryParameters.named(params),
    );

    return {
      'courses': results.map((row) => <String, dynamic>{
        'id': row[0],
        'title': row[1],
        'slug': row[2],
        'categoryId': row[3],
        'difficulty': row[4],
        'isPublished': row[5],
        'isFeatured': row[6],
        'price': row[7],
        'enrollmentCount': row[8],
        'avgRating': row[9],
        'reviewCount': row[10],
        'totalLectures': row[11],
        'totalSections': row[12],
        'createdAt': (row[13] as DateTime?)?.toIso8601String(),
        'updatedAt': (row[14] as DateTime?)?.toIso8601String(),
      }).toList(),
      'totalCount': totalCount,
      'page': page,
      'pageSize': pageSize,
      'totalPages': (totalCount / pageSize).ceil(),
    };
  }

  /// Get full course detail including sections, lectures, and stats.
  Future<Map<String, dynamic>?> adminGetCourse(
    Session session,
    int courseId,
  ) async {
    final course = await Course.db.findById(session, courseId);
    if (course == null) return null;

    // Sections with lectures
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
      sectionData.add({
        'id': section.id,
        'title': section.title,
        'description': section.description,
        'sortOrder': section.sortOrder,
        'lectures': lectures.map((l) => l.toJson()).toList(),
      });
    }

    // Enrollment stats
    final enrollStats = await session.db.unsafeQuery(
      'SELECT COUNT(*) AS total, '
      'COUNT(*) FILTER (WHERE status = \'completed\') AS completed, '
      'COUNT(*) FILTER (WHERE status = \'in_progress\') AS in_progress '
      'FROM enrollments WHERE "courseId" = @courseId',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    // Revenue for this course
    final revenueResult = await session.db.unsafeQuery(
      'SELECT COALESCE(SUM(amount), 0) FROM payments WHERE "courseId" = @courseId AND status = \'completed\'',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    // Reviews summary
    final reviewStats = await session.db.unsafeQuery(
      'SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM reviews WHERE "courseId" = @courseId',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    return {
      'course': course.toJson(),
      'sections': sectionData,
      'stats': {
        'totalEnrollments': enrollStats.first[0],
        'completedEnrollments': enrollStats.first[1],
        'inProgressEnrollments': enrollStats.first[2],
        'totalRevenue': (revenueResult.first[0] as num?)?.toDouble() ?? 0.0,
        'totalReviews': reviewStats.first[0],
        'avgRating': (reviewStats.first[1] as num?)?.toDouble() ?? 0.0,
      },
    };
  }

  /// Create a new course.
  Future<Map<String, dynamic>> adminCreateCourse(
    Session session,
    String title,
    String slug,
    String? description,
    int? categoryId,
    String difficulty,
  ) async {
    final now = DateTime.now();
    final course = Course(
      title: title,
      slug: slug,
      description: description,
      categoryId: categoryId,
      difficulty: difficulty,
      createdAt: now,
      updatedAt: now,
    );

    final inserted = await Course.db.insertRow(session, course);

    await _audit(session,
      action: 'create',
      entityType: 'course',
      entityId: inserted.id.toString(),
      newValue: jsonEncode({'title': title, 'slug': slug}),
    );

    return {
      'success': true,
      'courseId': inserted.id,
      'course': inserted.toJson(),
    };
  }

  /// Update an existing course.
  Future<Map<String, dynamic>> adminUpdateCourse(
    Session session,
    int courseId,
    String title,
    String? description,
    int? categoryId,
    String difficulty,
    bool isPublished,
    bool isFeatured,
    double price,
  ) async {
    final course = await Course.db.findById(session, courseId);
    if (course == null) {
      return {'success': false, 'error': 'Course not found'};
    }

    final oldJson = jsonEncode({
      'title': course.title,
      'isPublished': course.isPublished,
      'price': course.price,
    });

    final updated = await Course.db.updateRow(
      session,
      course.copyWith(
        title: title,
        description: description,
        categoryId: categoryId,
        difficulty: difficulty,
        isPublished: isPublished,
        isFeatured: isFeatured,
        price: price,
        updatedAt: DateTime.now(),
      ),
    );

    await _audit(session,
      action: 'update',
      entityType: 'course',
      entityId: courseId.toString(),
      oldValue: oldJson,
      newValue: jsonEncode({
        'title': title,
        'isPublished': isPublished,
        'price': price,
      }),
    );

    return {
      'success': true,
      'course': updated.toJson(),
    };
  }

  /// Delete a course and all related data (sections, lectures, enrollments, reviews).
  Future<Map<String, dynamic>> adminDeleteCourse(
    Session session,
    int courseId,
  ) async {
    final course = await Course.db.findById(session, courseId);
    if (course == null) {
      return {'success': false, 'error': 'Course not found'};
    }

    // Delete in dependency order
    await session.db.unsafeQuery(
      'DELETE FROM lecture_progress WHERE "courseId" = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );
    await session.db.unsafeQuery(
      'DELETE FROM lectures WHERE "courseId" = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );
    await session.db.unsafeQuery(
      'DELETE FROM course_sections WHERE "courseId" = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );
    await session.db.unsafeQuery(
      'DELETE FROM enrollments WHERE "courseId" = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );
    await session.db.unsafeQuery(
      'DELETE FROM reviews WHERE "courseId" = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );
    await session.db.unsafeQuery(
      'DELETE FROM courses WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    await _audit(session,
      action: 'delete',
      entityType: 'course',
      entityId: courseId.toString(),
      oldValue: jsonEncode({'title': course.title}),
    );

    return {'success': true};
  }

  /// Duplicate a course (and its sections/lectures) as a new draft.
  Future<Map<String, dynamic>> adminDuplicateCourse(
    Session session,
    int courseId,
  ) async {
    final original = await Course.db.findById(session, courseId);
    if (original == null) {
      return {'success': false, 'error': 'Course not found'};
    }

    final now = DateTime.now();
    final newSlug = '${original.slug}-copy-${now.millisecondsSinceEpoch}';

    final newCourse = await Course.db.insertRow(
      session,
      Course(
        title: '${original.title} (Copy)',
        slug: newSlug,
        description: original.description,
        shortDescription: original.shortDescription,
        categoryId: original.categoryId,
        difficulty: original.difficulty,
        thumbnailUrl: original.thumbnailUrl,
        promoVideoUrl: original.promoVideoUrl,
        isPublished: false,
        isFeatured: false,
        price: original.price,
        language: original.language,
        createdAt: now,
        updatedAt: now,
      ),
    );

    // Duplicate sections and lectures
    final sections = await CourseSection.db.find(session,
      where: (t) => t.courseId.equals(courseId),
      orderBy: (t) => t.sortOrder,
    );

    for (final section in sections) {
      final newSection = await CourseSection.db.insertRow(
        session,
        CourseSection(
          courseId: newCourse.id!,
          title: section.title,
          description: section.description,
          sortOrder: section.sortOrder,
        ),
      );

      final lectures = await Lecture.db.find(session,
        where: (t) => t.sectionId.equals(section.id!),
        orderBy: (t) => t.sortOrder,
      );

      for (final lecture in lectures) {
        await Lecture.db.insertRow(
          session,
          Lecture(
            sectionId: newSection.id!,
            courseId: newCourse.id!,
            title: lecture.title,
            type: lecture.type,
            durationMinutes: lecture.durationMinutes,
            videoUrl: lecture.videoUrl,
            audioUrl: lecture.audioUrl,
            content: lecture.content,
            scriptJson: lecture.scriptJson,
            slidesJson: lecture.slidesJson,
            sortOrder: lecture.sortOrder,
            isFreePreview: lecture.isFreePreview,
          ),
        );
      }
    }

    // Update totals on the new course
    final sectionCount = await CourseSection.db.count(session,
      where: (t) => t.courseId.equals(newCourse.id!),
    );
    final lectureCount = await Lecture.db.count(session,
      where: (t) => t.courseId.equals(newCourse.id!),
    );
    await Course.db.updateRow(
      session,
      newCourse.copyWith(
        totalSections: sectionCount,
        totalLectures: lectureCount,
      ),
    );

    await _audit(session,
      action: 'duplicate',
      entityType: 'course',
      entityId: newCourse.id.toString(),
      oldValue: jsonEncode({'originalId': courseId}),
      newValue: jsonEncode({'title': newCourse.title}),
    );

    return {
      'success': true,
      'courseId': newCourse.id,
      'slug': newSlug,
    };
  }

  // ===========================================================================
  // SECTION MANAGEMENT
  // ===========================================================================

  /// Add a new section to a course.
  Future<Map<String, dynamic>> adminCreateSection(
    Session session,
    int courseId,
    String title,
    int sortOrder,
  ) async {
    final section = await CourseSection.db.insertRow(
      session,
      CourseSection(
        courseId: courseId,
        title: title,
        sortOrder: sortOrder,
      ),
    );

    // Update course totalSections
    await session.db.unsafeQuery(
      'UPDATE courses SET "totalSections" = (SELECT COUNT(*) FROM course_sections WHERE "courseId" = @id), '
      '"updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    await _audit(session,
      action: 'create',
      entityType: 'section',
      entityId: section.id.toString(),
      newValue: jsonEncode({'courseId': courseId, 'title': title}),
    );

    return {
      'success': true,
      'section': section.toJson(),
    };
  }

  /// Update an existing section.
  Future<Map<String, dynamic>> adminUpdateSection(
    Session session,
    int sectionId,
    String title,
    String? description,
    int sortOrder,
  ) async {
    final section = await CourseSection.db.findById(session, sectionId);
    if (section == null) {
      return {'success': false, 'error': 'Section not found'};
    }

    final updated = await CourseSection.db.updateRow(
      session,
      section.copyWith(
        title: title,
        description: description,
        sortOrder: sortOrder,
      ),
    );

    await _audit(session,
      action: 'update',
      entityType: 'section',
      entityId: sectionId.toString(),
    );

    return {
      'success': true,
      'section': updated.toJson(),
    };
  }

  /// Delete a section and its lectures.
  Future<Map<String, dynamic>> adminDeleteSection(
    Session session,
    int sectionId,
  ) async {
    final section = await CourseSection.db.findById(session, sectionId);
    if (section == null) {
      return {'success': false, 'error': 'Section not found'};
    }

    final courseId = section.courseId;

    // Delete lectures in this section
    await session.db.unsafeQuery(
      'DELETE FROM lectures WHERE "sectionId" = @sectionId',
      parameters: QueryParameters.named({'sectionId': sectionId}),
    );

    // Delete the section
    await CourseSection.db.deleteRow(session, section);

    // Update course counts
    await session.db.unsafeQuery(
      'UPDATE courses SET '
      '"totalSections" = (SELECT COUNT(*) FROM course_sections WHERE "courseId" = @id), '
      '"totalLectures" = (SELECT COUNT(*) FROM lectures WHERE "courseId" = @id), '
      '"updatedAt" = NOW() '
      'WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    await _audit(session,
      action: 'delete',
      entityType: 'section',
      entityId: sectionId.toString(),
      oldValue: jsonEncode({'courseId': courseId, 'title': section.title}),
    );

    return {'success': true};
  }

  // ===========================================================================
  // LECTURE MANAGEMENT
  // ===========================================================================

  /// Add a new lecture.
  Future<Map<String, dynamic>> adminCreateLecture(
    Session session,
    int sectionId,
    int courseId,
    String title,
    String type,
    int sortOrder,
  ) async {
    final lecture = await Lecture.db.insertRow(
      session,
      Lecture(
        sectionId: sectionId,
        courseId: courseId,
        title: title,
        type: type,
        sortOrder: sortOrder,
      ),
    );

    // Update course totalLectures
    await session.db.unsafeQuery(
      'UPDATE courses SET "totalLectures" = (SELECT COUNT(*) FROM lectures WHERE "courseId" = @id), '
      '"updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    await _audit(session,
      action: 'create',
      entityType: 'lecture',
      entityId: lecture.id.toString(),
      newValue: jsonEncode({'courseId': courseId, 'title': title, 'type': type}),
    );

    return {
      'success': true,
      'lecture': lecture.toJson(),
    };
  }

  /// Update a lecture.
  Future<Map<String, dynamic>> adminUpdateLecture(
    Session session,
    int lectureId,
    String title,
    String? content,
    String? scriptJson,
    bool isFreePreview,
  ) async {
    final lecture = await Lecture.db.findById(session, lectureId);
    if (lecture == null) {
      return {'success': false, 'error': 'Lecture not found'};
    }

    final updated = await Lecture.db.updateRow(
      session,
      lecture.copyWith(
        title: title,
        content: content,
        scriptJson: scriptJson,
        isFreePreview: isFreePreview,
      ),
    );

    await _audit(session,
      action: 'update',
      entityType: 'lecture',
      entityId: lectureId.toString(),
    );

    return {
      'success': true,
      'lecture': updated.toJson(),
    };
  }

  /// Delete a lecture.
  Future<Map<String, dynamic>> adminDeleteLecture(
    Session session,
    int lectureId,
  ) async {
    final lecture = await Lecture.db.findById(session, lectureId);
    if (lecture == null) {
      return {'success': false, 'error': 'Lecture not found'};
    }

    final courseId = lecture.courseId;

    // Delete progress records
    await session.db.unsafeQuery(
      'DELETE FROM lecture_progress WHERE "lectureId" = @lectureId',
      parameters: QueryParameters.named({'lectureId': lectureId}),
    );

    await Lecture.db.deleteRow(session, lecture);

    // Update course totalLectures
    await session.db.unsafeQuery(
      'UPDATE courses SET "totalLectures" = (SELECT COUNT(*) FROM lectures WHERE "courseId" = @id), '
      '"updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    await _audit(session,
      action: 'delete',
      entityType: 'lecture',
      entityId: lectureId.toString(),
      oldValue: jsonEncode({'courseId': courseId, 'title': lecture.title}),
    );

    return {'success': true};
  }

  /// Reorder sections within a course.
  /// [orderJson] is a JSON array of objects: [{"id": 1, "sortOrder": 0}, ...]
  Future<Map<String, dynamic>> adminReorderSections(
    Session session,
    int courseId,
    String orderJson,
  ) async {
    final List<dynamic> orders = jsonDecode(orderJson);

    for (final item in orders) {
      final id = item['id'] as int;
      final sortOrder = item['sortOrder'] as int;
      await session.db.unsafeQuery(
        'UPDATE course_sections SET "sortOrder" = @sortOrder WHERE id = @id AND "courseId" = @courseId',
        parameters: QueryParameters.named({
          'sortOrder': sortOrder,
          'id': id,
          'courseId': courseId,
        }),
      );
    }

    await _audit(session,
      action: 'reorder',
      entityType: 'section',
      entityId: courseId.toString(),
      newValue: orderJson,
    );

    return {'success': true};
  }

  /// Reorder lectures within a section.
  /// [orderJson] is a JSON array of objects: [{"id": 1, "sortOrder": 0}, ...]
  Future<Map<String, dynamic>> adminReorderLectures(
    Session session,
    int sectionId,
    String orderJson,
  ) async {
    final List<dynamic> orders = jsonDecode(orderJson);

    for (final item in orders) {
      final id = item['id'] as int;
      final sortOrder = item['sortOrder'] as int;
      await session.db.unsafeQuery(
        'UPDATE lectures SET "sortOrder" = @sortOrder WHERE id = @id AND "sectionId" = @sectionId',
        parameters: QueryParameters.named({
          'sortOrder': sortOrder,
          'id': id,
          'sectionId': sectionId,
        }),
      );
    }

    await _audit(session,
      action: 'reorder',
      entityType: 'lecture',
      entityId: sectionId.toString(),
      newValue: orderJson,
    );

    return {'success': true};
  }

  // ===========================================================================
  // USER MANAGEMENT
  // ===========================================================================

  /// List users with search, role, subscription status filters and paging.
  Future<Map<String, dynamic>> adminListUsers(
    Session session,
    String? search,
    String? role,
    String? subscriptionStatus,
    int page,
    int pageSize,
  ) async {
    final offset = (page - 1) * pageSize;
    var whereClause = 'TRUE';
    final params = <String, dynamic>{
      'limit': pageSize,
      'offset': offset,
    };

    if (search != null && search.isNotEmpty) {
      whereClause += ' AND (name ILIKE @search OR email ILIKE @search)';
      params['search'] = '%$search%';
    }
    if (role != null && role.isNotEmpty) {
      whereClause += ' AND role = @role';
      params['role'] = role;
    }
    if (subscriptionStatus != null && subscriptionStatus.isNotEmpty) {
      whereClause += ' AND "subscriptionStatus" = @subStatus';
      params['subStatus'] = subscriptionStatus;
    }

    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM users WHERE $whereClause',
      parameters: QueryParameters.named(params),
    );
    final totalCount = countResult.first[0] as int;

    final results = await session.db.unsafeQuery(
      'SELECT id, email, name, "avatarUrl", role, "subscriptionStatus", '
      '"emailVerified", "isActive", "lastLoginAt", "loginCount", "createdAt" '
      'FROM users WHERE $whereClause '
      'ORDER BY "createdAt" DESC LIMIT @limit OFFSET @offset',
      parameters: QueryParameters.named(params),
    );

    return {
      'users': results.map((row) => <String, dynamic>{
        'id': row[0],
        'email': row[1],
        'name': row[2],
        'avatarUrl': row[3],
        'role': row[4],
        'subscriptionStatus': row[5],
        'emailVerified': row[6],
        'isActive': row[7],
        'lastLoginAt': (row[8] as DateTime?)?.toIso8601String(),
        'loginCount': row[9],
        'createdAt': (row[10] as DateTime?)?.toIso8601String(),
      }).toList(),
      'totalCount': totalCount,
      'page': page,
      'pageSize': pageSize,
      'totalPages': (totalCount / pageSize).ceil(),
    };
  }

  /// Get full user detail with enrollments, payments, and active sessions.
  Future<Map<String, dynamic>?> adminGetUser(
    Session session,
    int userId,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) return null;

    // Strip sensitive fields for response
    final userJson = user.toJson();
    userJson.remove('passwordHash');
    userJson.remove('passwordResetToken');
    userJson.remove('emailVerificationToken');
    userJson.remove('totpSecret');
    userJson.remove('recoveryCodes');
    userJson.remove('passwordHistory');

    // Enrollments
    final enrollments = await session.db.unsafeQuery(
      'SELECT e.id, e."courseId", e."progressPercent", e.status, e."enrolledAt", '
      'c.title AS "courseTitle" '
      'FROM enrollments e '
      'JOIN courses c ON e."courseId" = c.id '
      'WHERE e."userId" = @userId '
      'ORDER BY e."enrolledAt" DESC LIMIT 50',
      parameters: QueryParameters.named({'userId': userId}),
    );

    // Payments
    final payments = await session.db.unsafeQuery(
      'SELECT id, amount, currency, status, "paymentGateway", "createdAt" '
      'FROM payments WHERE "userId" = @userId ORDER BY "createdAt" DESC LIMIT 50',
      parameters: QueryParameters.named({'userId': userId}),
    );

    // Active sessions
    final sessions = await session.db.unsafeQuery(
      'SELECT id, "deviceInfo", "ipAddress", "lastActiveAt", "createdAt" '
      'FROM user_sessions WHERE "userId" = @userId AND "isRevoked" = false AND "expiresAt" > NOW() '
      'ORDER BY "lastActiveAt" DESC',
      parameters: QueryParameters.named({'userId': userId}),
    );

    return {
      'user': userJson,
      'enrollments': enrollments.map((row) => <String, dynamic>{
        'id': row[0],
        'courseId': row[1],
        'progressPercent': row[2],
        'status': row[3],
        'enrolledAt': (row[4] as DateTime?)?.toIso8601String(),
        'courseTitle': row[5],
      }).toList(),
      'payments': payments.map((row) => <String, dynamic>{
        'id': row[0],
        'amount': row[1],
        'currency': row[2],
        'status': row[3],
        'paymentGateway': row[4],
        'createdAt': (row[5] as DateTime?)?.toIso8601String(),
      }).toList(),
      'activeSessions': sessions.map((row) => <String, dynamic>{
        'id': row[0],
        'deviceInfo': row[1],
        'ipAddress': row[2],
        'lastActiveAt': (row[3] as DateTime?)?.toIso8601String(),
        'createdAt': (row[4] as DateTime?)?.toIso8601String(),
      }).toList(),
    };
  }

  /// Change a user's role.
  Future<Map<String, dynamic>> adminUpdateUserRole(
    Session session,
    int userId,
    String role,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    final oldRole = user.role;
    await User.db.updateRow(
      session,
      user.copyWith(role: role, updatedAt: DateTime.now()),
    );

    await _audit(session,
      action: 'update_role',
      entityType: 'user',
      entityId: userId.toString(),
      oldValue: jsonEncode({'role': oldRole}),
      newValue: jsonEncode({'role': role}),
    );

    return {'success': true, 'oldRole': oldRole, 'newRole': role};
  }

  /// Ban or unban a user (sets isActive flag).
  Future<Map<String, dynamic>> adminBanUser(
    Session session,
    int userId,
    bool banned,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    await User.db.updateRow(
      session,
      user.copyWith(isActive: !banned, updatedAt: DateTime.now()),
    );

    // If banning, revoke all sessions
    if (banned) {
      await session.db.unsafeQuery(
        'UPDATE user_sessions SET "isRevoked" = true WHERE "userId" = @userId',
        parameters: QueryParameters.named({'userId': userId}),
      );
    }

    await _audit(session,
      action: banned ? 'ban' : 'unban',
      entityType: 'user',
      entityId: userId.toString(),
    );

    return {'success': true, 'banned': banned};
  }

  /// Force a password reset for a user (sets a reset token and clears sessions).
  Future<Map<String, dynamic>> adminForcePasswordReset(
    Session session,
    int userId,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    // Generate a simple reset token (same pattern as auth endpoint)
    final resetToken = DateTime.now().millisecondsSinceEpoch.toRadixString(36);
    final expiresAt = DateTime.now().add(const Duration(hours: 24));

    await session.db.unsafeQuery(
      'UPDATE users SET "passwordResetToken" = @token, "passwordResetExpiresAt" = @expires, '
      '"updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({
        'token': resetToken,
        'expires': expiresAt.toIso8601String(),
        'id': userId,
      }),
    );

    // Revoke all sessions to force re-login
    await session.db.unsafeQuery(
      'UPDATE user_sessions SET "isRevoked" = true WHERE "userId" = @userId',
      parameters: QueryParameters.named({'userId': userId}),
    );

    await _audit(session,
      action: 'force_password_reset',
      entityType: 'user',
      entityId: userId.toString(),
    );

    return {
      'success': true,
      'message': 'Password reset forced. All sessions revoked.',
      'resetToken': resetToken,
    };
  }

  // ===========================================================================
  // CATEGORY MANAGEMENT
  // ===========================================================================

  /// Get all categories ordered by sortOrder.
  Future<List<Map<String, dynamic>>> adminListCategories(
    Session session,
  ) async {
    final categories = await Category.db.find(session,
      orderBy: (t) => t.sortOrder,
    );
    return categories.map((c) => c.toJson()).toList();
  }

  /// Create a new category.
  Future<Map<String, dynamic>> adminCreateCategory(
    Session session,
    String name,
    String slug,
    String? description,
    String? icon,
    int sortOrder,
  ) async {
    final category = await Category.db.insertRow(
      session,
      Category(
        name: name,
        slug: slug,
        description: description,
        icon: icon,
        sortOrder: sortOrder,
        createdAt: DateTime.now(),
      ),
    );

    await _audit(session,
      action: 'create',
      entityType: 'category',
      entityId: category.id.toString(),
      newValue: jsonEncode({'name': name, 'slug': slug}),
    );

    return {
      'success': true,
      'category': category.toJson(),
    };
  }

  /// Update a category.
  Future<Map<String, dynamic>> adminUpdateCategory(
    Session session,
    int categoryId,
    String name,
    String? description,
    String? icon,
    int sortOrder,
  ) async {
    final category = await Category.db.findById(session, categoryId);
    if (category == null) {
      return {'success': false, 'error': 'Category not found'};
    }

    final updated = await Category.db.updateRow(
      session,
      category.copyWith(
        name: name,
        description: description,
        icon: icon,
        sortOrder: sortOrder,
      ),
    );

    await _audit(session,
      action: 'update',
      entityType: 'category',
      entityId: categoryId.toString(),
    );

    return {
      'success': true,
      'category': updated.toJson(),
    };
  }

  /// Delete a category. Courses in this category will have their categoryId set to null.
  Future<Map<String, dynamic>> adminDeleteCategory(
    Session session,
    int categoryId,
  ) async {
    final category = await Category.db.findById(session, categoryId);
    if (category == null) {
      return {'success': false, 'error': 'Category not found'};
    }

    // Unlink courses from this category
    await session.db.unsafeQuery(
      'UPDATE courses SET "categoryId" = NULL WHERE "categoryId" = @id',
      parameters: QueryParameters.named({'id': categoryId}),
    );

    await Category.db.deleteRow(session, category);

    await _audit(session,
      action: 'delete',
      entityType: 'category',
      entityId: categoryId.toString(),
      oldValue: jsonEncode({'name': category.name}),
    );

    return {'success': true};
  }

  // ===========================================================================
  // SETTINGS
  // ===========================================================================

  /// Get all site settings as a key-value map.
  Future<Map<String, dynamic>> adminGetSettings(Session session) async {
    final settings = await SiteSetting.db.find(session);
    final map = <String, dynamic>{};
    for (final s in settings) {
      map[s.key] = {
        'id': s.id,
        'value': s.value,
        'updatedBy': s.updatedBy,
        'updatedAt': s.updatedAt.toIso8601String(),
      };
    }
    return map;
  }

  /// Update (or create) a site setting by key.
  Future<Map<String, dynamic>> adminUpdateSetting(
    Session session,
    String key,
    String value,
  ) async {
    final existing = await SiteSetting.db.findFirstRow(session,
      where: (t) => t.key.equals(key),
    );

    if (existing != null) {
      final oldValue = existing.value;
      await SiteSetting.db.updateRow(
        session,
        existing.copyWith(
          value: value,
          updatedAt: DateTime.now(),
        ),
      );
      await _audit(session,
        action: 'update',
        entityType: 'setting',
        entityId: key,
        oldValue: oldValue,
        newValue: value,
      );
    } else {
      await SiteSetting.db.insertRow(
        session,
        SiteSetting(
          key: key,
          value: value,
          updatedAt: DateTime.now(),
        ),
      );
      await _audit(session,
        action: 'create',
        entityType: 'setting',
        entityId: key,
        newValue: value,
      );
    }

    return {'success': true, 'key': key, 'value': value};
  }

  /// Toggle maintenance mode.
  Future<Map<String, dynamic>> adminToggleMaintenanceMode(
    Session session,
    bool enabled,
    String? message,
  ) async {
    // Update or insert the maintenance_mode flag
    await adminUpdateSetting(session, 'maintenance_mode', enabled.toString());
    if (message != null) {
      await adminUpdateSetting(session, 'maintenance_message', message);
    }

    await _audit(session,
      action: enabled ? 'enable_maintenance' : 'disable_maintenance',
      entityType: 'setting',
      entityId: 'maintenance_mode',
      newValue: jsonEncode({'enabled': enabled, 'message': message}),
    );

    return {
      'success': true,
      'maintenanceMode': enabled,
      'message': message,
    };
  }

  // ===========================================================================
  // AUDIT LOG
  // ===========================================================================

  /// Get paginated audit log with optional filters.
  Future<Map<String, dynamic>> adminGetAuditLog(
    Session session,
    int? userId,
    String? action,
    String? entityType,
    int page,
    int pageSize,
  ) async {
    final offset = (page - 1) * pageSize;
    var whereClause = 'TRUE';
    final params = <String, dynamic>{
      'limit': pageSize,
      'offset': offset,
    };

    if (userId != null) {
      whereClause += ' AND al."userId" = @userId';
      params['userId'] = userId;
    }
    if (action != null && action.isNotEmpty) {
      whereClause += ' AND al.action = @action';
      params['action'] = action;
    }
    if (entityType != null && entityType.isNotEmpty) {
      whereClause += ' AND al."entityType" = @entityType';
      params['entityType'] = entityType;
    }

    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM audit_logs al WHERE $whereClause',
      parameters: QueryParameters.named(params),
    );
    final totalCount = countResult.first[0] as int;

    final results = await session.db.unsafeQuery(
      'SELECT al.id, al."userId", al.action, al."entityType", al."entityId", '
      'al."oldValue", al."newValue", al."ipAddress", al."createdAt", '
      'u.name AS "userName", u.email AS "userEmail" '
      'FROM audit_logs al '
      'LEFT JOIN users u ON al."userId" = u.id '
      'WHERE $whereClause '
      'ORDER BY al."createdAt" DESC LIMIT @limit OFFSET @offset',
      parameters: QueryParameters.named(params),
    );

    return {
      'logs': results.map((row) => <String, dynamic>{
        'id': row[0],
        'userId': row[1],
        'action': row[2],
        'entityType': row[3],
        'entityId': row[4],
        'oldValue': row[5],
        'newValue': row[6],
        'ipAddress': row[7],
        'createdAt': (row[8] as DateTime?)?.toIso8601String(),
        'userName': row[9],
        'userEmail': row[10],
      }).toList(),
      'totalCount': totalCount,
      'page': page,
      'pageSize': pageSize,
      'totalPages': (totalCount / pageSize).ceil(),
    };
  }
}
