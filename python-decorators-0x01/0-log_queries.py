import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query parameter from function arguments
        query = None
        
        # Check for query in keyword arguments first
        if 'query' in kwargs:
            query = kwargs['query']
        # Then check positional arguments (assume first argument is query)
        elif args and len(args) > 0:
            query = args[0]
        
        # Log the SQL query
        if query:
            print(f"[SQL LOG] Executing query: {query}")
        else:
            print("[SQL LOG] No query found to log")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")