import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class DiscussionEndpoint extends Endpoint {
  /// Returns paginated discussions for a course, optionally filtered by lecture.
  /// Pinned discussions are returned first, then sorted by most recent.
  Future<Map<String, dynamic>> getDiscussions(
    Session session,
    int courseId,
    int? lectureId,
    int page,
    int pageSize,
  ) async {
    final offset = (page - 1) * pageSize;

    // Build the where clause depending on whether lectureId is provided
    final where = lectureId != null
        ? (DiscussionTable t) =>
            t.courseId.equals(courseId) & t.lectureId.equals(lectureId)
        : (DiscussionTable t) => t.courseId.equals(courseId);

    final totalCount = await Discussion.db.count(
      session,
      where: where,
    );

    // Fetch discussions: pinned first, then by creation date descending
    final discussions = await Discussion.db.find(
      session,
      where: where,
      orderByList: (t) => [
        Order(column: t.isPinned, orderDescending: true),
        Order(column: t.createdAt, orderDescending: true),
      ],
      limit: pageSize,
      offset: offset,
    );

    return {
      'discussions': discussions.map((d) => d.toJson()).toList(),
      'totalCount': totalCount,
      'page': page,
      'pageSize': pageSize,
      'totalPages': totalCount > 0 ? (totalCount / pageSize).ceil() : 0,
    };
  }

  /// Creates a new discussion thread in a course (optionally tied to a lecture).
  Future<Discussion> createDiscussion(
    Session session,
    int userId,
    int courseId,
    int? lectureId,
    String title,
    String content,
  ) async {
    final now = DateTime.now().toUtc();

    final discussion = Discussion(
      courseId: courseId,
      lectureId: lectureId,
      userId: userId,
      title: title,
      content: content,
      isPinned: false,
      isResolved: false,
      replyCount: 0,
      createdAt: now,
      updatedAt: now,
    );

    final savedDiscussion =
        await Discussion.db.insertRow(session, discussion);
    return savedDiscussion;
  }

  /// Returns all replies for a given discussion, ordered by creation date
  /// ascending (oldest first) so the conversation reads top-to-bottom.
  Future<List<DiscussionReply>> getDiscussionReplies(
    Session session,
    int discussionId,
  ) async {
    final replies = await DiscussionReply.db.find(
      session,
      where: (t) => t.discussionId.equals(discussionId),
      orderBy: (t) => t.createdAt,
    );

    return replies;
  }

  /// Adds a reply to an existing discussion. Also increments the discussion's
  /// replyCount and updates its updatedAt timestamp.
  Future<DiscussionReply> createReply(
    Session session,
    int userId,
    int discussionId,
    String content,
  ) async {
    final discussion = await Discussion.db.findById(session, discussionId);
    if (discussion == null) {
      throw Exception('Discussion not found');
    }

    final now = DateTime.now().toUtc();

    final reply = DiscussionReply(
      discussionId: discussionId,
      userId: userId,
      content: content,
      isInstructorReply: false,
      createdAt: now,
      updatedAt: now,
    );

    final savedReply = await DiscussionReply.db.insertRow(session, reply);

    // Update the discussion's reply count and updatedAt
    final updatedDiscussion = discussion.copyWith(
      replyCount: discussion.replyCount + 1,
      updatedAt: now,
    );
    await Discussion.db.updateRow(session, updatedDiscussion);

    return savedReply;
  }

  /// Marks a discussion as resolved. Only the original author (userId) can
  /// resolve their own discussion.
  Future<Discussion> resolveDiscussion(
    Session session,
    int discussionId,
    int userId,
  ) async {
    final discussion = await Discussion.db.findById(session, discussionId);
    if (discussion == null) {
      throw Exception('Discussion not found');
    }

    if (discussion.userId != userId) {
      throw Exception('Only the discussion author can resolve it');
    }

    final updatedDiscussion = discussion.copyWith(
      isResolved: true,
      updatedAt: DateTime.now().toUtc(),
    );

    final saved = await Discussion.db.updateRow(session, updatedDiscussion);
    return saved;
  }
}
