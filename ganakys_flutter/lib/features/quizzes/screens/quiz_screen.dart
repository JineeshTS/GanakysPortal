import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';

import '../../../core/client_provider.dart';
import '../../../core/providers/auth_provider.dart';

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

class _QuizState {
  final bool isLoading;
  final String? error;
  final String quizTitle;
  final int passPercentage;
  final List<_QuestionData> questions;
  final Map<int, int> selectedAnswers; // questionId -> optionIndex
  final QuizAttempt? result;
  final bool isSubmitting;

  const _QuizState({
    this.isLoading = false,
    this.error,
    this.quizTitle = '',
    this.passPercentage = 70,
    this.questions = const [],
    this.selectedAnswers = const {},
    this.result,
    this.isSubmitting = false,
  });

  bool get isCompleted => result != null;
  bool get allAnswered => selectedAnswers.length == questions.length;
}

class _QuestionData {
  final int id;
  final String question;
  final List<_OptionData> options;
  final String? explanation;

  const _QuestionData({
    required this.id,
    required this.question,
    required this.options,
    this.explanation,
  });
}

class _OptionData {
  final String text;
  final bool isCorrect;

  const _OptionData({required this.text, required this.isCorrect});
}

// ---------------------------------------------------------------------------
// Screen
// ---------------------------------------------------------------------------

class QuizScreen extends ConsumerStatefulWidget {
  final int quizId;

  const QuizScreen({super.key, required this.quizId});

  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  _QuizState _state = const _QuizState();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _loadQuiz();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadQuiz() async {
    setState(() {
      _state = const _QuizState(isLoading: true);
    });
    try {
      final client = ref.read(clientProvider);
      final data = await client.quiz.getQuiz(widget.quizId);
      if (data == null) {
        setState(() {
          _state = const _QuizState(error: 'Quiz not found');
        });
        return;
      }

      final quizData = data['quiz'] as Map<String, dynamic>?;
      final questionsRaw =
          (data['questions'] as List?)?.cast<Map<String, dynamic>>() ?? [];

      final questions = questionsRaw.map((q) {
        final optionsJson = q['options'] as String? ?? '[]';
        final optionsList =
            (jsonDecode(optionsJson) as List).cast<Map<String, dynamic>>();
        return _QuestionData(
          id: q['id'] as int,
          question: q['question'] as String? ?? '',
          explanation: q['explanation'] as String?,
          options: optionsList.map((o) {
            return _OptionData(
              text: o['text'] as String? ?? '',
              isCorrect: o['isCorrect'] as bool? ?? false,
            );
          }).toList(),
        );
      }).toList();

      setState(() {
        _state = _QuizState(
          quizTitle: quizData?['title'] as String? ?? 'Quiz',
          passPercentage: quizData?['passPercentage'] as int? ?? 70,
          questions: questions,
        );
      });
    } catch (e) {
      setState(() {
        _state = _QuizState(error: 'Failed to load quiz: $e');
      });
    }
  }

  void _selectAnswer(int questionId, int optionIndex) {
    if (_state.isCompleted) return;
    setState(() {
      _state = _QuizState(
        quizTitle: _state.quizTitle,
        passPercentage: _state.passPercentage,
        questions: _state.questions,
        selectedAnswers: {
          ..._state.selectedAnswers,
          questionId: optionIndex,
        },
      );
    });
  }

  Future<void> _submitQuiz() async {
    if (!_state.allAnswered || _state.isSubmitting) return;
    setState(() {
      _state = _QuizState(
        quizTitle: _state.quizTitle,
        passPercentage: _state.passPercentage,
        questions: _state.questions,
        selectedAnswers: _state.selectedAnswers,
        isSubmitting: true,
      );
    });

    try {
      final client = ref.read(clientProvider);
      final userId = ref.read(authProvider).user?.id ?? 0;

      final answersPayload = _state.selectedAnswers.entries.map((e) {
        return {'questionId': e.key, 'selectedOption': e.value};
      }).toList();

      final attempt = await client.quiz.submitQuizAttempt(
        userId,
        widget.quizId,
        jsonEncode(answersPayload),
      );

      setState(() {
        _state = _QuizState(
          quizTitle: _state.quizTitle,
          passPercentage: _state.passPercentage,
          questions: _state.questions,
          selectedAnswers: _state.selectedAnswers,
          result: attempt,
        );
      });

      // Scroll to top to show results
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    } catch (e) {
      setState(() {
        _state = _QuizState(
          quizTitle: _state.quizTitle,
          passPercentage: _state.passPercentage,
          questions: _state.questions,
          selectedAnswers: _state.selectedAnswers,
          error: 'Failed to submit quiz: $e',
        );
      });
    }
  }

