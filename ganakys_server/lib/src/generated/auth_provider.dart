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

abstract class AuthProvider
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  AuthProvider._({
    this.id,
    required this.userId,
    required this.provider,
    required this.providerUid,
    required this.createdAt,
  });

  factory AuthProvider({
    int? id,
    required int userId,
    required String provider,
    required String providerUid,
    required DateTime createdAt,
  }) = _AuthProviderImpl;

  factory AuthProvider.fromJson(Map<String, dynamic> jsonSerialization) {
    return AuthProvider(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      provider: jsonSerialization['provider'] as String,
      providerUid: jsonSerialization['providerUid'] as String,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = AuthProviderTable();

  static const db = AuthProviderRepository._();

  @override
  int? id;

  int userId;

  String provider;

  String providerUid;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [AuthProvider]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  AuthProvider copyWith({
    int? id,
    int? userId,
    String? provider,
    String? providerUid,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'provider': provider,
      'providerUid': providerUid,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'provider': provider,
      'providerUid': providerUid,
      'createdAt': createdAt.toJson(),
    };
  }

  static AuthProviderInclude include() {
    return AuthProviderInclude._();
  }

  static AuthProviderIncludeList includeList({
    _i1.WhereExpressionBuilder<AuthProviderTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AuthProviderTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuthProviderTable>? orderByList,
    AuthProviderInclude? include,
  }) {
    return AuthProviderIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(AuthProvider.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(AuthProvider.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AuthProviderImpl extends AuthProvider {
  _AuthProviderImpl({
    int? id,
    required int userId,
    required String provider,
    required String providerUid,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          provider: provider,
          providerUid: providerUid,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [AuthProvider]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  AuthProvider copyWith({
    Object? id = _Undefined,
    int? userId,
    String? provider,
    String? providerUid,
    DateTime? createdAt,
  }) {
    return AuthProvider(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      provider: provider ?? this.provider,
      providerUid: providerUid ?? this.providerUid,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class AuthProviderTable extends _i1.Table<int?> {
  AuthProviderTable({super.tableRelation})
      : super(tableName: 'auth_providers') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    provider = _i1.ColumnString(
      'provider',
      this,
    );
    providerUid = _i1.ColumnString(
      'providerUid',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString provider;

  late final _i1.ColumnString providerUid;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        provider,
        providerUid,
        createdAt,
      ];
}

class AuthProviderInclude extends _i1.IncludeObject {
  AuthProviderInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => AuthProvider.t;
}

class AuthProviderIncludeList extends _i1.IncludeList {
  AuthProviderIncludeList._({
    _i1.WhereExpressionBuilder<AuthProviderTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(AuthProvider.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => AuthProvider.t;
}

class AuthProviderRepository {
  const AuthProviderRepository._();

  /// Returns a list of [AuthProvider]s matching the given query parameters.
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
  Future<List<AuthProvider>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuthProviderTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<AuthProviderTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuthProviderTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<AuthProvider>(
      where: where?.call(AuthProvider.t),
      orderBy: orderBy?.call(AuthProvider.t),
      orderByList: orderByList?.call(AuthProvider.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [AuthProvider] matching the given query parameters.
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
  Future<AuthProvider?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuthProviderTable>? where,
    int? offset,
    _i1.OrderByBuilder<AuthProviderTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<AuthProviderTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<AuthProvider>(
      where: where?.call(AuthProvider.t),
      orderBy: orderBy?.call(AuthProvider.t),
      orderByList: orderByList?.call(AuthProvider.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [AuthProvider] by its [id] or null if no such row exists.
  Future<AuthProvider?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<AuthProvider>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [AuthProvider]s in the list and returns the inserted rows.
  ///
  /// The returned [AuthProvider]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<AuthProvider>> insert(
    _i1.Session session,
    List<AuthProvider> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<AuthProvider>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [AuthProvider] and returns the inserted row.
  ///
  /// The returned [AuthProvider] will have its `id` field set.
  Future<AuthProvider> insertRow(
    _i1.Session session,
    AuthProvider row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<AuthProvider>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [AuthProvider]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<AuthProvider>> update(
    _i1.Session session,
    List<AuthProvider> rows, {
    _i1.ColumnSelections<AuthProviderTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<AuthProvider>(
      rows,
      columns: columns?.call(AuthProvider.t),
      transaction: transaction,
    );
  }

  /// Updates a single [AuthProvider]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<AuthProvider> updateRow(
    _i1.Session session,
    AuthProvider row, {
    _i1.ColumnSelections<AuthProviderTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<AuthProvider>(
      row,
      columns: columns?.call(AuthProvider.t),
      transaction: transaction,
    );
  }

  /// Deletes all [AuthProvider]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<AuthProvider>> delete(
    _i1.Session session,
    List<AuthProvider> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<AuthProvider>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [AuthProvider].
  Future<AuthProvider> deleteRow(
    _i1.Session session,
    AuthProvider row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<AuthProvider>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<AuthProvider>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<AuthProviderTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<AuthProvider>(
      where: where(AuthProvider.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<AuthProviderTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<AuthProvider>(
      where: where?.call(AuthProvider.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
