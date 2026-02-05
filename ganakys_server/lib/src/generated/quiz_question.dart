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

abstract class QuizQuestion
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  QuizQuestion._({
    this.id,
    required this.quizId,
    required this.question,
    required this.options,
    this.explanation,
    int? sortOrder,
  }) : sortOrder = sortOrder ?? 0;

  factory QuizQuestion({
    int? id,
    required int quizId,
    required String question,
    required String options,
    String? explanation,
    int? sortOrder,
  }) = _QuizQuestionImpl;

  factory QuizQuestion.fromJson(Map<String, dynamic> jsonSerialization) {
    return QuizQuestion(
      id: jsonSerialization['id'] as int?,
      quizId: jsonSerialization['quizId'] as int,
      question: jsonSerialization['question'] as String,
      options: jsonSerialization['options'] as String,
      explanation: jsonSerialization['explanation'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
    );
  }

  static final t = QuizQuestionTable();

  static const db = QuizQuestionRepository._();

  @override
  int? id;

  int quizId;

  String question;

  String options;

  String? explanation;

  int sortOrder;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [QuizQuestion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  QuizQuestion copyWith({
    int? id,
    int? quizId,
    String? question,
    String? options,
    String? explanation,
    int? sortOrder,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'quizId': quizId,
      'question': question,
      'options': options,
      if (explanation != null) 'explanation': explanation,
      'sortOrder': sortOrder,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'quizId': quizId,
      'question': question,
      'options': options,
      if (explanation != null) 'explanation': explanation,
      'sortOrder': sortOrder,
    };
  }

  static QuizQuestionInclude include() {
    return QuizQuestionInclude._();
  }

  static QuizQuestionIncludeList includeList({
    _i1.WhereExpressionBuilder<QuizQuestionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizQuestionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizQuestionTable>? orderByList,
    QuizQuestionInclude? include,
  }) {
    return QuizQuestionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(QuizQuestion.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(QuizQuestion.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizQuestionImpl extends QuizQuestion {
  _QuizQuestionImpl({
    int? id,
    required int quizId,
    required String question,
    required String options,
    String? explanation,
    int? sortOrder,
  }) : super._(
          id: id,
          quizId: quizId,
          question: question,
          options: options,
          explanation: explanation,
          sortOrder: sortOrder,
        );

  /// Returns a shallow copy of this [QuizQuestion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  QuizQuestion copyWith({
    Object? id = _Undefined,
    int? quizId,
    String? question,
    String? options,
    Object? explanation = _Undefined,
    int? sortOrder,
  }) {
    return QuizQuestion(
      id: id is int? ? id : this.id,
      quizId: quizId ?? this.quizId,
      question: question ?? this.question,
      options: options ?? this.options,
      explanation: explanation is String? ? explanation : this.explanation,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }
}

class QuizQuestionTable extends _i1.Table<int?> {
  QuizQuestionTable({super.tableRelation})
      : super(tableName: 'quiz_questions') {
    quizId = _i1.ColumnInt(
      'quizId',
      this,
    );
    question = _i1.ColumnString(
      'question',
      this,
    );
    options = _i1.ColumnString(
      'options',
      this,
    );
    explanation = _i1.ColumnString(
      'explanation',
      this,
    );
    sortOrder = _i1.ColumnInt(
      'sortOrder',
      this,
      hasDefault: true,
    );
  }

  late final _i1.ColumnInt quizId;

  late final _i1.ColumnString question;

  late final _i1.ColumnString options;

  late final _i1.ColumnString explanation;

  late final _i1.ColumnInt sortOrder;

  @override
  List<_i1.Column> get columns => [
        id,
        quizId,
        question,
        options,
        explanation,
        sortOrder,
      ];
}

class QuizQuestionInclude extends _i1.IncludeObject {
  QuizQuestionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => QuizQuestion.t;
}

class QuizQuestionIncludeList extends _i1.IncludeList {
  QuizQuestionIncludeList._({
    _i1.WhereExpressionBuilder<QuizQuestionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(QuizQuestion.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => QuizQuestion.t;
}

class QuizQuestionRepository {
  const QuizQuestionRepository._();

  /// Returns a list of [QuizQuestion]s matching the given query parameters.
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
  Future<List<QuizQuestion>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizQuestionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<QuizQuestionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizQuestionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<QuizQuestion>(
      where: where?.call(QuizQuestion.t),
      orderBy: orderBy?.call(QuizQuestion.t),
      orderByList: orderByList?.call(QuizQuestion.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [QuizQuestion] matching the given query parameters.
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
  Future<QuizQuestion?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizQuestionTable>? where,
    int? offset,
    _i1.OrderByBuilder<QuizQuestionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<QuizQuestionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<QuizQuestion>(
      where: where?.call(QuizQuestion.t),
      orderBy: orderBy?.call(QuizQuestion.t),
      orderByList: orderByList?.call(QuizQuestion.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [QuizQuestion] by its [id] or null if no such row exists.
  Future<QuizQuestion?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<QuizQuestion>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [QuizQuestion]s in the list and returns the inserted rows.
  ///
  /// The returned [QuizQuestion]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<QuizQuestion>> insert(
    _i1.Session session,
    List<QuizQuestion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<QuizQuestion>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [QuizQuestion] and returns the inserted row.
  ///
  /// The returned [QuizQuestion] will have its `id` field set.
  Future<QuizQuestion> insertRow(
    _i1.Session session,
    QuizQuestion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<QuizQuestion>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [QuizQuestion]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<QuizQuestion>> update(
    _i1.Session session,
    List<QuizQuestion> rows, {
    _i1.ColumnSelections<QuizQuestionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<QuizQuestion>(
      rows,
      columns: columns?.call(QuizQuestion.t),
      transaction: transaction,
    );
  }

  /// Updates a single [QuizQuestion]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<QuizQuestion> updateRow(
    _i1.Session session,
    QuizQuestion row, {
    _i1.ColumnSelections<QuizQuestionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<QuizQuestion>(
      row,
      columns: columns?.call(QuizQuestion.t),
      transaction: transaction,
    );
  }

  /// Deletes all [QuizQuestion]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<QuizQuestion>> delete(
    _i1.Session session,
    List<QuizQuestion> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<QuizQuestion>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [QuizQuestion].
  Future<QuizQuestion> deleteRow(
    _i1.Session session,
    QuizQuestion row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<QuizQuestion>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<QuizQuestion>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<QuizQuestionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<QuizQuestion>(
      where: where(QuizQuestion.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<QuizQuestionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<QuizQuestion>(
      where: where?.call(QuizQuestion.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
