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

abstract class AuthProvider implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  String provider;

  String providerUid;

  DateTime createdAt;

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
