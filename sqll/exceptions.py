"""
Custom exceptions for the SQL Client Library

This module defines all custom exceptions used throughout the library,
providing clear error messages and proper exception hierarchy.
"""

from typing import Optional, Any


class SQLClientError(Exception):
    """
    Base exception class for all SQL Client errors
    
    This is the root exception class that all other custom exceptions
    inherit from, allowing for easy exception handling at the library level.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize the base SQL Client error
        
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
        """Return formatted error message"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConnectionError(SQLClientError):
    """
    Raised when database connection operations fail
    
    This exception is raised when there are issues establishing,
    maintaining, or closing database connections.
    """
    
    def __init__(self, message: str, db_path: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize connection error
        
        Args:
            message: Error message
            db_path: Database path that caused the error
            details: Additional error details
        """
        super().__init__(message, "CONNECTION_ERROR", details)
        self.db_path = db_path


class QueryError(SQLClientError):
    """
    Raised when SQL query execution fails
    
    This exception is raised when there are syntax errors, constraint
    violations, or other issues with SQL query execution.
    """
    
    def __init__(self, message: str, sql: Optional[str] = None, params: Optional[tuple] = None, details: Optional[Any] = None):
        """
        Initialize query error
        
        Args:
            message: Error message
            sql: SQL query that caused the error
            params: Parameters used with the query
            details: Additional error details
        """
        super().__init__(message, "QUERY_ERROR", details)
        self.sql = sql
        self.params = params


class TransactionError(SQLClientError):
    """
    Raised when transaction operations fail
    
    This exception is raised when there are issues with transaction
    management, such as rollback failures or nested transaction problems.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize transaction error
        
        Args:
            message: Error message
            operation: Transaction operation that failed
            details: Additional error details
        """
        super().__init__(message, "TRANSACTION_ERROR", details)
        self.operation = operation


class ValidationError(SQLClientError):
    """
    Raised when input validation fails
    
    This exception is raised when provided data doesn't meet
    the expected format or constraints.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Any] = None):
        """
        Initialize validation error
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional error details
        """
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class ConfigurationError(SQLClientError):
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
        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key


class MigrationError(SQLClientError):
    """
    Raised when database migration operations fail
    
    This exception is raised when there are issues with database
    schema migrations or version management.
    """
    
    def __init__(self, message: str, migration_name: Optional[str] = None, version: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize migration error
        
        Args:
            message: Error message
            migration_name: Name of the migration that failed
            version: Database version when error occurred
            details: Additional error details
        """
        super().__init__(message, "MIGRATION_ERROR", details)
        self.migration_name = migration_name
        self.version = version


# Convenience functions for common error scenarios

def raise_connection_error(db_path: str, original_error: Exception) -> None:
    """
    Raise a ConnectionError with details from the original error
    
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
    Raise a QueryError with details from the original error
    
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
    Raise a ValidationError with field and value details
    
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