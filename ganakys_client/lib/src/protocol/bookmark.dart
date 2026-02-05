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

abstract class Bookmark implements _i1.SerializableModel {
  Bookmark._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    int? timestampSeconds,
    this.label,
    required this.createdAt,
  }) : timestampSeconds = timestampSeconds ?? 0;

  factory Bookmark({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    int? timestampSeconds,
    String? label,
    required DateTime createdAt,
  }) = _BookmarkImpl;

  factory Bookmark.fromJson(Map<String, dynamic> jsonSerialization) {
    return Bookmark(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      timestampSeconds: jsonSerialization['timestampSeconds'] as int,
      label: jsonSerialization['label'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int lectureId;

  int courseId;

  int timestampSeconds;

  String? label;

  DateTime createdAt;

  /// Returns a shallow copy of this [Bookmark]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Bookmark copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    int? timestampSeconds,
    String? label,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'timestampSeconds': timestampSeconds,
      if (label != null) 'label': label,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _BookmarkImpl extends Bookmark {
  _BookmarkImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    int? timestampSeconds,
    String? label,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          timestampSeconds: timestampSeconds,
          label: label,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Bookmark]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Bookmark copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    int? timestampSeconds,
    Object? label = _Undefined,
    DateTime? createdAt,
  }) {
    return Bookmark(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      timestampSeconds: timestampSeconds ?? this.timestampSeconds,
      label: label is String? ? label : this.label,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
