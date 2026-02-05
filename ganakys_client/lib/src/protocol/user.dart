/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod_client/serverpod_client.dart' as _i1;

abstract class User implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
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
