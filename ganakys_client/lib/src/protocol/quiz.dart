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

abstract class Quiz implements _i1.SerializableModel {
  Quiz._({
    this.id,
    required this.courseId,
    this.lectureId,
    required this.title,
    String? type,
    int? passPercentage,
  })  : type = type ?? 'section_quiz',
        passPercentage = passPercentage ?? 70;

  factory Quiz({
    int? id,
    required int courseId,
    int? lectureId,
    required String title,
    String? type,
    int? passPercentage,
  }) = _QuizImpl;

  factory Quiz.fromJson(Map<String, dynamic> jsonSerialization) {
    return Quiz(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      lectureId: jsonSerialization['lectureId'] as int?,
      title: jsonSerialization['title'] as String,
      type: jsonSerialization['type'] as String,
      passPercentage: jsonSerialization['passPercentage'] as int,
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int courseId;

  int? lectureId;

  String title;

  String type;

  int passPercentage;

  /// Returns a shallow copy of this [Quiz]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Quiz copyWith({
    int? id,
    int? courseId,
    int? lectureId,
    String? title,
    String? type,
    int? passPercentage,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'title': title,
      'type': type,
      'passPercentage': passPercentage,
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizImpl extends Quiz {
  _QuizImpl({
    int? id,
    required int courseId,
    int? lectureId,
    required String title,
    String? type,
    int? passPercentage,
  }) : super._(
          id: id,
          courseId: courseId,
          lectureId: lectureId,
          title: title,
          type: type,
          passPercentage: passPercentage,
        );

  /// Returns a shallow copy of this [Quiz]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Quiz copyWith({
    Object? id = _Undefined,
    int? courseId,
    Object? lectureId = _Undefined,
    String? title,
    String? type,
    int? passPercentage,
  }) {
    return Quiz(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      lectureId: lectureId is int? ? lectureId : this.lectureId,
      title: title ?? this.title,
      type: type ?? this.type,
      passPercentage: passPercentage ?? this.passPercentage,
    );
  }
}
