from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import user_manager, imap_service, system_service, smtp_service
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["UI"])
templates = Jinja2Templates(directory="app/templates")

# Add global helpers to templates
templates.env.globals.update({
    "now": datetime.now,
    "os": os
})

# --- Helpers ---

def get_session_user(request: Request):
    """Retrieve username and password from cookies (Simple PoC session)."""
    username = request.cookies.get("mail_user")
    password = request.cookies.get("mail_pass")
    if not username or not password:
        return None
    return {"username": username, "password": password}

# --- GET Routes (Pages) ---

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return templates.TemplateResponse("login.html", {"request": request, "error": error, "users": usernames})

@router.get("/users", response_class=HTMLResponse)
async def users_list_page(request: Request):
    _, users = user_manager.list_system_users()
    return templates.TemplateResponse("users_list.html", {"request": request, "users": users})

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
    return templates.TemplateResponse("health.html", {"request": request, "health": health_data})

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return templates.TemplateResponse("change_password.html", {"request": request, "users": usernames})

@router.get("/delete-user", response_class=HTMLResponse)
async def delete_user_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return templates.TemplateResponse("delete_user.html", {"request": request, "users": usernames})

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
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": f"IMAP Error ({folder}): {mails}",
            "users": usernames
        })
    
    return templates.TemplateResponse("inbox.html", {
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
    return templates.TemplateResponse("compose.html", {"request": request, "user": user, "error": error, "counts": counts})

@router.get("/mail/{uid}", response_class=HTMLResponse)
async def view_mail_page(request: Request, uid: str, folder: str = "INBOX"):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    success, mail = imap_service.fetch_message_by_uid(user["username"], user["password"], uid, folder=folder)
    _, counts = imap_service.fetch_folder_counts(user["username"], user["password"])
    
    if not success:
        return RedirectResponse(url=f"/ui/inbox?folder={folder}&error={mail}", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("view_mail.html", {
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
    # 1. Check if passwords match
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "error": "Паролі не збігаються",
            "user": username
        })

    # 2. Proceed with creation
    success, msg = user_manager.create_system_user(username, password)
    if success:
        return templates.TemplateResponse("register.html", {
            "request": request, 
            "success_msg": f"Користувача {username} успішно створено! Повернення до списку...",
            "user": username
        })
    
    return templates.TemplateResponse("register.html", {
        "request": request, 
        "error": f"Помилка створення: {msg}",
        "user": username
    })

@router.post("/login")
async def handle_login(request: Request, username: str = Form(...), password: str = Form(...)):
    # Verify via system manager
    if user_manager.verify_user_password(username, password):
        # Successful login - Store in cookies for now
        response = RedirectResponse(url="/ui/inbox", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="mail_user", value=username, httponly=True)
        response.set_cookie(key="mail_pass", value=password, httponly=True)
        return response
    
    # Fetch users for re-rendering the login page
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Невірний логін або пароль",
        "users": usernames
    })

@router.post("/logout")
async def handle_logout():
    response = RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("mail_user")
    response.delete_cookie("mail_pass")
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

    # 1. Check if new passwords match
    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request, 
            "error": "Нові паролі не збігаються",
            "user": username,
            "users": usernames
        })

    # 2. Verify current password
    if not user_manager.verify_user_password(username, current_password):
        return templates.TemplateResponse("change_password.html", {
            "request": request, 
            "error": "Невірний поточний пароль",
            "user": username,
            "users": usernames
        })

    # 3. Perform the change
    success, msg = user_manager.change_user_password(username, new_password)
    if success:
        return templates.TemplateResponse("change_password.html", {
            "request": request, 
            "success_msg": "Пароль успішно оновлено! Повернення до списку...",
            "user": username,
            "users": usernames
        })
    
    return templates.TemplateResponse("change_password.html", {
        "request": request, 
        "error": f"Помилка оновлення: {msg}",
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

    # 1. Check for DELETE word confirmation
    if confirm_delete != "DELETE":
        return templates.TemplateResponse("delete_user.html", {
            "request": request, 
            "error": "Будь ласка, введіть 'DELETE' для підтвердження",
            "users": usernames,
            "user": username
        })

    # 2. Verify password before deletion
    if not user_manager.verify_user_password(username, password):
        return templates.TemplateResponse("delete_user.html", {
            "request": request, 
            "error": "Невірний пароль для підтвердження видалення",
            "users": usernames,
            "user": username
        })

    success, msg = user_manager.delete_system_user(username)
    if success:
        return templates.TemplateResponse("delete_user.html", {
            "request": request, 
            "success_msg": f"Акаунт {username} видалено назавжди. Повернення до списку...",
            "users": usernames
        })
    
    return templates.TemplateResponse("delete_user.html", {
        "request": request, 
        "error": f"Помилка видалення: {msg}",
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
        return templates.TemplateResponse("compose.html", {
            "request": request,
            "success_msg": "Лист успішно надіслано! Повернення до вхідних...",
            "recipient": to
        })
    
    return templates.TemplateResponse("compose.html", {
        "request": request,
        "error": f"Помилка відправлення: {msg}",
        "recipient": to,
        "subject": subject,
        "body": body
    })
@router.post("/mail/{uid}/delete")
async def handle_delete_mail(request: Request, uid: str, folder: str = "INBOX"):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Move to Trash
    success, msg = imap_service.move_message(user["username"], user["password"], uid, folder, "Trash")
    
    if success:
        return templates.TemplateResponse("view_mail.html", {
            "request": request,
            "success_msg": "Лист переміщено до кошика. Повернення...",
            "mail": {"uid": uid}, # Placeholder for template logic
            "user": user,
            "current_folder": folder,
            "redirect_url": f"/ui/inbox?folder={folder}"
        })
    
    return RedirectResponse(url=f"/ui/inbox?folder={folder}&error={msg}", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/mail/{uid}/restore")
async def handle_restore_mail(request: Request, uid: str):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Restore from Trash to INBOX
    success, msg = imap_service.move_message(user["username"], user["password"], uid, "Trash", "INBOX")
    return RedirectResponse(url="/ui/inbox?folder=Trash", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/mail/{uid}/permanent-delete")
async def handle_permanent_delete_mail(request: Request, uid: str):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Final deletion from Trash
    success, msg = imap_service.delete_permanent(user["username"], user["password"], uid, "Trash")
    return RedirectResponse(url="/ui/inbox?folder=Trash", status_code=status.HTTP_303_SEE_OTHER)
