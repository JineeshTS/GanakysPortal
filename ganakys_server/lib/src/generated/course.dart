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

abstract class Course implements _i1.TableRow<int?>, _i1.ProtocolSerialization {
  Course._({
    this.id,
    required this.title,
    required this.slug,
    this.description,
    this.shortDescription,
    this.categoryId,
    String? difficulty,
    int? durationMinutes,
    this.thumbnailUrl,
    this.promoVideoUrl,
    bool? isPublished,
    bool? isFeatured,
    double? price,
    int? totalLectures,
    int? totalSections,
    this.generationStatus,
    this.generationJobId,
    this.qualityScore,
    this.instructorId,
    String? language,
    double? avgRating,
    int? reviewCount,
    int? enrollmentCount,
    this.metaTitle,
    this.metaDescription,
    this.ogImageUrl,
    int? version,
    required this.createdAt,
    required this.updatedAt,
  })  : difficulty = difficulty ?? 'beginner',
        durationMinutes = durationMinutes ?? 0,
        isPublished = isPublished ?? false,
        isFeatured = isFeatured ?? false,
        price = price ?? 0.0,
        totalLectures = totalLectures ?? 0,
        totalSections = totalSections ?? 0,
        language = language ?? 'en',
        avgRating = avgRating ?? 0.0,
        reviewCount = reviewCount ?? 0,
        enrollmentCount = enrollmentCount ?? 0,
        version = version ?? 1;

