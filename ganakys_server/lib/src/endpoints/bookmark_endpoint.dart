import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class BookmarkEndpoint extends Endpoint {
  // Get bookmarks for a course
  Future<List<Bookmark>> getBookmarks(
    Session session,
    int userId,
    int courseId,
  ) async {
    return await Bookmark.db.find(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
    );
  }

  // Create a new bookmark
  Future<Bookmark> createBookmark(
    Session session,
    int userId,
    int lectureId,
    int courseId,
    int timestampSeconds,
    String? label,
  ) async {
    final bookmark = Bookmark(
      userId: userId,
      lectureId: lectureId,
      courseId: courseId,
      timestampSeconds: timestampSeconds,
      label: label,
      createdAt: DateTime.now(),
    );

    return await Bookmark.db.insertRow(session, bookmark);
  }

  // Delete a bookmark
  Future<Map<String, dynamic>> deleteBookmark(
    Session session,
    int userId,
    int bookmarkId,
  ) async {
    final bookmark = await Bookmark.db.findById(session, bookmarkId);

    if (bookmark == null) {
      return {'success': false, 'error': 'Bookmark not found'};
    }

    if (bookmark.userId != userId) {
      return {'success': false, 'error': 'Not authorized to delete this bookmark'};
    }

    await Bookmark.db.deleteRow(session, bookmark);

    return {'success': true};
  }
}
