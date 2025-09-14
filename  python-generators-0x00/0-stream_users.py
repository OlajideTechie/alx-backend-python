#!/usr/bin/python3
"""
0-stream_users.py - Generator to stream rows from the user_data table
"""

import mysql.connector

def stream_users():
    """Generator that yields rows from user_data one by one"""
    try:
        # Connect to ALX_prodev database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # update with your MySQL username
            password='',      # update with your MySQL password
            database='ALX_prodev'
        )

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data;")

        # Single loop to fetch and yield rows one by one
        for row in cursor:
            yield row

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
