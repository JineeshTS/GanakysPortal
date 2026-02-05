import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class EnrollmentEndpoint extends Endpoint {
  // Enroll in a course
  Future<Map<String, dynamic>> enroll(
    Session session,
    int userId,
    int courseId,
  ) async {
    // Check if already enrolled
    final existing = await Enrollment.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );

    if (existing != null) {
      return {'success': false, 'error': 'Already enrolled in this course'};
    }

    final course = await Course.db.findById(session, courseId);
    if (course == null || !course.isPublished) {
      return {'success': false, 'error': 'Course not found'};
    }

    final enrollment = Enrollment(
      userId: userId,
      courseId: courseId,
      enrolledAt: DateTime.now(),
    );

    final inserted = await Enrollment.db.insertRow(session, enrollment);

    // Update enrollment count
    await session.db.unsafeQuery(
      'UPDATE courses SET "enrollmentCount" = "enrollmentCount" + 1 WHERE id = @id',
      parameters: QueryParameters.named({'id': courseId}),
    );

    return {'success': true, 'enrollmentId': inserted.id};
  }

  // Get user enrollments
  Future<List<Map<String, dynamic>>> getMyEnrollments(
    Session session,
    int userId,
  ) async {
    final enrollments = await Enrollment.db.find(session,
      where: (t) => t.userId.equals(userId),
      orderBy: (t) => t.enrolledAt,
      orderDescending: true,
    );

    final result = <Map<String, dynamic>>[];
    for (final e in enrollments) {
      final course = await Course.db.findById(session, e.courseId);
      if (course != null) {
        result.add({
          'enrollment': e.toJson(),
          'course': {
            'id': course.id,
            'title': course.title,
            'slug': course.slug,
            'thumbnailUrl': course.thumbnailUrl,
            'totalLectures': course.totalLectures,
            'durationMinutes': course.durationMinutes,
          },
        });
      }
    }

    return result;
  }

  // Update lecture progress
  Future<Map<String, dynamic>> updateProgress(
    Session session,
    int userId,
    int lectureId,
    int courseId,
    int positionSeconds,
    int watchTimeSeconds,
    bool isCompleted,
  ) async {
    var progress = await LectureProgress.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.lectureId.equals(lectureId),
    );

    final now = DateTime.now();

    if (progress == null) {
      progress = LectureProgress(
        userId: userId,
        lectureId: lectureId,
        courseId: courseId,
        isCompleted: isCompleted,
        watchTimeSeconds: watchTimeSeconds,
        lastPositionSeconds: positionSeconds,
        completedAt: isCompleted ? now : null,
      );
      await LectureProgress.db.insertRow(session, progress);
    } else {
      await LectureProgress.db.updateRow(session, progress.copyWith(
        isCompleted: isCompleted || progress.isCompleted,
        watchTimeSeconds: watchTimeSeconds,
        lastPositionSeconds: positionSeconds,
        completedAt: isCompleted && !progress.isCompleted ? now : progress.completedAt,
      ));
    }

    // Recalculate enrollment progress
    final totalLectures = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM lectures WHERE "courseId" = @courseId',
      parameters: QueryParameters.named({'courseId': courseId}),
    );
    final completedLectures = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM lecture_progress WHERE "userId" = @userId AND "courseId" = @courseId AND "isCompleted" = true',
      parameters: QueryParameters.named({'userId': userId, 'courseId': courseId}),
    );

    final total = (totalLectures.first[0] as int);
    final completed = (completedLectures.first[0] as int);
    final percent = total > 0 ? (completed / total * 100).round().toDouble() : 0.0;
    final isCourseDone = percent >= 100;

    await session.db.unsafeQuery(
      'UPDATE enrollments SET "progressPercent" = @percent, status = @status, "completedAt" = @completedAt WHERE "userId" = @userId AND "courseId" = @courseId',
      parameters: QueryParameters.named({
        'percent': percent,
        'status': isCourseDone ? 'completed' : 'in_progress',
        'completedAt': isCourseDone ? now.toIso8601String() : null,
        'userId': userId,
        'courseId': courseId,
      }),
    );

    return {
      'success': true,
      'progressPercent': percent,
      'courseCompleted': isCourseDone,
    };
  }

  // Get continue learning (last accessed courses)
  Future<List<Map<String, dynamic>>> getContinueLearning(
    Session session,
    int userId,
  ) async {
    final results = await session.db.unsafeQuery(
      '''SELECT e.id, e."courseId", e."progressPercent", e.status,
         c.title, c.slug, c."thumbnailUrl", c."totalLectures", c."durationMinutes",
         lp."lectureId", lp."lastPositionSeconds"
         FROM enrollments e
         JOIN courses c ON e."courseId" = c.id
         LEFT JOIN LATERAL (
           SELECT "lectureId", "lastPositionSeconds"
           FROM lecture_progress
           WHERE "userId" = @userId AND "courseId" = e."courseId"
           ORDER BY "completedAt" DESC NULLS FIRST
           LIMIT 1
         ) lp ON true
         WHERE e."userId" = @userId AND e.status = 'in_progress'
         ORDER BY e."enrolledAt" DESC
         LIMIT 5''',
      parameters: QueryParameters.named({'userId': userId}),
    );

    return results.map((row) => <String, dynamic>{
      'enrollmentId': row[0],
      'courseId': row[1],
      'progressPercent': row[2],
      'status': row[3],
      'courseTitle': row[4],
      'courseSlug': row[5],
      'thumbnailUrl': row[6],
      'totalLectures': row[7],
      'durationMinutes': row[8],
      'lastLectureId': row[9],
      'lastPositionSeconds': row[10],
    }).toList();
  }
}
