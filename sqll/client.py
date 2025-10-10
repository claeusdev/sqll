"""
Main SQL Client class for the SQL Client Library

This module provides the main SQLClient class that serves as the primary
interface for database operations with SQLite.
"""

import sqlite3
import logging
import json
from typing import Any, Dict, List, Optional, Tuple, Union, ContextManager
from contextlib import contextmanager
from datetime import datetime, date
from dataclasses import dataclass

from .connection import ConnectionManager, SimpleConnectionManager, ConnectionConfig
from .query_builder import QueryBuilder, select_from, count_from
from .exceptions import (
    SQLClientError, ConnectionError, QueryError, TransactionError,
    ValidationError, raise_query_error, raise_validation_error
)


@dataclass
class ClientConfig:
    """Configuration for SQLClient"""
    db_path: str
    timeout: float = 30.0
    check_same_thread: bool = False
    isolation_level: Optional[str] = None
    foreign_keys: bool = True
    journal_mode: str = "WAL"
    synchronous: str = "NORMAL"
    cache_size: int = -2000
    temp_store: str = "MEMORY"
    mmap_size: int = 134217728
    use_connection_pool: bool = True
    max_connections: int = 10
    enable_logging: bool = True
    log_level: int = logging.INFO


class SQLClient:
    """
    Main SQL Client class for database operations
    
    This class provides a clean, intuitive interface for SQLite database
    operations with support for both raw SQL and query builder patterns.
    """
    
    def __init__(self, db_path: str, **kwargs):
        """
        Initialize the SQL Client
        
        Args:
            db_path: Path to SQLite database file
            **kwargs: Additional configuration options
        """
        self.config = ClientConfig(db_path=db_path, **kwargs)
        self.logger = self._setup_logging()
        
        # Initialize connection manager
        if self.config.use_connection_pool:
            conn_config = ConnectionConfig(
                db_path=db_path,
                timeout=self.config.timeout,
                check_same_thread=self.config.check_same_thread,
                isolation_level=self.config.isolation_level,
                foreign_keys=self.config.foreign_keys,
                journal_mode=self.config.journal_mode,
                synchronous=self.config.synchronous,
                cache_size=self.config.cache_size,
                temp_store=self.config.temp_store,
                mmap_size=self.config.mmap_size
            )
            self.connection_manager = ConnectionManager(conn_config)
        else:
            self.connection_manager = SimpleConnectionManager(db_path, **kwargs)
        
        self.logger.info(f"SQLClient initialized for database: {db_path}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the client"""
        logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if self.config.enable_logging:
            logger.setLevel(self.config.log_level)
            
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)
        
        return logger
    
    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> sqlite3.Cursor:
        """
        Execute raw SQL query
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            
        Returns:
            SQLite cursor object
            
        Raises:
            QueryError: If query execution fails
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                self.logger.debug(f"Executing SQL: {sql}")
                if params:
                    self.logger.debug(f"Parameters: {params}")
                
                cursor = conn.execute(sql, params or ())
                conn.commit()
                
                self.logger.debug(f"Query executed successfully, affected rows: {cursor.rowcount}")
                return cursor
                
        except sqlite3.Error as e:
            self.logger.error(f"Query execution failed: {e}")
            raise_query_error(sql, params, e)
        except Exception as e:
            self.logger.error(f"Unexpected error during query execution: {e}")
            raise_query_error(sql, params, e)
    
    def execute_many(self, sql: str, params_list: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """
        Execute SQL query multiple times with different parameters
        
        Args:
            sql: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            SQLite cursor object
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                self.logger.debug(f"Executing SQL many times: {sql}")
                self.logger.debug(f"Parameter sets: {len(params_list)}")
                
                cursor = conn.executemany(sql, params_list)
                conn.commit()
                
                self.logger.debug(f"Batch query executed successfully, affected rows: {cursor.rowcount}")
                return cursor
                
        except sqlite3.Error as e:
            self.logger.error(f"Batch query execution failed: {e}")
            raise_query_error(sql, params_list[0] if params_list else None, e)
        except Exception as e:
            self.logger.error(f"Unexpected error during batch query execution: {e}")
            raise_query_error(sql, params_list[0] if params_list else None, e)
    
    def execute_script(self, sql_script: str) -> None:
        """
        Execute multiple SQL statements from a script
        
        Args:
            sql_script: SQL script containing multiple statements
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                self.logger.debug("Executing SQL script")
                conn.executescript(sql_script)
                conn.commit()
                self.logger.debug("SQL script executed successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"SQL script execution failed: {e}")
            raise_query_error(sql_script, None, e)
        except Exception as e:
            self.logger.error(f"Unexpected error during script execution: {e}")
            raise_query_error(sql_script, None, e)
    
    def fetchone(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[sqlite3.Row]:
        """
        Execute query and return single row
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            
        Returns:
            Single row or None if no results
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, params or ())
                result = cursor.fetchone()
                self.logger.debug(f"Fetchone returned: {result is not None}")
                return result
                
        except sqlite3.Error as e:
            self.logger.error(f"Fetchone query failed: {e}")
            raise_query_error(sql, params, e)
    
    def fetchall(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[sqlite3.Row]:
        """
        Execute query and return all rows
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of rows
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, params or ())
                results = cursor.fetchall()
                self.logger.debug(f"Fetchall returned {len(results)} rows")
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Fetchall query failed: {e}")
            raise_query_error(sql, params, e)
    
    def fetchmany(self, sql: str, params: Optional[Tuple[Any, ...]] = None, size: int = 1000) -> List[sqlite3.Row]:
        """
        Execute query and return limited number of rows
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            size: Maximum number of rows to return
            
        Returns:
            List of rows (up to size)
        """
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, params or ())
                results = cursor.fetchmany(size)
                self.logger.debug(f"Fetchmany returned {len(results)} rows")
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Fetchmany query failed: {e}")
            raise_query_error(sql, params, e)
    
    def execute_query(self, query: QueryBuilder) -> List[sqlite3.Row]:
        """
        Execute a QueryBuilder query
        
        Args:
            query: QueryBuilder instance
            
        Returns:
            List of rows
        """
        sql, params = query.build()
        return self.fetchall(sql, params)
    
    # CRUD Operations
    
    def select(self, table: str, columns: Optional[List[str]] = None, 
               where: Optional[Dict[str, Any]] = None, 
               order_by: Optional[Union[str, List[str]]] = None,
               limit: Optional[int] = None, 
               offset: Optional[int] = None) -> List[sqlite3.Row]:
        """
        Select data from table
        
        Args:
            table: Table name
            columns: List of columns to select (default: all)
            where: Dictionary of WHERE conditions
            order_by: Column(s) to order by
            limit: Maximum number of rows
            offset: Number of rows to skip
            
        Returns:
            List of rows
        """
        # Build query using QueryBuilder
        query = QueryBuilder()
        
        # SELECT clause
        if columns:
            query.select(*columns)
        else:
            query.select("*")
        
        query.from_table(table)
        
        # WHERE clause
        if where:
            for column, value in where.items():
                if isinstance(value, list):
                    query.where_in(column, value)
                elif value is None:
                    query.where_is_null(column)
                else:
                    query.where(f"{column} = ?", value)
        
        # ORDER BY clause
        if order_by:
            if isinstance(order_by, str):
                query.order_by(order_by)
            else:
                for col in order_by:
                    query.order_by(col)
        
        # LIMIT and OFFSET
        if limit:
            query.limit(limit)
        if offset:
            query.offset(offset)
        
        return self.execute_query(query)
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert data into table
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs
            
        Returns:
            ID of inserted row
        """
        if not data:
            raise_validation_error("data", data, "Data dictionary cannot be empty")
        
        columns = list(data.keys())
        placeholders = ", ".join("?" * len(columns))
        values = tuple(data[column] for column in columns)
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, values)
                conn.commit()
                row_id = cursor.lastrowid
                self.logger.debug(f"Inserted row with ID: {row_id}")
                return row_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Insert failed: {e}")
            raise_query_error(sql, values, e)
    
    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """
        Insert multiple rows into table
        
        Args:
            table: Table name
            data_list: List of dictionaries with column-value pairs
            
        Returns:
            Number of rows inserted
        """
        if not data_list:
            raise_validation_error("data_list", data_list, "Data list cannot be empty")
        
        # Get columns from first row
        columns = list(data_list[0].keys())
        placeholders = ", ".join("?" * len(columns))
        
        # Prepare data
        params_list = []
        for data in data_list:
            if set(data.keys()) != set(columns):
                raise_validation_error("data_list", data, "All rows must have the same columns")
            params_list.append(tuple(data[column] for column in columns))
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.executemany(sql, params_list)
                conn.commit()
                self.logger.debug(f"Inserted {cursor.rowcount} rows")
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Batch insert failed: {e}")
            raise_query_error(sql, params_list[0] if params_list else None, e)
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """
        Update data in table
        
        Args:
            table: Table name
            data: Dictionary of column-value pairs to update
            where: Dictionary of WHERE conditions
            
        Returns:
            Number of rows updated
        """
        if not data:
            raise_validation_error("data", data, "Data dictionary cannot be empty")
        if not where:
            raise_validation_error("where", where, "WHERE conditions cannot be empty")
        
        # Build SET clause
        set_clauses = []
        values = []
        for column, value in data.items():
            set_clauses.append(f"{column} = ?")
            values.append(value)
        
        # Build WHERE clause
        where_clauses = []
        for column, value in where.items():
            if isinstance(value, list):
                placeholders = ", ".join("?" * len(value))
                where_clauses.append(f"{column} IN ({placeholders})")
                values.extend(value)
            elif value is None:
                where_clauses.append(f"{column} IS NULL")
            else:
                where_clauses.append(f"{column} = ?")
                values.append(value)
        
        sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, tuple(values))
                conn.commit()
                self.logger.debug(f"Updated {cursor.rowcount} rows")
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Update failed: {e}")
            raise_query_error(sql, tuple(values), e)
    
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """
        Delete data from table
        
        Args:
            table: Table name
            where: Dictionary of WHERE conditions
            
        Returns:
            Number of rows deleted
        """
        if not where:
            raise_validation_error("where", where, "WHERE conditions cannot be empty")
        
        # Build WHERE clause
        where_clauses = []
        values = []
        for column, value in where.items():
            if isinstance(value, list):
                placeholders = ", ".join("?" * len(value))
                where_clauses.append(f"{column} IN ({placeholders})")
                values.extend(value)
            elif value is None:
                where_clauses.append(f"{column} IS NULL")
            else:
                where_clauses.append(f"{column} = ?")
                values.append(value)
        
        sql = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.execute(sql, tuple(values))
                conn.commit()
                self.logger.debug(f"Deleted {cursor.rowcount} rows")
                return cursor.rowcount
                
        except sqlite3.Error as e:
            self.logger.error(f"Delete failed: {e}")
            raise_query_error(sql, tuple(values), e)
    
    # Transaction Management
    
    @contextmanager
    def transaction(self) -> ContextManager[None]:
        """
        Context manager for database transactions
        
        Yields:
            None (transaction is managed automatically)
        """
        conn = None
        try:
            conn = self.connection_manager.get_connection()
            self.logger.debug("Transaction started")
            yield
            conn.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            if conn:
                conn.rollback()
                self.logger.debug("Transaction rolled back")
            raise
        finally:
            if conn:
                self.connection_manager.return_connection(conn)
    
    # Utility Methods
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if table exists
        
        Args:
            table_name: Name of the table
            
        Returns:
            True if table exists, False otherwise
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetchone(sql, (table_name,))
        return result is not None
    
    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """
        Get table schema information
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information
        """
        sql = "PRAGMA table_info(?)"
        return self.fetchall(sql, (table_name,))
    
    def get_tables(self) -> List[str]:
        """
        Get list of all tables in the database
        
        Returns:
            List of table names
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.fetchall(sql)
        return [row['name'] for row in results]
    
    def count(self, table: str, where: Optional[Dict[str, Any]] = None) -> int:
        """
        Count rows in table
        
        Args:
            table: Table name
            where: Optional WHERE conditions
            
        Returns:
            Number of rows
        """
        query = count_from(table)
        
        if where:
            for column, value in where.items():
                if isinstance(value, list):
                    query.where_in(column, value)
                elif value is None:
                    query.where_is_null(column)
                else:
                    query.where(f"{column} = ?", value)
        
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def close(self) -> None:
        """Close the database connection"""
        if hasattr(self.connection_manager, 'close_all'):
            self.connection_manager.close_all()
        self.logger.info("SQLClient closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.close()
        except:
            pass