# Detailed Implementation Outline: SQLL Critical Fixes and Simplifications

## Overview

This document provides a step-by-step guide for implementing all critical bug fixes and simplifications identified in the codebase analysis. Each change is broken down with specific file locations, code changes, and verification steps.

---

## Phase 1: Critical Bug Fixes (MUST DO FIRST)

### Task 1.1: Fix Class Import Inconsistency

**Problem**: Class is correctly named `SQLL` in `client.py` but `__init__.py` tries to import `SQLClient` which doesn't exist.

**Files to Modify**:
1. `sqll/__init__.py`
2. `examples/basic_usage.py`
3. `examples/advanced_queries.py`
4. `tests/test_client.py`

**Detailed Steps**:

#### Step 1.1.1: Fix Import in `__init__.py`
- **File**: `sqll/__init__.py`
- **Line**: 12
- **Current Code**:
  ```python
  from .client import SQLClient
  ```
- **Change To**:
  ```python
  from .client import SQLL
  ```
- **Reason**: Class is correctly named `SQLL`, need to import the actual class name
- **Impact**: Import will work correctly
- **Verification**: Import should work after fix

#### Step 1.1.2: Update Export in `__init__.py`
- **File**: `sqll/__init__.py`
- **Line**: 27
- **Current Code**:
  ```python
  __all__ = [
      'SQLClient',
      ...
  ]
  ```
- **Change To**:
  ```python
  __all__ = [
      'SQLL',
      ...
  ]
  ```
- **Reason**: Export the correct class name
- **Verification**: Check `__all__` exports `SQLL`

#### Step 1.1.3: Update Log Message in `client.py`
- **File**: `sqll/client.py`
- **Line**: 69
- **Current Code**:
  ```python
  self.logger.info(f"SQLLClient initialized for database: {db_path}")
  ```
- **Change To**:
  ```python
  self.logger.info(f"SQLL initialized for database: {db_path}")
  ```
- **Reason**: Fix typo in log message (remove extra "Client")
- **Verification**: Log message should show "SQLL initialized"

#### Step 1.1.4: Update Examples to Use SQLL
- **File**: `examples/basic_usage.py`
- **Line**: 15
- **Current Code**:
  ```python
  from sqll import SQLClient, QueryBuilder
  ```
- **Change To**:
  ```python
  from sqll import SQLL, QueryBuilder
  ```
- **Action**: Replace all `SQLClient` with `SQLL` in this file

#### Step 1.1.5: Update Examples to Use SQLL (Advanced)
- **File**: `examples/advanced_queries.py`
- **Line**: 15
- **Current Code**:
  ```python
  from sqll import SQLClient, QueryBuilder
  ```
- **Change To**:
  ```python
  from sqll import SQLL, QueryBuilder
  ```
- **Action**: Replace all `SQLClient` with `SQLL` in this file

#### Step 1.1.6: Update Tests to Use SQLL
- **File**: `tests/test_client.py`
- **Line**: 18
- **Current Code**:
  ```python
  from sqll import SQLClient, QueryBuilder
  ```
- **Change To**:
  ```python
  from sqll import SQLL, QueryBuilder
  ```
- **Action**: Replace all `SQLClient` with `SQLL` in this file

**Testing**:
```python
# Test import
from sqll import SQLL
client = SQLL('test.db')
assert client.__class__.__name__ == 'SQLL'
```

---

### Task 1.2: Fix Exception Naming Inconsistency

**Problem**: Exception class is correctly named `SQLLError` but `__init__.py` tries to import `SQLClientError` which doesn't exist.

**Files to Modify**:
1. `sqll/__init__.py`
2. `tests/test_client.py`

**Detailed Steps**:

#### Step 1.2.1: Fix Exception Import in `__init__.py`
- **File**: `sqll/__init__.py`
- **Line**: 15-21 (in the import section)
- **Current Code**:
  ```python
  from .exceptions import (
      SQLClientError,  # This doesn't exist!
      ConnectionError,
      QueryError,
      TransactionError,
      ValidationError
  )
  ```
