"""
Standardized Error Messages
Centralized error messages for consistent API responses
"""
from fastapi import HTTPException, status


# ============================================================================
# Standard Error Messages
# ============================================================================

class ErrorMessages:
    """Standard error messages for API responses"""

    # Authentication & Authorization
    INVALID_CREDENTIALS = "Could not validate credentials"
    AUTH_REQUIRED = "Authentication required"
    PERMISSION_DENIED = "Permission denied"
    INSUFFICIENT_PERMISSIONS = "Insufficient permissions for this operation"
    INVALID_TOKEN = "Invalid or expired token"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_REFRESH_TOKEN = "Invalid or expired refresh token"

    # Resource Not Found
    NOT_FOUND = "{resource} not found"
    USER_NOT_FOUND = "User not found"
    COMPANY_NOT_FOUND = "Company not found"
    EMPLOYEE_NOT_FOUND = "Employee not found"
    DOCUMENT_NOT_FOUND = "Document not found"
    RECORD_NOT_FOUND = "Record not found"

    # Validation Errors
    INVALID_INPUT = "Invalid input data"
    MISSING_REQUIRED_FIELD = "Missing required field: {field}"
    INVALID_FORMAT = "Invalid format for {field}"
    VALUE_OUT_OF_RANGE = "Value out of range for {field}"
    DUPLICATE_ENTRY = "{resource} already exists"

    # Business Logic Errors
    OPERATION_NOT_ALLOWED = "Operation not allowed in current state"
    ALREADY_EXISTS = "{resource} already exists"
    CANNOT_DELETE = "Cannot delete {resource}: {reason}"
    CANNOT_UPDATE = "Cannot update {resource}: {reason}"

    # Server Errors
    INTERNAL_ERROR = "An internal error occurred"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"
    DATABASE_ERROR = "Database operation failed"

    # File Operations
    FILE_TOO_LARGE = "File size exceeds maximum limit"
    INVALID_FILE_TYPE = "Invalid file type"
    FILE_NOT_FOUND = "File not found"
    UPLOAD_FAILED = "File upload failed"


# ============================================================================
# Exception Factory Functions
# ============================================================================

def not_found(resource: str) -> HTTPException:
    """Create a 404 Not Found exception"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource} not found"
    )


def bad_request(message: str) -> HTTPException:
    """Create a 400 Bad Request exception"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def unauthorized(message: str = ErrorMessages.AUTH_REQUIRED) -> HTTPException:
    """Create a 401 Unauthorized exception"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"}
    )


def forbidden(message: str = ErrorMessages.PERMISSION_DENIED) -> HTTPException:
    """Create a 403 Forbidden exception"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )


def conflict(resource: str) -> HTTPException:
    """Create a 409 Conflict exception"""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{resource} already exists"
    )


def unprocessable(message: str) -> HTTPException:
    """Create a 422 Unprocessable Entity exception"""
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=message
    )


def internal_error(message: str = ErrorMessages.INTERNAL_ERROR) -> HTTPException:
    """Create a 500 Internal Server Error exception"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )


def service_unavailable(message: str = ErrorMessages.SERVICE_UNAVAILABLE) -> HTTPException:
    """Create a 503 Service Unavailable exception"""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=message
    )


# ============================================================================
# Common Exception Patterns
# ============================================================================

class ResourceNotFoundError(Exception):
    """Raised when a requested resource is not found"""
    def __init__(self, resource: str, identifier: str = None):
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with id '{identifier}' not found"
        super().__init__(message)


class PermissionDeniedError(Exception):
    """Raised when user lacks permission for an operation"""
    def __init__(self, operation: str = None):
        self.operation = operation
        message = "Permission denied"
        if operation:
            message = f"Permission denied for operation: {operation}"
        super().__init__(message)


class ValidationError(Exception):
    """Raised when input validation fails"""
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")


class BusinessRuleError(Exception):
    """Raised when a business rule is violated"""
    def __init__(self, message: str):
        super().__init__(message)
