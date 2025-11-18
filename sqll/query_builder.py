from typing import List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class JoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"

class OrderDirection(Enum):
    ASC = "ASC"
    DESC = "DESC"

@dataclass
class JoinClause:
    table: str
    condition: str
    join_type: JoinType = JoinType.INNER
    alias: Optional[str] = None

@dataclass
class WhereClause:
    condition: str
    params: Tuple[Any, ...] = ()

class QueryBuilder:
    """Fluent interface for building SQL queries"""
    
    def __init__(self):
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
        self._select_columns.extend(columns)
        return self

    def from_table(self, table: str, alias: Optional[str] = None) -> 'QueryBuilder':
        self._from_table = f"{table} {alias}" if alias else table
        return self

    def join(self, table: str, condition: str, join_type: JoinType = JoinType.INNER, alias: Optional[str] = None) -> 'QueryBuilder':
        self._joins.append(JoinClause(table, condition, join_type, alias))
        return self

    def inner_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        return self.join(table, condition, JoinType.INNER, alias)

    def left_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        return self.join(table, condition, JoinType.LEFT, alias)

    def right_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        return self.join(table, condition, JoinType.RIGHT, alias)

    def full_join(self, table: str, condition: str, alias: Optional[str] = None) -> 'QueryBuilder':
        return self.join(table, condition, JoinType.FULL, alias)
    
    def cross_join(self, table: str, alias: Optional[str] = None) -> 'QueryBuilder':
        return self.join(table, "", JoinType.CROSS, alias)

    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        self._where_clauses.append(WhereClause(condition, params))
        return self
    
    def where_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        if not values:
            return self.where("1 = 0")
        placeholders = ", ".join("?" * len(values))
        return self.where(f"{column} IN ({placeholders})", *values)

    def where_not_in(self, column: str, values: List[Any]) -> 'QueryBuilder':
        if not values:
            return self
        placeholders = ", ".join("?" * len(values))
        return self.where(f"{column} NOT IN ({placeholders})", *values)

    def where_between(self, column: str, start: Any, end: Any) -> 'QueryBuilder':
        return self.where(f"{column} BETWEEN ? AND ?", start, end)

    def where_like(self, column: str, pattern: str) -> 'QueryBuilder':
        return self.where(f"{column} LIKE ?", pattern)

    def where_is_null(self, column: str) -> 'QueryBuilder':
        return self.where(f"{column} IS NULL")

    def where_is_not_null(self, column: str) -> 'QueryBuilder':
        return self.where(f"{column} IS NOT NULL")

    def group_by(self, *columns: str) -> 'QueryBuilder':
        self._group_by_columns.extend(columns)
        return self

    def having(self, condition: str, *params: Any) -> 'QueryBuilder':
        self._having_clauses.append(WhereClause(condition, params))
        return self
    
    def union(self, other_query: 'QueryBuilder') -> 'QueryBuilder':
        self._union_queries.append(other_query)
        return self

    def order_by(self, column: str, direction: Union[OrderDirection, str] = OrderDirection.ASC) -> 'QueryBuilder':
        if isinstance(direction, str):
            direction = OrderDirection(direction.upper())
        self._order_by_columns.append((column, direction))
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        self._limit_count = count
        return self

    def offset(self, count: int) -> 'QueryBuilder':
        self._offset_count = count
        return self

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if not self._select_columns:
            raise ValueError("SELECT clause is required")
        if not self._from_table:
            raise ValueError("FROM clause is required")

        sql_parts = []
        params = []

        # SELECT
        distinct = "DISTINCT " if self._distinct else ""
        sql_parts.append(f"SELECT {distinct}{', '.join(self._select_columns)}")
        
        # FROM
        sql_parts.append(f"FROM {self._from_table}")

        # JOINs
        for join in self._joins:
            table_str = f"{join.table} {join.alias}" if join.alias else join.table
            if join.join_type == JoinType.CROSS:
                sql_parts.append(f"{join.join_type.value} {table_str}")
            else:
                sql_parts.append(f"{join.join_type.value} {table_str} ON {join.condition}")

        # WHERE
        if self._where_clauses:
            conditions = [w.condition for w in self._where_clauses]
            sql_parts.append(f"WHERE {' AND '.join(conditions)}")
            for w in self._where_clauses:
                params.extend(w.params)

        # GROUP BY
        if self._group_by_columns:
            sql_parts.append(f"GROUP BY {', '.join(self._group_by_columns)}")

        # HAVING
        if self._having_clauses:
            conditions = [h.condition for h in self._having_clauses]
            sql_parts.append(f"HAVING {' AND '.join(conditions)}")
            for h in self._having_clauses:
                params.extend(h.params)

        # ORDER BY
        if self._order_by_columns:
            orders = [f"{col} {dir.value}" for col, dir in self._order_by_columns]
            sql_parts.append(f"ORDER BY {', '.join(orders)}")

        # LIMIT/OFFSET
        if self._limit_count is not None:
            sql_parts.append(f"LIMIT {self._limit_count}")
        if self._offset_count is not None:
            sql_parts.append(f"OFFSET {self._offset_count}")

        main_sql = " ".join(sql_parts)
        
        if self._union_queries:
            union_sql_parts = [main_sql]
            for union_query in self._union_queries:
                union_sql, union_params = union_query.build()
                union_sql_parts.append(f"UNION {union_sql}")
                params.extend(union_params)
            main_sql = " ".join(union_sql_parts)

        return main_sql, tuple(params)

def select_from(table: str, *columns: str) -> QueryBuilder:
    if not columns:
        columns = ("*",)
    return QueryBuilder().select(*columns).from_table(table)

def count_from(table: str, column: str = "*") -> QueryBuilder:
    return QueryBuilder().select(f"COUNT({column})").from_table(table)

def exists_in(table: str, condition: str, *params: Any) -> QueryBuilder:
    return QueryBuilder().select("1").from_table(table).where(condition, *params)