- **Change To**:
  ```python
  from .exceptions import (
      SQLLError,
      ConnectionError,
      QueryError,
      TransactionError,
      ValidationError,
      ConfigurationError,
      MigrationError
  )
  ```
- **Reason**: Import the actual exception class name `SQLLError`
- **Impact**: All imports of `SQLLError` will work correctly

#### Step 1.2.2: Update `__all__` Export List
- **File**: `sqll/__init__.py`
- **Line**: 26-35
- **Current Code**:
  ```python
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
  ```
- **Change To**:
  ```python
  __all__ = [
      'SQLL',
      'ConnectionManager',
      'QueryBuilder',
      'SQLLError',
      'ConnectionError',
      'QueryError',
      'TransactionError',
      'ValidationError',
      'ConfigurationError',
      'MigrationError'
  ]
  ```
- **Reason**: Export correct class and exception names

#### Step 1.2.3: Update Test Imports
- **File**: `tests/test_client.py`
- **Line**: 19-21
- **Current Code**:
  ```python
  from sqll.exceptions import (
      SQLClientError, ConnectionError, QueryError, TransactionError, ValidationError
  )
  ```
- **Change To**:
  ```python
  from sqll.exceptions import (
      SQLLError, ConnectionError, QueryError, TransactionError, ValidationError
  )
  ```
- **Action**: Replace `SQLClientError` with `SQLLError` throughout test file

**Testing**:
```python
# Test exception imports
from sqll import SQLLError, ConnectionError, QueryError
assert SQLLError.__name__ == 'SQLLError'
```

---

### Task 1.3: Fix Exception Constructor Parameter Order

**Problem**: All exception subclasses pass parameters to parent in wrong order.

**Files to Modify**:
1. `sqll/exceptions.py`

**Detailed Steps**:

#### Step 1.3.1: Fix `ConnectionError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 52-60
- **Current Code**:
  ```python
  def __init__(self, message: str, db_path: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(details, message=message, error_code=ErrorCodes.connection_error)
      self.db_path = db_path
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, db_path: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.connection_error, details=details)
      self.db_path = db_path
  ```
- **Reason**: Base class expects `(message, error_code, details)` order
- **Verification**: Test exception creation and message display

#### Step 1.3.2: Fix `QueryError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 69-79
- **Current Code**:
  ```python
  def __init__(self, message: str, sql: Optional[str] = None, params: Optional[tuple] = None, details: Optional[Any] = None):
      super().__init__(details, message=message, error_code=ErrorCodes.query_error)
      self.sql = sql
      self.params = params
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, sql: Optional[str] = None, params: Optional[tuple] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.query_error, details=details)
      self.sql = sql
      self.params = params
  ```
- **Verification**: Test exception with SQL and params

#### Step 1.3.3: Fix `TransactionError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 89-97
- **Current Code**:
  ```python
  def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(details, message=message, error_code=ErrorCodes.transaction_error)
      self.operation = operation
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.transaction_error, details=details)
      self.operation = operation
  ```
- **Verification**: Test transaction error creation

#### Step 1.3.4: Fix `ValidationError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 107-117
- **Current Code**:
  ```python
  def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Any] = None):
      super().__init__(details, message=message, error_code=ErrorCodes.validation_error)
      self.field = field
      self.value = value
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.validation_error, details=details)
      self.field = field
      self.value = value
  ```
- **Verification**: Test validation error creation

#### Step 1.3.5: Fix `ConfigurationError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 126-135
- **Current Code**:
  ```python
  def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(details, error_code=ErrorCodes.configuration_error, message=message)
      self.config_key = config_key
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.configuration_error, details=details)
      self.config_key = config_key
  ```
- **Verification**: Test configuration error creation

#### Step 1.3.6: Fix `MigrationError.__init__`
- **File**: `sqll/exceptions.py`
- **Line**: 145-155
- **Current Code**:
  ```python
  def __init__(self, message: str, migration_name: Optional[str] = None, version: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(details, error_code=ErrorCodes.migration_error, message=message)
      self.migration_name = migration_name
      self.version = version
  ```
