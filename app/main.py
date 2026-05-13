"""
Main FastAPI application factory with improved architecture.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config.settings import settings
from app.core.exceptions import (
    AppError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
    ValidationError
)
from app.core.middleware import RequestLoggingMiddleware
from app.config.logging import setup_logging
from app.schemas.base import HealthResponse, ErrorResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handle startup and shutdown events.
    """
    # Startup
    setup_logging()
    print(f"Starting {settings.app_name} v{settings.version}")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    
    # Database will be initialized via Alembic migrations
    print("Database initialization will be handled by Alembic migrations")
    
    # TODO: Initialize external service connections
    # TODO: Load configuration and caches
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.app_name}")
    # TODO: Close database connections
    # TODO: Close external service connections
    # TODO: Clean up resources


def create_app() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application.
    """
    app = FastAPI(
        title=settings.app_name,
        description="Tetrics: Testing Metrics Meassurement CRUD Application",
        version=settings.version,
        docs_url=settings.docs_url if not settings.is_production else None,
        redoc_url=settings.redoc_url if not settings.is_production else None,
        openapi_url=settings.openapi_url if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Configure CORS - must be before other middleware
    # Allow all localhost ports for development
    if settings.debug:
        print(f"Configuring CORS with allow_origins=['*']")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=False,  # Must be False when allow_origins is ["*"]
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(RequestLoggingMiddleware)
    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    # Health check endpoints
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with basic information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.version,
            "environment": settings.environment,
            "docs": settings.docs_url,
            "status": "active"
        }
    
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check():
        """Comprehensive health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version=settings.version,
            environment=settings.environment
        )

    @app.get("/health/readiness", tags=["health"])
    async def readiness_check():
        """Readiness check for Kubernetes."""
        # Simple database connectivity check
        try:
            from app.config.database import engine
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            db_healthy = True
        except Exception:
            db_healthy = False
        
        if not db_healthy:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "database": "unhealthy"}
            )
        
        # TODO: Check external service availability
        return {"status": "ready", "database": "healthy"}


    # Global exception handler
    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError):
        """Handle application-specific exceptions."""
        status_code = status.HTTP_400_BAD_REQUEST
        
        # Map exception types to HTTP status codes
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, ConflictError):
            status_code = status.HTTP_409_CONFLICT
        elif isinstance(exc, UnauthorizedError):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, ForbiddenError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error=exc.message,
                error_code=exc.error_code,
                details=exc.details
            ).model_dump()
        )


    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Return friendlier 422 payloads for request validation errors and invalid JSON."""
        # exc.errors() gives field-level error details
        errors = exc.errors()
        # If the root cause is a JSON decode error, FastAPI will raise a RequestValidationError with a body error.
        # Provide an explanatory response that suggests common fixes.
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Request validation failed",
                "message": "Your request body could not be parsed or did not match the expected schema.",
                "details": errors,
                "hint": "Check that your request is valid JSON and that fields match their expected types (avoid trailing commas, percent signs in numbers, and unescaped characters)."
            }
        )


    return app


# Create application instance
app = create_app()
