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

abstract class Announcement implements _i1.SerializableModel {
  Announcement._({
    this.id,
    required this.title,
    required this.message,
    String? type,
    String? targetAudience,
    this.targetCourseId,
    this.targetPlanId,
    bool? isDismissible,
    this.startsAt,
    this.endsAt,
    bool? isActive,
    this.createdBy,
    required this.createdAt,
  })  : type = type ?? 'banner',
        targetAudience = targetAudience ?? 'all',
        isDismissible = isDismissible ?? true,
        isActive = isActive ?? true;

  factory Announcement({
    int? id,
    required String title,
    required String message,
    String? type,
    String? targetAudience,
    int? targetCourseId,
    int? targetPlanId,
    bool? isDismissible,
    DateTime? startsAt,
    DateTime? endsAt,
    bool? isActive,
    int? createdBy,
    required DateTime createdAt,
  }) = _AnnouncementImpl;

  factory Announcement.fromJson(Map<String, dynamic> jsonSerialization) {
    return Announcement(
      id: jsonSerialization['id'] as int?,
      title: jsonSerialization['title'] as String,
      message: jsonSerialization['message'] as String,
      type: jsonSerialization['type'] as String,
      targetAudience: jsonSerialization['targetAudience'] as String,
      targetCourseId: jsonSerialization['targetCourseId'] as int?,
      targetPlanId: jsonSerialization['targetPlanId'] as int?,
      isDismissible: jsonSerialization['isDismissible'] as bool,
      startsAt: jsonSerialization['startsAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['startsAt']),
      endsAt: jsonSerialization['endsAt'] == null
          ? null
          : _i1.DateTimeJsonExtension.fromJson(jsonSerialization['endsAt']),
      isActive: jsonSerialization['isActive'] as bool,
      createdBy: jsonSerialization['createdBy'] as int?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  String title;

  String message;

  String type;

  String targetAudience;

  int? targetCourseId;

  int? targetPlanId;

  bool isDismissible;

  DateTime? startsAt;

  DateTime? endsAt;

  bool isActive;

  int? createdBy;

  DateTime createdAt;

  /// Returns a shallow copy of this [Announcement]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  Announcement copyWith({
    int? id,
    String? title,
    String? message,
    String? type,
    String? targetAudience,
    int? targetCourseId,
    int? targetPlanId,
    bool? isDismissible,
    DateTime? startsAt,
    DateTime? endsAt,
    bool? isActive,
    int? createdBy,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'title': title,
      'message': message,
      'type': type,
      'targetAudience': targetAudience,
      if (targetCourseId != null) 'targetCourseId': targetCourseId,
      if (targetPlanId != null) 'targetPlanId': targetPlanId,
      'isDismissible': isDismissible,
      if (startsAt != null) 'startsAt': startsAt?.toJson(),
      if (endsAt != null) 'endsAt': endsAt?.toJson(),
      'isActive': isActive,
      if (createdBy != null) 'createdBy': createdBy,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AnnouncementImpl extends Announcement {
  _AnnouncementImpl({
    int? id,
    required String title,
    required String message,
    String? type,
    String? targetAudience,
    int? targetCourseId,
    int? targetPlanId,
    bool? isDismissible,
    DateTime? startsAt,
    DateTime? endsAt,
    bool? isActive,
    int? createdBy,
    required DateTime createdAt,
  }) : super._(
          id: id,
          title: title,
          message: message,
          type: type,
          targetAudience: targetAudience,
          targetCourseId: targetCourseId,
          targetPlanId: targetPlanId,
          isDismissible: isDismissible,
          startsAt: startsAt,
          endsAt: endsAt,
          isActive: isActive,
          createdBy: createdBy,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [Announcement]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  Announcement copyWith({
    Object? id = _Undefined,
    String? title,
    String? message,
    String? type,
    String? targetAudience,
    Object? targetCourseId = _Undefined,
    Object? targetPlanId = _Undefined,
    bool? isDismissible,
    Object? startsAt = _Undefined,
    Object? endsAt = _Undefined,
    bool? isActive,
    Object? createdBy = _Undefined,
    DateTime? createdAt,
  }) {
    return Announcement(
      id: id is int? ? id : this.id,
      title: title ?? this.title,
      message: message ?? this.message,
      type: type ?? this.type,
      targetAudience: targetAudience ?? this.targetAudience,
      targetCourseId:
          targetCourseId is int? ? targetCourseId : this.targetCourseId,
      targetPlanId: targetPlanId is int? ? targetPlanId : this.targetPlanId,
      isDismissible: isDismissible ?? this.isDismissible,
      startsAt: startsAt is DateTime? ? startsAt : this.startsAt,
      endsAt: endsAt is DateTime? ? endsAt : this.endsAt,
      isActive: isActive ?? this.isActive,
      createdBy: createdBy is int? ? createdBy : this.createdBy,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
