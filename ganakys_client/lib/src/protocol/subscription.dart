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

abstract class Subscription implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
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
