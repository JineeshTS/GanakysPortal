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

abstract class UserSession
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  UserSession._({
    this.id,
    required this.userId,
    required this.refreshTokenHash,
    this.deviceInfo,
    this.ipAddress,
    this.userAgentFingerprint,
    required this.lastActiveAt,
    required this.expiresAt,
    bool? isRevoked,
    required this.createdAt,
  }) : isRevoked = isRevoked ?? false;

  factory UserSession({
    int? id,
    required int userId,
    required String refreshTokenHash,
    String? deviceInfo,
    String? ipAddress,
    String? userAgentFingerprint,
    required DateTime lastActiveAt,
    required DateTime expiresAt,
    bool? isRevoked,
    required DateTime createdAt,
  }) = _UserSessionImpl;

  factory UserSession.fromJson(Map<String, dynamic> jsonSerialization) {
    return UserSession(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      refreshTokenHash: jsonSerialization['refreshTokenHash'] as String,
      deviceInfo: jsonSerialization['deviceInfo'] as String?,
      ipAddress: jsonSerialization['ipAddress'] as String?,
      userAgentFingerprint:
          jsonSerialization['userAgentFingerprint'] as String?,
      lastActiveAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['lastActiveAt']),
      expiresAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['expiresAt']),
      isRevoked: jsonSerialization['isRevoked'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = UserSessionTable();

  static const db = UserSessionRepository._();

  @override
  int? id;

  int userId;

  String refreshTokenHash;

  String? deviceInfo;

  String? ipAddress;

  String? userAgentFingerprint;

  DateTime lastActiveAt;

  DateTime expiresAt;

  bool isRevoked;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [UserSession]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  UserSession copyWith({
    int? id,
    int? userId,
    String? refreshTokenHash,
    String? deviceInfo,
    String? ipAddress,
    String? userAgentFingerprint,
    DateTime? lastActiveAt,
    DateTime? expiresAt,
    bool? isRevoked,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'refreshTokenHash': refreshTokenHash,
      if (deviceInfo != null) 'deviceInfo': deviceInfo,
      if (ipAddress != null) 'ipAddress': ipAddress,
      if (userAgentFingerprint != null)
        'userAgentFingerprint': userAgentFingerprint,
      'lastActiveAt': lastActiveAt.toJson(),
      'expiresAt': expiresAt.toJson(),
      'isRevoked': isRevoked,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'refreshTokenHash': refreshTokenHash,
      if (deviceInfo != null) 'deviceInfo': deviceInfo,
      if (ipAddress != null) 'ipAddress': ipAddress,
      if (userAgentFingerprint != null)
        'userAgentFingerprint': userAgentFingerprint,
      'lastActiveAt': lastActiveAt.toJson(),
      'expiresAt': expiresAt.toJson(),
      'isRevoked': isRevoked,
      'createdAt': createdAt.toJson(),
    };
  }

  static UserSessionInclude include() {
    return UserSessionInclude._();
  }

  static UserSessionIncludeList includeList({
    _i1.WhereExpressionBuilder<UserSessionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<UserSessionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserSessionTable>? orderByList,
    UserSessionInclude? include,
  }) {
    return UserSessionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(UserSession.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(UserSession.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _UserSessionImpl extends UserSession {
  _UserSessionImpl({
    int? id,
    required int userId,
    required String refreshTokenHash,
    String? deviceInfo,
    String? ipAddress,
    String? userAgentFingerprint,
    required DateTime lastActiveAt,
    required DateTime expiresAt,
    bool? isRevoked,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          refreshTokenHash: refreshTokenHash,
          deviceInfo: deviceInfo,
          ipAddress: ipAddress,
          userAgentFingerprint: userAgentFingerprint,
          lastActiveAt: lastActiveAt,
          expiresAt: expiresAt,
          isRevoked: isRevoked,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [UserSession]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  UserSession copyWith({
    Object? id = _Undefined,
    int? userId,
    String? refreshTokenHash,
    Object? deviceInfo = _Undefined,
    Object? ipAddress = _Undefined,
    Object? userAgentFingerprint = _Undefined,
    DateTime? lastActiveAt,
    DateTime? expiresAt,
    bool? isRevoked,
    DateTime? createdAt,
  }) {
    return UserSession(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      refreshTokenHash: refreshTokenHash ?? this.refreshTokenHash,
      deviceInfo: deviceInfo is String? ? deviceInfo : this.deviceInfo,
      ipAddress: ipAddress is String? ? ipAddress : this.ipAddress,
      userAgentFingerprint: userAgentFingerprint is String?
          ? userAgentFingerprint
          : this.userAgentFingerprint,
      lastActiveAt: lastActiveAt ?? this.lastActiveAt,
      expiresAt: expiresAt ?? this.expiresAt,
      isRevoked: isRevoked ?? this.isRevoked,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class UserSessionTable extends _i1.Table<int?> {
  UserSessionTable({super.tableRelation}) : super(tableName: 'user_sessions') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    refreshTokenHash = _i1.ColumnString(
      'refreshTokenHash',
      this,
    );
    deviceInfo = _i1.ColumnString(
      'deviceInfo',
      this,
    );
    ipAddress = _i1.ColumnString(
      'ipAddress',
      this,
    );
    userAgentFingerprint = _i1.ColumnString(
      'userAgentFingerprint',
      this,
    );
    lastActiveAt = _i1.ColumnDateTime(
      'lastActiveAt',
      this,
    );
    expiresAt = _i1.ColumnDateTime(
      'expiresAt',
      this,
    );
    isRevoked = _i1.ColumnBool(
      'isRevoked',
      this,
      hasDefault: true,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString refreshTokenHash;

  late final _i1.ColumnString deviceInfo;

  late final _i1.ColumnString ipAddress;

  late final _i1.ColumnString userAgentFingerprint;

  late final _i1.ColumnDateTime lastActiveAt;

  late final _i1.ColumnDateTime expiresAt;

  late final _i1.ColumnBool isRevoked;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        refreshTokenHash,
        deviceInfo,
        ipAddress,
        userAgentFingerprint,
        lastActiveAt,
        expiresAt,
        isRevoked,
        createdAt,
      ];
}

class UserSessionInclude extends _i1.IncludeObject {
  UserSessionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => UserSession.t;
}

class UserSessionIncludeList extends _i1.IncludeList {
  UserSessionIncludeList._({
    _i1.WhereExpressionBuilder<UserSessionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(UserSession.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => UserSession.t;
}

class UserSessionRepository {
  const UserSessionRepository._();

  /// Returns a list of [UserSession]s matching the given query parameters.
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
  Future<List<UserSession>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserSessionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<UserSessionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserSessionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<UserSession>(
      where: where?.call(UserSession.t),
      orderBy: orderBy?.call(UserSession.t),
      orderByList: orderByList?.call(UserSession.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [UserSession] matching the given query parameters.
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
  Future<UserSession?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserSessionTable>? where,
    int? offset,
    _i1.OrderByBuilder<UserSessionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserSessionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<UserSession>(
      where: where?.call(UserSession.t),
      orderBy: orderBy?.call(UserSession.t),
      orderByList: orderByList?.call(UserSession.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [UserSession] by its [id] or null if no such row exists.
  Future<UserSession?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<UserSession>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [UserSession]s in the list and returns the inserted rows.
  ///
  /// The returned [UserSession]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<UserSession>> insert(
    _i1.Session session,
    List<UserSession> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<UserSession>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [UserSession] and returns the inserted row.
  ///
  /// The returned [UserSession] will have its `id` field set.
  Future<UserSession> insertRow(
    _i1.Session session,
    UserSession row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<UserSession>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [UserSession]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<UserSession>> update(
    _i1.Session session,
    List<UserSession> rows, {
    _i1.ColumnSelections<UserSessionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<UserSession>(
      rows,
      columns: columns?.call(UserSession.t),
      transaction: transaction,
    );
  }

  /// Updates a single [UserSession]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<UserSession> updateRow(
    _i1.Session session,
    UserSession row, {
    _i1.ColumnSelections<UserSessionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<UserSession>(
      row,
      columns: columns?.call(UserSession.t),
      transaction: transaction,
    );
  }

  /// Deletes all [UserSession]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<UserSession>> delete(
    _i1.Session session,
    List<UserSession> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<UserSession>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [UserSession].
  Future<UserSession> deleteRow(
    _i1.Session session,
    UserSession row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<UserSession>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<UserSession>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<UserSessionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<UserSession>(
      where: where(UserSession.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserSessionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<UserSession>(
      where: where?.call(UserSession.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
