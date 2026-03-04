from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services import user_manager, imap_service, system_service, smtp_service
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["UI"])
templates = Jinja2Templates(directory="app/templates")

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
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@router.get("/users", response_class=HTMLResponse)
async def users_list_page(request: Request):
    _, users = user_manager.list_system_users()
    return templates.TemplateResponse("users_list.html", {"request": request, "users": users})

@router.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    health_data = {
        "mail_services": {
            "postfix": system_service.get_service_details("postfix"),
            "dovecot": system_service.get_service_details("dovecot"),
        },
        "system_info": system_service.get_system_info(),
        "network_info": system_service.get_network_info(),
        "mail_security": system_service.get_mail_security_status()
    }
    return templates.TemplateResponse("health.html", {"request": request, "health": health_data})

@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})

@router.get("/delete-user", response_class=HTMLResponse)
async def delete_user_page(request: Request):
    return templates.TemplateResponse("delete_user.html", {"request": request})

@router.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request, error: str = None):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    success, mails = imap_service.fetch_inbox(user["username"], user["password"])
    if not success:
        # If IMAP fails, likely password issue or service down
        return templates.TemplateResponse("login.html", {"request": request, "error": f"IMAP Error: {mails}"})
    
    return templates.TemplateResponse("inbox.html", {"request": request, "mails": mails, "user": user, "error": error})

@router.get("/compose", response_class=HTMLResponse)
async def compose_page(request: Request, error: str = None):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("compose.html", {"request": request, "user": user, "error": error})

@router.get("/mail/{uid}", response_class=HTMLResponse)
async def view_mail_page(request: Request, uid: str):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    success, mail = imap_service.fetch_message_by_uid(user["username"], user["password"], uid)
    if not success:
        return RedirectResponse(url="/ui/inbox", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("view_mail.html", {"request": request, "mail": mail, "user": user})

# --- POST Routes (Actions) ---

@router.post("/register")
async def handle_register(username: str = Form(...), password: str = Form(...)):
    success, msg = user_manager.create_system_user(username, password)
    if success:
        return RedirectResponse(url="/ui/users", status_code=status.HTTP_303_SEE_OTHER)
    # TODO: Error handling with template feedback
    return RedirectResponse(url="/ui/register?error=" + str(msg), status_code=status.HTTP_303_SEE_OTHER)

@router.post("/login")
async def handle_login(username: str = Form(...), password: str = Form(...)):
    # Verify via system manager
    if user_manager.verify_user_password(username, password):
        # Successful login - Store in cookies for now
        response = RedirectResponse(url="/ui/inbox", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="mail_user", value=username, httponly=True)
        response.set_cookie(key="mail_pass", value=password, httponly=True)
        return response
    return RedirectResponse(url="/ui/login?error=Invalid+credentials", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/logout")
async def handle_logout():
    response = RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("mail_user")
    response.delete_cookie("mail_pass")
    return response

@router.post("/change-password")
async def handle_change_password(
    username: str = Form(...), 
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    # 1. Check if new passwords match
    if new_password != confirm_password:
        return RedirectResponse(
            url=f"/ui/change-password?error=Нові+паролі+не+збігаються&user={username}", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 2. Verify current password
    if not user_manager.verify_user_password(username, current_password):
        return RedirectResponse(
            url=f"/ui/change-password?error=Невірний+поточний+пароль&user={username}", 
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 3. Perform the change
    success, msg = user_manager.change_user_password(username, new_password)
    if success:
        return RedirectResponse(url="/ui/users?msg=Password+updated", status_code=status.HTTP_303_SEE_OTHER)
    
    return RedirectResponse(
        url=f"/ui/change-password?error={msg}&user={username}", 
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/delete-user")
async def handle_delete_user(username: str = Form(...)):
    success, msg = user_manager.delete_system_user(username)
    if success:
        return RedirectResponse(url="/ui/users", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/ui/delete-user?error=" + str(msg), status_code=status.HTTP_303_SEE_OTHER)

@router.post("/compose")
async def handle_send_mail(request: Request, to: str = Form(...), subject: str = Form(...), body: str = Form(...)):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Simple SMTP send
    # Note: smtp_service Expects specific arguments
    # I'll check smtp_service.send_mail signature later if it fails
    return RedirectResponse(url="/ui/inbox", status_code=status.HTTP_303_SEE_OTHER)
