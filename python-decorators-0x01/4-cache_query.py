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

query_cache = {}

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    Subsequent calls with the same query will return cached results.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query parameter to use as cache key
        cache_key = None
        
        # Check for query in keyword arguments
        if 'query' in kwargs:
            cache_key = kwargs['query']
        # Check positional arguments (assuming query is after conn)
        elif len(args) > 1:  # args[0] is conn, args[1] should be query
            cache_key = args[1]
        
        # If no query found, execute without caching
        if not cache_key:
            print("⚠️  No query found for caching, executing without cache")
            return func(*args, **kwargs)
        
        # Normalize the query for consistent caching (remove extra whitespace)
        normalized_query = ' '.join(cache_key.split()).lower()
        
        # Check if result is already cached
        if normalized_query in query_cache:
            print(f"🎯 Cache HIT: Using cached result for query: {cache_key[:50]}...")
            cached_data = query_cache[normalized_query]
            print(f"📊 Retrieved {len(cached_data['result'])} rows from cache")
            print(f"⏰ Original query executed at: {cached_data['timestamp']}")
            return cached_data['result']
        
        # Cache miss - execute the function
        print(f"💾 Cache MISS: Executing query: {cache_key[:50]}...")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Store result in cache with metadata
            query_cache[normalized_query] = {
                'result': result,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'execution_time': execution_time
            }
            
            print(f"✅ Query executed in {execution_time:.3f}s and cached")
            print(f"📊 Cached {len(result)} rows")
            
            return result
            
        except Exception as e:
            print(f"❌ Query failed, not caching: {e}")
            raise
    
    return wrapper

def clear_query_cache():
    """Utility function to clear the query cache"""
    global query_cache
    cache_size = len(query_cache)
    query_cache.clear()
    print(f"🗑️  Cleared cache ({cache_size} entries removed)")

def show_cache_stats():
    """Utility function to show cache statistics"""
    print(f"\n📈 Cache Statistics:")
    print(f"Total cached queries: {len(query_cache)}")
    for i, (query, data) in enumerate(query_cache.items(), 1):
        print(f"{i}. Query: {query[:60]}...")
        print(f"   Rows: {len(data['result'])}, Time: {data['timestamp']}")
    print()

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
print("=== First Query Execution ===")
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Result: {users}")

print("\n=== Second Query Execution (Same Query) ===")
#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Result: {users_again}")

print("\n=== Third Query Execution (Different Query) ===")
#### Different query will not use cache
specific_user = fetch_users_with_cache(query="SELECT * FROM users WHERE id = 1")
print(f"Result: {specific_user}")

print("\n=== Fourth Query Execution (Same as First) ===")
#### This should use cache again
users_third_time = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Result: {users_third_time}")

# Show cache statistics
show_cache_stats()

# Demonstrate cache clearing
# clear_query_cache()