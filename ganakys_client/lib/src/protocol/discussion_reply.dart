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

abstract class DiscussionReply implements _i1.SerializableModel {
  DiscussionReply._({
    this.id,
    required this.discussionId,
    required this.userId,
    required this.content,
    bool? isInstructorReply,
    required this.createdAt,
    required this.updatedAt,
  }) : isInstructorReply = isInstructorReply ?? false;

  factory DiscussionReply({
    int? id,
    required int discussionId,
    required int userId,
    required String content,
    bool? isInstructorReply,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _DiscussionReplyImpl;

  factory DiscussionReply.fromJson(Map<String, dynamic> jsonSerialization) {
    return DiscussionReply(
      id: jsonSerialization['id'] as int?,
      discussionId: jsonSerialization['discussionId'] as int,
      userId: jsonSerialization['userId'] as int,
      content: jsonSerialization['content'] as String,
      isInstructorReply: jsonSerialization['isInstructorReply'] as bool,
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

  int discussionId;

  int userId;

  String content;

  bool isInstructorReply;

  DateTime createdAt;

  DateTime updatedAt;

  /// Returns a shallow copy of this [DiscussionReply]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  DiscussionReply copyWith({
    int? id,
    int? discussionId,
    int? userId,
    String? content,
    bool? isInstructorReply,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'discussionId': discussionId,
      'userId': userId,
      'content': content,
      'isInstructorReply': isInstructorReply,
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

class _DiscussionReplyImpl extends DiscussionReply {
  _DiscussionReplyImpl({
    int? id,
    required int discussionId,
    required int userId,
    required String content,
    bool? isInstructorReply,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          discussionId: discussionId,
          userId: userId,
          content: content,
          isInstructorReply: isInstructorReply,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [DiscussionReply]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  DiscussionReply copyWith({
    Object? id = _Undefined,
    int? discussionId,
    int? userId,
    String? content,
    bool? isInstructorReply,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return DiscussionReply(
      id: id is int? ? id : this.id,
      discussionId: discussionId ?? this.discussionId,
      userId: userId ?? this.userId,
      content: content ?? this.content,
      isInstructorReply: isInstructorReply ?? this.isInstructorReply,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
