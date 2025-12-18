# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pages.authentication import authentication_router
from pages.tracks import track_router
from pages.users import user_router
from pages.administration import administration_router
from dependencies import get_current_user

def create_app() -> FastAPI:
    app = FastAPI(title="Mini FastAPI – Items")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/media", StaticFiles(directory="media"), name="media")
    app.state.templates = Jinja2Templates(directory="templates")
    app.state.templates.env.globals["get_current_user"] = get_current_user

    app.state.templates.env.globals["role_administrator"] = "administrator"
    app.state.templates.env.globals["role_artist"] = "artist"
    app.state.templates.env.globals["role_listener"] = "listener"

    app.include_router(authentication_router, prefix="", tags=["authentication"])
    app.include_router(track_router, prefix="", tags=["tracks"])
    app.include_router(user_router, prefix="", tags=["users"])
    app.include_router(administration_router, prefix="", tags=["administration"])

    return app

def print_all_routes(app):
    for r in app.routes:
        try:
            print(getattr(r, "methods", ""), getattr(r, "path", ""))
        except Exception:
            pass

app = create_app()
print_all_routes(app)