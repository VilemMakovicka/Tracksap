# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from pages.test import router as test_router
from dependencies import get_current_user

def create_app() -> FastAPI:
    app = FastAPI(title="Mini FastAPI – Items")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/media", StaticFiles(directory="media"), name="media")
    app.state.templates = Jinja2Templates(directory="templates")
    app.state.templates.env.globals["get_current_user"] = get_current_user
    app.include_router(test_router, prefix="", tags=["test"])
    return app

def print_all_routes(app):
    print("=== ROUTES ===")
    for r in app.routes:
        try:
            print(getattr(r, "methods", ""), getattr(r, "path", ""))
        except Exception:
            pass

app = create_app()
print_all_routes(app)