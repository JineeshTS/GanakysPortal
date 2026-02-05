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

abstract class LectureProgress implements _i1.SerializableModel {
  LectureProgress._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    this.completedAt,
  })  : isCompleted = isCompleted ?? false,
        watchTimeSeconds = watchTimeSeconds ?? 0,
        lastPositionSeconds = lastPositionSeconds ?? 0;

  factory LectureProgress({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  }) = _LectureProgressImpl;

  factory LectureProgress.fromJson(Map<String, dynamic> jsonSerialization) {
    return LectureProgress(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      isCompleted: jsonSerialization['isCompleted'] as bool,
      watchTimeSeconds: jsonSerialization['watchTimeSeconds'] as int,
      lastPositionSeconds: jsonSerialization['lastPositionSeconds'] as int,
      completedAt: jsonSerialization['completedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['completedAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int lectureId;

  int courseId;

  bool isCompleted;

  int watchTimeSeconds;

  int lastPositionSeconds;

  DateTime? completedAt;

  /// Returns a shallow copy of this [LectureProgress]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  LectureProgress copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'isCompleted': isCompleted,
      'watchTimeSeconds': watchTimeSeconds,
      'lastPositionSeconds': lastPositionSeconds,
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LectureProgressImpl extends LectureProgress {
  _LectureProgressImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          isCompleted: isCompleted,
          watchTimeSeconds: watchTimeSeconds,
          lastPositionSeconds: lastPositionSeconds,
          completedAt: completedAt,
        );

  /// Returns a shallow copy of this [LectureProgress]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  LectureProgress copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    Object? completedAt = _Undefined,
  }) {
    return LectureProgress(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      isCompleted: isCompleted ?? this.isCompleted,
      watchTimeSeconds: watchTimeSeconds ?? this.watchTimeSeconds,
      lastPositionSeconds: lastPositionSeconds ?? this.lastPositionSeconds,
      completedAt: completedAt is DateTime? ? completedAt : this.completedAt,
    );
  }
}
