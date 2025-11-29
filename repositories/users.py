# app/repositories/items.py
from types import NoneType
from typing import List, Dict, Any, Optional
import sqlite3

def select_all(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT ID, UserRoleID, UserBlockStatusID, Username, Email, Password, ProfilePicturePath FROM Users"
    ).fetchall()
    return [dict(r) for r in rows]

def select(conn: sqlite3.Connection, id) -> List[Dict[str, Any]]:
    row = conn.execute(
        "SELECT ID, UserRoleID, UserBlockStatusID, Username, Email, Password, ProfilePicturePath FROM Users WHERE ID='" + id + "'"
    ).fetchone()
    if row != None:
        return dict(row)
    else:
        return None

def insert(conn: sqlite3.Connection, username: str, email: str, password: str):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Users (UserRoleID, UserBlockStatusID, Username, Email, Password) VALUES (1, 1, ?, ?, ?)",
        (username, email, password)
    )
    conn.commit()

def get_by_email(conn: sqlite3.Connection, email: str):
    row = conn.execute(
        "SELECT ID, UserRoleID, UserBlockStatusID, Username, Email, Password, ProfilePicturePath FROM Users WHERE Email='" + email + "'"
    ).fetchone()
    if row != None:
        return dict(row)
    else:
        return None
