import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ganakys_client/ganakys_client.dart';
import 'package:serverpod_flutter/serverpod_flutter.dart';

final clientProvider = Provider<Client>((ref) {
  const serverUrl = String.fromEnvironment(
    'SERVER_URL',
    defaultValue: 'http://localhost:8080/',
  );
  final client = Client(serverUrl)
    ..connectivityMonitor = FlutterConnectivityMonitor();
  return client;
});
