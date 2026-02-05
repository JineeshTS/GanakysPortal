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

abstract class StudentNote
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  StudentNote._({
    this.id,
    required this.userId,
    required this.lectureId,
    required this.courseId,
    required this.content,
    this.timestampSeconds,
    required this.createdAt,
    required this.updatedAt,
  });

  factory StudentNote({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    required String content,
    int? timestampSeconds,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _StudentNoteImpl;

  factory StudentNote.fromJson(Map<String, dynamic> jsonSerialization) {
    return StudentNote(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      lectureId: jsonSerialization['lectureId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      content: jsonSerialization['content'] as String,
      timestampSeconds: jsonSerialization['timestampSeconds'] as int?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = StudentNoteTable();

  static const db = StudentNoteRepository._();

  @override
  int? id;

  int userId;

  int lectureId;

  int courseId;

  String content;

  int? timestampSeconds;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [StudentNote]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  StudentNote copyWith({
    int? id,
    int? userId,
    int? lectureId,
    int? courseId,
    String? content,
    int? timestampSeconds,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'content': content,
      if (timestampSeconds != null) 'timestampSeconds': timestampSeconds,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'lectureId': lectureId,
      'courseId': courseId,
      'content': content,
      if (timestampSeconds != null) 'timestampSeconds': timestampSeconds,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static StudentNoteInclude include() {
    return StudentNoteInclude._();
  }

  static StudentNoteIncludeList includeList({
    _i1.WhereExpressionBuilder<StudentNoteTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<StudentNoteTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<StudentNoteTable>? orderByList,
    StudentNoteInclude? include,
  }) {
    return StudentNoteIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(StudentNote.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(StudentNote.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _StudentNoteImpl extends StudentNote {
  _StudentNoteImpl({
    int? id,
    required int userId,
    required int lectureId,
    required int courseId,
    required String content,
    int? timestampSeconds,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          userId: userId,
          lectureId: lectureId,
          courseId: courseId,
          content: content,
          timestampSeconds: timestampSeconds,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [StudentNote]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  StudentNote copyWith({
    Object? id = _Undefined,
    int? userId,
    int? lectureId,
    int? courseId,
    String? content,
    Object? timestampSeconds = _Undefined,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return StudentNote(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      lectureId: lectureId ?? this.lectureId,
      courseId: courseId ?? this.courseId,
      content: content ?? this.content,
      timestampSeconds:
          timestampSeconds is int? ? timestampSeconds : this.timestampSeconds,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class StudentNoteTable extends _i1.Table<int?> {
  StudentNoteTable({super.tableRelation}) : super(tableName: 'student_notes') {
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
    content = _i1.ColumnString(
      'content',
      this,
    );
    timestampSeconds = _i1.ColumnInt(
      'timestampSeconds',
      this,
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

  late final _i1.ColumnInt lectureId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnString content;

  late final _i1.ColumnInt timestampSeconds;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        lectureId,
        courseId,
        content,
        timestampSeconds,
        createdAt,
        updatedAt,
      ];
}

class StudentNoteInclude extends _i1.IncludeObject {
  StudentNoteInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => StudentNote.t;
}

class StudentNoteIncludeList extends _i1.IncludeList {
  StudentNoteIncludeList._({
    _i1.WhereExpressionBuilder<StudentNoteTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(StudentNote.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => StudentNote.t;
}

class StudentNoteRepository {
  const StudentNoteRepository._();

  /// Returns a list of [StudentNote]s matching the given query parameters.
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
  Future<List<StudentNote>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<StudentNoteTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<StudentNoteTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<StudentNoteTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<StudentNote>(
      where: where?.call(StudentNote.t),
      orderBy: orderBy?.call(StudentNote.t),
      orderByList: orderByList?.call(StudentNote.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [StudentNote] matching the given query parameters.
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
  Future<StudentNote?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<StudentNoteTable>? where,
    int? offset,
    _i1.OrderByBuilder<StudentNoteTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<StudentNoteTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<StudentNote>(
      where: where?.call(StudentNote.t),
      orderBy: orderBy?.call(StudentNote.t),
      orderByList: orderByList?.call(StudentNote.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [StudentNote] by its [id] or null if no such row exists.
  Future<StudentNote?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<StudentNote>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [StudentNote]s in the list and returns the inserted rows.
  ///
  /// The returned [StudentNote]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<StudentNote>> insert(
    _i1.Session session,
    List<StudentNote> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<StudentNote>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [StudentNote] and returns the inserted row.
  ///
  /// The returned [StudentNote] will have its `id` field set.
  Future<StudentNote> insertRow(
    _i1.Session session,
    StudentNote row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<StudentNote>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [StudentNote]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<StudentNote>> update(
    _i1.Session session,
    List<StudentNote> rows, {
    _i1.ColumnSelections<StudentNoteTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<StudentNote>(
      rows,
      columns: columns?.call(StudentNote.t),
      transaction: transaction,
    );
  }

  /// Updates a single [StudentNote]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<StudentNote> updateRow(
    _i1.Session session,
    StudentNote row, {
    _i1.ColumnSelections<StudentNoteTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<StudentNote>(
      row,
      columns: columns?.call(StudentNote.t),
      transaction: transaction,
    );
  }

  /// Deletes all [StudentNote]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<StudentNote>> delete(
    _i1.Session session,
    List<StudentNote> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<StudentNote>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [StudentNote].
  Future<StudentNote> deleteRow(
    _i1.Session session,
    StudentNote row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<StudentNote>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<StudentNote>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<StudentNoteTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<StudentNote>(
      where: where(StudentNote.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<StudentNoteTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<StudentNote>(
      where: where?.call(StudentNote.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
