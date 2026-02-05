import 'dart:math';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class CertificateEndpoint extends Endpoint {
  // Generate a certificate upon course completion
  Future<Map<String, dynamic>> generateCertificate(
    Session session,
    int userId,
    int courseId,
  ) async {
    // Check that the user has a completed enrollment for this course
    final enrollment = await Enrollment.db.findFirstRow(session,
      where: (t) =>
          t.userId.equals(userId) &
          t.courseId.equals(courseId) &
          t.status.equals('completed'),
    );

    if (enrollment == null) {
      return {
        'success': false,
        'error': 'Course enrollment not found or not completed',
      };
    }

    // Check if a certificate already exists for this user and course
    final existing = await Certificate.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );

    if (existing != null) {
      return {
        'success': false,
        'error': 'Certificate already issued for this course',
        'certificate': existing.toJson(),
      };
    }

    // Generate a unique certificate number
    final certificateNumber = _generateCertificateNumber();

    final certificate = Certificate(
      userId: userId,
      courseId: courseId,
      certificateNumber: certificateNumber,
      issuedAt: DateTime.now(),
    );

    final inserted = await Certificate.db.insertRow(session, certificate);

    return {
      'success': true,
      'certificate': inserted.toJson(),
    };
  }

  // Get all certificates for a user
  Future<List<Certificate>> getCertificates(
    Session session,
    int userId,
  ) async {
    return await Certificate.db.find(session,
      where: (t) => t.userId.equals(userId) & t.isRevoked.equals(false),
      orderBy: (t) => t.issuedAt,
      orderDescending: true,
    );
  }

  // Public endpoint to verify a certificate by its number
  @override
  bool get requireLogin => false;

  Future<Map<String, dynamic>> verifyCertificate(
    Session session,
    String certificateNumber,
  ) async {
    final certificate = await Certificate.db.findFirstRow(session,
      where: (t) => t.certificateNumber.equals(certificateNumber),
    );

    if (certificate == null) {
      return {
        'valid': false,
        'error': 'Certificate not found',
      };
    }

    if (certificate.isRevoked) {
      return {
        'valid': false,
        'error': 'Certificate has been revoked',
      };
    }

    // Fetch course and user details for the verification response
    final course = await Course.db.findById(session, certificate.courseId);
    final user = await User.db.findById(session, certificate.userId);

    return {
      'valid': true,
      'certificateNumber': certificate.certificateNumber,
      'issuedAt': certificate.issuedAt.toIso8601String(),
      'courseName': course?.title,
      'recipientName': user?.name,
    };
  }

  /// Generates a unique certificate number in the format CERT-XXXXXXXX-XXXX
  /// using a combination of timestamp and secure random characters.
  String _generateCertificateNumber() {
    final random = Random.secure();
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final hexTimestamp = timestamp.toRadixString(16).toUpperCase();

    final randomPart = List.generate(
      4,
      (_) => chars[random.nextInt(chars.length)],
    ).join();

    return 'CERT-$hexTimestamp-$randomPart';
  }
}
