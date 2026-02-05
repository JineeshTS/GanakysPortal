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

abstract class SubscriptionPlan implements _i1.SerializableModel {
  SubscriptionPlan._({
    this.id,
    required this.name,
    required this.slug,
    required this.priceMonthly,
    required this.priceYearly,
    String? currency,
    required this.features,
    bool? isActive,
    this.stripePriceId,
    this.razorpayPlanId,
    int? sortOrder,
    required this.createdAt,
  })  : currency = currency ?? 'INR',
        isActive = isActive ?? true,
        sortOrder = sortOrder ?? 0;

  factory SubscriptionPlan({
    int? id,
    required String name,
    required String slug,
    required double priceMonthly,
    required double priceYearly,
    String? currency,
    required String features,
    bool? isActive,
    String? stripePriceId,
    String? razorpayPlanId,
    int? sortOrder,
    required DateTime createdAt,
  }) = _SubscriptionPlanImpl;

  factory SubscriptionPlan.fromJson(Map<String, dynamic> jsonSerialization) {
    return SubscriptionPlan(
      id: jsonSerialization['id'] as int?,
      name: jsonSerialization['name'] as String,
      slug: jsonSerialization['slug'] as String,
      priceMonthly: (jsonSerialization['priceMonthly'] as num).toDouble(),
      priceYearly: (jsonSerialization['priceYearly'] as num).toDouble(),
      currency: jsonSerialization['currency'] as String,
      features: jsonSerialization['features'] as String,
      isActive: jsonSerialization['isActive'] as bool,
      stripePriceId: jsonSerialization['stripePriceId'] as String?,
      razorpayPlanId: jsonSerialization['razorpayPlanId'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String name;

  String slug;

  double priceMonthly;

  double priceYearly;

  String currency;

  String features;

  bool isActive;

  String? stripePriceId;

  String? razorpayPlanId;

  int sortOrder;

  DateTime createdAt;

  /// Returns a shallow copy of this [SubscriptionPlan]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  SubscriptionPlan copyWith({
    int? id,
    String? name,
    String? slug,
    double? priceMonthly,
    double? priceYearly,
    String? currency,
    String? features,
    bool? isActive,
    String? stripePriceId,
    String? razorpayPlanId,
    int? sortOrder,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'slug': slug,
      'priceMonthly': priceMonthly,
      'priceYearly': priceYearly,
      'currency': currency,
      'features': features,
      'isActive': isActive,
      if (stripePriceId != null) 'stripePriceId': stripePriceId,
      if (razorpayPlanId != null) 'razorpayPlanId': razorpayPlanId,
      'sortOrder': sortOrder,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _SubscriptionPlanImpl extends SubscriptionPlan {
  _SubscriptionPlanImpl({
    int? id,
    required String name,
    required String slug,
    required double priceMonthly,
    required double priceYearly,
    String? currency,
    required String features,
    bool? isActive,
    String? stripePriceId,
    String? razorpayPlanId,
    int? sortOrder,
    required DateTime createdAt,
  }) : super._(
          id: id,
          name: name,
          slug: slug,
          priceMonthly: priceMonthly,
          priceYearly: priceYearly,
          currency: currency,
          features: features,
          isActive: isActive,
          stripePriceId: stripePriceId,
          razorpayPlanId: razorpayPlanId,
          sortOrder: sortOrder,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [SubscriptionPlan]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  SubscriptionPlan copyWith({
    Object? id = _Undefined,
    String? name,
    String? slug,
    double? priceMonthly,
    double? priceYearly,
    String? currency,
    String? features,
    bool? isActive,
    Object? stripePriceId = _Undefined,
    Object? razorpayPlanId = _Undefined,
    int? sortOrder,
    DateTime? createdAt,
  }) {
    return SubscriptionPlan(
      id: id is int? ? id : this.id,
      name: name ?? this.name,
      slug: slug ?? this.slug,
      priceMonthly: priceMonthly ?? this.priceMonthly,
      priceYearly: priceYearly ?? this.priceYearly,
      currency: currency ?? this.currency,
      features: features ?? this.features,
      isActive: isActive ?? this.isActive,
      stripePriceId:
          stripePriceId is String? ? stripePriceId : this.stripePriceId,
      razorpayPlanId:
          razorpayPlanId is String? ? razorpayPlanId : this.razorpayPlanId,
      sortOrder: sortOrder ?? this.sortOrder,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
