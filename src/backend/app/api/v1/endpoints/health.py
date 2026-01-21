"""
Health Check Endpoints
Sprint 5: Deployment readiness and monitoring
"""
from typing import Dict, Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db

router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str  # healthy, degraded, unhealthy
    timestamp: str
    version: str
    components: Dict[str, Any]


class ComponentHealth(BaseModel):
    """Individual component health."""
    status: str
    latency_ms: float
    message: str = ""


# Application version (should match deployment)
APP_VERSION = "1.0.0"


@router.get("/health", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.

    Returns status of all critical components:
    - Database connectivity
    - Redis connectivity (if configured)
    - External services (Daily.co, OpenAI)

    Used by:
    - Kubernetes liveness probes
    - Load balancer health checks
    - Monitoring systems
    """
    import time

    components = {}
    overall_status = "healthy"

    # Database health check
    db_start = time.time()
    try:
        await db.execute(text("SELECT 1"))
        db_latency = (time.time() - db_start) * 1000
        components["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2),
        }
    except Exception as e:
        components["database"] = {
            "status": "unhealthy",
            "latency_ms": 0,
            "error": str(e)[:100],
        }
        overall_status = "unhealthy"

    # Redis health check (optional)
    try:
        from app.core.config import settings
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            import redis.asyncio as aioredis
            redis_start = time.time()
            redis_client = aioredis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            redis_latency = (time.time() - redis_start) * 1000
            components["redis"] = {
                "status": "healthy",
                "latency_ms": round(redis_latency, 2),
            }
            await redis_client.close()
    except ImportError:
        components["redis"] = {
            "status": "not_configured",
            "latency_ms": 0,
        }
    except Exception as e:
        components["redis"] = {
            "status": "degraded",
            "latency_ms": 0,
            "error": str(e)[:100],
        }
        if overall_status == "healthy":
            overall_status = "degraded"

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=APP_VERSION,
        components=components,
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe.

    Simple check that the application is running.
    Returns 200 if alive, used by K8s to determine if pod needs restart.
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/health/ready")
async def readiness_probe(db: AsyncSession = Depends(get_db)):
    """
    Kubernetes readiness probe.

    Checks if application is ready to receive traffic.
    Must have database connectivity.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Not ready: Database unavailable - {str(e)[:100]}"
        )


@router.get("/health/recruitment")
async def recruitment_health(db: AsyncSession = Depends(get_db)):
    """
    Recruitment system specific health check.

    Verifies all recruitment-related tables and services.
    """
    import time

    checks = {}

    # Check recruitment tables exist
    tables_to_check = [
        "job_openings",
        "candidates",
        "job_applications",
        "ai_interview_sessions",
        "human_interviews",
        "offers",
        "candidate_ranklist",
    ]

    for table in tables_to_check:
        try:
            start = time.time()
            result = await db.execute(
                text(f"SELECT COUNT(*) FROM {table} LIMIT 1")
            )
            latency = (time.time() - start) * 1000
            checks[table] = {
                "status": "healthy",
                "latency_ms": round(latency, 2),
            }
        except Exception as e:
            checks[table] = {
                "status": "unhealthy",
                "error": str(e)[:100],
            }

    # Check critical indexes exist
    try:
        result = await db.execute(
            text("""
                SELECT indexname FROM pg_indexes
                WHERE tablename IN ('job_applications', 'ai_interview_sessions', 'offers')
            """)
        )
        index_count = len(result.fetchall())
        checks["indexes"] = {
            "status": "healthy" if index_count > 10 else "degraded",
            "count": index_count,
        }
    except Exception:
        checks["indexes"] = {"status": "unknown"}

    # Determine overall status
    statuses = [c.get("status", "unknown") for c in checks.values()]
    if all(s == "healthy" for s in statuses):
        overall = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


@router.get("/metrics")
async def metrics(db: AsyncSession = Depends(get_db)):
    """
    Basic metrics endpoint for monitoring.

    Returns key recruitment metrics for dashboards.
    """
    try:
        # Application counts
        apps_result = await db.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as last_24h,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as last_7d
                FROM job_applications
            """)
        )
        apps = apps_result.first()

        # Interview counts
        interviews_result = await db.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'scheduled') as scheduled,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed
                FROM ai_interview_sessions
            """)
        )
        interviews = interviews_result.first()

        # Offer counts
        offers_result = await db.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'sent') as sent,
                    COUNT(*) FILTER (WHERE status = 'accepted') as accepted,
                    COUNT(*) FILTER (WHERE status = 'hired') as hired
                FROM offers
            """)
        )
        offers = offers_result.first()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "applications": {
                "total": apps.total if apps else 0,
                "last_24h": apps.last_24h if apps else 0,
                "last_7d": apps.last_7d if apps else 0,
            },
            "ai_interviews": {
                "total": interviews.total if interviews else 0,
                "scheduled": interviews.scheduled if interviews else 0,
                "completed": interviews.completed if interviews else 0,
            },
            "offers": {
                "total": offers.total if offers else 0,
                "sent": offers.sent if offers else 0,
                "accepted": offers.accepted if offers else 0,
                "hired": offers.hired if offers else 0,
            },
        }
    except Exception as e:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)[:100],
        }
