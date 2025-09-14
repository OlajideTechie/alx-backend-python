import time
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

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function a certain number of times if it raises an exception.
    
    Args:
        retries (int): Maximum number of retry attempts (default: 3)
        delay (int): Delay in seconds between retries (default: 2)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            # Try the function up to (retries + 1) times (original attempt + retries)
            for attempt in range(retries + 1):
                try:
                    # Attempt to execute the function
                    result = func(*args, **kwargs)
                    
                    # If successful and this wasn't the first attempt, log success
                    if attempt > 0:
                        print(f"Function succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # If this was the last attempt, don't retry
                    if attempt == retries:
                        print(f"Function failed after {retries + 1} attempts. Final error: {e}")
                        raise e
                    
                    # Log the failure and prepare to retry
                    print(f" Attempt {attempt + 1} failed: {e}")
                    print(f" Retrying in {delay} seconds... (attempt {attempt + 2} of {retries + 1})")
                    
                    # Wait before retrying
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)