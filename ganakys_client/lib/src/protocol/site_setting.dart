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

abstract class SiteSetting implements _i1.SerializableModel {
  SiteSetting._({
    this.id,
    required this.key,
    required this.value,
    this.updatedBy,
    required this.updatedAt,
  });

  factory SiteSetting({
    int? id,
    required String key,
    required String value,
    int? updatedBy,
    required DateTime updatedAt,
  }) = _SiteSettingImpl;

  factory SiteSetting.fromJson(Map<String, dynamic> jsonSerialization) {
    return SiteSetting(
      id: jsonSerialization['id'] as int?,
      key: jsonSerialization['key'] as String,
      value: jsonSerialization['value'] as String,
      updatedBy: jsonSerialization['updatedBy'] as int?,
      updatedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['updatedAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String key;

  String value;

  int? updatedBy;

  DateTime updatedAt;

  /// Returns a shallow copy of this [SiteSetting]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  SiteSetting copyWith({
    int? id,
    String? key,
    String? value,
    int? updatedBy,
    DateTime? updatedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'key': key,
      'value': value,
      if (updatedBy != null) 'updatedBy': updatedBy,
      'updatedAt': updatedAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _SiteSettingImpl extends SiteSetting {
  _SiteSettingImpl({
    int? id,
    required String key,
    required String value,
    int? updatedBy,
    required DateTime updatedAt,
  }) : super._(
          id: id,
          key: key,
          value: value,
          updatedBy: updatedBy,
          updatedAt: updatedAt,
        );

  /// Returns a shallow copy of this [SiteSetting]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  SiteSetting copyWith({
    Object? id = _Undefined,
    String? key,
    String? value,
    Object? updatedBy = _Undefined,
    DateTime? updatedAt,
  }) {
    return SiteSetting(
      id: id is int? ? id : this.id,
      key: key ?? this.key,
      value: value ?? this.value,
      updatedBy: updatedBy is int? ? updatedBy : this.updatedBy,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
