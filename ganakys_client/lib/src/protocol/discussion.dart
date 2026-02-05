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

abstract class Discussion implements _i1.SerializableModel {
  Discussion._({
    this.id,
    required this.courseId,
    this.lectureId,
    required this.userId,
    required this.title,
    required this.content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required this.createdAt,
    required this.updatedAt,
  })  : isPinned = isPinned ?? false,
        isResolved = isResolved ?? false,
        replyCount = replyCount ?? 0;

  factory Discussion({
    int? id,
    required int courseId,
    int? lectureId,
    required int userId,
    required String title,
    required String content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _DiscussionImpl;

  factory Discussion.fromJson(Map<String, dynamic> jsonSerialization) {
    return Discussion(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      lectureId: jsonSerialization['lectureId'] as int?,
      userId: jsonSerialization['userId'] as int,
      title: jsonSerialization['title'] as String,
      content: jsonSerialization['content'] as String,
      isPinned: jsonSerialization['isPinned'] as bool,
      isResolved: jsonSerialization['isResolved'] as bool,
      replyCount: jsonSerialization['replyCount'] as int,
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

  int courseId;

  int? lectureId;

  int userId;

  String title;

  String content;

  bool isPinned;

  bool isResolved;

  int replyCount;

  DateTime createdAt;

  DateTime updatedAt;

  /// Returns a shallow copy of this [Discussion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Discussion copyWith({
    int? id,
    int? courseId,
    int? lectureId,
    int? userId,
    String? title,
    String? content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'userId': userId,
      'title': title,
      'content': content,
      'isPinned': isPinned,
      'isResolved': isResolved,
      'replyCount': replyCount,
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

class _DiscussionImpl extends Discussion {
  _DiscussionImpl({
    int? id,
    required int courseId,
    int? lectureId,
    required int userId,
    required String title,
    required String content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          courseId: courseId,
          lectureId: lectureId,
          userId: userId,
          title: title,
          content: content,
          isPinned: isPinned,
          isResolved: isResolved,
          replyCount: replyCount,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Discussion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Discussion copyWith({
    Object? id = _Undefined,
    int? courseId,
    Object? lectureId = _Undefined,
    int? userId,
    String? title,
    String? content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Discussion(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      lectureId: lectureId is int? ? lectureId : this.lectureId,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      content: content ?? this.content,
      isPinned: isPinned ?? this.isPinned,
      isResolved: isResolved ?? this.isResolved,
      replyCount: replyCount ?? this.replyCount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
