#lib/__init__.py

import sqlite3
"""this opens a connection to a SQLites DB file named event_planner. If it doesn't exist SQLite will create it."""
CONN = sqlite3.connect('event_planner.db')
""" This cursor object allows us to execute SQL commands against the DB"""
CURSOR = CONN.cursor()

def commit_and_close():
    """commit changes and close the connection to the DataBase"""
    CONN.commit()
    CONN.close() 