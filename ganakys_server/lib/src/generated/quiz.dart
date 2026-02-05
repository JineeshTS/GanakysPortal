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

abstract class Quiz implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Quiz._({
    this.id,
    required this.courseId,
    this.lectureId,
    required this.title,
    String? type,
    int? passPercentage,
  })  : type = type ?? 'section_quiz',
        passPercentage = passPercentage ?? 70;

  factory Quiz({
    int? id,
    required int courseId,
    int? lectureId,
    required String title,
    String? type,
    int? passPercentage,
  }) = _QuizImpl;

  factory Quiz.fromJson(Map<String, dynamic> jsonSerialization) {
    return Quiz(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      lectureId: jsonSerialization['lectureId'] as int?,
      title: jsonSerialization['title'] as String,
      type: jsonSerialization['type'] as String,
      passPercentage: jsonSerialization['passPercentage'] as int,
    );
  }

  static final t = QuizTable();

  static const db = QuizRepository._();

  @override
  int? id;

  int courseId;

  int? lectureId;

  String title;

  String type;

  int passPercentage;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Quiz]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Quiz copyWith({
    int? id,
    int? courseId,
    int? lectureId,
    String? title,
    String? type,
    int? passPercentage,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'title': title,
      'type': type,
      'passPercentage': passPercentage,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      if (lectureId != null) 'lectureId': lectureId,
      'title': title,
      'type': type,
      'passPercentage': passPercentage,
    };
  }

  static QuizInclude include() {
    return QuizInclude._();
  }

  static QuizIncludeList includeList({
    _i1.WhereExpressionBuilder<QuizTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizTable>? orderByList,
    QuizInclude? include,
  }) {
    return QuizIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Quiz.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Quiz.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizImpl extends Quiz {
  _QuizImpl({
    int? id,
    required int courseId,
    int? lectureId,
    required String title,
    String? type,
    int? passPercentage,
  }) : super._(
          id: id,
          courseId: courseId,
          lectureId: lectureId,
          title: title,
          type: type,
          passPercentage: passPercentage,
        );

  /// Returns a shallow copy of this [Quiz]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Quiz copyWith({
    Object? id = _Undefined,
    int? courseId,
    Object? lectureId = _Undefined,
    String? title,
    String? type,
    int? passPercentage,
  }) {
    return Quiz(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      lectureId: lectureId is int? ? lectureId : this.lectureId,
      title: title ?? this.title,
      type: type ?? this.type,
      passPercentage: passPercentage ?? this.passPercentage,
    );
  }
}

class QuizTable extends _i1.Table<int?> {
  QuizTable({super.tableRelation}) : super(tableName: 'quizzes') {
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    lectureId = _i1.ColumnInt(
      'lectureId',
      this,
    );
    title = _i1.ColumnString(
      'title',
      this,
    );
    type = _i1.ColumnString(
      'type',
      this,
      hasDefault: true,
    );
    passPercentage = _i1.ColumnInt(
      'passPercentage',
      this,
      hasDefault: true,
    );
  }

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnInt lectureId;

  late final _i1.ColumnString title;

  late final _i1.ColumnString type;

  late final _i1.ColumnInt passPercentage;

  @override
  List<_i1.Column> get columns => [
        id,
        courseId,
        lectureId,
        title,
        type,
        passPercentage,
      ];
}

class QuizInclude extends _i1.IncludeObject {
  QuizInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Quiz.t;
}

class QuizIncludeList extends _i1.IncludeList {
  QuizIncludeList._({
    _i1.WhereExpressionBuilder<QuizTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Quiz.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Quiz.t;
}

class QuizRepository {
  const QuizRepository._();

  /// Returns a list of [Quiz]s matching the given query parameters.
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
  Future<List<Quiz>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Quiz>(
      where: where?.call(Quiz.t),
      orderBy: orderBy?.call(Quiz.t),
      orderByList: orderByList?.call(Quiz.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Quiz] matching the given query parameters.
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
  Future<Quiz?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizTable>? where,
    int? offset,
    _i1.OrderByBuilder<QuizTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Quiz>(
      where: where?.call(Quiz.t),
      orderBy: orderBy?.call(Quiz.t),
      orderByList: orderByList?.call(Quiz.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Quiz] by its [id] or null if no such row exists.
  Future<Quiz?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Quiz>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Quiz]s in the list and returns the inserted rows.
  ///
  /// The returned [Quiz]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Quiz>> insert(
    _i1.Session session,
    List<Quiz> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Quiz>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Quiz] and returns the inserted row.
  ///
  /// The returned [Quiz] will have its `id` field set.
  Future<Quiz> insertRow(
    _i1.Session session,
    Quiz row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Quiz>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Quiz]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Quiz>> update(
    _i1.Session session,
    List<Quiz> rows, {
    _i1.ColumnSelections<QuizTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Quiz>(
      rows,
      columns: columns?.call(Quiz.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Quiz]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Quiz> updateRow(
    _i1.Session session,
    Quiz row, {
    _i1.ColumnSelections<QuizTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Quiz>(
      row,
      columns: columns?.call(Quiz.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Quiz]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Quiz>> delete(
    _i1.Session session,
    List<Quiz> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Quiz>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Quiz].
  Future<Quiz> deleteRow(
    _i1.Session session,
    Quiz row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Quiz>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Quiz>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<QuizTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Quiz>(
      where: where(Quiz.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Quiz>(
      where: where?.call(Quiz.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
