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

abstract class Review implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Review._({
    this.id,
    required this.userId,
    required this.courseId,
    required this.rating,
    this.comment,
    bool? isApproved,
    bool? isFlagged,
    required this.createdAt,
    required this.updatedAt,
  })  : isApproved = isApproved ?? true,
        isFlagged = isFlagged ?? false;

  factory Review({
    int? id,
    required int userId,
    required int courseId,
    required int rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _ReviewImpl;

  factory Review.fromJson(Map<String, dynamic> jsonSerialization) {
    return Review(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      rating: jsonSerialization['rating'] as int,
      comment: jsonSerialization['comment'] as String?,
      isApproved: jsonSerialization['isApproved'] as bool,
      isFlagged: jsonSerialization['isFlagged'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = ReviewTable();

  static const db = ReviewRepository._();

  @override
  int? id;

  int userId;

  int courseId;

  int rating;

  String? comment;

  bool isApproved;

  bool isFlagged;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Review]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Review copyWith({
    int? id,
    int? userId,
    int? courseId,
    int? rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'rating': rating,
      if (comment != null) 'comment': comment,
      'isApproved': isApproved,
      'isFlagged': isFlagged,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'rating': rating,
      if (comment != null) 'comment': comment,
      'isApproved': isApproved,
      'isFlagged': isFlagged,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static ReviewInclude include() {
    return ReviewInclude._();
  }

  static ReviewIncludeList includeList({
    _i1.WhereExpressionBuilder<ReviewTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<ReviewTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ReviewTable>? orderByList,
    ReviewInclude? include,
  }) {
    return ReviewIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Review.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Review.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _ReviewImpl extends Review {
  _ReviewImpl({
    int? id,
    required int userId,
    required int courseId,
    required int rating,
    String? comment,
    bool? isApproved,
    bool? isFlagged,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          userId: userId,
          courseId: courseId,
          rating: rating,
          comment: comment,
          isApproved: isApproved,
          isFlagged: isFlagged,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Review]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Review copyWith({
    Object? id = _Undefined,
    int? userId,
    int? courseId,
    int? rating,
    Object? comment = _Undefined,
    bool? isApproved,
    bool? isFlagged,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Review(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      courseId: courseId ?? this.courseId,
      rating: rating ?? this.rating,
      comment: comment is String? ? comment : this.comment,
      isApproved: isApproved ?? this.isApproved,
      isFlagged: isFlagged ?? this.isFlagged,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class ReviewTable extends _i1.Table<int?> {
  ReviewTable({super.tableRelation}) : super(tableName: 'reviews') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    rating = _i1.ColumnInt(
      'rating',
      this,
    );
    comment = _i1.ColumnString(
      'comment',
      this,
    );
    isApproved = _i1.ColumnBool(
      'isApproved',
      this,
      hasDefault: true,
    );
    isFlagged = _i1.ColumnBool(
      'isFlagged',
      this,
      hasDefault: true,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
    updatedAt = _i1.ColumnDateTime(
      'updatedAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnInt rating;

  late final _i1.ColumnString comment;

  late final _i1.ColumnBool isApproved;

  late final _i1.ColumnBool isFlagged;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        courseId,
        rating,
        comment,
        isApproved,
        isFlagged,
        createdAt,
        updatedAt,
      ];
}

class ReviewInclude extends _i1.IncludeObject {
  ReviewInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Review.t;
}

class ReviewIncludeList extends _i1.IncludeList {
  ReviewIncludeList._({
    _i1.WhereExpressionBuilder<ReviewTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Review.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Review.t;
}

class ReviewRepository {
  const ReviewRepository._();

  /// Returns a list of [Review]s matching the given query parameters.
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
  Future<List<Review>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ReviewTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<ReviewTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ReviewTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Review>(
      where: where?.call(Review.t),
      orderBy: orderBy?.call(Review.t),
      orderByList: orderByList?.call(Review.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Review] matching the given query parameters.
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
  Future<Review?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ReviewTable>? where,
    int? offset,
    _i1.OrderByBuilder<ReviewTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ReviewTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Review>(
      where: where?.call(Review.t),
      orderBy: orderBy?.call(Review.t),
      orderByList: orderByList?.call(Review.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Review] by its [id] or null if no such row exists.
  Future<Review?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Review>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Review]s in the list and returns the inserted rows.
  ///
  /// The returned [Review]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Review>> insert(
    _i1.Session session,
    List<Review> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Review>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Review] and returns the inserted row.
  ///
  /// The returned [Review] will have its `id` field set.
  Future<Review> insertRow(
    _i1.Session session,
    Review row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Review>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Review]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Review>> update(
    _i1.Session session,
    List<Review> rows, {
    _i1.ColumnSelections<ReviewTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Review>(
      rows,
      columns: columns?.call(Review.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Review]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Review> updateRow(
    _i1.Session session,
    Review row, {
    _i1.ColumnSelections<ReviewTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Review>(
      row,
      columns: columns?.call(Review.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Review]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Review>> delete(
    _i1.Session session,
    List<Review> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Review>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Review].
  Future<Review> deleteRow(
    _i1.Session session,
    Review row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Review>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Review>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<ReviewTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Review>(
      where: where(Review.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ReviewTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Review>(
      where: where?.call(Review.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