  void _retry() {
    setState(() {
      _state = _QuizState(
        quizTitle: _state.quizTitle,
        passPercentage: _state.passPercentage,
        questions: _state.questions,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: Text(_state.quizTitle, style: theme.textTheme.titleMedium),
      ),
      body: _buildBody(theme, colorScheme),
    );
  }

  Widget _buildBody(ThemeData theme, ColorScheme colorScheme) {
    if (_state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_state.error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: colorScheme.error),
              const SizedBox(height: 16),
              Text(
                _state.error!,
                style: theme.textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loadQuiz,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    if (_state.questions.isEmpty) {
      return Center(
        child: Text(
          'This quiz has no questions.',
          style: theme.textTheme.bodyLarge?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      );
    }

    return Column(
      children: [
        // Result banner
        if (_state.isCompleted) _ResultBanner(state: _state, onRetry: _retry),
        // Questions
        Expanded(
          child: ListView.builder(
            controller: _scrollController,
            padding: const EdgeInsets.all(16),
            itemCount: _state.questions.length,
            itemBuilder: (context, index) {
              final q = _state.questions[index];
              return _QuestionCard(
                index: index,
                question: q,
                selectedOption: _state.selectedAnswers[q.id],
                showResults: _state.isCompleted,
                onSelect: (optionIndex) => _selectAnswer(q.id, optionIndex),
              );
            },
          ),
        ),
        // Submit bar
        if (!_state.isCompleted)
          _SubmitBar(
            allAnswered: _state.allAnswered,
            answeredCount: _state.selectedAnswers.length,
            totalCount: _state.questions.length,
            isSubmitting: _state.isSubmitting,
            onSubmit: _submitQuiz,
          ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Result banner
// ---------------------------------------------------------------------------

class _ResultBanner extends StatelessWidget {
  final _QuizState state;
  final VoidCallback onRetry;

  const _ResultBanner({required this.state, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final result = state.result!;
    final passed = result.passed;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      color: passed
          ? colorScheme.primaryContainer.withValues(alpha: 0.5)
          : colorScheme.errorContainer.withValues(alpha: 0.5),
      child: Column(
        children: [
          Icon(
            passed ? Icons.celebration : Icons.sentiment_dissatisfied,
            size: 48,
            color: passed ? colorScheme.primary : colorScheme.error,
          ),
          const SizedBox(height: 12),
          Text(
            passed ? 'Congratulations! You Passed!' : 'Not Quite There Yet',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: passed ? colorScheme.primary : colorScheme.error,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Score: ${result.score.toStringAsFixed(0)}%  (Pass: ${state.passPercentage}%)',
            style: theme.textTheme.bodyLarge,
          ),
          if (!passed) ...[
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('Try Again'),
            ),
          ],
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Question card
// ---------------------------------------------------------------------------

class _QuestionCard extends StatelessWidget {
  final int index;
  final _QuestionData question;
  final int? selectedOption;
  final bool showResults;
  final ValueChanged<int> onSelect;

  const _QuestionCard({
    required this.index,
    required this.question,
    this.selectedOption,
    required this.showResults,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Question ${index + 1}',
              style: theme.textTheme.labelMedium?.copyWith(
                color: colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              question.question,
              style: theme.textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 16),
            ...List.generate(question.options.length, (optIndex) {
              final option = question.options[optIndex];
              final isSelected = selectedOption == optIndex;
              final isCorrect = option.isCorrect;

              Color? tileColor;
              Color? borderColor;
              if (showResults) {
                if (isCorrect) {
                  tileColor = Colors.green.withValues(alpha: 0.1);
                  borderColor = Colors.green;
                } else if (isSelected && !isCorrect) {
                  tileColor = Colors.red.withValues(alpha: 0.1);
                  borderColor = Colors.red;
                }
              } else if (isSelected) {
                tileColor = colorScheme.primaryContainer.withValues(alpha: 0.5);
                borderColor = colorScheme.primary;
              }

              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Material(
                  color: tileColor ?? Colors.transparent,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: BorderSide(
                      color: borderColor ?? colorScheme.outlineVariant,
                    ),
                  ),
                  child: InkWell(
                    onTap: showResults ? null : () => onSelect(optIndex),
                    borderRadius: BorderRadius.circular(8),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 10),
                      child: Row(
                        children: [
                          _optionIndicator(
                              optIndex, isSelected, showResults, isCorrect,
                              colorScheme),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(option.text,
                                style: theme.textTheme.bodyMedium),
                          ),
                          if (showResults && isCorrect)
                            const Icon(Icons.check_circle,
                                color: Colors.green, size: 20),
                          if (showResults && isSelected && !isCorrect)
                            const Icon(Icons.cancel,
                                color: Colors.red, size: 20),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }),
            // Explanation
            if (showResults &&
                question.explanation != null &&
                question.explanation!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Explanation',
                      style: theme.textTheme.labelMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      question.explanation!,
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _optionIndicator(
      int optIndex, bool isSelected, bool showResults, bool isCorrect,
      ColorScheme colorScheme) {
    final letter = String.fromCharCode(65 + optIndex); // A, B, C, D
    Color bgColor;
    Color fgColor;

    if (showResults && isCorrect) {
      bgColor = Colors.green;
      fgColor = Colors.white;
    } else if (showResults && isSelected && !isCorrect) {
      bgColor = Colors.red;
      fgColor = Colors.white;
    } else if (isSelected) {
      bgColor = colorScheme.primary;
      fgColor = colorScheme.onPrimary;
    } else {
      bgColor = colorScheme.surfaceContainerHighest;
      fgColor = colorScheme.onSurface;
    }

    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        color: bgColor,
        shape: BoxShape.circle,
      ),
      child: Center(
        child: Text(
          letter,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.bold,
            color: fgColor,
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Submit bar
// ---------------------------------------------------------------------------

class _SubmitBar extends StatelessWidget {
  final bool allAnswered;
  final int answeredCount;
  final int totalCount;
  final bool isSubmitting;
  final VoidCallback onSubmit;

  const _SubmitBar({
    required this.allAnswered,
    required this.answeredCount,
    required this.totalCount,
    required this.isSubmitting,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        border: Border(
          top: BorderSide(color: colorScheme.outlineVariant),
        ),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Text(
              '$answeredCount / $totalCount answered',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            const Spacer(),
            FilledButton(
              onPressed: allAnswered && !isSubmitting ? onSubmit : null,
              child: isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }
}
