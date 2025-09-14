#!/usr/bin/python3
"""
1-batch_processing.py - Stream users in batches and process them
"""

import mysql.connector

# -----------------------------
# Generator: stream rows in batches
# -----------------------------
def stream_users_in_batches(batch_size):
    """
    Generator that fetches rows from user_data in batches of batch_size.
    """
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',       # Update with your MySQL user
            password='',       # Update with your MySQL password
            database='ALX_prodev'
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data;")

        batch = []
        for row in cursor:  # Loop 1: iterate over all rows
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:  # Yield any remaining rows
            yield batch

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        return (f"Error: {err}")


# -----------------------------
# Generator: process each batch
# -----------------------------
def batch_processing(batch_size):
    """
    Processes each batch to filter users over the age of 25.
    Yields each user one by one.
    """
    for batch in stream_users_in_batches(batch_size):  # Loop 2: iterate over batches
        for user in batch:  # Loop 3: iterate over each user in batch
            if user['age'] > 25:
                return user