  factory Course({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? shortDescription,
    int? categoryId,
    String? difficulty,
    int? durationMinutes,
    String? thumbnailUrl,
    String? promoVideoUrl,
    bool? isPublished,
    bool? isFeatured,
    double? price,
    int? totalLectures,
    int? totalSections,
    String? generationStatus,
    int? generationJobId,
    double? qualityScore,
    int? instructorId,
    String? language,
    double? avgRating,
    int? reviewCount,
    int? enrollmentCount,
    String? metaTitle,
    String? metaDescription,
    String? ogImageUrl,
    int? version,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _CourseImpl;

  factory Course.fromJson(Map<String, dynamic> jsonSerialization) {
    return Course(
      id: jsonSerialization['id'] as int?,
      title: jsonSerialization['title'] as String,
      slug: jsonSerialization['slug'] as String,
      description: jsonSerialization['description'] as String?,
      shortDescription: jsonSerialization['shortDescription'] as String?,
      categoryId: jsonSerialization['categoryId'] as int?,
      difficulty: jsonSerialization['difficulty'] as String,
      durationMinutes: jsonSerialization['durationMinutes'] as int,
      thumbnailUrl: jsonSerialization['thumbnailUrl'] as String?,
      promoVideoUrl: jsonSerialization['promoVideoUrl'] as String?,
      isPublished: jsonSerialization['isPublished'] as bool,
      isFeatured: jsonSerialization['isFeatured'] as bool,
      price: (jsonSerialization['price'] as num).toDouble(),
      totalLectures: jsonSerialization['totalLectures'] as int,
      totalSections: jsonSerialization['totalSections'] as int,
      generationStatus: jsonSerialization['generationStatus'] as String?,
      generationJobId: jsonSerialization['generationJobId'] as int?,
      qualityScore: (jsonSerialization['qualityScore'] as num?)?.toDouble(),
      instructorId: jsonSerialization['instructorId'] as int?,
      language: jsonSerialization['language'] as String,
      avgRating: (jsonSerialization['avgRating'] as num).toDouble(),
      reviewCount: jsonSerialization['reviewCount'] as int,
      enrollmentCount: jsonSerialization['enrollmentCount'] as int,
      metaTitle: jsonSerialization['metaTitle'] as String?,
      metaDescription: jsonSerialization['metaDescription'] as String?,
      ogImageUrl: jsonSerialization['ogImageUrl'] as String?,
      version: jsonSerialization['version'] as int,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  static final t = CourseTable();

  static const db = CourseRepository._();

  @override
  int? id;

  String title;

  String slug;

  String? description;

  String? shortDescription;

  int? categoryId;

  String difficulty;

  int durationMinutes;

  String? thumbnailUrl;

  String? promoVideoUrl;

  bool isPublished;

  bool isFeatured;

  double price;

  int totalLectures;

  int totalSections;

  String? generationStatus;

  int? generationJobId;

  double? qualityScore;

  int? instructorId;

  String language;

  double avgRating;

  int reviewCount;

  int enrollmentCount;

  String? metaTitle;

  String? metaDescription;

  String? ogImageUrl;

  int version;

  DateTime createdAt;

  DateTime updatedAt;

  @override
  _i1.Table<int?> get table => t;

  /// Returns a shallow copy of this [Course]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Course copyWith({
    int? id,
    String? title,
    String? slug,
    String? description,
    String? shortDescription,
    int? categoryId,
    String? difficulty,
    int? durationMinutes,
    String? thumbnailUrl,
    String? promoVideoUrl,
    bool? isPublished,
    bool? isFeatured,
    double? price,
    int? totalLectures,
    int? totalSections,
    String? generationStatus,
    int? generationJobId,
    double? qualityScore,
    int? instructorId,
    String? language,
    double? avgRating,
    int? reviewCount,
    int? enrollmentCount,
    String? metaTitle,
    String? metaDescription,
    String? ogImageUrl,
    int? version,
    DateTime? createdAt,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'slug': slug,
      if (description != null) 'description': description,
      if (shortDescription != null) 'shortDescription': shortDescription,
      if (categoryId != null) 'categoryId': categoryId,
      'difficulty': difficulty,
      'durationMinutes': durationMinutes,
      if (thumbnailUrl != null) 'thumbnailUrl': thumbnailUrl,
      if (promoVideoUrl != null) 'promoVideoUrl': promoVideoUrl,
      'isPublished': isPublished,
      'isFeatured': isFeatured,
      'price': price,
      'totalLectures': totalLectures,
      'totalSections': totalSections,
      if (generationStatus != null) 'generationStatus': generationStatus,
      if (generationJobId != null) 'generationJobId': generationJobId,
      if (qualityScore != null) 'qualityScore': qualityScore,
      if (instructorId != null) 'instructorId': instructorId,
      'language': language,
      'avgRating': avgRating,
      'reviewCount': reviewCount,
      'enrollmentCount': enrollmentCount,
      if (metaTitle != null) 'metaTitle': metaTitle,
      if (metaDescription != null) 'metaDescription': metaDescription,
      if (ogImageUrl != null) 'ogImageUrl': ogImageUrl,
      'version': version,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  Map<String, dynamic> toJsonForProtocol() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'slug': slug,
      if (description != null) 'description': description,
      if (shortDescription != null) 'shortDescription': shortDescription,
      if (categoryId != null) 'categoryId': categoryId,
      'difficulty': difficulty,
      'durationMinutes': durationMinutes,
      if (thumbnailUrl != null) 'thumbnailUrl': thumbnailUrl,
      if (promoVideoUrl != null) 'promoVideoUrl': promoVideoUrl,
      'isPublished': isPublished,
      'isFeatured': isFeatured,
      'price': price,
      'totalLectures': totalLectures,
      'totalSections': totalSections,
      if (generationStatus != null) 'generationStatus': generationStatus,
      if (generationJobId != null) 'generationJobId': generationJobId,
      if (qualityScore != null) 'qualityScore': qualityScore,
      if (instructorId != null) 'instructorId': instructorId,
      'language': language,
      'avgRating': avgRating,
      'reviewCount': reviewCount,
      'enrollmentCount': enrollmentCount,
      if (metaTitle != null) 'metaTitle': metaTitle,
      if (metaDescription != null) 'metaDescription': metaDescription,
      if (ogImageUrl != null) 'ogImageUrl': ogImageUrl,
      'version': version,
      'createdAt': createdAt.toJson(),
      'updatedAt': updatedAt.toJson(),
    };
  }

  static CourseInclude include() {
    return CourseInclude._();
  }

  static CourseIncludeList includeList({
    _i1.WhereExpressionBuilder<CourseTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseTable>? orderByList,
    CourseInclude? include,
  }) {
    return CourseIncludeList._(
      where: where,
      limit: limit,
      offset: offset,
      orderBy: orderBy?.call(Course.t),
      orderDescending: orderDescending,
      orderByList: orderByList?.call(Course.t),
      include: include,
    );
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CourseImpl extends Course {
  _CourseImpl({
    int? id,
    required String title,
    required String slug,
    String? description,
    String? shortDescription,
    int? categoryId,
    String? difficulty,
    int? durationMinutes,
    String? thumbnailUrl,
    String? promoVideoUrl,
    bool? isPublished,
    bool? isFeatured,
    double? price,
    int? totalLectures,
    int? totalSections,
    String? generationStatus,
    int? generationJobId,
    double? qualityScore,
    int? instructorId,
    String? language,
    double? avgRating,
    int? reviewCount,
    int? enrollmentCount,
    String? metaTitle,
    String? metaDescription,
    String? ogImageUrl,
    int? version,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          title: title,
          slug: slug,
          description: description,
          shortDescription: shortDescription,
          categoryId: categoryId,
          difficulty: difficulty,
          durationMinutes: durationMinutes,
          thumbnailUrl: thumbnailUrl,
          promoVideoUrl: promoVideoUrl,
          isPublished: isPublished,
          isFeatured: isFeatured,
          price: price,
          totalLectures: totalLectures,
          totalSections: totalSections,
          generationStatus: generationStatus,
          generationJobId: generationJobId,
          qualityScore: qualityScore,
          instructorId: instructorId,
          language: language,
          avgRating: avgRating,
          reviewCount: reviewCount,
          enrollmentCount: enrollmentCount,
          metaTitle: metaTitle,
          metaDescription: metaDescription,
          ogImageUrl: ogImageUrl,
          version: version,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [Course]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Course copyWith({
    Object? id = _Undefined,
    String? title,
    String? slug,
    Object? description = _Undefined,
    Object? shortDescription = _Undefined,
    Object? categoryId = _Undefined,
    String? difficulty,
    int? durationMinutes,
    Object? thumbnailUrl = _Undefined,
    Object? promoVideoUrl = _Undefined,
    bool? isPublished,
    bool? isFeatured,
    double? price,
    int? totalLectures,
    int? totalSections,
    Object? generationStatus = _Undefined,
    Object? generationJobId = _Undefined,
    Object? qualityScore = _Undefined,
    Object? instructorId = _Undefined,
    String? language,
    double? avgRating,
    int? reviewCount,
    int? enrollmentCount,
    Object? metaTitle = _Undefined,
    Object? metaDescription = _Undefined,
    Object? ogImageUrl = _Undefined,
    int? version,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Course(
      id: id is int? ? id : this.id,
      title: title ?? this.title,
      slug: slug ?? this.slug,
      description: description is String? ? description : this.description,
      shortDescription: shortDescription is String?
          ? shortDescription
          : this.shortDescription,
      categoryId: categoryId is int? ? categoryId : this.categoryId,
      difficulty: difficulty ?? this.difficulty,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      thumbnailUrl: thumbnailUrl is String? ? thumbnailUrl : this.thumbnailUrl,
      promoVideoUrl:
          promoVideoUrl is String? ? promoVideoUrl : this.promoVideoUrl,
      isPublished: isPublished ?? this.isPublished,
      isFeatured: isFeatured ?? this.isFeatured,
      price: price ?? this.price,
      totalLectures: totalLectures ?? this.totalLectures,
      totalSections: totalSections ?? this.totalSections,
      generationStatus: generationStatus is String?
          ? generationStatus
          : this.generationStatus,
      generationJobId:
          generationJobId is int? ? generationJobId : this.generationJobId,
      qualityScore: qualityScore is double? ? qualityScore : this.qualityScore,
      instructorId: instructorId is int? ? instructorId : this.instructorId,
      language: language ?? this.language,
      avgRating: avgRating ?? this.avgRating,
      reviewCount: reviewCount ?? this.reviewCount,
      enrollmentCount: enrollmentCount ?? this.enrollmentCount,
      metaTitle: metaTitle is String? ? metaTitle : this.metaTitle,
      metaDescription:
          metaDescription is String? ? metaDescription : this.metaDescription,
      ogImageUrl: ogImageUrl is String? ? ogImageUrl : this.ogImageUrl,
      version: version ?? this.version,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class CourseTable extends _i1.Table<int?> {
  CourseTable({super.tableRelation}) : super(tableName: 'courses') {
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
    shortDescription = _i1.ColumnString(
      'shortDescription',
      this,
    );
    categoryId = _i1.ColumnInt(
      'categoryId',
      this,
    );
    difficulty = _i1.ColumnString(
      'difficulty',
      this,
      hasDefault: true,
    );
    durationMinutes = _i1.ColumnInt(
      'durationMinutes',
      this,
      hasDefault: true,
    );
    thumbnailUrl = _i1.ColumnString(
      'thumbnailUrl',
      this,
    );
    promoVideoUrl = _i1.ColumnString(
      'promoVideoUrl',
      this,
    );
    isPublished = _i1.ColumnBool(
      'isPublished',
      this,
      hasDefault: true,
    );
    isFeatured = _i1.ColumnBool(
      'isFeatured',
      this,
      hasDefault: true,
    );
    price = _i1.ColumnDouble(
      'price',
      this,
      hasDefault: true,
    );
    totalLectures = _i1.ColumnInt(
      'totalLectures',
      this,
      hasDefault: true,
    );
    totalSections = _i1.ColumnInt(
      'totalSections',
      this,
      hasDefault: true,
    );
    generationStatus = _i1.ColumnString(
      'generationStatus',
      this,
    );
    generationJobId = _i1.ColumnInt(
      'generationJobId',
      this,
    );
    qualityScore = _i1.ColumnDouble(
      'qualityScore',
      this,
    );
    instructorId = _i1.ColumnInt(
      'instructorId',
      this,
    );
    language = _i1.ColumnString(
      'language',
      this,
      hasDefault: true,
    );
    avgRating = _i1.ColumnDouble(
      'avgRating',
      this,
      hasDefault: true,
    );
    reviewCount = _i1.ColumnInt(
      'reviewCount',
      this,
      hasDefault: true,
    );
    enrollmentCount = _i1.ColumnInt(
      'enrollmentCount',
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
    ogImageUrl = _i1.ColumnString(
      'ogImageUrl',
      this,
    );
    version = _i1.ColumnInt(
      'version',
      this,
      hasDefault: true,
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

  late final _i1.ColumnString title;

  late final _i1.ColumnString slug;

  late final _i1.ColumnString description;

  late final _i1.ColumnString shortDescription;

  late final _i1.ColumnInt categoryId;

  late final _i1.ColumnString difficulty;

  late final _i1.ColumnInt durationMinutes;

  late final _i1.ColumnString thumbnailUrl;

  late final _i1.ColumnString promoVideoUrl;

  late final _i1.ColumnBool isPublished;

  late final _i1.ColumnBool isFeatured;

  late final _i1.ColumnDouble price;

  late final _i1.ColumnInt totalLectures;

  late final _i1.ColumnInt totalSections;

  late final _i1.ColumnString generationStatus;

  late final _i1.ColumnInt generationJobId;

  late final _i1.ColumnDouble qualityScore;

  late final _i1.ColumnInt instructorId;

  late final _i1.ColumnString language;

  late final _i1.ColumnDouble avgRating;

  late final _i1.ColumnInt reviewCount;

  late final _i1.ColumnInt enrollmentCount;

  late final _i1.ColumnString metaTitle;

  late final _i1.ColumnString metaDescription;

  late final _i1.ColumnString ogImageUrl;

  late final _i1.ColumnInt version;

  late final _i1.ColumnDateTime createdAt;

  late final _i1.ColumnDateTime updatedAt;

  @override
  List<_i1.Column> get columns => [
        id,
        title,
        slug,
        description,
        shortDescription,
        categoryId,
        difficulty,
        durationMinutes,
        thumbnailUrl,
        promoVideoUrl,
        isPublished,
        isFeatured,
        price,
        totalLectures,
        totalSections,
        generationStatus,
        generationJobId,
        qualityScore,
        instructorId,
        language,
        avgRating,
        reviewCount,
        enrollmentCount,
        metaTitle,
        metaDescription,
        ogImageUrl,
        version,
        createdAt,
        updatedAt,
      ];
}

class CourseInclude extends _i1.IncludeObject {
  CourseInclude._();

  @override
  Map<String, _i1.Include?> get includes => {};

  @override
  _i1.Table<int?> get table => Course.t;
}

class CourseIncludeList extends _i1.IncludeList {
  CourseIncludeList._({
    _i1.WhereExpressionBuilder<CourseTable>? where,
    super.limit,
    super.offset,
    super.orderBy,
    super.orderDescending,
    super.orderByList,
    super.include,
  }) {
    super.where = where?.call(Course.t);
  }

  @override
  Map<String, _i1.Include?> get includes => include?.includes ?? {};

  @override
  _i1.Table<int?> get table => Course.t;
}

class CourseRepository {
  const CourseRepository._();

  /// Returns a list of [Course]s matching the given query parameters.
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
  Future<List<Course>> find(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseTable>? where,
    int? limit,
    int? offset,
    _i1.OrderByBuilder<CourseTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.find<Course>(
      where: where?.call(Course.t),
      orderBy: orderBy?.call(Course.t),
      orderByList: orderByList?.call(Course.t),
      orderDescending: orderDescending,
      limit: limit,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Returns the first matching [Course] matching the given query parameters.
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
  Future<Course?> findFirstRow(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseTable>? where,
    int? offset,
    _i1.OrderByBuilder<CourseTable>? orderBy,
    bool orderDescending = false,
    _i1.OrderByListBuilder<CourseTable>? orderByList,
    _i1.Transaction? transaction,
  }) async {
    return session.db.findFirstRow<Course>(
      where: where?.call(Course.t),
      orderBy: orderBy?.call(Course.t),
      orderByList: orderByList?.call(Course.t),
      orderDescending: orderDescending,
      offset: offset,
      transaction: transaction,
    );
  }

  /// Finds a single [Course] by its [id] or null if no such row exists.
  Future<Course?> findById(
    _i1.Session session,
    int id, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.findById<Course>(
      id,
      transaction: transaction,
    );
  }

  /// Inserts all [Course]s in the list and returns the inserted rows.
  ///
  /// The returned [Course]s will have their `id` fields set.
  ///
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// insert, none of the rows will be inserted.
  Future<List<Course>> insert(
    _i1.Session session,
    List<Course> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insert<Course>(
      rows,
      transaction: transaction,
    );
  }

  /// Inserts a single [Course] and returns the inserted row.
  ///
  /// The returned [Course] will have its `id` field set.
  Future<Course> insertRow(
    _i1.Session session,
    Course row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.insertRow<Course>(
      row,
      transaction: transaction,
    );
  }

  /// Updates all [Course]s in the list and returns the updated rows. If
  /// [columns] is provided, only those columns will be updated. Defaults to
  /// all columns.
  /// This is an atomic operation, meaning that if one of the rows fails to
  /// update, none of the rows will be updated.
  Future<List<Course>> update(
    _i1.Session session,
    List<Course> rows, {
    _i1.ColumnSelections<CourseTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.update<Course>(
      rows,
      columns: columns?.call(Course.t),
      transaction: transaction,
    );
  }

  /// Updates a single [Course]. The row needs to have its id set.
  /// Optionally, a list of [columns] can be provided to only update those
  /// columns. Defaults to all columns.
  Future<Course> updateRow(
    _i1.Session session,
    Course row, {
    _i1.ColumnSelections<CourseTable>? columns,
    _i1.Transaction? transaction,
  }) async {
    return session.db.updateRow<Course>(
      row,
      columns: columns?.call(Course.t),
      transaction: transaction,
    );
  }

  /// Deletes all [Course]s in the list and returns the deleted rows.
  /// This is an atomic operation, meaning that if one of the rows fail to
  /// be deleted, none of the rows will be deleted.
  Future<List<Course>> delete(
    _i1.Session session,
    List<Course> rows, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.delete<Course>(
      rows,
      transaction: transaction,
    );
  }

  /// Deletes a single [Course].
  Future<Course> deleteRow(
    _i1.Session session,
    Course row, {
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteRow<Course>(
      row,
      transaction: transaction,
    );
  }

  /// Deletes all rows matching the [where] expression.
  Future<List<Course>> deleteWhere(
    _i1.Session session, {
    required _i1.WhereExpressionBuilder<CourseTable> where,
    _i1.Transaction? transaction,
  }) async {
    return session.db.deleteWhere<Course>(
      where: where(Course.t),
      transaction: transaction,
    );
  }

  /// Counts the number of rows matching the [where] expression. If omitted,
  /// will return the count of all rows in the table.
  Future<int> count(
    _i1.Session session, {
    _i1.WhereExpressionBuilder<CourseTable>? where,
    int? limit,
    _i1.Transaction? transaction,
  }) async {
    return session.db.count<Course>(
      where: where?.call(Course.t),
      limit: limit,
      transaction: transaction,
    );
  }
}
