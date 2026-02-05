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

abstract class Bookmark
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Bookmark._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    int? timestampSeconds,
    this.label,
    required this.createdAt,
  }) : timestampSeconds = timestampSeconds ?? 0;

  factory Bookmark({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    int? timestampSeconds,
    String? label,
    required DateTime createdAt,
  }) = _BookmarkImpl;

  factory Bookmark.fromJson(Map<String, dynamic> jsonSerialization) {
    return Bookmark(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      timestampSeconds: jsonSerialization['timestampSeconds'] as int,
      label: jsonSerialization['label'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = BookmarkTable();

  static const db = BookmarkRepository._();

  @override
  int? id;

  int userId;

  int lectureId;

  int courseId;

  int timestampSeconds;

  String? label;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Bookmark]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Bookmark copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    int? timestampSeconds,
    String? label,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'timestampSeconds': timestampSeconds,
      if (label != null) 'label': label,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'timestampSeconds': timestampSeconds,
      if (label != null) 'label': label,
      'createdAt': createdAt.toJson(),
    };
  }

  static BookmarkInclude include() {
    return BookmarkInclude._();
  }

  static BookmarkIncludeList includeList({
    _i1.WhereExpressionBuilder<BookmarkTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<BookmarkTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<BookmarkTable>? orderByList,
    BookmarkInclude? include,
  }) {
    return BookmarkIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Bookmark.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Bookmark.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _BookmarkImpl extends Bookmark {
  _BookmarkImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    int? timestampSeconds,
    String? label,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          timestampSeconds: timestampSeconds,
          label: label,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Bookmark]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Bookmark copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    int? timestampSeconds,
    Object? label = _Undefined,
    DateTime? createdAt,
  }) {
    return Bookmark(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      timestampSeconds: timestampSeconds ?? this.timestampSeconds,
      label: label is String? ? label : this.label,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class BookmarkTable extends _i1.Table<int?> {
  BookmarkTable({super.tableRelation}) : super(tableName: 'bookmarks') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    lectureId = _i1.ColumnInt(
      'lectureId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    timestampSeconds = _i1.ColumnInt(
      'timestampSeconds',
      this,
      hasDefault: true,
    );
    label = _i1.ColumnString(
      'label',
      this,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt lectureId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnInt timestampSeconds;

  late final _i1.ColumnString label;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        lectureId,
        courseId,
        timestampSeconds,
        label,
        createdAt,
      ];
}

class BookmarkInclude extends _i1.IncludeObject {
  BookmarkInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Bookmark.t;
}

class BookmarkIncludeList extends _i1.IncludeList {
  BookmarkIncludeList._({
    _i1.WhereExpressionBuilder<BookmarkTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Bookmark.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Bookmark.t;
}

class BookmarkRepository {
  const BookmarkRepository._();

  /// Returns a list of [Bookmark]s matching the given query parameters.
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
  Future<List<Bookmark>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<BookmarkTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<BookmarkTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<BookmarkTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Bookmark>(
      where: where?.call(Bookmark.t),
      orderBy: orderBy?.call(Bookmark.t),
      orderByList: orderByList?.call(Bookmark.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Bookmark] matching the given query parameters.
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
  Future<Bookmark?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<BookmarkTable>? where,
    int? offset,
    _i1.OrderByBuilder<BookmarkTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<BookmarkTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Bookmark>(
      where: where?.call(Bookmark.t),
      orderBy: orderBy?.call(Bookmark.t),
      orderByList: orderByList?.call(Bookmark.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Bookmark] by its [id] or null if no such row exists.
  Future<Bookmark?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Bookmark>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Bookmark]s in the list and returns the inserted rows.
  ///
  /// The returned [Bookmark]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Bookmark>> insert(
    _i1.Session session,
    List<Bookmark> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Bookmark>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Bookmark] and returns the inserted row.
  ///
  /// The returned [Bookmark] will have its `id` field set.
  Future<Bookmark> insertRow(
    _i1.Session session,
    Bookmark row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Bookmark>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Bookmark]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Bookmark>> update(
    _i1.Session session,
    List<Bookmark> rows, {
    _i1.ColumnSelections<BookmarkTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Bookmark>(
      rows,
      columns: columns?.call(Bookmark.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Bookmark]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Bookmark> updateRow(
    _i1.Session session,
    Bookmark row, {
    _i1.ColumnSelections<BookmarkTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Bookmark>(
      row,
      columns: columns?.call(Bookmark.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Bookmark]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Bookmark>> delete(
    _i1.Session session,
    List<Bookmark> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Bookmark>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Bookmark].
  Future<Bookmark> deleteRow(
    _i1.Session session,
    Bookmark row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Bookmark>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Bookmark>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<BookmarkTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Bookmark>(
      where: where(Bookmark.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<BookmarkTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Bookmark>(
      where: where?.call(Bookmark.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
