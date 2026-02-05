/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod_client/serverpod_client.dart' as _i1;
import 'dart:async' as _i2;
import 'package:ganakys_client/src/protocol/bookmark.dart' as _i3;
import 'package:ganakys_client/src/protocol/certificate.dart' as _i4;
import 'package:ganakys_client/src/protocol/course.dart' as _i5;
import 'package:ganakys_client/src/protocol/category.dart' as _i6;
import 'package:ganakys_client/src/protocol/discussion.dart' as _i7;
import 'package:ganakys_client/src/protocol/discussion_reply.dart' as _i8;
import 'package:ganakys_client/src/protocol/student_note.dart' as _i9;
import 'package:ganakys_client/src/protocol/page.dart' as _i10;
import 'package:ganakys_client/src/protocol/announcement.dart' as _i11;
import 'package:ganakys_client/src/protocol/subscription_plan.dart' as _i12;
import 'package:ganakys_client/src/protocol/payment.dart' as _i13;
import 'package:ganakys_client/src/protocol/notification.dart' as _i14;
import 'package:ganakys_client/src/protocol/quiz_attempt.dart' as _i15;
import 'protocol.dart' as _i16;

/// {@category Endpoint}
class EndpointAdmin extends _i1.EndpointRef {
  EndpointAdmin(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'admin';

  /// Returns aggregate dashboard statistics for the admin panel.
  _i2.Future<Map<String, dynamic>> getDashboardStats() =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'getDashboardStats',
        {},
      );

  /// List courses with search, status, category, difficulty filters and paging.
  _i2.Future<Map<String, dynamic>> adminListCourses(
    String? search,
    String? status,
    int? categoryId,
    String? difficulty,
    int page,
    int pageSize,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminListCourses',
        {
          'search': search,
          'status': status,
          'categoryId': categoryId,
          'difficulty': difficulty,
          'page': page,
          'pageSize': pageSize,
        },
      );

  /// Get full course detail including sections, lectures, and stats.
  _i2.Future<Map<String, dynamic>?> adminGetCourse(int courseId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'admin',
        'adminGetCourse',
        {'courseId': courseId},
      );

  /// Create a new course.
  _i2.Future<Map<String, dynamic>> adminCreateCourse(
    String title,
    String slug,
    String? description,
    int? categoryId,
    String difficulty,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminCreateCourse',
        {
          'title': title,
          'slug': slug,
          'description': description,
          'categoryId': categoryId,
          'difficulty': difficulty,
        },
      );

  /// Update an existing course.
  _i2.Future<Map<String, dynamic>> adminUpdateCourse(
    int courseId,
    String title,
    String? description,
    int? categoryId,
    String difficulty,
    bool isPublished,
    bool isFeatured,
    double price,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateCourse',
        {
          'courseId': courseId,
          'title': title,
          'description': description,
          'categoryId': categoryId,
          'difficulty': difficulty,
          'isPublished': isPublished,
          'isFeatured': isFeatured,
          'price': price,
        },
      );

  /// Delete a course and all related data (sections, lectures, enrollments, reviews).
  _i2.Future<Map<String, dynamic>> adminDeleteCourse(int courseId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminDeleteCourse',
        {'courseId': courseId},
      );

  /// Duplicate a course (and its sections/lectures) as a new draft.
  _i2.Future<Map<String, dynamic>> adminDuplicateCourse(int courseId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminDuplicateCourse',
        {'courseId': courseId},
      );

  /// Add a new section to a course.
  _i2.Future<Map<String, dynamic>> adminCreateSection(
    int courseId,
    String title,
    int sortOrder,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminCreateSection',
        {
          'courseId': courseId,
          'title': title,
          'sortOrder': sortOrder,
        },
      );

  /// Update an existing section.
  _i2.Future<Map<String, dynamic>> adminUpdateSection(
    int sectionId,
    String title,
    String? description,
    int sortOrder,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateSection',
        {
          'sectionId': sectionId,
          'title': title,
          'description': description,
          'sortOrder': sortOrder,
        },
      );

