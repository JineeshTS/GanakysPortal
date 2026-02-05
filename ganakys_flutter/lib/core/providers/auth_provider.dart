import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:ganakys_client/ganakys_client.dart';
import '../client_provider.dart';

class AuthUser {
  final int id;
  final String email;
  final String name;
  final String role;
  final String? avatarUrl;
  final String? subscriptionStatus;
  final bool emailVerified;
  final bool totpEnabled;

  const AuthUser({
    required this.id,
    required this.email,
    required this.name,
    required this.role,
    this.avatarUrl,
    this.subscriptionStatus,
    this.emailVerified = false,
    this.totpEnabled = false,
  });

  bool get isAdmin => role == 'admin';
  bool get isInstructor => role == 'instructor';
  bool get isStudent => role == 'student';

  factory AuthUser.fromMap(Map<String, dynamic> map) {
    return AuthUser(
      id: map['id'] as int,
      email: map['email'] as String,
      name: map['name'] as String,
      role: map['role'] as String? ?? 'student',
      avatarUrl: map['avatarUrl'] as String?,
      subscriptionStatus: map['subscriptionStatus'] as String?,
      emailVerified: map['emailVerified'] as bool? ?? false,
      totpEnabled: map['totpEnabled'] as bool? ?? false,
    );
  }
}

class AuthState {
  final AuthUser? user;
  final String? accessToken;
  final String? refreshToken;
  final bool isLoading;
  final String? error;
  final bool requires2fa;
  final int? pending2faUserId;

  const AuthState({
    this.user,
    this.accessToken,
    this.refreshToken,
    this.isLoading = false,
    this.error,
    this.requires2fa = false,
    this.pending2faUserId,
  });

  bool get isAuthenticated => user != null && accessToken != null;
  bool get isAdmin => user?.isAdmin ?? false;

