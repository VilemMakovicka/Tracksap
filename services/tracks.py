from typing import List, Dict, Any
import sqlite3
from repositories.tracks import select_by_user, select_all_liked, add_liked, remove_liked, debug_select_all, select_by_text, insert
import json
from datetime import datetime
from pages.tools import time_ago

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

    def debugSelectAll(self, current_user_id):
        return debug_select_all(self.conn, current_user_id)

    def SelectByQuery(self, query, current_user_id = 0):
        return select_by_text(self.conn, query, current_user_id)

    def Insert(self, title: str, audio_file_path: str, track_cover_file_name: str, current_user_id, track_length: str):
        insert(self.conn, title, audio_file_path, track_cover_file_name, current_user_id, track_length)

    @staticmethod
    def format_tracks(tracks):
        for track in tracks:
            track["Contributors"] = json.loads(track["Contributors"])
            upload_date_string = track["UploadDate"].split("-")
            upload_date = datetime(int(upload_date_string[0]),
                                   int(upload_date_string[1]),
                                   int(upload_date_string[2]),
                                   int(upload_date_string[3]),
                                   int(upload_date_string[4]))
            track["UploadDate"] = time_ago(upload_date)
        return tracks