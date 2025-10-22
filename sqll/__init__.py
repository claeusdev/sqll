"""
SQL Client Library for SQLite

A simple SQL client library for Python with SQLite support.
Provides a simple interface for database operations while maintaining
the flexibility and power of raw SQL.

Author: Nana Adjei Manu
Version: 1.0.0
"""

from .client import SQLClient
from .connection import ConnectionManager
from .query_builder import QueryBuilder
from .exceptions import (
    SQLClientError,
    ConnectionError,
    QueryError,
    TransactionError,
    ValidationError
)

__version__ = "1.0.0"
__author__ = "Nana Adjei Manu"

__all__ = [
    'SQLClient',
    'ConnectionManager',
    'QueryBuilder',
    'SQLClientError',
    'ConnectionError',
    'QueryError',
    'TransactionError',
    'ValidationError'
]
