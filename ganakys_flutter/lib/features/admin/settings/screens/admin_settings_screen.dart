import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/client_provider.dart';

final _settingsProvider = FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final client = ref.watch(clientProvider);
  return await client.admin.adminGetSettings();
});

class AdminSettingsScreen extends ConsumerStatefulWidget {
  const AdminSettingsScreen({super.key});

  @override
  ConsumerState<AdminSettingsScreen> createState() => _AdminSettingsScreenState();
}

class _AdminSettingsScreenState extends ConsumerState<AdminSettingsScreen> {
  final _siteNameCtrl = TextEditingController();
  final _taglineCtrl = TextEditingController();
  final _primaryColorCtrl = TextEditingController();
  final _secondaryColorCtrl = TextEditingController();
  final _maintenanceMessageCtrl = TextEditingController();
  bool _maintenanceMode = false;
  bool _loaded = false;
  bool _savingGeneral = false;
  bool _savingMaintenance = false;

  @override
  void dispose() {
    _siteNameCtrl.dispose();
    _taglineCtrl.dispose();
    _primaryColorCtrl.dispose();
    _secondaryColorCtrl.dispose();
    _maintenanceMessageCtrl.dispose();
    super.dispose();
  }

  void _populateFields(Map<String, dynamic> settings) {
    if (_loaded) return;
    _loaded = true;
    _siteNameCtrl.text = settings['site_name']?.toString() ?? '';
    _taglineCtrl.text = settings['tagline']?.toString() ?? '';
    _primaryColorCtrl.text = settings['primary_color']?.toString() ?? '';
    _secondaryColorCtrl.text = settings['secondary_color']?.toString() ?? '';
    _maintenanceMode = settings['maintenance_mode'] == 'true' || settings['maintenance_mode'] == true;
    _maintenanceMessageCtrl.text = settings['maintenance_message']?.toString() ?? '';
  }

  Future<void> _saveGeneralSettings() async {
    setState(() => _savingGeneral = true);
    try {
      final client = ref.read(clientProvider);
      await client.admin.adminUpdateSetting('site_name', _siteNameCtrl.text.trim());
      await client.admin.adminUpdateSetting('tagline', _taglineCtrl.text.trim());
      await client.admin.adminUpdateSetting('primary_color', _primaryColorCtrl.text.trim());
      await client.admin.adminUpdateSetting('secondary_color', _secondaryColorCtrl.text.trim());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Settings saved')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _savingGeneral = false);
    }
  }

  Future<void> _saveMaintenanceSettings() async {
    setState(() => _savingMaintenance = true);
    try {
      final client = ref.read(clientProvider);
      await client.admin.adminToggleMaintenanceMode(
        _maintenanceMode,
        _maintenanceMessageCtrl.text.trim().isEmpty ? null : _maintenanceMessageCtrl.text.trim(),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(_maintenanceMode ? 'Maintenance mode enabled' : 'Maintenance mode disabled')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _savingMaintenance = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final settingsAsync = ref.watch(_settingsProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Settings', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          settingsAsync.when(
            data: (settings) {
              _populateFields(settings);
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // General settings
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('General', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 16),
                          TextField(
                            controller: _siteNameCtrl,
                            decoration: const InputDecoration(
                              labelText: 'Site Name',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _taglineCtrl,
                            decoration: const InputDecoration(
                              labelText: 'Tagline',
                              border: OutlineInputBorder(),
                            ),
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: TextField(
                                  controller: _primaryColorCtrl,
                                  decoration: const InputDecoration(
                                    labelText: 'Primary Color',
                                    hintText: '#6366f1',
                                    border: OutlineInputBorder(),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: TextField(
                                  controller: _secondaryColorCtrl,
                                  decoration: const InputDecoration(
                                    labelText: 'Secondary Color',
                                    hintText: '#10b981',
                                    border: OutlineInputBorder(),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          FilledButton(
                            onPressed: _savingGeneral ? null : _saveGeneralSettings,
                            child: _savingGeneral
                                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                                : const Text('Save General Settings'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Maintenance mode
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Maintenance Mode', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 16),
                          SwitchListTile(
                            title: const Text('Enable Maintenance Mode'),
                            subtitle: const Text('When enabled, the site shows a maintenance page to non-admin users'),
                            value: _maintenanceMode,
                            onChanged: (v) => setState(() => _maintenanceMode = v),
                            contentPadding: EdgeInsets.zero,
                          ),
                          const SizedBox(height: 12),
                          TextField(
                            controller: _maintenanceMessageCtrl,
                            decoration: const InputDecoration(
                              labelText: 'Maintenance Message',
                              hintText: 'We are performing scheduled maintenance...',
                              border: OutlineInputBorder(),
                            ),
                            maxLines: 3,
                          ),
                          const SizedBox(height: 16),
                          FilledButton(
                            onPressed: _savingMaintenance ? null : _saveMaintenanceSettings,
                            style: _maintenanceMode
                                ? FilledButton.styleFrom(backgroundColor: colorScheme.error)
                                : null,
                            child: _savingMaintenance
                                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                                : Text(_maintenanceMode ? 'Enable Maintenance' : 'Save Maintenance Settings'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            },
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(48),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, _) => Card(
              color: colorScheme.errorContainer,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.error, color: colorScheme.onErrorContainer),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text('Failed to load settings: $error',
                          style: TextStyle(color: colorScheme.onErrorContainer)),
                    ),
                    TextButton(
                      onPressed: () {
                        _loaded = false;
                        ref.invalidate(_settingsProvider);
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
