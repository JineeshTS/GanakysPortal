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

abstract class StudentNote implements _i1.SerializableModel {
  StudentNote._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    required this.content,
    this.timestampSeconds,
    required this.createdAt,
    required this.updatedAt,
  });

  factory StudentNote({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    required String content,
    int? timestampSeconds,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _StudentNoteImpl;

  factory StudentNote.fromJson(Map<String, dynamic> jsonSerialization) {
    return StudentNote(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      content: jsonSerialization['content'] as String,
      timestampSeconds: jsonSerialization['timestampSeconds'] as int?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int lectureId;

  int courseId;

  String content;

  int? timestampSeconds;

  DateTime createdAt;

  DateTime updatedAt;

  /// Returns a shallow copy of this [StudentNote]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  StudentNote copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    String? content,
    int? timestampSeconds,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'content': content,
      if (timestampSeconds != null) 'timestampSeconds': timestampSeconds,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _StudentNoteImpl extends StudentNote {
  _StudentNoteImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    required String content,
    int? timestampSeconds,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          content: content,
          timestampSeconds: timestampSeconds,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [StudentNote]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  StudentNote copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    String? content,
    Object? timestampSeconds = _Undefined,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return StudentNote(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      content: content ?? this.content,
      timestampSeconds:
          timestampSeconds is int? ? timestampSeconds : this.timestampSeconds,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
