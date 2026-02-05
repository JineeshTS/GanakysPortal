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

abstract class Review implements _i1.SerializableModel {
  Review._({
    this.id,
    required this.userId,
    required this.courseId,
    required this.rating,
    this.comment,
    bool? isApproved,
    bool? isFlagged,
    required this.createdAt,
    required this.updatedAt,
  })  : isApproved = isApproved ?? true,
        isFlagged = isFlagged ?? false;

  factory Review({
    int? id,
    required int userId,
    required int courseId,
    required int rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _ReviewImpl;

  factory Review.fromJson(Map<String, dynamic> jsonSerialization) {
    return Review(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      rating: jsonSerialization['rating'] as int,
      comment: jsonSerialization['comment'] as String?,
      isApproved: jsonSerialization['isApproved'] as bool,
      isFlagged: jsonSerialization['isFlagged'] as bool,
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

  int courseId;

  int rating;

  String? comment;

  bool isApproved;

  bool isFlagged;

  DateTime createdAt;

  DateTime updatedAt;

  /// Returns a shallow copy of this [Review]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Review copyWith({
    int? id,
    int? userId,
    int? courseId,
    int? rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'rating': rating,
      if (comment != null) 'comment': comment,
      'isApproved': isApproved,
      'isFlagged': isFlagged,
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

class _ReviewImpl extends Review {
  _ReviewImpl({
    int? id,
    required int userId,
    required int courseId,
    required int rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          userId: userId,
          courseId: courseId,
          rating: rating,
          comment: comment,
          isApproved: isApproved,
          isFlagged: isFlagged,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Review]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Review copyWith({
    Object? id = _Undefined,
    int? userId,
    int? courseId,
    int? rating,
    Object? comment = _Undefined,
    bool? isApproved,
    bool? isFlagged,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Review(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      courseId: courseId ?? this.courseId,
      rating: rating ?? this.rating,
      comment: comment is String? ? comment : this.comment,
      isApproved: isApproved ?? this.isApproved,
      isFlagged: isFlagged ?? this.isFlagged,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
