import sqlite3

def connect():
    conn = sqlite3.connect("dcr.db")
    conn.row_factory = sqlite3.Row

    return conn

