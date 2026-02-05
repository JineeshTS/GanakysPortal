import 'package:serverpod/serverpod.dart';

class HealthEndpoint extends Endpoint {
  @override
  bool get requireLogin => false;

  Future<Map<String, dynamic>> check(Session session) async {
    final dbOk = await _checkDatabase(session);
    return {
      'status': dbOk ? 'healthy' : 'degraded',
      'database': dbOk ? 'connected' : 'disconnected',
      'timestamp': DateTime.now().toIso8601String(),
      'uptime': _uptime(),
    };
  }

  Future<bool> _checkDatabase(Session session) async {
    try {
      await session.db.unsafeQuery('SELECT 1');
      return true;
    } catch (_) {
      return false;
    }
  }

  String _uptime() {
    return DateTime.now().toIso8601String();
  }
}
