import sqlite3
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, ContextManager
from contextlib import contextmanager

from .exceptions import ConnectionError, QueryError, ValidationError
from .query_builder import QueryBuilder

class SQLClient:
    """Simple SQL Client"""
    
    def __init__(self, db_path: str, **kwargs):
        self.db_path = db_path
        self.conn_kwargs = kwargs
        self._conn = None
        self.logger = logging.getLogger(__name__)
        self._in_transaction = False
        
    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(self.db_path, **self.conn_kwargs)
                self._conn.row_factory = sqlite3.Row
                self._conn.execute("PRAGMA foreign_keys = ON")
            except sqlite3.Error as e:
                raise ConnectionError(f"Failed to connect to {self.db_path}: {e}")
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @contextmanager
    def transaction(self):
        """Context manager for transactions"""
        conn = self.connect()
        if self._in_transaction:
            yield
            return
            
        self._in_transaction = True
        try:
            yield
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._in_transaction = False

    def _execute(self, sql: str, params: Tuple[Any, ...] = ()) -> sqlite3.Cursor:
        conn = self.connect()
        try:
            cursor = conn.execute(sql, params)
            if not self._in_transaction:
                conn.commit()
            return cursor
        except sqlite3.Error as e:
            raise QueryError(f"Query failed: {e}")

    def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Execute raw SQL"""
        return self._execute(sql, params)

    def execute_many(self, sql: str, params_list: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """Execute multiple SQL statements"""
        conn = self.connect()
        try:
            cursor = conn.executemany(sql, params_list)
            if not self._in_transaction:
                conn.commit()
            return cursor
        except sqlite3.Error as e:
            raise QueryError(f"Batch execution failed: {e}")

    def execute_query(self, query: QueryBuilder) -> List[sqlite3.Row]:
        """Execute a QueryBuilder query"""
        sql, params = query.build()
        return self.fetchall(sql, params)

    def fetchall(self, sql: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Execute and return all rows"""
        conn = self.connect()
        try:
            cursor = conn.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise QueryError(f"Fetch failed: {e}")

    def fetchone(self, sql: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Execute and return one row"""
        conn = self.connect()
        try:
            cursor = conn.execute(sql, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            raise QueryError(f"Fetch failed: {e}")

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a row"""
        if not data:
            raise ValidationError("Data cannot be empty")
            
        columns = list(data.keys())
        placeholders = ", ".join("?" * len(columns))
        values = tuple(data[c] for c in columns)
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        cursor = self._execute(sql, values)
        return cursor.lastrowid

    def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple rows"""
        if not data_list:
            raise ValidationError("Data list cannot be empty")
            
        columns = list(data_list[0].keys())
        placeholders = ", ".join("?" * len(columns))
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        params_list = []
        for data in data_list:
            params_list.append(tuple(data[c] for c in columns))
            
        cursor = self.execute_many(sql, params_list)
        return cursor.rowcount

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update rows"""
        if not data or not where:
            raise ValidationError("Data and Where clauses required")
            
        set_clauses = [f"{k} = ?" for k in data.keys()]
        where_clauses = []
        values = list(data.values())
        
        for k, v in where.items():
            if v is None:
                where_clauses.append(f"{k} IS NULL")
            else:
                where_clauses.append(f"{k} = ?")
                values.append(v)
                
        sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        
        cursor = self._execute(sql, tuple(values))
        return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete rows"""
        if not where:
            raise ValidationError("Where clause required")
            
        where_clauses = []
        values = []
        
        for k, v in where.items():
            if v is None:
                where_clauses.append(f"{k} IS NULL")
            else:
                where_clauses.append(f"{k} = ?")
                values.append(v)
                
        sql = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)}"
        
        cursor = self._execute(sql, tuple(values))
        return cursor.rowcount

    def select(self, table: str, **kwargs) -> List[sqlite3.Row]:
        """Select rows using QueryBuilder logic"""
        qb = QueryBuilder().from_table(table)
        if 'columns' in kwargs:
            qb.select(*kwargs['columns'])
        else:
            qb.select("*")
            
        if 'where' in kwargs:
            for k, v in kwargs['where'].items():
                if isinstance(v, list):
                    qb.where_in(k, v)
                elif v is None:
                    qb.where(f"{k} IS NULL")
                else:
                    qb.where(f"{k} = ?", v)
                    
        if 'limit' in kwargs:
            qb.limit(kwargs['limit'])
        if 'offset' in kwargs:
            qb.offset(kwargs['offset'])
        if 'order_by' in kwargs:
            qb.order_by(kwargs['order_by'])
            
        return self.execute_query(qb)

    def count(self, table: str, where: Optional[Dict[str, Any]] = None) -> int:
        """Count rows"""
        qb = QueryBuilder().select("COUNT(*)").from_table(table)
        if where:
            for k, v in where.items():
                if isinstance(v, list):
                    qb.where_in(k, v)
                elif v is None:
                    qb.where(f"{k} IS NULL")
                else:
                    qb.where(f"{k} = ?", v)
        
        result = self.execute_query(qb)
        return result[0][0] if result else 0

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self.fetchone(sql, (table_name,))
        return result is not None

    def get_table_info(self, table_name: str) -> List[sqlite3.Row]:
        """Get table schema info"""
        return self.fetchall(f"PRAGMA table_info({table_name})")

    def get_tables(self) -> List[str]:
        """Get all tables"""
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        results = self.fetchall(sql)
        return [row['name'] for row in results]
