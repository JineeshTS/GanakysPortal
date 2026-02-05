/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod/serverpod.dart' as _i1;
import '../endpoints/admin_endpoint.dart' as _i2;
import '../endpoints/auth_endpoint.dart' as _i3;
import '../endpoints/bookmark_endpoint.dart' as _i4;
import '../endpoints/certificate_endpoint.dart' as _i5;
import '../endpoints/course_endpoint.dart' as _i6;
import '../endpoints/discussion_endpoint.dart' as _i7;
import '../endpoints/enrollment_endpoint.dart' as _i8;
import '../endpoints/generation_endpoint.dart' as _i9;
import '../endpoints/health_endpoint.dart' as _i10;
import '../endpoints/note_endpoint.dart' as _i11;
import '../endpoints/page_endpoint.dart' as _i12;
import '../endpoints/payment_endpoint.dart' as _i13;
import '../endpoints/profile_endpoint.dart' as _i14;
import '../endpoints/quiz_endpoint.dart' as _i15;
import '../endpoints/review_endpoint.dart' as _i16;

class Endpoints extends _i1.EndpointDispatch {
  @override
  void initializeEndpoints(_i1.Server server) {
    var endpoints = <String, _i1.Endpoint>{
      'admin': _i2.AdminEndpoint()
        ..initialize(
          server,
          'admin',
          null,
        ),
      'auth': _i3.AuthEndpoint()
        ..initialize(
          server,
          'auth',
          null,
        ),
      'bookmark': _i4.BookmarkEndpoint()
        ..initialize(
          server,
          'bookmark',
          null,
        ),
      'certificate': _i5.CertificateEndpoint()
        ..initialize(
          server,
          'certificate',
          null,
        ),
      'course': _i6.CourseEndpoint()
        ..initialize(
          server,
          'course',
          null,
        ),
      'discussion': _i7.DiscussionEndpoint()
        ..initialize(
          server,
          'discussion',
          null,
        ),
      'enrollment': _i8.EnrollmentEndpoint()
        ..initialize(
          server,
          'enrollment',
          null,
        ),
      'generation': _i9.GenerationEndpoint()
        ..initialize(
          server,
          'generation',
          null,
        ),
      'health': _i10.HealthEndpoint()
        ..initialize(
          server,
          'health',
          null,
        ),
      'note': _i11.NoteEndpoint()
        ..initialize(
          server,
          'note',
          null,
        ),
      'page': _i12.PageEndpoint()
        ..initialize(
          server,
          'page',
          null,
        ),
      'payment': _i13.PaymentEndpoint()
        ..initialize(
          server,
          'payment',
          null,
        ),
      'profile': _i14.ProfileEndpoint()
        ..initialize(
          server,
          'profile',
          null,
        ),
      'quiz': _i15.QuizEndpoint()
        ..initialize(
          server,
          'quiz',
          null,
        ),
      'review': _i16.ReviewEndpoint()
        ..initialize(
          server,
          'review',
          null,
        ),
    };
    connectors['admin'] = _i1.EndpointConnector(
      name: 'admin',
      endpoint: endpoints['admin']!,
      methodConnectors: {
        'getDashboardStats': _i1.MethodConnector(
          name: 'getDashboardStats',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint)
                  .getDashboardStats(session),
        ),
        'adminListCourses': _i1.MethodConnector(
          name: 'adminListCourses',
          params: {
            'search': _i1.ParameterDescription(
              name: 'search',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'status': _i1.ParameterDescription(
              name: 'status',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminListCourses(
            session,
            params['search'],
            params['status'],
            params['categoryId'],
            params['difficulty'],
            params['page'],
            params['pageSize'],
          ),
        ),
        'adminGetCourse': _i1.MethodConnector(
          name: 'adminGetCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminGetCourse(
            session,
            params['courseId'],
          ),
        ),
        'adminCreateCourse': _i1.MethodConnector(
          name: 'adminCreateCourse',
          params: {
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'slug': _i1.ParameterDescription(
              name: 'slug',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'description': _i1.ParameterDescription(
              name: 'description',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminCreateCourse(
            session,
            params['title'],
            params['slug'],
            params['description'],
            params['categoryId'],
            params['difficulty'],
          ),
        ),
        'adminUpdateCourse': _i1.MethodConnector(
          name: 'adminUpdateCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'description': _i1.ParameterDescription(
              name: 'description',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'isPublished': _i1.ParameterDescription(
              name: 'isPublished',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
            'isFeatured': _i1.ParameterDescription(
              name: 'isFeatured',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
            'price': _i1.ParameterDescription(
              name: 'price',
              type: _i1.getType<double>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateCourse(
            session,
            params['courseId'],
            params['title'],
            params['description'],
            params['categoryId'],
            params['difficulty'],
            params['isPublished'],
            params['isFeatured'],
            params['price'],
          ),
        ),
        'adminDeleteCourse': _i1.MethodConnector(
          name: 'adminDeleteCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminDeleteCourse(
            session,
            params['courseId'],
          ),
        ),
        'adminDuplicateCourse': _i1.MethodConnector(
          name: 'adminDuplicateCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminDuplicateCourse(
            session,
            params['courseId'],
          ),
        ),
        'adminCreateSection': _i1.MethodConnector(
          name: 'adminCreateSection',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'sortOrder': _i1.ParameterDescription(
              name: 'sortOrder',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminCreateSection(
            session,
            params['courseId'],
            params['title'],
            params['sortOrder'],
          ),
        ),
        'adminUpdateSection': _i1.MethodConnector(
          name: 'adminUpdateSection',
          params: {
            'sectionId': _i1.ParameterDescription(
              name: 'sectionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'description': _i1.ParameterDescription(
              name: 'description',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'sortOrder': _i1.ParameterDescription(
              name: 'sortOrder',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateSection(
            session,
            params['sectionId'],
            params['title'],
            params['description'],
            params['sortOrder'],
          ),
        ),
        'adminDeleteSection': _i1.MethodConnector(
          name: 'adminDeleteSection',
          params: {
            'sectionId': _i1.ParameterDescription(
              name: 'sectionId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminDeleteSection(
            session,
            params['sectionId'],
          ),
        ),
        'adminCreateLecture': _i1.MethodConnector(
          name: 'adminCreateLecture',
          params: {
            'sectionId': _i1.ParameterDescription(
              name: 'sectionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'type': _i1.ParameterDescription(
              name: 'type',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'sortOrder': _i1.ParameterDescription(
              name: 'sortOrder',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminCreateLecture(
            session,
            params['sectionId'],
            params['courseId'],
            params['title'],
            params['type'],
            params['sortOrder'],
          ),
        ),
        'adminUpdateLecture': _i1.MethodConnector(
          name: 'adminUpdateLecture',
          params: {
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'content': _i1.ParameterDescription(
              name: 'content',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'scriptJson': _i1.ParameterDescription(
              name: 'scriptJson',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'isFreePreview': _i1.ParameterDescription(
              name: 'isFreePreview',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateLecture(
            session,
            params['lectureId'],
            params['title'],
            params['content'],
            params['scriptJson'],
            params['isFreePreview'],
          ),
        ),
        'adminDeleteLecture': _i1.MethodConnector(
          name: 'adminDeleteLecture',
          params: {
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminDeleteLecture(
            session,
            params['lectureId'],
          ),
        ),
        'adminReorderSections': _i1.MethodConnector(
          name: 'adminReorderSections',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'orderJson': _i1.ParameterDescription(
              name: 'orderJson',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminReorderSections(
            session,
            params['courseId'],
            params['orderJson'],
          ),
        ),
        'adminReorderLectures': _i1.MethodConnector(
          name: 'adminReorderLectures',
          params: {
            'sectionId': _i1.ParameterDescription(
              name: 'sectionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'orderJson': _i1.ParameterDescription(
              name: 'orderJson',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminReorderLectures(
            session,
            params['sectionId'],
            params['orderJson'],
          ),
        ),
        'adminListUsers': _i1.MethodConnector(
          name: 'adminListUsers',
          params: {
            'search': _i1.ParameterDescription(
              name: 'search',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'role': _i1.ParameterDescription(
              name: 'role',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'subscriptionStatus': _i1.ParameterDescription(
              name: 'subscriptionStatus',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminListUsers(
            session,
            params['search'],
            params['role'],
            params['subscriptionStatus'],
            params['page'],
            params['pageSize'],
          ),
        ),
        'adminGetUser': _i1.MethodConnector(
          name: 'adminGetUser',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminGetUser(
            session,
            params['userId'],
          ),
        ),
        'adminUpdateUserRole': _i1.MethodConnector(
          name: 'adminUpdateUserRole',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'role': _i1.ParameterDescription(
              name: 'role',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateUserRole(
            session,
            params['userId'],
            params['role'],
          ),
        ),
        'adminBanUser': _i1.MethodConnector(
          name: 'adminBanUser',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'banned': _i1.ParameterDescription(
              name: 'banned',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminBanUser(
            session,
            params['userId'],
            params['banned'],
          ),
        ),
        'adminForcePasswordReset': _i1.MethodConnector(
          name: 'adminForcePasswordReset',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminForcePasswordReset(
            session,
            params['userId'],
          ),
        ),
        'adminListCategories': _i1.MethodConnector(
          name: 'adminListCategories',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint)
                  .adminListCategories(session),
        ),
        'adminCreateCategory': _i1.MethodConnector(
          name: 'adminCreateCategory',
          params: {
            'name': _i1.ParameterDescription(
              name: 'name',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'slug': _i1.ParameterDescription(
              name: 'slug',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'description': _i1.ParameterDescription(
              name: 'description',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'icon': _i1.ParameterDescription(
              name: 'icon',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'sortOrder': _i1.ParameterDescription(
              name: 'sortOrder',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminCreateCategory(
            session,
            params['name'],
            params['slug'],
            params['description'],
            params['icon'],
            params['sortOrder'],
          ),
        ),
        'adminUpdateCategory': _i1.MethodConnector(
          name: 'adminUpdateCategory',
          params: {
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'name': _i1.ParameterDescription(
              name: 'name',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'description': _i1.ParameterDescription(
              name: 'description',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'icon': _i1.ParameterDescription(
              name: 'icon',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'sortOrder': _i1.ParameterDescription(
              name: 'sortOrder',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateCategory(
            session,
            params['categoryId'],
            params['name'],
            params['description'],
            params['icon'],
            params['sortOrder'],
          ),
        ),
        'adminDeleteCategory': _i1.MethodConnector(
          name: 'adminDeleteCategory',
          params: {
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminDeleteCategory(
            session,
            params['categoryId'],
          ),
        ),
        'adminGetSettings': _i1.MethodConnector(
          name: 'adminGetSettings',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint)
                  .adminGetSettings(session),
        ),
        'adminUpdateSetting': _i1.MethodConnector(
          name: 'adminUpdateSetting',
          params: {
            'key': _i1.ParameterDescription(
              name: 'key',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'value': _i1.ParameterDescription(
              name: 'value',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminUpdateSetting(
            session,
            params['key'],
            params['value'],
          ),
        ),
        'adminToggleMaintenanceMode': _i1.MethodConnector(
          name: 'adminToggleMaintenanceMode',
          params: {
            'enabled': _i1.ParameterDescription(
              name: 'enabled',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
            'message': _i1.ParameterDescription(
              name: 'message',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint)
                  .adminToggleMaintenanceMode(
            session,
            params['enabled'],
            params['message'],
          ),
        ),
        'adminGetAuditLog': _i1.MethodConnector(
          name: 'adminGetAuditLog',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'action': _i1.ParameterDescription(
              name: 'action',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'entityType': _i1.ParameterDescription(
              name: 'entityType',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['admin'] as _i2.AdminEndpoint).adminGetAuditLog(
            session,
            params['userId'],
            params['action'],
            params['entityType'],
            params['page'],
            params['pageSize'],
          ),
        ),
      },
    );
    connectors['auth'] = _i1.EndpointConnector(
      name: 'auth',
      endpoint: endpoints['auth']!,
      methodConnectors: {
        'register': _i1.MethodConnector(
          name: 'register',
          params: {
            'email': _i1.ParameterDescription(
              name: 'email',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'name': _i1.ParameterDescription(
              name: 'name',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'password': _i1.ParameterDescription(
              name: 'password',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).register(
            session,
            params['email'],
            params['name'],
            params['password'],
          ),
        ),
        'login': _i1.MethodConnector(
          name: 'login',
          params: {
            'email': _i1.ParameterDescription(
              name: 'email',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'password': _i1.ParameterDescription(
              name: 'password',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'deviceInfo': _i1.ParameterDescription(
              name: 'deviceInfo',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'ipAddress': _i1.ParameterDescription(
              name: 'ipAddress',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).login(
            session,
            params['email'],
            params['password'],
            params['deviceInfo'],
            params['ipAddress'],
          ),
        ),
        'verify2fa': _i1.MethodConnector(
          name: 'verify2fa',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'code': _i1.ParameterDescription(
              name: 'code',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'deviceInfo': _i1.ParameterDescription(
              name: 'deviceInfo',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'ipAddress': _i1.ParameterDescription(
              name: 'ipAddress',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).verify2fa(
            session,
            params['userId'],
            params['code'],
            params['deviceInfo'],
            params['ipAddress'],
          ),
        ),
        'refreshToken': _i1.MethodConnector(
          name: 'refreshToken',
          params: {
            'refreshToken': _i1.ParameterDescription(
              name: 'refreshToken',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'ipAddress': _i1.ParameterDescription(
              name: 'ipAddress',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).refreshToken(
            session,
            params['refreshToken'],
            params['ipAddress'],
          ),
        ),
        'verifyEmail': _i1.MethodConnector(
          name: 'verifyEmail',
          params: {
            'token': _i1.ParameterDescription(
              name: 'token',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).verifyEmail(
            session,
            params['token'],
          ),
        ),
        'forgotPassword': _i1.MethodConnector(
          name: 'forgotPassword',
          params: {
            'email': _i1.ParameterDescription(
              name: 'email',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).forgotPassword(
            session,
            params['email'],
          ),
        ),
        'resetPassword': _i1.MethodConnector(
          name: 'resetPassword',
          params: {
            'token': _i1.ParameterDescription(
              name: 'token',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'newPassword': _i1.ParameterDescription(
              name: 'newPassword',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).resetPassword(
            session,
            params['token'],
            params['newPassword'],
          ),
        ),
        'logout': _i1.MethodConnector(
          name: 'logout',
          params: {
            'refreshToken': _i1.ParameterDescription(
              name: 'refreshToken',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).logout(
            session,
            params['refreshToken'],
          ),
        ),
        'getSessions': _i1.MethodConnector(
          name: 'getSessions',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).getSessions(
            session,
            params['userId'],
          ),
        ),
        'revokeSession': _i1.MethodConnector(
          name: 'revokeSession',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'sessionId': _i1.ParameterDescription(
              name: 'sessionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['auth'] as _i3.AuthEndpoint).revokeSession(
            session,
            params['userId'],
            params['sessionId'],
          ),
        ),
      },
    );
    connectors['bookmark'] = _i1.EndpointConnector(
      name: 'bookmark',
      endpoint: endpoints['bookmark']!,
      methodConnectors: {
        'getBookmarks': _i1.MethodConnector(
          name: 'getBookmarks',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['bookmark'] as _i4.BookmarkEndpoint).getBookmarks(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
        'createBookmark': _i1.MethodConnector(
          name: 'createBookmark',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'timestampSeconds': _i1.ParameterDescription(
              name: 'timestampSeconds',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'label': _i1.ParameterDescription(
              name: 'label',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['bookmark'] as _i4.BookmarkEndpoint).createBookmark(
            session,
            params['userId'],
            params['lectureId'],
            params['courseId'],
            params['timestampSeconds'],
            params['label'],
          ),
        ),
        'deleteBookmark': _i1.MethodConnector(
          name: 'deleteBookmark',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'bookmarkId': _i1.ParameterDescription(
              name: 'bookmarkId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['bookmark'] as _i4.BookmarkEndpoint).deleteBookmark(
            session,
            params['userId'],
            params['bookmarkId'],
          ),
        ),
      },
    );
    connectors['certificate'] = _i1.EndpointConnector(
      name: 'certificate',
      endpoint: endpoints['certificate']!,
      methodConnectors: {
        'generateCertificate': _i1.MethodConnector(
          name: 'generateCertificate',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['certificate'] as _i5.CertificateEndpoint)
                  .generateCertificate(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
        'getCertificates': _i1.MethodConnector(
          name: 'getCertificates',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['certificate'] as _i5.CertificateEndpoint)
                  .getCertificates(
            session,
            params['userId'],
          ),
        ),
        'verifyCertificate': _i1.MethodConnector(
          name: 'verifyCertificate',
          params: {
            'certificateNumber': _i1.ParameterDescription(
              name: 'certificateNumber',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['certificate'] as _i5.CertificateEndpoint)
                  .verifyCertificate(
            session,
            params['certificateNumber'],
          ),
        ),
      },
    );
    connectors['course'] = _i1.EndpointConnector(
      name: 'course',
      endpoint: endpoints['course']!,
      methodConnectors: {
        'listCourses': _i1.MethodConnector(
          name: 'listCourses',
          params: {
            'search': _i1.ParameterDescription(
              name: 'search',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'sortBy': _i1.ParameterDescription(
              name: 'sortBy',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint).listCourses(
            session,
            search: params['search'],
            categoryId: params['categoryId'],
            difficulty: params['difficulty'],
            sortBy: params['sortBy'],
            page: params['page'],
            pageSize: params['pageSize'],
          ),
        ),
        'getCourseBySlug': _i1.MethodConnector(
          name: 'getCourseBySlug',
          params: {
            'slug': _i1.ParameterDescription(
              name: 'slug',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint).getCourseBySlug(
            session,
            params['slug'],
          ),
        ),
        'getCourse': _i1.MethodConnector(
          name: 'getCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint).getCourse(
            session,
            params['courseId'],
          ),
        ),
        'getCategories': _i1.MethodConnector(
          name: 'getCategories',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint)
                  .getCategories(session),
        ),
        'getFeaturedCourses': _i1.MethodConnector(
          name: 'getFeaturedCourses',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint)
                  .getFeaturedCourses(session),
        ),
        'getCourseCurriculum': _i1.MethodConnector(
          name: 'getCourseCurriculum',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['course'] as _i6.CourseEndpoint).getCourseCurriculum(
            session,
            params['courseId'],
            params['userId'],
          ),
        ),
      },
    );
    connectors['discussion'] = _i1.EndpointConnector(
      name: 'discussion',
      endpoint: endpoints['discussion']!,
      methodConnectors: {
        'getDiscussions': _i1.MethodConnector(
          name: 'getDiscussions',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['discussion'] as _i7.DiscussionEndpoint)
                  .getDiscussions(
            session,
            params['courseId'],
            params['lectureId'],
            params['page'],
            params['pageSize'],
          ),
        ),
        'createDiscussion': _i1.MethodConnector(
          name: 'createDiscussion',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'title': _i1.ParameterDescription(
              name: 'title',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'content': _i1.ParameterDescription(
              name: 'content',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['discussion'] as _i7.DiscussionEndpoint)
                  .createDiscussion(
            session,
            params['userId'],
            params['courseId'],
            params['lectureId'],
            params['title'],
            params['content'],
          ),
        ),
        'getDiscussionReplies': _i1.MethodConnector(
          name: 'getDiscussionReplies',
          params: {
            'discussionId': _i1.ParameterDescription(
              name: 'discussionId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['discussion'] as _i7.DiscussionEndpoint)
                  .getDiscussionReplies(
            session,
            params['discussionId'],
          ),
        ),
        'createReply': _i1.MethodConnector(
          name: 'createReply',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'discussionId': _i1.ParameterDescription(
              name: 'discussionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'content': _i1.ParameterDescription(
              name: 'content',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['discussion'] as _i7.DiscussionEndpoint).createReply(
            session,
            params['userId'],
            params['discussionId'],
            params['content'],
          ),
        ),
        'resolveDiscussion': _i1.MethodConnector(
          name: 'resolveDiscussion',
          params: {
            'discussionId': _i1.ParameterDescription(
              name: 'discussionId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['discussion'] as _i7.DiscussionEndpoint)
                  .resolveDiscussion(
            session,
            params['discussionId'],
            params['userId'],
          ),
        ),
      },
    );
    connectors['enrollment'] = _i1.EndpointConnector(
      name: 'enrollment',
      endpoint: endpoints['enrollment']!,
      methodConnectors: {
        'enroll': _i1.MethodConnector(
          name: 'enroll',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['enrollment'] as _i8.EnrollmentEndpoint).enroll(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
        'getMyEnrollments': _i1.MethodConnector(
          name: 'getMyEnrollments',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['enrollment'] as _i8.EnrollmentEndpoint)
                  .getMyEnrollments(
            session,
            params['userId'],
          ),
        ),
        'updateProgress': _i1.MethodConnector(
          name: 'updateProgress',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'positionSeconds': _i1.ParameterDescription(
              name: 'positionSeconds',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'watchTimeSeconds': _i1.ParameterDescription(
              name: 'watchTimeSeconds',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'isCompleted': _i1.ParameterDescription(
              name: 'isCompleted',
              type: _i1.getType<bool>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['enrollment'] as _i8.EnrollmentEndpoint)
                  .updateProgress(
            session,
            params['userId'],
            params['lectureId'],
            params['courseId'],
            params['positionSeconds'],
            params['watchTimeSeconds'],
            params['isCompleted'],
          ),
        ),
        'getContinueLearning': _i1.MethodConnector(
          name: 'getContinueLearning',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['enrollment'] as _i8.EnrollmentEndpoint)
                  .getContinueLearning(
            session,
            params['userId'],
          ),
        ),
      },
    );
    connectors['generation'] = _i1.EndpointConnector(
      name: 'generation',
      endpoint: endpoints['generation']!,
      methodConnectors: {
        'listJobs': _i1.MethodConnector(
          name: 'listJobs',
          params: {
            'status': _i1.ParameterDescription(
              name: 'status',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint).listJobs(
            session,
            status: params['status'],
            page: params['page'],
            pageSize: params['pageSize'],
          ),
        ),
        'getJob': _i1.MethodConnector(
          name: 'getJob',
          params: {
            'jobId': _i1.ParameterDescription(
              name: 'jobId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint).getJob(
            session,
            params['jobId'],
          ),
        ),
        'startGeneration': _i1.MethodConnector(
          name: 'startGeneration',
          params: {
            'topic': _i1.ParameterDescription(
              name: 'topic',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'targetDurationMinutes': _i1.ParameterDescription(
              name: 'targetDurationMinutes',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'createdBy': _i1.ParameterDescription(
              name: 'createdBy',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint)
                  .startGeneration(
            session,
            params['topic'],
            params['categoryId'],
            params['difficulty'],
            params['targetDurationMinutes'],
            params['createdBy'],
          ),
        ),
        'startStepByStep': _i1.MethodConnector(
          name: 'startStepByStep',
          params: {
            'topic': _i1.ParameterDescription(
              name: 'topic',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'createdBy': _i1.ParameterDescription(
              name: 'createdBy',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint)
                  .startStepByStep(
            session,
            params['topic'],
            params['createdBy'],
          ),
        ),
        'generateOutline': _i1.MethodConnector(
          name: 'generateOutline',
          params: {
            'jobId': _i1.ParameterDescription(
              name: 'jobId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'topic': _i1.ParameterDescription(
              name: 'topic',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'difficulty': _i1.ParameterDescription(
              name: 'difficulty',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'targetDurationMinutes': _i1.ParameterDescription(
              name: 'targetDurationMinutes',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint)
                  .generateOutline(
            session,
            params['jobId'],
            params['topic'],
            params['difficulty'],
            params['targetDurationMinutes'],
          ),
        ),
        'saveOutline': _i1.MethodConnector(
          name: 'saveOutline',
          params: {
            'jobId': _i1.ParameterDescription(
              name: 'jobId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'outlineJson': _i1.ParameterDescription(
              name: 'outlineJson',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint).saveOutline(
            session,
            params['jobId'],
            params['outlineJson'],
          ),
        ),
        'importPipelineOutput': _i1.MethodConnector(
          name: 'importPipelineOutput',
          params: {
            'jobId': _i1.ParameterDescription(
              name: 'jobId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'categoryId': _i1.ParameterDescription(
              name: 'categoryId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint)
                  .importPipelineOutput(
            session,
            params['jobId'],
            params['categoryId'],
          ),
        ),
        'retryJob': _i1.MethodConnector(
          name: 'retryJob',
          params: {
            'jobId': _i1.ParameterDescription(
              name: 'jobId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['generation'] as _i9.GenerationEndpoint).retryJob(
            session,
            params['jobId'],
          ),
        ),
      },
    );
    connectors['health'] = _i1.EndpointConnector(
      name: 'health',
      endpoint: endpoints['health']!,
      methodConnectors: {
        'check': _i1.MethodConnector(
          name: 'check',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['health'] as _i10.HealthEndpoint).check(session),
        )
      },
    );
    connectors['note'] = _i1.EndpointConnector(
      name: 'note',
      endpoint: endpoints['note']!,
      methodConnectors: {
        'getNotes': _i1.MethodConnector(
          name: 'getNotes',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['note'] as _i11.NoteEndpoint).getNotes(
            session,
            params['userId'],
            params['lectureId'],
          ),
        ),
        'getCourseNotes': _i1.MethodConnector(
          name: 'getCourseNotes',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['note'] as _i11.NoteEndpoint).getCourseNotes(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
        'createNote': _i1.MethodConnector(
          name: 'createNote',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'lectureId': _i1.ParameterDescription(
              name: 'lectureId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'content': _i1.ParameterDescription(
              name: 'content',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'timestampSeconds': _i1.ParameterDescription(
              name: 'timestampSeconds',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['note'] as _i11.NoteEndpoint).createNote(
            session,
            params['userId'],
            params['lectureId'],
            params['courseId'],
            params['content'],
            params['timestampSeconds'],
          ),
        ),
        'updateNote': _i1.MethodConnector(
          name: 'updateNote',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'noteId': _i1.ParameterDescription(
              name: 'noteId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'content': _i1.ParameterDescription(
              name: 'content',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['note'] as _i11.NoteEndpoint).updateNote(
            session,
            params['userId'],
            params['noteId'],
            params['content'],
          ),
        ),
        'deleteNote': _i1.MethodConnector(
          name: 'deleteNote',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'noteId': _i1.ParameterDescription(
              name: 'noteId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['note'] as _i11.NoteEndpoint).deleteNote(
            session,
            params['userId'],
            params['noteId'],
          ),
        ),
      },
    );
    connectors['page'] = _i1.EndpointConnector(
      name: 'page',
      endpoint: endpoints['page']!,
      methodConnectors: {
        'getPage': _i1.MethodConnector(
          name: 'getPage',
          params: {
            'slug': _i1.ParameterDescription(
              name: 'slug',
              type: _i1.getType<String>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['page'] as _i12.PageEndpoint).getPage(
            session,
            params['slug'],
          ),
        ),
        'getPages': _i1.MethodConnector(
          name: 'getPages',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['page'] as _i12.PageEndpoint).getPages(session),
        ),
        'getActiveAnnouncements': _i1.MethodConnector(
          name: 'getActiveAnnouncements',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['page'] as _i12.PageEndpoint)
                  .getActiveAnnouncements(session),
        ),
        'getPublicSettings': _i1.MethodConnector(
          name: 'getPublicSettings',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['page'] as _i12.PageEndpoint)
                  .getPublicSettings(session),
        ),
      },
    );
    connectors['payment'] = _i1.EndpointConnector(
      name: 'payment',
      endpoint: endpoints['payment']!,
      methodConnectors: {
        'getPlans': _i1.MethodConnector(
          name: 'getPlans',
          params: {},
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).getPlans(session),
        ),
        'createCheckout': _i1.MethodConnector(
          name: 'createCheckout',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'planId': _i1.ParameterDescription(
              name: 'planId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'gateway': _i1.ParameterDescription(
              name: 'gateway',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'couponCode': _i1.ParameterDescription(
              name: 'couponCode',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).createCheckout(
            session,
            params['userId'],
            params['planId'],
            params['gateway'],
            params['couponCode'],
          ),
        ),
        'confirmPayment': _i1.MethodConnector(
          name: 'confirmPayment',
          params: {
            'paymentId': _i1.ParameterDescription(
              name: 'paymentId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'gatewayPaymentId': _i1.ParameterDescription(
              name: 'gatewayPaymentId',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'gatewayOrderId': _i1.ParameterDescription(
              name: 'gatewayOrderId',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).confirmPayment(
            session,
            params['paymentId'],
            params['gatewayPaymentId'],
            params['gatewayOrderId'],
          ),
        ),
        'getBillingHistory': _i1.MethodConnector(
          name: 'getBillingHistory',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).getBillingHistory(
            session,
            params['userId'],
          ),
        ),
        'getSubscription': _i1.MethodConnector(
          name: 'getSubscription',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).getSubscription(
            session,
            params['userId'],
          ),
        ),
        'cancelSubscription': _i1.MethodConnector(
          name: 'cancelSubscription',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).cancelSubscription(
            session,
            params['userId'],
          ),
        ),
        'validateCoupon': _i1.MethodConnector(
          name: 'validateCoupon',
          params: {
            'code': _i1.ParameterDescription(
              name: 'code',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'planId': _i1.ParameterDescription(
              name: 'planId',
              type: _i1.getType<int?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['payment'] as _i13.PaymentEndpoint).validateCoupon(
            session,
            params['code'],
            params['planId'],
          ),
        ),
      },
    );
    connectors['profile'] = _i1.EndpointConnector(
      name: 'profile',
      endpoint: endpoints['profile']!,
      methodConnectors: {
        'getProfile': _i1.MethodConnector(
          name: 'getProfile',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).getProfile(
            session,
            params['userId'],
          ),
        ),
        'updateProfile': _i1.MethodConnector(
          name: 'updateProfile',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'name': _i1.ParameterDescription(
              name: 'name',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'bio': _i1.ParameterDescription(
              name: 'bio',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'avatarUrl': _i1.ParameterDescription(
              name: 'avatarUrl',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
            'locale': _i1.ParameterDescription(
              name: 'locale',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).updateProfile(
            session,
            params['userId'],
            params['name'],
            params['bio'],
            params['avatarUrl'],
            params['locale'],
          ),
        ),
        'changePassword': _i1.MethodConnector(
          name: 'changePassword',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'currentPassword': _i1.ParameterDescription(
              name: 'currentPassword',
              type: _i1.getType<String>(),
              nullable: false,
            ),
            'newPassword': _i1.ParameterDescription(
              name: 'newPassword',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).changePassword(
            session,
            params['userId'],
            params['currentPassword'],
            params['newPassword'],
          ),
        ),
        'exportData': _i1.MethodConnector(
          name: 'exportData',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).exportData(
            session,
            params['userId'],
          ),
        ),
        'requestDeletion': _i1.MethodConnector(
          name: 'requestDeletion',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'password': _i1.ParameterDescription(
              name: 'password',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).requestDeletion(
            session,
            params['userId'],
            params['password'],
          ),
        ),
        'cancelDeletion': _i1.MethodConnector(
          name: 'cancelDeletion',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).cancelDeletion(
            session,
            params['userId'],
          ),
        ),
        'getWishlist': _i1.MethodConnector(
          name: 'getWishlist',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).getWishlist(
            session,
            params['userId'],
          ),
        ),
        'toggleWishlist': _i1.MethodConnector(
          name: 'toggleWishlist',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).toggleWishlist(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
        'getNotifications': _i1.MethodConnector(
          name: 'getNotifications',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint).getNotifications(
            session,
            params['userId'],
          ),
        ),
        'markNotificationRead': _i1.MethodConnector(
          name: 'markNotificationRead',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'notificationId': _i1.ParameterDescription(
              name: 'notificationId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['profile'] as _i14.ProfileEndpoint)
                  .markNotificationRead(
            session,
            params['userId'],
            params['notificationId'],
          ),
        ),
      },
    );
    connectors['quiz'] = _i1.EndpointConnector(
      name: 'quiz',
      endpoint: endpoints['quiz']!,
      methodConnectors: {
        'getQuizzesForCourse': _i1.MethodConnector(
          name: 'getQuizzesForCourse',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['quiz'] as _i15.QuizEndpoint).getQuizzesForCourse(
            session,
            params['courseId'],
          ),
        ),
        'getQuiz': _i1.MethodConnector(
          name: 'getQuiz',
          params: {
            'quizId': _i1.ParameterDescription(
              name: 'quizId',
              type: _i1.getType<int>(),
              nullable: false,
            )
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['quiz'] as _i15.QuizEndpoint).getQuiz(
            session,
            params['quizId'],
          ),
        ),
        'submitQuizAttempt': _i1.MethodConnector(
          name: 'submitQuizAttempt',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'quizId': _i1.ParameterDescription(
              name: 'quizId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'answersJson': _i1.ParameterDescription(
              name: 'answersJson',
              type: _i1.getType<String>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['quiz'] as _i15.QuizEndpoint).submitQuizAttempt(
            session,
            params['userId'],
            params['quizId'],
            params['answersJson'],
          ),
        ),
        'getQuizAttempts': _i1.MethodConnector(
          name: 'getQuizAttempts',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['quiz'] as _i15.QuizEndpoint).getQuizAttempts(
            session,
            params['userId'],
            params['courseId'],
          ),
        ),
      },
    );
    connectors['review'] = _i1.EndpointConnector(
      name: 'review',
      endpoint: endpoints['review']!,
      methodConnectors: {
        'getCourseReviews': _i1.MethodConnector(
          name: 'getCourseReviews',
          params: {
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'page': _i1.ParameterDescription(
              name: 'page',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'pageSize': _i1.ParameterDescription(
              name: 'pageSize',
              type: _i1.getType<int>(),
              nullable: false,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['review'] as _i16.ReviewEndpoint).getCourseReviews(
            session,
            params['courseId'],
            page: params['page'],
            pageSize: params['pageSize'],
          ),
        ),
        'submitReview': _i1.MethodConnector(
          name: 'submitReview',
          params: {
            'userId': _i1.ParameterDescription(
              name: 'userId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'courseId': _i1.ParameterDescription(
              name: 'courseId',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'rating': _i1.ParameterDescription(
              name: 'rating',
              type: _i1.getType<int>(),
              nullable: false,
            ),
            'comment': _i1.ParameterDescription(
              name: 'comment',
              type: _i1.getType<String?>(),
              nullable: true,
            ),
          },
          call: (
            _i1.Session session,
            Map<String, dynamic> params,
          ) async =>
              (endpoints['review'] as _i16.ReviewEndpoint).submitReview(
            session,
            params['userId'],
            params['courseId'],
            params['rating'],
            params['comment'],
          ),
        ),
      },
    );
  }
}
