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

abstract class ContentPage
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  ContentPage._({
    this.id,
    required this.slug,
    required this.title,
    required this.content,
    bool? isPublished,
    this.metaTitle,
    this.metaDescription,
    int? version,
    required this.updatedAt,
  })  : isPublished = isPublished ?? true,
        version = version ?? 1;

  factory ContentPage({
    int? id,
    required String slug,
    required String title,
    required String content,
    bool? isPublished,
    String? metaTitle,
    String? metaDescription,
    int? version,
    required DateTime updatedAt,
  }) = _ContentPageImpl;

  factory ContentPage.fromJson(Map<String, dynamic> jsonSerialization) {
    return ContentPage(
      id: jsonSerialization['id'] as int?,
      slug: jsonSerialization['slug'] as String,
      title: jsonSerialization['title'] as String,
      content: jsonSerialization['content'] as String,
      isPublished: jsonSerialization['isPublished'] as bool,
      metaTitle: jsonSerialization['metaTitle'] as String?,
      metaDescription: jsonSerialization['metaDescription'] as String?,
      version: jsonSerialization['version'] as int,
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = ContentPageTable();

  static const db = ContentPageRepository._();

  @override
  int? id;

  String slug;

  String title;

  String content;

  bool isPublished;

  String? metaTitle;

  String? metaDescription;

  int version;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [ContentPage]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  ContentPage copyWith({
    int? id,
    String? slug,
    String? title,
    String? content,
    bool? isPublished,
    String? metaTitle,
    String? metaDescription,
    int? version,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'slug': slug,
      'title': title,
      'content': content,
      'isPublished': isPublished,
      if (metaTitle != null) 'metaTitle': metaTitle,
      if (metaDescription != null) 'metaDescription': metaDescription,
      'version': version,
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'slug': slug,
      'title': title,
      'content': content,
      'isPublished': isPublished,
      if (metaTitle != null) 'metaTitle': metaTitle,
      if (metaDescription != null) 'metaDescription': metaDescription,
      'version': version,
      'updatedAt': updatedAt.toJson(),
    };
  }

  static ContentPageInclude include() {
    return ContentPageInclude._();
  }

  static ContentPageIncludeList includeList({
    _i1.WhereExpressionBuilder<ContentPageTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<ContentPageTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ContentPageTable>? orderByList,
    ContentPageInclude? include,
  }) {
    return ContentPageIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(ContentPage.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(ContentPage.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _ContentPageImpl extends ContentPage {
  _ContentPageImpl({
    int? id,
    required String slug,
    required String title,
    required String content,
    bool? isPublished,
    String? metaTitle,
    String? metaDescription,
    int? version,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          slug: slug,
          title: title,
          content: content,
          isPublished: isPublished,
          metaTitle: metaTitle,
          metaDescription: metaDescription,
          version: version,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [ContentPage]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  ContentPage copyWith({
    Object? id = _Undefined,
    String? slug,
    String? title,
    String? content,
    bool? isPublished,
    Object? metaTitle = _Undefined,
    Object? metaDescription = _Undefined,
    int? version,
    DateTime? updatedAt,
  }) {
    return ContentPage(
      id: id is int? ? id : this.id,
      slug: slug ?? this.slug,
      title: title ?? this.title,
      content: content ?? this.content,
      isPublished: isPublished ?? this.isPublished,
      metaTitle: metaTitle is String? ? metaTitle : this.metaTitle,
      metaDescription:
          metaDescription is String? ? metaDescription : this.metaDescription,
      version: version ?? this.version,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class ContentPageTable extends _i1.Table<int?> {
  ContentPageTable({super.tableRelation}) : super(tableName: 'pages') {
    slug = _i1.ColumnString(
      'slug',
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
    isPublished = _i1.ColumnBool(
      'isPublished',
      this,
      hasDefault: true,
    );
    metaTitle = _i1.ColumnString(
      'metaTitle',
      this,
    );
    metaDescription = _i1.ColumnString(
      'metaDescription',
      this,
    );
    version = _i1.ColumnInt(
      'version',
      this,
      hasDefault: true,
    );
    updatedAt = _i1.ColumnDateTime(
      'updatedAt',
      this,
    );
  }

  late final _i1.ColumnString slug;

  late final _i1.ColumnString title;

  late final _i1.ColumnString content;

  late final _i1.ColumnBool isPublished;

  late final _i1.ColumnString metaTitle;

  late final _i1.ColumnString metaDescription;

  late final _i1.ColumnInt version;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        slug,
        title,
        content,
        isPublished,
        metaTitle,
        metaDescription,
        version,
        updatedAt,
      ];
}

class ContentPageInclude extends _i1.IncludeObject {
  ContentPageInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => ContentPage.t;
}

class ContentPageIncludeList extends _i1.IncludeList {
  ContentPageIncludeList._({
    _i1.WhereExpressionBuilder<ContentPageTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(ContentPage.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => ContentPage.t;
}

class ContentPageRepository {
  const ContentPageRepository._();

  /// Returns a list of [ContentPage]s matching the given query parameters.
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
  Future<List<ContentPage>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ContentPageTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<ContentPageTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ContentPageTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<ContentPage>(
      where: where?.call(ContentPage.t),
      orderBy: orderBy?.call(ContentPage.t),
      orderByList: orderByList?.call(ContentPage.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [ContentPage] matching the given query parameters.
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
  Future<ContentPage?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ContentPageTable>? where,
    int? offset,
    _i1.OrderByBuilder<ContentPageTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<ContentPageTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<ContentPage>(
      where: where?.call(ContentPage.t),
      orderBy: orderBy?.call(ContentPage.t),
      orderByList: orderByList?.call(ContentPage.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [ContentPage] by its [id] or null if no such row exists.
  Future<ContentPage?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<ContentPage>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [ContentPage]s in the list and returns the inserted rows.
  ///
  /// The returned [ContentPage]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<ContentPage>> insert(
    _i1.Session session,
    List<ContentPage> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<ContentPage>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [ContentPage] and returns the inserted row.
  ///
  /// The returned [ContentPage] will have its `id` field set.
  Future<ContentPage> insertRow(
    _i1.Session session,
    ContentPage row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<ContentPage>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [ContentPage]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<ContentPage>> update(
    _i1.Session session,
    List<ContentPage> rows, {
    _i1.ColumnSelections<ContentPageTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<ContentPage>(
      rows,
      columns: columns?.call(ContentPage.t),
      transaction: transaction,
    );
  }

  /// Updates a single [ContentPage]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<ContentPage> updateRow(
    _i1.Session session,
    ContentPage row, {
    _i1.ColumnSelections<ContentPageTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<ContentPage>(
      row,
      columns: columns?.call(ContentPage.t),
      transaction: transaction,
    );
  }

  /// Deletes all [ContentPage]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<ContentPage>> delete(
    _i1.Session session,
    List<ContentPage> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<ContentPage>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [ContentPage].
  Future<ContentPage> deleteRow(
    _i1.Session session,
    ContentPage row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<ContentPage>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<ContentPage>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<ContentPageTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<ContentPage>(
      where: where(ContentPage.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<ContentPageTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<ContentPage>(
      where: where?.call(ContentPage.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
