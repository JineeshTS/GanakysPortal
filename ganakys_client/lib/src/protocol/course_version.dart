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

abstract class CourseVersion implements _i1.SerializableModel {
  CourseVersion._({
    this.id,
    required this.courseId,
    required this.versionNumber,
    required this.snapshotJson,
    this.changeSummary,
    this.createdBy,
    required this.createdAt,
  });

  factory CourseVersion({
    int? id,
    required int courseId,
    required int versionNumber,
    required String snapshotJson,
    String? changeSummary,
    int? createdBy,
    required DateTime createdAt,
  }) = _CourseVersionImpl;

  factory CourseVersion.fromJson(Map<String, dynamic> jsonSerialization) {
    return CourseVersion(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      versionNumber: jsonSerialization['versionNumber'] as int,
      snapshotJson: jsonSerialization['snapshotJson'] as String,
      changeSummary: jsonSerialization['changeSummary'] as String?,
      createdBy: jsonSerialization['createdBy'] as int?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int courseId;

  int versionNumber;

  String snapshotJson;

  String? changeSummary;

  int? createdBy;

  DateTime createdAt;

  /// Returns a shallow copy of this [CourseVersion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  CourseVersion copyWith({
    int? id,
    int? courseId,
    int? versionNumber,
    String? snapshotJson,
    String? changeSummary,
    int? createdBy,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      'versionNumber': versionNumber,
      'snapshotJson': snapshotJson,
      if (changeSummary != null) 'changeSummary': changeSummary,
      if (createdBy != null) 'createdBy': createdBy,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CourseVersionImpl extends CourseVersion {
  _CourseVersionImpl({
    int? id,
    required int courseId,
    required int versionNumber,
    required String snapshotJson,
    String? changeSummary,
    int? createdBy,
    required DateTime createdAt,
  }) : super._(
          id: id,
          courseId: courseId,
          versionNumber: versionNumber,
          snapshotJson: snapshotJson,
          changeSummary: changeSummary,
          createdBy: createdBy,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [CourseVersion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  CourseVersion copyWith({
    Object? id = _Undefined,
    int? courseId,
    int? versionNumber,
    String? snapshotJson,
    Object? changeSummary = _Undefined,
    Object? createdBy = _Undefined,
    DateTime? createdAt,
  }) {
    return CourseVersion(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      versionNumber: versionNumber ?? this.versionNumber,
      snapshotJson: snapshotJson ?? this.snapshotJson,
      changeSummary:
          changeSummary is String? ? changeSummary : this.changeSummary,
      createdBy: createdBy is int? ? createdBy : this.createdBy,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
