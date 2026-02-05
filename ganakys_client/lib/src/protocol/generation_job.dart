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

abstract class GenerationJob implements _i1.SerializableModel {
  GenerationJob._({
    this.id,
    this.courseId,
    required this.topic,
    String? status,
    this.currentStage,
    int? progressPercent,
    this.contentJson,
    this.qualityScore,
    this.qualityReport,
    this.errorMessage,
    this.pipelineLog,
    this.outputDir,
    this.config,
    this.startedAt,
    this.completedAt,
    this.createdBy,
    required this.createdAt,
  })  : status = status ?? 'queued',
        progressPercent = progressPercent ?? 0;

  factory GenerationJob({
    int? id,
    int? courseId,
    required String topic,
    String? status,
    String? currentStage,
    int? progressPercent,
    String? contentJson,
    double? qualityScore,
    String? qualityReport,
    String? errorMessage,
    String? pipelineLog,
    String? outputDir,
    String? config,
    DateTime? startedAt,
    DateTime? completedAt,
    int? createdBy,
    required DateTime createdAt,
  }) = _GenerationJobImpl;

  factory GenerationJob.fromJson(Map<String, dynamic> jsonSerialization) {
    return GenerationJob(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int?,
      topic: jsonSerialization['topic'] as String,
      status: jsonSerialization['status'] as String,
      currentStage: jsonSerialization['currentStage'] as String?,
      progressPercent: jsonSerialization['progressPercent'] as int,
      contentJson: jsonSerialization['contentJson'] as String?,
      qualityScore: (jsonSerialization['qualityScore'] as num?)?.toDouble(),
      qualityReport: jsonSerialization['qualityReport'] as String?,
      errorMessage: jsonSerialization['errorMessage'] as String?,
      pipelineLog: jsonSerialization['pipelineLog'] as String?,
      outputDir: jsonSerialization['outputDir'] as String?,
      config: jsonSerialization['config'] as String?,
      startedAt: jsonSerialization['startedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['startedAt']),
      completedAt: jsonSerialization['completedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['completedAt']),
      createdBy: jsonSerialization['createdBy'] as int?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int? courseId;

  String topic;

  String status;

  String? currentStage;

  int progressPercent;

  String? contentJson;

  double? qualityScore;

  String? qualityReport;

  String? errorMessage;

  String? pipelineLog;

  String? outputDir;

  String? config;

  DateTime? startedAt;

  DateTime? completedAt;

  int? createdBy;

  DateTime createdAt;

  /// Returns a shallow copy of this [GenerationJob]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  GenerationJob copyWith({
    int? id,
    int? courseId,
    String? topic,
    String? status,
    String? currentStage,
    int? progressPercent,
    String? contentJson,
    double? qualityScore,
    String? qualityReport,
    String? errorMessage,
    String? pipelineLog,
    String? outputDir,
    String? config,
    DateTime? startedAt,
    DateTime? completedAt,
    int? createdBy,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (courseId != null) 'courseId': courseId,
      'topic': topic,
      'status': status,
      if (currentStage != null) 'currentStage': currentStage,
      'progressPercent': progressPercent,
      if (contentJson != null) 'contentJson': contentJson,
      if (qualityScore != null) 'qualityScore': qualityScore,
      if (qualityReport != null) 'qualityReport': qualityReport,
      if (errorMessage != null) 'errorMessage': errorMessage,
      if (pipelineLog != null) 'pipelineLog': pipelineLog,
      if (outputDir != null) 'outputDir': outputDir,
      if (config != null) 'config': config,
      if (startedAt != null) 'startedAt': startedAt?.toJson(),
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
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

class _GenerationJobImpl extends GenerationJob {
  _GenerationJobImpl({
    int? id,
    int? courseId,
    required String topic,
    String? status,
    String? currentStage,
    int? progressPercent,
    String? contentJson,
    double? qualityScore,
    String? qualityReport,
    String? errorMessage,
    String? pipelineLog,
    String? outputDir,
    String? config,
    DateTime? startedAt,
    DateTime? completedAt,
    int? createdBy,
    required DateTime createdAt,
  }) : super._(
          id: id,
          courseId: courseId,
          topic: topic,
          status: status,
          currentStage: currentStage,
          progressPercent: progressPercent,
          contentJson: contentJson,
          qualityScore: qualityScore,
          qualityReport: qualityReport,
          errorMessage: errorMessage,
          pipelineLog: pipelineLog,
          outputDir: outputDir,
          config: config,
          startedAt: startedAt,
          completedAt: completedAt,
          createdBy: createdBy,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [GenerationJob]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  GenerationJob copyWith({
    Object? id = _Undefined,
    Object? courseId = _Undefined,
    String? topic,
    String? status,
    Object? currentStage = _Undefined,
    int? progressPercent,
    Object? contentJson = _Undefined,
    Object? qualityScore = _Undefined,
    Object? qualityReport = _Undefined,
    Object? errorMessage = _Undefined,
    Object? pipelineLog = _Undefined,
    Object? outputDir = _Undefined,
    Object? config = _Undefined,
    Object? startedAt = _Undefined,
    Object? completedAt = _Undefined,
    Object? createdBy = _Undefined,
    DateTime? createdAt,
  }) {
    return GenerationJob(
      id: id is int? ? id : this.id,
      courseId: courseId is int? ? courseId : this.courseId,
      topic: topic ?? this.topic,
      status: status ?? this.status,
      currentStage: currentStage is String? ? currentStage : this.currentStage,
      progressPercent: progressPercent ?? this.progressPercent,
      contentJson: contentJson is String? ? contentJson : this.contentJson,
      qualityScore: qualityScore is double? ? qualityScore : this.qualityScore,
      qualityReport:
          qualityReport is String? ? qualityReport : this.qualityReport,
      errorMessage: errorMessage is String? ? errorMessage : this.errorMessage,
      pipelineLog: pipelineLog is String? ? pipelineLog : this.pipelineLog,
      outputDir: outputDir is String? ? outputDir : this.outputDir,
      config: config is String? ? config : this.config,
      startedAt: startedAt is DateTime? ? startedAt : this.startedAt,
      completedAt: completedAt is DateTime? ? completedAt : this.completedAt,
      createdBy: createdBy is int? ? createdBy : this.createdBy,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
