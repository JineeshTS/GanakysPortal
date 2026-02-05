import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';

import '../client_provider.dart';
import 'auth_provider.dart';

// ---------------------------------------------------------------------------
// Data models for curriculum (parsed from the Map<String,dynamic> response)
// ---------------------------------------------------------------------------

class LectureItem {
  final int id;
  final String title;
  final String type;
  final int durationMinutes;
  final String? videoUrl;
  final String? audioUrl;
  final String? content;
  final bool isFreePreview;
  final bool isCompleted;
  final int lastPositionSeconds;
  final int sectionId;

  const LectureItem({
    required this.id,
    required this.title,
    required this.type,
    required this.durationMinutes,
    this.videoUrl,
    this.audioUrl,
    this.content,
    this.isFreePreview = false,
    this.isCompleted = false,
    this.lastPositionSeconds = 0,
    required this.sectionId,
  });

  LectureItem copyWith({
    bool? isCompleted,
    int? lastPositionSeconds,
  }) {
    return LectureItem(
      id: id,
      title: title,
      type: type,
      durationMinutes: durationMinutes,
      videoUrl: videoUrl,
      audioUrl: audioUrl,
      content: content,
      isFreePreview: isFreePreview,
      isCompleted: isCompleted ?? this.isCompleted,
      lastPositionSeconds: lastPositionSeconds ?? this.lastPositionSeconds,
      sectionId: sectionId,
    );
  }
}

class SectionItem {
  final int id;
  final String title;
  final List<LectureItem> lectures;

  const SectionItem({
    required this.id,
    required this.title,
    required this.lectures,
  });
}

// ---------------------------------------------------------------------------
// Player state
// ---------------------------------------------------------------------------

class PlayerState {
  final bool isLoading;
  final String? error;
  final Map<String, dynamic>? courseData;
  final List<SectionItem> sections;
  final int? currentLectureId;
  final bool isEnrolled;
  final int courseId;
  final String courseTitle;
  final List<StudentNote> notes;
  final List<Bookmark> bookmarks;
  final VideoPlayerController? videoController;
  final ChewieController? chewieController;
  final bool videoReady;

  const PlayerState({
    this.isLoading = false,
    this.error,
    this.courseData,
    this.sections = const [],
    this.currentLectureId,
    this.isEnrolled = false,
    this.courseId = 0,
    this.courseTitle = '',
    this.notes = const [],
    this.bookmarks = const [],
    this.videoController,
    this.chewieController,
    this.videoReady = false,
  });

  List<LectureItem> get allLectures {
    final result = <LectureItem>[];
    for (final s in sections) {
      result.addAll(s.lectures);
    }
    return result;
  }

  LectureItem? get currentLecture {
    if (currentLectureId == null) return null;
    final all = allLectures;
    for (final l in all) {
      if (l.id == currentLectureId) return l;
    }
    return null;
  }

  int get currentLectureIndex {
    if (currentLectureId == null) return -1;
    final all = allLectures;
    for (int i = 0; i < all.length; i++) {
      if (all[i].id == currentLectureId) return i;
    }
    return -1;
  }

  LectureItem? get nextLecture {
    final idx = currentLectureIndex;
    final all = allLectures;
    if (idx >= 0 && idx < all.length - 1) return all[idx + 1];
    return null;
  }

  int get completedCount => allLectures.where((l) => l.isCompleted).length;
  int get totalCount => allLectures.length;
  double get progressPercent =>
      totalCount > 0 ? completedCount / totalCount : 0;

