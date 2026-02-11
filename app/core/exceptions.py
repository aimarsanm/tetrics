"""
Custom application exceptions.
"""
from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error exception."""
    pass


class NotFoundError(AppError):
    """Resource not found exception."""
    pass


class ConflictError(AppError):
    """Resource conflict exception."""
    pass


class UnauthorizedError(AppError):
    """Unauthorized access exception."""
    pass


class ForbiddenError(AppError):
    """Forbidden access exception."""
    pass


class DatabaseError(AppError):
    """Database operation exception."""
    pass


class ExternalServiceError(AppError):
    """External service error exception."""
    pass


class ConfigurationError(AppError):
    """Configuration error exception."""
    pass
