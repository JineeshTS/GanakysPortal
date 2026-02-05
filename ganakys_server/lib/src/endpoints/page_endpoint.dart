import 'package:serverpod/serverpod.dart';
import '../generated/protocol.dart';

class PageEndpoint extends Endpoint {
  @override
  bool get requireLogin => false;

  // Get published page by slug (public)
  Future<ContentPage?> getPage(Session session, String slug) async {
    return await ContentPage.db.findFirstRow(session,
      where: (t) => t.slug.equals(slug) & t.isPublished.equals(true),
    );
  }

  // Get all published pages
  Future<List<ContentPage>> getPages(Session session) async {
    return await ContentPage.db.find(session,
      where: (t) => t.isPublished.equals(true),
    );
  }

  // Get announcements
  Future<List<Announcement>> getActiveAnnouncements(Session session) async {
    return await Announcement.db.find(session,
      where: (t) => t.isActive.equals(true),
    );
  }

  // Get site settings (public subset)
  Future<Map<String, String>> getPublicSettings(Session session) async {
    final publicKeys = [
      'site_name', 'tagline', 'logo_url', 'favicon_url',
      'primary_color', 'secondary_color', 'maintenance_mode',
    ];

    final settings = await SiteSetting.db.find(session);
    final result = <String, String>{};
    for (final setting in settings) {
      if (publicKeys.contains(setting.key)) {
        result[setting.key] = setting.value;
      }
    }
    return result;
  }
}
