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

abstract class Certificate implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int courseId;

  String certificateNumber;

  String? pdfUrl;

  bool isRevoked;

  DateTime issuedAt;

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
