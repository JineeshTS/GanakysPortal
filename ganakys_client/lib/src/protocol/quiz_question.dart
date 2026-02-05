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

abstract class QuizQuestion implements _i1.SerializableModel {
  QuizQuestion._({
    this.id,
    required this.quizId,
    required this.question,
    required this.options,
    this.explanation,
    int? sortOrder,
  }) : sortOrder = sortOrder ?? 0;

  factory QuizQuestion({
    int? id,
    required int quizId,
    required String question,
    required String options,
    String? explanation,
    int? sortOrder,
  }) = _QuizQuestionImpl;

  factory QuizQuestion.fromJson(Map<String, dynamic> jsonSerialization) {
    return QuizQuestion(
      id: jsonSerialization['id'] as int?,
      quizId: jsonSerialization['quizId'] as int,
      question: jsonSerialization['question'] as String,
      options: jsonSerialization['options'] as String,
      explanation: jsonSerialization['explanation'] as String?,
      sortOrder: jsonSerialization['sortOrder'] as int,
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int quizId;

  String question;

  String options;

  String? explanation;

  int sortOrder;

  /// Returns a shallow copy of this [QuizQuestion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  QuizQuestion copyWith({
    int? id,
    int? quizId,
    String? question,
    String? options,
    String? explanation,
    int? sortOrder,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'quizId': quizId,
      'question': question,
      'options': options,
      if (explanation != null) 'explanation': explanation,
      'sortOrder': sortOrder,
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizQuestionImpl extends QuizQuestion {
  _QuizQuestionImpl({
    int? id,
    required int quizId,
    required String question,
    required String options,
    String? explanation,
    int? sortOrder,
  }) : super._(
          id: id,
          quizId: quizId,
          question: question,
          options: options,
          explanation: explanation,
          sortOrder: sortOrder,
        );

  /// Returns a shallow copy of this [QuizQuestion]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  QuizQuestion copyWith({
    Object? id = _Undefined,
    int? quizId,
    String? question,
    String? options,
    Object? explanation = _Undefined,
    int? sortOrder,
  }) {
    return QuizQuestion(
      id: id is int? ? id : this.id,
      quizId: quizId ?? this.quizId,
      question: question ?? this.question,
      options: options ?? this.options,
      explanation: explanation is String? ? explanation : this.explanation,
      sortOrder: sortOrder ?? this.sortOrder,
    );
  }
}
