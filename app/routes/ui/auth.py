from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.services import user_manager
from app.routes.ui.utils import render_template
from app.routes.ui.utils import get_all_sessions
from app.routes.ui.utils import set_sessions_cookie

router = APIRouter(tags=["UI Auth"])


@router.get(
    "/register",
    response_class=HTMLResponse
)
async def register_page(request: Request):
    return render_template(
        name="register.html",
        context={"request": request}
    )


@router.get(
    "/login",
    response_class=HTMLResponse
)
async def login_page(
    request: Request,
    error: str = None
):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template(
        name="login.html",
        context={
            "request": request,
            "error": error,
            "users": usernames
        }
    )


@router.get(
    "/change-password",
    response_class=HTMLResponse
)
async def change_password_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template(
        name="change_password.html",
        context={
            "request": request,
            "users": usernames
        }
    )


@router.get(
    "/delete-user",
    response_class=HTMLResponse
)
async def delete_user_page(request: Request):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
    return render_template(
        name="delete_user.html",
        context={
            "request": request,
            "users": usernames
        }
    )


@router.post("/register")
async def handle_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    if password != confirm_password:
        return render_template(
            name="register.html",
            context={
                "request": request,
                "error_key": "reg_err_passwords_mismatch",
                "user": username
            }
        )

    success, msg = user_manager.create_system_user(
        username=username,
        password=password
    )
    if success:
        return render_template(
            name="register.html",
            context={
                "request": request,
                "success_key": "reg_success",
                "success_args": {"username": username},
                "user": username
            }
        )

    return render_template(
        name="register.html",
        context={
            "request": request,
            "error_key": "reg_err_creation",
            "error_detail": msg,
            "user": username
        }
    )


@router.post("/login")
async def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if user_manager.verify_user_password(
        username=username,
        password=password
    ):
        sessions = get_all_sessions(request)
        sessions[username] = password

        response = RedirectResponse(
            url=f"/ui/inbox?user={username}",
            status_code=status.HTTP_303_SEE_OTHER
        )
        set_sessions_cookie(
            response=response,
            sessions=sessions
        )
        return response

    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []

    return render_template(
        name="login.html",
        context={
            "request": request,
            "error_key": "login_err_invalid",
            "users": usernames
        }
    )


@router.post("/logout")
async def handle_logout(request: Request):
    sessions = get_all_sessions(request)
    user_to_logout = request.query_params.get("user")

    if user_to_logout and user_to_logout in sessions:
        del sessions[user_to_logout]
    else:
        sessions = {}

    response = RedirectResponse(
        url="/ui/",
        status_code=status.HTTP_303_SEE_OTHER
    )

    if not sessions:
        response.delete_cookie("mail_sessions")
        response.delete_cookie("mail_user")
        response.delete_cookie("mail_pass")
    else:
        set_sessions_cookie(
            response=response,
            sessions=sessions
        )

    return response


@router.post("/change-password")
async def handle_change_password(
    request: Request,
    username: str = Form(...),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []

    if new_password != confirm_password:
        return render_template(
            name="change_password.html",
            context={
                "request": request,
                "error_key": "chpw_err_mismatch",
                "user": username,
                "users": usernames
            }
        )

    if not user_manager.verify_user_password(
        username=username,
        password=current_password
    ):
        return render_template(
            name="change_password.html",
            context={
                "request": request,
                "error_key": "chpw_err_wrong_pass",
                "user": username,
                "users": usernames
            }
        )

    success, msg = user_manager.change_user_password(
        username=username,
        password=new_password
    )
    if success:
        return render_template(
            name="change_password.html",
            context={
                "request": request,
                "success_key": "chpw_success",
                "user": username,
                "users": usernames
            }
        )

    return render_template(
        name="change_password.html",
        context={
            "request": request,
            "error_key": "chpw_err_update",
            "error_detail": msg,
            "user": username,
            "users": usernames
        }
    )


@router.post("/delete-user")
async def handle_delete_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_delete: str = Form(...)
):
    _, user_details = user_manager.list_system_users()
    usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []

    if confirm_delete != "DELETE":
        return render_template(
            name="delete_user.html",
            context={
                "request": request,
                "error_key": "del_err_confirm_word",
                "users": usernames,
                "user": username
            }
        )

    if not user_manager.verify_user_password(
        username=username,
        password=password
    ):
        return render_template(
            name="delete_user.html",
            context={
                "request": request,
                "error_key": "del_err_wrong_pass",
                "users": usernames,
                "user": username
            }
        )

    success, msg = user_manager.delete_system_user(username=username)
    if success:
        return render_template(
            name="delete_user.html",
            context={
                "request": request,
                "success_key": "del_success",
                "success_args": {"username": username},
                "users": usernames
            }
        )

    return render_template(
        name="delete_user.html",
        context={
            "request": request,
            "error_key": "del_err_deletion",
            "error_detail": msg,
            "users": usernames,
            "user": username
        }
    )
