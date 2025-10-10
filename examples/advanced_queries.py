"""
Advanced Query Examples for Simple SQL Client Library

This module demonstrates advanced query patterns, window functions,
recursive queries, and complex data analysis using the SQL Client Library.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the parent directory to the path to import the library
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqll import SQLClient, QueryBuilder
from sqll.query_builder import select_from, JoinType


def window_functions_example():
    """
    Demonstrate window functions for analytical queries
    """
    print("=== Window Functions Example ===")
    
    client = SQLClient('example_window.db')
    
    try:
        # Create sales data table
        client.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                sale_date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                salesperson VARCHAR(50) NOT NULL,
                region VARCHAR(50) NOT NULL
            )
        ''')
        
        # Insert sample sales data
        sales_data = [
            {'product_name': 'Laptop', 'sale_date': '2024-01-15', 'amount': 1299.99, 'salesperson': 'Alice', 'region': 'North'},
            {'product_name': 'Mouse', 'sale_date': '2024-01-16', 'amount': 29.99, 'salesperson': 'Bob', 'region': 'South'},
            {'product_name': 'Keyboard', 'sale_date': '2024-01-17', 'amount': 79.99, 'salesperson': 'Alice', 'region': 'North'},
            {'product_name': 'Monitor', 'sale_date': '2024-01-18', 'amount': 299.99, 'salesperson': 'Charlie', 'region': 'East'},
            {'product_name': 'Laptop', 'sale_date': '2024-01-19', 'amount': 1299.99, 'salesperson': 'Alice', 'region': 'North'},
            {'product_name': 'Mouse', 'sale_date': '2024-01-20', 'amount': 29.99, 'salesperson': 'Bob', 'region': 'South'},
            {'product_name': 'Headphones', 'sale_date': '2024-01-21', 'amount': 149.99, 'salesperson': 'Charlie', 'region': 'East'},
            {'product_name': 'Laptop', 'sale_date': '2024-01-22', 'amount': 1299.99, 'salesperson': 'Alice', 'region': 'North'},
            {'product_name': 'Tablet', 'sale_date': '2024-01-23', 'amount': 599.99, 'salesperson': 'Bob', 'region': 'South'},
            {'product_name': 'Phone', 'sale_date': '2024-01-24', 'amount': 799.99, 'salesperson': 'Charlie', 'region': 'East'}
        ]
        client.insert_many('sales', sales_data)
        
        print("✓ Sales data inserted")
        
        # ROW_NUMBER() - Rank sales by amount
        query = '''
            SELECT 
                product_name,
                sale_date,
                amount,
                salesperson,
                ROW_NUMBER() OVER (ORDER BY amount DESC) as rank_by_amount,
                ROW_NUMBER() OVER (PARTITION BY salesperson ORDER BY amount DESC) as rank_by_salesperson
            FROM sales
            ORDER BY amount DESC
        '''
        
        ranked_sales = client.fetchall(query)
        print("✓ Sales ranked by amount:")
        for sale in ranked_sales:
            print(f"  {sale['product_name']}: ${sale['amount']:.2f} - "
                  f"Overall Rank: {sale['rank_by_amount']}, Salesperson Rank: {sale['rank_by_salesperson']}")
        
        # Running totals and moving averages
        query = '''
            SELECT 
                sale_date,
                amount,
                SUM(amount) OVER (ORDER BY sale_date) as running_total,
                AVG(amount) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg_3day,
                COUNT(*) OVER (ORDER BY sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_count_3day
            FROM sales
            ORDER BY sale_date
        '''
        
        running_stats = client.fetchall(query)
        print("\n✓ Running totals and moving averages:")
        for stat in running_stats:
            print(f"  {stat['sale_date']}: ${stat['amount']:.2f} - "
                  f"Running Total: ${stat['running_total']:.2f}, "
                  f"3-Day Avg: ${stat['moving_avg_3day']:.2f} "
                  f"(Count: {stat['moving_count_3day']})")
        
        # LAG and LEAD for period-over-period analysis
        query = '''
            SELECT 
                sale_date,
                amount,
                LAG(amount, 1) OVER (ORDER BY sale_date) as previous_amount,
                LEAD(amount, 1) OVER (ORDER BY sale_date) as next_amount,
                ROUND(
                    (amount - LAG(amount, 1) OVER (ORDER BY sale_date)) / 
                    LAG(amount, 1) OVER (ORDER BY sale_date) * 100, 2
                ) as pct_change
            FROM sales
            ORDER BY sale_date
        '''
        
        period_analysis = client.fetchall(query)
        print("\n✓ Period-over-period analysis:")
        for analysis in period_analysis:
            pct_change = f"{analysis['pct_change']:.1f}%" if analysis['pct_change'] else "N/A"
            print(f"  {analysis['sale_date']}: ${analysis['amount']:.2f} - "
                  f"Change: {pct_change}")
        
    finally:
        client.close()


def recursive_queries_example():
    """
    Demonstrate recursive queries for hierarchical data
    """
    print("\n=== Recursive Queries Example ===")
    
    client = SQLClient('example_recursive.db')
    
    try:
        # Create hierarchical categories table
        client.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                parent_id INTEGER,
                level INTEGER DEFAULT 0,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        ''')
        
        # Insert hierarchical data
        categories_data = [
            {'id': 1, 'name': 'Electronics', 'parent_id': None, 'level': 0},
            {'id': 2, 'name': 'Computers', 'parent_id': 1, 'level': 1},
            {'id': 3, 'name': 'Laptops', 'parent_id': 2, 'level': 2},
            {'id': 4, 'name': 'Desktops', 'parent_id': 2, 'level': 2},
            {'id': 5, 'name': 'Smartphones', 'parent_id': 1, 'level': 1},
            {'id': 6, 'name': 'Books', 'parent_id': None, 'level': 0},
            {'id': 7, 'name': 'Fiction', 'parent_id': 6, 'level': 1},
            {'id': 8, 'name': 'Non-Fiction', 'parent_id': 6, 'level': 1},
            {'id': 9, 'name': 'Programming', 'parent_id': 8, 'level': 2},
            {'id': 10, 'name': 'Science', 'parent_id': 8, 'level': 2}
        ]
        client.insert_many('categories', categories_data)
        
        print("✓ Hierarchical categories created")
        
        # Recursive query to build category tree
        query = '''
            WITH RECURSIVE category_tree AS (
                -- Base case: root categories
                SELECT id, name, parent_id, level, 0 as depth, name as path
                FROM categories
                WHERE parent_id IS NULL
                
                UNION ALL
                
                -- Recursive case: children
                SELECT c.id, c.name, c.parent_id, c.level, ct.depth + 1, 
                       ct.path || ' > ' || c.name
                FROM categories c
                JOIN category_tree ct ON c.parent_id = ct.id
            )
            SELECT 
                REPEAT('  ', depth) || name as tree_structure,
                level,
                depth,
                path
            FROM category_tree
            ORDER BY level, depth, name
        '''
        
        tree_structure = client.fetchall(query)
        print("✓ Category tree structure:")
        for node in tree_structure:
            print(f"  {node['tree_structure']} (Level: {node['level']}, Depth: {node['depth']})")
        
        # Find all descendants of a specific category
        query = '''
            WITH RECURSIVE category_descendants AS (
                -- Base case: start with target category
                SELECT id, name, parent_id, level
                FROM categories
                WHERE id = 1  -- Electronics
                
                UNION ALL
                
                -- Recursive case: find children
                SELECT c.id, c.name, c.parent_id, c.level
                FROM categories c
                JOIN category_descendants cd ON c.parent_id = cd.id
            )
            SELECT name, level
            FROM category_descendants
            ORDER BY level, name
        '''
        
        descendants = client.fetchall(query)
        print(f"\n✓ Descendants of 'Electronics' category:")
        for desc in descendants:
            print(f"  Level {desc['level']}: {desc['name']}")
        
        # Find all ancestors of a specific category
        query = '''
            WITH RECURSIVE category_ancestors AS (
                -- Base case: start with target category
                SELECT id, name, parent_id, level
                FROM categories
                WHERE id = 3  -- Laptops
                
                UNION ALL
                
                -- Recursive case: find parents
                SELECT c.id, c.name, c.parent_id, c.level
                FROM categories c
                JOIN category_ancestors ca ON c.id = ca.parent_id
            )
            SELECT name, level
            FROM category_ancestors
            ORDER BY level
        '''
        
        ancestors = client.fetchall(query)
        print(f"\n✓ Ancestors of 'Laptops' category:")
        for anc in ancestors:
            print(f"  Level {anc['level']}: {anc['name']}")
        
    finally:
        client.close()


def complex_analytics_example():
    """
    Demonstrate complex analytical queries
    """
    print("\n=== Complex Analytics Example ===")
    
    client = SQLClient('example_analytics.db')
    
    try:
        # Create comprehensive sales data
        client.execute('''
            CREATE TABLE IF NOT EXISTS sales_fact (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                customer_id INTEGER,
                salesperson_id INTEGER,
                sale_date DATE,
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                total_amount DECIMAL(10,2),
                region VARCHAR(50),
                discount_percent DECIMAL(5,2) DEFAULT 0
            )
        ''')
        
        client.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                category VARCHAR(50),
                brand VARCHAR(50)
            )
        ''')
        
        client.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                segment VARCHAR(50),
                region VARCHAR(50)
            )
        ''')
        
        # Insert sample data
        products_data = [
            {'id': 1, 'name': 'Laptop Pro', 'category': 'Electronics', 'brand': 'TechCorp'},
            {'id': 2, 'name': 'Office Chair', 'category': 'Furniture', 'brand': 'ComfortCo'},
            {'id': 3, 'name': 'Coffee Maker', 'category': 'Appliances', 'brand': 'BrewMaster'},
            {'id': 4, 'name': 'Desk Lamp', 'category': 'Furniture', 'brand': 'LightCo'},
            {'id': 5, 'name': 'Wireless Mouse', 'category': 'Electronics', 'brand': 'TechCorp'}
        ]
        client.insert_many('products', products_data)
        
        customers_data = [
            {'id': 1, 'name': 'Acme Corp', 'segment': 'Enterprise', 'region': 'North'},
            {'id': 2, 'name': 'SmallBiz Inc', 'segment': 'SMB', 'region': 'South'},
            {'id': 3, 'name': 'StartupXYZ', 'segment': 'Startup', 'region': 'East'},
            {'id': 4, 'name': 'MegaCorp', 'segment': 'Enterprise', 'region': 'West'},
            {'id': 5, 'name': 'LocalShop', 'segment': 'SMB', 'region': 'North'}
        ]
        client.insert_many('customers', customers_data)
        
        # Generate sample sales data
        import random
        from datetime import datetime, timedelta
        
        sales_data = []
        base_date = datetime(2024, 1, 1)
        
        for i in range(100):
            sale_date = base_date + timedelta(days=random.randint(0, 30))
            product_id = random.randint(1, 5)
            customer_id = random.randint(1, 5)
            salesperson_id = random.randint(1, 3)
            quantity = random.randint(1, 5)
            unit_price = round(random.uniform(10, 1000), 2)
            total_amount = round(quantity * unit_price, 2)
            region = random.choice(['North', 'South', 'East', 'West'])
            discount = round(random.uniform(0, 20), 2)
            
            sales_data.append({
                'product_id': product_id,
                'customer_id': customer_id,
                'salesperson_id': salesperson_id,
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': total_amount,
                'region': region,
                'discount_percent': discount
            })
        
        client.insert_many('sales_fact', sales_data)
        
        print("✓ Sample sales data generated")
        
        # Top products by revenue
        query = '''
            SELECT 
                p.name as product_name,
                p.category,
                p.brand,
                COUNT(sf.id) as sales_count,
                SUM(sf.total_amount) as total_revenue,
                AVG(sf.total_amount) as avg_sale_amount,
                SUM(sf.quantity) as total_quantity
            FROM products p
            JOIN sales_fact sf ON p.id = sf.product_id
            GROUP BY p.id, p.name, p.category, p.brand
            ORDER BY total_revenue DESC
            LIMIT 5
        '''
        
        top_products = client.fetchall(query)
        print("✓ Top 5 products by revenue:")
        for product in top_products:
            print(f"  {product['product_name']} ({product['category']}) - "
                  f"Revenue: ${product['total_revenue']:.2f}, "
                  f"Sales: {product['sales_count']}, "
                  f"Avg: ${product['avg_sale_amount']:.2f}")
        
        # Customer segment analysis
        query = '''
            SELECT 
                c.segment,
                COUNT(DISTINCT c.id) as customer_count,
                COUNT(sf.id) as total_orders,
                SUM(sf.total_amount) as total_revenue,
                AVG(sf.total_amount) as avg_order_value,
                SUM(sf.quantity) as total_quantity
            FROM customers c
            JOIN sales_fact sf ON c.id = sf.customer_id
            GROUP BY c.segment
            ORDER BY total_revenue DESC
        '''
        
        segment_analysis = client.fetchall(query)
        print("\n✓ Customer segment analysis:")
        for segment in segment_analysis:
            print(f"  {segment['segment']}: {segment['customer_count']} customers, "
                  f"{segment['total_orders']} orders, "
                  f"${segment['total_revenue']:.2f} revenue, "
                  f"${segment['avg_order_value']:.2f} avg order")
        
        # Regional performance with window functions
        query = '''
            SELECT 
                region,
                COUNT(*) as order_count,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                RANK() OVER (ORDER BY SUM(total_amount) DESC) as revenue_rank,
                RANK() OVER (ORDER BY COUNT(*) DESC) as volume_rank
            FROM sales_fact
            GROUP BY region
            ORDER BY total_revenue DESC
        '''
        
        regional_performance = client.fetchall(query)
        print("\n✓ Regional performance:")
        for region in regional_performance:
            print(f"  {region['region']}: Rank #{region['revenue_rank']} by revenue, "
                  f"Rank #{region['volume_rank']} by volume - "
                  f"${region['total_revenue']:.2f} revenue, "
                  f"{region['order_count']} orders")
        
        # Monthly sales trend
        query = '''
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                COUNT(*) as order_count,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                SUM(quantity) as total_quantity
            FROM sales_fact
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month
        '''
        
        monthly_trends = client.fetchall(query)
        print("\n✓ Monthly sales trends:")
        for month in monthly_trends:
            print(f"  {month['month']}: {month['order_count']} orders, "
                  f"${month['total_revenue']:.2f} revenue, "
                  f"${month['avg_order_value']:.2f} avg order")
        
    finally:
        client.close()


def json_operations_example():
    """
    Demonstrate JSON operations with SQLite
    """
    print("\n=== JSON Operations Example ===")
    
    client = SQLClient('example_json.db')
    
    try:
        # Create table with JSON column
        client.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                profile_data JSON,
                preferences JSON,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert JSON data
        profile_data = {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001"
            },
            "interests": ["programming", "reading", "hiking"],
            "social_media": {
                "twitter": "@johndoe",
                "linkedin": "john-doe-dev"
            }
        }
        
        preferences = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "sms": False,
                "push": True
            },
            "language": "en",
            "timezone": "America/New_York"
        }
        
        metadata = {
            "last_login": "2024-01-15T10:30:00Z",
            "login_count": 42,
            "device_info": {
                "os": "Windows 11",
                "browser": "Chrome",
                "version": "120.0"
            }
        }
        
        import json
        
        client.insert('user_profiles', {
            'user_id': 1,
            'profile_data': json.dumps(profile_data),
            'preferences': json.dumps(preferences),
            'metadata': json.dumps(metadata)
        })
        
        print("✓ JSON data inserted")
        
        # Extract JSON fields
        query = '''
            SELECT 
                user_id,
                json_extract(profile_data, '$.first_name') as first_name,
                json_extract(profile_data, '$.last_name') as last_name,
                json_extract(profile_data, '$.address.city') as city,
                json_extract(profile_data, '$.address.state') as state,
                json_extract(preferences, '$.theme') as theme,
                json_extract(metadata, '$.login_count') as login_count
            FROM user_profiles
        '''
        
        extracted_data = client.fetchall(query)
        print("✓ Extracted JSON fields:")
        for data in extracted_data:
            print(f"  User {data['user_id']}: {data['first_name']} {data['last_name']} "
                  f"from {data['city']}, {data['state']} - "
                  f"Theme: {data['theme']}, Logins: {data['login_count']}")
        
        # Query JSON arrays
        query = '''
            SELECT 
                user_id,
                json_extract(profile_data, '$.interests') as interests,
                json_array_length(json_extract(profile_data, '$.interests')) as interest_count
            FROM user_profiles
        '''
        
        interests_data = client.fetchall(query)
        print("\n✓ JSON array analysis:")
        for data in interests_data:
            print(f"  User {data['user_id']}: {data['interest_count']} interests")
        
        # Update JSON data
        query = '''
            UPDATE user_profiles 
            SET profile_data = json_set(profile_data, '$.age', 31),
                metadata = json_set(metadata, '$.login_count', 
                    json_extract(metadata, '$.login_count') + 1)
            WHERE user_id = 1
        '''
        
        client.execute(query)
        print("✓ JSON data updated")
        
        # Complex JSON query with filtering
        query = '''
            SELECT 
                user_id,
                json_extract(profile_data, '$.first_name') as first_name,
                json_extract(profile_data, '$.age') as age,
                json_extract(preferences, '$.notifications.email') as email_notifications
            FROM user_profiles
            WHERE json_extract(profile_data, '$.age') > 25
            AND json_extract(preferences, '$.notifications.email') = 1
        '''
        
        filtered_data = client.fetchall(query)
        print("\n✓ Filtered JSON data (age > 25 and email notifications enabled):")
        for data in filtered_data:
            print(f"  User {data['user_id']}: {data['first_name']}, Age: {data['age']}")
        
    finally:
        client.close()


def main():
    """
    Run all advanced query examples
    """
    print("Simple SQL Client Library - Advanced Query Examples")
    print("=" * 60)
    
    try:
        window_functions_example()
        recursive_queries_example()
        complex_analytics_example()
        json_operations_example()
        
        print("\n" + "=" * 60)
        print("✓ All advanced examples completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()