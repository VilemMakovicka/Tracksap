import sqlite3
from typing import Iterator, Optional
from fastapi import Depends, Request
from database.database import open_connection
from services.authentication import AuthenticationService
from services.reports import ReportsService
from services.tracks import TracksService
from services.users import UsersService, User
from services.session import session_store, SESSION_COOKIE_NAME
from fastapi.templating import Jinja2Templates

def get_conn() -> Iterator[sqlite3.Connection]:
    with open_connection() as conn:
        yield conn

def users_service(conn: sqlite3.Connection = Depends(get_conn)) -> UsersService:
    return UsersService(conn)

def tracks_service(conn: sqlite3.Connection = Depends(get_conn)) -> TracksService:
    return TracksService(conn)

def reports_service(conn: sqlite3.Connection = Depends(get_conn)) -> ReportsService:
    return ReportsService(conn)

def authentication_service(conn: sqlite3.Connection = Depends(get_conn)) -> AuthenticationService:
    return AuthenticationService(conn)

def get_current_user(request: Request) -> Optional[User]:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    return session_store.get_user(session_id)