  PlayerState copyWith({
    bool? isLoading,
    String? error,
    Map<String, dynamic>? courseData,
    List<SectionItem>? sections,
    int? currentLectureId,
    bool? isEnrolled,
    int? courseId,
    String? courseTitle,
    List<StudentNote>? notes,
    List<Bookmark>? bookmarks,
    VideoPlayerController? videoController,
    ChewieController? chewieController,
    bool? videoReady,
    bool clearError = false,
    bool clearVideo = false,
    bool clearCurrentLecture = false,
  }) {
    return PlayerState(
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      courseData: courseData ?? this.courseData,
      sections: sections ?? this.sections,
      currentLectureId: clearCurrentLecture
          ? null
          : (currentLectureId ?? this.currentLectureId),
      isEnrolled: isEnrolled ?? this.isEnrolled,
      courseId: courseId ?? this.courseId,
      courseTitle: courseTitle ?? this.courseTitle,
      notes: notes ?? this.notes,
      bookmarks: bookmarks ?? this.bookmarks,
      videoController:
          clearVideo ? null : (videoController ?? this.videoController),
      chewieController:
          clearVideo ? null : (chewieController ?? this.chewieController),
      videoReady: clearVideo ? false : (videoReady ?? this.videoReady),
    );
  }
}

// ---------------------------------------------------------------------------
// StateNotifier
// ---------------------------------------------------------------------------

class PlayerNotifier extends StateNotifier<PlayerState> {
  final Client _client;
  final int? _userId;
  Timer? _progressTimer;

  PlayerNotifier(this._client, this._userId) : super(const PlayerState());

  @override
  void dispose() {
    _progressTimer?.cancel();
    _disposeVideo();
    super.dispose();
  }

  void _disposeVideo() {
    state.chewieController?.dispose();
    state.videoController?.dispose();
  }

  // -----------------------------------------------------------------------
  // Load curriculum
  // -----------------------------------------------------------------------

  Future<void> loadCurriculum(String courseSlug, {int? initialLectureId}) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      // First get course by slug to obtain courseId
      final courseDetail = await _client.course.getCourseBySlug(courseSlug);
      if (courseDetail == null) {
        state = state.copyWith(isLoading: false, error: 'Course not found');
        return;
      }

      final courseId = courseDetail['id'] as int;
      final courseTitle = courseDetail['title'] as String? ?? courseSlug;
      final userId = _userId ?? 0;

      // Load curriculum
      final curriculum =
          await _client.course.getCourseCurriculum(courseId, userId);

      if (curriculum == null) {
        state = state.copyWith(
          isLoading: false,
          error: 'Could not load course content',
        );
        return;
      }

      // Parse sections
      final rawSections =
          (curriculum['sections'] as List?)?.cast<Map<String, dynamic>>() ?? [];
      final sections = <SectionItem>[];
      for (final rs in rawSections) {
        final sectionId = rs['id'] as int;
        final rawLectures =
            (rs['lectures'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final lectures = rawLectures.map((rl) {
          return LectureItem(
            id: rl['id'] as int,
            title: rl['title'] as String? ?? 'Untitled',
            type: rl['type'] as String? ?? 'video',
            durationMinutes: rl['durationMinutes'] as int? ?? 0,
            videoUrl: rl['videoUrl'] as String?,
            audioUrl: rl['audioUrl'] as String?,
            content: rl['content'] as String?,
            isFreePreview: rl['isFreePreview'] as bool? ?? false,
            isCompleted: rl['isCompleted'] as bool? ?? false,
            lastPositionSeconds: rl['lastPositionSeconds'] as int? ?? 0,
            sectionId: sectionId,
          );
        }).toList();
        sections.add(SectionItem(
          id: sectionId,
          title: rs['title'] as String? ?? 'Section',
          lectures: lectures,
        ));
      }

      final enrollment = curriculum['enrollment'];
      final isEnrolled = enrollment != null;

      state = state.copyWith(
        isLoading: false,
        courseId: courseId,
        courseTitle: courseTitle,
        courseData: courseDetail,
        sections: sections,
        isEnrolled: isEnrolled,
      );

      // Select initial lecture
      if (sections.isNotEmpty) {
        final allLectures = state.allLectures;
        if (allLectures.isNotEmpty) {
          final targetId = initialLectureId ?? allLectures.first.id;
          await selectLecture(targetId);
        }
      }

      // Load bookmarks
      if (isEnrolled && userId > 0) {
        await _loadBookmarks();
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Failed to load course: $e',
      );
    }
  }

