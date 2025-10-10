"""
Connection management for the SQL Client Library

This module handles database connections, connection pooling, and
connection lifecycle management with proper error handling and cleanup.
"""

import sqlite3
import threading
import time
import logging
from typing import Optional, Dict, Any, List, ContextManager
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from .exceptions import ConnectionError, raise_connection_error


class ConnectionState(Enum):
    """Enumeration of possible connection states"""
    CLOSED = "closed"
    OPEN = "open"
    TRANSACTION = "transaction"
    ERROR = "error"


@dataclass
class ConnectionConfig:
    """Configuration for database connections"""
    db_path: str
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: Optional[str] = None
    foreign_keys: bool = True
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = -2000  # 2MB cache
    temp_store: str = "MEMORY"
    mmap_size: int = 134217728  # 128MB


class ConnectionManager:
    """
    Manages database connections with pooling and lifecycle management
    
    This class provides a robust connection management system that handles
    connection creation, pooling, and cleanup with proper error handling.
    """
    
    def __init__(self, config: ConnectionConfig):
        """
        Initialize the connection manager
        
        Args:
            config: Connection configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._lock = threading.Lock()
        self._connections: List[sqlite3.Connection] = []
        self._max_connections = 10
        self._connection_count = 0
        
    def create_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection with proper configuration
        
        Returns:
            Configured SQLite connection
            
        Raises:
            ConnectionError: If connection creation fails
        """
        try:
            self.logger.debug(f"Creating connection to {self.config.db_path}")
            
            # Create connection with timeout
            conn = sqlite3.connect(
                self.config.db_path,
                timeout=self.config.timeout,
                check_same_thread=self.config.check_same_thread,
                isolation_level=self.config.isolation_level
            )
            
            # Configure connection
            self._configure_connection(conn)
            
            # Set row factory for easier data access
            conn.row_factory = sqlite3.Row
            
            self.logger.debug("Connection created successfully")
            return conn
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create connection: {e}")
            raise_connection_error(self.config.db_path, e)
        except Exception as e:
            self.logger.error(f"Unexpected error creating connection: {e}")
            raise_connection_error(self.config.db_path, e)
    
    def _configure_connection(self, conn: sqlite3.Connection) -> None:
        """
        Configure a connection with optimal settings
        
        Args:
            conn: SQLite connection to configure
        """
        try:
            # Enable foreign key constraints
            if self.config.foreign_keys:
                conn.execute("PRAGMA foreign_keys = ON")
            
            # Set journal mode for better concurrency
            conn.execute(f"PRAGMA journal_mode = {self.config.journal_mode}")
            
            # Set synchronous mode for performance vs safety balance
            conn.execute(f"PRAGMA synchronous = {self.config.synchronous}")
            
            # Set cache size for better performance
            conn.execute(f"PRAGMA cache_size = {self.config.cache_size}")
            
            # Set temp store for better performance
            conn.execute(f"PRAGMA temp_store = {self.config.temp_store}")
            
            # Set memory-mapped I/O size
            conn.execute(f"PRAGMA mmap_size = {self.config.mmap_size}")
            
            # Enable query optimization
            conn.execute("PRAGMA optimize")
            
            self.logger.debug("Connection configured successfully")
            
        except sqlite3.Error as e:
            self.logger.warning(f"Failed to configure connection: {e}")
            # Don't raise here as connection is still usable
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection from the pool or create a new one
        
        Returns:
            Available database connection
        """
        with self._lock:
            if self._connections:
                conn = self._connections.pop()
                self.logger.debug("Retrieved connection from pool")
                return conn
            elif self._connection_count < self._max_connections:
                conn = self.create_connection()
                self._connection_count += 1
                self.logger.debug(f"Created new connection (total: {self._connection_count})")
                return conn
            else:
                # Wait for a connection to become available
                self.logger.warning("Connection pool exhausted, waiting for available connection")
                # In a real implementation, you might want to implement a proper wait mechanism
                conn = self.create_connection()
                self._connection_count += 1
                return conn
    
    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        Return a connection to the pool
        
        Args:
            conn: Connection to return to the pool
        """
        if conn is None:
            return
            
        try:
            # Check if connection is still valid
            conn.execute("SELECT 1")
            
            with self._lock:
                if len(self._connections) < self._max_connections:
                    self._connections.append(conn)
                    self.logger.debug("Connection returned to pool")
                else:
                    conn.close()
                    self._connection_count -= 1
                    self.logger.debug("Connection closed (pool full)")
                    
        except sqlite3.Error:
            # Connection is invalid, close it
            try:
                conn.close()
            except:
                pass
            with self._lock:
                self._connection_count -= 1
            self.logger.debug("Invalid connection closed")
    
    def close_all(self) -> None:
        """Close all connections in the pool"""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except:
                    pass
            self._connections.clear()
            self._connection_count = 0
            self.logger.debug("All connections closed")
    
    @contextmanager
    def get_connection_context(self) -> ContextManager[sqlite3.Connection]:
        """
        Context manager for automatic connection management
        
        Yields:
            Database connection that will be automatically returned to pool
        """
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
        finally:
            if conn:
                self.return_connection(conn)
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the connection pool
        
        Returns:
            Dictionary with connection pool statistics
        """
        with self._lock:
            return {
                "max_connections": self._max_connections,
                "active_connections": self._connection_count,
                "available_connections": len(self._connections),
                "db_path": self.config.db_path,
                "timeout": self.config.timeout
            }
    
    def health_check(self) -> bool:
        """
        Perform a health check on the connection pool
        
        Returns:
            True if pool is healthy, False otherwise
        """
        try:
            with self.get_connection_context() as conn:
                conn.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False


class SimpleConnectionManager:
    """
    Simplified connection manager for basic use cases
    
    This is a lightweight version of ConnectionManager that doesn't
    use connection pooling, suitable for simple applications.
    """
    
    def __init__(self, db_path: str, **kwargs):
        """
        Initialize simple connection manager
        
        Args:
            db_path: Path to SQLite database
            **kwargs: Additional connection parameters
        """
        self.db_path = db_path
        self.kwargs = kwargs
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_connection(self) -> sqlite3.Connection:
        """
        Create a new database connection
        
        Returns:
            Configured SQLite connection
        """
        try:
            conn = sqlite3.connect(self.db_path, **self.kwargs)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            raise_connection_error(self.db_path, e)
    
    @contextmanager
    def get_connection_context(self) -> ContextManager[sqlite3.Connection]:
        """
        Context manager for connection management
        
        Yields:
            Database connection that will be automatically closed
        """
        conn = None
        try:
            conn = self.create_connection()
            yield conn
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
        finally:
            if conn:
                conn.close()