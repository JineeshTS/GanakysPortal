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

abstract class CourseVersion
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
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

  static final t = CourseVersionTable();

  static const db = CourseVersionRepository._();

  @override
  int? id;

  int courseId;

  int versionNumber;

  String snapshotJson;

  String? changeSummary;

  int? createdBy;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

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
  Map<String, dynamic> toJsonForProtocol() {
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

  static CourseVersionInclude include() {
    return CourseVersionInclude._();
  }

  static CourseVersionIncludeList includeList({
    _i1.WhereExpressionBuilder<CourseVersionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseVersionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseVersionTable>? orderByList,
    CourseVersionInclude? include,
  }) {
    return CourseVersionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(CourseVersion.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(CourseVersion.t),
      include: include,
    );
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

class CourseVersionTable extends _i1.Table<int?> {
  CourseVersionTable({super.tableRelation})
      : super(tableName: 'course_versions') {
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    versionNumber = _i1.ColumnInt(
      'versionNumber',
      this,
    );
    snapshotJson = _i1.ColumnString(
      'snapshotJson',
      this,
    );
    changeSummary = _i1.ColumnString(
      'changeSummary',
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

  late final _i1.ColumnInt versionNumber;

  late final _i1.ColumnString snapshotJson;

  late final _i1.ColumnString changeSummary;

  late final _i1.ColumnInt createdBy;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        courseId,
        versionNumber,
        snapshotJson,
        changeSummary,
        createdBy,
        createdAt,
      ];
}

class CourseVersionInclude extends _i1.IncludeObject {
  CourseVersionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => CourseVersion.t;
}

class CourseVersionIncludeList extends _i1.IncludeList {
  CourseVersionIncludeList._({
    _i1.WhereExpressionBuilder<CourseVersionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(CourseVersion.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => CourseVersion.t;
}

class CourseVersionRepository {
  const CourseVersionRepository._();

  /// Returns a list of [CourseVersion]s matching the given query parameters.
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
  Future<List<CourseVersion>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseVersionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseVersionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseVersionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<CourseVersion>(
      where: where?.call(CourseVersion.t),
      orderBy: orderBy?.call(CourseVersion.t),
      orderByList: orderByList?.call(CourseVersion.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [CourseVersion] matching the given query parameters.
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
  Future<CourseVersion?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseVersionTable>? where,
    int? offset,
    _i1.OrderByBuilder<CourseVersionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseVersionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<CourseVersion>(
      where: where?.call(CourseVersion.t),
      orderBy: orderBy?.call(CourseVersion.t),
      orderByList: orderByList?.call(CourseVersion.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [CourseVersion] by its [id] or null if no such row exists.
  Future<CourseVersion?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<CourseVersion>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [CourseVersion]s in the list and returns the inserted rows.
  ///
  /// The returned [CourseVersion]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<CourseVersion>> insert(
    _i1.Session session,
    List<CourseVersion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<CourseVersion>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [CourseVersion] and returns the inserted row.
  ///
  /// The returned [CourseVersion] will have its `id` field set.
  Future<CourseVersion> insertRow(
    _i1.Session session,
    CourseVersion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<CourseVersion>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [CourseVersion]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<CourseVersion>> update(
    _i1.Session session,
    List<CourseVersion> rows, {
    _i1.ColumnSelections<CourseVersionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<CourseVersion>(
      rows,
      columns: columns?.call(CourseVersion.t),
      transaction: transaction,
    );
  }

  /// Updates a single [CourseVersion]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<CourseVersion> updateRow(
    _i1.Session session,
    CourseVersion row, {
    _i1.ColumnSelections<CourseVersionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<CourseVersion>(
      row,
      columns: columns?.call(CourseVersion.t),
      transaction: transaction,
    );
  }

  /// Deletes all [CourseVersion]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<CourseVersion>> delete(
    _i1.Session session,
    List<CourseVersion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<CourseVersion>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [CourseVersion].
  Future<CourseVersion> deleteRow(
    _i1.Session session,
    CourseVersion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<CourseVersion>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<CourseVersion>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<CourseVersionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<CourseVersion>(
      where: where(CourseVersion.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseVersionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<CourseVersion>(
      where: where?.call(CourseVersion.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
