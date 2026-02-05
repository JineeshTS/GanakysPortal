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

abstract class DiscussionReply
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  DiscussionReply._({
    this.id,
    required this.discussionId,
    required this.userId,
    required this.content,
    bool? isInstructorReply,
    required this.createdAt,
    required this.updatedAt,
  }) : isInstructorReply = isInstructorReply ?? false;

  factory DiscussionReply({
    int? id,
    required int discussionId,
    required int userId,
    required String content,
    bool? isInstructorReply,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _DiscussionReplyImpl;

  factory DiscussionReply.fromJson(Map<String, dynamic> jsonSerialization) {
    return DiscussionReply(
      id: jsonSerialization['id'] as int?,
      discussionId: jsonSerialization['discussionId'] as int,
      userId: jsonSerialization['userId'] as int,
      content: jsonSerialization['content'] as String,
      isInstructorReply: jsonSerialization['isInstructorReply'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = DiscussionReplyTable();

  static const db = DiscussionReplyRepository._();

  @override
  int? id;

  int discussionId;

  int userId;

  String content;

  bool isInstructorReply;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [DiscussionReply]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  DiscussionReply copyWith({
    int? id,
    int? discussionId,
    int? userId,
    String? content,
    bool? isInstructorReply,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'discussionId': discussionId,
      'userId': userId,
      'content': content,
      'isInstructorReply': isInstructorReply,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'discussionId': discussionId,
      'userId': userId,
      'content': content,
      'isInstructorReply': isInstructorReply,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static DiscussionReplyInclude include() {
    return DiscussionReplyInclude._();
  }

  static DiscussionReplyIncludeList includeList({
    _i1.WhereExpressionBuilder<DiscussionReplyTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<DiscussionReplyTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionReplyTable>? orderByList,
    DiscussionReplyInclude? include,
  }) {
    return DiscussionReplyIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(DiscussionReply.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(DiscussionReply.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _DiscussionReplyImpl extends DiscussionReply {
  _DiscussionReplyImpl({
    int? id,
    required int discussionId,
    required int userId,
    required String content,
    bool? isInstructorReply,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          discussionId: discussionId,
          userId: userId,
          content: content,
          isInstructorReply: isInstructorReply,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [DiscussionReply]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  DiscussionReply copyWith({
    Object? id = _Undefined,
    int? discussionId,
    int? userId,
    String? content,
    bool? isInstructorReply,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return DiscussionReply(
      id: id is int? ? id : this.id,
      discussionId: discussionId ?? this.discussionId,
      userId: userId ?? this.userId,
      content: content ?? this.content,
      isInstructorReply: isInstructorReply ?? this.isInstructorReply,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class DiscussionReplyTable extends _i1.Table<int?> {
  DiscussionReplyTable({super.tableRelation})
      : super(tableName: 'discussion_replies') {
    discussionId = _i1.ColumnInt(
      'discussionId',
      this,
    );
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    content = _i1.ColumnString(
      'content',
      this,
    );
    isInstructorReply = _i1.ColumnBool(
      'isInstructorReply',
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

  late final _i1.ColumnInt discussionId;

  late final _i1.ColumnInt userId;

  late final _i1.ColumnString content;

  late final _i1.ColumnBool isInstructorReply;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        discussionId,
        userId,
        content,
        isInstructorReply,
        createdAt,
        updatedAt,
      ];
}

class DiscussionReplyInclude extends _i1.IncludeObject {
  DiscussionReplyInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => DiscussionReply.t;
}

class DiscussionReplyIncludeList extends _i1.IncludeList {
  DiscussionReplyIncludeList._({
    _i1.WhereExpressionBuilder<DiscussionReplyTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(DiscussionReply.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => DiscussionReply.t;
}

class DiscussionReplyRepository {
  const DiscussionReplyRepository._();

  /// Returns a list of [DiscussionReply]s matching the given query parameters.
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
  Future<List<DiscussionReply>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionReplyTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<DiscussionReplyTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionReplyTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<DiscussionReply>(
      where: where?.call(DiscussionReply.t),
      orderBy: orderBy?.call(DiscussionReply.t),
      orderByList: orderByList?.call(DiscussionReply.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [DiscussionReply] matching the given query parameters.
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
  Future<DiscussionReply?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionReplyTable>? where,
    int? offset,
    _i1.OrderByBuilder<DiscussionReplyTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<DiscussionReplyTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<DiscussionReply>(
      where: where?.call(DiscussionReply.t),
      orderBy: orderBy?.call(DiscussionReply.t),
      orderByList: orderByList?.call(DiscussionReply.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [DiscussionReply] by its [id] or null if no such row exists.
  Future<DiscussionReply?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<DiscussionReply>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [DiscussionReply]s in the list and returns the inserted rows.
  ///
  /// The returned [DiscussionReply]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<DiscussionReply>> insert(
    _i1.Session session,
    List<DiscussionReply> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<DiscussionReply>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [DiscussionReply] and returns the inserted row.
  ///
  /// The returned [DiscussionReply] will have its `id` field set.
  Future<DiscussionReply> insertRow(
    _i1.Session session,
    DiscussionReply row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<DiscussionReply>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [DiscussionReply]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<DiscussionReply>> update(
    _i1.Session session,
    List<DiscussionReply> rows, {
    _i1.ColumnSelections<DiscussionReplyTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<DiscussionReply>(
      rows,
      columns: columns?.call(DiscussionReply.t),
      transaction: transaction,
    );
  }

  /// Updates a single [DiscussionReply]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<DiscussionReply> updateRow(
    _i1.Session session,
    DiscussionReply row, {
    _i1.ColumnSelections<DiscussionReplyTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<DiscussionReply>(
      row,
      columns: columns?.call(DiscussionReply.t),
      transaction: transaction,
    );
  }

  /// Deletes all [DiscussionReply]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<DiscussionReply>> delete(
    _i1.Session session,
    List<DiscussionReply> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<DiscussionReply>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [DiscussionReply].
  Future<DiscussionReply> deleteRow(
    _i1.Session session,
    DiscussionReply row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<DiscussionReply>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<DiscussionReply>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<DiscussionReplyTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<DiscussionReply>(
      where: where(DiscussionReply.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<DiscussionReplyTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<DiscussionReply>(
      where: where?.call(DiscussionReply.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
