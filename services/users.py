from typing import List, Dict, Any
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

    def select_all(self) -> List[Dict[str, Any]]:
        return users_select(self.conn)

    def select_by_id(self, id) -> Dict[str, Any]:
        return users_select_by_id(self.conn, id)

    def insert_user(self, username: str, email: str, password: str):
        users_insert_user(self.conn, username, email, password)

    def get_by_email(self, email: str):
        return users_get_by_email(self.conn, email)

    def update_value(self, user_id: int, value_name: str, value: str):
        users_update_value(self.conn, user_id, value_name, value)

    def update_profile_picture_path(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "ProfilePicturePath", f"'{value}'")

    def update_username(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "Username", f"'{value}'")

    def update_email(self, user_id: int, value: str):
        users_update_value(self.conn, user_id, "Email", f"'{value}'")

    def update_role_to_artist(self, user_id: int):
        artist_role_id = 3
        users_update_value(self.conn, user_id, "UserRoleID", str(artist_role_id))