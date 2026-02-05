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

abstract class UserSession implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
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
