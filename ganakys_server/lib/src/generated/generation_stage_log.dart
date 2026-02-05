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

abstract class GenerationStageLog
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
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

  static final t = GenerationStageLogTable();

  static const db = GenerationStageLogRepository._();

  @override
  int? id;

  int jobId;

  String stage;

  String status;

  String? message;

  DateTime? startedAt;

  DateTime? completedAt;

  int? durationMs;

  @override
  _i1.Table<int?> get table => t;

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
  Map<String, dynamic> toJsonForProtocol() {
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

  static GenerationStageLogInclude include() {
    return GenerationStageLogInclude._();
  }

  static GenerationStageLogIncludeList includeList({
    _i1.WhereExpressionBuilder<GenerationStageLogTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<GenerationStageLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationStageLogTable>? orderByList,
    GenerationStageLogInclude? include,
  }) {
    return GenerationStageLogIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(GenerationStageLog.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(GenerationStageLog.t),
      include: include,
    );
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

class GenerationStageLogTable extends _i1.Table<int?> {
  GenerationStageLogTable({super.tableRelation})
      : super(tableName: 'generation_stage_logs') {
    jobId = _i1.ColumnInt(
      'jobId',
      this,
    );
    stage = _i1.ColumnString(
      'stage',
      this,
    );
    status = _i1.ColumnString(
      'status',
      this,
      hasDefault: true,
    );
    message = _i1.ColumnString(
      'message',
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
    durationMs = _i1.ColumnInt(
      'durationMs',
      this,
    );
  }

  late final _i1.ColumnInt jobId;

  late final _i1.ColumnString stage;

  late final _i1.ColumnString status;

  late final _i1.ColumnString message;

  late final _i1.ColumnDateTime startedAt;

  late final _i1.ColumnDateTime completedAt;

  late final _i1.ColumnInt durationMs;

  @override
  List<_i1.Column> get columns => [
        id,
        jobId,
        stage,
        status,
        message,
        startedAt,
        completedAt,
        durationMs,
      ];
}

class GenerationStageLogInclude extends _i1.IncludeObject {
  GenerationStageLogInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => GenerationStageLog.t;
}

class GenerationStageLogIncludeList extends _i1.IncludeList {
  GenerationStageLogIncludeList._({
    _i1.WhereExpressionBuilder<GenerationStageLogTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(GenerationStageLog.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => GenerationStageLog.t;
}

class GenerationStageLogRepository {
  const GenerationStageLogRepository._();

  /// Returns a list of [GenerationStageLog]s matching the given query parameters.
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
  Future<List<GenerationStageLog>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationStageLogTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<GenerationStageLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationStageLogTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<GenerationStageLog>(
      where: where?.call(GenerationStageLog.t),
      orderBy: orderBy?.call(GenerationStageLog.t),
      orderByList: orderByList?.call(GenerationStageLog.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [GenerationStageLog] matching the given query parameters.
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
  Future<GenerationStageLog?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationStageLogTable>? where,
    int? offset,
    _i1.OrderByBuilder<GenerationStageLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<GenerationStageLogTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<GenerationStageLog>(
      where: where?.call(GenerationStageLog.t),
      orderBy: orderBy?.call(GenerationStageLog.t),
      orderByList: orderByList?.call(GenerationStageLog.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [GenerationStageLog] by its [id] or null if no such row exists.
  Future<GenerationStageLog?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<GenerationStageLog>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [GenerationStageLog]s in the list and returns the inserted rows.
  ///
  /// The returned [GenerationStageLog]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<GenerationStageLog>> insert(
    _i1.Session session,
    List<GenerationStageLog> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<GenerationStageLog>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [GenerationStageLog] and returns the inserted row.
  ///
  /// The returned [GenerationStageLog] will have its `id` field set.
  Future<GenerationStageLog> insertRow(
    _i1.Session session,
    GenerationStageLog row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<GenerationStageLog>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [GenerationStageLog]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<GenerationStageLog>> update(
    _i1.Session session,
    List<GenerationStageLog> rows, {
    _i1.ColumnSelections<GenerationStageLogTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<GenerationStageLog>(
      rows,
      columns: columns?.call(GenerationStageLog.t),
      transaction: transaction,
    );
  }

  /// Updates a single [GenerationStageLog]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<GenerationStageLog> updateRow(
    _i1.Session session,
    GenerationStageLog row, {
    _i1.ColumnSelections<GenerationStageLogTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<GenerationStageLog>(
      row,
      columns: columns?.call(GenerationStageLog.t),
      transaction: transaction,
    );
  }

  /// Deletes all [GenerationStageLog]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<GenerationStageLog>> delete(
    _i1.Session session,
    List<GenerationStageLog> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<GenerationStageLog>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [GenerationStageLog].
  Future<GenerationStageLog> deleteRow(
    _i1.Session session,
    GenerationStageLog row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<GenerationStageLog>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<GenerationStageLog>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<GenerationStageLogTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<GenerationStageLog>(
      where: where(GenerationStageLog.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<GenerationStageLogTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<GenerationStageLog>(
      where: where?.call(GenerationStageLog.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
