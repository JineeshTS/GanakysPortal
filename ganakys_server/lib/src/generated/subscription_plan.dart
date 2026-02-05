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

abstract class SubscriptionPlan
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
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

  static final t = SubscriptionPlanTable();

  static const db = SubscriptionPlanRepository._();

  @override
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

  @override
  _i1.Table<int?> get table => t;

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
  Map<String, dynamic> toJsonForProtocol() {
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

  static SubscriptionPlanInclude include() {
    return SubscriptionPlanInclude._();
  }

  static SubscriptionPlanIncludeList includeList({
    _i1.WhereExpressionBuilder<SubscriptionPlanTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SubscriptionPlanTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionPlanTable>? orderByList,
    SubscriptionPlanInclude? include,
  }) {
    return SubscriptionPlanIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(SubscriptionPlan.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(SubscriptionPlan.t),
      include: include,
    );
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

class SubscriptionPlanTable extends _i1.Table<int?> {
  SubscriptionPlanTable({super.tableRelation})
      : super(tableName: 'subscription_plans') {
    name = _i1.ColumnString(
      'name',
      this,
    );
    slug = _i1.ColumnString(
      'slug',
      this,
    );
    priceMonthly = _i1.ColumnDouble(
      'priceMonthly',
      this,
    );
    priceYearly = _i1.ColumnDouble(
      'priceYearly',
      this,
    );
    currency = _i1.ColumnString(
      'currency',
      this,
      hasDefault: true,
    );
    features = _i1.ColumnString(
      'features',
      this,
    );
    isActive = _i1.ColumnBool(
      'isActive',
      this,
      hasDefault: true,
    );
    stripePriceId = _i1.ColumnString(
      'stripePriceId',
      this,
    );
    razorpayPlanId = _i1.ColumnString(
      'razorpayPlanId',
      this,
    );
    sortOrder = _i1.ColumnInt(
      'sortOrder',
      this,
      hasDefault: true,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnString name;

  late final _i1.ColumnString slug;

  late final _i1.ColumnDouble priceMonthly;

  late final _i1.ColumnDouble priceYearly;

  late final _i1.ColumnString currency;

  late final _i1.ColumnString features;

  late final _i1.ColumnBool isActive;

  late final _i1.ColumnString stripePriceId;

  late final _i1.ColumnString razorpayPlanId;

  late final _i1.ColumnInt sortOrder;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        name,
        slug,
        priceMonthly,
        priceYearly,
        currency,
        features,
        isActive,
        stripePriceId,
        razorpayPlanId,
        sortOrder,
        createdAt,
      ];
}

class SubscriptionPlanInclude extends _i1.IncludeObject {
  SubscriptionPlanInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => SubscriptionPlan.t;
}

class SubscriptionPlanIncludeList extends _i1.IncludeList {
  SubscriptionPlanIncludeList._({
    _i1.WhereExpressionBuilder<SubscriptionPlanTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(SubscriptionPlan.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => SubscriptionPlan.t;
}

class SubscriptionPlanRepository {
  const SubscriptionPlanRepository._();

  /// Returns a list of [SubscriptionPlan]s matching the given query parameters.
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
  Future<List<SubscriptionPlan>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionPlanTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SubscriptionPlanTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionPlanTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<SubscriptionPlan>(
      where: where?.call(SubscriptionPlan.t),
      orderBy: orderBy?.call(SubscriptionPlan.t),
      orderByList: orderByList?.call(SubscriptionPlan.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [SubscriptionPlan] matching the given query parameters.
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
  Future<SubscriptionPlan?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionPlanTable>? where,
    int? offset,
    _i1.OrderByBuilder<SubscriptionPlanTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SubscriptionPlanTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<SubscriptionPlan>(
      where: where?.call(SubscriptionPlan.t),
      orderBy: orderBy?.call(SubscriptionPlan.t),
      orderByList: orderByList?.call(SubscriptionPlan.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [SubscriptionPlan] by its [id] or null if no such row exists.
  Future<SubscriptionPlan?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<SubscriptionPlan>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [SubscriptionPlan]s in the list and returns the inserted rows.
  ///
  /// The returned [SubscriptionPlan]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<SubscriptionPlan>> insert(
    _i1.Session session,
    List<SubscriptionPlan> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<SubscriptionPlan>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [SubscriptionPlan] and returns the inserted row.
  ///
  /// The returned [SubscriptionPlan] will have its `id` field set.
  Future<SubscriptionPlan> insertRow(
    _i1.Session session,
    SubscriptionPlan row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<SubscriptionPlan>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [SubscriptionPlan]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<SubscriptionPlan>> update(
    _i1.Session session,
    List<SubscriptionPlan> rows, {
    _i1.ColumnSelections<SubscriptionPlanTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<SubscriptionPlan>(
      rows,
      columns: columns?.call(SubscriptionPlan.t),
      transaction: transaction,
    );
  }

  /// Updates a single [SubscriptionPlan]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<SubscriptionPlan> updateRow(
    _i1.Session session,
    SubscriptionPlan row, {
    _i1.ColumnSelections<SubscriptionPlanTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<SubscriptionPlan>(
      row,
      columns: columns?.call(SubscriptionPlan.t),
      transaction: transaction,
    );
  }

  /// Deletes all [SubscriptionPlan]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<SubscriptionPlan>> delete(
    _i1.Session session,
    List<SubscriptionPlan> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<SubscriptionPlan>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [SubscriptionPlan].
  Future<SubscriptionPlan> deleteRow(
    _i1.Session session,
    SubscriptionPlan row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<SubscriptionPlan>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<SubscriptionPlan>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<SubscriptionPlanTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<SubscriptionPlan>(
      where: where(SubscriptionPlan.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SubscriptionPlanTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<SubscriptionPlan>(
      where: where?.call(SubscriptionPlan.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
