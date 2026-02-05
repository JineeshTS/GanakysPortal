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

abstract class QuizAttempt implements _i1.SerializableModel {
  QuizAttempt._({
    this.id,
    required this.userId,
    required this.quizId,
    required this.score,
    required this.answers,
    required this.passed,
    required this.attemptedAt,
  });

  factory QuizAttempt({
    int? id,
    required int userId,
    required int quizId,
    required double score,
    required String answers,
    required bool passed,
    required DateTime attemptedAt,
  }) = _QuizAttemptImpl;

  factory QuizAttempt.fromJson(Map<String, dynamic> jsonSerialization) {
    return QuizAttempt(
      id: jsonSerialization['id'] as int?,
      userId: jsonSerialization['userId'] as int,
      quizId: jsonSerialization['quizId'] as int,
      score: (jsonSerialization['score'] as num).toDouble(),
      answers: jsonSerialization['answers'] as String,
      passed: jsonSerialization['passed'] as bool,
      attemptedAt:
          _i1.DateTimeJsonExtension.fromJson(jsonSerialization['attemptedAt']),
    );
  }

  /// The database id, set if the object has been inserted into the
  /// database or if it has been fetched from the database. Otherwise,
  /// the id will be null.
  int? id;

  int userId;

  int quizId;

  double score;

  String answers;

  bool passed;

  DateTime attemptedAt;

  /// Returns a shallow copy of this [QuizAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  QuizAttempt copyWith({
    int? id,
    int? userId,
    int? quizId,
    double? score,
    String? answers,
    bool? passed,
    DateTime? attemptedAt,
  });
  @override
  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'userId': userId,
      'quizId': quizId,
      'score': score,
      'answers': answers,
      'passed': passed,
      'attemptedAt': attemptedAt.toJson(),
    };
  }

  @override
  String toString() {
    return _i1.SerializationManager.encode(this);
  }
}

class _Undefined {}

class _QuizAttemptImpl extends QuizAttempt {
  _QuizAttemptImpl({
    int? id,
    required int userId,
    required int quizId,
    required double score,
    required String answers,
    required bool passed,
    required DateTime attemptedAt,
  }) : super._(
          id: id,
          userId: userId,
          quizId: quizId,
          score: score,
          answers: answers,
          passed: passed,
          attemptedAt: attemptedAt,
        );

  /// Returns a shallow copy of this [QuizAttempt]
  /// with some or all fields replaced by the given arguments.
  @_i1.useResult
  @override
  QuizAttempt copyWith({
    Object? id = _Undefined,
    int? userId,
    int? quizId,
    double? score,
    String? answers,
    bool? passed,
    DateTime? attemptedAt,
  }) {
    return QuizAttempt(
      id: id is int? ? id : this.id,
      userId: userId ?? this.userId,
      quizId: quizId ?? this.quizId,
      score: score ?? this.score,
      answers: answers ?? this.answers,
      passed: passed ?? this.passed,
      attemptedAt: attemptedAt ?? this.attemptedAt,
    );
  }
}
