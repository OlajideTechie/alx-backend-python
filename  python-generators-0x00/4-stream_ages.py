#!/usr/bin/python3
"""
3-aggregate_age.py - Memory-efficient computation of average age using a generator
"""

import seed

# -----------------------------
# Generator to yield user ages one by one
# -----------------------------
def stream_user_ages():
    """
    Generator that yields ages from the user_data table one at a time.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data;")
    
    for row in cursor:  # Loop 1
        yield row['age']
    
    cursor.close()
    connection.close()


# -----------------------------
# Function to calculate average age
# -----------------------------
def compute_average_age():
    """
    Computes average age using the generator without loading all ages into memory.
    """
    total = 0
    count = 0
    
    for age in stream_user_ages():  # Loop 2
        total += age
        count += 1
    
    average = total / count if count > 0 else 0
    print(f"Average age of users: {average:.2f}")


# -----------------------------
# Execute computation
# -----------------------------
if __name__ == "__main__":
    compute_average_age()
