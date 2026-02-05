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

abstract class EmailTemplate
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  EmailTemplate._({
    this.id,
    required this.slug,
    required this.subject,
    required this.bodyHtml,
    this.bodyText,
    this.variables,
  });

  factory EmailTemplate({
    int? id,
    required String slug,
    required String subject,
    required String bodyHtml,
    String? bodyText,
    String? variables,
  }) = _EmailTemplateImpl;

  factory EmailTemplate.fromJson(Map<String, dynamic> jsonSerialization) {
    return EmailTemplate(
      id: jsonSerialization['id'] as int?,
      slug: jsonSerialization['slug'] as String,
      subject: jsonSerialization['subject'] as String,
      bodyHtml: jsonSerialization['bodyHtml'] as String,
      bodyText: jsonSerialization['bodyText'] as String?,
      variables: jsonSerialization['variables'] as String?,
    );
  }

  static final t = EmailTemplateTable();

  static const db = EmailTemplateRepository._();

  @override
  int? id;

  String slug;

  String subject;

  String bodyHtml;

  String? bodyText;

  String? variables;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [EmailTemplate]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  EmailTemplate copyWith({
    int? id,
    String? slug,
    String? subject,
    String? bodyHtml,
    String? bodyText,
    String? variables,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'slug': slug,
      'subject': subject,
      'bodyHtml': bodyHtml,
      if (bodyText != null) 'bodyText': bodyText,
      if (variables != null) 'variables': variables,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'slug': slug,
      'subject': subject,
      'bodyHtml': bodyHtml,
      if (bodyText != null) 'bodyText': bodyText,
      if (variables != null) 'variables': variables,
    };
  }

  static EmailTemplateInclude include() {
    return EmailTemplateInclude._();
  }

  static EmailTemplateIncludeList includeList({
    _i1.WhereExpressionBuilder<EmailTemplateTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<EmailTemplateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<EmailTemplateTable>? orderByList,
    EmailTemplateInclude? include,
  }) {
    return EmailTemplateIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(EmailTemplate.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(EmailTemplate.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _EmailTemplateImpl extends EmailTemplate {
  _EmailTemplateImpl({
    int? id,
    required String slug,
    required String subject,
    required String bodyHtml,
    String? bodyText,
    String? variables,
  }) : super._(
          id: id,
          slug: slug,
          subject: subject,
          bodyHtml: bodyHtml,
          bodyText: bodyText,
          variables: variables,
        );

  /// Returns a shallow copy of this [EmailTemplate]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  EmailTemplate copyWith({
    Object? id = _Undefined,
    String? slug,
    String? subject,
    String? bodyHtml,
    Object? bodyText = _Undefined,
    Object? variables = _Undefined,
  }) {
    return EmailTemplate(
      id: id is int? ? id : this.id,
      slug: slug ?? this.slug,
      subject: subject ?? this.subject,
      bodyHtml: bodyHtml ?? this.bodyHtml,
      bodyText: bodyText is String? ? bodyText : this.bodyText,
      variables: variables is String? ? variables : this.variables,
    );
  }
}

class EmailTemplateTable extends _i1.Table<int?> {
  EmailTemplateTable({super.tableRelation})
      : super(tableName: 'email_templates') {
    slug = _i1.ColumnString(
      'slug',
      this,
    );
    subject = _i1.ColumnString(
      'subject',
      this,
    );
    bodyHtml = _i1.ColumnString(
      'bodyHtml',
      this,
    );
    bodyText = _i1.ColumnString(
      'bodyText',
      this,
    );
    variables = _i1.ColumnString(
      'variables',
      this,
    );
  }

  late final _i1.ColumnString slug;

  late final _i1.ColumnString subject;

  late final _i1.ColumnString bodyHtml;

  late final _i1.ColumnString bodyText;

  late final _i1.ColumnString variables;

  @override
  List<_i1.Column> get columns => [
        id,
        slug,
        subject,
        bodyHtml,
        bodyText,
        variables,
      ];
}

class EmailTemplateInclude extends _i1.IncludeObject {
  EmailTemplateInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => EmailTemplate.t;
}

class EmailTemplateIncludeList extends _i1.IncludeList {
  EmailTemplateIncludeList._({
    _i1.WhereExpressionBuilder<EmailTemplateTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(EmailTemplate.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => EmailTemplate.t;
}

class EmailTemplateRepository {
  const EmailTemplateRepository._();

  /// Returns a list of [EmailTemplate]s matching the given query parameters.
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
  Future<List<EmailTemplate>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<EmailTemplateTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<EmailTemplateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<EmailTemplateTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<EmailTemplate>(
      where: where?.call(EmailTemplate.t),
      orderBy: orderBy?.call(EmailTemplate.t),
      orderByList: orderByList?.call(EmailTemplate.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [EmailTemplate] matching the given query parameters.
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
  Future<EmailTemplate?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<EmailTemplateTable>? where,
    int? offset,
    _i1.OrderByBuilder<EmailTemplateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<EmailTemplateTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<EmailTemplate>(
      where: where?.call(EmailTemplate.t),
      orderBy: orderBy?.call(EmailTemplate.t),
      orderByList: orderByList?.call(EmailTemplate.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [EmailTemplate] by its [id] or null if no such row exists.
  Future<EmailTemplate?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<EmailTemplate>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [EmailTemplate]s in the list and returns the inserted rows.
  ///
  /// The returned [EmailTemplate]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<EmailTemplate>> insert(
    _i1.Session session,
    List<EmailTemplate> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<EmailTemplate>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [EmailTemplate] and returns the inserted row.
  ///
  /// The returned [EmailTemplate] will have its `id` field set.
  Future<EmailTemplate> insertRow(
    _i1.Session session,
    EmailTemplate row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<EmailTemplate>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [EmailTemplate]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<EmailTemplate>> update(
    _i1.Session session,
    List<EmailTemplate> rows, {
    _i1.ColumnSelections<EmailTemplateTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<EmailTemplate>(
      rows,
      columns: columns?.call(EmailTemplate.t),
      transaction: transaction,
    );
  }

  /// Updates a single [EmailTemplate]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<EmailTemplate> updateRow(
    _i1.Session session,
    EmailTemplate row, {
    _i1.ColumnSelections<EmailTemplateTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<EmailTemplate>(
      row,
      columns: columns?.call(EmailTemplate.t),
      transaction: transaction,
    );
  }

  /// Deletes all [EmailTemplate]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<EmailTemplate>> delete(
    _i1.Session session,
    List<EmailTemplate> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<EmailTemplate>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [EmailTemplate].
  Future<EmailTemplate> deleteRow(
    _i1.Session session,
    EmailTemplate row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<EmailTemplate>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<EmailTemplate>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<EmailTemplateTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<EmailTemplate>(
      where: where(EmailTemplate.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<EmailTemplateTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<EmailTemplate>(
      where: where?.call(EmailTemplate.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
