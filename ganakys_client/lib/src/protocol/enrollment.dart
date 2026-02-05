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

abstract class Enrollment implements _i1.SerializableModel {
  Enrollment._({
    this.id,
    required this.userId,
    required this.courseId,
    double? progressPercent,
    String? status,
    required this.enrolledAt,
    this.completedAt,
  })  : progressPercent = progressPercent ?? 0.0,
        status = status ?? 'enrolled';

  factory Enrollment({
    int? id,
    required int userId,
    required int courseId,
    double? progressPercent,
    String? status,
    required DateTime enrolledAt,
    DateTime? completedAt,
  }) = _EnrollmentImpl;

  factory Enrollment.fromJson(Map<String, dynamic> jsonSerialization) {
    return Enrollment(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      progressPercent: (jsonSerialization['progressPercent'] as num).toDouble(),
      status: jsonSerialization['status'] as String,
      enrolledAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['enrolledAt']),
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

  int courseId;

  double progressPercent;

  String status;

  DateTime enrolledAt;

  DateTime? completedAt;

  /// Returns a shallow copy of this [Enrollment]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Enrollment copyWith({
    int? id,
    int? userId,
    int? courseId,
    double? progressPercent,
    String? status,
    DateTime? enrolledAt,
    DateTime? completedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'progressPercent': progressPercent,
      'status': status,
      'enrolledAt': enrolledAt.toJson(),
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _EnrollmentImpl extends Enrollment {
  _EnrollmentImpl({
    int? id,
    required int userId,
    required int courseId,
    double? progressPercent,
    String? status,
    required DateTime enrolledAt,
    DateTime? completedAt,
  }) : super._(
          id: id,
          userId: userId,
          courseId: courseId,
          progressPercent: progressPercent,
          status: status,
          enrolledAt: enrolledAt,
          completedAt: completedAt,
        );

  /// Returns a shallow copy of this [Enrollment]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Enrollment copyWith({
    Object? id = _Undefined,
    int? userId,
    int? courseId,
    double? progressPercent,
    String? status,
    DateTime? enrolledAt,
    Object? completedAt = _Undefined,
  }) {
    return Enrollment(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      courseId: courseId ?? this.courseId,
      progressPercent: progressPercent ?? this.progressPercent,
      status: status ?? this.status,
      enrolledAt: enrolledAt ?? this.enrolledAt,
      completedAt: completedAt is DateTime? ? completedAt : this.completedAt,
    );
  }
}
