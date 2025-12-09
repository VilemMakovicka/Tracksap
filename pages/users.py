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
from pages.config import BASE_TEMPLATE

user_router = APIRouter()

@user_router.get("/user/usersettings", name="user_settings_ui")
async def user_settings_ui(
        request: Request,
        service: UsersService = Depends(users_service),
        current_user: Optional[User] = Depends(get_current_user)
    ):
    if(current_user == None):
        return render_page(
        request,
        "login.html",
        {}
        )

    template = "usersettings.html"

    user = service.select_by_id(current_user.id)
    context = {
        "user": user,
        "request": request,
        "content_template": template
    }

    hx_request = request.headers.get("HX-Request")
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)

@user_router.post("/usersettings", name="user_settings_post")
async def user_settings_post(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    profile_picture: Optional[UploadFile] = File(None),
    user_service: UsersService = Depends(users_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    #pfp
    if profile_picture is not None and not profile_picture.filename == "":
        profile_picture_name = profile_picture.filename.replace(' ', '-')
        profile_picture_path = f"media/profile_pictures/{profile_picture_name}"

        with open(profile_picture_path, "wb") as f:
            shutil.copyfileobj(profile_picture.file, f)

        user_service.update_profile_picture_path(current_user.id, profile_picture_name);

    #username
    if username is not None and str(username).strip() != "":
        user_service.update_username(current_user.id, username)
    #email
    if email is not None and str(email).strip() != "":
        user_service.update_email(current_user.id, email)
    #password
    #jeste nefunkcni
    return {"message": "Files uploaded"}

@user_router.get("/user/{selected_user_id}", name="user_ui")
@user_router.get("/user/{selected_user_id}/tracks", name="user_tracks_ui")
async def userpage_ui(
    request: Request,
    selected_user_id: str,
    service: UsersService = Depends(users_service),
    track_service: TracksService = Depends(tracks_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    selected_user = service.select_by_id(selected_user_id)
    current_user_id = current_user.id if current_user is not None else 0
    tracks = track_service.format_tracks(track_service.selectByUser(selected_user_id, current_user_id))

    template = "userpage.html"
    context = {"user": selected_user, "tracks": tracks}

    return render_page(request, template, context)

@user_router.post("/changetoartist", name="user_change_to_artist_post")
async def user_settings_post(
    user_service: UsersService = Depends(users_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    user_service.update_role_to_artist(current_user.id)
    return {"message": "Successfully changed to artist"}