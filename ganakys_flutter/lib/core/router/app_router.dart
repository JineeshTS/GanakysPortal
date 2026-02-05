import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/auth/screens/forgot_password_screen.dart';
import '../../features/auth/screens/reset_password_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/courses/screens/course_catalog_screen.dart';
import '../../features/courses/screens/course_detail_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/player/screens/player_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/pages/screens/static_page_screen.dart';
import '../../features/payments/screens/pricing_screen.dart';
import '../../features/payments/screens/checkout_screen.dart';
import '../../features/payments/screens/billing_screen.dart';
import '../../features/certificates/screens/certificates_screen.dart';
import '../../features/admin/dashboard/screens/admin_dashboard_screen.dart';
import '../../features/admin/courses/screens/admin_courses_screen.dart';
import '../../features/admin/courses/screens/admin_course_detail_screen.dart';
import '../../features/admin/users/screens/admin_users_screen.dart';
import '../../features/admin/users/screens/admin_user_detail_screen.dart';
import '../../features/admin/categories/screens/admin_categories_screen.dart';
import '../../features/admin/generation/screens/admin_generation_screen.dart';
import '../../features/admin/settings/screens/admin_settings_screen.dart';
import '../../features/admin/audit/screens/admin_audit_log_screen.dart';
import '../../features/admin/payments/screens/admin_payments_screen.dart';
import '../../features/admin/plans/screens/admin_plans_screen.dart';
import '../../features/admin/coupons/screens/admin_coupons_screen.dart';
import '../../features/admin/reviews/screens/admin_reviews_screen.dart';
import '../../features/admin/discussions/screens/admin_discussions_screen.dart';
import '../../features/admin/notifications/screens/admin_notifications_screen.dart';
import '../../features/admin/email_templates/screens/admin_email_templates_screen.dart';
import '../../features/admin/pages/screens/admin_pages_screen.dart';
import '../../features/admin/certificates/screens/admin_certificates_screen.dart';
import '../../features/admin/analytics/screens/admin_analytics_screen.dart';
import '../../features/admin/enrollments/screens/admin_enrollments_screen.dart';
import '../../features/admin/learning_paths/screens/admin_learning_paths_screen.dart';
import '../../features/admin/backups/screens/admin_backups_screen.dart';
import '../../features/admin/storage/screens/admin_storage_screen.dart';
import '../widgets/shell_scaffold.dart';
import '../widgets/admin_shell.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();
final _adminNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/',
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isAdmin = authState.isAdmin;
      final path = state.uri.path;

      // Auth pages — redirect to home if already logged in
      final authPaths = ['/login', '/register', '/forgot-password'];
      if (authPaths.contains(path) && isAuthenticated) {
        return '/dashboard';
      }

      // Protected student routes
      final protectedPrefixes = ['/dashboard', '/my-courses', '/profile', '/settings', '/subscription', '/billing', '/certificates', '/checkout'];
      final isProtected = protectedPrefixes.any((p) => path.startsWith(p));
      if (isProtected && !isAuthenticated) {
        return '/login?redirect=$path';
      }

      // Admin routes
      if (path.startsWith('/admin') && !isAuthenticated) {
        return '/login?redirect=$path';
      }
      if (path.startsWith('/admin') && isAuthenticated && !isAdmin) {
        return '/dashboard';
      }

      return null;
    },
    routes: [
      // Public routes (no shell)
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/forgot-password',
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: '/reset-password/:token',
        builder: (context, state) => ResetPasswordScreen(
          token: state.pathParameters['token']!,
        ),
      ),

      // Course player (full screen, no shell)
      GoRoute(
        path: '/courses/:slug/learn',
        builder: (context, state) => PlayerScreen(
          courseSlug: state.pathParameters['slug']!,
          lectureId: state.uri.queryParameters['lecture'] != null
              ? int.tryParse(state.uri.queryParameters['lecture']!)
              : null,
        ),
      ),

      // Main shell (student/public routes with nav)
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => ShellScaffold(child: child),
        routes: [
          GoRoute(
            path: '/',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/courses',
            builder: (context, state) => const CourseCatalogScreen(),
          ),
          GoRoute(
            path: '/courses/:slug',
            builder: (context, state) => CourseDetailScreen(
              slug: state.pathParameters['slug']!,
            ),
          ),
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
          GoRoute(
            path: '/privacy',
            builder: (context, state) => const StaticPageScreen(slug: 'privacy'),
          ),
          GoRoute(
            path: '/terms',
            builder: (context, state) => const StaticPageScreen(slug: 'terms'),
          ),
          GoRoute(
            path: '/about',
            builder: (context, state) => const StaticPageScreen(slug: 'about'),
          ),
          GoRoute(
            path: '/pricing',
            builder: (context, state) => const PricingScreen(),
          ),
          GoRoute(
            path: '/my-courses',
            builder: (context, state) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/certificates',
            builder: (context, state) => const CertificatesScreen(),
          ),
          GoRoute(
            path: '/billing',
            builder: (context, state) => const BillingScreen(),
          ),
          GoRoute(
            path: '/checkout/:planSlug',
            builder: (context, state) => CheckoutScreen(
              planSlug: state.pathParameters['planSlug']!,
            ),
          ),
        ],
      ),

      // Admin shell
      ShellRoute(
        navigatorKey: _adminNavigatorKey,
        builder: (context, state, child) => AdminShell(child: child),
        routes: [
          GoRoute(
            path: '/admin',
            builder: (context, state) => const AdminDashboardScreen(),
          ),
          GoRoute(
            path: '/admin/courses',
            builder: (context, state) => const AdminCoursesScreen(),
          ),
          GoRoute(
            path: '/admin/courses/:id',
            builder: (context, state) => AdminCourseDetailScreen(
              courseId: int.parse(state.pathParameters['id']!),
            ),
          ),
          GoRoute(
            path: '/admin/users',
            builder: (context, state) => const AdminUsersScreen(),
          ),
          GoRoute(
            path: '/admin/users/:id',
            builder: (context, state) => AdminUserDetailScreen(
              userId: int.parse(state.pathParameters['id']!),
            ),
          ),
          GoRoute(
            path: '/admin/categories',
            builder: (context, state) => const AdminCategoriesScreen(),
          ),
          GoRoute(
            path: '/admin/generate',
            builder: (context, state) => const AdminGenerationScreen(),
          ),
          GoRoute(
            path: '/admin/settings',
            builder: (context, state) => const AdminSettingsScreen(),
          ),
          GoRoute(
            path: '/admin/audit-log',
            builder: (context, state) => const AdminAuditLogScreen(),
          ),
          GoRoute(
            path: '/admin/payments',
            builder: (context, state) => const AdminPaymentsScreen(),
          ),
          GoRoute(
            path: '/admin/plans',
            builder: (context, state) => const AdminPlansScreen(),
          ),
          GoRoute(
            path: '/admin/coupons',
            builder: (context, state) => const AdminCouponsScreen(),
          ),
          GoRoute(
            path: '/admin/reviews',
            builder: (context, state) => const AdminReviewsScreen(),
          ),
          GoRoute(
            path: '/admin/discussions',
            builder: (context, state) => const AdminDiscussionsScreen(),
          ),
          GoRoute(
            path: '/admin/notifications',
            builder: (context, state) => const AdminNotificationsScreen(),
          ),
          GoRoute(
            path: '/admin/email-templates',
            builder: (context, state) => const AdminEmailTemplatesScreen(),
          ),
          GoRoute(
            path: '/admin/pages',
            builder: (context, state) => const AdminPagesScreen(),
          ),
          GoRoute(
            path: '/admin/certificates',
            builder: (context, state) => const AdminCertificatesScreen(),
          ),
          GoRoute(
            path: '/admin/analytics',
            builder: (context, state) => const AdminAnalyticsScreen(),
          ),
          GoRoute(
            path: '/admin/enrollments',
            builder: (context, state) => const AdminEnrollmentsScreen(),
          ),
          GoRoute(
            path: '/admin/learning-paths',
            builder: (context, state) => const AdminLearningPathsScreen(),
          ),
          GoRoute(
            path: '/admin/backups',
            builder: (context, state) => const AdminBackupsScreen(),
          ),
          GoRoute(
            path: '/admin/storage',
            builder: (context, state) => const AdminStorageScreen(),
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      appBar: AppBar(title: const Text('Page Not Found')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Theme.of(context).colorScheme.error),
            const SizedBox(height: 16),
            Text(
              '404 - Page Not Found',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text('The page "${state.uri.path}" could not be found.'),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/'),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    ),
  );
});
