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

def transactional(func):
    """
    Decorator that wraps database operations in a transaction.
    Commits on success, rolls back on error.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Begin transaction (SQLite auto-begins with first statement)
            # Execute the function
            result = func(conn, *args, **kwargs)
            
            # If we get here, no exception occurred - commit the transaction
            conn.commit()
            print("Transaction committed successfully")
            return result
            
        except Exception as e:
            # An error occurred - rollback the transaction
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            # Re-raise the exception
            raise
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
    print(f"Updated user {user_id} email to {new_email}")

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')