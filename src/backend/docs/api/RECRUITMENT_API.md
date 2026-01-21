# GanaPortal Recruitment API Documentation

## Overview

The GanaPortal Recruitment API provides a comprehensive set of endpoints for managing the entire recruitment pipeline, from job posting to onboarding. This document covers all recruitment-related endpoints.

## Base URL

```
Production: https://api.ganakys.com/api/v1
Staging: https://api-staging.ganakys.com/api/v1
```

## Authentication

### Candidate Portal
- Candidates authenticate via `/candidates/auth/login`
- Bearer token required in `Authorization` header
- Tokens expire after 24 hours

### Recruiter Portal
- Standard GanaPortal authentication
- Role-based access control (recruiter, hiring_manager, hr)

---

## Candidate Portal Endpoints

### Authentication

#### Register Candidate
```http
POST /candidates/auth/register
```

**Request Body:**
```json
{
  "email": "john.doe@email.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+91-9876543210"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "john.doe@email.com",
  "first_name": "John",
  "last_name": "Doe",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Login
```http
POST /candidates/auth/login
```

**Rate Limit:** 5 requests per 5 minutes

**Request Body:**
```json
{
  "email": "john.doe@email.com",
  "password": "SecurePass123!"
}
```

### Profile Management

#### Get Profile
```http
GET /candidates/profile
Authorization: Bearer {token}
```

#### Update Profile
```http
PATCH /candidates/profile
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "headline": "Senior Software Engineer",
  "current_company": "Tech Corp",
  "current_designation": "Lead Developer",
  "total_experience_years": 5,
  "current_salary": 1500000,
  "expected_salary": 2000000,
  "notice_period_days": 30,
  "skills": ["Python", "FastAPI", "React"]
}
```

### Applications

#### Apply to Job
```http
POST /candidates/applications
Authorization: Bearer {token}
```

**Rate Limit:** 10 applications per hour

**Request Body:**
```json
{
  "job_id": "uuid",
  "cover_letter": "I am excited to apply...",
  "expected_salary": 2000000,
  "answers": {
    "willing_to_relocate": true,
    "expected_joining_date": "2026-03-01"
  }
}
```

#### List My Applications
```http
GET /candidates/applications
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` - Filter by status (submitted, screening, interview, offer, hired, rejected)
- `limit` - Results per page (default: 20)
- `offset` - Pagination offset

#### Get Application Details
```http
GET /candidates/applications/{application_id}
Authorization: Bearer {token}
```

#### Withdraw Application
```http
POST /candidates/applications/{application_id}/withdraw
Authorization: Bearer {token}
```

---

## Public API Endpoints

### Job Listings (No Auth Required)

#### List Published Jobs
```http
GET /public/jobs
```

**Query Parameters:**
- `location` - Filter by location
- `department` - Filter by department
- `experience_min` - Minimum experience (years)
- `experience_max` - Maximum experience (years)
- `salary_min` - Minimum salary
- `salary_max` - Maximum salary
- `skills` - Comma-separated list of skills
- `employment_type` - full_time, part_time, contract
- `remote` - true/false for remote jobs
- `search` - Full-text search query
- `limit` - Results per page (default: 20)
- `offset` - Pagination offset

**Response:**
```json
{
  "jobs": [
    {
      "id": "uuid",
      "title": "Senior Software Engineer",
      "department": "Engineering",
      "location": "Bangalore",
      "employment_type": "full_time",
      "experience_range": "5-10 years",
      "salary_range": "18-25 LPA",
      "skills_required": ["Python", "FastAPI"],
      "posted_at": "2026-01-15T10:00:00Z",
      "slug": "senior-software-engineer-bangalore"
    }
  ],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

#### Get Job Details
```http
GET /public/jobs/{job_id}
```

---

## AI Interview Endpoints

### Schedule AI Interview
```http
POST /ai-interview/schedule
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "application_id": "uuid",
  "scheduled_at": "2026-01-25T14:00:00Z"
}
```

### Get Interview Session
```http
GET /ai-interview/session/{session_token}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "scheduled",
  "scheduled_at": "2026-01-25T14:00:00Z",
  "room_url": "https://daily.co/rooms/interview-abc123",
  "questions_count": 5,
  "time_limit_minutes": 30,
  "instructions": "..."
}
```

### Start Interview
```http
POST /ai-interview/session/{session_token}/start
```

### Get Next Question
```http
GET /ai-interview/session/{session_token}/next-question
```

**Response:**
```json
{
  "question_id": 1,
  "question_text": "Tell me about yourself and your experience.",
  "question_type": "introduction",
  "max_duration_seconds": 180,
  "is_last": false
}
```

### Submit Answer
```http
POST /ai-interview/session/{session_token}/submit-answer
```

**Request Body:**
```json
{
  "question_id": 1,
  "audio_url": "https://storage.example.com/audio/answer.webm",
  "duration_seconds": 120
}
```

### Complete Interview
```http
POST /ai-interview/session/{session_token}/complete
```

### Get Results (Candidate View)
```http
GET /ai-interview/session/{session_token}/results
```

**Response:**
```json
{
  "completed_at": "2026-01-25T14:45:00Z",
  "status": "completed",
  "next_steps": "Your responses are being reviewed. We will contact you within 3-5 business days."
}
```

---

## Recruiter Endpoints

### Recruitment Dashboard

#### Get Dashboard Stats
```http
GET /recruitment/dashboard/stats
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_applications": 1250,
  "new_this_week": 85,
  "interviews_scheduled": 42,
  "offers_pending": 8,
  "positions_open": 15,
  "average_time_to_hire": 28
}
```

#### Get Job Pipeline
```http
GET /recruitment/dashboard/jobs/{job_id}/pipeline
Authorization: Bearer {token}
```

**Response:**
```json
{
  "job_id": "uuid",
  "job_title": "Senior Software Engineer",
  "pipeline": {
    "new": 45,
    "screening": 20,
    "ai_interview": 15,
    "human_interview": 8,
    "offer": 3,
    "hired": 1,
    "rejected": 18
  }
}
```

### Candidate Ranklist

#### Get Ranked Candidates
```http
GET /recruitment/jobs/{job_id}/ranklist
Authorization: Bearer {token}
```

**Query Parameters:**
- `tier` - Filter by tier (top, middle, bottom)
- `stage` - Filter by stage
- `limit` - Results per page
- `offset` - Pagination offset

**Response:**
```json
{
  "job_id": "uuid",
  "job_title": "Senior Software Engineer",
  "total_candidates": 45,
  "last_updated": "2026-01-20T15:30:00Z",
  "candidates": [
    {
      "rank": 1,
      "application_id": "uuid",
      "candidate_name": "John Doe",
      "composite_score": 8.7,
      "tier": "top",
      "component_scores": {
        "ai_interview": 9.0,
        "resume_match": 8.5,
        "experience_fit": 8.5,
        "skills_match": 9.0,
        "salary_fit": 7.5
      },
      "stage": "human_interview",
      "ai_recommendation": "proceed"
    }
  ]
}
```

#### Refresh Ranklist
```http
POST /recruitment/jobs/{job_id}/ranklist/refresh
Authorization: Bearer {token}
```

#### Export Ranklist
```http
GET /recruitment/jobs/{job_id}/ranklist/export
Authorization: Bearer {token}
```

**Query Parameters:**
- `format` - csv or xlsx

### Recruiter Actions

#### Advance Candidate
```http
POST /recruitment/applications/{application_id}/advance
Authorization: Bearer {token}
```

#### Reject Candidate
```http
POST /recruitment/applications/{application_id}/reject
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "reason": "Not a good fit for the role",
  "send_notification": true
}
```

#### Put on Hold
```http
POST /recruitment/applications/{application_id}/hold
Authorization: Bearer {token}
```

---

## Human Interview Endpoints

### Interview Slot Management

#### Create Slot
```http
POST /recruitment/interviews/slots
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "job_id": "uuid",
  "slot_date": "2026-01-28",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "interviewer_id": "uuid",
  "interview_type": "technical",
  "location": "Conference Room A",
  "video_link": "https://meet.google.com/abc-defg-hij"
}
```

#### Create Bulk Slots
```http
POST /recruitment/interviews/slots/bulk
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "job_id": "uuid",
  "start_date": "2026-02-01",
  "end_date": "2026-02-07",
  "daily_start_time": "09:00:00",
  "daily_end_time": "17:00:00",
  "slot_duration_minutes": 60,
  "break_between_slots": 15,
  "exclude_weekends": true,
  "interview_type": "screening"
}
```

#### List Available Slots
```http
GET /recruitment/interviews/slots
Authorization: Bearer {token}
```

**Query Parameters:**
- `job_id` - Filter by job
- `interviewer_id` - Filter by interviewer
- `start_date` - Filter by start date
- `end_date` - Filter by end date
- `available_only` - Show only available slots (default: true)

### Interview Scheduling

#### Schedule Interview
```http
POST /recruitment/interviews/schedule
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "application_id": "uuid",
  "slot_id": "uuid",
  "send_invite": true,
  "additional_interviewers": ["interviewer@company.com"],
  "custom_message": "Looking forward to meeting you!"
}
```

#### List Scheduled Interviews
```http
GET /recruitment/interviews/scheduled
Authorization: Bearer {token}
```

#### Cancel Interview
```http
POST /recruitment/interviews/scheduled/{interview_id}/cancel
Authorization: Bearer {token}
```

**Query Parameters:**
- `reason` - Cancellation reason

### Interview Feedback

#### Submit Feedback
```http
POST /recruitment/interviews/scheduled/{interview_id}/feedback
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "overall_rating": 4,
  "technical_rating": 4,
  "communication_rating": 5,
  "cultural_fit_rating": 4,
  "strengths": ["Strong coding skills", "Excellent communication"],
  "weaknesses": ["Limited microservices experience"],
  "recommendation": "hire",
  "detailed_notes": "Candidate demonstrated strong technical skills..."
}
```

**Recommendation Values:** `strong_hire`, `hire`, `no_hire`, `strong_no_hire`

#### Get Interview Feedback
```http
GET /recruitment/interviews/scheduled/{interview_id}/feedback
Authorization: Bearer {token}
```

---

## Offer Management Endpoints

### Create Offer
```http
POST /recruitment/offers/
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "application_id": "uuid",
  "position_title": "Senior Software Engineer",
  "department_id": "uuid",
  "salary": {
    "base_salary": 2000000,
    "currency": "INR",
    "bonus": 200000,
    "bonus_type": "annual",
    "stock_options": 1000,
    "other_benefits": {
      "health_insurance": true,
      "meal_allowance": 5000
    }
  },
  "start_date": "2026-03-01",
  "offer_expiry_date": "2026-02-15",
  "employment_type": "full_time",
  "location": "Bangalore",
  "remote_policy": "hybrid",
  "probation_period_months": 3,
  "requires_approval": true,
  "approvers": ["uuid1", "uuid2"]
}
```

### List Offers
```http
GET /recruitment/offers/
Authorization: Bearer {token}
```

**Query Parameters:**
- `status` - draft, pending_approval, approved, sent, accepted, rejected, hired
- `job_id` - Filter by job
- `pending_approval` - Show only pending approval

### Approval Workflow

#### Submit for Approval
```http
POST /recruitment/offers/{offer_id}/submit-for-approval
Authorization: Bearer {token}
```

#### Approve/Reject Offer
```http
POST /recruitment/offers/{offer_id}/approve
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "decision": "approve",
  "comments": "Compensation is within budget. Approved."
}
```

### Send Offer
```http
POST /recruitment/offers/{offer_id}/send
Authorization: Bearer {token}
```

### Candidate Response

#### Record Response
```http
POST /recruitment/offers/{offer_id}/candidate-response
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "decision": "accept"
}
```

Or for negotiation:
```json
{
  "decision": "negotiate",
  "negotiation_notes": "Would like to discuss base salary",
  "expected_salary": 2300000,
  "preferred_start_date": "2026-03-15"
}
```

### Revise Offer (During Negotiation)
```http
POST /recruitment/offers/{offer_id}/revise
Authorization: Bearer {token}
```

### Complete Hire
```http
POST /recruitment/offers/{offer_id}/complete-hire
Authorization: Bearer {token}
```

**Note:** This triggers the onboarding workflow automatically.

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description",
  "error_code": "ERROR_CODE",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Login | 5 | 5 minutes |
| Registration | 3 | 1 hour |
| Job Applications | 10 | 1 hour |
| Interview Start | 3 | 1 hour |
| Job Search | 100 | 1 minute |
| General API | 100 | 1 minute |

When rate limited, response includes `Retry-After` header.

---

## Webhooks

GanaPortal can send webhooks for recruitment events. Configure webhook URLs in Settings.

### Supported Events
- `application.submitted`
- `application.stage_changed`
- `interview.scheduled`
- `interview.completed`
- `offer.sent`
- `offer.accepted`
- `offer.rejected`
- `candidate.hired`

### Webhook Payload
```json
{
  "event": "offer.accepted",
  "timestamp": "2026-01-20T15:30:00Z",
  "data": {
    "offer_id": "uuid",
    "candidate_id": "uuid",
    "job_id": "uuid",
    "position_title": "Senior Software Engineer"
  }
}
```

---

## Changelog

### v1.0.0 (2026-01-21)
- Initial release of AI-Powered Recruitment System
- Candidate portal with authentication
- AI Interview with Daily.co integration
- Smart Ranklist with weighted scoring
- Full offer management workflow
- Onboarding integration
