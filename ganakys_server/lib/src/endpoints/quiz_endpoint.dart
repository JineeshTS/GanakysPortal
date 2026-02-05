import 'dart:convert';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class QuizEndpoint extends Endpoint {
  /// Returns all quizzes for a given course, each with its questions attached.
  Future<List<Map<String, dynamic>>> getQuizzesForCourse(
    Session session,
    int courseId,
  ) async {
    final quizzes = await Quiz.db.find(
      session,
      where: (t) => t.courseId.equals(courseId),
      orderBy: (t) => t.title,
    );

    final result = <Map<String, dynamic>>[];
    for (final quiz in quizzes) {
      final questions = await QuizQuestion.db.find(
        session,
        where: (t) => t.quizId.equals(quiz.id!),
        orderBy: (t) => t.sortOrder,
      );
      result.add({
        'quiz': quiz.toJson(),
        'questions': questions.map((q) => q.toJson()).toList(),
      });
    }

    return result;
  }

  /// Returns a single quiz by ID with its questions.
  Future<Map<String, dynamic>?> getQuiz(
    Session session,
    int quizId,
  ) async {
    final quiz = await Quiz.db.findById(session, quizId);
    if (quiz == null) return null;

    final questions = await QuizQuestion.db.find(
      session,
      where: (t) => t.quizId.equals(quizId),
      orderBy: (t) => t.sortOrder,
    );

    return {
      'quiz': quiz.toJson(),
      'questions': questions.map((q) => q.toJson()).toList(),
    };
  }

  /// Scores a quiz attempt and saves it to the database.
  ///
  /// [answersJson] is expected to be a JSON-encoded array of objects, each with
  /// `questionId` (int) and `selectedOption` (int index). The options JSON for
  /// each question is expected to contain objects with an `isCorrect` boolean
  /// field so that scoring can be performed server-side.
  ///
  /// Returns the saved [QuizAttempt] with the computed score and pass/fail.
  Future<QuizAttempt> submitQuizAttempt(
    Session session,
    int userId,
    int quizId,
    String answersJson,
  ) async {
    final quiz = await Quiz.db.findById(session, quizId);
    if (quiz == null) {
      throw Exception('Quiz not found');
    }

    final questions = await QuizQuestion.db.find(
      session,
      where: (t) => t.quizId.equals(quizId),
    );

    // Build a lookup of questionId -> question
    final questionMap = {for (final q in questions) q.id!: q};

    // Parse submitted answers
    final List<dynamic> answers = jsonDecode(answersJson) as List<dynamic>;

    int correctCount = 0;
    final totalQuestions = questions.length;

    for (final answer in answers) {
      final questionId = answer['questionId'] as int;
      final selectedOption = answer['selectedOption'] as int;
      final question = questionMap[questionId];
      if (question == null) continue;

      // Parse the options JSON to determine correctness.
      // Expected format: [{"text": "...", "isCorrect": true/false}, ...]
      final List<dynamic> options =
          jsonDecode(question.options) as List<dynamic>;
      if (selectedOption >= 0 && selectedOption < options.length) {
        final option = options[selectedOption] as Map<String, dynamic>;
        if (option['isCorrect'] == true) {
          correctCount++;
        }
      }
    }

    // Calculate score as a percentage
    final double score =
        totalQuestions > 0 ? (correctCount / totalQuestions) * 100.0 : 0.0;
    final bool passed = score >= quiz.passPercentage;

    final attempt = QuizAttempt(
      userId: userId,
      quizId: quizId,
      score: score,
      answers: answersJson,
      passed: passed,
      attemptedAt: DateTime.now().toUtc(),
    );

    final savedAttempt = await QuizAttempt.db.insertRow(session, attempt);
    return savedAttempt;
  }

  /// Returns all quiz attempts for a user within a given course, ordered by
  /// most recent first.
  Future<List<QuizAttempt>> getQuizAttempts(
    Session session,
    int userId,
    int courseId,
  ) async {
    // First, get all quiz IDs belonging to this course
    final quizzes = await Quiz.db.find(
      session,
      where: (t) => t.courseId.equals(courseId),
    );

    if (quizzes.isEmpty) return [];

    final quizIds = quizzes.map((q) => q.id!).toSet();

    // Fetch attempts for all quizzes in this course for the given user
    final attempts = await QuizAttempt.db.find(
      session,
      where: (t) =>
          t.userId.equals(userId) & t.quizId.inSet(quizIds),
      orderBy: (t) => t.attemptedAt,
      orderDescending: true,
    );

    return attempts;
  }
}
