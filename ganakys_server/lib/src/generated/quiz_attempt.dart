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

abstract class QuizAttempt
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  QuizAttempt._({
    this.id,
    required this.userId,
    required this.quizId,
    required this.score,
    required this.answers,
    required this.passed,
    required this.attemptedAt,
  });

  factory QuizAttempt({
    int? id,
    required int userId,
    required int quizId,
    required double score,
    required String answers,
    required bool passed,
    required DateTime attemptedAt,
  }) = _QuizAttemptImpl;

  factory QuizAttempt.fromJson(Map<String, dynamic> jsonSerialization) {
    return QuizAttempt(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      quizId: jsonSerialization['quizId'] as int,
      score: (jsonSerialization['score'] as num).toDouble(),
      answers: jsonSerialization['answers'] as String,
      passed: jsonSerialization['passed'] as bool,
      attemptedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['attemptedAt']),
    );
  }

  static final t = QuizAttemptTable();

  static const db = QuizAttemptRepository._();

  @override
  int? id;

  int userId;

  int quizId;

  double score;

  String answers;

  bool passed;

  DateTime attemptedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [QuizAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  QuizAttempt copyWith({
    int? id,
    int? userId,
    int? quizId,
    double? score,
    String? answers,
    bool? passed,
    DateTime? attemptedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'quizId': quizId,
      'score': score,
      'answers': answers,
      'passed': passed,
      'attemptedAt': attemptedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'quizId': quizId,
      'score': score,
      'answers': answers,
      'passed': passed,
      'attemptedAt': attemptedAt.toJson(),
    };
  }

  static QuizAttemptInclude include() {
    return QuizAttemptInclude._();
  }

  static QuizAttemptIncludeList includeList({
    _i1.WhereExpressionBuilder<QuizAttemptTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizAttemptTable>? orderByList,
    QuizAttemptInclude? include,
  }) {
    return QuizAttemptIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(QuizAttempt.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(QuizAttempt.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizAttemptImpl extends QuizAttempt {
  _QuizAttemptImpl({
    int? id,
    required int userId,
    required int quizId,
    required double score,
    required String answers,
    required bool passed,
    required DateTime attemptedAt,
  }) : super._(
          id: id,
          userId: userId,
          quizId: quizId,
          score: score,
          answers: answers,
          passed: passed,
          attemptedAt: attemptedAt,
        );

  /// Returns a shallow copy of this [QuizAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  QuizAttempt copyWith({
    Object? id = _Undefined,
    int? userId,
    int? quizId,
    double? score,
    String? answers,
    bool? passed,
    DateTime? attemptedAt,
  }) {
    return QuizAttempt(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      quizId: quizId ?? this.quizId,
      score: score ?? this.score,
      answers: answers ?? this.answers,
      passed: passed ?? this.passed,
      attemptedAt: attemptedAt ?? this.attemptedAt,
    );
  }
}

class QuizAttemptTable extends _i1.Table<int?> {
  QuizAttemptTable({super.tableRelation}) : super(tableName: 'quiz_attempts') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    quizId = _i1.ColumnInt(
      'quizId',
      this,
    );
    score = _i1.ColumnDouble(
      'score',
      this,
    );
    answers = _i1.ColumnString(
      'answers',
      this,
    );
    passed = _i1.ColumnBool(
      'passed',
      this,
    );
    attemptedAt = _i1.ColumnDateTime(
      'attemptedAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt quizId;

  late final _i1.ColumnDouble score;

  late final _i1.ColumnString answers;

  late final _i1.ColumnBool passed;

  late final _i1.ColumnDateTime attemptedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        quizId,
        score,
        answers,
        passed,
        attemptedAt,
      ];
}

class QuizAttemptInclude extends _i1.IncludeObject {
  QuizAttemptInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => QuizAttempt.t;
}

class QuizAttemptIncludeList extends _i1.IncludeList {
  QuizAttemptIncludeList._({
    _i1.WhereExpressionBuilder<QuizAttemptTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(QuizAttempt.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => QuizAttempt.t;
}

class QuizAttemptRepository {
  const QuizAttemptRepository._();

  /// Returns a list of [QuizAttempt]s matching the given query parameters.
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
  Future<List<QuizAttempt>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizAttemptTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizAttemptTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<QuizAttempt>(
      where: where?.call(QuizAttempt.t),
      orderBy: orderBy?.call(QuizAttempt.t),
      orderByList: orderByList?.call(QuizAttempt.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [QuizAttempt] matching the given query parameters.
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
  Future<QuizAttempt?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizAttemptTable>? where,
    int? offset,
    _i1.OrderByBuilder<QuizAttemptTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizAttemptTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<QuizAttempt>(
      where: where?.call(QuizAttempt.t),
      orderBy: orderBy?.call(QuizAttempt.t),
      orderByList: orderByList?.call(QuizAttempt.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [QuizAttempt] by its [id] or null if no such row exists.
  Future<QuizAttempt?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<QuizAttempt>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [QuizAttempt]s in the list and returns the inserted rows.
  ///
  /// The returned [QuizAttempt]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<QuizAttempt>> insert(
    _i1.Session session,
    List<QuizAttempt> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<QuizAttempt>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [QuizAttempt] and returns the inserted row.
  ///
  /// The returned [QuizAttempt] will have its `id` field set.
  Future<QuizAttempt> insertRow(
    _i1.Session session,
    QuizAttempt row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<QuizAttempt>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [QuizAttempt]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<QuizAttempt>> update(
    _i1.Session session,
    List<QuizAttempt> rows, {
    _i1.ColumnSelections<QuizAttemptTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<QuizAttempt>(
      rows,
      columns: columns?.call(QuizAttempt.t),
      transaction: transaction,
    );
  }

  /// Updates a single [QuizAttempt]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<QuizAttempt> updateRow(
    _i1.Session session,
    QuizAttempt row, {
    _i1.ColumnSelections<QuizAttemptTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<QuizAttempt>(
      row,
      columns: columns?.call(QuizAttempt.t),
      transaction: transaction,
    );
  }

  /// Deletes all [QuizAttempt]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<QuizAttempt>> delete(
    _i1.Session session,
    List<QuizAttempt> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<QuizAttempt>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [QuizAttempt].
  Future<QuizAttempt> deleteRow(
    _i1.Session session,
    QuizAttempt row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<QuizAttempt>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<QuizAttempt>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<QuizAttemptTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<QuizAttempt>(
      where: where(QuizAttempt.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizAttemptTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<QuizAttempt>(
      where: where?.call(QuizAttempt.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
