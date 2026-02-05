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

abstract class LectureProgress
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  LectureProgress._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    this.completedAt,
  })  : isCompleted = isCompleted ?? false,
        watchTimeSeconds = watchTimeSeconds ?? 0,
        lastPositionSeconds = lastPositionSeconds ?? 0;

  factory LectureProgress({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  }) = _LectureProgressImpl;

  factory LectureProgress.fromJson(Map<String, dynamic> jsonSerialization) {
    return LectureProgress(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      isCompleted: jsonSerialization['isCompleted'] as bool,
      watchTimeSeconds: jsonSerialization['watchTimeSeconds'] as int,
      lastPositionSeconds: jsonSerialization['lastPositionSeconds'] as int,
      completedAt: jsonSerialization['completedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['completedAt']),
    );
  }

  static final t = LectureProgressTable();

  static const db = LectureProgressRepository._();

  @override
  int? id;

  int userId;

  int lectureId;

  int courseId;

  bool isCompleted;

  int watchTimeSeconds;

  int lastPositionSeconds;

  DateTime? completedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [LectureProgress]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  LectureProgress copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'isCompleted': isCompleted,
      'watchTimeSeconds': watchTimeSeconds,
      'lastPositionSeconds': lastPositionSeconds,
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'isCompleted': isCompleted,
      'watchTimeSeconds': watchTimeSeconds,
      'lastPositionSeconds': lastPositionSeconds,
      if (completedAt != null) 'completedAt': completedAt?.toJson(),
    };
  }

  static LectureProgressInclude include() {
    return LectureProgressInclude._();
  }

  static LectureProgressIncludeList includeList({
    _i1.WhereExpressionBuilder<LectureProgressTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LectureProgressTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureProgressTable>? orderByList,
    LectureProgressInclude? include,
  }) {
    return LectureProgressIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(LectureProgress.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(LectureProgress.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LectureProgressImpl extends LectureProgress {
  _LectureProgressImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    DateTime? completedAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          isCompleted: isCompleted,
          watchTimeSeconds: watchTimeSeconds,
          lastPositionSeconds: lastPositionSeconds,
          completedAt: completedAt,
        );

  /// Returns a shallow copy of this [LectureProgress]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  LectureProgress copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    bool? isCompleted,
    int? watchTimeSeconds,
    int? lastPositionSeconds,
    Object? completedAt = _Undefined,
  }) {
    return LectureProgress(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      isCompleted: isCompleted ?? this.isCompleted,
      watchTimeSeconds: watchTimeSeconds ?? this.watchTimeSeconds,
      lastPositionSeconds: lastPositionSeconds ?? this.lastPositionSeconds,
      completedAt: completedAt is DateTime? ? completedAt : this.completedAt,
    );
  }
}

class LectureProgressTable extends _i1.Table<int?> {
  LectureProgressTable({super.tableRelation})
      : super(tableName: 'lecture_progress') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    lectureId = _i1.ColumnInt(
      'lectureId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    isCompleted = _i1.ColumnBool(
      'isCompleted',
      this,
      hasDefault: true,
    );
    watchTimeSeconds = _i1.ColumnInt(
      'watchTimeSeconds',
      this,
      hasDefault: true,
    );
    lastPositionSeconds = _i1.ColumnInt(
      'lastPositionSeconds',
      this,
      hasDefault: true,
    );
    completedAt = _i1.ColumnDateTime(
      'completedAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt lectureId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnBool isCompleted;

  late final _i1.ColumnInt watchTimeSeconds;

  late final _i1.ColumnInt lastPositionSeconds;

  late final _i1.ColumnDateTime completedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        lectureId,
        courseId,
        isCompleted,
        watchTimeSeconds,
        lastPositionSeconds,
        completedAt,
      ];
}

class LectureProgressInclude extends _i1.IncludeObject {
  LectureProgressInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => LectureProgress.t;
}

class LectureProgressIncludeList extends _i1.IncludeList {
  LectureProgressIncludeList._({
    _i1.WhereExpressionBuilder<LectureProgressTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(LectureProgress.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => LectureProgress.t;
}

class LectureProgressRepository {
  const LectureProgressRepository._();

  /// Returns a list of [LectureProgress]s matching the given query parameters.
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
  Future<List<LectureProgress>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureProgressTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LectureProgressTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureProgressTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<LectureProgress>(
      where: where?.call(LectureProgress.t),
      orderBy: orderBy?.call(LectureProgress.t),
      orderByList: orderByList?.call(LectureProgress.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [LectureProgress] matching the given query parameters.
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
  Future<LectureProgress?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureProgressTable>? where,
    int? offset,
    _i1.OrderByBuilder<LectureProgressTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureProgressTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<LectureProgress>(
      where: where?.call(LectureProgress.t),
      orderBy: orderBy?.call(LectureProgress.t),
      orderByList: orderByList?.call(LectureProgress.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [LectureProgress] by its [id] or null if no such row exists.
  Future<LectureProgress?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<LectureProgress>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [LectureProgress]s in the list and returns the inserted rows.
  ///
  /// The returned [LectureProgress]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<LectureProgress>> insert(
    _i1.Session session,
    List<LectureProgress> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<LectureProgress>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [LectureProgress] and returns the inserted row.
  ///
  /// The returned [LectureProgress] will have its `id` field set.
  Future<LectureProgress> insertRow(
    _i1.Session session,
    LectureProgress row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<LectureProgress>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [LectureProgress]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<LectureProgress>> update(
    _i1.Session session,
    List<LectureProgress> rows, {
    _i1.ColumnSelections<LectureProgressTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<LectureProgress>(
      rows,
      columns: columns?.call(LectureProgress.t),
      transaction: transaction,
    );
  }

  /// Updates a single [LectureProgress]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<LectureProgress> updateRow(
    _i1.Session session,
    LectureProgress row, {
    _i1.ColumnSelections<LectureProgressTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<LectureProgress>(
      row,
      columns: columns?.call(LectureProgress.t),
      transaction: transaction,
    );
  }

  /// Deletes all [LectureProgress]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<LectureProgress>> delete(
    _i1.Session session,
    List<LectureProgress> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<LectureProgress>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [LectureProgress].
  Future<LectureProgress> deleteRow(
    _i1.Session session,
    LectureProgress row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<LectureProgress>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<LectureProgress>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<LectureProgressTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<LectureProgress>(
      where: where(LectureProgress.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureProgressTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<LectureProgress>(
      where: where?.call(LectureProgress.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
