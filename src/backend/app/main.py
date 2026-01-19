"""
GanaPortal - AI-First ERP System
Main FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import structlog

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine
from app.core.security import (
    SecurityHeadersMiddleware,
    SQLInjectionMiddleware,
    XSSProtectionMiddleware,
    RateLimitMiddleware,
)


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info(
        "Starting GanaPortal",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )

    # Initialize database connection pool
    # await init_db()

    yield

    # Shutdown
    logger.info("Shutting down GanaPortal")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-First ERP System for Ganakys Codilla Apps",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# CORS Middleware - Restricted to necessary methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "X-CSRF-Token",
    ],
    expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# GZip Middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Middleware - Defense in depth
# Note: These are ADDITIONAL protections, not replacements for:
# - Parameterized queries (for SQL injection)
# - Output encoding (for XSS)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SQLInjectionMiddleware)
app.add_middleware(XSSProtectionMiddleware)

# Rate Limiting - Protect against DoS and abuse
# Uses Redis for distributed deployments, falls back to in-memory for single instance
app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,  # requests per window
    window=60,  # seconds
    redis_url=getattr(settings, 'REDIS_URL', None)
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Disabled in production",
        "health": "/health"
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