- **Change To**:
  ```python
  def __init__(self, message: str, migration_name: Optional[str] = None, version: Optional[str] = None, details: Optional[Any] = None):
      super().__init__(message, error_code=ErrorCodes.migration_error, details=details)
      self.migration_name = migration_name
      self.version = version
  ```
- **Verification**: Test migration error creation

**Testing**:
```python
# Test each exception type
from sqll import SQLLError, ConnectionError, QueryError, ValidationError

# Test ConnectionError
try:
    raise ConnectionError("Test error", db_path="test.db")
except ConnectionError as e:
    assert str(e) == "[ErrorCodes.connection_error]: Test error"
    assert e.db_path == "test.db"

# Test QueryError
try:
    raise QueryError("Query failed", sql="SELECT * FROM users", params=(1,))
except QueryError as e:
    assert e.sql == "SELECT * FROM users"
    assert e.params == (1,)

# Test ValidationError
try:
    raise ValidationError("Invalid input", field="username", value="")
except ValidationError as e:
    assert e.field == "username"
    assert e.value == ""
```

---

### Task 1.4: Fix Convenience Functions Parameter Order

**Problem**: Convenience functions may have parameter order issues.

**Files to Modify**:
1. `sqll/exceptions.py`

**Detailed Steps**:

#### Step 1.4.1: Verify `raise_connection_error`
- **File**: `sqll/exceptions.py`
- **Line**: 160-171
- **Current Code**: Check parameter order
- **Action**: Verify it creates exception correctly with fixed constructor
- **Change**: Should work after fixing ConnectionError constructor

#### Step 1.4.2: Verify `raise_query_error`
- **File**: `sqll/exceptions.py`
- **Line**: 174-187
- **Current Code**: Check parameter order
- **Action**: Verify it creates exception correctly with fixed constructor
- **Change**: Should work after fixing QueryError constructor

#### Step 1.4.3: Verify `raise_validation_error`
- **File**: `sqll/exceptions.py`
- **Line**: 190-203
- **Current Code**: Check parameter order
- **Action**: Verify it creates exception correctly with fixed constructor
- **Change**: Should work after fixing ValidationError constructor

**Testing**:
```python
from sqll.exceptions import raise_connection_error, raise_query_error, raise_validation_error
import sqlite3

# Test raise_connection_error
try:
    raise_connection_error("test.db", sqlite3.Error("Connection failed"))
except ConnectionError as e:
    assert "test.db" in str(e)
    assert e.db_path == "test.db"
```

---

## Phase 2: Fix Test Imports

### Task 2.1: Update Test File Imports

**Files to Modify**:
1. `tests/test_client.py`

**Detailed Steps**:

#### Step 2.1.1: Fix Import Statement
- **File**: `tests/test_client.py`
- **Line**: 18-21
- **Current Code**:
  ```python
  from sqll import SQLClient, QueryBuilder
  from sqll.exceptions import (
      SQLClientError, ConnectionError, QueryError, TransactionError, ValidationError
  )
  ```
- **Change To**:
  ```python
  from sqll import SQLL, QueryBuilder
  from sqll.exceptions import (
      SQLLError, ConnectionError, QueryError, TransactionError, ValidationError
  )
  ```
- **Action**: Replace all `SQLClient` with `SQLL` and `SQLClientError` with `SQLLError` throughout test file
- **Verification**: Run tests to ensure they pass

**Testing**:
```bash
# Run test suite
python -m pytest tests/test_client.py -v
```

---

## Phase 3: Simplifications

### Task 3.1: Remove Unused ConnectionState Enum

**Files to Modify**:
1. `sqll/connection.py`

**Detailed Steps**:

#### Step 3.1.1: Remove Enum Definition
- **File**: `sqll/connection.py`
- **Line**: 20-25
- **Current Code**:
  ```python
  class ConnectionState(Enum):
      """Enumeration of possible connection states"""
      CLOSED = "closed"
      OPEN = "open"
      TRANSACTION = "transaction"
      ERROR = "error"
  ```
