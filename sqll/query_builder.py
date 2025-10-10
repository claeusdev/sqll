"""
Query Builder for the SQL Client Library

This module provides a fluent interface for building SQL queries
with type safety and proper parameter handling.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class JoinType(Enum):
    """Types of SQL joins"""
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"


class OrderDirection(Enum):
    """Order by directions"""
    ASC = "ASC"
    DESC = "DESC"


@dataclass
class JoinClause:
    """Represents a JOIN clause in a query"""
    table: str
    condition: str
    join_type: JoinType = JoinType.INNER
    alias: Optional[str] = None


@dataclass
class WhereClause:
    """Represents a WHERE clause in a query"""
    condition: str
    params: Tuple[Any, ...] = ()


class QueryBuilder:
    """
    Fluent interface for building SQL queries
    
    This class provides a clean, readable way to build complex SQL queries
    with proper parameter handling and type safety.
    """
    
    def __init__(self):
        """Initialize the query builder"""
        self._select_columns: List[str] = []
        self._from_table: Optional[str] = None
        self._joins: List[JoinClause] = []
        self._where_clauses: List[WhereClause] = []
        self._group_by_columns: List[str] = []
        self._having_clauses: List[WhereClause] = []
        self._order_by_columns: List[Tuple[str, OrderDirection]] = []
        self._limit_count: Optional[int] = None
        self._offset_count: Optional[int] = None
        self._distinct: bool = False
        self._union_queries: List['QueryBuilder'] = []
    
    def select(self, *columns: str) -> 'QueryBuilder':
        """
        Add columns to SELECT clause
        
        Args:
            *columns: Column names or expressions to select
            
        Returns:
            Self for method chaining
        """
        self._select_columns.extend(columns)
        return self
    
    def select_distinct(self, *columns: str) -> 'QueryBuilder':
        """
        Add columns to SELECT DISTINCT clause
        
        Args:
            *columns: Column names or expressions to select
            
        Returns:
            Self for method chaining
        """
        self._distinct = True
        self._select_columns.extend(columns)
        return self
    
    def from_table(self, table: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """
        Set the main table for FROM clause
        
        Args:
            table: Table name
            alias: Optional table alias
            
        Returns:
            Self for method chaining
        """
        if alias:
            self._from_table = f"{table} {alias}"
        else:
            self._from_table = table
        return self
    
    def join(self, table: str, condition: str, join_type: JoinType = JoinType.INNER, alias: Optional[str] = None) -> 'QueryBuilder':
        """
        Add a JOIN clause
        
        Args:
            table: Table name to join
            condition: JOIN condition
            join_type: Type of join
            alias: Optional table alias
            
        Returns:
            Self for method chaining
        """
        join_clause = JoinClause(table, condition, join_type, alias)
        self._joins.append(join_clause)
        return self
    
    def inner_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add an INNER JOIN clause"""
        return self.join(table, condition, JoinType.INNER, alias)
    
    def left_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add a LEFT JOIN clause"""
        return self.join(table, condition, JoinType.LEFT, alias)
    
    def right_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add a RIGHT JOIN clause"""
        return self.join(table, condition, JoinType.RIGHT, alias)
    
    def full_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add a FULL OUTER JOIN clause"""
        return self.join(table, condition, JoinType.FULL, alias)
    
    def cross_join(self, table: str, alias: Optional[str] = None) -> 'QueryBuilder':
        """Add a CROSS JOIN clause"""
        return self.join(table, "", JoinType.CROSS, alias)
    
    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """
        Add a WHERE clause
        
        Args:
            condition: WHERE condition with placeholders
            *params: Parameters for the condition
            
        Returns:
            Self for method chaining
        """
        where_clause = WhereClause(condition, params)
        self._where_clauses.append(where_clause)
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """
        Add WHERE column IN (values) clause
        
        Args:
            column: Column name
            values: List of values
            
        Returns:
            Self for method chaining
        """
        if not values:
            return self.where("1 = 0")  # Empty IN clause
        
        placeholders = ", ".join("?" * len(values))
        condition = f"{column} IN ({placeholders})"
        return self.where(condition, *values)
    
    def where_not_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        """
        Add WHERE column NOT IN (values) clause
        
        Args:
            column: Column name
            values: List of values
            
        Returns:
            Self for method chaining
        """
        if not values:
            return self  # Empty NOT IN clause is always true
        
        placeholders = ", ".join("?" * len(values))
        condition = f"{column} NOT IN ({placeholders})"
        return self.where(condition, *values)
    
    def where_between(self, column: str, start: Any, end: Any) -> 'QueryBuilder':
        """
        Add WHERE column BETWEEN start AND end clause
        
        Args:
            column: Column name
            start: Start value
            end: End value
            
        Returns:
            Self for method chaining
        """
        return self.where(f"{column} BETWEEN ? AND ?", start, end)
    
    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        """
        Add WHERE column LIKE pattern clause
        
        Args:
            column: Column name
            pattern: LIKE pattern
            
        Returns:
            Self for method chaining
        """
        return self.where(f"{column} LIKE ?", pattern)
    
    def where_is_null(self, column: str) -> 'QueryBuilder':
        """
        Add WHERE column IS NULL clause
        
        Args:
            column: Column name
            
        Returns:
            Self for method chaining
        """
        return self.where(f"{column} IS NULL")
    
    def where_is_not_null(self, column: str) -> 'QueryBuilder':
        """
        Add WHERE column IS NOT NULL clause
        
        Args:
            column: Column name
            
        Returns:
            Self for method chaining
        """
        return self.where(f"{column} IS NOT NULL")
    
    def group_by(self, *columns: str) -> 'QueryBuilder':
        """
        Add columns to GROUP BY clause
        
        Args:
            *columns: Column names to group by
            
        Returns:
            Self for method chaining
        """
        self._group_by_columns.extend(columns)
        return self
    
    def having(self, condition: str, *params: Any) -> 'QueryBuilder':
        """
        Add a HAVING clause
        
        Args:
            condition: HAVING condition with placeholders
            *params: Parameters for the condition
            
        Returns:
            Self for method chaining
        """
        having_clause = WhereClause(condition, params)
        self._having_clauses.append(having_clause)
        return self
    
    def order_by(self, column: str, direction: OrderDirection = OrderDirection.ASC) -> 'QueryBuilder':
        """
        Add a column to ORDER BY clause
        
        Args:
            column: Column name or expression
            direction: Sort direction
            
        Returns:
            Self for method chaining
        """
        self._order_by_columns.append((column, direction))
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """
        Add LIMIT clause
        
        Args:
            count: Number of rows to limit
            
        Returns:
            Self for method chaining
        """
        self._limit_count = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """
        Add OFFSET clause
        
        Args:
            count: Number of rows to skip
            
        Returns:
            Self for method chaining
        """
        self._offset_count = count
        return self
    
    def union(self, other_query: 'QueryBuilder') -> 'QueryBuilder':
        """
        Add a UNION with another query
        
        Args:
            other_query: Another QueryBuilder instance
            
        Returns:
            Self for method chaining
        """
        self._union_queries.append(other_query)
        return self
    
    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        """
        Build the final SQL query and parameters
        
        Returns:
            Tuple of (SQL query string, parameters tuple)
        """
        sql_parts = []
        params = []
        
        # SELECT clause
        if not self._select_columns:
            raise ValueError("SELECT clause is required")
        
        distinct_str = "DISTINCT " if self._distinct else ""
        select_str = f"SELECT {distinct_str}{', '.join(self._select_columns)}"
        sql_parts.append(select_str)
        
        # FROM clause
        if not self._from_table:
            raise ValueError("FROM clause is required")
        
        sql_parts.append(f"FROM {self._from_table}")
        
        # JOIN clauses
        for join in self._joins:
            table_str = join.table
            if join.alias:
                table_str += f" {join.alias}"
            
            if join.join_type == JoinType.CROSS:
                sql_parts.append(f"{join.join_type.value} {table_str}")
            else:
                sql_parts.append(f"{join.join_type.value} {table_str} ON {join.condition}")
        
        # WHERE clauses
        if self._where_clauses:
            where_conditions = []
            for where_clause in self._where_clauses:
                where_conditions.append(where_clause.condition)
                params.extend(where_clause.params)
            
            sql_parts.append(f"WHERE {' AND '.join(where_conditions)}")
        
        # GROUP BY clause
        if self._group_by_columns:
            sql_parts.append(f"GROUP BY {', '.join(self._group_by_columns)}")
        
        # HAVING clauses
        if self._having_clauses:
            having_conditions = []
            for having_clause in self._having_clauses:
                having_conditions.append(having_clause.condition)
                params.extend(having_clause.params)
            
            sql_parts.append(f"HAVING {' AND '.join(having_conditions)}")
        
        # ORDER BY clause
        if self._order_by_columns:
            order_parts = []
            for column, direction in self._order_by_columns:
                order_parts.append(f"{column} {direction.value}")
            sql_parts.append(f"ORDER BY {', '.join(order_parts)}")
        
        # LIMIT clause
        if self._limit_count is not None:
            sql_parts.append(f"LIMIT {self._limit_count}")
        
        # OFFSET clause
        if self._offset_count is not None:
            sql_parts.append(f"OFFSET {self._offset_count}")
        
        # Build main query
        main_sql = " ".join(sql_parts)
        
        # Handle UNION queries
        if self._union_queries:
            union_sql_parts = [main_sql]
            for union_query in self._union_queries:
                union_sql, union_params = union_query.build()
                union_sql_parts.append(f"UNION {union_sql}")
                params.extend(union_params)
            
            main_sql = " ".join(union_sql_parts)
        
        return main_sql, tuple(params)
    
    def __str__(self) -> str:
        """Return string representation of the query"""
        sql, params = self.build()
        if params:
            return f"{sql} -- Params: {params}"
        return sql
    
    def clone(self) -> 'QueryBuilder':
        """
        Create a copy of this query builder
        
        Returns:
            New QueryBuilder instance with same configuration
        """
        new_builder = QueryBuilder()
        new_builder._select_columns = self._select_columns.copy()
        new_builder._from_table = self._from_table
        new_builder._joins = self._joins.copy()
        new_builder._where_clauses = self._where_clauses.copy()
        new_builder._group_by_columns = self._group_by_columns.copy()
        new_builder._having_clauses = self._having_clauses.copy()
        new_builder._order_by_columns = self._order_by_columns.copy()
        new_builder._limit_count = self._limit_count
        new_builder._offset_count = self._offset_count
        new_builder._distinct = self._distinct
        new_builder._union_queries = self._union_queries.copy()
        return new_builder


# Convenience functions for common query patterns

def select_from(table: str, *columns: str) -> QueryBuilder:
    """
    Create a query builder with SELECT and FROM clauses
    
    Args:
        table: Table name
        *columns: Columns to select
        
    Returns:
        Configured QueryBuilder instance
    """
    return QueryBuilder().select(*columns).from_table(table)


def count_from(table: str, column: str = "*") -> QueryBuilder:
    """
    Create a COUNT query
    
    Args:
        table: Table name
        column: Column to count (default: *)
        
    Returns:
        Configured QueryBuilder instance
    """
    return QueryBuilder().select(f"COUNT({column})").from_table(table)


def exists_in(table: str, condition: str, *params: Any) -> QueryBuilder:
    """
    Create an EXISTS subquery
    
    Args:
        table: Table name
        condition: WHERE condition
        *params: Parameters for the condition
        
    Returns:
        Configured QueryBuilder instance
    """
    return QueryBuilder().select("1").from_table(table).where(condition, *params)