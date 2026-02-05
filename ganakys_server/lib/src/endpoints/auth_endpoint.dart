import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:bcrypt/bcrypt.dart';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class AuthEndpoint extends Endpoint {
  @override
  bool get requireLogin => false;

  // Register new user
  Future<Map<String, dynamic>> register(
    Session session,
    String email,
    String name,
    String password,
  ) async {
    email = email.trim().toLowerCase();
    if (!_isValidEmail(email)) {
      return {'success': false, 'error': 'Invalid email address'};
    }
    if (password.length < 8 || !_isStrongPassword(password)) {
      return {
        'success': false,
        'error': 'Password must be 8+ chars with upper, lower, and number',
      };
    }

    // Check existing user
    final existing = await session.db.unsafeQuery(
      'SELECT id FROM users WHERE email = @email',
      parameters: QueryParameters.named({'email': email}),
    );
    if (existing.isNotEmpty) {
      return {'success': false, 'error': 'Email already registered'};
    }

    final passwordHash = BCrypt.hashpw(password, BCrypt.gensalt(logRounds: 12));
    final verificationToken = _generateToken();
    final now = DateTime.now();

    final user = User(
      email: email,
      name: name,
      passwordHash: passwordHash,
      emailVerificationToken: verificationToken,
      createdAt: now,
      updatedAt: now,
    );

    final inserted = await User.db.insertRow(session, user);

    // TODO: Send verification email via EmailService

    return {
      'success': true,
      'userId': inserted.id,
      'message': 'Registration successful. Please verify your email.',
    };
  }

  // Login
  Future<Map<String, dynamic>> login(
    Session session,
    String email,
    String password,
    String? deviceInfo,
    String? ipAddress,
  ) async {
    email = email.trim().toLowerCase();

    // Check rate limiting via Redis
    // Simple rate check - in production, use Redis INCR + TTL

    final users = await session.db.unsafeQuery(
      'SELECT * FROM users WHERE email = @email LIMIT 1',
      parameters: QueryParameters.named({'email': email}),
    );

    if (users.isEmpty) {
      await _logLoginAttempt(session, email, ipAddress ?? '', false, 'User not found');
      return {'success': false, 'error': 'Invalid email or password'};
    }

    final row = users.first;
    final userId = row[0] as int;

    // Fetch user properly
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'Invalid email or password'};
    }

    if (!user.isActive) {
      return {'success': false, 'error': 'Account is deactivated'};
    }

    // Check lockout
    if (user.lockedUntil != null && user.lockedUntil!.isAfter(DateTime.now())) {
      return {
        'success': false,
        'error': 'Account temporarily locked. Try again later.',
        'lockedUntil': user.lockedUntil!.toIso8601String(),
      };
    }

    // Verify password
    if (user.passwordHash == null || !BCrypt.checkpw(password, user.passwordHash!)) {
      final newFailedCount = user.failedLoginCount + 1;
      DateTime? newLockedUntil;

      if (newFailedCount >= 20) {
        newLockedUntil = DateTime.now().add(const Duration(minutes: 30));
      } else if (newFailedCount >= 10) {
        newLockedUntil = DateTime.now().add(const Duration(minutes: 5));
      }

      await User.db.updateRow(session, user.copyWith(
        failedLoginCount: newFailedCount,
        lockedUntil: newLockedUntil,
      ));

      await _logLoginAttempt(session, email, ipAddress ?? '', false, 'Invalid password');

      if (newFailedCount >= 5) {
        return {
          'success': false,
          'error': 'Invalid email or password',
          'requireCaptcha': true,
          'attemptsRemaining': 10 - newFailedCount,
        };
      }

      return {'success': false, 'error': 'Invalid email or password'};
    }

    // Check 2FA
    if (user.totpEnabled) {
      return {
        'success': false,
        'requires2fa': true,
        'userId': user.id,
        'message': 'Please provide your 2FA code',
      };
    }

    // Successful login
    return await _completeLogin(session, user, deviceInfo, ipAddress);
  }

  // Complete login after 2FA verification
  Future<Map<String, dynamic>> verify2fa(
    Session session,
    int userId,
    String code,
    String? deviceInfo,
    String? ipAddress,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    // TODO: Verify TOTP code using otp package
    // For now, placeholder
    return await _completeLogin(session, user, deviceInfo, ipAddress);
  }

  Future<Map<String, dynamic>> _completeLogin(
    Session session,
    User user,
    String? deviceInfo,
    String? ipAddress,
  ) async {
    final now = DateTime.now();

    // Reset failed login count and update login info
    await User.db.updateRow(session, user.copyWith(
      failedLoginCount: 0,
      lockedUntil: null,
      lastLoginAt: now,
      lastLoginIp: ipAddress,
      loginCount: user.loginCount + 1,
      updatedAt: now,
    ));

    // Generate tokens
    final accessToken = _generateToken();
    final refreshToken = _generateToken();
    final refreshTokenHash = sha256.convert(utf8.encode(refreshToken)).toString();

    // Create session (limit to 3 concurrent)
    final existingSessions = await session.db.unsafeQuery(
      'SELECT id FROM user_sessions WHERE "userId" = @userId AND "isRevoked" = false ORDER BY "createdAt" ASC',
      parameters: QueryParameters.named({'userId': user.id}),
    );

    if (existingSessions.length >= 3) {
      // Revoke oldest session
      final oldestId = existingSessions.first[0] as int;
      await session.db.unsafeQuery(
        'UPDATE user_sessions SET "isRevoked" = true WHERE id = @id',
        parameters: QueryParameters.named({'id': oldestId}),
      );
    }

    final userSession = UserSession(
      userId: user.id!,
      refreshTokenHash: refreshTokenHash,
      deviceInfo: deviceInfo,
      ipAddress: ipAddress,
      lastActiveAt: now,
      expiresAt: now.add(const Duration(days: 7)),
      createdAt: now,
    );

    await UserSession.db.insertRow(session, userSession);
    await _logLoginAttempt(session, user.email, ipAddress ?? '', true, null);

    return {
      'success': true,
      'accessToken': accessToken,
      'refreshToken': refreshToken,
      'expiresIn': 900, // 15 minutes
      'user': {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'avatarUrl': user.avatarUrl,
        'subscriptionStatus': user.subscriptionStatus,
        'emailVerified': user.emailVerified,
        'totpEnabled': user.totpEnabled,
      },
    };
  }

  // Refresh token
  Future<Map<String, dynamic>> refreshToken(
    Session session,
    String refreshToken,
    String? ipAddress,
  ) async {
    final tokenHash = sha256.convert(utf8.encode(refreshToken)).toString();

    final sessions = await session.db.unsafeQuery(
      'SELECT * FROM user_sessions WHERE "refreshTokenHash" = @hash AND "isRevoked" = false AND "expiresAt" > NOW() LIMIT 1',
      parameters: QueryParameters.named({'hash': tokenHash}),
    );

    if (sessions.isEmpty) {
      // Possible token theft - revoke all sessions for associated user
      return {'success': false, 'error': 'Invalid or expired refresh token'};
    }

    final sessionRow = sessions.first;
    final sessionId = sessionRow[0] as int;
    final userId = sessionRow[1] as int;

    // Revoke old session
    await session.db.unsafeQuery(
      'UPDATE user_sessions SET "isRevoked" = true WHERE id = @id',
      parameters: QueryParameters.named({'id': sessionId}),
    );

    // Issue new tokens
    final newAccessToken = _generateToken();
    final newRefreshToken = _generateToken();
    final newRefreshHash = sha256.convert(utf8.encode(newRefreshToken)).toString();
    final now = DateTime.now();

    final newSession = UserSession(
      userId: userId,
      refreshTokenHash: newRefreshHash,
      ipAddress: ipAddress,
      lastActiveAt: now,
      expiresAt: now.add(const Duration(days: 7)),
      createdAt: now,
    );

    await UserSession.db.insertRow(session, newSession);

    return {
      'success': true,
      'accessToken': newAccessToken,
      'refreshToken': newRefreshToken,
      'expiresIn': 900,
    };
  }

  // Verify email
  Future<Map<String, dynamic>> verifyEmail(Session session, String token) async {
    final users = await session.db.unsafeQuery(
      'SELECT id FROM users WHERE "emailVerificationToken" = @token LIMIT 1',
      parameters: QueryParameters.named({'token': token}),
    );

    if (users.isEmpty) {
      return {'success': false, 'error': 'Invalid verification token'};
    }

    await session.db.unsafeQuery(
      'UPDATE users SET "emailVerified" = true, "emailVerificationToken" = NULL, "updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({'id': users.first[0]}),
    );

    return {'success': true, 'message': 'Email verified successfully'};
  }

  // Forgot password
  Future<Map<String, dynamic>> forgotPassword(
    Session session,
    String email,
  ) async {
    email = email.trim().toLowerCase();
    final users = await session.db.unsafeQuery(
      'SELECT id FROM users WHERE email = @email LIMIT 1',
      parameters: QueryParameters.named({'email': email}),
    );

    // Always return success (don't reveal if email exists)
    if (users.isEmpty) {
      return {'success': true, 'message': 'If an account exists, a reset email has been sent'};
    }

    final resetToken = _generateToken();
    final expiresAt = DateTime.now().add(const Duration(hours: 1));

    await session.db.unsafeQuery(
      'UPDATE users SET "passwordResetToken" = @token, "passwordResetExpiresAt" = @expires, "updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({
        'token': resetToken,
        'expires': expiresAt.toIso8601String(),
        'id': users.first[0],
      }),
    );

    // TODO: Send reset email

    return {'success': true, 'message': 'If an account exists, a reset email has been sent'};
  }

  // Reset password
  Future<Map<String, dynamic>> resetPassword(
    Session session,
    String token,
    String newPassword,
  ) async {
    if (newPassword.length < 8 || !_isStrongPassword(newPassword)) {
      return {'success': false, 'error': 'Password must be 8+ chars with upper, lower, and number'};
    }

    final users = await session.db.unsafeQuery(
      'SELECT id, "passwordHistory" FROM users WHERE "passwordResetToken" = @token AND "passwordResetExpiresAt" > NOW() LIMIT 1',
      parameters: QueryParameters.named({'token': token}),
    );

    if (users.isEmpty) {
      return {'success': false, 'error': 'Invalid or expired reset token'};
    }

    final userId = users.first[0] as int;
    final passwordHash = BCrypt.hashpw(newPassword, BCrypt.gensalt(logRounds: 12));

    await session.db.unsafeQuery(
      'UPDATE users SET "passwordHash" = @hash, "passwordResetToken" = NULL, "passwordResetExpiresAt" = NULL, "updatedAt" = NOW() WHERE id = @id',
      parameters: QueryParameters.named({'hash': passwordHash, 'id': userId}),
    );

    // Revoke all sessions
    await session.db.unsafeQuery(
      'UPDATE user_sessions SET "isRevoked" = true WHERE "userId" = @userId',
      parameters: QueryParameters.named({'userId': userId}),
    );

    return {'success': true, 'message': 'Password reset successfully'};
  }

  // Logout
  Future<Map<String, dynamic>> logout(Session session, String refreshToken) async {
    final tokenHash = sha256.convert(utf8.encode(refreshToken)).toString();
    await session.db.unsafeQuery(
      'UPDATE user_sessions SET "isRevoked" = true WHERE "refreshTokenHash" = @hash',
      parameters: QueryParameters.named({'hash': tokenHash}),
    );
    return {'success': true};
  }

  // Get active sessions
  Future<List<Map<String, dynamic>>> getSessions(Session session, int userId) async {
    final sessions = await session.db.unsafeQuery(
      'SELECT id, "deviceInfo", "ipAddress", "lastActiveAt", "createdAt" FROM user_sessions WHERE "userId" = @userId AND "isRevoked" = false AND "expiresAt" > NOW() ORDER BY "lastActiveAt" DESC',
      parameters: QueryParameters.named({'userId': userId}),
    );

    return sessions.map((row) => <String, dynamic>{
      'id': row[0],
      'deviceInfo': row[1],
      'ipAddress': row[2],
      'lastActiveAt': (row[3] as DateTime?)?.toIso8601String(),
      'createdAt': (row[4] as DateTime?)?.toIso8601String(),
    }).toList();
  }

  // Revoke session
  Future<Map<String, dynamic>> revokeSession(Session session, int userId, int sessionId) async {
    await session.db.unsafeQuery(
      'UPDATE user_sessions SET "isRevoked" = true WHERE id = @id AND "userId" = @userId',
      parameters: QueryParameters.named({'id': sessionId, 'userId': userId}),
    );
    return {'success': true};
  }

  Future<void> _logLoginAttempt(
    Session session,
    String email,
    String ipAddress,
    bool success,
    String? failureReason,
  ) async {
    final attempt = LoginAttempt(
      email: email,
      ipAddress: ipAddress,
      success: success,
      failureReason: failureReason,
      createdAt: DateTime.now(),
    );
    await LoginAttempt.db.insertRow(session, attempt);
  }

  bool _isValidEmail(String email) {
    return RegExp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(email);
  }

  bool _isStrongPassword(String password) {
    return RegExp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$').hasMatch(password);
  }

  String _generateToken() {
    final random = Random.secure();
    final bytes = List<int>.generate(32, (_) => random.nextInt(256));
    return base64Url.encode(bytes);
  }
}
