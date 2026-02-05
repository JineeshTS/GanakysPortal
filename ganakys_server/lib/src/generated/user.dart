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

abstract class User implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  User._({
    this.id,
    required this.email,
    required this.name,
    this.avatarUrl,
    String? role,
    this.bio,
    String? subscriptionStatus,
    this.subscriptionExpiresAt,
    bool? emailVerified,
    this.emailVerificationToken,
    this.passwordHash,
    this.passwordResetToken,
    this.passwordResetExpiresAt,
    String? locale,
    this.passwordHistory,
    this.totpSecret,
    bool? totpEnabled,
    this.recoveryCodes,
    int? failedLoginCount,
    this.lockedUntil,
    this.lastLoginAt,
    this.lastLoginIp,
    int? loginCount,
    this.deletionRequestedAt,
    bool? isActive,
    required this.createdAt,
    required this.updatedAt,
  })  : role = role ?? 'student',
        subscriptionStatus = subscriptionStatus ?? 'free',
        emailVerified = emailVerified ?? false,
        locale = locale ?? 'en',
        totpEnabled = totpEnabled ?? false,
        failedLoginCount = failedLoginCount ?? 0,
        loginCount = loginCount ?? 0,
        isActive = isActive ?? true;

  factory User({
    int? id,
    required String email,
    required String name,
    String? avatarUrl,
    String? role,
    String? bio,
    String? subscriptionStatus,
    DateTime? subscriptionExpiresAt,
    bool? emailVerified,
    String? emailVerificationToken,
    String? passwordHash,
    String? passwordResetToken,
    DateTime? passwordResetExpiresAt,
    String? locale,
    String? passwordHistory,
    String? totpSecret,
    bool? totpEnabled,
    String? recoveryCodes,
    int? failedLoginCount,
    DateTime? lockedUntil,
    DateTime? lastLoginAt,
    String? lastLoginIp,
    int? loginCount,
    DateTime? deletionRequestedAt,
    bool? isActive,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _UserImpl;

  factory User.fromJson(Map<String, dynamic> jsonSerialization) {
    return User(
      id: jsonSerialization['id'] as int?,
      email: jsonSerialization['email'] as String,
      name: jsonSerialization['name'] as String,
      avatarUrl: jsonSerialization['avatarUrl'] as String?,
      role: jsonSerialization['role'] as String,
      bio: jsonSerialization['bio'] as String?,
      subscriptionStatus: jsonSerialization['subscriptionStatus'] as String,
      subscriptionExpiresAt: jsonSerialization['subscriptionExpiresAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['subscriptionExpiresAt']),
      emailVerified: jsonSerialization['emailVerified'] as bool,
      emailVerificationToken:
          jsonSerialization['emailVerificationToken'] as String?,
      passwordHash: jsonSerialization['passwordHash'] as String?,
      passwordResetToken: jsonSerialization['passwordResetToken'] as String?,
      passwordResetExpiresAt:
          jsonSerialization['passwordResetExpiresAt'] == null
              ? null
              : _i1.DateTimeJsonExtension.fromJson(
                  jsonSerialization['passwordResetExpiresAt']),
      locale: jsonSerialization['locale'] as String,
      passwordHistory: jsonSerialization['passwordHistory'] as String?,
      totpSecret: jsonSerialization['totpSecret'] as String?,
      totpEnabled: jsonSerialization['totpEnabled'] as bool,
      recoveryCodes: jsonSerialization['recoveryCodes'] as String?,
      failedLoginCount: jsonSerialization['failedLoginCount'] as int,
      lockedUntil: jsonSerialization['lockedUntil'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['lockedUntil']),
      lastLoginAt: jsonSerialization['lastLoginAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['lastLoginAt']),
      lastLoginIp: jsonSerialization['lastLoginIp'] as String?,
      loginCount: jsonSerialization['loginCount'] as int,
      deletionRequestedAt: jsonSerialization['deletionRequestedAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(
              jsonSerialization['deletionRequestedAt']),
      isActive: jsonSerialization['isActive'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = UserTable();

  static const db = UserRepository._();

  @override
  int? id;

  String email;

  String name;

  String? avatarUrl;

  String role;

  String? bio;

  String subscriptionStatus;

  DateTime? subscriptionExpiresAt;

  bool emailVerified;

  String? emailVerificationToken;

  String? passwordHash;

  String? passwordResetToken;

  DateTime? passwordResetExpiresAt;

  String locale;

  String? passwordHistory;

  String? totpSecret;

  bool totpEnabled;

  String? recoveryCodes;

  int failedLoginCount;

  DateTime? lockedUntil;

  DateTime? lastLoginAt;

  String? lastLoginIp;

  int loginCount;

  DateTime? deletionRequestedAt;

  bool isActive;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [User]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  User copyWith({
    int? id,
    String? email,
    String? name,
    String? avatarUrl,
    String? role,
    String? bio,
    String? subscriptionStatus,
    DateTime? subscriptionExpiresAt,
    bool? emailVerified,
    String? emailVerificationToken,
    String? passwordHash,
    String? passwordResetToken,
    DateTime? passwordResetExpiresAt,
    String? locale,
    String? passwordHistory,
    String? totpSecret,
    bool? totpEnabled,
    String? recoveryCodes,
    int? failedLoginCount,
    DateTime? lockedUntil,
    DateTime? lastLoginAt,
    String? lastLoginIp,
    int? loginCount,
    DateTime? deletionRequestedAt,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'email': email,
      'name': name,
      if (avatarUrl != null) 'avatarUrl': avatarUrl,
      'role': role,
      if (bio != null) 'bio': bio,
      'subscriptionStatus': subscriptionStatus,
      if (subscriptionExpiresAt != null)
        'subscriptionExpiresAt': subscriptionExpiresAt?.toJson(),
      'emailVerified': emailVerified,
      if (emailVerificationToken != null)
        'emailVerificationToken': emailVerificationToken,
      if (passwordHash != null) 'passwordHash': passwordHash,
      if (passwordResetToken != null) 'passwordResetToken': passwordResetToken,
      if (passwordResetExpiresAt != null)
        'passwordResetExpiresAt': passwordResetExpiresAt?.toJson(),
      'locale': locale,
      if (passwordHistory != null) 'passwordHistory': passwordHistory,
      if (totpSecret != null) 'totpSecret': totpSecret,
      'totpEnabled': totpEnabled,
      if (recoveryCodes != null) 'recoveryCodes': recoveryCodes,
      'failedLoginCount': failedLoginCount,
      if (lockedUntil != null) 'lockedUntil': lockedUntil?.toJson(),
      if (lastLoginAt != null) 'lastLoginAt': lastLoginAt?.toJson(),
      if (lastLoginIp != null) 'lastLoginIp': lastLoginIp,
      'loginCount': loginCount,
      if (deletionRequestedAt != null)
        'deletionRequestedAt': deletionRequestedAt?.toJson(),
      'isActive': isActive,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'email': email,
      'name': name,
      if (avatarUrl != null) 'avatarUrl': avatarUrl,
      'role': role,
      if (bio != null) 'bio': bio,
      'subscriptionStatus': subscriptionStatus,
      if (subscriptionExpiresAt != null)
        'subscriptionExpiresAt': subscriptionExpiresAt?.toJson(),
      'emailVerified': emailVerified,
      if (emailVerificationToken != null)
        'emailVerificationToken': emailVerificationToken,
      if (passwordHash != null) 'passwordHash': passwordHash,
      if (passwordResetToken != null) 'passwordResetToken': passwordResetToken,
      if (passwordResetExpiresAt != null)
        'passwordResetExpiresAt': passwordResetExpiresAt?.toJson(),
      'locale': locale,
      if (passwordHistory != null) 'passwordHistory': passwordHistory,
      if (totpSecret != null) 'totpSecret': totpSecret,
      'totpEnabled': totpEnabled,
      if (recoveryCodes != null) 'recoveryCodes': recoveryCodes,
      'failedLoginCount': failedLoginCount,
      if (lockedUntil != null) 'lockedUntil': lockedUntil?.toJson(),
      if (lastLoginAt != null) 'lastLoginAt': lastLoginAt?.toJson(),
      if (lastLoginIp != null) 'lastLoginIp': lastLoginIp,
      'loginCount': loginCount,
      if (deletionRequestedAt != null)
        'deletionRequestedAt': deletionRequestedAt?.toJson(),
      'isActive': isActive,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static UserInclude include() {
    return UserInclude._();
  }

  static UserIncludeList includeList({
    _i1.WhereExpressionBuilder<UserTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<UserTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserTable>? orderByList,
    UserInclude? include,
  }) {
    return UserIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(User.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(User.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _UserImpl extends User {
  _UserImpl({
    int? id,
    required String email,
    required String name,
    String? avatarUrl,
    String? role,
    String? bio,
    String? subscriptionStatus,
    DateTime? subscriptionExpiresAt,
    bool? emailVerified,
    String? emailVerificationToken,
    String? passwordHash,
    String? passwordResetToken,
    DateTime? passwordResetExpiresAt,
    String? locale,
    String? passwordHistory,
    String? totpSecret,
    bool? totpEnabled,
    String? recoveryCodes,
    int? failedLoginCount,
    DateTime? lockedUntil,
    DateTime? lastLoginAt,
    String? lastLoginIp,
    int? loginCount,
    DateTime? deletionRequestedAt,
    bool? isActive,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          email: email,
          name: name,
          avatarUrl: avatarUrl,
          role: role,
          bio: bio,
          subscriptionStatus: subscriptionStatus,
          subscriptionExpiresAt: subscriptionExpiresAt,
          emailVerified: emailVerified,
          emailVerificationToken: emailVerificationToken,
          passwordHash: passwordHash,
          passwordResetToken: passwordResetToken,
          passwordResetExpiresAt: passwordResetExpiresAt,
          locale: locale,
          passwordHistory: passwordHistory,
          totpSecret: totpSecret,
          totpEnabled: totpEnabled,
          recoveryCodes: recoveryCodes,
          failedLoginCount: failedLoginCount,
          lockedUntil: lockedUntil,
          lastLoginAt: lastLoginAt,
          lastLoginIp: lastLoginIp,
          loginCount: loginCount,
          deletionRequestedAt: deletionRequestedAt,
          isActive: isActive,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [User]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  User copyWith({
    Object? id = _Undefined,
    String? email,
    String? name,
    Object? avatarUrl = _Undefined,
    String? role,
    Object? bio = _Undefined,
    String? subscriptionStatus,
    Object? subscriptionExpiresAt = _Undefined,
    bool? emailVerified,
    Object? emailVerificationToken = _Undefined,
    Object? passwordHash = _Undefined,
    Object? passwordResetToken = _Undefined,
    Object? passwordResetExpiresAt = _Undefined,
    String? locale,
    Object? passwordHistory = _Undefined,
    Object? totpSecret = _Undefined,
    bool? totpEnabled,
    Object? recoveryCodes = _Undefined,
    int? failedLoginCount,
    Object? lockedUntil = _Undefined,
    Object? lastLoginAt = _Undefined,
    Object? lastLoginIp = _Undefined,
    int? loginCount,
    Object? deletionRequestedAt = _Undefined,
    bool? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id is int? ? id : this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      avatarUrl: avatarUrl is String? ? avatarUrl : this.avatarUrl,
      role: role ?? this.role,
      bio: bio is String? ? bio : this.bio,
      subscriptionStatus: subscriptionStatus ?? this.subscriptionStatus,
      subscriptionExpiresAt: subscriptionExpiresAt is DateTime?
          ? subscriptionExpiresAt
          : this.subscriptionExpiresAt,
      emailVerified: emailVerified ?? this.emailVerified,
      emailVerificationToken: emailVerificationToken is String?
          ? emailVerificationToken
          : this.emailVerificationToken,
      passwordHash: passwordHash is String? ? passwordHash : this.passwordHash,
      passwordResetToken: passwordResetToken is String?
          ? passwordResetToken
          : this.passwordResetToken,
      passwordResetExpiresAt: passwordResetExpiresAt is DateTime?
          ? passwordResetExpiresAt
          : this.passwordResetExpiresAt,
      locale: locale ?? this.locale,
      passwordHistory:
          passwordHistory is String? ? passwordHistory : this.passwordHistory,
      totpSecret: totpSecret is String? ? totpSecret : this.totpSecret,
      totpEnabled: totpEnabled ?? this.totpEnabled,
      recoveryCodes:
          recoveryCodes is String? ? recoveryCodes : this.recoveryCodes,
      failedLoginCount: failedLoginCount ?? this.failedLoginCount,
      lockedUntil: lockedUntil is DateTime? ? lockedUntil : this.lockedUntil,
      lastLoginAt: lastLoginAt is DateTime? ? lastLoginAt : this.lastLoginAt,
      lastLoginIp: lastLoginIp is String? ? lastLoginIp : this.lastLoginIp,
      loginCount: loginCount ?? this.loginCount,
      deletionRequestedAt: deletionRequestedAt is DateTime?
          ? deletionRequestedAt
          : this.deletionRequestedAt,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class UserTable extends _i1.Table<int?> {
  UserTable({super.tableRelation}) : super(tableName: 'users') {
    email = _i1.ColumnString(
      'email',
      this,
    );
    name = _i1.ColumnString(
      'name',
      this,
    );
    avatarUrl = _i1.ColumnString(
      'avatarUrl',
      this,
    );
    role = _i1.ColumnString(
      'role',
      this,
      hasDefault: true,
    );
    bio = _i1.ColumnString(
      'bio',
      this,
    );
    subscriptionStatus = _i1.ColumnString(
      'subscriptionStatus',
      this,
      hasDefault: true,
    );
    subscriptionExpiresAt = _i1.ColumnDateTime(
      'subscriptionExpiresAt',
      this,
    );
    emailVerified = _i1.ColumnBool(
      'emailVerified',
      this,
      hasDefault: true,
    );
    emailVerificationToken = _i1.ColumnString(
      'emailVerificationToken',
      this,
    );
    passwordHash = _i1.ColumnString(
      'passwordHash',
      this,
    );
    passwordResetToken = _i1.ColumnString(
      'passwordResetToken',
      this,
    );
    passwordResetExpiresAt = _i1.ColumnDateTime(
      'passwordResetExpiresAt',
      this,
    );
    locale = _i1.ColumnString(
      'locale',
      this,
      hasDefault: true,
    );
    passwordHistory = _i1.ColumnString(
      'passwordHistory',
      this,
    );
    totpSecret = _i1.ColumnString(
      'totpSecret',
      this,
    );
    totpEnabled = _i1.ColumnBool(
      'totpEnabled',
      this,
      hasDefault: true,
    );
    recoveryCodes = _i1.ColumnString(
      'recoveryCodes',
      this,
    );
    failedLoginCount = _i1.ColumnInt(
      'failedLoginCount',
      this,
      hasDefault: true,
    );
    lockedUntil = _i1.ColumnDateTime(
      'lockedUntil',
      this,
    );
    lastLoginAt = _i1.ColumnDateTime(
      'lastLoginAt',
      this,
    );
    lastLoginIp = _i1.ColumnString(
      'lastLoginIp',
      this,
    );
    loginCount = _i1.ColumnInt(
      'loginCount',
      this,
      hasDefault: true,
    );
    deletionRequestedAt = _i1.ColumnDateTime(
      'deletionRequestedAt',
      this,
    );
    isActive = _i1.ColumnBool(
      'isActive',
      this,
      hasDefault: true,
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

  late final _i1.ColumnString email;

  late final _i1.ColumnString name;

  late final _i1.ColumnString avatarUrl;

  late final _i1.ColumnString role;

  late final _i1.ColumnString bio;

  late final _i1.ColumnString subscriptionStatus;

  late final _i1.ColumnDateTime subscriptionExpiresAt;

  late final _i1.ColumnBool emailVerified;

  late final _i1.ColumnString emailVerificationToken;

  late final _i1.ColumnString passwordHash;

  late final _i1.ColumnString passwordResetToken;

  late final _i1.ColumnDateTime passwordResetExpiresAt;

  late final _i1.ColumnString locale;

  late final _i1.ColumnString passwordHistory;

  late final _i1.ColumnString totpSecret;

  late final _i1.ColumnBool totpEnabled;

  late final _i1.ColumnString recoveryCodes;

  late final _i1.ColumnInt failedLoginCount;

  late final _i1.ColumnDateTime lockedUntil;

  late final _i1.ColumnDateTime lastLoginAt;

  late final _i1.ColumnString lastLoginIp;

  late final _i1.ColumnInt loginCount;

  late final _i1.ColumnDateTime deletionRequestedAt;

  late final _i1.ColumnBool isActive;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        email,
        name,
        avatarUrl,
        role,
        bio,
        subscriptionStatus,
        subscriptionExpiresAt,
        emailVerified,
        emailVerificationToken,
        passwordHash,
        passwordResetToken,
        passwordResetExpiresAt,
        locale,
        passwordHistory,
        totpSecret,
        totpEnabled,
        recoveryCodes,
        failedLoginCount,
        lockedUntil,
        lastLoginAt,
        lastLoginIp,
        loginCount,
        deletionRequestedAt,
        isActive,
        createdAt,
        updatedAt,
      ];
}

class UserInclude extends _i1.IncludeObject {
  UserInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => User.t;
}

class UserIncludeList extends _i1.IncludeList {
  UserIncludeList._({
    _i1.WhereExpressionBuilder<UserTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(User.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => User.t;
}

class UserRepository {
  const UserRepository._();

  /// Returns a list of [User]s matching the given query parameters.
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
  Future<List<User>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<UserTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<User>(
      where: where?.call(User.t),
      orderBy: orderBy?.call(User.t),
      orderByList: orderByList?.call(User.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [User] matching the given query parameters.
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
  Future<User?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserTable>? where,
    int? offset,
    _i1.OrderByBuilder<UserTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<UserTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<User>(
      where: where?.call(User.t),
      orderBy: orderBy?.call(User.t),
      orderByList: orderByList?.call(User.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [User] by its [id] or null if no such row exists.
  Future<User?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<User>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [User]s in the list and returns the inserted rows.
  ///
  /// The returned [User]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<User>> insert(
    _i1.Session session,
    List<User> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<User>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [User] and returns the inserted row.
  ///
  /// The returned [User] will have its `id` field set.
  Future<User> insertRow(
    _i1.Session session,
    User row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<User>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [User]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<User>> update(
    _i1.Session session,
    List<User> rows, {
    _i1.ColumnSelections<UserTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<User>(
      rows,
      columns: columns?.call(User.t),
      transaction: transaction,
    );
  }

  /// Updates a single [User]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<User> updateRow(
    _i1.Session session,
    User row, {
    _i1.ColumnSelections<UserTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<User>(
      row,
      columns: columns?.call(User.t),
      transaction: transaction,
    );
  }

  /// Deletes all [User]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<User>> delete(
    _i1.Session session,
    List<User> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<User>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [User].
  Future<User> deleteRow(
    _i1.Session session,
    User row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<User>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<User>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<UserTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<User>(
      where: where(User.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<UserTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<User>(
      where: where?.call(User.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
