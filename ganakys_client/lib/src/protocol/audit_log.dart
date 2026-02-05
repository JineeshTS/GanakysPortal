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

abstract class AuditLog implements _i1.SerializableModel {
  AuditLog._({
    this.id,
    this.userId,
    required this.action,
    required this.entityType,
    this.entityId,
    this.oldValue,
    this.newValue,
    this.ipAddress,
    required this.createdAt,
  });

  factory AuditLog({
    int? id,
    int? userId,
    required String action,
    required String entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    required DateTime createdAt,
  }) = _AuditLogImpl;

  factory AuditLog.fromJson(Map<String, dynamic> jsonSerialization) {
    return AuditLog(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int?,
      action: jsonSerialization['action'] as String,
      entityType: jsonSerialization['entityType'] as String,
      entityId: jsonSerialization['entityId'] as String?,
      oldValue: jsonSerialization['oldValue'] as String?,
      newValue: jsonSerialization['newValue'] as String?,
      ipAddress: jsonSerialization['ipAddress'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int? userId;

  String action;

  String entityType;

  String? entityId;

  String? oldValue;

  String? newValue;

  String? ipAddress;

  DateTime createdAt;

  /// Returns a shallow copy of this [AuditLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  AuditLog copyWith({
    int? id,
    int? userId,
    String? action,
    String? entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'action': action,
      'entityType': entityType,
      if (entityId != null) 'entityId': entityId,
      if (oldValue != null) 'oldValue': oldValue,
      if (newValue != null) 'newValue': newValue,
      if (ipAddress != null) 'ipAddress': ipAddress,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AuditLogImpl extends AuditLog {
  _AuditLogImpl({
    int? id,
    int? userId,
    required String action,
    required String entityType,
    String? entityId,
    String? oldValue,
    String? newValue,
    String? ipAddress,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          action: action,
          entityType: entityType,
          entityId: entityId,
          oldValue: oldValue,
          newValue: newValue,
          ipAddress: ipAddress,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [AuditLog]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  AuditLog copyWith({
    Object? id = _Undefined,
    Object? userId = _Undefined,
    String? action,
    String? entityType,
    Object? entityId = _Undefined,
    Object? oldValue = _Undefined,
    Object? newValue = _Undefined,
    Object? ipAddress = _Undefined,
    DateTime? createdAt,
  }) {
    return AuditLog(
      id: id is int? ? id : this.id,
      userId: userId is int? ? userId : this.userId,
      action: action ?? this.action,
      entityType: entityType ?? this.entityType,
      entityId: entityId is String? ? entityId : this.entityId,
      oldValue: oldValue is String? ? oldValue : this.oldValue,
      newValue: newValue is String? ? newValue : this.newValue,
      ipAddress: ipAddress is String? ? ipAddress : this.ipAddress,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
