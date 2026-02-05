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

abstract class EmailTemplate implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String slug;

  String subject;

  String bodyHtml;

  String? bodyText;

  String? variables;

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