  /// Delete a section and its lectures.
  _i2.Future<Map<String, dynamic>> adminDeleteSection(int sectionId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminDeleteSection',
        {'sectionId': sectionId},
      );

  /// Add a new lecture.
  _i2.Future<Map<String, dynamic>> adminCreateLecture(
    int sectionId,
    int courseId,
    String title,
    String type,
    int sortOrder,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminCreateLecture',
        {
          'sectionId': sectionId,
          'courseId': courseId,
          'title': title,
          'type': type,
          'sortOrder': sortOrder,
        },
      );

  /// Update a lecture.
  _i2.Future<Map<String, dynamic>> adminUpdateLecture(
    int lectureId,
    String title,
    String? content,
    String? scriptJson,
    bool isFreePreview,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateLecture',
        {
          'lectureId': lectureId,
          'title': title,
          'content': content,
          'scriptJson': scriptJson,
          'isFreePreview': isFreePreview,
        },
      );

  /// Delete a lecture.
  _i2.Future<Map<String, dynamic>> adminDeleteLecture(int lectureId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminDeleteLecture',
        {'lectureId': lectureId},
      );

  /// Reorder sections within a course.
  /// [orderJson] is a JSON array of objects: [{"id": 1, "sortOrder": 0}, ...]
  _i2.Future<Map<String, dynamic>> adminReorderSections(
    int courseId,
    String orderJson,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminReorderSections',
        {
          'courseId': courseId,
          'orderJson': orderJson,
        },
      );

  /// Reorder lectures within a section.
  /// [orderJson] is a JSON array of objects: [{"id": 1, "sortOrder": 0}, ...]
  _i2.Future<Map<String, dynamic>> adminReorderLectures(
    int sectionId,
    String orderJson,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminReorderLectures',
        {
          'sectionId': sectionId,
          'orderJson': orderJson,
        },
      );

  /// List users with search, role, subscription status filters and paging.
  _i2.Future<Map<String, dynamic>> adminListUsers(
    String? search,
    String? role,
    String? subscriptionStatus,
    int page,
    int pageSize,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminListUsers',
        {
          'search': search,
          'role': role,
          'subscriptionStatus': subscriptionStatus,
          'page': page,
          'pageSize': pageSize,
        },
      );

  /// Get full user detail with enrollments, payments, and active sessions.
  _i2.Future<Map<String, dynamic>?> adminGetUser(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'admin',
        'adminGetUser',
        {'userId': userId},
      );

  /// Change a user's role.
  _i2.Future<Map<String, dynamic>> adminUpdateUserRole(
    int userId,
    String role,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateUserRole',
        {
          'userId': userId,
          'role': role,
        },
      );

  /// Ban or unban a user (sets isActive flag).
  _i2.Future<Map<String, dynamic>> adminBanUser(
    int userId,
    bool banned,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminBanUser',
        {
          'userId': userId,
          'banned': banned,
        },
      );

  /// Force a password reset for a user (sets a reset token and clears sessions).
  _i2.Future<Map<String, dynamic>> adminForcePasswordReset(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminForcePasswordReset',
        {'userId': userId},
      );

