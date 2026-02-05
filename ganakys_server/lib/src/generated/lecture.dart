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

abstract class Lecture
    implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Lecture._({
    this.id,
    required this.sectionId,
    required this.courseId,
    required this.title,
    String? type,
    int? durationMinutes,
    this.videoUrl,
    this.audioUrl,
    this.content,
    this.scriptJson,
    this.slidesJson,
    int? sortOrder,
    bool? isFreePreview,
    int? version,
  })  : type = type ?? 'video',
        durationMinutes = durationMinutes ?? 0,
        sortOrder = sortOrder ?? 0,
        isFreePreview = isFreePreview ?? false,
        version = version ?? 1;

  factory Lecture({
    int? id,
    required int sectionId,
    required int courseId,
    required String title,
    String? type,
    int? durationMinutes,
    String? videoUrl,
    String? audioUrl,
    String? content,
    String? scriptJson,
    String? slidesJson,
    int? sortOrder,
    bool? isFreePreview,
    int? version,
  }) = _LectureImpl;

  factory Lecture.fromJson(Map<String, dynamic> jsonSerialization) {
    return Lecture(
      id: jsonSerialization['id'] as int?,
      sectionId: jsonSerialization['sectionId'] as int,
      courseId: jsonSerialization['courseId'] as int,
      title: jsonSerialization['title'] as String,
      type: jsonSerialization['type'] as String,
      durationMinutes: jsonSerialization['durationMinutes'] as int,
      videoUrl: jsonSerialization['videoUrl'] as String?,
      audioUrl: jsonSerialization['audioUrl'] as String?,
      content: jsonSerialization['content'] as String?,
      scriptJson: jsonSerialization['scriptJson'] as String?,
      slidesJson: jsonSerialization['slidesJson'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
      isFreePreview: jsonSerialization['isFreePreview'] as bool,
      version: jsonSerialization['version'] as int,
    );
  }

  static final t = LectureTable();

  static const db = LectureRepository._();

  @override
  int? id;

  int sectionId;

  int courseId;

  String title;

  String type;

  int durationMinutes;

  String? videoUrl;

  String? audioUrl;

  String? content;

  String? scriptJson;

  String? slidesJson;

  int sortOrder;

  bool isFreePreview;

  int version;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Lecture]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Lecture copyWith({
    int? id,
    int? sectionId,
    int? courseId,
    String? title,
    String? type,
    int? durationMinutes,
    String? videoUrl,
    String? audioUrl,
    String? content,
    String? scriptJson,
    String? slidesJson,
    int? sortOrder,
    bool? isFreePreview,
    int? version,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'sectionId': sectionId,
      'courseId': courseId,
      'title': title,
      'type': type,
      'durationMinutes': durationMinutes,
      if (videoUrl != null) 'videoUrl': videoUrl,
      if (audioUrl != null) 'audioUrl': audioUrl,
      if (content != null) 'content': content,
      if (scriptJson != null) 'scriptJson': scriptJson,
      if (slidesJson != null) 'slidesJson': slidesJson,
      'sortOrder': sortOrder,
      'isFreePreview': isFreePreview,
      'version': version,
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'sectionId': sectionId,
      'courseId': courseId,
      'title': title,
      'type': type,
      'durationMinutes': durationMinutes,
      if (videoUrl != null) 'videoUrl': videoUrl,
      if (audioUrl != null) 'audioUrl': audioUrl,
      if (content != null) 'content': content,
      if (scriptJson != null) 'scriptJson': scriptJson,
      if (slidesJson != null) 'slidesJson': slidesJson,
      'sortOrder': sortOrder,
      'isFreePreview': isFreePreview,
      'version': version,
    };
  }

  static LectureInclude include() {
    return LectureInclude._();
  }

  static LectureIncludeList includeList({
    _i1.WhereExpressionBuilder<LectureTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LectureTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureTable>? orderByList,
    LectureInclude? include,
  }) {
    return LectureIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Lecture.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Lecture.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _LectureImpl extends Lecture {
  _LectureImpl({
    int? id,
    required int sectionId,
    required int courseId,
    required String title,
    String? type,
    int? durationMinutes,
    String? videoUrl,
    String? audioUrl,
    String? content,
    String? scriptJson,
    String? slidesJson,
    int? sortOrder,
    bool? isFreePreview,
    int? version,
  }) : super._(
          id: id,
          sectionId: sectionId,
          courseId: courseId,
          title: title,
          type: type,
          durationMinutes: durationMinutes,
          videoUrl: videoUrl,
          audioUrl: audioUrl,
          content: content,
          scriptJson: scriptJson,
          slidesJson: slidesJson,
          sortOrder: sortOrder,
          isFreePreview: isFreePreview,
          version: version,
        );

  /// Returns a shallow copy of this [Lecture]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Lecture copyWith({
    Object? id = _Undefined,
    int? sectionId,
    int? courseId,
    String? title,
    String? type,
    int? durationMinutes,
    Object? videoUrl = _Undefined,
    Object? audioUrl = _Undefined,
    Object? content = _Undefined,
    Object? scriptJson = _Undefined,
    Object? slidesJson = _Undefined,
    int? sortOrder,
    bool? isFreePreview,
    int? version,
  }) {
    return Lecture(
      id: id is int? ? id : this.id,
      sectionId: sectionId ?? this.sectionId,
      courseId: courseId ?? this.courseId,
      title: title ?? this.title,
      type: type ?? this.type,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      videoUrl: videoUrl is String? ? videoUrl : this.videoUrl,
      audioUrl: audioUrl is String? ? audioUrl : this.audioUrl,
      content: content is String? ? content : this.content,
      scriptJson: scriptJson is String? ? scriptJson : this.scriptJson,
      slidesJson: slidesJson is String? ? slidesJson : this.slidesJson,
      sortOrder: sortOrder ?? this.sortOrder,
      isFreePreview: isFreePreview ?? this.isFreePreview,
      version: version ?? this.version,
    );
  }
}

