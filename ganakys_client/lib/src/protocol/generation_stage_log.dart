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

abstract class GenerationStageLog implements _i1.SerializableModel {
  GenerationStageLog._({
    this.id,
    required this.jobId,
    required this.stage,
    String? status,
    this.message,
    this.startedAt,
    this.completedAt,
    this.durationMs,
  }) : status = status ?? 'pending';

  factory GenerationStageLog({
    int? id,
    required int jobId,
    required String stage,
    String? status,
    String? message,
    DateTime? startedAt,
    DateTime? completedAt,
    int? durationMs,
  }) = _GenerationStageLogImpl;

  factory GenerationStageLog.fromJson(Map<String, dynamic> jsonSerialization) {
    return GenerationStageLog(
      id: jsonSerialization['id'] as int?,
      jobId: jsonSerialization['jobId'] as int,
      stage: jsonSerialization['stage'] as String,
      status: jsonSerialization['status'] as String,
      message: jsonSerialization['message'] as String?,
      startedAt: jsonSerialization['startedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['startedAt']),
      completedAt: jsonSerialization['completedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['completedAt']),
      durationMs: jsonSerialization['durationMs'] as int?,
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int jobId;

  String stage;

  String status;

  String? message;

  DateTime? startedAt;

  DateTime? completedAt;

  int? durationMs;

  /// Returns a shallow copy of this [GenerationStageLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  GenerationStageLog copyWith({
    int? id,
    int? jobId,
    String? stage,
    String? status,
    String? message,
    DateTime? startedAt,
    DateTime? completedAt,
    int? durationMs,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'jobId': jobId,
      'stage': stage,
      'status': status,
      if (message != null) 'message': message,
      if (startedAt != null) 'startedAt': startedAt?.toJson(),
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
      if (durationMs != null) 'durationMs': durationMs,
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _GenerationStageLogImpl extends GenerationStageLog {
  _GenerationStageLogImpl({
    int? id,
    required int jobId,
    required String stage,
    String? status,
    String? message,
    DateTime? startedAt,
    DateTime? completedAt,
    int? durationMs,
  }) : super._(
          id: id,
          jobId: jobId,
          stage: stage,
          status: status,
          message: message,
          startedAt: startedAt,
          completedAt: completedAt,
          durationMs: durationMs,
        );

  /// Returns a shallow copy of this [GenerationStageLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  GenerationStageLog copyWith({
    Object? id = _Undefined,
    int? jobId,
    String? stage,
    String? status,
    Object? message = _Undefined,
    Object? startedAt = _Undefined,
    Object? completedAt = _Undefined,
    Object? durationMs = _Undefined,
  }) {
    return GenerationStageLog(
      id: id is int? ? id : this.id,
      jobId: jobId ?? this.jobId,
      stage: stage ?? this.stage,
      status: status ?? this.status,
      message: message is String? ? message : this.message,
      startedAt: startedAt is DateTime? ? startedAt : this.startedAt,
      completedAt: completedAt is DateTime? ? completedAt : this.completedAt,
      durationMs: durationMs is int? ? durationMs : this.durationMs,
    );
  }
}
