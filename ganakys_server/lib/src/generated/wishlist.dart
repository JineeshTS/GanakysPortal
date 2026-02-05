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

abstract class Wishlist
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Wishlist._({
    this.id,
    required this.userId,
    required this.courseId,
    required this.createdAt,
  });

  factory Wishlist({
    int? id,
    required int userId,
    required int courseId,
    required DateTime createdAt,
  }) = _WishlistImpl;

  factory Wishlist.fromJson(Map<String, dynamic> jsonSerialization) {
    return Wishlist(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = WishlistTable();

  static const db = WishlistRepository._();

  @override
  int? id;

  int userId;

  int courseId;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Wishlist]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Wishlist copyWith({
    int? id,
    int? userId,
    int? courseId,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'createdAt': createdAt.toJson(),
    };
  }

  static WishlistInclude include() {
    return WishlistInclude._();
  }

  static WishlistIncludeList includeList({
    _i1.WhereExpressionBuilder<WishlistTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<WishlistTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<WishlistTable>? orderByList,
    WishlistInclude? include,
  }) {
    return WishlistIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Wishlist.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Wishlist.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _WishlistImpl extends Wishlist {
  _WishlistImpl({
    int? id,
    required int userId,
    required int courseId,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          courseId: courseId,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Wishlist]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Wishlist copyWith({
    Object? id = _Undefined,
    int? userId,
    int? courseId,
    DateTime? createdAt,
  }) {
    return Wishlist(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      courseId: courseId ?? this.courseId,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class WishlistTable extends _i1.Table<int?> {
  WishlistTable({super.tableRelation}) : super(tableName: 'wishlists') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        courseId,
        createdAt,
      ];
}

class WishlistInclude extends _i1.IncludeObject {
  WishlistInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Wishlist.t;
}

class WishlistIncludeList extends _i1.IncludeList {
  WishlistIncludeList._({
    _i1.WhereExpressionBuilder<WishlistTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Wishlist.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Wishlist.t;
}

class WishlistRepository {
  const WishlistRepository._();

  /// Returns a list of [Wishlist]s matching the given query parameters.
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
  Future<List<Wishlist>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<WishlistTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<WishlistTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<WishlistTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Wishlist>(
      where: where?.call(Wishlist.t),
      orderBy: orderBy?.call(Wishlist.t),
      orderByList: orderByList?.call(Wishlist.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Wishlist] matching the given query parameters.
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
  Future<Wishlist?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<WishlistTable>? where,
    int? offset,
    _i1.OrderByBuilder<WishlistTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<WishlistTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Wishlist>(
      where: where?.call(Wishlist.t),
      orderBy: orderBy?.call(Wishlist.t),
      orderByList: orderByList?.call(Wishlist.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Wishlist] by its [id] or null if no such row exists.
  Future<Wishlist?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Wishlist>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Wishlist]s in the list and returns the inserted rows.
  ///
  /// The returned [Wishlist]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Wishlist>> insert(
    _i1.Session session,
    List<Wishlist> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Wishlist>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Wishlist] and returns the inserted row.
  ///
  /// The returned [Wishlist] will have its `id` field set.
  Future<Wishlist> insertRow(
    _i1.Session session,
    Wishlist row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Wishlist>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Wishlist]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Wishlist>> update(
    _i1.Session session,
    List<Wishlist> rows, {
    _i1.ColumnSelections<WishlistTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Wishlist>(
      rows,
      columns: columns?.call(Wishlist.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Wishlist]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Wishlist> updateRow(
    _i1.Session session,
    Wishlist row, {
    _i1.ColumnSelections<WishlistTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Wishlist>(
      row,
      columns: columns?.call(Wishlist.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Wishlist]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Wishlist>> delete(
    _i1.Session session,
    List<Wishlist> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Wishlist>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Wishlist].
  Future<Wishlist> deleteRow(
    _i1.Session session,
    Wishlist row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Wishlist>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Wishlist>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<WishlistTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Wishlist>(
      where: where(Wishlist.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<WishlistTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Wishlist>(
      where: where?.call(Wishlist.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
