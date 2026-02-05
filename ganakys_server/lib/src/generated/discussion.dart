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

abstract class Discussion
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Discussion._({
    this.id,
    required this.courseId,
    this.lectureId,
    required this.userId,
    required this.title,
    required this.content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required this.createdAt,
    required this.updatedAt,
  })  : isPinned = isPinned ?? false,
        isResolved = isResolved ?? false,
        replyCount = replyCount ?? 0;

  factory Discussion({
    int? id,
    required int courseId,
    int? lectureId,
    required int userId,
    required String title,
    required String content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _DiscussionImpl;

  factory Discussion.fromJson(Map<String, dynamic> jsonSerialization) {
    return Discussion(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      lectureId: jsonSerialization['lectureId'] as int?,
      userId: jsonSerialization['userId'] as int,
      title: jsonSerialization['title'] as String,
      content: jsonSerialization['content'] as String,
      isPinned: jsonSerialization['isPinned'] as bool,
      isResolved: jsonSerialization['isResolved'] as bool,
      replyCount: jsonSerialization['replyCount'] as int,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = DiscussionTable();

  static const db = DiscussionRepository._();

  @override
  int? id;

  int courseId;

  int? lectureId;

  int userId;

  String title;

  String content;

  bool isPinned;

  bool isResolved;

  int replyCount;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Discussion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Discussion copyWith({
    int? id,
    int? courseId,
    int? lectureId,
    int? userId,
    String? title,
    String? content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'userId': userId,
      'title': title,
      'content': content,
      'isPinned': isPinned,
      'isResolved': isResolved,
      'replyCount': replyCount,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'userId': userId,
      'title': title,
      'content': content,
      'isPinned': isPinned,
      'isResolved': isResolved,
      'replyCount': replyCount,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static DiscussionInclude include() {
    return DiscussionInclude._();
  }

  static DiscussionIncludeList includeList({
    _i1.WhereExpressionBuilder<DiscussionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<DiscussionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionTable>? orderByList,
    DiscussionInclude? include,
  }) {
    return DiscussionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Discussion.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Discussion.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _DiscussionImpl extends Discussion {
  _DiscussionImpl({
    int? id,
    required int courseId,
    int? lectureId,
    required int userId,
    required String title,
    required String content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          courseId: courseId,
          lectureId: lectureId,
          userId: userId,
          title: title,
          content: content,
          isPinned: isPinned,
          isResolved: isResolved,
          replyCount: replyCount,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Discussion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Discussion copyWith({
    Object? id = _Undefined,
    int? courseId,
    Object? lectureId = _Undefined,
    int? userId,
    String? title,
    String? content,
    bool? isPinned,
    bool? isResolved,
    int? replyCount,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Discussion(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      lectureId: lectureId is int? ? lectureId : this.lectureId,
      userId: userId ?? this.userId,
      title: title ?? this.title,
      content: content ?? this.content,
      isPinned: isPinned ?? this.isPinned,
      isResolved: isResolved ?? this.isResolved,
      replyCount: replyCount ?? this.replyCount,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class DiscussionTable extends _i1.Table<int?> {
  DiscussionTable({super.tableRelation}) : super(tableName: 'discussions') {
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    lectureId = _i1.ColumnInt(
      'lectureId',
      this,
    );
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    title = _i1.ColumnString(
      'title',
      this,
    );
    content = _i1.ColumnString(
      'content',
      this,
    );
    isPinned = _i1.ColumnBool(
      'isPinned',
      this,
      hasDefault: true,
    );
    isResolved = _i1.ColumnBool(
      'isResolved',
      this,
      hasDefault: true,
    );
    replyCount = _i1.ColumnInt(
      'replyCount',
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

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnInt lectureId;

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString title;

  late final _i1.ColumnString content;

  late final _i1.ColumnBool isPinned;

  late final _i1.ColumnBool isResolved;

  late final _i1.ColumnInt replyCount;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        courseId,
        lectureId,
        userId,
        title,
        content,
        isPinned,
        isResolved,
        replyCount,
        createdAt,
        updatedAt,
      ];
}

class DiscussionInclude extends _i1.IncludeObject {
  DiscussionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Discussion.t;
}

class DiscussionIncludeList extends _i1.IncludeList {
  DiscussionIncludeList._({
    _i1.WhereExpressionBuilder<DiscussionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Discussion.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Discussion.t;
}

class DiscussionRepository {
  const DiscussionRepository._();

  /// Returns a list of [Discussion]s matching the given query parameters.
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
  Future<List<Discussion>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<DiscussionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Discussion>(
      where: where?.call(Discussion.t),
      orderBy: orderBy?.call(Discussion.t),
      orderByList: orderByList?.call(Discussion.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Discussion] matching the given query parameters.
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
  Future<Discussion?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionTable>? where,
    int? offset,
    _i1.OrderByBuilder<DiscussionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Discussion>(
      where: where?.call(Discussion.t),
      orderBy: orderBy?.call(Discussion.t),
      orderByList: orderByList?.call(Discussion.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Discussion] by its [id] or null if no such row exists.
  Future<Discussion?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Discussion>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Discussion]s in the list and returns the inserted rows.
  ///
  /// The returned [Discussion]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Discussion>> insert(
    _i1.Session session,
    List<Discussion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Discussion>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Discussion] and returns the inserted row.
  ///
  /// The returned [Discussion] will have its `id` field set.
  Future<Discussion> insertRow(
    _i1.Session session,
    Discussion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Discussion>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Discussion]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Discussion>> update(
    _i1.Session session,
    List<Discussion> rows, {
    _i1.ColumnSelections<DiscussionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Discussion>(
      rows,
      columns: columns?.call(Discussion.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Discussion]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Discussion> updateRow(
    _i1.Session session,
    Discussion row, {
    _i1.ColumnSelections<DiscussionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Discussion>(
      row,
      columns: columns?.call(Discussion.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Discussion]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Discussion>> delete(
    _i1.Session session,
    List<Discussion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Discussion>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Discussion].
  Future<Discussion> deleteRow(
    _i1.Session session,
    Discussion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Discussion>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Discussion>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<DiscussionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Discussion>(
      where: where(Discussion.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Discussion>(
      where: where?.call(Discussion.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
