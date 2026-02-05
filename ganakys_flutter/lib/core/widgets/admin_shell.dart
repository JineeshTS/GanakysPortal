import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';

class AdminShell extends ConsumerWidget {
  final Widget child;

  const AdminShell({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isWide = MediaQuery.sizeOf(context).width > 1000;
    final auth = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        leading: isWide
            ? null
            : Builder(
                builder: (ctx) => IconButton(
                  icon: const Icon(Icons.menu),
                  onPressed: () => Scaffold.of(ctx).openDrawer(),
                ),
              ),
        title: InkWell(
          onTap: () => context.go('/admin'),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.admin_panel_settings, color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: 8),
              Text(
                'Admin Panel',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
        actions: [
          TextButton.icon(
            onPressed: () => context.go('/'),
            icon: const Icon(Icons.open_in_new, size: 16),
            label: const Text('View Site'),
          ),
          const SizedBox(width: 4),
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: CircleAvatar(
              radius: 16,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Text(
                auth.user?.name.isNotEmpty == true ? auth.user!.name[0].toUpperCase() : 'A',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
      drawer: isWide ? null : _AdminDrawer(currentPath: GoRouterState.of(context).uri.path),
      body: isWide
          ? Row(
              children: [
                SizedBox(
                  width: 260,
                  child: _AdminSidebar(currentPath: GoRouterState.of(context).uri.path),
                ),
                const VerticalDivider(width: 1),
                Expanded(child: child),
              ],
            )
          : child,
    );
  }
}

class _AdminDrawer extends StatelessWidget {
  final String currentPath;

  const _AdminDrawer({required this.currentPath});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: _AdminNavContent(currentPath: currentPath, onItemTap: () => Navigator.pop(context)),
    );
  }
}

class _AdminSidebar extends StatelessWidget {
  final String currentPath;

  const _AdminSidebar({required this.currentPath});

  @override
  Widget build(BuildContext context) {
    return _AdminNavContent(currentPath: currentPath);
  }
}

class _AdminNavContent extends StatelessWidget {
  final String currentPath;
  final VoidCallback? onItemTap;

  const _AdminNavContent({required this.currentPath, this.onItemTap});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.symmetric(vertical: 8),
      children: [
        _NavItem(icon: Icons.dashboard, label: 'Dashboard', path: '/admin', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'Content'),
        _NavItem(icon: Icons.book, label: 'Courses', path: '/admin/courses', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.auto_awesome, label: 'Generation', path: '/admin/generate', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.category, label: 'Categories', path: '/admin/categories', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.route, label: 'Learning Paths', path: '/admin/learning-paths', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'Users'),
        _NavItem(icon: Icons.people, label: 'Users', path: '/admin/users', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.school, label: 'Enrollments', path: '/admin/enrollments', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'Revenue'),
        _NavItem(icon: Icons.payment, label: 'Payments', path: '/admin/payments', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.card_membership, label: 'Plans', path: '/admin/plans', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.local_offer, label: 'Coupons', path: '/admin/coupons', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'Community'),
        _NavItem(icon: Icons.star, label: 'Reviews', path: '/admin/reviews', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.forum, label: 'Discussions', path: '/admin/discussions', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'Communication'),
        _NavItem(icon: Icons.notifications, label: 'Notifications', path: '/admin/notifications', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.email, label: 'Email Templates', path: '/admin/email-templates', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.article, label: 'Pages', path: '/admin/pages', currentPath: currentPath, onTap: onItemTap),
        const _NavDivider(label: 'System'),
        _NavItem(icon: Icons.verified, label: 'Certificates', path: '/admin/certificates', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.analytics, label: 'Analytics', path: '/admin/analytics', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.settings, label: 'Settings', path: '/admin/settings', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.history, label: 'Audit Log', path: '/admin/audit-log', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.backup, label: 'Backups', path: '/admin/backups', currentPath: currentPath, onTap: onItemTap),
        _NavItem(icon: Icons.storage, label: 'Storage', path: '/admin/storage', currentPath: currentPath, onTap: onItemTap),
      ],
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String path;
  final String currentPath;
  final VoidCallback? onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.path,
    required this.currentPath,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isSelected = currentPath == path || (path != '/admin' && currentPath.startsWith(path));
    final colorScheme = Theme.of(context).colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 1),
      child: ListTile(
        dense: true,
        leading: Icon(icon, size: 20, color: isSelected ? colorScheme.primary : null),
        title: Text(label, style: TextStyle(
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          color: isSelected ? colorScheme.primary : null,
        )),
        selected: isSelected,
        selectedTileColor: colorScheme.primaryContainer.withValues(alpha: 0.3),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        onTap: () {
          onTap?.call();
          context.go(path);
        },
      ),
    );
  }
}

class _NavDivider extends StatelessWidget {
  final String label;

  const _NavDivider({required this.label});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
      child: Text(
        label.toUpperCase(),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Theme.of(context).colorScheme.outline,
              letterSpacing: 1.2,
            ),
      ),
    );
  }
}
