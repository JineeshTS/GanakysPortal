import 'dart:convert';
import 'package:bcrypt/bcrypt.dart';
import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class ProfileEndpoint extends Endpoint {
  // Get user profile
  Future<Map<String, dynamic>?> getProfile(Session session, int userId) async {
    final user = await User.db.findById(session, userId);
    if (user == null) return null;

    return {
      'id': user.id,
      'email': user.email,
      'name': user.name,
      'avatarUrl': user.avatarUrl,
      'bio': user.bio,
      'role': user.role,
      'subscriptionStatus': user.subscriptionStatus,
      'subscriptionExpiresAt': user.subscriptionExpiresAt?.toIso8601String(),
      'emailVerified': user.emailVerified,
      'totpEnabled': user.totpEnabled,
      'locale': user.locale,
      'createdAt': user.createdAt.toIso8601String(),
    };
  }

  // Update profile
  Future<Map<String, dynamic>> updateProfile(
    Session session,
    int userId,
    String name,
    String? bio,
    String? avatarUrl,
    String? locale,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    await User.db.updateRow(session, user.copyWith(
      name: name,
      bio: bio,
      avatarUrl: avatarUrl,
      locale: locale ?? user.locale,
      updatedAt: DateTime.now(),
    ));

    return {'success': true};
  }

  // Change password
  Future<Map<String, dynamic>> changePassword(
    Session session,
    int userId,
    String currentPassword,
    String newPassword,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) {
      return {'success': false, 'error': 'User not found'};
    }

    if (user.passwordHash == null || !BCrypt.checkpw(currentPassword, user.passwordHash!)) {
      return {'success': false, 'error': 'Current password is incorrect'};
    }

    if (newPassword.length < 8) {
      return {'success': false, 'error': 'Password must be at least 8 characters'};
    }

    // Check password history
    if (user.passwordHistory != null) {
      try {
        final history = jsonDecode(user.passwordHistory!) as List;
        for (final oldHash in history) {
          if (BCrypt.checkpw(newPassword, oldHash as String)) {
            return {'success': false, 'error': 'Cannot reuse recent passwords'};
          }
        }
      } catch (_) {}
    }

    final newHash = BCrypt.hashpw(newPassword, BCrypt.gensalt(logRounds: 12));

    // Update password history (keep last 5)
    var historyList = <String>[];
    if (user.passwordHistory != null) {
      try {
        historyList = (jsonDecode(user.passwordHistory!) as List).cast<String>();
      } catch (_) {}
    }
    historyList.insert(0, user.passwordHash!);
    if (historyList.length > 5) historyList = historyList.sublist(0, 5);

    await User.db.updateRow(session, user.copyWith(
      passwordHash: newHash,
      passwordHistory: jsonEncode(historyList),
      updatedAt: DateTime.now(),
    ));

    return {'success': true, 'message': 'Password changed successfully'};
  }

  // Export user data (GDPR)
  Future<Map<String, dynamic>> exportData(Session session, int userId) async {
    final user = await User.db.findById(session, userId);
    if (user == null) return {'error': 'User not found'};

    final enrollments = await Enrollment.db.find(session,
      where: (t) => t.userId.equals(userId),
    );
    final notes = await StudentNote.db.find(session,
      where: (t) => t.userId.equals(userId),
    );
    final bookmarks = await Bookmark.db.find(session,
      where: (t) => t.userId.equals(userId),
    );
    final certificates = await Certificate.db.find(session,
      where: (t) => t.userId.equals(userId),
    );
    final reviews = await Review.db.find(session,
      where: (t) => t.userId.equals(userId),
    );

    return {
      'profile': {
        'name': user.name,
        'email': user.email,
        'bio': user.bio,
        'createdAt': user.createdAt.toIso8601String(),
      },
      'enrollments': enrollments.map((e) => e.toJson()).toList(),
      'notes': notes.map((n) => n.toJson()).toList(),
      'bookmarks': bookmarks.map((b) => b.toJson()).toList(),
      'certificates': certificates.map((c) => c.toJson()).toList(),
      'reviews': reviews.map((r) => r.toJson()).toList(),
    };
  }

  // Request account deletion
  Future<Map<String, dynamic>> requestDeletion(
    Session session,
    int userId,
    String password,
  ) async {
    final user = await User.db.findById(session, userId);
    if (user == null) return {'success': false, 'error': 'User not found'};

    if (user.passwordHash == null || !BCrypt.checkpw(password, user.passwordHash!)) {
      return {'success': false, 'error': 'Incorrect password'};
    }

    await User.db.updateRow(session, user.copyWith(
      deletionRequestedAt: DateTime.now(),
      updatedAt: DateTime.now(),
    ));

    // TODO: Send confirmation email

    return {
      'success': true,
      'message': 'Account deletion requested. Your account will be deleted in 30 days.',
    };
  }

  // Cancel account deletion
  Future<Map<String, dynamic>> cancelDeletion(Session session, int userId) async {
    final user = await User.db.findById(session, userId);
    if (user == null) return {'success': false, 'error': 'User not found'};

    await User.db.updateRow(session, user.copyWith(
      deletionRequestedAt: null,
      updatedAt: DateTime.now(),
    ));

    return {'success': true, 'message': 'Account deletion cancelled'};
  }

  // Get wishlist
  Future<List<Map<String, dynamic>>> getWishlist(Session session, int userId) async {
    final wishlists = await Wishlist.db.find(session,
      where: (t) => t.userId.equals(userId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
    );

    final result = <Map<String, dynamic>>[];
    for (final w in wishlists) {
      final course = await Course.db.findById(session, w.courseId);
      if (course != null) {
        result.add({
          'wishlistId': w.id,
          'course': {
            'id': course.id,
            'title': course.title,
            'slug': course.slug,
            'thumbnailUrl': course.thumbnailUrl,
            'price': course.price,
            'avgRating': course.avgRating,
          },
        });
      }
    }
    return result;
  }

  // Toggle wishlist
  Future<Map<String, dynamic>> toggleWishlist(
    Session session,
    int userId,
    int courseId,
  ) async {
    final existing = await Wishlist.db.findFirstRow(session,
      where: (t) => t.userId.equals(userId) & t.courseId.equals(courseId),
    );

    if (existing != null) {
      await Wishlist.db.deleteRow(session, existing);
      return {'success': true, 'wishlisted': false};
    } else {
      await Wishlist.db.insertRow(session, Wishlist(
        userId: userId,
        courseId: courseId,
        createdAt: DateTime.now(),
      ));
      return {'success': true, 'wishlisted': true};
    }
  }

  // Get notifications
  Future<List<Notification>> getNotifications(
    Session session,
    int userId,
  ) async {
    return await Notification.db.find(session,
      where: (t) => t.userId.equals(userId),
      orderBy: (t) => t.createdAt,
      orderDescending: true,
      limit: 50,
    );
  }

  // Mark notification as read
  Future<bool> markNotificationRead(
    Session session,
    int userId,
    int notificationId,
  ) async {
    final notif = await Notification.db.findById(session, notificationId);
    if (notif == null || notif.userId != userId) return false;

    await Notification.db.updateRow(session, notif.copyWith(isRead: true));
    return true;
  }
}