- **Change To**: Delete entire enum (not used anywhere)
- **Reason**: Dead code, never referenced
- **Verification**: Search codebase for `ConnectionState` references (should find none)

**Testing**:
```bash
# Verify no references exist
grep -r "ConnectionState" sqll/
# Should return no results
```

---

### Task 3.2: Simplify Connection Manager Selection

**Files to Modify**:
1. `sqll/client.py`

**Detailed Steps**:

#### Step 3.2.1: Simplify Connection Manager Initialization
- **File**: `sqll/client.py`
- **Line**: 51-67
- **Current Code**:
  ```python
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
  ```
- **Change To**:
  ```python
  # Initialize connection manager
  # Use simple manager by default for simplicity
  # Pooling available when explicitly enabled
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
      # Simple manager: create connection per operation
      self.connection_manager = SimpleConnectionManager(db_path, **kwargs)
  ```
- **Reason**: Add clarifying comments, no logic change
- **Impact**: Better code readability

**Testing**:
```python
# Test both connection manager types
client1 = SQLL('test1.db', use_connection_pool=False)
client2 = SQLL('test2.db', use_connection_pool=True)
assert isinstance(client1.connection_manager, SimpleConnectionManager)
assert isinstance(client2.connection_manager, ConnectionManager)
```

---

### Task 3.3: Simplify ClientConfig Defaults

**Files to Modify**:
1. `sqll/client.py`

**Detailed Steps**:

#### Step 3.3.1: Review and Document Defaults
- **File**: `sqll/client.py`
- **Line**: 17-32
- **Current Code**: Review all defaults
- **Action**: Add comments explaining why each default is chosen
- **Change**: Add documentation, consider if defaults are optimal

**Suggested Changes**:
```python
@dataclass
class ClientConfig:
    """Configuration for SQLL"""
    db_path: str
    timeout: float = 30.0  # SQLite connection timeout in seconds
    check_same_thread: bool = False  # Allow multi-threaded access
    isolation_level: Optional[str] = None  # None = autocommit mode
    foreign_keys: bool = True  # Enable foreign key constraints
    journal_mode: str = "WAL"  # Write-Ahead Logging for better concurrency
    synchronous: str = "NORMAL"  # Balance between safety and performance
    cache_size: int = -2000  # 2MB cache (negative = KB, positive = pages)
    temp_store: str = "MEMORY"  # Store temp tables in memory
    mmap_size: int = 134217728  # 128MB memory-mapped I/O
    use_connection_pool: bool = True  # Use connection pooling
    max_connections: int = 10  # Max connections in pool
    enable_logging: bool = True  # Enable logging
    log_level: int = logging.INFO  # Logging level
```

**Testing**: Verify defaults work correctly

---

## Phase 4: Security Improvements

### Task 4.1: Add Input Validation for Table/Column Names

**Files to Modify**:
1. `sqll/client.py`
2. `sqll/query_builder.py`

**Detailed Steps**:

#### Step 4.1.1: Create Validation Utility Function
- **File**: `sqll/client.py`
- **Location**: Add after imports, before ClientConfig
- **New Code**:
  ```python
  import re
  
  def _validate_identifier(name: str, identifier_type: str = "identifier") -> None:
      """
      Validate SQL identifier (table/column name) to prevent SQL injection.
      
      Args:
          name: Identifier to validate
          identifier_type: Type of identifier for error messages
          
      Raises:
          ValidationError: If identifier is invalid
      """
      if not name:
          raise ValidationError(
              f"{identifier_type.capitalize()} name cannot be empty",
              field=identifier_type,
              value=name
          )
      
      # SQLite identifiers: letters, digits, underscore, and $, but not starting with digit
      # Also allow dots for qualified names (e.g., "schema.table")
      pattern = r'^[a-zA-Z_$][a-zA-Z0-9_$.]*$|^[a-zA-Z_$][a-zA-Z0-9_$.]*\.[a-zA-Z_$][a-zA-Z0-9_$.]*$'
      
      if not re.match(pattern, name):
          raise ValidationError(
              f"Invalid {identifier_type} name: '{name}'. "
              f"Must start with letter/underscore and contain only letters, digits, underscores, and dots.",
              field=identifier_type,
              value=name
          )
  ```

