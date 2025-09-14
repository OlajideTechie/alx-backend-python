#!/usr/bin/python3
"""
seed.py - Python script to setup MySQL database, table, populate data,
and provide a generator to stream rows one by one.
"""

import mysql.connector
import csv
import uuid
from mysql.connector import Error

# -----------------------------
# Connect to MySQL server
# -----------------------------
def connect_db():
    """Connect to the MySQL server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',        # update with your MySQL user
            password=''         # update with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# -----------------------------
# Create database ALX_prodev
# -----------------------------
def create_database(connection):
    """Create ALX_prodev database if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        cursor.close()
        print("Database ALX_prodev created successfully or already exists")
    except Error as e:
        print(f"Error creating database: {e}")

# -----------------------------
# Connect to ALX_prodev database
# -----------------------------
def connect_to_prodev():
    """Connect to the ALX_prodev database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # update with your MySQL password
            database='ALX_prodev'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# -----------------------------
# Create table user_data
# -----------------------------
def create_table(connection):
    """Create user_data table if it does not exist"""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX idx_user_id(user_id)
        );
        """
        cursor.execute(create_table_query)
        cursor.close()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

# -----------------------------
# Insert data from CSV
# -----------------------------
def insert_data(connection, csv_file):
    """Insert data from CSV into user_data table if it does not exist"""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Generate UUID for user_id if not present
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']
                
                # Insert only if email does not exist
                cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                        (user_id, name, email, age)
                    )
        connection.commit()
        cursor.close()
        print("Data inserted successfully")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
    except Error as e:
        print(f"Error inserting data: {e}")

# -----------------------------
# Generator to stream rows
# -----------------------------
def stream_user_data(connection):
    """Generator that yields rows from user_data one by one"""
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")
    row = cursor.fetchone()
    while row:
        yield row
        row = cursor.fetchone()
    cursor.close()