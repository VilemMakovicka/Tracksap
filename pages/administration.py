from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from services.reports import ReportsService
from dependencies import users_service, get_current_user
from dependencies import reports_service
from services.users import UsersService, User
from pages.tools import render_page

administration_router = APIRouter()

@administration_router.get("/administration", name="administration_ui")
async def administration_users_ui(
        request: Request,
        user_service: UsersService = Depends(users_service),
        current_user: Optional[User] = Depends(get_current_user)
):
    if current_user is None or current_user.role != "administrator":
        return request.app.state.templates.TemplateResponse("template.error.no_permission.html", {"request": request})

    users: List[Dict[str, Any]] = user_service.select_all()
    template_filename = "administration.html"
    page_context = {"users": users}

    return render_page(
        request,
        template_filename,
        page_context
    )

@administration_router.get("/administration/users", name="administration_users_ui")
async def administration_users_ui(
        request: Request,
        user_service: UsersService = Depends(users_service),
        current_user: Optional[User] = Depends(get_current_user)
):
    if current_user is None or current_user.role != "administrator":
        return request.app.state.templates.TemplateResponse("template.error.no_permission.html", {"request": request})

    users: List[Dict[str, Any]] = user_service.select_all()
    template_filename = "administration_users.html"
    page_context = {"users": users}

    return render_page(
        request,
        template_filename,
        page_context
    )

@administration_router.get("/administration/reports", name="administration_reports_ui")
async def administration_reports_ui(
        request: Request,
        service: ReportsService = Depends(reports_service),
        current_user: Optional[User] = Depends(get_current_user)
):
    if current_user is None or current_user.role != "administrator":
        return request.app.state.templates.TemplateResponse("template.error.no_permission.html", {"request": request})

    tracks: List[Dict[str, Any]] = service.debugSelectAll()
    template_filename = "administration_reports.html"
    page_context = {"tracks": tracks}

    return render_page(
        request,
        template_filename,
        page_context
    )