#### Step 4.1.2: Add Validation to CRUD Methods
- **File**: `sqll/client.py`
- **Methods to Update**: `select`, `insert`, `update`, `delete`, `count`
- **Example for `select` method**:
  ```python
  def select(self, table: str, ...):
      _validate_identifier(table, "table")
      # ... rest of method
  ```
- **Example for `insert` method**:
  ```python
  def insert(self, table: str, data: Dict[str, Any]) -> int:
      _validate_identifier(table, "table")
      for column in data.keys():
          _validate_identifier(column, "column")
      # ... rest of method
  ```

#### Step 4.1.3: Add Validation to Query Builder
- **File**: `sqll/query_builder.py`
- **Methods to Update**: `from_table`, `join`, `where`, `group_by`, `order_by`
- **Example for `from_table`**:
  ```python
  def from_table(self, table: str, alias: Optional[str] = None) -> 'QueryBuilder':
      _validate_identifier(table, "table")
      if alias:
          _validate_identifier(alias, "alias")
      # ... rest of method
  ```

**Testing**:
```python
from sqll import SQLL, ValidationError

client = SQLL('test.db')

# Test invalid table names
try:
    client.select('users; DROP TABLE users--')
except ValidationError as e:
    assert "Invalid table name" in str(e)

# Test valid table names
client.select('users')  # Should work
client.select('users_123')  # Should work
client.select('schema.users')  # Should work
```

---

### Task 4.2: Sanitize SQL Parameters

**Files to Modify**:
1. `sqll/client.py`
2. `sqll/query_builder.py`

**Detailed Steps**:

#### Step 4.2.1: Ensure Parameterized Queries
- **File**: `sqll/client.py`
- **Action**: Verify all SQL uses parameterized queries (already done, but document)
- **Add Comments**: Document that all queries use parameterized statements

#### Step 4.2.2: Add Parameter Type Validation
- **File**: `sqll/client.py`
- **New Function**:
  ```python
  def _validate_sql_params(params: Optional[Tuple[Any, ...]]) -> None:
      """
      Validate SQL parameters are safe types.
      
      Args:
          params: Parameters tuple to validate
      """
      if params is None:
          return
      
      allowed_types = (str, int, float, bool, type(None), bytes, datetime, date)
      for param in params:
          if not isinstance(param, allowed_types):
              raise ValidationError(
                  f"Invalid parameter type: {type(param).__name__}. "
                  f"Allowed types: {', '.join(t.__name__ for t in allowed_types)}",
                  field="params",
                  value=type(param).__name__
              )
  ```

**Testing**:
```python
# Test parameter validation
try:
    client.execute("SELECT * FROM users WHERE id = ?", (lambda x: x,))
except ValidationError as e:
    assert "Invalid parameter type" in str(e)
```

---

## Phase 5: Code Quality Improvements

### Task 5.1: Improve Error Messages

**Files to Modify**:
1. `sqll/exceptions.py`
2. `sqll/client.py`

**Detailed Steps**:

#### Step 5.1.1: Enhance Exception Messages
- **File**: `sqll/exceptions.py`
- **Action**: Review all exception messages, make them more descriptive
- **Example**: Include more context in error messages

#### Step 5.1.2: Add Context to Error Messages
- **File**: `sqll/client.py`
- **Action**: Include more context when raising exceptions
- **Example**:
  ```python
  except sqlite3.Error as e:
      self.logger.error(f"Query execution failed: {e}")
      raise_query_error(
          sql,
          params,
          e,
          additional_context=f"Table: {table_name}" if 'table_name' in locals() else None
      )
  ```

---

### Task 5.2: Add Missing Type Hints

