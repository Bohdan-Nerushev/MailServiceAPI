import os
import platform
import sys
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from app.services import system_service
from app.services import user_manager
from app.routes.ui.utils import render_template

router = APIRouter(tags=["UI System"])


@router.get(
    "/users",
    response_class=HTMLResponse
)
async def users_list_page(request: Request):
    _, users = user_manager.list_system_users()
    return render_template(
        name="users_list.html",
        context={
            "request": request,
            "users": users
        }
    )


@router.get(
    "/health",
    response_class=HTMLResponse
)
async def health_page(request: Request):
    """Render system health dashboard with structured details."""
    health_data = {
        "status": "OK",
        "api_service": "running",
        "mail_services": {
            "postfix": system_service.get_service_details("postfix"),
            "dovecot": system_service.get_service_details("dovecot"),
            "nginx": system_service.get_service_details("nginx"),
            "spamd": system_service.get_service_details("spamd"),
        },
        "mail_security": system_service.get_mail_security_status(),
        "system_info": system_service.get_system_info(),
        "network_info": system_service.get_network_info(),
        "server_configuration": {
            "debug_mode": str(os.getenv(
                "DEBUG",
                "True"
            )),
            "domain": os.getenv(
                "DOMAIN",
                "127.0.0.1"
            ),
            "python_version": sys.version.split()[0],
            "os_platform": platform.platform(),
            "working_dir": os.getcwd()
        }
    }
    return render_template(
        name="health.html",
        context={
            "request": request,
            "health": health_data
        }
    )
