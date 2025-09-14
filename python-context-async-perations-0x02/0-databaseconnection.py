import sqlite3

class DatabaseConnection:
    """
    A context manager class that handles opening and closing database connections automatically.
    """
    
    def __init__(self, database_path):
        """
        Initialize the context manager with the database path.
        
        Args:
            database_path (str): Path to the SQLite database file
        """
        self.database_path = database_path
        self.connection = None
    
    def __enter__(self):
        """
        Enter the context - open the database connection.
        
        Returns:
            sqlite3.Connection: The database connection object
        """
        print(f"🔗 Opening database connection to: {self.database_path}")
        try:
            self.connection = sqlite3.connect(self.database_path)
            print("✅ Database connection established successfully")
            return self.connection
        except sqlite3.Error as e:
            print(f"❌ Failed to connect to database: {e}")
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context - close the database connection.
        
        Args:
            exc_type: Exception type (if any)
            exc_value: Exception value (if any)
            traceback: Traceback object (if any)
        
        Returns:
            bool: False to propagate exceptions, True to suppress them
        """
        if self.connection:
            try:
                if exc_type is None:
                    # No exception occurred, commit any pending transactions
                    self.connection.commit()
                    print(" Transaction committed successfully")
                else:
                    # An exception occurred, rollback any pending transactions
                    self.connection.rollback()
                    print(f" Transaction rolled back due to exception: {exc_value}")
                
                # Always close the connection
                self.connection.close()
                print(" Database connection closed")
                
            except sqlite3.Error as e:
                print(f" Error while closing database: {e}")
        
        # Return False to propagate any exceptions that occurred
        return False

# Example usage with SELECT query
def fetch_all_users():
    """Fetch all users using the context manager"""
    try:
        # Use the context manager with 'with' statement
        with DatabaseConnection('users.db') as conn:
            print("\nExecuting query: SELECT * FROM users")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            print(f"Query Results ({len(results)} rows):")
            print("-" * 50)
            
            if results:
                for i, row in enumerate(results, 1):
                    print(f"{i}. {row}")
            else:
                print("No users found in the database")
                
            return results
            
    except sqlite3.Error as e:
        print(f" Database error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage with error handling
def fetch_users_with_error_example():
    """Example showing error handling in context manager"""
    try:
        with DatabaseConnection('users.db') as conn:
            print("\n🔍 Executing query with potential error...")
            cursor = conn.cursor()
            # This might cause an error if table doesn't exist
            cursor.execute("SELECT * FROM non_existent_table")
            results = cursor.fetchall()
            return results
            
    except sqlite3.Error as e:
        print(f"Caught database error: {e}")

# Advanced usage example with multiple operations
def perform_multiple_operations():
    """Example showing multiple database operations in one context"""
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        
        print("\n🔧 Performing multiple database operations...")
        
        # Operation 1: Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Available tables: {[table[0] for table in tables]}")
        
        # Operation 2: Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"Total users: {count}")
        
        # Operation 3: Get all users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print(f"User details: {users}")
        
        return users

# Create a sample database and table for testing
def setup_sample_database():
    """Create a sample database with test data"""
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Insert sample data
        sample_users = [
            (1, 'John Doe', 'john@example.com'),
            (2, 'Jane Smith', 'jane@example.com'),
            (3, 'Bob Johnson', 'bob@example.com')
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (id, name, email) VALUES (?, ?, ?)',
            sample_users
        )
        
        print("🎯 Sample database created with test data")

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  Database Context Manager Implementation")
    print("=" * 60)
    
    # Initialize test database
    setup_sample_database()
    
    # Primary objective: fetch users using context manager
    print("\n" + "=" * 30)
    print("PRIMARY: Query All Users")
    print("=" * 30)
    users = fetch_all_users()
    
    # Additional demonstration: multiple operations
    print("\n" + "=" * 30)
    print("🔧 BONUS: Multiple Operations")
    print("=" * 30)
    perform_multiple_operations()
    
    # Error handling demonstration
    print("\n" + "=" * 30)
    print("DEMO: Error Handling")
    print("=" * 30)
    fetch_users_with_error_example()
    
    print("\n✨ Context manager demonstrations complete!")