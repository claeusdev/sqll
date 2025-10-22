"""
Custom exceptions for the SQLL

This module defines all custom exceptions used throughout the library,
providing clear error messages and proper exception hierarchy.
"""

from typing import Optional, Any
from enum import Enum

class ErrorCodes(Enum):
    connection_error = "connection_error"
    transaction_error = "transaction_error"
    query_error = "query_error"
    validation_error = "validation_error"
    migration_error = "migration_error"
    configuration_error ="configuration_error"


class SQLLError(Exception):
    """
    Base exception class for all SQLL errors

    Root exception class that all other custom exceptions
    inherit from, allowing for easy exception handling at the library level.
    """
    def __init__(self, message: str, error_code: ErrorCodes | None = None, details: Optional[Any] = None):
        """
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}]: {self.message}"
        return self.message


class ConnectionError(SQLLError):
    """
    Raised when database connection operations fail

    When there are issues establishing, maintaining, or closing database connections.
    """

    def __init__(self, message: str, db_path: Optional[str] = None, details: Optional[Any] = None):
        """
        Args:
            message: Error message
            db_path: Database path that caused the error
            details: Additional error details
        """
        super().__init__(details, message=message, error_code=ErrorCodes.connection_error)
        self.db_path = db_path


class QueryError(SQLLError):
    """
    Raised when SQL query execution fails

    When there are syntax errors, constraint violations, or other issues with SQL query execution.
    """
    def __init__(self, message: str, sql: Optional[str] = None, params: Optional[tuple] = None, details: Optional[Any] = None):
        """
        Args:
            message: Error message
            sql: SQL query that caused the error
            params: Parameters used with the query
            details: Additional error details
        """
        super().__init__(details, message=message, error_code=ErrorCodes.query_error)
        self.sql = sql
        self.params = params


class TransactionError(SQLLError):
    """
    Raised when transaction operations fail

    When there are issues with transaction
    management, such as rollback failures or nested transaction problems.
    """
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Any] = None):
        """
        Args:
            message: Error message
            operation: Transaction operation that failed
            details: Additional error details
        """
        super().__init__(details, message=message, error_code=ErrorCodes.transaction_error)
        self.operation = operation


class ValidationError(SQLLError):
    """
    Raised when input validation fails

    When provided data doesn't meet
    the expected format or constraints.
    """
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Any] = None):
        """
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional error details
        """
        super().__init__(details, message=message, error_code=ErrorCodes.validation_error)
        self.field = field
        self.value = value


class ConfigurationError(SQLLError):
    """
    Raised when library configuration is invalid
    This exception is raised when there are issues with library
    configuration, such as invalid connection parameters.
    """
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize configuration error
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            details: Additional error details
        """
        super().__init__(details, error_code=ErrorCodes.configuration_error, message=message)
        self.config_key = config_key


class MigrationError(SQLLError):
    """
    Raised when database migration operations fail

    When there are issues with database
    schema migrations or version management.
    """
    def __init__(self, message: str, migration_name: Optional[str] = None, version: Optional[str] = None, details: Optional[Any] = None):
        """
        Args:
            message: Error message
            migration_name: Name of the migration that failed
            version: Database version when error occurred
            details: Additional error details
        """
        super().__init__(details, error_code=ErrorCodes.migration_error, message=message)
        self.migration_name = migration_name
        self.version = version


# Convenience functions for common error scenarios

def raise_connection_error(db_path: str, original_error: Exception) -> None:
    """
    ConnectionError with details from the original error
    Args:
        db_path: Database path that caused the error
        original_error: Original exception that occurred
    """
    raise ConnectionError(
        f"Failed to connect to database '{db_path}': {str(original_error)}",
        db_path=db_path,
        details={"original_error": str(original_error), "error_type": type(original_error).__name__}
    )


def raise_query_error(sql: str, params: Optional[tuple], original_error: Exception) -> None:
    """
    QueryError with details from the original error
    Args:
        sql: SQL query that caused the error
        params: Parameters used with the query
        original_error: Original exception that occurred
    """
    raise QueryError(
        f"Query execution failed: {str(original_error)}",
        sql=sql,
        params=params,
        details={"original_error": str(original_error), "error_type": type(original_error).__name__}
    )


def raise_validation_error(field: str, value: Any, message: str) -> None:
    """
    ValidationError with field and value details
    Args:
        field: Field that failed validation
        value: Value that failed validation
        message: Error message
    """
    raise ValidationError(
        f"Validation failed for field '{field}': {message}",
        field=field,
        value=value,
        details={"field": field, "value": str(value)}
    )
