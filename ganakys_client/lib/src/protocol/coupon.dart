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

abstract class Coupon implements _i1.SerializableModel {
  Coupon._({
    this.id,
    required this.code,
    String? discountType,
    required this.discountValue,
    this.maxUses,
    int? usedCount,
    this.validFrom,
    this.validUntil,
    bool? isActive,
    this.applicablePlans,
    this.applicableCourses,
    required this.createdAt,
  })  : discountType = discountType ?? 'percentage',
        usedCount = usedCount ?? 0,
        isActive = isActive ?? true;

  factory Coupon({
    int? id,
    required String code,
    String? discountType,
    required double discountValue,
    int? maxUses,
    int? usedCount,
    DateTime? validFrom,
    DateTime? validUntil,
    bool? isActive,
    String? applicablePlans,
    String? applicableCourses,
    required DateTime createdAt,
  }) = _CouponImpl;

  factory Coupon.fromJson(Map<String, dynamic> jsonSerialization) {
    return Coupon(
      id: jsonSerialization['id'] as int?,
      code: jsonSerialization['code'] as String,
      discountType: jsonSerialization['discountType'] as String,
      discountValue: (jsonSerialization['discountValue'] as num).toDouble(),
      maxUses: jsonSerialization['maxUses'] as int?,
      usedCount: jsonSerialization['usedCount'] as int,
      validFrom: jsonSerialization['validFrom'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['validFrom']),
      validUntil: jsonSerialization['validUntil'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['validUntil']),
      isActive: jsonSerialization['isActive'] as bool,
      applicablePlans: jsonSerialization['applicablePlans'] as String?,
      applicableCourses: jsonSerialization['applicableCourses'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String code;

  String discountType;

  double discountValue;

  int? maxUses;

  int usedCount;

  DateTime? validFrom;

  DateTime? validUntil;

  bool isActive;

  String? applicablePlans;

  String? applicableCourses;

  DateTime createdAt;

  /// Returns a shallow copy of this [Coupon]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Coupon copyWith({
    int? id,
    String? code,
    String? discountType,
    double? discountValue,
    int? maxUses,
    int? usedCount,
    DateTime? validFrom,
    DateTime? validUntil,
    bool? isActive,
    String? applicablePlans,
    String? applicableCourses,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'code': code,
      'discountType': discountType,
      'discountValue': discountValue,
      if (maxUses != null) 'maxUses': maxUses,
      'usedCount': usedCount,
      if (validFrom != null) 'validFrom': validFrom?.toJson(),
      if (validUntil != null) 'validUntil': validUntil?.toJson(),
      'isActive': isActive,
      if (applicablePlans != null) 'applicablePlans': applicablePlans,
      if (applicableCourses != null) 'applicableCourses': applicableCourses,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CouponImpl extends Coupon {
  _CouponImpl({
    int? id,
    required String code,
    String? discountType,
    required double discountValue,
    int? maxUses,
    int? usedCount,
    DateTime? validFrom,
    DateTime? validUntil,
    bool? isActive,
    String? applicablePlans,
    String? applicableCourses,
    required DateTime createdAt,
  }) : super._(
          id: id,
          code: code,
          discountType: discountType,
          discountValue: discountValue,
          maxUses: maxUses,
          usedCount: usedCount,
          validFrom: validFrom,
          validUntil: validUntil,
          isActive: isActive,
          applicablePlans: applicablePlans,
          applicableCourses: applicableCourses,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Coupon]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Coupon copyWith({
    Object? id = _Undefined,
    String? code,
    String? discountType,
    double? discountValue,
    Object? maxUses = _Undefined,
    int? usedCount,
    Object? validFrom = _Undefined,
    Object? validUntil = _Undefined,
    bool? isActive,
    Object? applicablePlans = _Undefined,
    Object? applicableCourses = _Undefined,
    DateTime? createdAt,
  }) {
    return Coupon(
      id: id is int? ? id : this.id,
      code: code ?? this.code,
      discountType: discountType ?? this.discountType,
      discountValue: discountValue ?? this.discountValue,
      maxUses: maxUses is int? ? maxUses : this.maxUses,
      usedCount: usedCount ?? this.usedCount,
      validFrom: validFrom is DateTime? ? validFrom : this.validFrom,
      validUntil: validUntil is DateTime? ? validUntil : this.validUntil,
      isActive: isActive ?? this.isActive,
      applicablePlans:
          applicablePlans is String? ? applicablePlans : this.applicablePlans,
      applicableCourses: applicableCourses is String?
          ? applicableCourses
          : this.applicableCourses,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
