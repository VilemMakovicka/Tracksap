import os
import json
import shutil
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, Header, UploadFile, File
from fastapi.responses import StreamingResponse
from datetime import datetime
from services.users import User
from dependencies import tracks_service, reports_service, get_current_user
from services.reports import ReportsService
from services.tracks import TracksService
from pages.tools import render_page, time_ago
from pages.config import BASE_TEMPLATE
from io import BytesIO
from mutagen import File as MutagenFile

track_router = APIRouter()

@track_router.get("/upload", name="upoad_track_ui")
async def upload_track_ui(request: Request):
    template = "upload.html"
    context = {"request": request, "content_template": template}

    hx_request = request.headers.get("HX-Request")
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)

@track_router.get("/track/{track_id}", name="track_ui")
async def track_ui(
        request: Request,
        track_id: int,
        track_service: TracksService = Depends(tracks_service),
        current_user: Optional[User] = Depends(get_current_user)
):
    current_user_id = current_user.id if current_user is not None else 0
    tracks = track_service.selectByID(track_id, current_user_id)
    track = tracks[0]

    track["Contributors"] = json.loads(track["Contributors"])
    upload_date_string = track["UploadDate"].split("-")
    upload_date = datetime(int(upload_date_string[0]),
                           int(upload_date_string[1]),
                           int(upload_date_string[2]),
                           int(upload_date_string[3]),
                           int(upload_date_string[4]))
    track["UploadDate"] = time_ago(upload_date)
    track["liked"] = 'true'

    template = "track.html"
    context = {"request": request, "content_template": template, "track": track}

    hx_request = request.headers.get("HX-Request")
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)


@track_router.post("/upload", name="upload_post")
async def upload(
    request: Request,
    track_name: str = Form(...),
    track_file: UploadFile = File(...),
    track_cover: UploadFile = File(...),
    track_service: TracksService = Depends(tracks_service),
    current_user: Optional[User] = Depends(get_current_user)
):
    track_file_name = track_file.filename.replace(' ', '-')
    track_cover_name = track_cover.filename.replace(' ', '-')

    track_path = f"media/tracks/{track_file_name}"

    with open(track_path, "wb") as f:
        shutil.copyfileobj(track_file.file, f)  # <-- FIXED HERE

    # extract duration
    audio = MutagenFile(track_path)
    if audio and audio.info:
        duration_seconds = int(audio.info.length)
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        track_length = f"{minutes}:{seconds:02d}"
    else:
        track_length = "0:00"

    cover_path = f"media/track_covers/{track_cover_name}"
    with open(cover_path, "wb") as f:
        shutil.copyfileobj(track_cover.file, f)

    track_service.Insert(
        title=track_name,
        audio_file_path=track_file_name,
        track_cover_file_name=track_cover_name,
        current_user_id=current_user.id,
        track_length=track_length
    )

    return {"message": "Files uploaded"}


@track_router.get("/library", name="library_ui")
async def library_ui(
    request: Request,
    hx_request: Optional[str] = Header(None)
):
    template = "library.html"
    context = {"request": request, "content_template": template}

    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)

@track_router.get("/library/liked", name="liked_ui")
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

@track_router.get("/library/playlists", name="playlists_ui")
async def test_ui(
        request: Request,
        user: Optional[User] = Depends(get_current_user)
):
    parent_template = "library.html"
    template = "playlists.html"

    context = {
        "user": user,
        "request": request,
        "content_template": parent_template,
        "library_content": template
    }

    hx_request = request.headers.get("HX-Request")

    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)

@track_router.get("/", name="homepage_ui")
@track_router.get("/discover", name="discover_ui")
async def discover_ui(
        request: Request,
        track_service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
):
    current_user_id = user.id if user is not None else 0
    tracks = track_service.format_tracks(track_service.debugSelectAll(current_user_id))
    template = "discover.html"
    context = {"tracks": tracks}

    return render_page(
        request,
        template,
        context
    )

@track_router.get("/search/{query}", name="track_search_ui")
async def user_settings_ui(
        query: str,
        request: Request,
        track_service: TracksService = Depends(tracks_service),
        current_user: Optional[User] = Depends(get_current_user)
    ):
    template = "search.html"
    current_user_id = current_user.id if current_user is not None else 0
    tracks = track_service.format_tracks(track_service.SelectByQuery(query, current_user_id))

    context = {
        "request": request,
        "content_template": template,
        "tracks": tracks,
        "query": query,
        "current_user": current_user
    }

    hx_request = request.headers.get("HX-Request")
    if hx_request:
        return request.app.state.templates.TemplateResponse(template, context)

    return request.app.state.templates.TemplateResponse(BASE_TEMPLATE, context)

@track_router.post("/unlike/{track_id}")
def like_post(
        request: Request,
        track_id: str,
        service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
):
    service.removeLike(track_id, user.id)
    return "unliked"

@track_router.post("/like/{track_id}")
def like_post(
        request: Request,
        track_id: str,
        service: TracksService = Depends(tracks_service),
        user: Optional[User] = Depends(get_current_user)
):
    service.addLike(track_id, user.id)
    return "liked"

@track_router.post("/report/{track_id}")
async def report_post(
        request: Request,
        track_id: str,
        message: str = Form(...),
        service: ReportsService = Depends(reports_service)
):
    service.insertReport(track_id, message)
    return "reported"

@track_router.get("/stream/{audio_path}")
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