  /// Get all categories ordered by sortOrder.
  _i2.Future<List<Map<String, dynamic>>> adminListCategories() =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'admin',
        'adminListCategories',
        {},
      );

  /// Create a new category.
  _i2.Future<Map<String, dynamic>> adminCreateCategory(
    String name,
    String slug,
    String? description,
    String? icon,
    int sortOrder,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminCreateCategory',
        {
          'name': name,
          'slug': slug,
          'description': description,
          'icon': icon,
          'sortOrder': sortOrder,
        },
      );

  /// Update a category.
  _i2.Future<Map<String, dynamic>> adminUpdateCategory(
    int categoryId,
    String name,
    String? description,
    String? icon,
    int sortOrder,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateCategory',
        {
          'categoryId': categoryId,
          'name': name,
          'description': description,
          'icon': icon,
          'sortOrder': sortOrder,
        },
      );

  /// Delete a category. Courses in this category will have their categoryId set to null.
  _i2.Future<Map<String, dynamic>> adminDeleteCategory(int categoryId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminDeleteCategory',
        {'categoryId': categoryId},
      );

  /// Get all site settings as a key-value map.
  _i2.Future<Map<String, dynamic>> adminGetSettings() =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminGetSettings',
        {},
      );

  /// Update (or create) a site setting by key.
  _i2.Future<Map<String, dynamic>> adminUpdateSetting(
    String key,
    String value,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminUpdateSetting',
        {
          'key': key,
          'value': value,
        },
      );

  /// Toggle maintenance mode.
  _i2.Future<Map<String, dynamic>> adminToggleMaintenanceMode(
    bool enabled,
    String? message,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminToggleMaintenanceMode',
        {
          'enabled': enabled,
          'message': message,
        },
      );

  /// Get paginated audit log with optional filters.
  _i2.Future<Map<String, dynamic>> adminGetAuditLog(
    int? userId,
    String? action,
    String? entityType,
    int page,
    int pageSize,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'admin',
        'adminGetAuditLog',
        {
          'userId': userId,
          'action': action,
          'entityType': entityType,
          'page': page,
          'pageSize': pageSize,
        },
      );
}

/// {@category Endpoint}
class EndpointAuth extends _i1.EndpointRef {
  EndpointAuth(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'auth';

  _i2.Future<Map<String, dynamic>> register(
    String email,
    String name,
    String password,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'register',
        {
          'email': email,
          'name': name,
          'password': password,
        },
      );

  _i2.Future<Map<String, dynamic>> login(
    String email,
    String password,
    String? deviceInfo,
    String? ipAddress,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'login',
        {
          'email': email,
          'password': password,
          'deviceInfo': deviceInfo,
          'ipAddress': ipAddress,
        },
      );

  _i2.Future<Map<String, dynamic>> verify2fa(
    int userId,
    String code,
    String? deviceInfo,
    String? ipAddress,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'verify2fa',
        {
          'userId': userId,
          'code': code,
          'deviceInfo': deviceInfo,
          'ipAddress': ipAddress,
        },
      );

  _i2.Future<Map<String, dynamic>> refreshToken(
    String refreshToken,
    String? ipAddress,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'refreshToken',
        {
          'refreshToken': refreshToken,
          'ipAddress': ipAddress,
        },
      );

  _i2.Future<Map<String, dynamic>> verifyEmail(String token) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'verifyEmail',
        {'token': token},
      );

  _i2.Future<Map<String, dynamic>> forgotPassword(String email) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'forgotPassword',
        {'email': email},
      );

  _i2.Future<Map<String, dynamic>> resetPassword(
    String token,
    String newPassword,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'resetPassword',
        {
          'token': token,
          'newPassword': newPassword,
        },
      );

  _i2.Future<Map<String, dynamic>> logout(String refreshToken) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'logout',
        {'refreshToken': refreshToken},
      );

  _i2.Future<List<Map<String, dynamic>>> getSessions(int userId) =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'auth',
        'getSessions',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> revokeSession(
    int userId,
    int sessionId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'auth',
        'revokeSession',
        {
          'userId': userId,
          'sessionId': sessionId,
        },
      );
}

