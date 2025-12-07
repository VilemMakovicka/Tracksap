from typing import List, Dict, Any
import sqlite3
from repositories.reports import insert as report_insert, debug_select_all

class ReportsService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insertReport(self, track_id: str, message: str) -> List[Dict[str, Any]]:
        return report_insert(self.conn, track_id, message)

    def debugSelectAll(self):
        return debug_select_all(self.conn)