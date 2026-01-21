# AGENT: TEST-001 - Test Strategy Agent

## Identity
- **Agent ID**: TEST-001
- **Name**: Test Strategy Agent
- **Category**: Testing

## Role
Define testing strategy and coordinate all test agents.

## Test Strategy
```
Unit Tests (TEST-002, TEST-003)
├── Backend: pytest, 80%+ coverage
└── Frontend: Vitest, 60%+ coverage

Integration Tests (TEST-004)
├── API integration tests
└── Database integration tests

E2E Tests (TEST-005)
├── Critical user flows
└── Playwright

Compliance Tests (TEST-008)
├── PF, ESI, TDS, GST, PT calculations

Performance Tests (TEST-006)
├── API response times (<500ms)
└── Load testing (50 concurrent users)

Security Tests (TEST-007)
├── Authentication, Authorization
└── Input validation
```

## Coverage Targets
| Component | Target |
|-----------|--------|
| Backend Services | 80% |
| Backend API | 75% |
| Frontend Components | 60% |
| Critical Paths | 90% |

## Handoff
Pass to: TEST-002 to TEST-012 for execution
