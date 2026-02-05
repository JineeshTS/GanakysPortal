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

abstract class LearningPath
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  LearningPath._({
    this.id,
    required this.title,
    required this.slug,
    this.description,
    this.thumbnailUrl,
    String? difficulty,
    required this.courseIds,
    bool? isPublished,
    required this.createdAt,
  })  : difficulty = difficulty ?? 'beginner',
        isPublished = isPublished ?? false;

  factory LearningPath({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    required String courseIds,
    bool? isPublished,
    required DateTime createdAt,
  }) = _LearningPathImpl;

  factory LearningPath.fromJson(Map<String, dynamic> jsonSerialization) {
    return LearningPath(
      id: jsonSerialization['id'] as int?,
      title: jsonSerialization['title'] as String,
      slug: jsonSerialization['slug'] as String,
      description: jsonSerialization['description'] as String?,
      thumbnailUrl: jsonSerialization['thumbnailUrl'] as String?,
      difficulty: jsonSerialization['difficulty'] as String,
      courseIds: jsonSerialization['courseIds'] as String,
      isPublished: jsonSerialization['isPublished'] as bool,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  static final t = LearningPathTable();

  static const db = LearningPathRepository._();

  @override
  int? id;

  String title;

  String slug;

  String? description;

  String? thumbnailUrl;

  String difficulty;

  String courseIds;

  bool isPublished;

  DateTime createdAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [LearningPath]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  LearningPath copyWith({
    int? id,
    String? title,
    String? slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    String? courseIds,
    bool? isPublished,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'slug': slug,
      if (description != null) 'description': description,
      if (thumbnailUrl != null) 'thumbnailUrl': thumbnailUrl,
      'difficulty': difficulty,
      'courseIds': courseIds,
      'isPublished': isPublished,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'slug': slug,
      if (description != null) 'description': description,
      if (thumbnailUrl != null) 'thumbnailUrl': thumbnailUrl,
      'difficulty': difficulty,
      'courseIds': courseIds,
      'isPublished': isPublished,
      'createdAt': createdAt.toJson(),
    };
  }

  static LearningPathInclude include() {
    return LearningPathInclude._();
  }

  static LearningPathIncludeList includeList({
    _i1.WhereExpressionBuilder<LearningPathTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LearningPathTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LearningPathTable>? orderByList,
    LearningPathInclude? include,
  }) {
    return LearningPathIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(LearningPath.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(LearningPath.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LearningPathImpl extends LearningPath {
  _LearningPathImpl({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? thumbnailUrl,
    String? difficulty,
    required String courseIds,
    bool? isPublished,
    required DateTime createdAt,
  }) : super._(
          id: id,
          title: title,
          slug: slug,
          description: description,
          thumbnailUrl: thumbnailUrl,
          difficulty: difficulty,
          courseIds: courseIds,
          isPublished: isPublished,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [LearningPath]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  LearningPath copyWith({
    Object? id = _Undefined,
    String? title,
    String? slug,
    Object? description = _Undefined,
    Object? thumbnailUrl = _Undefined,
    String? difficulty,
    String? courseIds,
    bool? isPublished,
    DateTime? createdAt,
  }) {
    return LearningPath(
      id: id is int? ? id : this.id,
      title: title ?? this.title,
      slug: slug ?? this.slug,
      description: description is String? ? description : this.description,
      thumbnailUrl: thumbnailUrl is String? ? thumbnailUrl : this.thumbnailUrl,
      difficulty: difficulty ?? this.difficulty,
      courseIds: courseIds ?? this.courseIds,
      isPublished: isPublished ?? this.isPublished,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}

class LearningPathTable extends _i1.Table<int?> {
  LearningPathTable({super.tableRelation})
      : super(tableName: 'learning_paths') {
    title = _i1.ColumnString(
      'title',
      this,
    );
    slug = _i1.ColumnString(
      'slug',
      this,
    );
    description = _i1.ColumnString(
      'description',
      this,
    );
    thumbnailUrl = _i1.ColumnString(
      'thumbnailUrl',
      this,
    );
    difficulty = _i1.ColumnString(
      'difficulty',
      this,
      hasDefault: true,
    );
    courseIds = _i1.ColumnString(
      'courseIds',
      this,
    );
    isPublished = _i1.ColumnBool(
      'isPublished',
      this,
      hasDefault: true,
    );
    createdAt = _i1.ColumnDateTime(
      'createdAt',
      this,
    );
  }

  late final _i1.ColumnString title;

  late final _i1.ColumnString slug;

  late final _i1.ColumnString description;

  late final _i1.ColumnString thumbnailUrl;

  late final _i1.ColumnString difficulty;

  late final _i1.ColumnString courseIds;

  late final _i1.ColumnBool isPublished;

  late final _i1.ColumnDateTime createdAt;

  @override
  List<_i1.Column> get columns => [
        id,
        title,
        slug,
        description,
        thumbnailUrl,
        difficulty,
        courseIds,
        isPublished,
        createdAt,
      ];
}

class LearningPathInclude extends _i1.IncludeObject {
  LearningPathInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => LearningPath.t;
}

class LearningPathIncludeList extends _i1.IncludeList {
  LearningPathIncludeList._({
    _i1.WhereExpressionBuilder<LearningPathTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(LearningPath.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => LearningPath.t;
}

class LearningPathRepository {
  const LearningPathRepository._();

  /// Returns a list of [LearningPath]s matching the given query parameters.
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
  Future<List<LearningPath>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LearningPathTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LearningPathTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LearningPathTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<LearningPath>(
      where: where?.call(LearningPath.t),
      orderBy: orderBy?.call(LearningPath.t),
      orderByList: orderByList?.call(LearningPath.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [LearningPath] matching the given query parameters.
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
  Future<LearningPath?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LearningPathTable>? where,
    int? offset,
    _i1.OrderByBuilder<LearningPathTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LearningPathTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<LearningPath>(
      where: where?.call(LearningPath.t),
      orderBy: orderBy?.call(LearningPath.t),
      orderByList: orderByList?.call(LearningPath.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [LearningPath] by its [id] or null if no such row exists.
  Future<LearningPath?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<LearningPath>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [LearningPath]s in the list and returns the inserted rows.
  ///
  /// The returned [LearningPath]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<LearningPath>> insert(
    _i1.Session session,
    List<LearningPath> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<LearningPath>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [LearningPath] and returns the inserted row.
  ///
  /// The returned [LearningPath] will have its `id` field set.
  Future<LearningPath> insertRow(
    _i1.Session session,
    LearningPath row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<LearningPath>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [LearningPath]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<LearningPath>> update(
    _i1.Session session,
    List<LearningPath> rows, {
    _i1.ColumnSelections<LearningPathTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<LearningPath>(
      rows,
      columns: columns?.call(LearningPath.t),
      transaction: transaction,
    );
  }

  /// Updates a single [LearningPath]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<LearningPath> updateRow(
    _i1.Session session,
    LearningPath row, {
    _i1.ColumnSelections<LearningPathTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<LearningPath>(
      row,
      columns: columns?.call(LearningPath.t),
      transaction: transaction,
    );
  }

  /// Deletes all [LearningPath]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<LearningPath>> delete(
    _i1.Session session,
    List<LearningPath> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<LearningPath>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [LearningPath].
  Future<LearningPath> deleteRow(
    _i1.Session session,
    LearningPath row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<LearningPath>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<LearningPath>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<LearningPathTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<LearningPath>(
      where: where(LearningPath.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LearningPathTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<LearningPath>(
      where: where?.call(LearningPath.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
