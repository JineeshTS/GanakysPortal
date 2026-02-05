/* AUTOMATICALLY GENERATED CODE DO NOT MODIFY */
/*   To generate run: "serverpod generate"    */

// ignore_for_file: implementation_imports
// ignore_for_file: library_private_types_in_public_api
// ignore_for_file: non_constant_identifier_names
// ignore_for_file: public_member_api_docs
// ignore_for_file: type_literal_in_constant_pattern
// ignore_for_file: use_super_parameters

// ignore_for_file: no_leading_underscores_for_library_prefixes
import 'package:serverpod_client/serverpod_client.dart' as _i1;
import 'discussion_reply.dart' as _i2;
import 'announcement.dart' as _i3;
import 'audit_log.dart' as _i4;
import 'auth_provider.dart' as _i5;
import 'bookmark.dart' as _i6;
import 'category.dart' as _i7;
import 'certificate.dart' as _i8;
import 'coupon.dart' as _i9;
import 'course.dart' as _i10;
import 'course_section.dart' as _i11;
import 'course_version.dart' as _i12;
import 'discussion.dart' as _i13;
import 'analytics_event.dart' as _i14;
import 'email_template.dart' as _i15;
import 'enrollment.dart' as _i16;
import 'generation_job.dart' as _i17;
import 'generation_stage_log.dart' as _i18;
import 'learning_path.dart' as _i19;
import 'lecture.dart' as _i20;
import 'lecture_progress.dart' as _i21;
import 'login_attempt.dart' as _i22;
import 'notification.dart' as _i23;
import 'wishlist.dart' as _i24;
import 'payment.dart' as _i25;
import 'quiz.dart' as _i26;
import 'quiz_attempt.dart' as _i27;
import 'quiz_question.dart' as _i28;
import 'review.dart' as _i29;
import 'site_setting.dart' as _i30;
import 'student_note.dart' as _i31;
import 'subscription.dart' as _i32;
import 'subscription_plan.dart' as _i33;
import 'user.dart' as _i34;
import 'user_session.dart' as _i35;
import 'page.dart' as _i36;
import 'package:ganakys_client/src/protocol/bookmark.dart' as _i37;
import 'package:ganakys_client/src/protocol/certificate.dart' as _i38;
import 'package:ganakys_client/src/protocol/category.dart' as _i39;
import 'package:ganakys_client/src/protocol/course.dart' as _i40;
import 'package:ganakys_client/src/protocol/discussion_reply.dart' as _i41;
import 'package:ganakys_client/src/protocol/student_note.dart' as _i42;
import 'package:ganakys_client/src/protocol/page.dart' as _i43;
import 'package:ganakys_client/src/protocol/announcement.dart' as _i44;
import 'package:ganakys_client/src/protocol/subscription_plan.dart' as _i45;
import 'package:ganakys_client/src/protocol/payment.dart' as _i46;
import 'package:ganakys_client/src/protocol/notification.dart' as _i47;
import 'package:ganakys_client/src/protocol/quiz_attempt.dart' as _i48;
export 'analytics_event.dart';
export 'announcement.dart';
export 'audit_log.dart';
export 'auth_provider.dart';
export 'bookmark.dart';
export 'category.dart';
export 'certificate.dart';
export 'coupon.dart';
export 'course.dart';
export 'course_section.dart';
export 'course_version.dart';
export 'discussion.dart';
export 'discussion_reply.dart';
export 'email_template.dart';
export 'enrollment.dart';
export 'generation_job.dart';
export 'generation_stage_log.dart';
export 'learning_path.dart';
export 'lecture.dart';
export 'lecture_progress.dart';
export 'login_attempt.dart';
export 'notification.dart';
export 'page.dart';
export 'payment.dart';
export 'quiz.dart';
export 'quiz_attempt.dart';
export 'quiz_question.dart';
export 'review.dart';
export 'site_setting.dart';
export 'student_note.dart';
export 'subscription.dart';
export 'subscription_plan.dart';
export 'user.dart';
export 'user_session.dart';
export 'wishlist.dart';
export 'client.dart';

class Protocol extends _i1.SerializationManager {
  Protocol._();

  factory Protocol() => _instance;

  static final Protocol _instance = Protocol._();

