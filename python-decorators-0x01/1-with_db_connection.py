import sqlite3 
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles database connection lifecycle.
    Opens a connection, passes it to the function, and ensures it's closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Call the original function with connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            # If there's an error, still close the connection
            print(f"Database error: {e}")
            raise
        finally:
            # Always close the connection
            conn.close()
    
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

#### Fetch user by ID with automatic connection handling 
user = get_user_by_id(user_id=1)
print(user)