  // -----------------------------------------------------------------------
  // Select lecture
  // -----------------------------------------------------------------------

  Future<void> selectLecture(int lectureId) async {
    _progressTimer?.cancel();
    _disposeVideo();
    state = state.copyWith(
      currentLectureId: lectureId,
      clearVideo: true,
      notes: const [],
    );

    final lecture = state.currentLecture;
    if (lecture == null) return;

    // Init video if applicable
    if (lecture.type == 'video' && lecture.videoUrl != null && lecture.videoUrl!.isNotEmpty) {
      await _initVideo(lecture.videoUrl!, lecture.lastPositionSeconds);
    }

    // Load notes for this lecture
    if (_userId != null && _userId > 0 && state.isEnrolled) {
      await _loadNotes(lectureId);
    }
  }

  Future<void> _initVideo(String url, int startPosition) async {
    try {
      final vc = VideoPlayerController.networkUrl(Uri.parse(url));
      await vc.initialize();

      if (startPosition > 0) {
        await vc.seekTo(Duration(seconds: startPosition));
      }

      final cc = ChewieController(
        videoPlayerController: vc,
        autoPlay: true,
        allowFullScreen: true,
        allowPlaybackSpeedChanging: true,
        playbackSpeeds: const [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0],
      );

      if (!mounted) {
        cc.dispose();
        vc.dispose();
        return;
      }

      state = state.copyWith(
        videoController: vc,
        chewieController: cc,
        videoReady: true,
      );

      // Listen for video completion
      vc.addListener(_onVideoUpdate);

      // Start progress saving timer
      _progressTimer = Timer.periodic(
        const Duration(seconds: 15),
        (_) => _autoSaveProgress(),
      );
    } catch (e) {
      debugPrint('Video init error: $e');
    }
  }

  void _onVideoUpdate() {
    final vc = state.videoController;
    if (vc == null) return;
    final position = vc.value.position;
    final duration = vc.value.duration;
    if (duration.inSeconds > 0 &&
        position.inSeconds >= duration.inSeconds - 2 &&
        !vc.value.isPlaying) {
      _onVideoCompleted();
    }
  }

  Future<void> _onVideoCompleted() async {
    await markCompleted();
    // Auto-advance
    final next = state.nextLecture;
    if (next != null) {
      await selectLecture(next.id);
    }
  }

  // -----------------------------------------------------------------------
  // Progress
  // -----------------------------------------------------------------------

  Future<void> saveProgress(int positionSeconds, int watchTimeSeconds) async {
    if (_userId == null || _userId <= 0) return;
    if (!state.isEnrolled) return;
    final lecture = state.currentLecture;
    if (lecture == null) return;

    try {
      await _client.enrollment.updateProgress(
        _userId,
        lecture.id,
        state.courseId,
        positionSeconds,
        watchTimeSeconds,
        false,
      );
    } catch (_) {}
  }

  void _autoSaveProgress() {
    final vc = state.videoController;
    if (vc == null || !vc.value.isInitialized) return;
    final pos = vc.value.position.inSeconds;
    saveProgress(pos, 15);
  }

  Future<void> markCompleted() async {
    if (_userId == null || _userId <= 0) return;
    if (!state.isEnrolled) return;
    final lecture = state.currentLecture;
    if (lecture == null) return;

    try {
      await _client.enrollment.updateProgress(
        _userId,
        lecture.id,
        state.courseId,
        0,
        0,
        true,
      );

      // Update local state
      final newSections = state.sections.map((s) {
        final newLectures = s.lectures.map((l) {
          if (l.id == lecture.id) {
            return l.copyWith(isCompleted: true);
          }
          return l;
        }).toList();
        return SectionItem(id: s.id, title: s.title, lectures: newLectures);
      }).toList();

      state = state.copyWith(sections: newSections);
    } catch (_) {}
  }

  // -----------------------------------------------------------------------
  // Enrollment
  // -----------------------------------------------------------------------

