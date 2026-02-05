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

abstract class SiteSetting
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  SiteSetting._({
    this.id,
    required this.key,
    required this.value,
    this.updatedBy,
    required this.updatedAt,
  });

  factory SiteSetting({
    int? id,
    required String key,
    required String value,
    int? updatedBy,
    required DateTime updatedAt,
  }) = _SiteSettingImpl;

  factory SiteSetting.fromJson(Map<String, dynamic> jsonSerialization) {
    return SiteSetting(
      id: jsonSerialization['id'] as int?,
      key: jsonSerialization['key'] as String,
      value: jsonSerialization['value'] as String,
      updatedBy: jsonSerialization['updatedBy'] as int?,
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = SiteSettingTable();

  static const db = SiteSettingRepository._();

  @override
  int? id;

  String key;

  String value;

  int? updatedBy;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [SiteSetting]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  SiteSetting copyWith({
    int? id,
    String? key,
    String? value,
    int? updatedBy,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'key': key,
      'value': value,
      if (updatedBy != null) 'updatedBy': updatedBy,
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'key': key,
      'value': value,
      if (updatedBy != null) 'updatedBy': updatedBy,
      'updatedAt': updatedAt.toJson(),
    };
  }

  static SiteSettingInclude include() {
    return SiteSettingInclude._();
  }

  static SiteSettingIncludeList includeList({
    _i1.WhereExpressionBuilder<SiteSettingTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SiteSettingTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SiteSettingTable>? orderByList,
    SiteSettingInclude? include,
  }) {
    return SiteSettingIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(SiteSetting.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(SiteSetting.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _SiteSettingImpl extends SiteSetting {
  _SiteSettingImpl({
    int? id,
    required String key,
    required String value,
    int? updatedBy,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          key: key,
          value: value,
          updatedBy: updatedBy,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [SiteSetting]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  SiteSetting copyWith({
    Object? id = _Undefined,
    String? key,
    String? value,
    Object? updatedBy = _Undefined,
    DateTime? updatedAt,
  }) {
    return SiteSetting(
      id: id is int? ? id : this.id,
      key: key ?? this.key,
      value: value ?? this.value,
      updatedBy: updatedBy is int? ? updatedBy : this.updatedBy,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class SiteSettingTable extends _i1.Table<int?> {
  SiteSettingTable({super.tableRelation}) : super(tableName: 'site_settings') {
    key = _i1.ColumnString(
      'key',
      this,
    );
    value = _i1.ColumnString(
      'value',
      this,
    );
    updatedBy = _i1.ColumnInt(
      'updatedBy',
      this,
    );
    updatedAt = _i1.ColumnDateTime(
      'updatedAt',
      this,
    );
  }

  late final _i1.ColumnString key;

  late final _i1.ColumnString value;

  late final _i1.ColumnInt updatedBy;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        key,
        value,
        updatedBy,
        updatedAt,
      ];
}

class SiteSettingInclude extends _i1.IncludeObject {
  SiteSettingInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => SiteSetting.t;
}

class SiteSettingIncludeList extends _i1.IncludeList {
  SiteSettingIncludeList._({
    _i1.WhereExpressionBuilder<SiteSettingTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(SiteSetting.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => SiteSetting.t;
}

class SiteSettingRepository {
  const SiteSettingRepository._();

  /// Returns a list of [SiteSetting]s matching the given query parameters.
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
  Future<List<SiteSetting>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SiteSettingTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<SiteSettingTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SiteSettingTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<SiteSetting>(
      where: where?.call(SiteSetting.t),
      orderBy: orderBy?.call(SiteSetting.t),
      orderByList: orderByList?.call(SiteSetting.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [SiteSetting] matching the given query parameters.
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
  Future<SiteSetting?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SiteSettingTable>? where,
    int? offset,
    _i1.OrderByBuilder<SiteSettingTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<SiteSettingTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<SiteSetting>(
      where: where?.call(SiteSetting.t),
      orderBy: orderBy?.call(SiteSetting.t),
      orderByList: orderByList?.call(SiteSetting.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [SiteSetting] by its [id] or null if no such row exists.
  Future<SiteSetting?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<SiteSetting>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [SiteSetting]s in the list and returns the inserted rows.
  ///
  /// The returned [SiteSetting]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<SiteSetting>> insert(
    _i1.Session session,
    List<SiteSetting> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<SiteSetting>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [SiteSetting] and returns the inserted row.
  ///
  /// The returned [SiteSetting] will have its `id` field set.
  Future<SiteSetting> insertRow(
    _i1.Session session,
    SiteSetting row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<SiteSetting>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [SiteSetting]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<SiteSetting>> update(
    _i1.Session session,
    List<SiteSetting> rows, {
    _i1.ColumnSelections<SiteSettingTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<SiteSetting>(
      rows,
      columns: columns?.call(SiteSetting.t),
      transaction: transaction,
    );
  }

  /// Updates a single [SiteSetting]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<SiteSetting> updateRow(
    _i1.Session session,
    SiteSetting row, {
    _i1.ColumnSelections<SiteSettingTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<SiteSetting>(
      row,
      columns: columns?.call(SiteSetting.t),
      transaction: transaction,
    );
  }

  /// Deletes all [SiteSetting]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<SiteSetting>> delete(
    _i1.Session session,
    List<SiteSetting> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<SiteSetting>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [SiteSetting].
  Future<SiteSetting> deleteRow(
    _i1.Session session,
    SiteSetting row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<SiteSetting>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<SiteSetting>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<SiteSettingTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<SiteSetting>(
      where: where(SiteSetting.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<SiteSettingTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<SiteSetting>(
      where: where?.call(SiteSetting.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
