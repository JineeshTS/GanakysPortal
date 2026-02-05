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

abstract class Payment implements _i1.SerializableModel {
  Payment._({
    this.id,
    required this.userId,
    this.planId,
    this.courseId,
    required this.amount,
    String? currency,
    String? status,
    required this.paymentGateway,
    this.gatewayPaymentId,
    this.gatewayOrderId,
    this.receiptUrl,
    required this.createdAt,
  })  : currency = currency ?? 'INR',
        status = status ?? 'pending';

  factory Payment({
    int? id,
    required int userId,
    int? planId,
    int? courseId,
    required double amount,
    String? currency,
    String? status,
    required String paymentGateway,
    String? gatewayPaymentId,
    String? gatewayOrderId,
    String? receiptUrl,
    required DateTime createdAt,
  }) = _PaymentImpl;

  factory Payment.fromJson(Map<String, dynamic> jsonSerialization) {
    return Payment(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      planId: jsonSerialization['planId'] as int?,
      courseId: jsonSerialization['courseId'] as int?,
      amount: (jsonSerialization['amount'] as num).toDouble(),
      currency: jsonSerialization['currency'] as String,
      status: jsonSerialization['status'] as String,
      paymentGateway: jsonSerialization['paymentGateway'] as String,
      gatewayPaymentId: jsonSerialization['gatewayPaymentId'] as String?,
      gatewayOrderId: jsonSerialization['gatewayOrderId'] as String?,
      receiptUrl: jsonSerialization['receiptUrl'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int? planId;

  int? courseId;

  double amount;

  String currency;

  String status;

  String paymentGateway;

  String? gatewayPaymentId;

  String? gatewayOrderId;

  String? receiptUrl;

  DateTime createdAt;

  /// Returns a shallow copy of this [Payment]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Payment copyWith({
    int? id,
    int? userId,
    int? planId,
    int? courseId,
    double? amount,
    String? currency,
    String? status,
    String? paymentGateway,
    String? gatewayPaymentId,
    String? gatewayOrderId,
    String? receiptUrl,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      if (planId != null) 'planId': planId,
      if (courseId != null) 'courseId': courseId,
      'amount': amount,
      'currency': currency,
      'status': status,
      'paymentGateway': paymentGateway,
      if (gatewayPaymentId != null) 'gatewayPaymentId': gatewayPaymentId,
      if (gatewayOrderId != null) 'gatewayOrderId': gatewayOrderId,
      if (receiptUrl != null) 'receiptUrl': receiptUrl,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _PaymentImpl extends Payment {
  _PaymentImpl({
    int? id,
    required int userId,
    int? planId,
    int? courseId,
    required double amount,
    String? currency,
    String? status,
    required String paymentGateway,
    String? gatewayPaymentId,
    String? gatewayOrderId,
    String? receiptUrl,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          planId: planId,
          courseId: courseId,
          amount: amount,
          currency: currency,
          status: status,
          paymentGateway: paymentGateway,
          gatewayPaymentId: gatewayPaymentId,
          gatewayOrderId: gatewayOrderId,
          receiptUrl: receiptUrl,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Payment]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Payment copyWith({
    Object? id = _Undefined,
    int? userId,
    Object? planId = _Undefined,
    Object? courseId = _Undefined,
    double? amount,
    String? currency,
    String? status,
    String? paymentGateway,
    Object? gatewayPaymentId = _Undefined,
    Object? gatewayOrderId = _Undefined,
    Object? receiptUrl = _Undefined,
    DateTime? createdAt,
  }) {
    return Payment(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      planId: planId is int? ? planId : this.planId,
      courseId: courseId is int? ? courseId : this.courseId,
      amount: amount ?? this.amount,
      currency: currency ?? this.currency,
      status: status ?? this.status,
      paymentGateway: paymentGateway ?? this.paymentGateway,
      gatewayPaymentId: gatewayPaymentId is String?
          ? gatewayPaymentId
          : this.gatewayPaymentId,
      gatewayOrderId:
          gatewayOrderId is String? ? gatewayOrderId : this.gatewayOrderId,
      receiptUrl: receiptUrl is String? ? receiptUrl : this.receiptUrl,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
