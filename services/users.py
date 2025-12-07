# app/services/items.py
from typing import List, Dict, Any, Optional
import sqlite3
from dataclasses import dataclass
from repositories.users import (
    select_all as users_select,
    select as users_select_by_id,
    insert as users_insert_user,
    get_by_email as users_get_by_email,
    update_value as users_update_value,
)

@dataclass
class User:
    id: int
    username: str
    email: str
    role: str
    profile_picture_path: str

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

    def updateValue(self, user_id: int, value_name: str, value: str):
        users_update_value(self.conn, user_id, value_name, value)

    def updateProfilePicturePath(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "ProfilePicturePath", f"'{value}'")

    def updateUsername(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "Username", f"'{value}'")

    def updateEmail(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "Email", f"'{value}'")