  Future<bool> enroll() async {
    if (_userId == null || _userId <= 0) return false;
    try {
      final result = await _client.enrollment.enroll(_userId, state.courseId);
      if (result['success'] == true) {
        state = state.copyWith(isEnrolled: true);
        return true;
      }
    } catch (_) {}
    return false;
  }

  // -----------------------------------------------------------------------
  // Notes
  // -----------------------------------------------------------------------

  Future<void> _loadNotes(int lectureId) async {
    if (_userId == null || _userId <= 0) return;
    try {
      final notes = await _client.note.getNotes(_userId, lectureId);
      if (mounted) {
        state = state.copyWith(notes: notes);
      }
    } catch (_) {}
  }

  Future<void> addNote(String content, int? timestampSeconds) async {
    if (_userId == null || _userId <= 0) return;
    final lecture = state.currentLecture;
    if (lecture == null) return;
    try {
      final note = await _client.note.createNote(
        _userId,
        lecture.id,
        state.courseId,
        content,
        timestampSeconds,
      );
      state = state.copyWith(notes: [...state.notes, note]);
    } catch (_) {}
  }

  Future<void> updateNote(int noteId, String content) async {
    if (_userId == null || _userId <= 0) return;
    try {
      await _client.note.updateNote(_userId, noteId, content);
      final updated = state.notes.map((n) {
        if (n.id == noteId) {
          return n.copyWith(content: content);
        }
        return n;
      }).toList();
      state = state.copyWith(notes: updated);
    } catch (_) {}
  }

  Future<void> deleteNote(int noteId) async {
    if (_userId == null || _userId <= 0) return;
    try {
      await _client.note.deleteNote(_userId, noteId);
      final filtered = state.notes.where((n) => n.id != noteId).toList();
      state = state.copyWith(notes: filtered);
    } catch (_) {}
  }

  // -----------------------------------------------------------------------
  // Bookmarks
  // -----------------------------------------------------------------------

  Future<void> _loadBookmarks() async {
    if (_userId == null || _userId <= 0) return;
    try {
      final bookmarks =
          await _client.bookmark.getBookmarks(_userId, state.courseId);
      if (mounted) {
        state = state.copyWith(bookmarks: bookmarks);
      }
    } catch (_) {}
  }

  Future<void> addBookmark(String? label) async {
    if (_userId == null || _userId <= 0) return;
    final lecture = state.currentLecture;
    if (lecture == null) return;
    final vc = state.videoController;
    final ts = vc?.value.position.inSeconds ?? 0;
    try {
      final bookmark = await _client.bookmark.createBookmark(
        _userId,
        lecture.id,
        state.courseId,
        ts,
        label,
      );
      state = state.copyWith(bookmarks: [...state.bookmarks, bookmark]);
    } catch (_) {}
  }

  Future<void> deleteBookmark(int bookmarkId) async {
    if (_userId == null || _userId <= 0) return;
    try {
      await _client.bookmark.deleteBookmark(_userId, bookmarkId);
      final filtered =
          state.bookmarks.where((b) => b.id != bookmarkId).toList();
      state = state.copyWith(bookmarks: filtered);
    } catch (_) {}
  }

  void seekTo(int seconds) {
    state.videoController?.seekTo(Duration(seconds: seconds));
  }

  /// Call when leaving the screen to save final position
  Future<void> onLeave() async {
    _progressTimer?.cancel();
    final vc = state.videoController;
    if (vc != null && vc.value.isInitialized) {
      await saveProgress(vc.value.position.inSeconds, 0);
    }
  }
}

// ---------------------------------------------------------------------------
// Providers
// ---------------------------------------------------------------------------

final playerStateProvider =
    StateNotifierProvider.autoDispose<PlayerNotifier, PlayerState>((ref) {
  final client = ref.watch(clientProvider);
  final userId = ref.watch(authProvider).user?.id;
  return PlayerNotifier(client, userId);
});

final currentLectureProvider = Provider.autoDispose<LectureItem?>((ref) {
  return ref.watch(playerStateProvider).currentLecture;
});

final courseProgressProvider = Provider.autoDispose<double>((ref) {
  return ref.watch(playerStateProvider).progressPercent;
});
