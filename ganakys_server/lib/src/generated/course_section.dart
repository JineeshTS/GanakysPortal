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

abstract class CourseSection
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  CourseSection._({
    this.id,
    required this.courseId,
    required this.title,
    this.description,
    int? sortOrder,
  }) : sortOrder = sortOrder ?? 0;

  factory CourseSection({
    int? id,
    required int courseId,
    required String title,
    String? description,
    int? sortOrder,
  }) = _CourseSectionImpl;

  factory CourseSection.fromJson(Map<String, dynamic> jsonSerialization) {
    return CourseSection(
      id: jsonSerialization['id'] as int?,
      courseId: jsonSerialization['courseId'] as int,
      title: jsonSerialization['title'] as String,
      description: jsonSerialization['description'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
    );
  }

  static final t = CourseSectionTable();

  static const db = CourseSectionRepository._();

  @override
  int? id;

  int courseId;

  String title;

  String? description;

  int sortOrder;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [CourseSection]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  CourseSection copyWith({
    int? id,
    int? courseId,
    String? title,
    String? description,
    int? sortOrder,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      'title': title,
      if (description != null) 'description': description,
      'sortOrder': sortOrder,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'courseId': courseId,
      'title': title,
      if (description != null) 'description': description,
      'sortOrder': sortOrder,
    };
  }

  static CourseSectionInclude include() {
    return CourseSectionInclude._();
  }

  static CourseSectionIncludeList includeList({
    _i1.WhereExpressionBuilder<CourseSectionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseSectionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseSectionTable>? orderByList,
    CourseSectionInclude? include,
  }) {
    return CourseSectionIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(CourseSection.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(CourseSection.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CourseSectionImpl extends CourseSection {
  _CourseSectionImpl({
    int? id,
    required int courseId,
    required String title,
    String? description,
    int? sortOrder,
  }) : super._(
          id: id,
          courseId: courseId,
          title: title,
          description: description,
          sortOrder: sortOrder,
        );

  /// Returns a shallow copy of this [CourseSection]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  CourseSection copyWith({
    Object? id = _Undefined,
    int? courseId,
    String? title,
    Object? description = _Undefined,
    int? sortOrder,
  }) {
    return CourseSection(
      id: id is int? ? id : this.id,
      courseId: courseId ?? this.courseId,
      title: title ?? this.title,
      description: description is String? ? description : this.description,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }
}

class CourseSectionTable extends _i1.Table<int?> {
  CourseSectionTable({super.tableRelation})
      : super(tableName: 'course_sections') {
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    title = _i1.ColumnString(
      'title',
      this,
    );
    description = _i1.ColumnString(
      'description',
      this,
    );
    sortOrder = _i1.ColumnInt(
      'sortOrder',
      this,
      hasDefault: true,
    );
  }

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnString title;

  late final _i1.ColumnString description;

  late final _i1.ColumnInt sortOrder;

  @override
  List<_i1.Column> get columns => [
        id,
        courseId,
        title,
        description,
        sortOrder,
      ];
}

class CourseSectionInclude extends _i1.IncludeObject {
  CourseSectionInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => CourseSection.t;
}

class CourseSectionIncludeList extends _i1.IncludeList {
  CourseSectionIncludeList._({
    _i1.WhereExpressionBuilder<CourseSectionTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(CourseSection.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => CourseSection.t;
}

class CourseSectionRepository {
  const CourseSectionRepository._();

  /// Returns a list of [CourseSection]s matching the given query parameters.
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
  Future<List<CourseSection>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseSectionTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseSectionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseSectionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<CourseSection>(
      where: where?.call(CourseSection.t),
      orderBy: orderBy?.call(CourseSection.t),
      orderByList: orderByList?.call(CourseSection.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [CourseSection] matching the given query parameters.
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
  Future<CourseSection?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseSectionTable>? where,
    int? offset,
    _i1.OrderByBuilder<CourseSectionTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseSectionTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<CourseSection>(
      where: where?.call(CourseSection.t),
      orderBy: orderBy?.call(CourseSection.t),
      orderByList: orderByList?.call(CourseSection.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [CourseSection] by its [id] or null if no such row exists.
  Future<CourseSection?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<CourseSection>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [CourseSection]s in the list and returns the inserted rows.
  ///
  /// The returned [CourseSection]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<CourseSection>> insert(
    _i1.Session session,
    List<CourseSection> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<CourseSection>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [CourseSection] and returns the inserted row.
  ///
  /// The returned [CourseSection] will have its `id` field set.
  Future<CourseSection> insertRow(
    _i1.Session session,
    CourseSection row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<CourseSection>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [CourseSection]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<CourseSection>> update(
    _i1.Session session,
    List<CourseSection> rows, {
    _i1.ColumnSelections<CourseSectionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<CourseSection>(
      rows,
      columns: columns?.call(CourseSection.t),
      transaction: transaction,
    );
  }

  /// Updates a single [CourseSection]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<CourseSection> updateRow(
    _i1.Session session,
    CourseSection row, {
    _i1.ColumnSelections<CourseSectionTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<CourseSection>(
      row,
      columns: columns?.call(CourseSection.t),
      transaction: transaction,
    );
  }

  /// Deletes all [CourseSection]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<CourseSection>> delete(
    _i1.Session session,
    List<CourseSection> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<CourseSection>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [CourseSection].
  Future<CourseSection> deleteRow(
    _i1.Session session,
    CourseSection row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<CourseSection>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<CourseSection>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<CourseSectionTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<CourseSection>(
      where: where(CourseSection.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseSectionTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<CourseSection>(
      where: where?.call(CourseSection.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
