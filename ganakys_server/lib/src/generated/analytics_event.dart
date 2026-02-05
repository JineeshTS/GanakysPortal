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

abstract class AnalyticsEvent
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  AnalyticsEvent._({
    this.id,
    this.userId,
    required this.eventType,
    this.eventData,
    this.sessionId,
    this.ipAddress,
    this.userAgent,
    required this.createdAt,
  });

  factory AnalyticsEvent({
    int? id,
    int? userId,
    required String eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    required DateTime createdAt,
  }) = _AnalyticsEventImpl;

  factory AnalyticsEvent.fromJson(Map<String, dynamic> jsonSerialization) {
    return AnalyticsEvent(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int?,
      eventType: jsonSerialization['eventType'] as String,
      eventData: jsonSerialization['eventData'] as String?,
      sessionId: jsonSerialization['sessionId'] as String?,
      ipAddress: jsonSerialization['ipAddress'] as String?,
      userAgent: jsonSerialization['userAgent'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = AnalyticsEventTable();

  static const db = AnalyticsEventRepository._();

  @override
  int? id;

  int? userId;

  String eventType;

  String? eventData;

  String? sessionId;

  String? ipAddress;

  String? userAgent;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [AnalyticsEvent]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  AnalyticsEvent copyWith({
    int? id,
    int? userId,
    String? eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'eventType': eventType,
      if (eventData != null) 'eventData': eventData,
      if (sessionId != null) 'sessionId': sessionId,
      if (ipAddress != null) 'ipAddress': ipAddress,
      if (userAgent != null) 'userAgent': userAgent,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'eventType': eventType,
      if (eventData != null) 'eventData': eventData,
      if (sessionId != null) 'sessionId': sessionId,
      if (ipAddress != null) 'ipAddress': ipAddress,
      if (userAgent != null) 'userAgent': userAgent,
      'createdAt': createdAt.toJson(),
    };
  }

  static AnalyticsEventInclude include() {
    return AnalyticsEventInclude._();
  }

  static AnalyticsEventIncludeList includeList({
    _i1.WhereExpressionBuilder<AnalyticsEventTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AnalyticsEventTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AnalyticsEventTable>? orderByList,
    AnalyticsEventInclude? include,
  }) {
    return AnalyticsEventIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(AnalyticsEvent.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(AnalyticsEvent.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AnalyticsEventImpl extends AnalyticsEvent {
  _AnalyticsEventImpl({
    int? id,
    int? userId,
    required String eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          eventType: eventType,
          eventData: eventData,
          sessionId: sessionId,
          ipAddress: ipAddress,
          userAgent: userAgent,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [AnalyticsEvent]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  AnalyticsEvent copyWith({
    Object? id = _Undefined,
    Object? userId = _Undefined,
    String? eventType,
    Object? eventData = _Undefined,
    Object? sessionId = _Undefined,
    Object? ipAddress = _Undefined,
    Object? userAgent = _Undefined,
    DateTime? createdAt,
  }) {
    return AnalyticsEvent(
      id: id is int? ? id : this.id,
      userId: userId is int? ? userId : this.userId,
      eventType: eventType ?? this.eventType,
      eventData: eventData is String? ? eventData : this.eventData,
      sessionId: sessionId is String? ? sessionId : this.sessionId,
      ipAddress: ipAddress is String? ? ipAddress : this.ipAddress,
      userAgent: userAgent is String? ? userAgent : this.userAgent,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class AnalyticsEventTable extends _i1.Table<int?> {
  AnalyticsEventTable({super.tableRelation})
      : super(tableName: 'analytics_events') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    eventType = _i1.ColumnString(
      'eventType',
      this,
    );
    eventData = _i1.ColumnString(
      'eventData',
      this,
    );
    sessionId = _i1.ColumnString(
      'sessionId',
      this,
    );
    ipAddress = _i1.ColumnString(
      'ipAddress',
      this,
    );
    userAgent = _i1.ColumnString(
      'userAgent',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString eventType;

  late final _i1.ColumnString eventData;

  late final _i1.ColumnString sessionId;

  late final _i1.ColumnString ipAddress;

  late final _i1.ColumnString userAgent;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        eventType,
        eventData,
        sessionId,
        ipAddress,
        userAgent,
        createdAt,
      ];
}

class AnalyticsEventInclude extends _i1.IncludeObject {
  AnalyticsEventInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => AnalyticsEvent.t;
}

class AnalyticsEventIncludeList extends _i1.IncludeList {
  AnalyticsEventIncludeList._({
    _i1.WhereExpressionBuilder<AnalyticsEventTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(AnalyticsEvent.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => AnalyticsEvent.t;
}

class AnalyticsEventRepository {
  const AnalyticsEventRepository._();

  /// Returns a list of [AnalyticsEvent]s matching the given query parameters.
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
  Future<List<AnalyticsEvent>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AnalyticsEventTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AnalyticsEventTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AnalyticsEventTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<AnalyticsEvent>(
      where: where?.call(AnalyticsEvent.t),
      orderBy: orderBy?.call(AnalyticsEvent.t),
      orderByList: orderByList?.call(AnalyticsEvent.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [AnalyticsEvent] matching the given query parameters.
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
  Future<AnalyticsEvent?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AnalyticsEventTable>? where,
    int? offset,
    _i1.OrderByBuilder<AnalyticsEventTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AnalyticsEventTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<AnalyticsEvent>(
      where: where?.call(AnalyticsEvent.t),
      orderBy: orderBy?.call(AnalyticsEvent.t),
      orderByList: orderByList?.call(AnalyticsEvent.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [AnalyticsEvent] by its [id] or null if no such row exists.
  Future<AnalyticsEvent?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<AnalyticsEvent>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [AnalyticsEvent]s in the list and returns the inserted rows.
  ///
  /// The returned [AnalyticsEvent]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<AnalyticsEvent>> insert(
    _i1.Session session,
    List<AnalyticsEvent> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<AnalyticsEvent>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [AnalyticsEvent] and returns the inserted row.
  ///
  /// The returned [AnalyticsEvent] will have its `id` field set.
  Future<AnalyticsEvent> insertRow(
    _i1.Session session,
    AnalyticsEvent row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<AnalyticsEvent>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [AnalyticsEvent]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<AnalyticsEvent>> update(
    _i1.Session session,
    List<AnalyticsEvent> rows, {
    _i1.ColumnSelections<AnalyticsEventTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<AnalyticsEvent>(
      rows,
      columns: columns?.call(AnalyticsEvent.t),
      transaction: transaction,
    );
  }

  /// Updates a single [AnalyticsEvent]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<AnalyticsEvent> updateRow(
    _i1.Session session,
    AnalyticsEvent row, {
    _i1.ColumnSelections<AnalyticsEventTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<AnalyticsEvent>(
      row,
      columns: columns?.call(AnalyticsEvent.t),
      transaction: transaction,
    );
  }

  /// Deletes all [AnalyticsEvent]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<AnalyticsEvent>> delete(
    _i1.Session session,
    List<AnalyticsEvent> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<AnalyticsEvent>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [AnalyticsEvent].
  Future<AnalyticsEvent> deleteRow(
    _i1.Session session,
    AnalyticsEvent row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<AnalyticsEvent>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<AnalyticsEvent>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<AnalyticsEventTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<AnalyticsEvent>(
      where: where(AnalyticsEvent.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AnalyticsEventTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<AnalyticsEvent>(
      where: where?.call(AnalyticsEvent.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
