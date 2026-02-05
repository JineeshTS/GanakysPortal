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

abstract class ContentPage implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String slug;

  String title;

  String content;

  bool isPublished;

  String? metaTitle;

  String? metaDescription;

  int version;

  DateTime updatedAt;

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
