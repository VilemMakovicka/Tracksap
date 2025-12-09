import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request, Header, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from passlib.context import CryptContext
from starlette.responses import RedirectResponse

from services.reports import ReportsService
from services.users import User

from services.authentication import AuthenticationService
from dependencies import authentication_service, get_current_user
import bcrypt
import secrets

import database.database
import repositories.users
from dependencies import users_service
from dependencies import tracks_service
from dependencies import reports_service
from services.session import session_store

from services.users import UsersService
from services.tracks import TracksService

from services.session import SESSION_COOKIE_NAME, session_store
import shutil
from pages.tools import time_ago, render_page

authentication_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

@authentication_router.get("/error/usernotfound", name="user_not_found_ui")
async def user_not_found_ui(request: Request):
    hx_request = request.headers.get("HX-Request")
    context = {"request": request}

    if hx_request:
        return request.app.state.templates.TemplateResponse("template.error.user_not_found.html", context)

    context["content_template"] = "template.error.user_not_found.html"
    return request.app.state.templates.TemplateResponse("base.html", context)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@authentication_router.get("/login", name="login_ui")
async def login_ui(request: Request):
    return render_page(
        request,
        "login.html",
        { "error": None }
    )

@authentication_router.post("/login", name="login_post")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        auth_service: AuthenticationService = Depends(authentication_service),
):
    user = auth_service.authenticate(email, password)
    if not user:
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    session_id = session_store.create_session(user)
    response = RedirectResponse(
        url=request.query_params.get("next") or request.url_for("liked_ui"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True)
    return response

@authentication_router.post("/logout", name="logout")
async def logout(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    session_store.delete_session(session_id)
    response = RedirectResponse(
        url=request.url_for("library_ui"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@authentication_router.get("/register", name="register_ui")
async def register_ui(request: Request):
    return render_page(
        request,
        "register.html",
        {}
    )

@authentication_router.post("/register", name="register_post")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    user_service: UsersService = Depends(users_service),
    auth_service = Depends(authentication_service)
):
    hashed_password = auth_service.hash_password(password)
    user_service.insert_user(username, email, hashed_password)
    # return login(request, email, password, auth_service)
    # return {"message": "Registered successfully!"}
    user: User = auth_service.authenticate(email, password)
    if not user:
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid email or password",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    session_id = session_store.create_session(user)
    response = RedirectResponse(
        url=request.query_params.get("next") or request.url_for("liked_ui"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(SESSION_COOKIE_NAME, session_id, httponly=True)
    return response