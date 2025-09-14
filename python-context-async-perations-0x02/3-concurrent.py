import asyncio
import aiosqlite
import sqlite3
from datetime import datetime

# First, let's set up a sample database with users
def setup_sample_database():
    """Create sample database with users of various ages"""
    with sqlite3.connect('async_users.db') as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL
            )
        ''')
        
        # Insert sample data with various ages including users over 40
        sample_users = [
            (1, 'John Doe', 'john@example.com', 30),
            (2, 'Jane Smith', 'jane@example.com', 22),
            (3, 'Bob Johnson', 'bob@example.com', 45),        # Over 40
            (4, 'Alice Brown', 'alice@example.com', 28),
            (5, 'Charlie Wilson', 'charlie@example.com', 19),
            (6, 'Diana Davis', 'diana@example.com', 52),       # Over 40
            (7, 'Eve Martinez', 'eve@example.com', 35),
            (8, 'Frank Miller', 'frank@example.com', 41),      # Over 40
            (9, 'Grace Taylor', 'grace@example.com', 26),
            (10, 'Henry Clark', 'henry@example.com', 48)       # Over 40
        ]
        
        cursor.executemany(
            'INSERT OR REPLACE INTO users (id, name, email, age) VALUES (?, ?, ?, ?)',
            sample_users
        )
        
        print("Async sample database created with user data")

# Asynchronous function to fetch all users
async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All user records from the database
    """
    print(" Starting async_fetch_users...")
    start_time = datetime.now()
    
    try:
        # Connect to database asynchronously
        async with aiosqlite.connect('async_users.db') as db:
            print("🔗 Connected to database for fetching all users")
            
            # Execute query asynchronously
            async with db.execute("SELECT * FROM users ORDER BY id") as cursor:
                results = await cursor.fetchall()
                
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f" async_fetch_users completed in {duration:.3f}s")
            print(f" Retrieved {len(results)} total users")
            
            return results
            
    except aiosqlite.Error as e:
        print(f" Database error in async_fetch_users: {e}")
        return []
    except Exception as e:
        print(f" Unexpected error in async_fetch_users: {e}")
        return []

# Asynchronous function to fetch users older than 40
async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: User records where age > 40
    """
    print(" Starting async_fetch_older_users...")
    start_time = datetime.now()
    
    try:
        # Connect to database asynchronously
        async with aiosqlite.connect('async_users.db') as db:
            print(" Connected to database for fetching older users")
            
            # Execute parameterized query asynchronously
            async with db.execute("SELECT * FROM users WHERE age > ? ORDER BY age DESC", (40,)) as cursor:
                results = await cursor.fetchall()
                
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f" async_fetch_older_users completed in {duration:.3f}s")
            print(f" Retrieved {len(results)} users older than 40")
            
            return results
            
    except aiosqlite.Error as e:
        print(f" Database error in async_fetch_older_users: {e}")
        return []
    except Exception as e:
        print(f" Unexpected error in async_fetch_older_users: {e}")
        return []

# Main concurrent execution function
async def fetch_concurrently():
    """
    Execute both async functions concurrently using asyncio.gather()
    
    Returns:
        tuple: Results from both async functions
    """
    print("\n Starting concurrent database operations...")
    print("=" * 60)
    
    overall_start = datetime.now()
    
    try:
        # Execute both queries concurrently using asyncio.gather()
        all_users, older_users = await asyncio.gather(
            async_fetch_users(),
            async_fetch_older_users()
        )
        
        overall_end = datetime.now()
        total_duration = (overall_end - overall_start).total_seconds()
        
        print("=" * 60)
        print(f" Both operations completed concurrently in {total_duration:.3f}s")
        
        # Display results
        print(f"\n RESULTS SUMMARY:")
        print(f" Total users found: {len(all_users)}")
        print(f" Users over 40: {len(older_users)}")
        
        # Display all users
        print(f"\n ALL USERS ({len(all_users)} records):")
        print("-" * 70)
        for user_id, name, email, age in all_users:
            print(f"ID: {user_id:2d} | Name: {name:<15} | Email: {email:<20} | Age: {age:2d}")
        
        # Display older users
        print(f"\n USERS OLDER THAN 40 ({len(older_users)} records):")
        print("-" * 70)
        if older_users:
            for user_id, name, email, age in older_users:
                print(f"ID: {user_id:2d} | Name: {name:<15} | Email: {email:<20} | Age: {age:2d}")
        else:
            print("No users found older than 40")
        
        return all_users, older_users
        
    except Exception as e:
        print(f" Error during concurrent execution: {e}")
        return [], []

# Additional demonstration: Show timing comparison
async def demonstrate_timing_benefits():
    """
    Demonstrate the performance benefits of concurrent execution
    """
    print("\n" + "=" * 60)
    print(" TIMING COMPARISON: Sequential vs Concurrent")
    print("=" * 60)
    
    # Sequential execution
    print("\nSEQUENTIAL EXECUTION:")
    sequential_start = datetime.now()
    
    users_sequential = await async_fetch_users()
    older_users_sequential = await async_fetch_older_users()
    
    sequential_end = datetime.now()
    sequential_time = (sequential_end - sequential_start).total_seconds()
    print(f" Sequential execution total time: {sequential_time:.3f}s")
    
    # Small delay to separate the tests
    await asyncio.sleep(0.1)
    
    # Concurrent execution
    print("\n CONCURRENT EXECUTION:")
    concurrent_start = datetime.now()
    
    users_concurrent, older_users_concurrent = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    concurrent_end = datetime.now()
    concurrent_time = (concurrent_end - concurrent_start).total_seconds()
    print(f"Concurrent execution total time: {concurrent_time:.3f}s")
    
    # Calculate improvement
    if sequential_time > 0:
        improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
        print(f"\n Performance improvement: {improvement:.1f}% faster with concurrent execution")

# Example of more complex concurrent operations
async def complex_concurrent_operations():
    """
    Show more complex concurrent database operations
    """
    print("\n" + "=" * 60)
    print("🔧 ADVANCED: Complex Concurrent Operations")
    print("=" * 60)
    
    async def get_user_count():
        async with aiosqlite.connect('async_users.db') as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    
    async def get_average_age():
        async with aiosqlite.connect('async_users.db') as db:
            async with db.execute("SELECT AVG(age) FROM users") as cursor:
                result = await cursor.fetchone()
                return round(result[0], 2) if result and result[0] else 0
    
    async def get_age_distribution():
        async with aiosqlite.connect('async_users.db') as db:
            async with db.execute("""
                SELECT 
                    CASE 
                        WHEN age < 30 THEN 'Under 30'
                        WHEN age BETWEEN 30 AND 40 THEN '30-40'
                        ELSE 'Over 40'
                    END as age_group,
                    COUNT(*) as count
                FROM users 
                GROUP BY age_group
            """) as cursor:
                results = await cursor.fetchall()
                return results
    
    # Execute all complex operations concurrently
    count, avg_age, distribution = await asyncio.gather(
        get_user_count(),
        get_average_age(),
        get_age_distribution()
    )
    
    print(f" User Statistics:")
    print(f"   Total Users: {count}")
    print(f"   Average Age: {avg_age}")
    print(f"   Age Distribution:")
    for age_group, group_count in distribution:
        print(f"     {age_group}: {group_count} users")

# Main execution function
def main():
    """Main function to run all async operations"""
    print("=" * 70)
    print(" AIOSQLITE ASYNC DATABASE OPERATIONS")
    print("=" * 70)
    
    # Setup database
    setup_sample_database()
    
    # Run the main concurrent fetch operation
    print(f"\n🎯 MAIN OBJECTIVE: Run fetch_concurrently()")
    asyncio.run(fetch_concurrently())
    
    # Additional demonstrations
    asyncio.run(demonstrate_timing_benefits())
    asyncio.run(complex_concurrent_operations())
    
    print(f"\n✨ All async operations completed successfully!")
    
    # Show the exact usage pattern
    print("\n" + "=" * 50)
    print(" USAGE PATTERN:")
    print("=" * 50)
    print("# The main functions as requested:")
    print("asyncio.run(fetch_concurrently())")
    print("\n# Inside fetch_concurrently():")
    print("all_users, older_users = await asyncio.gather(")
    print("    async_fetch_users(),")
    print("    async_fetch_older_users()")
    print(")")

if __name__ == "__main__":
    main()