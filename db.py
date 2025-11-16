import sqlite3
from flask import g, current_app

def get_connection():
    database = current_app.config.get('DATABASE', 'database.db')
    con = sqlite3.connect(database)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=None):
    if params is None:
        params = []
    con = get_connection()
    cur = con.execute(sql, params)
    con.commit()
    g.last_insert_id = cur.lastrowid
    con.close()
    return cur

def last_insert_id():
    return getattr(g, 'last_insert_id', None)

def query(sql, params=None):
    if params is None:
        params = []
    con = get_connection()
    cur = con.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows
