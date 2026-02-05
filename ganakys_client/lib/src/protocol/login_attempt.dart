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

abstract class LoginAttempt implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String email;

  String ipAddress;

  bool success;

  String? failureReason;

  String? userAgent;

  String? countryCode;

  DateTime createdAt;

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
