# app/services/items.py
from typing import List, Dict, Any, Optional
import sqlite3
from dataclasses import dataclass
from repositories.users import select_all as users_select, select as users_select_by_id, insert as users_insert_user, get_by_email as users_get_by_email

@dataclass
class User:
    id: int
    username: str
    role: str

class UsersService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def selectAll(self) -> List[Dict[str, Any]]:
        return users_select(self.conn)

    def selectByID(self, id) -> List[Dict[str, Any]]:
        return users_select_by_id(self.conn, id)

    def insertUser(self, username: str, email: str, password: str):
        users_insert_user(self.conn, username, email, password)

    def getByEmail(self, email: str):
        return users_get_by_email(self.conn, email)