  AuthState copyWith({
    AuthUser? user,
    String? accessToken,
    String? refreshToken,
    bool? isLoading,
    String? error,
    bool? requires2fa,
    int? pending2faUserId,
    bool clearUser = false,
    bool clearError = false,
    bool clear2fa = false,
  }) {
    return AuthState(
      user: clearUser ? null : (user ?? this.user),
      accessToken: clearUser ? null : (accessToken ?? this.accessToken),
      refreshToken: clearUser ? null : (refreshToken ?? this.refreshToken),
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      requires2fa: clear2fa ? false : (requires2fa ?? this.requires2fa),
      pending2faUserId: clear2fa ? null : (pending2faUserId ?? this.pending2faUserId),
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Client _client;
  final SharedPreferences _prefs;

  AuthNotifier(this._client, this._prefs) : super(const AuthState()) {
    _loadSavedAuth();
  }

  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userIdKey = 'user_id';
  static const _userEmailKey = 'user_email';
  static const _userNameKey = 'user_name';
  static const _userRoleKey = 'user_role';

  /// Call a server endpoint method dynamically.
  /// This works regardless of whether the endpoint has been generated
  /// in the client yet.
  Future<T> _call<T>(String endpoint, String method, Map<String, dynamic> args) {
    return _client.callServerEndpoint<T>(endpoint, method, args);
  }

  void _loadSavedAuth() {
    final accessToken = _prefs.getString(_accessTokenKey);
    final refreshToken = _prefs.getString(_refreshTokenKey);
    final userId = _prefs.getInt(_userIdKey);
    final email = _prefs.getString(_userEmailKey);
    final name = _prefs.getString(_userNameKey);
    final role = _prefs.getString(_userRoleKey);

    if (accessToken != null && userId != null && email != null && name != null) {
      state = AuthState(
        user: AuthUser(
          id: userId,
          email: email,
          name: name,
          role: role ?? 'student',
        ),
        accessToken: accessToken,
        refreshToken: refreshToken,
      );
    }
  }

  Future<void> _saveAuth(Map<String, dynamic> result) async {
    final user = result['user'] as Map<String, dynamic>;
    await _prefs.setString(_accessTokenKey, result['accessToken'] as String);
    if (result['refreshToken'] != null) {
      await _prefs.setString(_refreshTokenKey, result['refreshToken'] as String);
    }
    await _prefs.setInt(_userIdKey, user['id'] as int);
    await _prefs.setString(_userEmailKey, user['email'] as String);
    await _prefs.setString(_userNameKey, user['name'] as String);
    await _prefs.setString(_userRoleKey, user['role'] as String? ?? 'student');
  }

  Future<void> _clearAuth() async {
    await _prefs.remove(_accessTokenKey);
    await _prefs.remove(_refreshTokenKey);
    await _prefs.remove(_userIdKey);
    await _prefs.remove(_userEmailKey);
    await _prefs.remove(_userNameKey);
    await _prefs.remove(_userRoleKey);
  }

  Future<bool> login(String email, String password) async {
    state = state.copyWith(isLoading: true, clearError: true, clear2fa: true);
    try {
      final result = await _call<Map<String, dynamic>>('auth', 'login', {
        'email': email,
        'password': password,
        'deviceInfo': null,
        'ipAddress': null,
      });
      if (result['success'] == true) {
        if (result['requires2fa'] == true) {
          state = state.copyWith(
            isLoading: false,
            requires2fa: true,
            pending2faUserId: result['userId'] as int?,
          );
          return false;
        }
        await _saveAuth(result);
        state = AuthState(
          user: AuthUser.fromMap(result['user'] as Map<String, dynamic>),
          accessToken: result['accessToken'] as String,
          refreshToken: result['refreshToken'] as String?,
        );
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result['error'] as String? ?? 'Login failed',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Connection error. Please try again.',
      );
      return false;
    }
  }

  Future<bool> verify2fa(String code) async {
    if (state.pending2faUserId == null) return false;
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final result = await _call<Map<String, dynamic>>('auth', 'verify2fa', {
        'userId': state.pending2faUserId!,
        'code': code,
        'deviceInfo': null,
        'ipAddress': null,
      });
      if (result['success'] == true) {
        await _saveAuth(result);
        state = AuthState(
          user: AuthUser.fromMap(result['user'] as Map<String, dynamic>),
          accessToken: result['accessToken'] as String,
          refreshToken: result['refreshToken'] as String?,
        );
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result['error'] as String? ?? 'Verification failed',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Connection error. Please try again.',
      );
      return false;
    }
  }

  Future<bool> register(String email, String name, String password) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final result = await _call<Map<String, dynamic>>('auth', 'register', {
        'email': email,
        'name': name,
        'password': password,
      });
      if (result['success'] == true) {
        state = state.copyWith(isLoading: false);
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result['error'] as String? ?? 'Registration failed',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Connection error. Please try again.',
      );
      return false;
    }
  }

  Future<bool> forgotPassword(String email) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      await _call<Map<String, dynamic>>('auth', 'forgotPassword', {
        'email': email,
      });
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Connection error. Please try again.',
      );
      return false;
    }
  }

  Future<bool> resetPassword(String token, String newPassword) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final result = await _call<Map<String, dynamic>>('auth', 'resetPassword', {
        'token': token,
        'newPassword': newPassword,
      });
      if (result['success'] == true) {
        state = state.copyWith(isLoading: false);
        return true;
      } else {
        state = state.copyWith(
          isLoading: false,
          error: result['error'] as String? ?? 'Reset failed',
        );
        return false;
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'Connection error. Please try again.',
      );
      return false;
    }
  }

  Future<void> logout() async {
    if (state.refreshToken != null) {
      try {
        await _call<Map<String, dynamic>>('auth', 'logout', {
          'refreshToken': state.refreshToken!,
        });
      } catch (_) {}
    }
    await _clearAuth();
    state = const AuthState();
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }
}

final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('Must be overridden in main');
});

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final client = ref.watch(clientProvider);
  final prefs = ref.watch(sharedPreferencesProvider);
  return AuthNotifier(client, prefs);
});

final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isAuthenticated;
});

final isAdminProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isAdmin;
});

final currentUserProvider = Provider<AuthUser?>((ref) {
  return ref.watch(authProvider).user;
});
