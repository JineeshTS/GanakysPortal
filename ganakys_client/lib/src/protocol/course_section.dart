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

abstract class CourseSection implements _i1.SerializableModel {
  CourseSection._({
    this.id,
    required this.courseId,
    required this.title,
    this.description,
    int? sortOrder,
  }) : sortOrder = sortOrder ?? 0;

  factory CourseSection({
    int? id,
    required int courseId,
    required String title,
    String? description,
    int? sortOrder,
  }) = _CourseSectionImpl;

  factory CourseSection.fromJson(Map<String, dynamic> jsonSerialization) {
    return CourseSection(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      title: jsonSerialization['title'] as String,
      description: jsonSerialization['description'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int courseId;

  String title;

  String? description;

  int sortOrder;

  /// Returns a shallow copy of this [CourseSection]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  CourseSection copyWith({
    int? id,
    int? courseId,
    String? title,
    String? description,
    int? sortOrder,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      'title': title,
      if (description != null) 'description': description,
      'sortOrder': sortOrder,
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CourseSectionImpl extends CourseSection {
  _CourseSectionImpl({
    int? id,
    required int courseId,
    required String title,
    String? description,
    int? sortOrder,
  }) : super._(
          id: id,
          courseId: courseId,
          title: title,
          description: description,
          sortOrder: sortOrder,
        );

  /// Returns a shallow copy of this [CourseSection]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  CourseSection copyWith({
    Object? id = _Undefined,
    int? courseId,
    String? title,
    Object? description = _Undefined,
    int? sortOrder,
  }) {
    return CourseSection(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      title: title ?? this.title,
      description: description is String? ? description : this.description,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }
}
