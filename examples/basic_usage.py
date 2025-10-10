"""
Basic Usage Examples for Simple SQL Client Library

This module demonstrates the basic usage patterns of the SQL Client Library
with practical examples and best practices.
"""

import os
import sys
from datetime import datetime, date

# Add the parent directory to the path to import the library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqll import SQLClient, QueryBuilder
from sqll.query_builder import select_from, count_from, JoinType


def basic_crud_operations():
    """
    Demonstrate basic CRUD operations
    """
    print("=== Basic CRUD Operations ===")
    
    # Create a client (this will create the database file if it doesn't exist)
    client = SQLClient('example_basic.db')
    
    try:
        # Create a table
        client.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        print("✓ Table 'users' created successfully")
        
        # Insert a single user
        user_id = client.insert('users', {
            'username': 'johndoe',
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30
        })
        print(f"✓ Inserted user with ID: {user_id}")
        
        # Insert multiple users
        users_data = [
            {
                'username': 'janedoe',
                'email': 'jane.doe@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'age': 28
            },
            {
                'username': 'bobsmith',
                'email': 'bob.smith@example.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'age': 35
            },
            {
                'username': 'alicejohnson',
                'email': 'alice.johnson@example.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'age': 25
            }
        ]
        
        rows_inserted = client.insert_many('users', users_data)
        print(f"✓ Inserted {rows_inserted} users")
        
        # Select all users
        all_users = client.select('users')
        print(f"✓ Found {len(all_users)} users:")
        for user in all_users:
            print(f"  - {user['username']} ({user['email']}) - Age: {user['age']}")
        
        # Select users with conditions
        young_users = client.select('users', where={'age': [25, 28]}, order_by='age')
        print(f"✓ Found {len(young_users)} young users:")
        for user in young_users:
            print(f"  - {user['first_name']} {user['last_name']} (Age: {user['age']})")
        
        # Update a user
        rows_updated = client.update('users', {'age': 31}, {'username': 'johndoe'})
        print(f"✓ Updated {rows_updated} user(s)")
        
        # Count users
        total_users = client.count('users')
        active_users = client.count('users', where={'is_active': 1})
        print(f"✓ Total users: {total_users}, Active users: {active_users}")
        
        # Delete a user
        rows_deleted = client.delete('users', {'username': 'bobsmith'})
        print(f"✓ Deleted {rows_deleted} user(s)")
        
        # Final count
        final_count = client.count('users')
        print(f"✓ Final user count: {final_count}")
        
    finally:
        client.close()


