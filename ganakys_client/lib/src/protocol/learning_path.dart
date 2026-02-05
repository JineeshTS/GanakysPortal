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

abstract class LearningPath implements _i1.SerializableModel {
  LearningPath._({
    this.id,
    required this.title,
    required this.slug,
    this.description,
    this.thumbnailUrl,
    String? difficulty,
    required this.courseIds,
    bool? isPublished,
    required this.createdAt,
  })  : difficulty = difficulty ?? 'beginner',
        isPublished = isPublished ?? false;

  factory LearningPath({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    required String courseIds,
    bool? isPublished,
    required DateTime createdAt,
  }) = _LearningPathImpl;

  factory LearningPath.fromJson(Map<String, dynamic> jsonSerialization) {
    return LearningPath(
      id: jsonSerialization['id'] as int?,
      title: jsonSerialization['title'] as String,
      slug: jsonSerialization['slug'] as String,
      description: jsonSerialization['description'] as String?,
      thumbnailUrl: jsonSerialization['thumbnailUrl'] as String?,
      difficulty: jsonSerialization['difficulty'] as String,
      courseIds: jsonSerialization['courseIds'] as String,
      isPublished: jsonSerialization['isPublished'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String title;

  String slug;

  String? description;

  String? thumbnailUrl;

  String difficulty;

  String courseIds;

  bool isPublished;

  DateTime createdAt;

  /// Returns a shallow copy of this [LearningPath]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  LearningPath copyWith({
    int? id,
    String? title,
    String? slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    String? courseIds,
    bool? isPublished,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'slug': slug,
      if (description != null) 'description': description,
      if (thumbnailUrl != null) 'thumbnailUrl': thumbnailUrl,
      'difficulty': difficulty,
      'courseIds': courseIds,
      'isPublished': isPublished,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LearningPathImpl extends LearningPath {
  _LearningPathImpl({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    required String courseIds,
    bool? isPublished,
    required DateTime createdAt,
  }) : super._(
          id: id,
          title: title,
          slug: slug,
          description: description,
          thumbnailUrl: thumbnailUrl,
          difficulty: difficulty,
          courseIds: courseIds,
          isPublished: isPublished,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [LearningPath]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  LearningPath copyWith({
    Object? id = _Undefined,
    String? title,
    String? slug,
    Object? description = _Undefined,
    Object? thumbnailUrl = _Undefined,
    String? difficulty,
    String? courseIds,
    bool? isPublished,
    DateTime? createdAt,
  }) {
    return LearningPath(
      id: id is int? ? id : this.id,
      title: title ?? this.title,
      slug: slug ?? this.slug,
      description: description is String? ? description : this.description,
      thumbnailUrl: thumbnailUrl is String? ? thumbnailUrl : this.thumbnailUrl,
      difficulty: difficulty ?? this.difficulty,
      courseIds: courseIds ?? this.courseIds,
      isPublished: isPublished ?? this.isPublished,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
