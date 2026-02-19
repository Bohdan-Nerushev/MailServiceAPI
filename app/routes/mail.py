from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from app.services import smtp_service, imap_service

router = APIRouter(prefix="/mail", tags=["E-Mail"])

from pydantic import Field

class EmailSchema(BaseModel):
    to: str = Field(..., examples=["admin@lehrwerkstatt"])
    subject: str = Field(..., examples=["Test-E-Mail"])
    body: str = Field(..., examples=["Dies ist eine Test-Nachricht vom Mail-Service."])
    from_email: str = Field(None, examples=["testuser@lehrwerkstatt"])

@router.post("/send")
async def send_mail(email_data: EmailSchema):
    """Eine E-Mail über den lokalen SMTP-Server versenden."""
    success, message = await smtp_service.send_email(
        to_email=email_data.to,
        subject=email_data.subject,
        body=email_data.body,
        from_email=email_data.from_email
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=f"Fehler beim Senden: {message}")
    
    return {"message": "E-Mail erfolgreich versendet"}

@router.get("/inbox/{username}")
async def get_inbox(username: str, x_password: str = Header(..., description="Passwort des E-Mail-Kontos")):
    """Liste der neuesten E-Mails im Posteingang abrufen."""
    success, result = imap_service.fetch_inbox(username, x_password)
    if not success:
        raise HTTPException(status_code=401, detail=f"Login- oder IMAP-Fehler: {result}")
    return {"inbox": result}

@router.get("/message/{uid}")
async def get_message(uid: str, username: str, x_password: str = Header(..., description="Passwort des E-Mail-Kontos")):
    """Vollständigen Inhalt einer Nachricht anhand ihrer UID abrufen."""
    success, result = imap_service.fetch_message_by_uid(username, x_password, uid)
    if not success:
        raise HTTPException(status_code=404, detail=f"Fehler: {result}")
    return {"message": result}
