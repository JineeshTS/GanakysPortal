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

abstract class LoginAttempt
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  LoginAttempt._({
    this.id,
    required this.email,
    required this.ipAddress,
    required this.success,
    this.failureReason,
    this.userAgent,
    this.countryCode,
    required this.createdAt,
  });

  factory LoginAttempt({
    int? id,
    required String email,
    required String ipAddress,
    required bool success,
    String? failureReason,
    String? userAgent,
    String? countryCode,
    required DateTime createdAt,
  }) = _LoginAttemptImpl;

  factory LoginAttempt.fromJson(Map<String, dynamic> jsonSerialization) {
    return LoginAttempt(
      id: jsonSerialization['id'] as int?,
      email: jsonSerialization['email'] as String,
      ipAddress: jsonSerialization['ipAddress'] as String,
      success: jsonSerialization['success'] as bool,
      failureReason: jsonSerialization['failureReason'] as String?,
      userAgent: jsonSerialization['userAgent'] as String?,
      countryCode: jsonSerialization['countryCode'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = LoginAttemptTable();

  static const db = LoginAttemptRepository._();

  @override
  int? id;

  String email;

  String ipAddress;

  bool success;

  String? failureReason;

  String? userAgent;

  String? countryCode;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [LoginAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  LoginAttempt copyWith({
    int? id,
    String? email,
    String? ipAddress,
    bool? success,
    String? failureReason,
    String? userAgent,
    String? countryCode,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'email': email,
      'ipAddress': ipAddress,
      'success': success,
      if (failureReason != null) 'failureReason': failureReason,
      if (userAgent != null) 'userAgent': userAgent,
      if (countryCode != null) 'countryCode': countryCode,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'email': email,
      'ipAddress': ipAddress,
      'success': success,
      if (failureReason != null) 'failureReason': failureReason,
      if (userAgent != null) 'userAgent': userAgent,
      if (countryCode != null) 'countryCode': countryCode,
      'createdAt': createdAt.toJson(),
    };
  }

  static LoginAttemptInclude include() {
    return LoginAttemptInclude._();
  }

  static LoginAttemptIncludeList includeList({
    _i1.WhereExpressionBuilder<LoginAttemptTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LoginAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LoginAttemptTable>? orderByList,
    LoginAttemptInclude? include,
  }) {
    return LoginAttemptIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(LoginAttempt.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(LoginAttempt.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LoginAttemptImpl extends LoginAttempt {
  _LoginAttemptImpl({
    int? id,
    required String email,
    required String ipAddress,
    required bool success,
    String? failureReason,
    String? userAgent,
    String? countryCode,
    required DateTime createdAt,
  }) : super._(
          id: id,
          email: email,
          ipAddress: ipAddress,
          success: success,
          failureReason: failureReason,
          userAgent: userAgent,
          countryCode: countryCode,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [LoginAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  LoginAttempt copyWith({
    Object? id = _Undefined,
    String? email,
    String? ipAddress,
    bool? success,
    Object? failureReason = _Undefined,
    Object? userAgent = _Undefined,
    Object? countryCode = _Undefined,
    DateTime? createdAt,
  }) {
    return LoginAttempt(
      id: id is int? ? id : this.id,
      email: email ?? this.email,
      ipAddress: ipAddress ?? this.ipAddress,
      success: success ?? this.success,
      failureReason:
          failureReason is String? ? failureReason : this.failureReason,
      userAgent: userAgent is String? ? userAgent : this.userAgent,
      countryCode: countryCode is String? ? countryCode : this.countryCode,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class LoginAttemptTable extends _i1.Table<int?> {
  LoginAttemptTable({super.tableRelation})
      : super(tableName: 'login_attempts') {
    email = _i1.ColumnString(
      'email',
      this,
    );
    ipAddress = _i1.ColumnString(
      'ipAddress',
      this,
    );
    success = _i1.ColumnBool(
      'success',
      this,
    );
    failureReason = _i1.ColumnString(
      'failureReason',
      this,
    );
    userAgent = _i1.ColumnString(
      'userAgent',
      this,
    );
    countryCode = _i1.ColumnString(
      'countryCode',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnString email;

  late final _i1.ColumnString ipAddress;

  late final _i1.ColumnBool success;

  late final _i1.ColumnString failureReason;

  late final _i1.ColumnString userAgent;

  late final _i1.ColumnString countryCode;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        email,
        ipAddress,
        success,
        failureReason,
        userAgent,
        countryCode,
        createdAt,
      ];
}

class LoginAttemptInclude extends _i1.IncludeObject {
  LoginAttemptInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => LoginAttempt.t;
}

class LoginAttemptIncludeList extends _i1.IncludeList {
  LoginAttemptIncludeList._({
    _i1.WhereExpressionBuilder<LoginAttemptTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(LoginAttempt.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => LoginAttempt.t;
}

class LoginAttemptRepository {
  const LoginAttemptRepository._();

  /// Returns a list of [LoginAttempt]s matching the given query parameters.
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
  Future<List<LoginAttempt>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LoginAttemptTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LoginAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LoginAttemptTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<LoginAttempt>(
      where: where?.call(LoginAttempt.t),
      orderBy: orderBy?.call(LoginAttempt.t),
      orderByList: orderByList?.call(LoginAttempt.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [LoginAttempt] matching the given query parameters.
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
  Future<LoginAttempt?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LoginAttemptTable>? where,
    int? offset,
    _i1.OrderByBuilder<LoginAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LoginAttemptTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<LoginAttempt>(
      where: where?.call(LoginAttempt.t),
      orderBy: orderBy?.call(LoginAttempt.t),
      orderByList: orderByList?.call(LoginAttempt.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [LoginAttempt] by its [id] or null if no such row exists.
  Future<LoginAttempt?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<LoginAttempt>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [LoginAttempt]s in the list and returns the inserted rows.
  ///
  /// The returned [LoginAttempt]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<LoginAttempt>> insert(
    _i1.Session session,
    List<LoginAttempt> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<LoginAttempt>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [LoginAttempt] and returns the inserted row.
  ///
  /// The returned [LoginAttempt] will have its `id` field set.
  Future<LoginAttempt> insertRow(
    _i1.Session session,
    LoginAttempt row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<LoginAttempt>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [LoginAttempt]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<LoginAttempt>> update(
    _i1.Session session,
    List<LoginAttempt> rows, {
    _i1.ColumnSelections<LoginAttemptTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<LoginAttempt>(
      rows,
      columns: columns?.call(LoginAttempt.t),
      transaction: transaction,
    );
  }

  /// Updates a single [LoginAttempt]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<LoginAttempt> updateRow(
    _i1.Session session,
    LoginAttempt row, {
    _i1.ColumnSelections<LoginAttemptTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<LoginAttempt>(
      row,
      columns: columns?.call(LoginAttempt.t),
      transaction: transaction,
    );
  }

  /// Deletes all [LoginAttempt]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<LoginAttempt>> delete(
    _i1.Session session,
    List<LoginAttempt> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<LoginAttempt>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [LoginAttempt].
  Future<LoginAttempt> deleteRow(
    _i1.Session session,
    LoginAttempt row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<LoginAttempt>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<LoginAttempt>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<LoginAttemptTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<LoginAttempt>(
      where: where(LoginAttempt.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LoginAttemptTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<LoginAttempt>(
      where: where?.call(LoginAttempt.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
