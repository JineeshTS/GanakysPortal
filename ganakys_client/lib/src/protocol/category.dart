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

abstract class Category implements _i1.SerializableModel {
  Category._({
    this.id,
    required this.name,
    required this.slug,
    this.description,
    this.icon,
    this.parentId,
    int? sortOrder,
    int? courseCount,
    required this.createdAt,
  })  : sortOrder = sortOrder ?? 0,
        courseCount = courseCount ?? 0;

  factory Category({
    int? id,
    required String name,
    required String slug,
    String? description,
    String? icon,
    int? parentId,
    int? sortOrder,
    int? courseCount,
    required DateTime createdAt,
  }) = _CategoryImpl;

  factory Category.fromJson(Map<String, dynamic> jsonSerialization) {
    return Category(
      id: jsonSerialization['id'] as int?,
      name: jsonSerialization['name'] as String,
      slug: jsonSerialization['slug'] as String,
      description: jsonSerialization['description'] as String?,
      icon: jsonSerialization['icon'] as String?,
      parentId: jsonSerialization['parentId'] as int?,
      sortOrder: jsonSerialization['sortOrder'] as int,
      courseCount: jsonSerialization['courseCount'] as int,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String name;

  String slug;

  String? description;

  String? icon;

  int? parentId;

  int sortOrder;

  int courseCount;

  DateTime createdAt;

  /// Returns a shallow copy of this [Category]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Category copyWith({
    int? id,
    String? name,
    String? slug,
    String? description,
    String? icon,
    int? parentId,
    int? sortOrder,
    int? courseCount,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'name': name,
      'slug': slug,
      if (description != null) 'description': description,
      if (icon != null) 'icon': icon,
      if (parentId != null) 'parentId': parentId,
      'sortOrder': sortOrder,
      'courseCount': courseCount,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _CategoryImpl extends Category {
  _CategoryImpl({
    int? id,
    required String name,
    required String slug,
    String? description,
    String? icon,
    int? parentId,
    int? sortOrder,
    int? courseCount,
    required DateTime createdAt,
  }) : super._(
          id: id,
          name: name,
          slug: slug,
          description: description,
          icon: icon,
          parentId: parentId,
          sortOrder: sortOrder,
          courseCount: courseCount,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Category]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Category copyWith({
    Object? id = _Undefined,
    String? name,
    String? slug,
    Object? description = _Undefined,
    Object? icon = _Undefined,
    Object? parentId = _Undefined,
    int? sortOrder,
    int? courseCount,
    DateTime? createdAt,
  }) {
    return Category(
      id: id is int? ? id : this.id,
      name: name ?? this.name,
      slug: slug ?? this.slug,
      description: description is String? ? description : this.description,
      icon: icon is String? ? icon : this.icon,
      parentId: parentId is int? ? parentId : this.parentId,
      sortOrder: sortOrder ?? this.sortOrder,
      courseCount: courseCount ?? this.courseCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
