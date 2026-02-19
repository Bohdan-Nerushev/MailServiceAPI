from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from app.services import smtp_service, imap_service

router = APIRouter(prefix="/mail", tags=["Mail"])

class EmailSchema(BaseModel):
    to: str  # Використовуємо str замість EmailStr для підтримки .local
    subject: str
    body: str
    from_email: str = None

@router.post("/send")
async def send_mail(email_data: EmailSchema):
    # ... (код відправки)
    success, message = await smtp_service.send_email(
        to_email=email_data.to,
        subject=email_data.subject,
        body=email_data.body,
        from_email=email_data.from_email  # Передаємо відправника
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Помилка відправки: {message}")
    
    return {"message": "Лист успішно надіслано"}

@router.get("/inbox/{username}")
async def get_inbox(username: str, x_password: str = Header(...)):
    """Отримати список останніх листів для користувача."""
    success, result = imap_service.fetch_inbox(username, x_password)
    if not success:
        raise HTTPException(status_code=401, detail=f"Помилка входу або IMAP: {result}")
    return {"inbox": result}

@router.get("/message/{uid}")
async def get_message(uid: str, username: str, x_password: str = Header(...)):
    """Отримати повний текст повідомлення за UID."""
    success, result = imap_service.fetch_message_by_uid(username, x_password, uid)
    if not success:
        raise HTTPException(status_code=404, detail=f"Помилка: {result}")
    return {"message": result}
