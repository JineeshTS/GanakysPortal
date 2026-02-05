import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/theme_provider.dart';

class ShellScaffold extends ConsumerWidget {
  final Widget child;

  const ShellScaffold({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final isWide = MediaQuery.sizeOf(context).width > 800;

    if (isWide) {
      return _DesktopShell(auth: auth, child: child);
    }
    return _MobileShell(auth: auth, child: child);
  }
}

class _DesktopShell extends StatelessWidget {
  final AuthState auth;
  final Widget child;

  const _DesktopShell({required this.auth, required this.child});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: InkWell(
          onTap: () => context.go('/'),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.school, color: colorScheme.primary),
              const SizedBox(width: 8),
              Text(
                'Ganakys Academy',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.primary,
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => context.go('/courses'),
            child: const Text('Courses'),
          ),
          if (auth.isAuthenticated) ...[
            TextButton(
              onPressed: () => context.go('/dashboard'),
              child: const Text('Dashboard'),
            ),
            if (auth.isAdmin)
              TextButton(
                onPressed: () => context.go('/admin'),
                child: const Text('Admin'),
              ),
            _UserMenu(auth: auth),
          ] else ...[
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('Login'),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: () => context.go('/register'),
              child: const Text('Sign Up'),
            ),
            const SizedBox(width: 8),
          ],
          const _ThemeToggle(),
          const SizedBox(width: 8),
        ],
      ),
      body: child,
    );
  }
}

class _MobileShell extends StatelessWidget {
  final AuthState auth;
  final Widget child;

  const _MobileShell({required this.auth, required this.child});

  int _getIndex(BuildContext context) {
    final path = GoRouterState.of(context).uri.path;
    if (path == '/') return 0;
    if (path.startsWith('/courses')) return 1;
    if (path.startsWith('/dashboard')) return 2;
    if (path.startsWith('/profile')) return 3;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final index = _getIndex(context);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.school, color: Theme.of(context).colorScheme.primary),
            const SizedBox(width: 8),
            Text(
              'Ganakys',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ],
        ),
        actions: [
          const _ThemeToggle(),
          if (!auth.isAuthenticated)
            TextButton(
              onPressed: () => context.go('/login'),
              child: const Text('Login'),
            ),
          if (auth.isAuthenticated && auth.isAdmin)
            IconButton(
              icon: const Icon(Icons.admin_panel_settings),
              onPressed: () => context.go('/admin'),
              tooltip: 'Admin Panel',
            ),
        ],
      ),
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (i) {
          switch (i) {
            case 0:
              context.go('/');
            case 1:
              context.go('/courses');
            case 2:
              if (auth.isAuthenticated) {
                context.go('/dashboard');
              } else {
                context.go('/login');
              }
            case 3:
              if (auth.isAuthenticated) {
                context.go('/profile');
              } else {
                context.go('/login');
              }
          }
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.explore_outlined), selectedIcon: Icon(Icons.explore), label: 'Courses'),
          NavigationDestination(icon: Icon(Icons.dashboard_outlined), selectedIcon: Icon(Icons.dashboard), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}

class _UserMenu extends ConsumerWidget {
  final AuthState auth;

  const _UserMenu({required this.auth});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PopupMenuButton<String>(
      offset: const Offset(0, 40),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircleAvatar(
              radius: 16,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer,
              child: Text(
                auth.user?.name.isNotEmpty == true ? auth.user!.name[0].toUpperCase() : '?',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 4),
            const Icon(Icons.arrow_drop_down),
          ],
        ),
      ),
      onSelected: (value) {
        switch (value) {
          case 'profile':
            context.go('/profile');
          case 'dashboard':
            context.go('/dashboard');
          case 'logout':
            ref.read(authProvider.notifier).logout();
            context.go('/');
        }
      },
      itemBuilder: (context) => [
        PopupMenuItem(
          enabled: false,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(auth.user?.name ?? '', style: Theme.of(context).textTheme.titleSmall),
              Text(auth.user?.email ?? '', style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
        const PopupMenuDivider(),
        const PopupMenuItem(value: 'dashboard', child: ListTile(leading: Icon(Icons.dashboard), title: Text('Dashboard'), dense: true)),
        const PopupMenuItem(value: 'profile', child: ListTile(leading: Icon(Icons.person), title: Text('Profile'), dense: true)),
        const PopupMenuDivider(),
        const PopupMenuItem(value: 'logout', child: ListTile(leading: Icon(Icons.logout), title: Text('Logout'), dense: true)),
      ],
    );
  }
}

class _ThemeToggle extends ConsumerWidget {
  const _ThemeToggle();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    final isDark = themeMode == ThemeMode.dark ||
        (themeMode == ThemeMode.system && MediaQuery.platformBrightnessOf(context) == Brightness.dark);

    return IconButton(
      icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode),
      onPressed: () => ref.read(themeProvider.notifier).toggle(),
      tooltip: isDark ? 'Light mode' : 'Dark mode',
    );
  }
}
