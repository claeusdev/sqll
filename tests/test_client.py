"""
Test suite for SQLClient class

This module contains comprehensive tests for the SQLClient class,
covering all major functionality including CRUD operations, transactions,
and error handling.
"""

import unittest
import tempfile
import os
import sqlite3
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqll import SQLClient, QueryBuilder
from sqll.exceptions import (
    SQLClientError, ConnectionError, QueryError, TransactionError, ValidationError
)


class TestSQLClient(unittest.TestCase):
    """Test cases for SQLClient class"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.client = SQLClient(self.temp_db.name)
        
        # Create test table
        self.client.execute('''
            CREATE TABLE IF NOT EXISTS test_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def tearDown(self):
        """Clean up test database"""
        self.client.close()
        os.unlink(self.temp_db.name)
    
    def test_connection_creation(self):
        """Test database connection creation"""
        self.assertIsNotNone(self.client)
        self.assertTrue(os.path.exists(self.temp_db.name))
    
    def test_table_creation(self):
        """Test table creation"""
        # Table should be created in setUp
        self.assertTrue(self.client.table_exists('test_users'))
        
        # Test table info
        table_info = self.client.get_table_info('test_users')
        self.assertGreater(len(table_info), 0)
        
        # Check specific columns
        column_names = [col['name'] for col in table_info]
        self.assertIn('id', column_names)
        self.assertIn('username', column_names)
        self.assertIn('email', column_names)
    
    def test_insert_single_record(self):
        """Test inserting a single record"""
        user_id = self.client.insert('test_users', {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25
        })
        
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)
        
        # Verify the record was inserted
        user = self.client.fetchone("SELECT * FROM test_users WHERE id = ?", (user_id,))
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['email'], 'test@example.com')
        self.assertEqual(user['age'], 25)
    
    def test_insert_many_records(self):
        """Test inserting multiple records"""
        users_data = [
            {'username': 'user1', 'email': 'user1@example.com', 'age': 20},
            {'username': 'user2', 'email': 'user2@example.com', 'age': 30},
            {'username': 'user3', 'email': 'user3@example.com', 'age': 40}
        ]
        
        rows_inserted = self.client.insert_many('test_users', users_data)
        self.assertEqual(rows_inserted, 3)
        
        # Verify all records were inserted
        all_users = self.client.select('test_users')
        self.assertEqual(len(all_users), 3)
    
    def test_select_with_conditions(self):
        """Test selecting records with conditions"""
        # Insert test data
        self.client.insert_many('test_users', [
            {'username': 'alice', 'email': 'alice@example.com', 'age': 25},
            {'username': 'bob', 'email': 'bob@example.com', 'age': 30},
            {'username': 'charlie', 'email': 'charlie@example.com', 'age': 35}
        ])
        
        # Test simple where condition
        young_users = self.client.select('test_users', where={'age': 25})
        self.assertEqual(len(young_users), 1)
        self.assertEqual(young_users[0]['username'], 'alice')
        
        # Test IN condition
        middle_aged = self.client.select('test_users', where={'age': [25, 30]})
        self.assertEqual(len(middle_aged), 2)
        
        # Test ordering
        ordered_users = self.client.select('test_users', order_by='age')
        self.assertEqual(ordered_users[0]['username'], 'alice')
        self.assertEqual(ordered_users[-1]['username'], 'charlie')
        
        # Test limit
        limited_users = self.client.select('test_users', limit=2)
        self.assertEqual(len(limited_users), 2)
    
    def test_update_records(self):
        """Test updating records"""
        # Insert test data
        user_id = self.client.insert('test_users', {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25
        })
        
        # Update the record
        rows_updated = self.client.update('test_users', 
                                        {'age': 26, 'email': 'newemail@example.com'}, 
                                        {'id': user_id})
        self.assertEqual(rows_updated, 1)
        
        # Verify the update
        updated_user = self.client.fetchone("SELECT * FROM test_users WHERE id = ?", (user_id,))
        self.assertEqual(updated_user['age'], 26)
        self.assertEqual(updated_user['email'], 'newemail@example.com')
    
    def test_delete_records(self):
        """Test deleting records"""
        # Insert test data
        self.client.insert_many('test_users', [
            {'username': 'user1', 'email': 'user1@example.com', 'age': 20},
            {'username': 'user2', 'email': 'user2@example.com', 'age': 30},
            {'username': 'user3', 'email': 'user3@example.com', 'age': 40}
        ])
        
        # Delete specific record
        rows_deleted = self.client.delete('test_users', {'username': 'user2'})
        self.assertEqual(rows_deleted, 1)
        
        # Verify deletion
        remaining_users = self.client.select('test_users')
        self.assertEqual(len(remaining_users), 2)
        
        # Verify correct user was deleted
        usernames = [user['username'] for user in remaining_users]
        self.assertNotIn('user2', usernames)
    
    def test_count_records(self):
        """Test counting records"""
        # Insert test data
        self.client.insert_many('test_users', [
            {'username': 'user1', 'email': 'user1@example.com', 'age': 20},
            {'username': 'user2', 'email': 'user2@example.com', 'age': 30},
            {'username': 'user3', 'email': 'user3@example.com', 'age': 40}
        ])
        
        # Test total count
        total_count = self.client.count('test_users')
        self.assertEqual(total_count, 3)
        
        # Test count with condition
        young_count = self.client.count('test_users', where={'age': 20})
        self.assertEqual(young_count, 1)
        
        # Test count with IN condition
        middle_aged_count = self.client.count('test_users', where={'age': [20, 30]})
        self.assertEqual(middle_aged_count, 2)
    
    def test_transaction_success(self):
        """Test successful transaction"""
        # Insert test data
        self.client.insert('test_users', {
            'username': 'alice',
            'email': 'alice@example.com',
            'age': 25
        })
        
        # Test successful transaction
        with self.client.transaction():
            self.client.insert('test_users', {
                'username': 'bob',
                'email': 'bob@example.com',
                'age': 30
            })
            self.client.update('test_users', {'age': 26}, {'username': 'alice'})
        
        # Verify both operations were committed
        all_users = self.client.select('test_users')
        self.assertEqual(len(all_users), 2)
        
        alice = self.client.fetchone("SELECT * FROM test_users WHERE username = 'alice'")
        self.assertEqual(alice['age'], 26)
    
    def test_transaction_rollback(self):
        """Test transaction rollback on error"""
        # Insert test data
        self.client.insert('test_users', {
            'username': 'alice',
            'email': 'alice@example.com',
            'age': 25
        })
        
        # Test transaction that will fail
        with self.assertRaises(Exception):
            with self.client.transaction():
                self.client.insert('test_users', {
                    'username': 'bob',
                    'email': 'bob@example.com',
                    'age': 30
                })
                # This will cause a constraint violation (duplicate username)
                self.client.insert('test_users', {
                    'username': 'alice',  # Duplicate username
                    'email': 'alice2@example.com',
                    'age': 35
                })
        
        # Verify only the original record exists (rollback worked)
        all_users = self.client.select('test_users')
        self.assertEqual(len(all_users), 1)
        self.assertEqual(all_users[0]['username'], 'alice')
    
    def test_query_builder_integration(self):
        """Test integration with QueryBuilder"""
        # Insert test data
        self.client.insert_many('test_users', [
            {'username': 'alice', 'email': 'alice@example.com', 'age': 25},
            {'username': 'bob', 'email': 'bob@example.com', 'age': 30},
            {'username': 'charlie', 'email': 'charlie@example.com', 'age': 35}
        ])
        
        # Test QueryBuilder integration
        query = (QueryBuilder()
                .select('username', 'age')
                .from_table('test_users')
                .where('age > ?', 25)
                .order_by('age', 'DESC'))
        
        results = self.client.execute_query(query)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['username'], 'charlie')
        self.assertEqual(results[1]['username'], 'bob')
    
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid table name
        with self.assertRaises(QueryError):
            self.client.select('nonexistent_table')
        
        # Test invalid SQL
        with self.assertRaises(QueryError):
            self.client.execute('INVALID SQL STATEMENT')
        
        # Test constraint violation
        self.client.insert('test_users', {
            'username': 'testuser',
            'email': 'test@example.com',
            'age': 25
        })
        
        with self.assertRaises(QueryError):
            self.client.insert('test_users', {
                'username': 'testuser',  # Duplicate username
                'email': 'test2@example.com',
                'age': 30
            })
    
    def test_validation_errors(self):
        """Test validation error handling"""
        # Test empty data for insert
        with self.assertRaises(ValidationError):
            self.client.insert('test_users', {})
        
        # Test empty where clause for update
        with self.assertRaises(ValidationError):
            self.client.update('test_users', {'age': 30}, {})
        
        # Test empty where clause for delete
        with self.assertRaises(ValidationError):
            self.client.delete('test_users', {})
    
    def test_table_operations(self):
        """Test table-related operations"""
        # Test table exists
        self.assertTrue(self.client.table_exists('test_users'))
        self.assertFalse(self.client.table_exists('nonexistent_table'))
        
        # Test get tables
        tables = self.client.get_tables()
        self.assertIn('test_users', tables)
        
        # Test get table info
        table_info = self.client.get_table_info('test_users')
        self.assertGreater(len(table_info), 0)
    
    def test_context_manager(self):
        """Test context manager functionality"""
        with SQLClient(self.temp_db.name) as client:
            # Test that client works within context
            self.assertTrue(client.table_exists('test_users'))
            
            # Insert a record
            user_id = client.insert('test_users', {
                'username': 'contextuser',
                'email': 'context@example.com',
                'age': 25
            })
            self.assertIsNotNone(user_id)
        
        # Client should be closed after context exit
        # (We can't easily test this without accessing private attributes)


class TestSQLClientEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.client = SQLClient(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        self.client.close()
        os.unlink(self.temp_db.name)
    
    def test_empty_database_operations(self):
        """Test operations on empty database"""
        # Test count on empty table
        count = self.client.count('test_users')
        self.assertEqual(count, 0)
        
        # Test select on empty table
        results = self.client.select('test_users')
        self.assertEqual(len(results), 0)
    
    def test_large_dataset(self):
        """Test with larger dataset"""
        # Create table
        self.client.execute('''
            CREATE TABLE IF NOT EXISTS large_test (
                id INTEGER PRIMARY KEY,
                value INTEGER,
                text_field TEXT
            )
        ''')
        
        # Insert large number of records
        data = [{'value': i, 'text_field': f'text_{i}'} for i in range(1000)]
        rows_inserted = self.client.insert_many('large_test', data)
        self.assertEqual(rows_inserted, 1000)
        
        # Test count
        count = self.client.count('large_test')
        self.assertEqual(count, 1000)
        
        # Test pagination
        page1 = self.client.select('large_test', limit=100, offset=0)
        self.assertEqual(len(page1), 100)
        
        page2 = self.client.select('large_test', limit=100, offset=100)
        self.assertEqual(len(page2), 100)
        self.assertNotEqual(page1[0]['id'], page2[0]['id'])
    
    def test_special_characters(self):
        """Test handling of special characters"""
        # Create table
        self.client.execute('''
            CREATE TABLE IF NOT EXISTS special_chars (
                id INTEGER PRIMARY KEY,
                text_field TEXT
            )
        ''')
        
        # Insert data with special characters
        special_texts = [
            "Text with 'quotes'",
            "Text with \"double quotes\"",
            "Text with ; semicolon",
            "Text with \n newline",
            "Text with \t tab",
            "Text with unicode: café, naïve, résumé"
        ]
        
        for i, text in enumerate(special_texts):
            self.client.insert('special_chars', {'text_field': text})
        
        # Verify all texts were stored correctly
        results = self.client.select('special_chars')
        self.assertEqual(len(results), len(special_texts))
        
        for i, result in enumerate(results):
            self.assertEqual(result['text_field'], special_texts[i])


if __name__ == '__main__':
    unittest.main()