class LectureTable extends _i1.Table<int?> {
  LectureTable({super.tableRelation}) : super(tableName: 'lectures') {
    sectionId = _i1.ColumnInt(
      'sectionId',
      this,
    );
    courseId = _i1.ColumnInt(
      'courseId',
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
    durationMinutes = _i1.ColumnInt(
      'durationMinutes',
      this,
      hasDefault: true,
    );
    videoUrl = _i1.ColumnString(
      'videoUrl',
      this,
    );
    audioUrl = _i1.ColumnString(
      'audioUrl',
      this,
    );
    content = _i1.ColumnString(
      'content',
      this,
    );
    scriptJson = _i1.ColumnString(
      'scriptJson',
      this,
    );
    slidesJson = _i1.ColumnString(
      'slidesJson',
      this,
    );
    sortOrder = _i1.ColumnInt(
      'sortOrder',
      this,
      hasDefault: true,
    );
    isFreePreview = _i1.ColumnBool(
      'isFreePreview',
      this,
      hasDefault: true,
    );
    version = _i1.ColumnInt(
      'version',
      this,
      hasDefault: true,
    );
  }

  late final _i1.ColumnInt sectionId;

  late final _i1.ColumnInt courseId;

  late final _i1.ColumnString title;

  late final _i1.ColumnString type;

  late final _i1.ColumnInt durationMinutes;

  late final _i1.ColumnString videoUrl;

  late final _i1.ColumnString audioUrl;

  late final _i1.ColumnString content;

  late final _i1.ColumnString scriptJson;

  late final _i1.ColumnString slidesJson;

  late final _i1.ColumnInt sortOrder;

  late final _i1.ColumnBool isFreePreview;

  late final _i1.ColumnInt version;

  @override
  List<_i1.Column> get columns => [
        id,
        sectionId,
        courseId,
        title,
        type,
        durationMinutes,
        videoUrl,
        audioUrl,
        content,
        scriptJson,
        slidesJson,
        sortOrder,
        isFreePreview,
        version,
      ];
}

class LectureInclude extends _i1.IncludeObject {
  LectureInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Lecture.t;
}

class LectureIncludeList extends _i1.IncludeList {
  LectureIncludeList._({
    _i1.WhereExpressionBuilder<LectureTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Lecture.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Lecture.t;
}

class LectureRepository {
  const LectureRepository._();

  /// Returns a list of [Lecture]s matching the given query parameters.
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
  Future<List<Lecture>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<LectureTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Lecture>(
      where: where?.call(Lecture.t),
      orderBy: orderBy?.call(Lecture.t),
      orderByList: orderByList?.call(Lecture.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Lecture] matching the given query parameters.
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
  Future<Lecture?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureTable>? where,
    int? offset,
    _i1.OrderByBuilder<LectureTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<LectureTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Lecture>(
      where: where?.call(Lecture.t),
      orderBy: orderBy?.call(Lecture.t),
      orderByList: orderByList?.call(Lecture.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Lecture] by its [id] or null if no such row exists.
  Future<Lecture?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Lecture>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Lecture]s in the list and returns the inserted rows.
  ///
  /// The returned [Lecture]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Lecture>> insert(
    _i1.Session session,
    List<Lecture> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Lecture>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Lecture] and returns the inserted row.
  ///
  /// The returned [Lecture] will have its `id` field set.
  Future<Lecture> insertRow(
    _i1.Session session,
    Lecture row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Lecture>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Lecture]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Lecture>> update(
    _i1.Session session,
    List<Lecture> rows, {
    _i1.ColumnSelections<LectureTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Lecture>(
      rows,
      columns: columns?.call(Lecture.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Lecture]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Lecture> updateRow(
    _i1.Session session,
    Lecture row, {
    _i1.ColumnSelections<LectureTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Lecture>(
      row,
      columns: columns?.call(Lecture.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Lecture]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Lecture>> delete(
    _i1.Session session,
    List<Lecture> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Lecture>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Lecture].
  Future<Lecture> deleteRow(
    _i1.Session session,
    Lecture row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Lecture>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Lecture>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<LectureTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Lecture>(
      where: where(Lecture.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<LectureTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Lecture>(
      where: where?.call(Lecture.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
