import os
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Form, Request, Header, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from services.users import User

from services.authentication import AuthenticationService
from dependencies import authentication_service, get_current_user
import bcrypt
import secrets

import database.database
import repositories.users
from dependencies import users_service
from dependencies import tracks_service
from services.session import session_store

from services.users import UsersService
from services.tracks import TracksService

from services.session import SESSION_COOKIE_NAME, session_store

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"

@router.get("/", name="test_ui")
async def test_ui(request: Request):
    return render_page(
        request,
        "discover.html",
        {}
    )

@router.get("/error/usernotfound", name="user_not_found_ui")
async def user_not_found_ui(request: Request):
    hx_request = request.headers.get("HX-Request")
    context = {"request": request}

    if hx_request:
        return request.app.state.templates.TemplateResponse("template.error.user_not_found.html", context)

    context["content_template"] = "template.error.user_not_found.html"
    return request.app.state.templates.TemplateResponse("base.html", context)

@router.get("/library", name="library_ui")
async def library_ui(
    request: Request,
    hx_request: Optional[str] = Header(None)
):
    context = {
        "request": request
    }

    if hx_request:
        return request.app.state.templates.TemplateResponse("library.html", context)

    context["content_template"] = "library.html"
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

@router.get("/library/liked", name="liked_ui")
async def liked_ui(
        request: Request,
        track_service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
    ):
    if(user == None):
        return render_page(
        request,
        "login.html",
        {}
        )
    tracks = track_service.selectAllLiked(user.id)
    for track in tracks:
        track["Contributors"] = json.loads(track["Contributors"])
        upload_date_string = track["UploadDate"].split("-")
        upload_date = datetime(int(upload_date_string[0]),
                               int(upload_date_string[1]),
                               int(upload_date_string[2]),
                               int(upload_date_string[3]),
                               int(upload_date_string[4]))
        track["UploadDate"] = time_ago(upload_date)
        track["liked"] = 'true'

    context = {"liked_tracks": tracks, "user": user}

    hx_request = request.headers.get("HX-Request")
    context["request"] = request

    if hx_request:
        return request.app.state.templates.TemplateResponse("liked.html", context)

    context["content_template"] = "library.html"
    context["library_content"] = "liked.html"
    return request.app.state.templates.TemplateResponse("base.html", context)

@router.get("/login", name="login_ui")
async def login_ui(request: Request):
    return render_page(
        request,
        "login.html",
        { "error": None }
    )

@router.post("/login", name="login_post")
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

@router.post("/unlike/{track_id}")
def like_post(
        request: Request,
        track_id: str,
        service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
):
    service.removeLike(track_id, user.id)
    return "unliked"

@router.post("/like/{track_id}")
def like_post(
        request: Request,
        track_id: str,
        service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
):
    service.addLike(track_id, user.id)
    return "liked"

@router.post("/logout", name="logout")
async def logout(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    session_store.delete_session(session_id)
    response = RedirectResponse(
        url=request.url_for("library_ui"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@router.get("/register", name="register_ui")
async def register_ui(request: Request):
    return render_page(
        request,
        "register.html",
        {}
    )

@router.post("/register", name="register_post")
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    user_service: UsersService = Depends(users_service),
    auth_service = Depends(authentication_service)
):
    hashed_password = auth_service.hash_password(password)
    user_service.insertUser(username, email, hashed_password)
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

@router.get("/administration/users", name="administration_users_ui")
async def administration_users_ui(request: Request, service: UsersService = Depends(users_service)):
    users: List[Dict[str, Any]] = service.selectAll()

    return render_page(
        request,
        "administration_users.html",
        {"users": users}
    )

@router.get("/user/{user_id}", name="users_ui")
async def userpage_ui(
    request: Request,
    user_id: str,
    service: UsersService = Depends(users_service),
    track_service: TracksService = Depends(tracks_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    user = service.selectByID(user_id)
    current_user_id = current_user.id if current_user is not None else 0
    tracks = track_service.selectByUser(user_id, current_user_id)

    for track in tracks:
        track["Contributors"] = json.loads(track["Contributors"])
        upload_date_string = track["UploadDate"].split("-")
        upload_date = datetime(int(upload_date_string[0]),
                               int(upload_date_string[1]),
                               int(upload_date_string[2]),
                               int(upload_date_string[3]),
                               int(upload_date_string[4]))
        track["UploadDate"] = time_ago(upload_date)

    return render_page(
        request,
        "userpage.html",
        {"user": user, "tracks": tracks}
    )

@router.get("/library/playlists", name="playlists_ui")
async def test_ui(
        request: Request,
        user: Optional[User] = Depends(get_current_user)
):
    context = {"user": user}

    hx_request = request.headers.get("HX-Request")
    context["request"] = request

    if hx_request:
        return request.app.state.templates.TemplateResponse("playlists.html", context)

    context["content_template"] = "library.html"
    context["library_content"] = "playlists.html"
    return request.app.state.templates.TemplateResponse("base.html", context)

@router.get("/discover", name="discover_ui")
async def discover_ui(request: Request):
    return render_page(
        request,
        "discover.html",
        {}
    )

@router.get("/stream/{audio_path}")
async def stream_audio(audio_path, range: str = Header(None)):
    file_size = os.path.getsize("media/tracks/" + audio_path)

    if range:
        start = int(range.replace("bytes=", "").split("-")[0])
    else:
        start = 0

    def iterfile(start_pos: int):
        with open("media/tracks/" + audio_path, "rb") as f:
            f.seek(start_pos)
            while chunk := f.read(1024 * 64):
                yield chunk

    end = file_size - 1
    content_length = file_size - start

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
    }

    return StreamingResponse(
        iterfile(start),
        status_code=206 if range else 200,
        headers=headers,
        media_type="audio/mpeg",
    )

def render_page(request: Request, template: str, context: dict, basetemplate: str = "base.html"):
    hx_request = request.headers.get("HX-Request")
    context["request"] = request

    # If HTMX request → always return the template itself
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    # Load the template source to check if it extends another template
    env = request.app.state.templates.env
    source, _, _ = env.loader.get_source(env, template)

    # If the template already extends something → render it as-is
    if "{% extends" in source:
        return request.app.state.templates.TemplateResponse(template, context)

    # Template is standalone → include it into basetemplate
    context["content_template"] = template
    return request.app.state.templates.TemplateResponse(basetemplate, context)

def time_ago(date):
    now = datetime.now()
    diff = relativedelta(now, date)

    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "just now"