def query_builder_examples():
    """
    Demonstrate QueryBuilder usage
    """
    print("\n=== QueryBuilder Examples ===")
    
    client = SQLClient('example_query.db')
    
    try:
        # Create sample tables
        client.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT
            )
        ''')
        
        client.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category_id INTEGER,
                stock_quantity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        
        # Insert sample data
        categories_data = [
            {'id': 1, 'name': 'Electronics', 'description': 'Electronic devices'},
            {'id': 2, 'name': 'Books', 'description': 'Books and literature'},
            {'id': 3, 'name': 'Clothing', 'description': 'Apparel and fashion'}
        ]
        client.insert_many('categories', categories_data)
        
        products_data = [
            {'name': 'Laptop', 'price': 999.99, 'category_id': 1, 'stock_quantity': 10},
            {'name': 'Smartphone', 'price': 699.99, 'category_id': 1, 'stock_quantity': 25},
            {'name': 'Python Book', 'price': 49.99, 'category_id': 2, 'stock_quantity': 50},
            {'name': 'T-Shirt', 'price': 19.99, 'category_id': 3, 'stock_quantity': 100},
            {'name': 'Jeans', 'price': 79.99, 'category_id': 3, 'stock_quantity': 30}
        ]
        client.insert_many('products', products_data)
        
        print("✓ Sample data inserted")
        
        # Simple select query
        query = select_from('products').where('price > ?', 50).order_by('price', 'DESC')
        expensive_products = client.execute_query(query)
        print(f"✓ Found {len(expensive_products)} expensive products:")
        for product in expensive_products:
            print(f"  - {product['name']}: ${product['price']:.2f}")
        
        # Complex query with joins
        query = (QueryBuilder()
            .select('p.name', 'p.price', 'c.name as category_name', 'p.stock_quantity')
            .from_table('products p')
            .join('categories c', 'p.category_id = c.id', JoinType.INNER)
            .where('p.stock_quantity > ?', 20)
            .order_by('p.price', 'DESC'))
        
        in_stock_products = client.execute_query(query)
        print(f"✓ Found {len(in_stock_products)} in-stock products:")
        for product in in_stock_products:
            print(f"  - {product['name']}: ${product['price']:.2f} ({product['category_name']}) - Stock: {product['stock_quantity']}")
        
        # Aggregation query
        query = (QueryBuilder()
            .select('c.name as category_name', 'COUNT(p.id) as product_count', 'AVG(p.price) as avg_price')
            .from_table('categories c')
            .left_join('products p', 'c.id = p.category_id')
            .group_by('c.id', 'c.name')
            .order_by('product_count', 'DESC'))
        
        category_stats = client.execute_query(query)
        print(f"✓ Category statistics:")
        for stat in category_stats:
            avg_price = f"${stat['avg_price']:.2f}" if stat['avg_price'] else "N/A"
            print(f"  - {stat['category_name']}: {stat['product_count']} products, Avg price: {avg_price}")
        
        # Count query
        count_query = count_from('products').where('price > ?', 100)
        expensive_count = client.execute_query(count_query)[0][0]
        print(f"✓ Products over $100: {expensive_count}")
        
    finally:
        client.close()


def transaction_examples():
    """
    Demonstrate transaction management
    """
    print("\n=== Transaction Examples ===")
    
    client = SQLClient('example_transaction.db')
    
    try:
        # Create tables
        client.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                balance DECIMAL(10,2) DEFAULT 0
            )
        ''')
        
        client.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                from_account_id INTEGER,
                to_account_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES accounts(id),
                FOREIGN KEY (to_account_id) REFERENCES accounts(id)
            )
        ''')
        
        # Insert sample accounts
        client.insert('accounts', {'name': 'Alice', 'balance': 1000.00})
        client.insert('accounts', {'name': 'Bob', 'balance': 500.00})
        
        print("✓ Sample accounts created")
        
        # Successful transaction
        try:
            with client.transaction():
                # Transfer $200 from Alice to Bob
                client.update('accounts', {'balance': 800.00}, {'name': 'Alice'})
                client.update('accounts', {'balance': 700.00}, {'name': 'Bob'})
                client.insert('transactions', {
                    'from_account_id': 1,
                    'to_account_id': 2,
                    'amount': 200.00,
                    'description': 'Transfer from Alice to Bob'
                })
                print("✓ Transfer transaction completed successfully")
        except Exception as e:
            print(f"✗ Transfer transaction failed: {e}")
        
        # Check final balances
        alice_balance = client.fetchone("SELECT balance FROM accounts WHERE name = 'Alice'")['balance']
        bob_balance = client.fetchone("SELECT balance FROM accounts WHERE name = 'Bob'")['balance']
        print(f"✓ Final balances - Alice: ${alice_balance:.2f}, Bob: ${bob_balance:.2f}")
        
        # Transaction that will fail (insufficient funds)
        try:
            with client.transaction():
                # Try to transfer $1000 from Bob to Alice (Bob only has $700)
                client.update('accounts', {'balance': bob_balance - 1000.00}, {'name': 'Bob'})
                client.update('accounts', {'balance': alice_balance + 1000.00}, {'name': 'Alice'})
                print("✗ This should not print - transaction should have failed")
        except Exception as e:
            print(f"✓ Transaction correctly failed: {e}")
        
        # Verify balances haven't changed
        alice_final = client.fetchone("SELECT balance FROM accounts WHERE name = 'Alice'")['balance']
        bob_final = client.fetchone("SELECT balance FROM accounts WHERE name = 'Bob'")['balance']
        print(f"✓ Balances unchanged after failed transaction - Alice: ${alice_final:.2f}, Bob: ${bob_final:.2f}")
        
    finally:
        client.close()


def advanced_query_examples():
    """
    Demonstrate advanced query patterns
    """
    print("\n=== Advanced Query Examples ===")
    
    client = SQLClient('example_advanced.db')
    
    try:
        # Create hierarchical table
        client.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                manager_id INTEGER,
                department VARCHAR(50),
                salary DECIMAL(10,2),
                FOREIGN KEY (manager_id) REFERENCES employees(id)
            )
        ''')
        
        # Insert hierarchical data
        employees_data = [
            {'id': 1, 'name': 'CEO', 'manager_id': None, 'department': 'Executive', 'salary': 200000.00},
            {'id': 2, 'name': 'CTO', 'manager_id': 1, 'department': 'Engineering', 'salary': 150000.00},
            {'id': 3, 'name': 'CFO', 'manager_id': 1, 'department': 'Finance', 'salary': 140000.00},
            {'id': 4, 'name': 'Senior Developer', 'manager_id': 2, 'department': 'Engineering', 'salary': 120000.00},
            {'id': 5, 'name': 'Junior Developer', 'manager_id': 4, 'department': 'Engineering', 'salary': 80000.00},
            {'id': 6, 'name': 'Accountant', 'manager_id': 3, 'department': 'Finance', 'salary': 70000.00}
        ]
        client.insert_many('employees', employees_data)
        
        print("✓ Employee hierarchy created")
        
        # Self-join to show manager relationships
        query = (QueryBuilder()
            .select('e.name as employee', 'm.name as manager', 'e.department', 'e.salary')
            .from_table('employees e')
            .left_join('employees m', 'e.manager_id = m.id')
            .order_by('e.salary', 'DESC'))
        
        hierarchy = client.execute_query(query)
        print("✓ Employee hierarchy:")
        for emp in hierarchy:
            manager = emp['manager'] or 'No Manager'
            print(f"  - {emp['employee']} (Manager: {manager}, Dept: {emp['department']}, Salary: ${emp['salary']:.2f})")
        
        # Department statistics
        query = (QueryBuilder()
            .select('department', 'COUNT(*) as employee_count', 'AVG(salary) as avg_salary', 'MAX(salary) as max_salary')
            .from_table('employees')
            .group_by('department')
            .order_by('avg_salary', 'DESC'))
        
        dept_stats = client.execute_query(query)
        print("✓ Department statistics:")
        for dept in dept_stats:
            print(f"  - {dept['department']}: {dept['employee_count']} employees, "
                  f"Avg: ${dept['avg_salary']:.2f}, Max: ${dept['max_salary']:.2f}")
        
        # Find employees earning more than their manager
        query = (QueryBuilder()
            .select('e.name as employee', 'e.salary as employee_salary', 
                   'm.name as manager', 'm.salary as manager_salary')
            .from_table('employees e')
            .join('employees m', 'e.manager_id = m.id')
            .where('e.salary > m.salary'))
        
        high_earners = client.execute_query(query)
        print(f"✓ Employees earning more than their manager: {len(high_earners)}")
        for emp in high_earners:
            print(f"  - {emp['employee']} (${emp['employee_salary']:.2f}) > {emp['manager']} (${emp['manager_salary']:.2f})")
        
    finally:
        client.close()


def main():
    """
    Run all examples
    """
    print("Simple SQL Client Library - Basic Usage Examples")
    print("=" * 60)
    
    try:
        basic_crud_operations()
        query_builder_examples()
        transaction_examples()
        advanced_query_examples()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()