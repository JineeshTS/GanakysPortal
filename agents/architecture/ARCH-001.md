# AGENT: ARCH-001 - System Architect

## Identity
- **Agent ID**: ARCH-001
- **Name**: System Architect
- **Category**: Architecture

## Role
Design overall system architecture for GanaPortal.

## Responsibilities
1. Define system components
2. Define component interactions
3. Create architecture diagrams
4. Document technology decisions

## Output
- /var/ganaportal/artifacts/architecture/system_architecture.md

## System Components
```
┌─────────────────────────────────────────────────────────────────────┐
│                         GANAPORTAL ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐        │
│  │   Browser    │────▶│    Nginx     │────▶│   Next.js    │        │
│  │   Client     │     │  (SSL/Proxy) │     │   Frontend   │        │
│  └──────────────┘     └──────────────┘     └──────────────┘        │
│                              │                     │                 │
│                              │                     │ API Calls       │
│                              ▼                     ▼                 │
│                       ┌──────────────┐     ┌──────────────┐        │
│                       │   FastAPI    │◀───▶│    Redis     │        │
│                       │   Backend    │     │   (Cache)    │        │
│                       └──────────────┘     └──────────────┘        │
│                              │                                       │
│                              │ ORM                                   │
│                              ▼                                       │
│                       ┌──────────────┐                              │
│                       │ PostgreSQL   │                              │
│                       │  Database    │                              │
│                       └──────────────┘                              │
│                              │                                       │
│                              │ AI Queries                           │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    AI SERVICE (Fallback Chain)                 │  │
│  │  Claude API → Gemini API → OpenAI API → Together AI          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Technology Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend Framework | Next.js 14 | App Router, SSR, React ecosystem |
| Backend Framework | FastAPI | Async, type hints, auto docs |
| Database | PostgreSQL 16 | Robust, ACID, JSON support |
| Cache | Redis 7 | Fast, versatile, pub/sub |
| ORM | SQLAlchemy 2.0 | Async support, mature |
| AI Primary | Claude API | Best quality |
| Deployment | Docker | Reproducible, portable |

## Handoff
Pass to: ARCH-002 to ARCH-015 for detailed designs
