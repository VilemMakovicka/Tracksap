import sqlite3
from services.users import User
from typing import Optional
from passlib.context import CryptContext
from repositories.users import get_by_email as users_get_by_email
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticationService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def authenticate(self, email: str, plain_password: str) -> Optional[User]:
        user = users_get_by_email(self.conn, email)
        if not user:
            return None
        hashed_password = user["Password"]
        if not bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8")):
            return None
        return User(id=user["ID"], username=user["Email"], role=user["UserRole"])

    def hash_password(self, password: str) -> str:
        print("hashing the password:" + password)
        #return pwd_context.hash(password[:72])
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

