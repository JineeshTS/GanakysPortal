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

abstract class AuditLog
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  AuditLog._({
    this.id,
    this.userId,
    required this.action,
    required this.entityType,
    this.entityId,
    this.oldValue,
    this.newValue,
    this.ipAddress,
    required this.createdAt,
  });

  factory AuditLog({
    int? id,
    int? userId,
    required String action,
    required String entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    required DateTime createdAt,
  }) = _AuditLogImpl;

  factory AuditLog.fromJson(Map<String, dynamic> jsonSerialization) {
    return AuditLog(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int?,
      action: jsonSerialization['action'] as String,
      entityType: jsonSerialization['entityType'] as String,
      entityId: jsonSerialization['entityId'] as String?,
      oldValue: jsonSerialization['oldValue'] as String?,
      newValue: jsonSerialization['newValue'] as String?,
      ipAddress: jsonSerialization['ipAddress'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = AuditLogTable();

  static const db = AuditLogRepository._();

  @override
  int? id;

  int? userId;

  String action;

  String entityType;

  String? entityId;

  String? oldValue;

  String? newValue;

  String? ipAddress;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [AuditLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  AuditLog copyWith({
    int? id,
    int? userId,
    String? action,
    String? entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'action': action,
      'entityType': entityType,
      if (entityId != null) 'entityId': entityId,
      if (oldValue != null) 'oldValue': oldValue,
      if (newValue != null) 'newValue': newValue,
      if (ipAddress != null) 'ipAddress': ipAddress,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'action': action,
      'entityType': entityType,
      if (entityId != null) 'entityId': entityId,
      if (oldValue != null) 'oldValue': oldValue,
      if (newValue != null) 'newValue': newValue,
      if (ipAddress != null) 'ipAddress': ipAddress,
      'createdAt': createdAt.toJson(),
    };
  }

  static AuditLogInclude include() {
    return AuditLogInclude._();
  }

  static AuditLogIncludeList includeList({
    _i1.WhereExpressionBuilder<AuditLogTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AuditLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuditLogTable>? orderByList,
    AuditLogInclude? include,
  }) {
    return AuditLogIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(AuditLog.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(AuditLog.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AuditLogImpl extends AuditLog {
  _AuditLogImpl({
    int? id,
    int? userId,
    required String action,
    required String entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          action: action,
          entityType: entityType,
          entityId: entityId,
          oldValue: oldValue,
          newValue: newValue,
          ipAddress: ipAddress,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [AuditLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  AuditLog copyWith({
    Object? id = _Undefined,
    Object? userId = _Undefined,
    String? action,
    String? entityType,
    Object? entityId = _Undefined,
    Object? oldValue = _Undefined,
    Object? newValue = _Undefined,
    Object? ipAddress = _Undefined,
    DateTime? createdAt,
  }) {
    return AuditLog(
      id: id is int? ? id : this.id,
      userId: userId is int? ? userId : this.userId,
      action: action ?? this.action,
      entityType: entityType ?? this.entityType,
      entityId: entityId is String? ? entityId : this.entityId,
      oldValue: oldValue is String? ? oldValue : this.oldValue,
      newValue: newValue is String? ? newValue : this.newValue,
      ipAddress: ipAddress is String? ? ipAddress : this.ipAddress,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class AuditLogTable extends _i1.Table<int?> {
  AuditLogTable({super.tableRelation}) : super(tableName: 'audit_logs') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    action = _i1.ColumnString(
      'action',
      this,
    );
    entityType = _i1.ColumnString(
      'entityType',
      this,
    );
    entityId = _i1.ColumnString(
      'entityId',
      this,
    );
    oldValue = _i1.ColumnString(
      'oldValue',
      this,
    );
    newValue = _i1.ColumnString(
      'newValue',
      this,
    );
    ipAddress = _i1.ColumnString(
      'ipAddress',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString action;

  late final _i1.ColumnString entityType;

  late final _i1.ColumnString entityId;

  late final _i1.ColumnString oldValue;

  late final _i1.ColumnString newValue;

  late final _i1.ColumnString ipAddress;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        action,
        entityType,
        entityId,
        oldValue,
        newValue,
        ipAddress,
        createdAt,
      ];
}

class AuditLogInclude extends _i1.IncludeObject {
  AuditLogInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => AuditLog.t;
}

class AuditLogIncludeList extends _i1.IncludeList {
  AuditLogIncludeList._({
    _i1.WhereExpressionBuilder<AuditLogTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(AuditLog.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => AuditLog.t;
}

class AuditLogRepository {
  const AuditLogRepository._();

  /// Returns a list of [AuditLog]s matching the given query parameters.
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
  Future<List<AuditLog>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuditLogTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AuditLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuditLogTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<AuditLog>(
      where: where?.call(AuditLog.t),
      orderBy: orderBy?.call(AuditLog.t),
      orderByList: orderByList?.call(AuditLog.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [AuditLog] matching the given query parameters.
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
  Future<AuditLog?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuditLogTable>? where,
    int? offset,
    _i1.OrderByBuilder<AuditLogTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuditLogTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<AuditLog>(
      where: where?.call(AuditLog.t),
      orderBy: orderBy?.call(AuditLog.t),
      orderByList: orderByList?.call(AuditLog.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [AuditLog] by its [id] or null if no such row exists.
  Future<AuditLog?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<AuditLog>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [AuditLog]s in the list and returns the inserted rows.
  ///
  /// The returned [AuditLog]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<AuditLog>> insert(
    _i1.Session session,
    List<AuditLog> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<AuditLog>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [AuditLog] and returns the inserted row.
  ///
  /// The returned [AuditLog] will have its `id` field set.
  Future<AuditLog> insertRow(
    _i1.Session session,
    AuditLog row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<AuditLog>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [AuditLog]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<AuditLog>> update(
    _i1.Session session,
    List<AuditLog> rows, {
    _i1.ColumnSelections<AuditLogTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<AuditLog>(
      rows,
      columns: columns?.call(AuditLog.t),
      transaction: transaction,
    );
  }

  /// Updates a single [AuditLog]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<AuditLog> updateRow(
    _i1.Session session,
    AuditLog row, {
    _i1.ColumnSelections<AuditLogTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<AuditLog>(
      row,
      columns: columns?.call(AuditLog.t),
      transaction: transaction,
    );
  }

  /// Deletes all [AuditLog]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<AuditLog>> delete(
    _i1.Session session,
    List<AuditLog> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<AuditLog>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [AuditLog].
  Future<AuditLog> deleteRow(
    _i1.Session session,
    AuditLog row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<AuditLog>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<AuditLog>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<AuditLogTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<AuditLog>(
      where: where(AuditLog.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuditLogTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<AuditLog>(
      where: where?.call(AuditLog.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
