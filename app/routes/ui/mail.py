import os
from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.services import imap_service
from app.services import smtp_service
from app.services import user_manager
from app.routes.ui.utils import render_template
from app.routes.ui.utils import get_session_user

router = APIRouter(tags=["UI Mail"])


@router.get(
    "/inbox",
    response_class=HTMLResponse
)
async def inbox_page(
    request: Request,
    folder: str = "INBOX",
    error: str = None,
    page: int = 1
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    limit = 10
    offset = (page - 1) * limit

    success, mails = imap_service.fetch_emails(
        username=user["username"],
        password=user["password"],
        folder=folder,
        limit=limit,
        offset=offset
    )

    _, counts = imap_service.fetch_folder_counts(
        username=user["username"],
        password=user["password"]
    )

    total_emails = counts.get(folder, 0) if counts else 0
    total_pages = (total_emails + limit - 1) // limit if total_emails > 0 else 1

    if not success:
        _, user_details = user_manager.list_system_users()
        usernames = [u["username"] for u in user_details] if isinstance(user_details, list) else []
        return render_template(
            name="login.html",
            context={
                "request": request,
                "error": f"IMAP Error ({folder}): {mails}",
                "users": usernames
            }
        )

    return render_template(
        name="inbox.html",
        context={
            "request": request,
            "mails": mails,
            "user": user,
            "current_folder": folder,
            "error": error,
            "counts": counts,
            "current_page": page,
            "total_pages": total_pages
        }
    )


@router.get(
    "/compose",
    response_class=HTMLResponse
)
async def compose_page(
    request: Request,
    error: str = None
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    _, counts = imap_service.fetch_folder_counts(
        username=user["username"],
        password=user["password"]
    )
    return render_template(
        name="compose.html",
        context={
            "request": request,
            "user": user,
            "error": error,
            "counts": counts
        }
    )


@router.get(
    "/mail/{uid}",
    response_class=HTMLResponse
)
async def view_mail_page(
    request: Request,
    uid: str,
    folder: str = "INBOX"
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    success, mail = imap_service.fetch_message_by_uid(
        username=user["username"],
        password=user["password"],
        uid=uid,
        folder=folder
    )
    _, counts = imap_service.fetch_folder_counts(
        username=user["username"],
        password=user["password"]
    )

    if not success:
        return RedirectResponse(
            url=f"/ui/inbox?folder={folder}&error={mail}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return render_template(
        name="view_mail.html",
        context={
            "request": request,
            "mail": mail,
            "user": user,
            "current_folder": folder,
            "counts": counts
        }
    )


@router.post("/compose")
async def handle_send_mail(
    request: Request,
    to: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...)
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    domain = os.getenv('DOMAIN', 'localhost')
    success, msg = await smtp_service.send_email(
        to_email=to,
        subject=subject,
        body=body,
        from_email=f"{user['username']}@{domain}",
        auth_user=user["username"],
        auth_pass=user["password"]
    )

    if success:
        imap_service.append_to_sent(
            username=user["username"],
            password=user["password"],
            to_email=to,
            subject=subject,
            body=body
        )
        return render_template(
            name="compose.html",
            context={
                "request": request,
                "success_msg": True,
                "recipient": to,
                "user": user
            }
        )

    return render_template(
        name="compose.html",
        context={
            "request": request,
            "error": msg,
            "recipient": to,
            "subject": subject,
            "body": body,
            "user": user
        }
    )


@router.post("/mail/{uid}/delete")
async def handle_delete_mail(
    request: Request,
    uid: str,
    folder: str = "INBOX"
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    success, msg = imap_service.move_message(
        username=user["username"],
        password=user["password"],
        uid=uid,
        source_folder=folder,
        dest_folder="Trash"
    )

    if success:
        return render_template(
            name="view_mail.html",
            context={
                "request": request,
                "success_msg": True,
                "mail": {"uid": uid},
                "user": user,
                "current_folder": folder,
                "redirect_url": f"/ui/inbox?folder={folder}&user={user['username']}"
            }
        )

    return RedirectResponse(
        url=f"/ui/inbox?folder={folder}&error={msg}&user={user['username']}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/mail/{uid}/restore")
async def handle_restore_mail(
    request: Request,
    uid: str
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    success, msg = imap_service.move_message(
        username=user["username"],
        password=user["password"],
        uid=uid,
        source_folder="Trash",
        dest_folder="INBOX"
    )
    return RedirectResponse(
        url=f"/ui/inbox?folder=Trash&user={user['username']}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/mail/{uid}/permanent-delete")
async def handle_permanent_delete_mail(
    request: Request,
    uid: str
):
    user = get_session_user(request)
    if not user:
        return RedirectResponse(
            url="/ui/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    success, msg = imap_service.delete_permanent(
        username=user["username"],
        password=user["password"],
        uid=uid,
        folder="Trash"
    )
    return RedirectResponse(
        url=f"/ui/inbox?folder=Trash&user={user['username']}",
        status_code=status.HTTP_303_SEE_OTHER
    )