**Files to Modify**:
1. All files in `sqll/`

**Detailed Steps**:

#### Step 5.2.1: Audit Type Hints
- **Action**: Review all methods, add missing type hints
- **Focus Areas**: Return types, complex parameter types

#### Step 5.2.2: Add Return Type Hints
- **Example**: Methods missing return types
- **File**: `sqll/client.py`
- **Methods**: Ensure all public methods have return type hints

---

### Task 5.3: Improve Documentation

**Files to Modify**:
1. All files in `sqll/`

**Detailed Steps**:

#### Step 5.3.1: Add/Update Docstrings
- **Action**: Ensure all public methods have comprehensive docstrings
- **Format**: Google-style docstrings
- **Include**: Args, Returns, Raises, Examples

#### Step 5.3.2: Add Module-Level Docstrings
- **Action**: Add docstrings to each module explaining its purpose

---

## Phase 6: Testing and Verification

### Task 6.1: Run Test Suite

**Steps**:
1. Run all existing tests
2. Fix any failing tests
3. Add tests for new validation logic
4. Add tests for fixed exceptions

**Commands**:
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=sqll --cov-report=html

# Run specific test file
python -m pytest tests/test_client.py -v
```

---

### Task 6.2: Test Examples

**Steps**:
1. Run basic usage example
2. Run advanced queries example
3. Verify all examples work correctly

**Commands**:
```bash
python examples/basic_usage.py
python examples/advanced_queries.py
```

---

### Task 6.3: Manual Testing Checklist

**Checklist**:
- [ ] Import library successfully
- [ ] Create client instance
- [ ] Execute raw SQL
- [ ] Perform CRUD operations
- [ ] Use query builder
- [ ] Test transactions
- [ ] Test error handling
- [ ] Test input validation
- [ ] Test with invalid inputs (should raise ValidationError)

---

## Phase 7: Documentation Updates

### Task 7.1: Update README

**Files to Modify**:
1. `README.md`

**Steps**:
1. Verify all code examples work
2. Update any outdated examples
3. Add troubleshooting section
4. Add security notes about input validation

---

### Task 7.2: Create CHANGELOG

**Files to Create**:
1. `CHANGELOG.md`

**Content**:
- List all changes made
- Breaking changes (if any)
- New features
- Bug fixes
- Security improvements

---

## Implementation Order Summary

1. **Phase 1**: Critical Bug Fixes (DO FIRST)
   - Task 1.1: Fix class naming
   - Task 1.2: Fix exception naming
   - Task 1.3: Fix exception constructors
   - Task 1.4: Verify convenience functions

2. **Phase 2**: Fix Tests
   - Task 2.1: Update test imports

3. **Phase 3**: Simplifications
   - Task 3.1: Remove unused code
   - Task 3.2: Simplify connection manager
   - Task 3.3: Document defaults

4. **Phase 4**: Security
   - Task 4.1: Add input validation
   - Task 4.2: Sanitize parameters

5. **Phase 5**: Code Quality
   - Task 5.1: Improve error messages
   - Task 5.2: Add type hints
   - Task 5.3: Improve documentation

6. **Phase 6**: Testing
   - Task 6.1: Run test suite
   - Task 6.2: Test examples
   - Task 6.3: Manual testing

7. **Phase 7**: Documentation
   - Task 7.1: Update README
   - Task 7.2: Create CHANGELOG

---

## Verification Checklist

After each phase, verify:

- [ ] Code compiles without errors
- [ ] All imports work correctly
- [ ] Tests pass (or are fixed)
- [ ] Examples run successfully
- [ ] No regressions introduced
- [ ] Code follows project style
- [ ] Documentation is updated

---

## Rollback Plan

If issues arise:

1. **Git**: Use `git checkout` to revert specific files
2. **Incremental**: Each phase is independent, can revert individually
3. **Testing**: Run tests after each phase to catch issues early

---

## Notes

- Test after each major change
- Commit after each completed phase
- Document any deviations from this plan
- Update this document if better approaches are found
