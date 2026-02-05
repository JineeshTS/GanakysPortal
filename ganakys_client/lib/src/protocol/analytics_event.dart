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

abstract class AnalyticsEvent implements _i1.SerializableModel {
  AnalyticsEvent._({
    this.id,
    this.userId,
    required this.eventType,
    this.eventData,
    this.sessionId,
    this.ipAddress,
    this.userAgent,
    required this.createdAt,
  });

  factory AnalyticsEvent({
    int? id,
    int? userId,
    required String eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    required DateTime createdAt,
  }) = _AnalyticsEventImpl;

  factory AnalyticsEvent.fromJson(Map<String, dynamic> jsonSerialization) {
    return AnalyticsEvent(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int?,
      eventType: jsonSerialization['eventType'] as String,
      eventData: jsonSerialization['eventData'] as String?,
      sessionId: jsonSerialization['sessionId'] as String?,
      ipAddress: jsonSerialization['ipAddress'] as String?,
      userAgent: jsonSerialization['userAgent'] as String?,
      createdAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['createdAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int? userId;

  String eventType;

  String? eventData;

  String? sessionId;

  String? ipAddress;

  String? userAgent;

  DateTime createdAt;

  /// Returns a shallow copy of this [AnalyticsEvent]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  AnalyticsEvent copyWith({
    int? id,
    int? userId,
    String? eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    DateTime? createdAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      if (userId != null) 'userId': userId,
      'eventType': eventType,
      if (eventData != null) 'eventData': eventData,
      if (sessionId != null) 'sessionId': sessionId,
      if (ipAddress != null) 'ipAddress': ipAddress,
      if (userAgent != null) 'userAgent': userAgent,
      'createdAt': createdAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _AnalyticsEventImpl extends AnalyticsEvent {
  _AnalyticsEventImpl({
    int? id,
    int? userId,
    required String eventType,
    String? eventData,
    String? sessionId,
    String? ipAddress,
    String? userAgent,
    required DateTime createdAt,
  }) : super._(
          id: id,
          userId: userId,
          eventType: eventType,
          eventData: eventData,
          sessionId: sessionId,
          ipAddress: ipAddress,
          userAgent: userAgent,
          createdAt: createdAt,
        );

  /// Returns a shallow copy of this [AnalyticsEvent]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  AnalyticsEvent copyWith({
    Object? id = _Undefined,
    Object? userId = _Undefined,
    String? eventType,
    Object? eventData = _Undefined,
    Object? sessionId = _Undefined,
    Object? ipAddress = _Undefined,
    Object? userAgent = _Undefined,
    DateTime? createdAt,
  }) {
    return AnalyticsEvent(
      id: id is int? ? id : this.id,
      userId: userId is int? ? userId : this.userId,
      eventType: eventType ?? this.eventType,
      eventData: eventData is String? ? eventData : this.eventData,
      sessionId: sessionId is String? ? sessionId : this.sessionId,
      ipAddress: ipAddress is String? ? ipAddress : this.ipAddress,
      userAgent: userAgent is String? ? userAgent : this.userAgent,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
