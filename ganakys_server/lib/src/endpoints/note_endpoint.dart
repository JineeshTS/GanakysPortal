import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class NoteEndpoint extends Endpoint {
  // Get notes for a specific lecture
  Future<List<StudentNote>> getNotes(
    Session session,
    int userId,
    int lectureId,
  ) async {
    return await StudentNote.db.find(session,
      where: (t) => t.userId.equals(userId) & t.lectureId.equals(lectureId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
    );
  }

  // Get all notes for a course
  Future<List<StudentNote>> getCourseNotes(
    Session session,
    int userId,
    int courseId,
  ) async {
    return await StudentNote.db.find(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
    );
  }

  // Create a new note
  Future<StudentNote> createNote(
    Session session,
    int userId,
    int lectureId,
    int courseId,
    String content,
    int? timestampSeconds,
  ) async {
    final now = DateTime.now();

    final note = StudentNote(
      userId: userId,
      lectureId: lectureId,
      courseId: courseId,
      content: content,
      timestampSeconds: timestampSeconds,
      createdAt: now,
      updatedAt: now,
    );

    return await StudentNote.db.insertRow(session, note);
  }

  // Update an existing note
  Future<Map<String, dynamic>> updateNote(
    Session session,
    int userId,
    int noteId,
    String content,
  ) async {
    final note = await StudentNote.db.findById(session, noteId);

    if (note == null) {
      return {'success': false, 'error': 'Note not found'};
    }

    if (note.userId != userId) {
      return {'success': false, 'error': 'Not authorized to update this note'};
    }

    final updated = await StudentNote.db.updateRow(session, note.copyWith(
      content: content,
      updatedAt: DateTime.now(),
    ));

    return {
      'success': true,
      'note': updated.toJson(),
    };
  }

  // Delete a note
  Future<Map<String, dynamic>> deleteNote(
    Session session,
    int userId,
    int noteId,
  ) async {
    final note = await StudentNote.db.findById(session, noteId);

    if (note == null) {
      return {'success': false, 'error': 'Note not found'};
    }

    if (note.userId != userId) {
      return {'success': false, 'error': 'Not authorized to delete this note'};
    }

    await StudentNote.db.deleteRow(session, note);

    return {'success': true};
  }
}
