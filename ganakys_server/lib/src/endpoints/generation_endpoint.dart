import 'dart:convert';
import 'dart:io';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class GenerationEndpoint extends Endpoint {
  // List generation jobs
  Future<Map<String, dynamic>> listJobs(
    Session session, {
    String? status,
    int page = 1,
    int pageSize = 20,
  }) async {
    final offset = (page - 1) * pageSize;
    var where = 'true';
    final params = <String, dynamic>{
      'limit': pageSize,
      'offset': offset,
    };

    if (status != null) {
      where += ' AND status = @status';
      params['status'] = status;
    }

    final results = await session.db.unsafeQuery(
      'SELECT * FROM generation_jobs WHERE $where ORDER BY "createdAt" DESC LIMIT @limit OFFSET @offset',
      parameters: QueryParameters.named(params),
    );
    final countResult = await session.db.unsafeQuery(
      'SELECT COUNT(*) FROM generation_jobs WHERE $where',
      parameters: QueryParameters.named(params),
    );

    // Get stats
    final stats = await session.db.unsafeQuery(
      '''SELECT
         COUNT(*) as total,
         COUNT(*) FILTER (WHERE status = 'completed') as completed,
         COUNT(*) FILTER (WHERE status = 'failed') as failed,
         COUNT(*) FILTER (WHERE status NOT IN ('completed', 'failed')) as in_progress,
         AVG("qualityScore") FILTER (WHERE "qualityScore" IS NOT NULL) as avg_quality
         FROM generation_jobs''',
    );

    return {
      'jobs': results.map((row) => _jobRowToMap(row)).toList(),
      'totalCount': countResult.first[0],
      'stats': {
        'total': stats.first[0],
        'completed': stats.first[1],
        'failed': stats.first[2],
        'inProgress': stats.first[3],
        'avgQualityScore': stats.first[4],
      },
    };
  }

  // Get job detail
  Future<Map<String, dynamic>?> getJob(Session session, int jobId) async {
    final job = await GenerationJob.db.findById(session, jobId);
    if (job == null) return null;

    final stages = await GenerationStageLog.db.find(session,
      where: (t) => t.jobId.equals(jobId),
      orderBy: (t) => t.startedAt,
    );

    return {
      'job': job.toJson(),
      'stages': stages.map((s) => s.toJson()).toList(),
    };
  }

  // Start one-click generation
  Future<Map<String, dynamic>> startGeneration(
    Session session,
    String topic,
    int? categoryId,
    String difficulty,
    int targetDurationMinutes,
    int createdBy,
  ) async {
    final now = DateTime.now();

    // Create job record
    final job = GenerationJob(
      topic: topic,
      status: 'queued',
      currentStage: 'initialization',
      config: jsonEncode({
        'categoryId': categoryId,
        'difficulty': difficulty,
        'targetDurationMinutes': targetDurationMinutes,
      }),
      createdBy: createdBy,
      createdAt: now,
    );
    final inserted = await GenerationJob.db.insertRow(session, job);

    // Create stage logs for the 9 pipeline stages
    final stages = [
      'content_generation', 'script_writing', 'quiz_generation',
      'audio_generation', 'slide_generation', 'video_rendering',
      'thumbnail_generation', 'quality_check', 'import',
    ];

    for (final stage in stages) {
      await GenerationStageLog.db.insertRow(session, GenerationStageLog(
        jobId: inserted.id!,
        stage: stage,
        status: 'pending',
      ));
    }

    // Spawn the pipeline process asynchronously
    _spawnPipeline(session, inserted.id!, topic, difficulty, targetDurationMinutes);

    return {
      'success': true,
      'jobId': inserted.id,
      'message': 'Generation started',
    };
  }

  // Start step-by-step generation (just creates job, each step is triggered manually)
  Future<Map<String, dynamic>> startStepByStep(
    Session session,
    String topic,
    int createdBy,
  ) async {
    final job = GenerationJob(
      topic: topic,
      status: 'step_by_step',
      currentStage: 'topic_config',
      createdBy: createdBy,
      createdAt: DateTime.now(),
    );
    final inserted = await GenerationJob.db.insertRow(session, job);

    return {
      'success': true,
      'jobId': inserted.id,
    };
  }

  // Generate outline (step-by-step mode)
  Future<Map<String, dynamic>> generateOutline(
    Session session,
    int jobId,
    String topic,
    String difficulty,
    int targetDurationMinutes,
  ) async {
    // Update job status
    await session.db.unsafeQuery(
      'UPDATE generation_jobs SET status = \'content_generating\', "currentStage" = \'outline\', "progressPercent" = 10 WHERE id = @id',
      parameters: QueryParameters.named({'id': jobId}),
    );

    // TODO: Call Gemini API via GeminiService to generate outline
    // For now, return mock outline
    final mockOutline = {
      'sections': [
        {
          'title': 'Introduction to $topic',
          'lectures': ['What is $topic', 'Why Learn $topic', 'Prerequisites'],
        },
        {
          'title': 'Core Concepts',
          'lectures': ['Fundamentals', 'Key Principles', 'Best Practices'],
        },
        {
          'title': 'Advanced Topics',
          'lectures': ['Advanced Techniques', 'Real-World Applications'],
        },
        {
          'title': 'Wrap Up',
          'lectures': ['Summary', 'Next Steps', 'Final Assessment'],
        },
      ],
    };

    await session.db.unsafeQuery(
      'UPDATE generation_jobs SET "contentJson" = @content, "progressPercent" = 15 WHERE id = @id',
      parameters: QueryParameters.named({'id': jobId, 'content': jsonEncode(mockOutline)}),
    );

    return {
      'success': true,
      'outline': mockOutline,
    };
  }

  // Save edited outline
  Future<Map<String, dynamic>> saveOutline(
    Session session,
    int jobId,
    String outlineJson,
  ) async {
    await session.db.unsafeQuery(
      'UPDATE generation_jobs SET "contentJson" = @content, "currentStage" = \'outline_saved\', "progressPercent" = 20 WHERE id = @id',
      parameters: QueryParameters.named({'id': jobId, 'content': outlineJson}),
    );

    return {'success': true};
  }

  // Import completed pipeline output into database
  Future<Map<String, dynamic>> importPipelineOutput(
    Session session,
    int jobId,
    int categoryId,
  ) async {
    final job = await GenerationJob.db.findById(session, jobId);
    if (job == null) {
      return {'success': false, 'error': 'Job not found'};
    }

    if (job.outputDir == null) {
      return {'success': false, 'error': 'No output directory'};
    }

    try {
      // Read content.json from pipeline output
      final contentFile = File('${job.outputDir}/content.json');
      if (!await contentFile.exists()) {
        return {'success': false, 'error': 'content.json not found'};
      }

      final contentStr = await contentFile.readAsString();
      final content = jsonDecode(contentStr) as Map<String, dynamic>;

      final now = DateTime.now();
      final slug = _slugify(job.topic);

      // Create course
      final course = Course(
        title: content['title'] as String? ?? job.topic,
        slug: slug,
        description: content['description'] as String?,
        shortDescription: content['shortDescription'] as String?,
        categoryId: categoryId,
        difficulty: (content['difficulty'] as String?) ?? 'beginner',
        generationStatus: 'imported',
        generationJobId: jobId,
        qualityScore: job.qualityScore,
        createdAt: now,
        updatedAt: now,
      );
      final insertedCourse = await Course.db.insertRow(session, course);
      final courseId = insertedCourse.id!;

      // Import sections and lectures
      final sections = content['sections'] as List? ?? [];
      var totalLectures = 0;
      var totalDuration = 0;

      for (var sIdx = 0; sIdx < sections.length; sIdx++) {
        final sData = sections[sIdx] as Map<String, dynamic>;
        final section = CourseSection(
          courseId: courseId,
          title: sData['title'] as String? ?? 'Section ${sIdx + 1}',
          description: sData['description'] as String?,
          sortOrder: sIdx,
        );
        final insertedSection = await CourseSection.db.insertRow(session, section);

        final lectures = sData['lectures'] as List? ?? [];
        for (var lIdx = 0; lIdx < lectures.length; lIdx++) {
          final lData = lectures[lIdx] as Map<String, dynamic>;
          final lecture = Lecture(
            sectionId: insertedSection.id!,
            courseId: courseId,
            title: lData['title'] as String? ?? 'Lecture ${lIdx + 1}',
            type: lData['type'] as String? ?? 'video',
            durationMinutes: lData['durationMinutes'] as int? ?? 5,
            videoUrl: lData['videoUrl'] as String?,
            audioUrl: lData['audioUrl'] as String?,
            content: lData['content'] as String?,
            scriptJson: lData['script'] != null ? jsonEncode(lData['script']) : null,
            sortOrder: lIdx,
          );
          await Lecture.db.insertRow(session, lecture);
          totalLectures++;
          totalDuration += lecture.durationMinutes;
        }
      }

      // Update course stats
      await session.db.unsafeQuery(
        'UPDATE courses SET "totalLectures" = @total, "totalSections" = @sections, "durationMinutes" = @duration WHERE id = @id',
        parameters: QueryParameters.named({
          'total': totalLectures,
          'sections': sections.length,
          'duration': totalDuration,
          'id': courseId,
        }),
      );

      // Update job
      await GenerationJob.db.updateRow(session, job.copyWith(
        courseId: courseId,
        status: 'completed',
        currentStage: 'import',
        progressPercent: 100,
        completedAt: now,
      ));

      return {
        'success': true,
        'courseId': courseId,
        'totalSections': sections.length,
        'totalLectures': totalLectures,
      };
    } catch (e) {
      return {'success': false, 'error': 'Import failed: $e'};
    }
  }

  // Retry failed job
  Future<Map<String, dynamic>> retryJob(Session session, int jobId) async {
    final job = await GenerationJob.db.findById(session, jobId);
    if (job == null) {
      return {'success': false, 'error': 'Job not found'};
    }

    await GenerationJob.db.updateRow(session, job.copyWith(
      status: 'queued',
      errorMessage: null,
      progressPercent: 0,
    ));

    // Re-spawn pipeline
    _spawnPipeline(session, jobId, job.topic, 'intermediate', 60);

    return {'success': true, 'message': 'Job restarted'};
  }

  void _spawnPipeline(
    Session session,
    int jobId,
    String topic,
    String difficulty,
    int durationMinutes,
  ) async {
    try {
      final process = await Process.start(
        'node',
        [
          '/home/udemycrores/src/scripts/courseOrchestrator.js',
          '--topic', topic,
          '--difficulty', difficulty,
          '--duration', durationMinutes.toString(),
        ],
        environment: {
          'JOB_ID': jobId.toString(),
        },
      );

      // Monitor stdout for progress updates
      process.stdout.transform(utf8.decoder).listen((data) async {
        // Parse progress from pipeline output
        session.log('Pipeline [$jobId]: $data');
        // TODO: Parse stage updates and update DB + send WebSocket messages
      });

      process.stderr.transform(utf8.decoder).listen((data) {
        session.log('Pipeline ERROR [$jobId]: $data');
      });

      process.exitCode.then((exitCode) async {
        if (exitCode == 0) {
          // Mark as completed
          await session.db.unsafeQuery(
            'UPDATE generation_jobs SET status = \'completed\', "progressPercent" = 100, "completedAt" = NOW() WHERE id = @id',
            parameters: QueryParameters.named({'id': jobId}),
          );
        } else {
          await session.db.unsafeQuery(
            'UPDATE generation_jobs SET status = \'failed\', "errorMessage" = @error WHERE id = @id',
            parameters: QueryParameters.named({'id': jobId, 'error': 'Pipeline exited with code $exitCode'}),
          );
        }
      });
    } catch (e) {
      await session.db.unsafeQuery(
        'UPDATE generation_jobs SET status = \'failed\', "errorMessage" = @error WHERE id = @id',
        parameters: QueryParameters.named({'id': jobId, 'error': 'Failed to start pipeline: $e'}),
      );
    }
  }

  String _slugify(String input) {
    return input
        .toLowerCase()
        .replaceAll(RegExp(r'[^a-z0-9\s-]'), '')
        .replaceAll(RegExp(r'\s+'), '-')
        .replaceAll(RegExp(r'-+'), '-')
        .replaceAll(RegExp(r'^-|-$'), '');
  }

  Map<String, dynamic> _jobRowToMap(dynamic row) {
    return {
      'id': row[0],
      'courseId': row[1],
      'topic': row[2],
      'status': row[3],
      'currentStage': row[4],
      'progressPercent': row[5],
      'qualityScore': row[7],
      'errorMessage': row[9],
      'createdAt': row[15]?.toString(),
    };
  }
}
