import base64
import json
import logging
import os
from fastapi import Request
from fastapi.templating import Jinja2Templates
from app.services.time_service import time_service
from app.services.i18n_service import i18n_service

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")

# Add global helpers to templates
templates.env.globals.update({
    "now": time_service.now,
    "os": os,
    "domain": os.getenv("DOMAIN", "localhost")
})


def render_template(
    name: str,
    context: dict,
    status_code: int = 200,
    headers: dict = None
):
    request: Request = context.get("request")

    lang = request.query_params.get("lang")
    if not lang:
        lang = request.cookies.get("app_lang", "uk")

    context["_"] = lambda key: i18n_service.gettext(key, lang)
    context["current_lang"] = lang

    if headers is None:
        headers = {}
    headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    headers["Pragma"] = "no-cache"
    headers["Expires"] = "0"

    response = templates.TemplateResponse(
        name=name,
        context=context,
        status_code=status_code,
        headers=headers
    )

    if "lang" in request.query_params:
        response.set_cookie(
            key="app_lang",
            value=lang
        )

    return response


def get_all_sessions(request: Request) -> dict:
    sessions_str = request.cookies.get("mail_sessions")
    if not sessions_str:
        username = request.cookies.get("mail_user")
        password = request.cookies.get("mail_pass")
        if username and password:
            return {username: password}
        return {}
    try:
        return json.loads(base64.b64decode(sessions_str).decode('utf-8'))
    except Exception:
        return {}


def set_sessions_cookie(
    response,
    sessions: dict
):
    encoded = base64.b64encode(json.dumps(sessions).encode('utf-8')).decode('utf-8')
    response.set_cookie(
        key="mail_sessions",
        value=encoded,
        httponly=True
    )
    response.delete_cookie("mail_user")
    response.delete_cookie("mail_pass")


def get_session_user(request: Request):
    """Retrieve user and password from sessions with support for multiple accounts."""
    sessions = get_all_sessions(request)
    if not sessions:
        return None

    requested_user = request.query_params.get("user")
    if requested_user:
        if requested_user in sessions:
            return {
                "username": requested_user,
                "password": sessions[requested_user]
            }
        else:
            return None

    first_user = list(sessions.keys())[0]
    return {
        "username": first_user,
        "password": sessions[first_user]
    }
