from tools.date import get_current_date
from typing import List, Dict, Any
import sqlite3

def insert(conn: sqlite3.Connection, track_id: str, message: str):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ReportedTracks(TrackID, DateOfReport, Message) VALUES (?, ?, ?)",
        (track_id, get_current_date(), message)
    )
    conn.commit()

def debug_select_all(conn: sqlite3.Connection):
    rows = conn.execute(
        """SELECT * FROM ReportedTracks"""
    ).fetchall()
    return [dict(r) for r in rows]