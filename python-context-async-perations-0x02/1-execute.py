import sqlite3

class ExecuteQuery:
    """
    Custom context manager that executes a parameterized SQL query
    and handles the complete database operation lifecycle.
    """
    
    def __init__(self, database_path, query, parameters=None):
        """
        Initialize the query context manager.
        
        Args:
            database_path (str): Path to the SQLite database file
            query (str): SQL query to execute (with placeholders if needed)
            parameters (tuple/list): Parameters for the SQL query placeholders
        """
        self.database_path = database_path
        self.query = query
        self.parameters = parameters or ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Context entry - establish connection and execute the query.
        
        Returns:
            list: Query results from the executed SQL statement
        """
        print(f"🔗 Connecting to database: {self.database_path}")
        
        try:
            # Establish database connection
            self.connection = sqlite3.connect(self.database_path)
            self.cursor = self.connection.cursor()
            print(" Database connection established")
            
            # Execute the query with parameters
            print(f" Executing query: {self.query}")
            if self.parameters:
                print(f"🔧 With parameters: {self.parameters}")
                self.cursor.execute(self.query, self.parameters)
            else:
                self.cursor.execute(self.query)
            
            # Fetch and store results
            self.results = self.cursor.fetchall()
            print(f" Query executed successfully - {len(self.results)} rows retrieved")
            
            return self.results
            
        except sqlite3.Error as e:
            print(f" Database error during query execution: {e}")
            # Clean up on error
            if self.connection:
                self.connection.close()
            raise
        except Exception as e:
            print(f" Unexpected error: {e}")
            # Clean up on error
            if self.connection:
                self.connection.close()
            raise
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context cleanup - close cursor and database connection.
        
        Args:
            exc_type: Exception type (None if no error)
            exc_value: Exception instance (None if no error) 
            traceback: Traceback object (None if no error)
            
        Returns:
            bool: False to allow exceptions to propagate
        """
        try:
            # Close cursor if it exists
            if self.cursor:
                self.cursor.close()
                print(" Database cursor closed")
            
            # Handle connection cleanup
            if self.connection:
                if exc_type is None:
                    # No errors - commit any pending changes
                    self.connection.commit()
                    print(" Database changes committed")
                else:
                    # Error occurred - rollback changes
                    self.connection.rollback()
                    print(f"  Database changes rolled back due to: {exc_value}")
                
                # Always close the connection
                self.connection.close()
                print(" Database connection closed")
                
        except sqlite3.Error as e:
            print(f" Error during cleanup: {e}")
        
        # Return False to propagate any exceptions
        return False

# Setup function to create sample database with age column
def setup_sample_database_with_age():
    """Create sample database with users including age column"""
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        
        # Create users table with age column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data with ages
        sample_users = [
            (1, 'John Doe', 'john@example.com', 30),
            (2, 'Jane Smith', 'jane@example.com', 22),
            (3, 'Bob Johnson', 'bob@example.com', 35),
            (4, 'Alice Brown', 'alice@example.com', 28),
            (5, 'Charlie Wilson', 'charlie@example.com', 19),
            (6, 'Diana Davis', 'diana@example.com', 42)
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (id, name, email, age) VALUES (?, ?, ?, ?)',
            sample_users
        )
        
        print("🎯 Sample database created with age data")

# Main implementation using the ExecuteQuery context manager
def find_users_over_age():
    """Find users over age 25 using the ExecuteQuery context manager"""
    
    try:
        # Use the context manager to execute the parameterized query
        with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as results:
            
            print(f"\n Users over age 25 ({len(results)} found):")
            print("-" * 60)
            
            if results:
                # Display results with formatting
                for i, (user_id, name, email, age) in enumerate(results, 1):
                    print(f"{i}. ID: {user_id}, Name: {name}, Email: {email}, Age: {age}")
            else:
                print("No users found matching the criteria")
            
            return results
            
    except sqlite3.Error as e:
        print(f" Database operation failed: {e}")
        return None
    except Exception as e:
        print(f" Unexpected error occurred: {e}")
        return None

# Additional examples showing different query patterns
def example_different_queries():
    """Show various ways to use the ExecuteQuery context manager"""
    
    print("\n" + "=" * 50)
    print("🔍 EXAMPLE: Different Query Patterns")
    print("=" * 50)
    
    # Example 1: Query with different parameter
    print("\n1️ Finding users over age 30:")
    try:
        with ExecuteQuery('users.db', "SELECT name, age FROM users WHERE age > ?", (30,)) as results:
            for name, age in results:
                print(f"   • {name} (Age: {age})")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Example 2: Query without parameters
    print("\n2️ Getting all users (no parameters):")
    try:
        with ExecuteQuery('users.db', "SELECT COUNT(*) as total FROM users") as results:
            total = results[0][0] if results else 0
            print(f"    Total users in database: {total}")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Example 3: Query with multiple parameters
    print("\n3️ Finding users in age range (25-35):")
    try:
        with ExecuteQuery('users.db', 
                         "SELECT name, age FROM users WHERE age BETWEEN ? AND ?", 
                         (25, 35)) as results:
            for name, age in results:
                print(f"   • {name} (Age: {age})")
    except Exception as e:
        print(f"    Error: {e}")

# Example showing error handling
def example_error_handling():
    """Demonstrate error handling in ExecuteQuery context manager"""
    
    print("\n" + "=" * 50)
    print(" EXAMPLE: Error Handling")
    print("=" * 50)
    
    try:
        # Intentional error - table doesn't exist
        with ExecuteQuery('users.db', "SELECT * FROM non_existent_table WHERE age > ?", (25,)) as results:
            print(f"Results: {results}")
    except sqlite3.Error as e:
        print(f"Error properly handled: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("🗄️  ExecuteQuery Context Manager Implementation")
    print("=" * 70)
    
    # Setup database with age column
    setup_sample_database_with_age()
    
    # Main objective: Execute "SELECT * FROM users WHERE age > ?" with parameter 25
    print("\n" + "=" * 40)
    print(" PRIMARY OBJECTIVE: Find Users Over Age 25")
    print("=" * 40)
    users = find_users_over_age()
    
    # Additional examples
    example_different_queries()
    
    # Error handling demonstration
    example_error_handling()
    
    print("\n✨ ExecuteQuery context manager implementation complete!")
    
    # Show the exact usage pattern requested
    print("\n" + "=" * 40)
    print(" EXACT USAGE AS REQUESTED:")
    print("=" * 40)
    print("with ExecuteQuery('users.db', 'SELECT * FROM users WHERE age > ?', (25,)) as results:")
    print("    # Results are automatically available")
    print("    print(results)")