/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod_client/serverpod_client.dart' as _i1;

abstract class Course implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
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
