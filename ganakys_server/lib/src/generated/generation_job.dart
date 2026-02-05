/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod/serverpod.dart' as _i1;

abstract class GenerationJob
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
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

  static final t = GenerationJobTable();

  static const db = GenerationJobRepository._();

  @override
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

  @override
  _i1.Table<int?> get table => t;

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
  Map<String, dynamic> toJsonForProtocol() {
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

  static GenerationJobInclude include() {
    return GenerationJobInclude._();
  }

  static GenerationJobIncludeList includeList({
    _i1.WhereExpressionBuilder<GenerationJobTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<GenerationJobTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationJobTable>? orderByList,
    GenerationJobInclude? include,
  }) {
    return GenerationJobIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(GenerationJob.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(GenerationJob.t),
      include: include,
    );
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

class GenerationJobTable extends _i1.Table<int?> {
  GenerationJobTable({super.tableRelation})
      : super(tableName: 'generation_jobs') {
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    topic = _i1.ColumnString(
      'topic',
      this,
    );
    status = _i1.ColumnString(
      'status',
      this,
      hasDefault: true,
    );
    currentStage = _i1.ColumnString(
      'currentStage',
      this,
    );
    progressPercent = _i1.ColumnInt(
      'progressPercent',
      this,
      hasDefault: true,
    );
    contentJson = _i1.ColumnString(
      'contentJson',
      this,
    );
    qualityScore = _i1.ColumnDouble(
      'qualityScore',
      this,
    );
    qualityReport = _i1.ColumnString(
      'qualityReport',
      this,
    );
    errorMessage = _i1.ColumnString(
      'errorMessage',
      this,
    );
    pipelineLog = _i1.ColumnString(
      'pipelineLog',
      this,
    );
    outputDir = _i1.ColumnString(
      'outputDir',
      this,
    );
    config = _i1.ColumnString(
      'config',
      this,
    );
    startedAt = _i1.ColumnDateTime(
      'startedAt',
      this,
    );
    completedAt = _i1.ColumnDateTime(
      'completedAt',
      this,
    );
    createdBy = _i1.ColumnInt(
      'createdBy',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnString topic;

  late final _i1.ColumnString status;

  late final _i1.ColumnString currentStage;

  late final _i1.ColumnInt progressPercent;

  late final _i1.ColumnString contentJson;

  late final _i1.ColumnDouble qualityScore;

  late final _i1.ColumnString qualityReport;

  late final _i1.ColumnString errorMessage;

  late final _i1.ColumnString pipelineLog;

  late final _i1.ColumnString outputDir;

  late final _i1.ColumnString config;

  late final _i1.ColumnDateTime startedAt;

  late final _i1.ColumnDateTime completedAt;

  late final _i1.ColumnInt createdBy;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        courseId,
        topic,
        status,
        currentStage,
        progressPercent,
        contentJson,
        qualityScore,
        qualityReport,
        errorMessage,
        pipelineLog,
        outputDir,
        config,
        startedAt,
        completedAt,
        createdBy,
        createdAt,
      ];
}

class GenerationJobInclude extends _i1.IncludeObject {
  GenerationJobInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => GenerationJob.t;
}

class GenerationJobIncludeList extends _i1.IncludeList {
  GenerationJobIncludeList._({
    _i1.WhereExpressionBuilder<GenerationJobTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(GenerationJob.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => GenerationJob.t;
}

class GenerationJobRepository {
  const GenerationJobRepository._();

  /// Returns a list of [GenerationJob]s matching the given query parameters.
  ///
  /// Use [where] to specify which items to include in the return value.
  /// If none is specified, all items will be returned.
  ///
  /// To specify the order of the items use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// The maximum number of items can be set by [limit]. If no limit is set,
  /// all items matching the query will be returned.
  ///
  /// [offset] defines how many items to skip, after which [limit] (or all)
  /// items are read from the database.
  ///
  /// ```dart
  /// var persons = await Persons.db.find(
  ///   session,
  ///   where: (t) => t.lastName.equals('Jones'),
  ///   orderBy: (t) => t.firstName,
  ///   limit: 100,
  /// );
  /// ```
  Future<List<GenerationJob>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationJobTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<GenerationJobTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationJobTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<GenerationJob>(
      where: where?.call(GenerationJob.t),
      orderBy: orderBy?.call(GenerationJob.t),
      orderByList: orderByList?.call(GenerationJob.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [GenerationJob] matching the given query parameters.
  ///
  /// Use [where] to specify which items to include in the return value.
  /// If none is specified, all items will be returned.
  ///
  /// To specify the order use [orderBy] or [orderByList]
  /// when sorting by multiple columns.
  ///
  /// [offset] defines how many items to skip, after which the next one will be picked.
  ///
  /// ```dart
  /// var youngestPerson = await Persons.db.findFirstRow(
  ///   session,
  ///   where: (t) => t.lastName.equals('Jones'),
  ///   orderBy: (t) => t.age,
  /// );
  /// ```
  Future<GenerationJob?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationJobTable>? where,
    int? offset,
    _i1.OrderByBuilder<GenerationJobTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationJobTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<GenerationJob>(
      where: where?.call(GenerationJob.t),
      orderBy: orderBy?.call(GenerationJob.t),
      orderByList: orderByList?.call(GenerationJob.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [GenerationJob] by its [id] or null if no such row exists.
  Future<GenerationJob?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<GenerationJob>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [GenerationJob]s in the list and returns the inserted rows.
  ///
  /// The returned [GenerationJob]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<GenerationJob>> insert(
    _i1.Session session,
    List<GenerationJob> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<GenerationJob>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [GenerationJob] and returns the inserted row.
  ///
  /// The returned [GenerationJob] will have its `id` field set.
  Future<GenerationJob> insertRow(
    _i1.Session session,
    GenerationJob row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<GenerationJob>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [GenerationJob]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<GenerationJob>> update(
    _i1.Session session,
    List<GenerationJob> rows, {
    _i1.ColumnSelections<GenerationJobTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<GenerationJob>(
      rows,
      columns: columns?.call(GenerationJob.t),
      transaction: transaction,
    );
  }

  /// Updates a single [GenerationJob]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<GenerationJob> updateRow(
    _i1.Session session,
    GenerationJob row, {
    _i1.ColumnSelections<GenerationJobTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<GenerationJob>(
      row,
      columns: columns?.call(GenerationJob.t),
      transaction: transaction,
    );
  }

  /// Deletes all [GenerationJob]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<GenerationJob>> delete(
    _i1.Session session,
    List<GenerationJob> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<GenerationJob>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [GenerationJob].
  Future<GenerationJob> deleteRow(
    _i1.Session session,
    GenerationJob row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<GenerationJob>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<GenerationJob>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<GenerationJobTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<GenerationJob>(
      where: where(GenerationJob.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationJobTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<GenerationJob>(
      where: where?.call(GenerationJob.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
