from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import user_manager, imap_service, system_service, smtp_service
from datetime import datetime
import os
import logging
import json
import base64

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["UI"])
templates = Jinja2Templates(directory="app/templates")

# Add global helpers to templates
templates.env.globals.update({
    "now": datetime.now,
    "os": os
})

# --- Helpers ---
from app.services.i18n_service import i18n_service

def render_template(name: str, context: dict, status_code: int = 200, headers: dict = None):
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
    
    response = templates.TemplateResponse(name, context, status_code=status_code, headers=headers)
    
    if "lang" in request.query_params:
        response.set_cookie("app_lang", lang)
        
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

def set_sessions_cookie(response, sessions: dict):
    encoded = base64.b64encode(json.dumps(sessions).encode('utf-8')).decode('utf-8')
    response.set_cookie(key="mail_sessions", value=encoded, httponly=True)
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
            return {"username": requested_user, "password": sessions[requested_user]}
        else:
            return None
        
    first_user = list(sessions.keys())[0]
    return {"username": first_user, "password": sessions[first_user]}

# --- GET Routes (Pages) ---

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return render_template("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return render_template("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    # Retrieve user just to check if we wanted to auto-redirect, but we allow multiple accounts now.
    # You can bookmark /ui/inbox. If they hit /ui/login, assume they want to add/change account.
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template("login.html", {"request": request, "error": error, "users": usernames})

@router.get("/users", response_class=HTMLResponse)
async def users_list_page(request: Request):
    _, users = user_manager.list_system_users()
    return render_template("users_list.html", {"request": request, "users": users})

@router.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    """Render system health dashboard with structured details."""
    import sys
    import platform
    
    health_data = {
        "status": "OK",
        "api_service": "running",
        "mail_services": {
            "postfix": system_service.get_service_details("postfix"),
            "dovecot": system_service.get_service_details("dovecot"),
            "spamd": system_service.get_service_details("spamd"),
        },
        "mail_security": system_service.get_mail_security_status(),
        "system_info": system_service.get_system_info(),
        "network_info": system_service.get_network_info(),
        "server_configuration": {
            "debug_mode": str(os.getenv("DEBUG", "True")),
            "domain": os.getenv("DOMAIN", "127.0.0.1"),
            "python_version": sys.version.split()[0],
            "os_platform": platform.platform(),
            "working_dir": os.getcwd()
        }
    }
    return render_template("health.html", {"request": request, "health": health_data})

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template("change_password.html", {"request": request, "users": usernames})

@router.get("/delete-user", response_class=HTMLResponse)
async def delete_user_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template("delete_user.html", {"request": request, "users": usernames})

@router.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request, folder: str = "INBOX", error: str = None, page: int = 1):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    limit = 10
    offset = (page - 1) * limit
    
    success, mails = imap_service.fetch_emails(
        user["username"], 
        user["password"], 
        folder=folder, 
        limit=limit,
        offset=offset
    )
    # Отримуємо лічильники для бокової панелі
    _, counts = imap_service.fetch_folder_counts(user["username"], user["password"])
    
    total_emails = counts.get(folder, 0) if counts else 0
    total_pages = (total_emails + limit - 1) // limit if total_emails > 0 else 1
    
    if not success:
        # Fetch users again for the login page re-render if it's a login error
        _, user_details = user_manager.list_system_users()
        usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
        return render_template("login.html", {
            "request": request, 
            "error": f"IMAP Error ({folder}): {mails}",
            "users": usernames
        })
    
    return render_template("inbox.html", {
        "request": request, 
        "mails": mails, 
        "user": user, 
        "current_folder": folder,
        "error": error,
        "counts": counts,
        "current_page": page,
        "total_pages": total_pages
    })

@router.get("/compose", response_class=HTMLResponse)
async def compose_page(request: Request, error: str = None):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    _, counts = imap_service.fetch_folder_counts(user["username"], user["password"])
    return render_template("compose.html", {"request": request, "user": user, "error": error, "counts": counts})

@router.get("/mail/{uid}", response_class=HTMLResponse)
async def view_mail_page(request: Request, uid: str, folder: str = "INBOX"):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    success, mail = imap_service.fetch_message_by_uid(user["username"], user["password"], uid, folder=folder)
    _, counts = imap_service.fetch_folder_counts(user["username"], user["password"])
    
    if not success:
        return RedirectResponse(url=f"/ui/inbox?folder={folder}&error={mail}", status_code=status.HTTP_303_SEE_OTHER)
    
    return render_template("view_mail.html", {
        "request": request,
        "mail": mail,
        "user": user,
        "current_folder": folder,
        "counts": counts
    })

# --- POST Routes (Actions) ---

