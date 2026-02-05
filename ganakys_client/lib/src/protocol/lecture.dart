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

abstract class Lecture implements _i1.SerializableModel {
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

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
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
