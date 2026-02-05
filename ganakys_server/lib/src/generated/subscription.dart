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

abstract class Subscription
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Subscription._({
    this.id,
    required this.userId,
    required this.planId,
    String? status,
    required this.currentPeriodStart,
    required this.currentPeriodEnd,
    bool? cancelAtPeriodEnd,
    this.gatewaySubscriptionId,
    required this.createdAt,
    required this.updatedAt,
  })  : status = status ?? 'active',
        cancelAtPeriodEnd = cancelAtPeriodEnd ?? false;

  factory Subscription({
    int? id,
    required int userId,
    required int planId,
    String? status,
    required DateTime currentPeriodStart,
    required DateTime currentPeriodEnd,
    bool? cancelAtPeriodEnd,
    String? gatewaySubscriptionId,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _SubscriptionImpl;

  factory Subscription.fromJson(Map<String, dynamic> jsonSerialization) {
    return Subscription(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      planId: jsonSerialization['planId'] as int,
      status: jsonSerialization['status'] as String,
      currentPeriodStart: _i1.DateTimeJsonExtension.fromJson(
          jsonSerialization['currentPeriodStart']),
      currentPeriodEnd: _i1.DateTimeJsonExtension.fromJson(
          jsonSerialization['currentPeriodEnd']),
      cancelAtPeriodEnd: jsonSerialization['cancelAtPeriodEnd'] as bool,
      gatewaySubscriptionId:
          jsonSerialization['gatewaySubscriptionId'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = SubscriptionTable();

  static const db = SubscriptionRepository._();

  @override
  int? id;

  int userId;

  int planId;

  String status;

  DateTime currentPeriodStart;

  DateTime currentPeriodEnd;

  bool cancelAtPeriodEnd;

  String? gatewaySubscriptionId;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Subscription]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Subscription copyWith({
    int? id,
    int? userId,
    int? planId,
    String? status,
    DateTime? currentPeriodStart,
    DateTime? currentPeriodEnd,
    bool? cancelAtPeriodEnd,
    String? gatewaySubscriptionId,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'planId': planId,
      'status': status,
      'currentPeriodStart': currentPeriodStart.toJson(),
      'currentPeriodEnd': currentPeriodEnd.toJson(),
      'cancelAtPeriodEnd': cancelAtPeriodEnd,
      if (gatewaySubscriptionId != null)
        'gatewaySubscriptionId': gatewaySubscriptionId,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'planId': planId,
      'status': status,
      'currentPeriodStart': currentPeriodStart.toJson(),
      'currentPeriodEnd': currentPeriodEnd.toJson(),
      'cancelAtPeriodEnd': cancelAtPeriodEnd,
      if (gatewaySubscriptionId != null)
        'gatewaySubscriptionId': gatewaySubscriptionId,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static SubscriptionInclude include() {
    return SubscriptionInclude._();
  }

  static SubscriptionIncludeList includeList({
    _i1.WhereExpressionBuilder<SubscriptionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SubscriptionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionTable>? orderByList,
    SubscriptionInclude? include,
  }) {
    return SubscriptionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Subscription.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Subscription.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _SubscriptionImpl extends Subscription {
  _SubscriptionImpl({
    int? id,
    required int userId,
    required int planId,
    String? status,
    required DateTime currentPeriodStart,
    required DateTime currentPeriodEnd,
    bool? cancelAtPeriodEnd,
    String? gatewaySubscriptionId,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          userId: userId,
          planId: planId,
          status: status,
          currentPeriodStart: currentPeriodStart,
          currentPeriodEnd: currentPeriodEnd,
          cancelAtPeriodEnd: cancelAtPeriodEnd,
          gatewaySubscriptionId: gatewaySubscriptionId,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Subscription]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Subscription copyWith({
    Object? id = _Undefined,
    int? userId,
    int? planId,
    String? status,
    DateTime? currentPeriodStart,
    DateTime? currentPeriodEnd,
    bool? cancelAtPeriodEnd,
    Object? gatewaySubscriptionId = _Undefined,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Subscription(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      planId: planId ?? this.planId,
      status: status ?? this.status,
      currentPeriodStart: currentPeriodStart ?? this.currentPeriodStart,
      currentPeriodEnd: currentPeriodEnd ?? this.currentPeriodEnd,
      cancelAtPeriodEnd: cancelAtPeriodEnd ?? this.cancelAtPeriodEnd,
      gatewaySubscriptionId: gatewaySubscriptionId is String?
          ? gatewaySubscriptionId
          : this.gatewaySubscriptionId,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class SubscriptionTable extends _i1.Table<int?> {
  SubscriptionTable({super.tableRelation}) : super(tableName: 'subscriptions') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    planId = _i1.ColumnInt(
      'planId',
      this,
    );
    status = _i1.ColumnString(
      'status',
      this,
      hasDefault: true,
    );
    currentPeriodStart = _i1.ColumnDateTime(
      'currentPeriodStart',
      this,
    );
    currentPeriodEnd = _i1.ColumnDateTime(
      'currentPeriodEnd',
      this,
    );
    cancelAtPeriodEnd = _i1.ColumnBool(
      'cancelAtPeriodEnd',
      this,
      hasDefault: true,
    );
    gatewaySubscriptionId = _i1.ColumnString(
      'gatewaySubscriptionId',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
    updatedAt = _i1.ColumnDateTime(
      'updatedAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt planId;

  late final _i1.ColumnString status;

  late final _i1.ColumnDateTime currentPeriodStart;

  late final _i1.ColumnDateTime currentPeriodEnd;

  late final _i1.ColumnBool cancelAtPeriodEnd;

  late final _i1.ColumnString gatewaySubscriptionId;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        planId,
        status,
        currentPeriodStart,
        currentPeriodEnd,
        cancelAtPeriodEnd,
        gatewaySubscriptionId,
        createdAt,
        updatedAt,
      ];
}

class SubscriptionInclude extends _i1.IncludeObject {
  SubscriptionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Subscription.t;
}

class SubscriptionIncludeList extends _i1.IncludeList {
  SubscriptionIncludeList._({
    _i1.WhereExpressionBuilder<SubscriptionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Subscription.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Subscription.t;
}

class SubscriptionRepository {
  const SubscriptionRepository._();

  /// Returns a list of [Subscription]s matching the given query parameters.
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
  Future<List<Subscription>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SubscriptionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Subscription>(
      where: where?.call(Subscription.t),
      orderBy: orderBy?.call(Subscription.t),
      orderByList: orderByList?.call(Subscription.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Subscription] matching the given query parameters.
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
  Future<Subscription?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionTable>? where,
    int? offset,
    _i1.OrderByBuilder<SubscriptionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Subscription>(
      where: where?.call(Subscription.t),
      orderBy: orderBy?.call(Subscription.t),
      orderByList: orderByList?.call(Subscription.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Subscription] by its [id] or null if no such row exists.
  Future<Subscription?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Subscription>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Subscription]s in the list and returns the inserted rows.
  ///
  /// The returned [Subscription]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Subscription>> insert(
    _i1.Session session,
    List<Subscription> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Subscription>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Subscription] and returns the inserted row.
  ///
  /// The returned [Subscription] will have its `id` field set.
  Future<Subscription> insertRow(
    _i1.Session session,
    Subscription row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Subscription>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Subscription]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Subscription>> update(
    _i1.Session session,
    List<Subscription> rows, {
    _i1.ColumnSelections<SubscriptionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Subscription>(
      rows,
      columns: columns?.call(Subscription.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Subscription]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Subscription> updateRow(
    _i1.Session session,
    Subscription row, {
    _i1.ColumnSelections<SubscriptionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Subscription>(
      row,
      columns: columns?.call(Subscription.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Subscription]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Subscription>> delete(
    _i1.Session session,
    List<Subscription> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Subscription>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Subscription].
  Future<Subscription> deleteRow(
    _i1.Session session,
    Subscription row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Subscription>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Subscription>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<SubscriptionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Subscription>(
      where: where(Subscription.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Subscription>(
      where: where?.call(Subscription.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
