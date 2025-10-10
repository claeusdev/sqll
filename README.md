# SQLL: A very simple SQL client for python.

SQLL is a simple, yet powerful SQL client library for Python using SQLite. The library provides a clean, intuitive interface for database operations while maintaining the flexibility and power of raw SQL.

## Project Structure

```
project/
├── README.md                    # This file
├── sqll/                       # Main library package
│   ├── __init__.py
│   ├── client.py               # Main SQLClient class
│   ├── connection.py           # Connection management
│   ├── query_builder.py        # Query builder utilities
│   ├── exceptions.py           # Custom exceptions
│   └── utils.py                # Utility functions
├── examples/                   # Usage examples
│   ├── basic_usage.py
│   ├── advanced_queries.py
│   └── web_app_example.py
├── tests/                      # Test suite
│   ├── test_client.py
│   ├── test_connection.py
│   └── test_query_builder.py
├── requirements.txt            # Dependencies
└── setup.py                   # Package setup
```

## Features

### Core Features
- **Simple Connection Management**: Easy database connection with automatic cleanup
- **Query Builder**: Fluent interface for building complex queries
- **Transaction Support**: Full transaction management with context managers
- **Type Safety**: Comprehensive type hints for better IDE support
- **Error Handling**: Custom exceptions with detailed error messages
- **Connection Pooling**: Efficient connection management for concurrent access

### Advanced Features
- **JSON Support**: Native support for SQLite's JSON functions
- **Migration System**: Simple database schema migration support
- **Logging**: Comprehensive logging for debugging and monitoring
- **Performance Monitoring**: Built-in query performance tracking
- **Async Support**: Optional async/await support for concurrent operations

## Quick Start

### Installation

```bash
# Clone or download the project
cd sql/project

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Basic Usage

```python
from sqll import SQLClient

# Create a client
client = SQLClient('example.db')

# Create a table
client.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
''')

# Insert data
client.insert('users', {'name': 'John Doe', 'email': 'john@example.com'})

# Query data
users = client.select('users', where={'name': 'John Doe'})
print(users)

# Update data
client.update('users', {'name': 'Jane Doe'}, where={'email': 'john@example.com'})

# Delete data
client.delete('users', where={'email': 'jane@example.com'})

# Close connection
client.close()
```

### Advanced Usage

```python
from sqll import SQLClient
from sqll.query_builder import QueryBuilder

# Using query builder
client = SQLClient('example.db')

# Complex query with joins
query = (QueryBuilder()
    .select('u.name', 'u.email', 'p.title')
    .from_table('users u')
    .join('posts p', 'u.id = p.user_id')
    .where('u.active = ?', True)
    .order_by('u.name')
    .limit(10))

results = client.execute_query(query)
```

## API Reference

### SQLClient Class

The main class for database operations.

#### Methods

- `__init__(db_path: str, **kwargs)`: Initialize client with database path
- `execute(sql: str, params: tuple = None)`: Execute raw SQL
- `select(table: str, **kwargs)`: Select data from table
- `insert(table: str, data: dict)`: Insert data into table
- `update(table: str, data: dict, where: dict)`: Update table data
- `delete(table: str, where: dict)`: Delete data from table
- `transaction()`: Context manager for transactions
- `close()`: Close database connection

### QueryBuilder Class

Fluent interface for building SQL queries.

#### Methods

- `select(*columns)`: Specify columns to select
- `from_table(table: str)`: Specify main table
- `join(table: str, condition: str)`: Add JOIN clause
- `where(condition: str, *params)`: Add WHERE clause
- `order_by(column: str, direction: str = 'ASC')`: Add ORDER BY clause
- `limit(count: int)`: Add LIMIT clause
- `build()`: Build final SQL query

## Examples

### Example 1: Basic CRUD Operations

```python
from sqll import SQLClient

client = SQLClient('blog.db')

# Create tables
client.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        author_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Insert posts
client.insert('posts', {
    'title': 'Getting Started with Python',
    'content': 'Python is a great programming language...',
    'author_id': 1
})

# Query posts
posts = client.select('posts', where={'author_id': 1})
for post in posts:
    print(f"Title: {post['title']}")
```

### Example 2: Complex Queries with Joins

```python
# Complex query with multiple joins
query = (QueryBuilder()
    .select('p.title', 'p.created_at', 'u.name as author')
    .from_table('posts p')
    .join('users u', 'p.author_id = u.id')
    .join('categories c', 'p.category_id = c.id')
    .where('c.name = ?', 'Python')
    .order_by('p.created_at DESC')
    .limit(5))

results = client.execute_query(query)
```

### Example 3: Transaction Management

```python
# Using transactions
with client.transaction():
    client.insert('users', {'name': 'Alice', 'email': 'alice@example.com'})
    client.insert('posts', {'title': 'Hello World', 'author_id': 1})
    # Both operations will be committed together
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=simple_sql_client

# Run specific test file
python -m pytest tests/test_client.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Future Enhancements

- [ ] Support for other database backends (PostgreSQL, MySQL)
- [ ] Advanced query optimization
- [ ] Database introspection tools
- [ ] CLI interface
- [ ] Web dashboard for database management
- [ ] Integration with popular ORMs
- [ ] Real-time database monitoring