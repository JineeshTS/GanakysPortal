BEGIN;

--
-- ACTION CREATE TABLE
--
CREATE TABLE "analytics_events" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint,
    "eventType" text NOT NULL,
    "eventData" text,
    "sessionId" text,
    "ipAddress" text,
    "userAgent" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "event_type_idx" ON "analytics_events" USING btree ("eventType");
CREATE INDEX "event_user_idx" ON "analytics_events" USING btree ("userId");
CREATE INDEX "event_date_idx" ON "analytics_events" USING btree ("createdAt");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "announcements" (
    "id" bigserial PRIMARY KEY,
    "title" text NOT NULL,
    "message" text NOT NULL,
    "type" text NOT NULL DEFAULT 'banner'::text,
    "targetAudience" text NOT NULL DEFAULT 'all'::text,
    "targetCourseId" bigint,
    "targetPlanId" bigint,
    "isDismissible" boolean NOT NULL DEFAULT true,
    "startsAt" timestamp without time zone,
    "endsAt" timestamp without time zone,
    "isActive" boolean NOT NULL DEFAULT true,
    "createdBy" bigint,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "announcement_active_idx" ON "announcements" USING btree ("isActive");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "audit_logs" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint,
    "action" text NOT NULL,
    "entityType" text NOT NULL,
    "entityId" text,
    "oldValue" text,
    "newValue" text,
    "ipAddress" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "audit_user_idx" ON "audit_logs" USING btree ("userId");
CREATE INDEX "audit_action_idx" ON "audit_logs" USING btree ("action");
CREATE INDEX "audit_entity_idx" ON "audit_logs" USING btree ("entityType", "entityId");
CREATE INDEX "audit_date_idx" ON "audit_logs" USING btree ("createdAt");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "auth_providers" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "provider" text NOT NULL,
    "providerUid" text NOT NULL,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "auth_provider_uid_idx" ON "auth_providers" USING btree ("provider", "providerUid");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "bookmarks" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "lectureId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "timestampSeconds" bigint NOT NULL DEFAULT 0,
    "label" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "bookmark_user_idx" ON "bookmarks" USING btree ("userId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "categories" (
    "id" bigserial PRIMARY KEY,
    "name" text NOT NULL,
    "slug" text NOT NULL,
    "description" text,
    "icon" text,
    "parentId" bigint,
    "sortOrder" bigint NOT NULL DEFAULT 0,
    "courseCount" bigint NOT NULL DEFAULT 0,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "category_slug_idx" ON "categories" USING btree ("slug");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "certificates" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "certificateNumber" text NOT NULL,
    "pdfUrl" text,
    "isRevoked" boolean NOT NULL DEFAULT false,
    "issuedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "cert_number_idx" ON "certificates" USING btree ("certificateNumber");
CREATE INDEX "cert_user_course_idx" ON "certificates" USING btree ("userId", "courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "coupons" (
    "id" bigserial PRIMARY KEY,
    "code" text NOT NULL,
    "discountType" text NOT NULL DEFAULT 'percentage'::text,
    "discountValue" double precision NOT NULL,
    "maxUses" bigint,
    "usedCount" bigint NOT NULL DEFAULT 0,
    "validFrom" timestamp without time zone,
    "validUntil" timestamp without time zone,
    "isActive" boolean NOT NULL DEFAULT true,
    "applicablePlans" text,
    "applicableCourses" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "coupon_code_idx" ON "coupons" USING btree ("code");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "course_sections" (
    "id" bigserial PRIMARY KEY,
    "courseId" bigint NOT NULL,
    "title" text NOT NULL,
    "description" text,
    "sortOrder" bigint NOT NULL DEFAULT 0
);

-- Indexes
CREATE INDEX "section_course_idx" ON "course_sections" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "course_versions" (
    "id" bigserial PRIMARY KEY,
    "courseId" bigint NOT NULL,
    "versionNumber" bigint NOT NULL,
    "snapshotJson" text NOT NULL,
    "changeSummary" text,
    "createdBy" bigint,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "version_course_idx" ON "course_versions" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "courses" (
    "id" bigserial PRIMARY KEY,
    "title" text NOT NULL,
    "slug" text NOT NULL,
    "description" text,
    "shortDescription" text,
    "categoryId" bigint,
    "difficulty" text NOT NULL DEFAULT 'beginner'::text,
    "durationMinutes" bigint NOT NULL DEFAULT 0,
    "thumbnailUrl" text,
    "promoVideoUrl" text,
    "isPublished" boolean NOT NULL DEFAULT false,
    "isFeatured" boolean NOT NULL DEFAULT false,
    "price" double precision NOT NULL DEFAULT 0,
    "totalLectures" bigint NOT NULL DEFAULT 0,
    "totalSections" bigint NOT NULL DEFAULT 0,
    "generationStatus" text,
    "generationJobId" bigint,
    "qualityScore" double precision,
    "instructorId" bigint,
    "language" text NOT NULL DEFAULT 'en'::text,
    "avgRating" double precision NOT NULL DEFAULT 0,
    "reviewCount" bigint NOT NULL DEFAULT 0,
    "enrollmentCount" bigint NOT NULL DEFAULT 0,
    "metaTitle" text,
    "metaDescription" text,
    "ogImageUrl" text,
    "version" bigint NOT NULL DEFAULT 1,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "course_slug_idx" ON "courses" USING btree ("slug");
CREATE INDEX "course_category_idx" ON "courses" USING btree ("categoryId");
CREATE INDEX "course_published_idx" ON "courses" USING btree ("isPublished");
CREATE INDEX "course_instructor_idx" ON "courses" USING btree ("instructorId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "discussion_replies" (
    "id" bigserial PRIMARY KEY,
    "discussionId" bigint NOT NULL,
    "userId" bigint NOT NULL,
    "content" text NOT NULL,
    "isInstructorReply" boolean NOT NULL DEFAULT false,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "reply_discussion_idx" ON "discussion_replies" USING btree ("discussionId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "discussions" (
    "id" bigserial PRIMARY KEY,
    "courseId" bigint NOT NULL,
    "lectureId" bigint,
    "userId" bigint NOT NULL,
    "title" text NOT NULL,
    "content" text NOT NULL,
    "isPinned" boolean NOT NULL DEFAULT false,
    "isResolved" boolean NOT NULL DEFAULT false,
    "replyCount" bigint NOT NULL DEFAULT 0,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "discussion_course_idx" ON "discussions" USING btree ("courseId");
CREATE INDEX "discussion_user_idx" ON "discussions" USING btree ("userId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "email_templates" (
    "id" bigserial PRIMARY KEY,
    "slug" text NOT NULL,
    "subject" text NOT NULL,
    "bodyHtml" text NOT NULL,
    "bodyText" text,
    "variables" text
);

-- Indexes
CREATE UNIQUE INDEX "template_slug_idx" ON "email_templates" USING btree ("slug");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "enrollments" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "progressPercent" double precision NOT NULL DEFAULT 0,
    "status" text NOT NULL DEFAULT 'enrolled'::text,
    "enrolledAt" timestamp without time zone NOT NULL,
    "completedAt" timestamp without time zone
);

-- Indexes
CREATE UNIQUE INDEX "enrollment_user_course_idx" ON "enrollments" USING btree ("userId", "courseId");
CREATE INDEX "enrollment_user_idx" ON "enrollments" USING btree ("userId");
CREATE INDEX "enrollment_course_idx" ON "enrollments" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "generation_jobs" (
    "id" bigserial PRIMARY KEY,
    "courseId" bigint,
    "topic" text NOT NULL,
    "status" text NOT NULL DEFAULT 'queued'::text,
    "currentStage" text,
    "progressPercent" bigint NOT NULL DEFAULT 0,
    "contentJson" text,
    "qualityScore" double precision,
    "qualityReport" text,
    "errorMessage" text,
    "pipelineLog" text,
    "outputDir" text,
    "config" text,
    "startedAt" timestamp without time zone,
    "completedAt" timestamp without time zone,
    "createdBy" bigint,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "job_status_idx" ON "generation_jobs" USING btree ("status");
CREATE INDEX "job_course_idx" ON "generation_jobs" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "generation_stage_logs" (
    "id" bigserial PRIMARY KEY,
    "jobId" bigint NOT NULL,
    "stage" text NOT NULL,
    "status" text NOT NULL DEFAULT 'pending'::text,
    "message" text,
    "startedAt" timestamp without time zone,
    "completedAt" timestamp without time zone,
    "durationMs" bigint
);

-- Indexes
CREATE INDEX "stage_job_idx" ON "generation_stage_logs" USING btree ("jobId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "learning_paths" (
    "id" bigserial PRIMARY KEY,
    "title" text NOT NULL,
    "slug" text NOT NULL,
    "description" text,
    "thumbnailUrl" text,
    "difficulty" text NOT NULL DEFAULT 'beginner'::text,
    "courseIds" text NOT NULL,
    "isPublished" boolean NOT NULL DEFAULT false,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "path_slug_idx" ON "learning_paths" USING btree ("slug");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "lecture_progress" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "lectureId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "isCompleted" boolean NOT NULL DEFAULT false,
    "watchTimeSeconds" bigint NOT NULL DEFAULT 0,
    "lastPositionSeconds" bigint NOT NULL DEFAULT 0,
    "completedAt" timestamp without time zone
);

-- Indexes
CREATE UNIQUE INDEX "progress_user_lecture_idx" ON "lecture_progress" USING btree ("userId", "lectureId");
CREATE INDEX "progress_user_course_idx" ON "lecture_progress" USING btree ("userId", "courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "lectures" (
    "id" bigserial PRIMARY KEY,
    "sectionId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "title" text NOT NULL,
    "type" text NOT NULL DEFAULT 'video'::text,
    "durationMinutes" bigint NOT NULL DEFAULT 0,
    "videoUrl" text,
    "audioUrl" text,
    "content" text,
    "scriptJson" text,
    "slidesJson" text,
    "sortOrder" bigint NOT NULL DEFAULT 0,
    "isFreePreview" boolean NOT NULL DEFAULT false,
    "version" bigint NOT NULL DEFAULT 1
);

-- Indexes
CREATE INDEX "lecture_section_idx" ON "lectures" USING btree ("sectionId");
CREATE INDEX "lecture_course_idx" ON "lectures" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "login_attempts" (
    "id" bigserial PRIMARY KEY,
    "email" text NOT NULL,
    "ipAddress" text NOT NULL,
    "success" boolean NOT NULL,
    "failureReason" text,
    "userAgent" text,
    "countryCode" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "login_email_idx" ON "login_attempts" USING btree ("email");
CREATE INDEX "login_ip_idx" ON "login_attempts" USING btree ("ipAddress");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "notifications" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "title" text NOT NULL,
    "message" text NOT NULL,
    "type" text NOT NULL,
    "isRead" boolean NOT NULL DEFAULT false,
    "data" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "notif_user_idx" ON "notifications" USING btree ("userId");
CREATE INDEX "notif_read_idx" ON "notifications" USING btree ("userId", "isRead");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "pages" (
    "id" bigserial PRIMARY KEY,
    "slug" text NOT NULL,
    "title" text NOT NULL,
    "content" text NOT NULL,
    "isPublished" boolean NOT NULL DEFAULT true,
    "metaTitle" text,
    "metaDescription" text,
    "version" bigint NOT NULL DEFAULT 1,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "page_slug_idx" ON "pages" USING btree ("slug");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "payments" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "planId" bigint,
    "courseId" bigint,
    "amount" double precision NOT NULL,
    "currency" text NOT NULL DEFAULT 'INR'::text,
    "status" text NOT NULL DEFAULT 'pending'::text,
    "paymentGateway" text NOT NULL,
    "gatewayPaymentId" text,
    "gatewayOrderId" text,
    "receiptUrl" text,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "payment_user_idx" ON "payments" USING btree ("userId");
CREATE INDEX "payment_status_idx" ON "payments" USING btree ("status");
CREATE INDEX "payment_gateway_id_idx" ON "payments" USING btree ("gatewayPaymentId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "quiz_attempts" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "quizId" bigint NOT NULL,
    "score" double precision NOT NULL,
    "answers" text NOT NULL,
    "passed" boolean NOT NULL,
    "attemptedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "attempt_user_quiz_idx" ON "quiz_attempts" USING btree ("userId", "quizId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "quiz_questions" (
    "id" bigserial PRIMARY KEY,
    "quizId" bigint NOT NULL,
    "question" text NOT NULL,
    "options" text NOT NULL,
    "explanation" text,
    "sortOrder" bigint NOT NULL DEFAULT 0
);

-- Indexes
CREATE INDEX "question_quiz_idx" ON "quiz_questions" USING btree ("quizId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "quizzes" (
    "id" bigserial PRIMARY KEY,
    "courseId" bigint NOT NULL,
    "lectureId" bigint,
    "title" text NOT NULL,
    "type" text NOT NULL DEFAULT 'section_quiz'::text,
    "passPercentage" bigint NOT NULL DEFAULT 70
);

-- Indexes
CREATE INDEX "quiz_course_idx" ON "quizzes" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "reviews" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "rating" bigint NOT NULL,
    "comment" text,
    "isApproved" boolean NOT NULL DEFAULT true,
    "isFlagged" boolean NOT NULL DEFAULT false,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "review_user_course_idx" ON "reviews" USING btree ("userId", "courseId");
CREATE INDEX "review_course_idx" ON "reviews" USING btree ("courseId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "site_settings" (
    "id" bigserial PRIMARY KEY,
    "key" text NOT NULL,
    "value" text NOT NULL,
    "updatedBy" bigint,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "setting_key_idx" ON "site_settings" USING btree ("key");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "student_notes" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "lectureId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "content" text NOT NULL,
    "timestampSeconds" bigint,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "note_user_lecture_idx" ON "student_notes" USING btree ("userId", "lectureId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "subscription_plans" (
    "id" bigserial PRIMARY KEY,
    "name" text NOT NULL,
    "slug" text NOT NULL,
    "priceMonthly" double precision NOT NULL,
    "priceYearly" double precision NOT NULL,
    "currency" text NOT NULL DEFAULT 'INR'::text,
    "features" text NOT NULL,
    "isActive" boolean NOT NULL DEFAULT true,
    "stripePriceId" text,
    "razorpayPlanId" text,
    "sortOrder" bigint NOT NULL DEFAULT 0,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "plan_slug_idx" ON "subscription_plans" USING btree ("slug");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "subscriptions" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "planId" bigint NOT NULL,
    "status" text NOT NULL DEFAULT 'active'::text,
    "currentPeriodStart" timestamp without time zone NOT NULL,
    "currentPeriodEnd" timestamp without time zone NOT NULL,
    "cancelAtPeriodEnd" boolean NOT NULL DEFAULT false,
    "gatewaySubscriptionId" text,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "sub_user_idx" ON "subscriptions" USING btree ("userId");
CREATE INDEX "sub_gateway_idx" ON "subscriptions" USING btree ("gatewaySubscriptionId");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "user_sessions" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "refreshTokenHash" text NOT NULL,
    "deviceInfo" text,
    "ipAddress" text,
    "userAgentFingerprint" text,
    "lastActiveAt" timestamp without time zone NOT NULL,
    "expiresAt" timestamp without time zone NOT NULL,
    "isRevoked" boolean NOT NULL DEFAULT false,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE INDEX "session_user_idx" ON "user_sessions" USING btree ("userId");
CREATE UNIQUE INDEX "session_token_idx" ON "user_sessions" USING btree ("refreshTokenHash");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "users" (
    "id" bigserial PRIMARY KEY,
    "email" text NOT NULL,
    "name" text NOT NULL,
    "avatarUrl" text,
    "role" text NOT NULL DEFAULT 'student'::text,
    "bio" text,
    "subscriptionStatus" text NOT NULL DEFAULT 'free'::text,
    "subscriptionExpiresAt" timestamp without time zone,
    "emailVerified" boolean NOT NULL DEFAULT false,
    "emailVerificationToken" text,
    "passwordHash" text,
    "passwordResetToken" text,
    "passwordResetExpiresAt" timestamp without time zone,
    "locale" text NOT NULL DEFAULT 'en'::text,
    "passwordHistory" text,
    "totpSecret" text,
    "totpEnabled" boolean NOT NULL DEFAULT false,
    "recoveryCodes" text,
    "failedLoginCount" bigint NOT NULL DEFAULT 0,
    "lockedUntil" timestamp without time zone,
    "lastLoginAt" timestamp without time zone,
    "lastLoginIp" text,
    "loginCount" bigint NOT NULL DEFAULT 0,
    "deletionRequestedAt" timestamp without time zone,
    "isActive" boolean NOT NULL DEFAULT true,
    "createdAt" timestamp without time zone NOT NULL,
    "updatedAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "user_email_idx" ON "users" USING btree ("email");
CREATE INDEX "user_role_idx" ON "users" USING btree ("role");

--
-- ACTION CREATE TABLE
--
CREATE TABLE "wishlists" (
    "id" bigserial PRIMARY KEY,
    "userId" bigint NOT NULL,
    "courseId" bigint NOT NULL,
    "createdAt" timestamp without time zone NOT NULL
);

-- Indexes
CREATE UNIQUE INDEX "wishlist_user_course_idx" ON "wishlists" USING btree ("userId", "courseId");

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "auth_providers"
    ADD CONSTRAINT "auth_providers_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "bookmarks"
    ADD CONSTRAINT "bookmarks_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "bookmarks"
    ADD CONSTRAINT "bookmarks_fk_1"
    FOREIGN KEY("lectureId")
    REFERENCES "lectures"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "bookmarks"
    ADD CONSTRAINT "bookmarks_fk_2"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "certificates"
    ADD CONSTRAINT "certificates_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "certificates"
    ADD CONSTRAINT "certificates_fk_1"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "course_sections"
    ADD CONSTRAINT "course_sections_fk_0"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "course_versions"
    ADD CONSTRAINT "course_versions_fk_0"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "discussion_replies"
    ADD CONSTRAINT "discussion_replies_fk_0"
    FOREIGN KEY("discussionId")
    REFERENCES "discussions"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "discussion_replies"
    ADD CONSTRAINT "discussion_replies_fk_1"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "discussions"
    ADD CONSTRAINT "discussions_fk_0"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "discussions"
    ADD CONSTRAINT "discussions_fk_1"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "enrollments"
    ADD CONSTRAINT "enrollments_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "enrollments"
    ADD CONSTRAINT "enrollments_fk_1"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "generation_stage_logs"
    ADD CONSTRAINT "generation_stage_logs_fk_0"
    FOREIGN KEY("jobId")
    REFERENCES "generation_jobs"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "lecture_progress"
    ADD CONSTRAINT "lecture_progress_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "lecture_progress"
    ADD CONSTRAINT "lecture_progress_fk_1"
    FOREIGN KEY("lectureId")
    REFERENCES "lectures"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "lecture_progress"
    ADD CONSTRAINT "lecture_progress_fk_2"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "lectures"
    ADD CONSTRAINT "lectures_fk_0"
    FOREIGN KEY("sectionId")
    REFERENCES "course_sections"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "lectures"
    ADD CONSTRAINT "lectures_fk_1"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "notifications"
    ADD CONSTRAINT "notifications_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "payments"
    ADD CONSTRAINT "payments_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "quiz_attempts"
    ADD CONSTRAINT "quiz_attempts_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "quiz_attempts"
    ADD CONSTRAINT "quiz_attempts_fk_1"
    FOREIGN KEY("quizId")
    REFERENCES "quizzes"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "quiz_questions"
    ADD CONSTRAINT "quiz_questions_fk_0"
    FOREIGN KEY("quizId")
    REFERENCES "quizzes"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "quizzes"
    ADD CONSTRAINT "quizzes_fk_0"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "reviews"
    ADD CONSTRAINT "reviews_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "reviews"
    ADD CONSTRAINT "reviews_fk_1"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "student_notes"
    ADD CONSTRAINT "student_notes_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "student_notes"
    ADD CONSTRAINT "student_notes_fk_1"
    FOREIGN KEY("lectureId")
    REFERENCES "lectures"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "student_notes"
    ADD CONSTRAINT "student_notes_fk_2"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "subscriptions"
    ADD CONSTRAINT "subscriptions_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "subscriptions"
    ADD CONSTRAINT "subscriptions_fk_1"
    FOREIGN KEY("planId")
    REFERENCES "subscription_plans"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "user_sessions"
    ADD CONSTRAINT "user_sessions_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;

--
-- ACTION CREATE FOREIGN KEY
--
ALTER TABLE ONLY "wishlists"
    ADD CONSTRAINT "wishlists_fk_0"
    FOREIGN KEY("userId")
    REFERENCES "users"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;
ALTER TABLE ONLY "wishlists"
    ADD CONSTRAINT "wishlists_fk_1"
    FOREIGN KEY("courseId")
    REFERENCES "courses"("id")
    ON DELETE NO ACTION
    ON UPDATE NO ACTION;


--
-- MIGRATION VERSION FOR ganakys
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('ganakys', '20260205112723211', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20260205112723211', "timestamp" = now();

--
-- MIGRATION VERSION FOR serverpod
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('serverpod', '20240516151843329', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20240516151843329', "timestamp" = now();


COMMIT;