@router.post("/register")
async def handle_register(
    request: Request,
    username: str = Form(...), 
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return render_template("register.html", {
            "request": request,
            "error_key": "reg_err_passwords_mismatch",
            "user": username
        })

    success, msg = user_manager.create_system_user(username, password)
    if success:
        return render_template("register.html", {
            "request": request,
            "success_key": "reg_success",
            "success_args": {"username": username},
            "user": username
        })

    return render_template("register.html", {
        "request": request,
        "error_key": "reg_err_creation",
        "error_detail": msg,
        "user": username
    })

@router.post("/login")
async def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Verify via system manager
    if user_manager.verify_user_password(username, password):
        sessions = get_all_sessions(request)
        sessions[username] = password
        
        response = RedirectResponse(url=f"/ui/inbox?user={username}", status_code=status.HTTP_303_SEE_OTHER)
        set_sessions_cookie(response, sessions)
        return response
    
    # Fetch users for re-rendering the login page
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    
    return render_template("login.html", {
        "request": request,
        "error_key": "login_err_invalid",
        "users": usernames
    })

@router.post("/logout")
async def handle_logout(request: Request):
    sessions = get_all_sessions(request)
    user_to_logout = request.query_params.get("user")
    
    if user_to_logout and user_to_logout in sessions:
        del sessions[user_to_logout]
    else:
        sessions = {}

    response = RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)

    if not sessions:
        response.delete_cookie("mail_sessions")
        response.delete_cookie("mail_user")
        response.delete_cookie("mail_pass")
    else:
        set_sessions_cookie(response, sessions)
        
    return response

@router.post("/change-password")
async def handle_change_password(
    request: Request,
    username: str = Form(...), 
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Fetch users for re-rendering the form in case of error
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []

    if new_password != confirm_password:
        return render_template("change_password.html", {
            "request": request,
            "error_key": "chpw_err_mismatch",
            "user": username,
            "users": usernames
        })

    if not user_manager.verify_user_password(username, current_password):
        return render_template("change_password.html", {
            "request": request,
            "error_key": "chpw_err_wrong_pass",
            "user": username,
            "users": usernames
        })

    success, msg = user_manager.change_user_password(username, new_password)
    if success:
        return render_template("change_password.html", {
            "request": request,
            "success_key": "chpw_success",
            "user": username,
            "users": usernames
        })

    return render_template("change_password.html", {
        "request": request,
        "error_key": "chpw_err_update",
        "error_detail": msg,
        "user": username,
        "users": usernames
    })

@router.post("/delete-user")
async def handle_delete_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_delete: str = Form(...)
):
    # Fetch users for re-rendering if error
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []

    if confirm_delete != "DELETE":
        return render_template("delete_user.html", {
            "request": request,
            "error_key": "del_err_confirm_word",
            "users": usernames,
            "user": username
        })

    if not user_manager.verify_user_password(username, password):
        return render_template("delete_user.html", {
            "request": request,
            "error_key": "del_err_wrong_pass",
            "users": usernames,
            "user": username
        })

    success, msg = user_manager.delete_system_user(username)
    if success:
        return render_template("delete_user.html", {
            "request": request,
            "success_key": "del_success",
            "success_args": {"username": username},
            "users": usernames
        })

    return render_template("delete_user.html", {
        "request": request,
        "error_key": "del_err_deletion",
        "error_detail": msg,
        "users": usernames,
        "user": username
    })

@router.post("/compose")
async def handle_send_mail(
    request: Request, 
    to: str = Form(...), 
    subject: str = Form(...), 
    body: str = Form(...)
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Actually send the email using SMTP service
    # Fix: User reported 127.0.0.1 syntax error. Try 'localhost' or just the hostname.
    domain = os.getenv('DOMAIN', 'localhost')
    success, msg = await smtp_service.send_email(
        to_email=to,
        subject=subject,
        body=body,
        from_email=f"{user['username']}@{domain}"
    )
    
    if success:
        imap_service.append_to_sent(user["username"], user["password"], to, subject, body)
        return render_template("compose.html", {
            "request": request,
            "success_msg": True,
            "recipient": to,
            "user": user
        })

    return render_template("compose.html", {
        "request": request,
        "error": msg,
        "recipient": to,
        "subject": subject,
        "body": body,
        "user": user
    })
@router.post("/mail/{uid}/delete")
async def handle_delete_mail(request: Request, uid: str, folder: str = "INBOX"):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Move to Trash
    success, msg = imap_service.move_message(user["username"], user["password"], uid, folder, "Trash")
    
    if success:
        return render_template("view_mail.html", {
            "request": request,
            "success_msg": True,
            "mail": {"uid": uid},
            "user": user,
            "current_folder": folder,
            "redirect_url": f"/ui/inbox?folder={folder}&user={user['username']}"
        })
    
    return RedirectResponse(url=f"/ui/inbox?folder={folder}&error={msg}&user={user['username']}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/mail/{uid}/restore")
async def handle_restore_mail(request: Request, uid: str):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Restore from Trash to INBOX
    success, msg = imap_service.move_message(user["username"], user["password"], uid, "Trash", "INBOX")
    return RedirectResponse(url=f"/ui/inbox?folder=Trash&user={user['username']}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/mail/{uid}/permanent-delete")
async def handle_permanent_delete_mail(request: Request, uid: str):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Final deletion from Trash
    success, msg = imap_service.delete_permanent(user["username"], user["password"], uid, "Trash")
    return RedirectResponse(url=f"/ui/inbox?folder=Trash&user={user['username']}", status_code=status.HTTP_303_SEE_OTHER)
