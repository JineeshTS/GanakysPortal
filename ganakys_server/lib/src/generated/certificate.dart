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

abstract class Certificate
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Certificate._({
    this.id,
    required this.userId,
    required this.courseId,
    required this.certificateNumber,
    this.pdfUrl,
    bool? isRevoked,
    required this.issuedAt,
  }) : isRevoked = isRevoked ?? false;

  factory Certificate({
    int? id,
    required int userId,
    required int courseId,
    required String certificateNumber,
    String? pdfUrl,
    bool? isRevoked,
    required DateTime issuedAt,
  }) = _CertificateImpl;

  factory Certificate.fromJson(Map<String, dynamic> jsonSerialization) {
    return Certificate(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      certificateNumber: jsonSerialization['certificateNumber'] as String,
      pdfUrl: jsonSerialization['pdfUrl'] as String?,
      isRevoked: jsonSerialization['isRevoked'] as bool,
      issuedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['issuedAt']),
    );
  }

  static final t = CertificateTable();

  static const db = CertificateRepository._();

  @override
  int? id;

  int userId;

  int courseId;

  String certificateNumber;

  String? pdfUrl;

  bool isRevoked;

  DateTime issuedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Certificate]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Certificate copyWith({
    int? id,
    int? userId,
    int? courseId,
    String? certificateNumber,
    String? pdfUrl,
    bool? isRevoked,
    DateTime? issuedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'certificateNumber': certificateNumber,
      if (pdfUrl != null) 'pdfUrl': pdfUrl,
      'isRevoked': isRevoked,
      'issuedAt': issuedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'courseId': courseId,
      'certificateNumber': certificateNumber,
      if (pdfUrl != null) 'pdfUrl': pdfUrl,
      'isRevoked': isRevoked,
      'issuedAt': issuedAt.toJson(),
    };
  }

  static CertificateInclude include() {
    return CertificateInclude._();
  }

  static CertificateIncludeList includeList({
    _i1.WhereExpressionBuilder<CertificateTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CertificateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CertificateTable>? orderByList,
    CertificateInclude? include,
  }) {
    return CertificateIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Certificate.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Certificate.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CertificateImpl extends Certificate {
  _CertificateImpl({
    int? id,
    required int userId,
    required int courseId,
    required String certificateNumber,
    String? pdfUrl,
    bool? isRevoked,
    required DateTime issuedAt,
  }) : super._(
          id: id,
          userId: userId,
          courseId: courseId,
          certificateNumber: certificateNumber,
          pdfUrl: pdfUrl,
          isRevoked: isRevoked,
          issuedAt: issuedAt,
        );

  /// Returns a shallow copy of this [Certificate]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Certificate copyWith({
    Object? id = _Undefined,
    int? userId,
    int? courseId,
    String? certificateNumber,
    Object? pdfUrl = _Undefined,
    bool? isRevoked,
    DateTime? issuedAt,
  }) {
    return Certificate(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      courseId: courseId ?? this.courseId,
      certificateNumber: certificateNumber ?? this.certificateNumber,
      pdfUrl: pdfUrl is String? ? pdfUrl : this.pdfUrl,
      isRevoked: isRevoked ?? this.isRevoked,
      issuedAt: issuedAt ?? this.issuedAt,
    );
  }
}

class CertificateTable extends _i1.Table<int?> {
  CertificateTable({super.tableRelation}) : super(tableName: 'certificates') {
    userId = _i1.ColumnInt(
      'userId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
      this,
    );
    certificateNumber = _i1.ColumnString(
      'certificateNumber',
      this,
    );
    pdfUrl = _i1.ColumnString(
      'pdfUrl',
      this,
    );
    isRevoked = _i1.ColumnBool(
      'isRevoked',
      this,
      hasDefault: true,
    );
    issuedAt = _i1.ColumnDateTime(
      'issuedAt',
      this,
    );
  }

  late final _i1.ColumnInt userId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnString certificateNumber;

  late final _i1.ColumnString pdfUrl;

  late final _i1.ColumnBool isRevoked;

  late final _i1.ColumnDateTime issuedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        userId,
        courseId,
        certificateNumber,
        pdfUrl,
        isRevoked,
        issuedAt,
      ];
}

class CertificateInclude extends _i1.IncludeObject {
  CertificateInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Certificate.t;
}

class CertificateIncludeList extends _i1.IncludeList {
  CertificateIncludeList._({
    _i1.WhereExpressionBuilder<CertificateTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Certificate.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Certificate.t;
}

class CertificateRepository {
  const CertificateRepository._();

  /// Returns a list of [Certificate]s matching the given query parameters.
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
  Future<List<Certificate>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CertificateTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CertificateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CertificateTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Certificate>(
      where: where?.call(Certificate.t),
      orderBy: orderBy?.call(Certificate.t),
      orderByList: orderByList?.call(Certificate.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Certificate] matching the given query parameters.
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
  Future<Certificate?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CertificateTable>? where,
    int? offset,
    _i1.OrderByBuilder<CertificateTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CertificateTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Certificate>(
      where: where?.call(Certificate.t),
      orderBy: orderBy?.call(Certificate.t),
      orderByList: orderByList?.call(Certificate.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Certificate] by its [id] or null if no such row exists.
  Future<Certificate?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Certificate>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Certificate]s in the list and returns the inserted rows.
  ///
  /// The returned [Certificate]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Certificate>> insert(
    _i1.Session session,
    List<Certificate> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Certificate>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Certificate] and returns the inserted row.
  ///
  /// The returned [Certificate] will have its `id` field set.
  Future<Certificate> insertRow(
    _i1.Session session,
    Certificate row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Certificate>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Certificate]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Certificate>> update(
    _i1.Session session,
    List<Certificate> rows, {
    _i1.ColumnSelections<CertificateTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Certificate>(
      rows,
      columns: columns?.call(Certificate.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Certificate]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Certificate> updateRow(
    _i1.Session session,
    Certificate row, {
    _i1.ColumnSelections<CertificateTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Certificate>(
      row,
      columns: columns?.call(Certificate.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Certificate]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Certificate>> delete(
    _i1.Session session,
    List<Certificate> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Certificate>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Certificate].
  Future<Certificate> deleteRow(
    _i1.Session session,
    Certificate row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Certificate>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Certificate>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<CertificateTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Certificate>(
      where: where(Certificate.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CertificateTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Certificate>(
      where: where?.call(Certificate.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