/// {@category Endpoint}
class EndpointBookmark extends _i1.EndpointRef {
  EndpointBookmark(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'bookmark';

  _i2.Future<List<_i3.Bookmark>> getBookmarks(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<List<_i3.Bookmark>>(
        'bookmark',
        'getBookmarks',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );

  _i2.Future<_i3.Bookmark> createBookmark(
    int userId,
    int lectureId,
    int courseId,
    int timestampSeconds,
    String? label,
  ) =>
      caller.callServerEndpoint<_i3.Bookmark>(
        'bookmark',
        'createBookmark',
        {
          'userId': userId,
          'lectureId': lectureId,
          'courseId': courseId,
          'timestampSeconds': timestampSeconds,
          'label': label,
        },
      );

  _i2.Future<Map<String, dynamic>> deleteBookmark(
    int userId,
    int bookmarkId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'bookmark',
        'deleteBookmark',
        {
          'userId': userId,
          'bookmarkId': bookmarkId,
        },
      );
}

/// {@category Endpoint}
class EndpointCertificate extends _i1.EndpointRef {
  EndpointCertificate(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'certificate';

  _i2.Future<Map<String, dynamic>> generateCertificate(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'certificate',
        'generateCertificate',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );

  _i2.Future<List<_i4.Certificate>> getCertificates(int userId) =>
      caller.callServerEndpoint<List<_i4.Certificate>>(
        'certificate',
        'getCertificates',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> verifyCertificate(
          String certificateNumber) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'certificate',
        'verifyCertificate',
        {'certificateNumber': certificateNumber},
      );
}

/// {@category Endpoint}
class EndpointCourse extends _i1.EndpointRef {
  EndpointCourse(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'course';

  _i2.Future<Map<String, dynamic>> listCourses({
    String? search,
    int? categoryId,
    String? difficulty,
    required String sortBy,
    required int page,
    required int pageSize,
  }) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'course',
        'listCourses',
        {
          'search': search,
          'categoryId': categoryId,
          'difficulty': difficulty,
          'sortBy': sortBy,
          'page': page,
          'pageSize': pageSize,
        },
      );

  _i2.Future<Map<String, dynamic>?> getCourseBySlug(String slug) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'course',
        'getCourseBySlug',
        {'slug': slug},
      );

  _i2.Future<_i5.Course?> getCourse(int courseId) =>
      caller.callServerEndpoint<_i5.Course?>(
        'course',
        'getCourse',
        {'courseId': courseId},
      );

  _i2.Future<List<_i6.Category>> getCategories() =>
      caller.callServerEndpoint<List<_i6.Category>>(
        'course',
        'getCategories',
        {},
      );

  _i2.Future<List<_i5.Course>> getFeaturedCourses() =>
      caller.callServerEndpoint<List<_i5.Course>>(
        'course',
        'getFeaturedCourses',
        {},
      );

  _i2.Future<Map<String, dynamic>?> getCourseCurriculum(
    int courseId,
    int userId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'course',
        'getCourseCurriculum',
        {
          'courseId': courseId,
          'userId': userId,
        },
      );
}

/// {@category Endpoint}
class EndpointDiscussion extends _i1.EndpointRef {
  EndpointDiscussion(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'discussion';

  /// Returns paginated discussions for a course, optionally filtered by lecture.
  /// Pinned discussions are returned first, then sorted by most recent.
  _i2.Future<Map<String, dynamic>> getDiscussions(
    int courseId,
    int? lectureId,
    int page,
    int pageSize,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'discussion',
        'getDiscussions',
        {
          'courseId': courseId,
          'lectureId': lectureId,
          'page': page,
          'pageSize': pageSize,
        },
      );

  /// Creates a new discussion thread in a course (optionally tied to a lecture).
  _i2.Future<_i7.Discussion> createDiscussion(
    int userId,
    int courseId,
    int? lectureId,
    String title,
    String content,
  ) =>
      caller.callServerEndpoint<_i7.Discussion>(
        'discussion',
        'createDiscussion',
        {
          'userId': userId,
          'courseId': courseId,
          'lectureId': lectureId,
          'title': title,
          'content': content,
        },
      );

  /// Returns all replies for a given discussion, ordered by creation date
  /// ascending (oldest first) so the conversation reads top-to-bottom.
  _i2.Future<List<_i8.DiscussionReply>> getDiscussionReplies(
          int discussionId) =>
      caller.callServerEndpoint<List<_i8.DiscussionReply>>(
        'discussion',
        'getDiscussionReplies',
        {'discussionId': discussionId},
      );

  /// Adds a reply to an existing discussion. Also increments the discussion's
  /// replyCount and updates its updatedAt timestamp.
  _i2.Future<_i8.DiscussionReply> createReply(
    int userId,
    int discussionId,
    String content,
  ) =>
      caller.callServerEndpoint<_i8.DiscussionReply>(
        'discussion',
        'createReply',
        {
          'userId': userId,
          'discussionId': discussionId,
          'content': content,
        },
      );

  /// Marks a discussion as resolved. Only the original author (userId) can
  /// resolve their own discussion.
  _i2.Future<_i7.Discussion> resolveDiscussion(
    int discussionId,
    int userId,
  ) =>
      caller.callServerEndpoint<_i7.Discussion>(
        'discussion',
        'resolveDiscussion',
        {
          'discussionId': discussionId,
          'userId': userId,
        },
      );
}

/// {@category Endpoint}
class EndpointEnrollment extends _i1.EndpointRef {
  EndpointEnrollment(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'enrollment';

  _i2.Future<Map<String, dynamic>> enroll(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'enrollment',
        'enroll',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );

  _i2.Future<List<Map<String, dynamic>>> getMyEnrollments(int userId) =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'enrollment',
        'getMyEnrollments',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> updateProgress(
    int userId,
    int lectureId,
    int courseId,
    int positionSeconds,
    int watchTimeSeconds,
    bool isCompleted,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'enrollment',
        'updateProgress',
        {
          'userId': userId,
          'lectureId': lectureId,
          'courseId': courseId,
          'positionSeconds': positionSeconds,
          'watchTimeSeconds': watchTimeSeconds,
          'isCompleted': isCompleted,
        },
      );

  _i2.Future<List<Map<String, dynamic>>> getContinueLearning(int userId) =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'enrollment',
        'getContinueLearning',
        {'userId': userId},
      );
}

/// {@category Endpoint}
class EndpointGeneration extends _i1.EndpointRef {
  EndpointGeneration(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'generation';

  _i2.Future<Map<String, dynamic>> listJobs({
    String? status,
    required int page,
    required int pageSize,
  }) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'listJobs',
        {
          'status': status,
          'page': page,
          'pageSize': pageSize,
        },
      );

  _i2.Future<Map<String, dynamic>?> getJob(int jobId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'generation',
        'getJob',
        {'jobId': jobId},
      );

  _i2.Future<Map<String, dynamic>> startGeneration(
    String topic,
    int? categoryId,
    String difficulty,
    int targetDurationMinutes,
    int createdBy,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'startGeneration',
        {
          'topic': topic,
          'categoryId': categoryId,
          'difficulty': difficulty,
          'targetDurationMinutes': targetDurationMinutes,
          'createdBy': createdBy,
        },
      );

  _i2.Future<Map<String, dynamic>> startStepByStep(
    String topic,
    int createdBy,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'startStepByStep',
        {
          'topic': topic,
          'createdBy': createdBy,
        },
      );

  _i2.Future<Map<String, dynamic>> generateOutline(
    int jobId,
    String topic,
    String difficulty,
    int targetDurationMinutes,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'generateOutline',
        {
          'jobId': jobId,
          'topic': topic,
          'difficulty': difficulty,
          'targetDurationMinutes': targetDurationMinutes,
        },
      );

  _i2.Future<Map<String, dynamic>> saveOutline(
    int jobId,
    String outlineJson,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'saveOutline',
        {
          'jobId': jobId,
          'outlineJson': outlineJson,
        },
      );

  _i2.Future<Map<String, dynamic>> importPipelineOutput(
    int jobId,
    int categoryId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'importPipelineOutput',
        {
          'jobId': jobId,
          'categoryId': categoryId,
        },
      );

  _i2.Future<Map<String, dynamic>> retryJob(int jobId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'generation',
        'retryJob',
        {'jobId': jobId},
      );
}

/// {@category Endpoint}
class EndpointHealth extends _i1.EndpointRef {
  EndpointHealth(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'health';

  _i2.Future<Map<String, dynamic>> check() =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'health',
        'check',
        {},
      );
}

/// {@category Endpoint}
class EndpointNote extends _i1.EndpointRef {
  EndpointNote(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'note';

  _i2.Future<List<_i9.StudentNote>> getNotes(
    int userId,
    int lectureId,
  ) =>
      caller.callServerEndpoint<List<_i9.StudentNote>>(
        'note',
        'getNotes',
        {
          'userId': userId,
          'lectureId': lectureId,
        },
      );

  _i2.Future<List<_i9.StudentNote>> getCourseNotes(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<List<_i9.StudentNote>>(
        'note',
        'getCourseNotes',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );

  _i2.Future<_i9.StudentNote> createNote(
    int userId,
    int lectureId,
    int courseId,
    String content,
    int? timestampSeconds,
  ) =>
      caller.callServerEndpoint<_i9.StudentNote>(
        'note',
        'createNote',
        {
          'userId': userId,
          'lectureId': lectureId,
          'courseId': courseId,
          'content': content,
          'timestampSeconds': timestampSeconds,
        },
      );

  _i2.Future<Map<String, dynamic>> updateNote(
    int userId,
    int noteId,
    String content,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'note',
        'updateNote',
        {
          'userId': userId,
          'noteId': noteId,
          'content': content,
        },
      );

  _i2.Future<Map<String, dynamic>> deleteNote(
    int userId,
    int noteId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'note',
        'deleteNote',
        {
          'userId': userId,
          'noteId': noteId,
        },
      );
}

/// {@category Endpoint}
class EndpointPage extends _i1.EndpointRef {
  EndpointPage(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'page';

  _i2.Future<_i10.ContentPage?> getPage(String slug) =>
      caller.callServerEndpoint<_i10.ContentPage?>(
        'page',
        'getPage',
        {'slug': slug},
      );

  _i2.Future<List<_i10.ContentPage>> getPages() =>
      caller.callServerEndpoint<List<_i10.ContentPage>>(
        'page',
        'getPages',
        {},
      );

  _i2.Future<List<_i11.Announcement>> getActiveAnnouncements() =>
      caller.callServerEndpoint<List<_i11.Announcement>>(
        'page',
        'getActiveAnnouncements',
        {},
      );

  _i2.Future<Map<String, String>> getPublicSettings() =>
      caller.callServerEndpoint<Map<String, String>>(
        'page',
        'getPublicSettings',
        {},
      );
}

/// {@category Endpoint}
class EndpointPayment extends _i1.EndpointRef {
  EndpointPayment(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'payment';

  _i2.Future<List<_i12.SubscriptionPlan>> getPlans() =>
      caller.callServerEndpoint<List<_i12.SubscriptionPlan>>(
        'payment',
        'getPlans',
        {},
      );

  _i2.Future<Map<String, dynamic>> createCheckout(
    int userId,
    int planId,
    String gateway,
    String? couponCode,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'payment',
        'createCheckout',
        {
          'userId': userId,
          'planId': planId,
          'gateway': gateway,
          'couponCode': couponCode,
        },
      );

  _i2.Future<Map<String, dynamic>> confirmPayment(
    int paymentId,
    String gatewayPaymentId,
    String gatewayOrderId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'payment',
        'confirmPayment',
        {
          'paymentId': paymentId,
          'gatewayPaymentId': gatewayPaymentId,
          'gatewayOrderId': gatewayOrderId,
        },
      );

  _i2.Future<List<_i13.Payment>> getBillingHistory(int userId) =>
      caller.callServerEndpoint<List<_i13.Payment>>(
        'payment',
        'getBillingHistory',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>?> getSubscription(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'payment',
        'getSubscription',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> cancelSubscription(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'payment',
        'cancelSubscription',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> validateCoupon(
    String code,
    int? planId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'payment',
        'validateCoupon',
        {
          'code': code,
          'planId': planId,
        },
      );
}

/// {@category Endpoint}
class EndpointProfile extends _i1.EndpointRef {
  EndpointProfile(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'profile';

  _i2.Future<Map<String, dynamic>?> getProfile(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'profile',
        'getProfile',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> updateProfile(
    int userId,
    String name,
    String? bio,
    String? avatarUrl,
    String? locale,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'updateProfile',
        {
          'userId': userId,
          'name': name,
          'bio': bio,
          'avatarUrl': avatarUrl,
          'locale': locale,
        },
      );

  _i2.Future<Map<String, dynamic>> changePassword(
    int userId,
    String currentPassword,
    String newPassword,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'changePassword',
        {
          'userId': userId,
          'currentPassword': currentPassword,
          'newPassword': newPassword,
        },
      );

  _i2.Future<Map<String, dynamic>> exportData(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'exportData',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> requestDeletion(
    int userId,
    String password,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'requestDeletion',
        {
          'userId': userId,
          'password': password,
        },
      );

  _i2.Future<Map<String, dynamic>> cancelDeletion(int userId) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'cancelDeletion',
        {'userId': userId},
      );

  _i2.Future<List<Map<String, dynamic>>> getWishlist(int userId) =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'profile',
        'getWishlist',
        {'userId': userId},
      );

  _i2.Future<Map<String, dynamic>> toggleWishlist(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'profile',
        'toggleWishlist',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );

  _i2.Future<List<_i14.Notification>> getNotifications(int userId) =>
      caller.callServerEndpoint<List<_i14.Notification>>(
        'profile',
        'getNotifications',
        {'userId': userId},
      );

  _i2.Future<bool> markNotificationRead(
    int userId,
    int notificationId,
  ) =>
      caller.callServerEndpoint<bool>(
        'profile',
        'markNotificationRead',
        {
          'userId': userId,
          'notificationId': notificationId,
        },
      );
}

/// {@category Endpoint}
class EndpointQuiz extends _i1.EndpointRef {
  EndpointQuiz(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'quiz';

  /// Returns all quizzes for a given course, each with its questions attached.
  _i2.Future<List<Map<String, dynamic>>> getQuizzesForCourse(int courseId) =>
      caller.callServerEndpoint<List<Map<String, dynamic>>>(
        'quiz',
        'getQuizzesForCourse',
        {'courseId': courseId},
      );

  /// Returns a single quiz by ID with its questions.
  _i2.Future<Map<String, dynamic>?> getQuiz(int quizId) =>
      caller.callServerEndpoint<Map<String, dynamic>?>(
        'quiz',
        'getQuiz',
        {'quizId': quizId},
      );

  /// Scores a quiz attempt and saves it to the database.
  ///
  /// [answersJson] is expected to be a JSON-encoded array of objects, each with
  /// `questionId` (int) and `selectedOption` (int index). The options JSON for
  /// each question is expected to contain objects with an `isCorrect` boolean
  /// field so that scoring can be performed server-side.
  ///
  /// Returns the saved [QuizAttempt] with the computed score and pass/fail.
  _i2.Future<_i15.QuizAttempt> submitQuizAttempt(
    int userId,
    int quizId,
    String answersJson,
  ) =>
      caller.callServerEndpoint<_i15.QuizAttempt>(
        'quiz',
        'submitQuizAttempt',
        {
          'userId': userId,
          'quizId': quizId,
          'answersJson': answersJson,
        },
      );

  /// Returns all quiz attempts for a user within a given course, ordered by
  /// most recent first.
  _i2.Future<List<_i15.QuizAttempt>> getQuizAttempts(
    int userId,
    int courseId,
  ) =>
      caller.callServerEndpoint<List<_i15.QuizAttempt>>(
        'quiz',
        'getQuizAttempts',
        {
          'userId': userId,
          'courseId': courseId,
        },
      );
}

/// {@category Endpoint}
class EndpointReview extends _i1.EndpointRef {
  EndpointReview(_i1.EndpointCaller caller) : super(caller);

  @override
  String get name => 'review';

  _i2.Future<Map<String, dynamic>> getCourseReviews(
    int courseId, {
    required int page,
    required int pageSize,
  }) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'review',
        'getCourseReviews',
        {
          'courseId': courseId,
          'page': page,
          'pageSize': pageSize,
        },
      );

  _i2.Future<Map<String, dynamic>> submitReview(
    int userId,
    int courseId,
    int rating,
    String? comment,
  ) =>
      caller.callServerEndpoint<Map<String, dynamic>>(
        'review',
        'submitReview',
        {
          'userId': userId,
          'courseId': courseId,
          'rating': rating,
          'comment': comment,
        },
      );
}

class Client extends _i1.ServerpodClientShared {
  Client(
    String host, {
    dynamic securityContext,
    _i1.AuthenticationKeyManager? authenticationKeyManager,
    Duration? streamingConnectionTimeout,
    Duration? connectionTimeout,
    Function(
      _i1.MethodCallContext,
      Object,
      StackTrace,
    )? onFailedCall,
    Function(_i1.MethodCallContext)? onSucceededCall,
    bool? disconnectStreamsOnLostInternetConnection,
  }) : super(
          host,
          _i16.Protocol(),
          securityContext: securityContext,
          authenticationKeyManager: authenticationKeyManager,
          streamingConnectionTimeout: streamingConnectionTimeout,
          connectionTimeout: connectionTimeout,
          onFailedCall: onFailedCall,
          onSucceededCall: onSucceededCall,
          disconnectStreamsOnLostInternetConnection:
              disconnectStreamsOnLostInternetConnection,
        ) {
    admin = EndpointAdmin(this);
    auth = EndpointAuth(this);
    bookmark = EndpointBookmark(this);
    certificate = EndpointCertificate(this);
    course = EndpointCourse(this);
    discussion = EndpointDiscussion(this);
    enrollment = EndpointEnrollment(this);
    generation = EndpointGeneration(this);
    health = EndpointHealth(this);
    note = EndpointNote(this);
    page = EndpointPage(this);
    payment = EndpointPayment(this);
    profile = EndpointProfile(this);
    quiz = EndpointQuiz(this);
    review = EndpointReview(this);
  }

  late final EndpointAdmin admin;

  late final EndpointAuth auth;

  late final EndpointBookmark bookmark;

  late final EndpointCertificate certificate;

  late final EndpointCourse course;

  late final EndpointDiscussion discussion;

  late final EndpointEnrollment enrollment;

  late final EndpointGeneration generation;

  late final EndpointHealth health;

  late final EndpointNote note;

  late final EndpointPage page;

  late final EndpointPayment payment;

  late final EndpointProfile profile;

  late final EndpointQuiz quiz;

  late final EndpointReview review;

  @override
  Map<String, _i1.EndpointRef> get endpointRefLookup => {
        'admin': admin,
        'auth': auth,
        'bookmark': bookmark,
        'certificate': certificate,
        'course': course,
        'discussion': discussion,
        'enrollment': enrollment,
        'generation': generation,
        'health': health,
        'note': note,
        'page': page,
        'payment': payment,
        'profile': profile,
        'quiz': quiz,
        'review': review,
      };

  @override
  Map<String, _i1.ModuleEndpointCaller> get moduleLookup => {};
}
