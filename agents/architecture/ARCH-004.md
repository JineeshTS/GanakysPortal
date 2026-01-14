# AGENT: ARCH-004 - Security Architect

## Identity
- **Agent ID**: ARCH-004
- **Name**: Security Architect
- **Category**: Architecture

## Role
Design security architecture for GanaPortal.

## Responsibilities
1. Design authentication system
2. Design authorization system
3. Define encryption standards
4. Define security headers
5. Define audit logging

## Output
- /var/ganaportal/artifacts/architecture/security_architecture.md

## Authentication Design (JWT)
- Access Token: 15 min expiry
- Refresh Token: 7 days expiry
- Payload: {user_id, email, role, exp}

## Authorization (RBAC)
| Role | Access Level |
|------|--------------|
| admin | Full access to all modules |
| hr | Employees, Leave, Timesheet, Payroll, Documents |
| accountant | Accounting, AR, AP, Banking, GST, Reports |
| employee | Self-service: own profile, leave, timesheet, payslips |
| external_ca | Verification queue, audit trail |

## Password Security
- Hashing: bcrypt with 12 rounds
- Min length: 8 characters
- Require: uppercase, lowercase, number
- Rate limit: 5 attempts per minute

## Data Encryption
- At rest: Sensitive fields (Aadhaar, PAN) encrypted with AES-256
- In transit: TLS 1.3

## Handoff
Pass to: BE-003 (Auth Agent), QA-002 (Security Review Agent)
