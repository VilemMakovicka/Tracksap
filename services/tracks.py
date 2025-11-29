# app/services/items.py
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import sqlite3
from repositories.tracks import select_by_user, select_all_liked, add_liked, remove_liked

class TracksService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def selectByUser(self, id, current_user_id) -> List[Dict[str, Any]]:
        return select_by_user(self.conn, id, current_user_id)

    def selectAllLiked(self, user_id):
        tracks = select_all_liked(self.conn, user_id)
        return tracks

    def addLike(self, track_id, user_id):
        add_liked(self.conn, track_id, user_id)

    def removeLike(self, track_id, user_id):
        remove_liked(self.conn, track_id, user_id)