  @override
  T deserialize<T>(
    dynamic data, [
    Type? t,
  ]) {
    t ??= T;
    if (t == _i2.DiscussionReply) {
      return _i2.DiscussionReply.fromJson(data) as T;
    }
    if (t == _i3.Announcement) {
      return _i3.Announcement.fromJson(data) as T;
    }
    if (t == _i4.AuditLog) {
      return _i4.AuditLog.fromJson(data) as T;
    }
    if (t == _i5.AuthProvider) {
      return _i5.AuthProvider.fromJson(data) as T;
    }
    if (t == _i6.Bookmark) {
      return _i6.Bookmark.fromJson(data) as T;
    }
    if (t == _i7.Category) {
      return _i7.Category.fromJson(data) as T;
    }
    if (t == _i8.Certificate) {
      return _i8.Certificate.fromJson(data) as T;
    }
    if (t == _i9.Coupon) {
      return _i9.Coupon.fromJson(data) as T;
    }
    if (t == _i10.Course) {
      return _i10.Course.fromJson(data) as T;
    }
    if (t == _i11.CourseSection) {
      return _i11.CourseSection.fromJson(data) as T;
    }
    if (t == _i12.CourseVersion) {
      return _i12.CourseVersion.fromJson(data) as T;
    }
    if (t == _i13.Discussion) {
      return _i13.Discussion.fromJson(data) as T;
    }
    if (t == _i14.AnalyticsEvent) {
      return _i14.AnalyticsEvent.fromJson(data) as T;
    }
    if (t == _i15.EmailTemplate) {
      return _i15.EmailTemplate.fromJson(data) as T;
    }
    if (t == _i16.Enrollment) {
      return _i16.Enrollment.fromJson(data) as T;
    }
    if (t == _i17.GenerationJob) {
      return _i17.GenerationJob.fromJson(data) as T;
    }
    if (t == _i18.GenerationStageLog) {
      return _i18.GenerationStageLog.fromJson(data) as T;
    }
    if (t == _i19.LearningPath) {
      return _i19.LearningPath.fromJson(data) as T;
    }
    if (t == _i20.Lecture) {
      return _i20.Lecture.fromJson(data) as T;
    }
    if (t == _i21.LectureProgress) {
      return _i21.LectureProgress.fromJson(data) as T;
    }
    if (t == _i22.LoginAttempt) {
      return _i22.LoginAttempt.fromJson(data) as T;
    }
    if (t == _i23.Notification) {
      return _i23.Notification.fromJson(data) as T;
    }
    if (t == _i24.Wishlist) {
      return _i24.Wishlist.fromJson(data) as T;
    }
    if (t == _i25.Payment) {
      return _i25.Payment.fromJson(data) as T;
    }
    if (t == _i26.Quiz) {
      return _i26.Quiz.fromJson(data) as T;
    }
    if (t == _i27.QuizAttempt) {
      return _i27.QuizAttempt.fromJson(data) as T;
    }
    if (t == _i28.QuizQuestion) {
      return _i28.QuizQuestion.fromJson(data) as T;
    }
    if (t == _i29.Review) {
      return _i29.Review.fromJson(data) as T;
    }
    if (t == _i30.SiteSetting) {
      return _i30.SiteSetting.fromJson(data) as T;
    }
    if (t == _i31.StudentNote) {
      return _i31.StudentNote.fromJson(data) as T;
    }
    if (t == _i32.Subscription) {
      return _i32.Subscription.fromJson(data) as T;
    }
    if (t == _i33.SubscriptionPlan) {
      return _i33.SubscriptionPlan.fromJson(data) as T;
    }
    if (t == _i34.User) {
      return _i34.User.fromJson(data) as T;
    }
    if (t == _i35.UserSession) {
      return _i35.UserSession.fromJson(data) as T;
    }
    if (t == _i36.ContentPage) {
      return _i36.ContentPage.fromJson(data) as T;
    }
    if (t == _i1.getType<_i2.DiscussionReply?>()) {
      return (data != null ? _i2.DiscussionReply.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i3.Announcement?>()) {
      return (data != null ? _i3.Announcement.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i4.AuditLog?>()) {
      return (data != null ? _i4.AuditLog.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i5.AuthProvider?>()) {
      return (data != null ? _i5.AuthProvider.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i6.Bookmark?>()) {
      return (data != null ? _i6.Bookmark.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i7.Category?>()) {
      return (data != null ? _i7.Category.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i8.Certificate?>()) {
      return (data != null ? _i8.Certificate.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i9.Coupon?>()) {
      return (data != null ? _i9.Coupon.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i10.Course?>()) {
      return (data != null ? _i10.Course.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i11.CourseSection?>()) {
      return (data != null ? _i11.CourseSection.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i12.CourseVersion?>()) {
      return (data != null ? _i12.CourseVersion.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i13.Discussion?>()) {
      return (data != null ? _i13.Discussion.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i14.AnalyticsEvent?>()) {
      return (data != null ? _i14.AnalyticsEvent.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i15.EmailTemplate?>()) {
      return (data != null ? _i15.EmailTemplate.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i16.Enrollment?>()) {
      return (data != null ? _i16.Enrollment.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i17.GenerationJob?>()) {
      return (data != null ? _i17.GenerationJob.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i18.GenerationStageLog?>()) {
      return (data != null ? _i18.GenerationStageLog.fromJson(data) : null)
          as T;
    }
    if (t == _i1.getType<_i19.LearningPath?>()) {
      return (data != null ? _i19.LearningPath.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i20.Lecture?>()) {
      return (data != null ? _i20.Lecture.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i21.LectureProgress?>()) {
      return (data != null ? _i21.LectureProgress.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i22.LoginAttempt?>()) {
      return (data != null ? _i22.LoginAttempt.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i23.Notification?>()) {
      return (data != null ? _i23.Notification.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i24.Wishlist?>()) {
      return (data != null ? _i24.Wishlist.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i25.Payment?>()) {
      return (data != null ? _i25.Payment.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i26.Quiz?>()) {
      return (data != null ? _i26.Quiz.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i27.QuizAttempt?>()) {
      return (data != null ? _i27.QuizAttempt.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i28.QuizQuestion?>()) {
      return (data != null ? _i28.QuizQuestion.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i29.Review?>()) {
      return (data != null ? _i29.Review.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i30.SiteSetting?>()) {
      return (data != null ? _i30.SiteSetting.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i31.StudentNote?>()) {
      return (data != null ? _i31.StudentNote.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i32.Subscription?>()) {
      return (data != null ? _i32.Subscription.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i33.SubscriptionPlan?>()) {
      return (data != null ? _i33.SubscriptionPlan.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i34.User?>()) {
      return (data != null ? _i34.User.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i35.UserSession?>()) {
      return (data != null ? _i35.UserSession.fromJson(data) : null) as T;
    }
    if (t == _i1.getType<_i36.ContentPage?>()) {
      return (data != null ? _i36.ContentPage.fromJson(data) : null) as T;
    }
    if (t == Map<String, dynamic>) {
      return (data as Map).map((k, v) =>
          MapEntry(deserialize<String>(k), deserialize<dynamic>(v))) as T;
    }
    if (t == _i1.getType<Map<String, dynamic>?>()) {
      return (data != null
          ? (data as Map).map((k, v) =>
              MapEntry(deserialize<String>(k), deserialize<dynamic>(v)))
          : null) as T;
    }
    if (t == List<Map<String, dynamic>>) {
      return (data as List)
          .map((e) => deserialize<Map<String, dynamic>>(e))
          .toList() as T;
    }
    if (t == List<_i37.Bookmark>) {
      return (data as List).map((e) => deserialize<_i37.Bookmark>(e)).toList()
          as T;
    }
    if (t == List<_i38.Certificate>) {
      return (data as List)
          .map((e) => deserialize<_i38.Certificate>(e))
          .toList() as T;
    }
    if (t == List<_i39.Category>) {
      return (data as List).map((e) => deserialize<_i39.Category>(e)).toList()
          as T;
    }
    if (t == List<_i40.Course>) {
      return (data as List).map((e) => deserialize<_i40.Course>(e)).toList()
          as T;
    }
    if (t == List<_i41.DiscussionReply>) {
      return (data as List)
          .map((e) => deserialize<_i41.DiscussionReply>(e))
          .toList() as T;
    }
    if (t == List<_i42.StudentNote>) {
      return (data as List)
          .map((e) => deserialize<_i42.StudentNote>(e))
          .toList() as T;
    }
    if (t == List<_i43.ContentPage>) {
      return (data as List)
          .map((e) => deserialize<_i43.ContentPage>(e))
          .toList() as T;
    }
    if (t == List<_i44.Announcement>) {
      return (data as List)
          .map((e) => deserialize<_i44.Announcement>(e))
          .toList() as T;
    }
    if (t == Map<String, String>) {
      return (data as Map).map((k, v) =>
          MapEntry(deserialize<String>(k), deserialize<String>(v))) as T;
    }
    if (t == List<_i45.SubscriptionPlan>) {
      return (data as List)
          .map((e) => deserialize<_i45.SubscriptionPlan>(e))
          .toList() as T;
    }
    if (t == List<_i46.Payment>) {
      return (data as List).map((e) => deserialize<_i46.Payment>(e)).toList()
          as T;
    }
    if (t == List<_i47.Notification>) {
      return (data as List)
          .map((e) => deserialize<_i47.Notification>(e))
          .toList() as T;
    }
    if (t == List<_i48.QuizAttempt>) {
      return (data as List)
          .map((e) => deserialize<_i48.QuizAttempt>(e))
          .toList() as T;
    }
    return super.deserialize<T>(data, t);
  }

  @override
  String? getClassNameForObject(Object? data) {
    String? className = super.getClassNameForObject(data);
    if (className != null) return className;
    if (data is _i2.DiscussionReply) {
      return 'DiscussionReply';
    }
    if (data is _i3.Announcement) {
      return 'Announcement';
    }
    if (data is _i4.AuditLog) {
      return 'AuditLog';
    }
    if (data is _i5.AuthProvider) {
      return 'AuthProvider';
    }
    if (data is _i6.Bookmark) {
      return 'Bookmark';
    }
    if (data is _i7.Category) {
      return 'Category';
    }
    if (data is _i8.Certificate) {
      return 'Certificate';
    }
    if (data is _i9.Coupon) {
      return 'Coupon';
    }
    if (data is _i10.Course) {
      return 'Course';
    }
    if (data is _i11.CourseSection) {
      return 'CourseSection';
    }
    if (data is _i12.CourseVersion) {
      return 'CourseVersion';
    }
    if (data is _i13.Discussion) {
      return 'Discussion';
    }
    if (data is _i14.AnalyticsEvent) {
      return 'AnalyticsEvent';
    }
    if (data is _i15.EmailTemplate) {
      return 'EmailTemplate';
    }
    if (data is _i16.Enrollment) {
      return 'Enrollment';
    }
    if (data is _i17.GenerationJob) {
      return 'GenerationJob';
    }
    if (data is _i18.GenerationStageLog) {
      return 'GenerationStageLog';
    }
    if (data is _i19.LearningPath) {
      return 'LearningPath';
    }
    if (data is _i20.Lecture) {
      return 'Lecture';
    }
    if (data is _i21.LectureProgress) {
      return 'LectureProgress';
    }
    if (data is _i22.LoginAttempt) {
      return 'LoginAttempt';
    }
    if (data is _i23.Notification) {
      return 'Notification';
    }
    if (data is _i24.Wishlist) {
      return 'Wishlist';
    }
    if (data is _i25.Payment) {
      return 'Payment';
    }
    if (data is _i26.Quiz) {
      return 'Quiz';
    }
    if (data is _i27.QuizAttempt) {
      return 'QuizAttempt';
    }
    if (data is _i28.QuizQuestion) {
      return 'QuizQuestion';
    }
    if (data is _i29.Review) {
      return 'Review';
    }
    if (data is _i30.SiteSetting) {
      return 'SiteSetting';
    }
    if (data is _i31.StudentNote) {
      return 'StudentNote';
    }
    if (data is _i32.Subscription) {
      return 'Subscription';
    }
    if (data is _i33.SubscriptionPlan) {
      return 'SubscriptionPlan';
    }
    if (data is _i34.User) {
      return 'User';
    }
    if (data is _i35.UserSession) {
      return 'UserSession';
    }
    if (data is _i36.ContentPage) {
      return 'ContentPage';
    }
    return null;
  }

  @override
  dynamic deserializeByClassName(Map<String, dynamic> data) {
    var dataClassName = data['className'];
    if (dataClassName is! String) {
      return super.deserializeByClassName(data);
    }
    if (dataClassName == 'DiscussionReply') {
      return deserialize<_i2.DiscussionReply>(data['data']);
    }
    if (dataClassName == 'Announcement') {
      return deserialize<_i3.Announcement>(data['data']);
    }
    if (dataClassName == 'AuditLog') {
      return deserialize<_i4.AuditLog>(data['data']);
    }
    if (dataClassName == 'AuthProvider') {
      return deserialize<_i5.AuthProvider>(data['data']);
    }
    if (dataClassName == 'Bookmark') {
      return deserialize<_i6.Bookmark>(data['data']);
    }
    if (dataClassName == 'Category') {
      return deserialize<_i7.Category>(data['data']);
    }
    if (dataClassName == 'Certificate') {
      return deserialize<_i8.Certificate>(data['data']);
    }
    if (dataClassName == 'Coupon') {
      return deserialize<_i9.Coupon>(data['data']);
    }
    if (dataClassName == 'Course') {
      return deserialize<_i10.Course>(data['data']);
    }
    if (dataClassName == 'CourseSection') {
      return deserialize<_i11.CourseSection>(data['data']);
    }
    if (dataClassName == 'CourseVersion') {
      return deserialize<_i12.CourseVersion>(data['data']);
    }
    if (dataClassName == 'Discussion') {
      return deserialize<_i13.Discussion>(data['data']);
    }
    if (dataClassName == 'AnalyticsEvent') {
      return deserialize<_i14.AnalyticsEvent>(data['data']);
    }
    if (dataClassName == 'EmailTemplate') {
      return deserialize<_i15.EmailTemplate>(data['data']);
    }
    if (dataClassName == 'Enrollment') {
      return deserialize<_i16.Enrollment>(data['data']);
    }
    if (dataClassName == 'GenerationJob') {
      return deserialize<_i17.GenerationJob>(data['data']);
    }
    if (dataClassName == 'GenerationStageLog') {
      return deserialize<_i18.GenerationStageLog>(data['data']);
    }
    if (dataClassName == 'LearningPath') {
      return deserialize<_i19.LearningPath>(data['data']);
    }
    if (dataClassName == 'Lecture') {
      return deserialize<_i20.Lecture>(data['data']);
    }
    if (dataClassName == 'LectureProgress') {
      return deserialize<_i21.LectureProgress>(data['data']);
    }
    if (dataClassName == 'LoginAttempt') {
      return deserialize<_i22.LoginAttempt>(data['data']);
    }
    if (dataClassName == 'Notification') {
      return deserialize<_i23.Notification>(data['data']);
    }
    if (dataClassName == 'Wishlist') {
      return deserialize<_i24.Wishlist>(data['data']);
    }
    if (dataClassName == 'Payment') {
      return deserialize<_i25.Payment>(data['data']);
    }
    if (dataClassName == 'Quiz') {
      return deserialize<_i26.Quiz>(data['data']);
    }
    if (dataClassName == 'QuizAttempt') {
      return deserialize<_i27.QuizAttempt>(data['data']);
    }
    if (dataClassName == 'QuizQuestion') {
      return deserialize<_i28.QuizQuestion>(data['data']);
    }
    if (dataClassName == 'Review') {
      return deserialize<_i29.Review>(data['data']);
    }
    if (dataClassName == 'SiteSetting') {
      return deserialize<_i30.SiteSetting>(data['data']);
    }
    if (dataClassName == 'StudentNote') {
      return deserialize<_i31.StudentNote>(data['data']);
    }
    if (dataClassName == 'Subscription') {
      return deserialize<_i32.Subscription>(data['data']);
    }
    if (dataClassName == 'SubscriptionPlan') {
      return deserialize<_i33.SubscriptionPlan>(data['data']);
    }
    if (dataClassName == 'User') {
      return deserialize<_i34.User>(data['data']);
    }
    if (dataClassName == 'UserSession') {
      return deserialize<_i35.UserSession>(data['data']);
    }
    if (dataClassName == 'ContentPage') {
      return deserialize<_i36.ContentPage>(data['data']);
    }
    return super.deserializeByClassName(data);
  }
}
