#!/usr/bin/python3
"""
2-lazy_paginate.py - Lazily fetch paginated data from user_data table using a generator
"""

import seed

def paginate_users(page_size, offset):
    """
    Fetch a page of users from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily fetches pages from the user_data table.
    """
    offset = 0
    while True:  # Single loop
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size