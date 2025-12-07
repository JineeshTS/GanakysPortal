# GanaPortal

AI-Powered ERP System for Ganakys Codilla Apps (OPC) Private Limited

## Overview

GanaPortal is a comprehensive, AI-powered ERP system designed specifically for a small IT services and SaaS company operating in India with international clients. The system combines HRMS, document management, accounting, CRM, and project management into a unified platform.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.11+), SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16, Redis 7 |
| AI | Claude API (claude-3.5-sonnet) |
| Deployment | Docker, Nginx, Let's Encrypt SSL |

## Project Structure

```
GanakysPortal/
├── frontend/          # Next.js 14 application
│   ├── src/
│   │   ├── app/       # App Router pages
│   │   ├── components/# React components
│   │   └── lib/       # Utility functions
│   └── package.json
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API routers
│   │   ├── core/      # Config, security, database
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utilities
│   ├── alembic/       # Database migrations
│   └── requirements.txt
├── docker/            # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── database/          # Database scripts
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/JineeshTS/GanakysPortal.git
   cd GanakysPortal
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   cd docker
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/v1/docs

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Core Modules

| Module | Description |
|--------|-------------|
| **HRMS** | Employee management, onboarding, leave, timesheet |
| **EDMS** | Enterprise document management with folder hierarchy |
| **Payroll** | Full India compliance - PF, ESI, TDS, PT, Form 16 |
| **Statutory** | PF ECR, ESI Return, TDS 24Q file generation |
| **Accounting** | GL, AR, AP, multi-currency, bank reconciliation |
| **GST Compliance** | GSTR-1, GSTR-3B, HSN/SAC management |
| **CRM** | Lead management, pipeline, AI-powered follow-ups |
| **Project Management** | Client & internal projects, billing, resource planning |
| **AI Layer** | Document processing, natural language queries, insights |

## User Roles

- **Admin (Employer)**: Full system access
- **HR**: Employee and HR management
- **Accountant**: Financial operations
- **Employee**: Self-service access
- **External CA**: Verification and compliance (Phase 2)

## API Documentation

When running in development mode, API documentation is available at:
- Swagger UI: `/api/v1/docs`
- ReDoc: `/api/v1/redoc`

## Contributing

This is a private project for Ganakys Codilla Apps (OPC) Private Limited.

## License

Proprietary - All rights reserved.
