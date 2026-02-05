import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class ReviewEndpoint extends Endpoint {
  // Get reviews for a course (public)
  @override
  bool get requireLogin => false;

  Future<Map<String, dynamic>> getCourseReviews(
    Session session,
    int courseId, {
    int page = 1,
    int pageSize = 20,
  }) async {
    final offset = (page - 1) * pageSize;

    final reviews = await session.db.unsafeQuery(
      '''SELECT r.id, r."userId", r.rating, r.comment, r."createdAt",
         u.name as "userName", u."avatarUrl"
         FROM reviews r
         JOIN users u ON r."userId" = u.id
         WHERE r."courseId" = @courseId AND r."isApproved" = true
         ORDER BY r."createdAt" DESC
         LIMIT @limit OFFSET @offset''',
      parameters: QueryParameters.named({
        'courseId': courseId,
        'limit': pageSize,
        'offset': offset,
      }),
    );

    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM reviews WHERE "courseId" = @courseId AND "isApproved" = true',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    final ratingDist = await session.db.unsafeQuery(
      'SELECT rating, COUNT(*) FROM reviews WHERE "courseId" = @courseId AND "isApproved" = true GROUP BY rating ORDER BY rating DESC',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    return {
      'reviews': reviews.map((row) => <String, dynamic>{
        'id': row[0],
        'userId': row[1],
        'rating': row[2],
        'comment': row[3],
        'createdAt': (row[4] as DateTime?)?.toIso8601String(),
        'userName': row[5],
        'avatarUrl': row[6],
      }).toList(),
      'totalCount': countResult.first[0],
      'ratingDistribution': {
        for (final row in ratingDist) row[0]: row[1],
      },
    };
  }

  // Submit review
  Future<Map<String, dynamic>> submitReview(
    Session session,
    int userId,
    int courseId,
    int rating,
    String? comment,
  ) async {
    if (rating < 1 || rating > 5) {
      return {'success': false, 'error': 'Rating must be between 1 and 5'};
    }

    // Check enrollment
    final enrollment = await Enrollment.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );
    if (enrollment == null) {
      return {'success': false, 'error': 'Must be enrolled to review'};
    }

    // Check existing review
    final existing = await Review.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );

    final now = DateTime.now();

    if (existing != null) {
      await Review.db.updateRow(session, existing.copyWith(
        rating: rating,
        comment: comment,
        updatedAt: now,
      ));
    } else {
      await Review.db.insertRow(session, Review(
        userId: userId,
        courseId: courseId,
        rating: rating,
        comment: comment,
        createdAt: now,
        updatedAt: now,
      ));
    }

    // Update course average rating
    await session.db.unsafeQuery(
      '''UPDATE courses SET
         "avgRating" = (SELECT AVG(rating)::numeric(3,2) FROM reviews WHERE "courseId" = @courseId AND "isApproved" = true),
         "reviewCount" = (SELECT COUNT(*) FROM reviews WHERE "courseId" = @courseId AND "isApproved" = true)
         WHERE id = @courseId''',
      parameters: QueryParameters.named({'courseId': courseId}),
    );

    return {'success': true};
  }
}
