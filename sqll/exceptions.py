class SQLLError(Exception):
    """Base exception for SQLL errors"""
    pass

SQLClientError = SQLLError

class ConnectionError(SQLLError):
    """Raised when database connection fails"""
    pass

class QueryError(SQLLError):
    """Raised when query execution fails"""
    pass

class ValidationError(SQLLError):
    """Raised when input validation fails"""
    pass

class TransactionError(SQLLError):
    """Raised when transaction fails"""
    pass
