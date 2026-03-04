from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from app.services import user_manager

router = APIRouter(prefix="/users", tags=["Benutzer"])

class UserCreate(BaseModel):
    username: str = Field(..., examples=["testuser"])
    password: str = Field(
        ...,
        examples=["SicheresPasswort123!"],
        json_schema_extra={"format": "password"}
    )

class UserPasswordChange(BaseModel):
    current_password: str = Field(
        ...,
        examples=["AltesPasswort123!"],
        json_schema_extra={"format": "password"}
    )
    new_password: str = Field(
        ...,
        examples=["NeuesPasswort456!"],
        json_schema_extra={"format": "password"}
    )

@router.get("/")
async def list_users():
    """Liste aller Systembenutzer abrufen."""
    success, result = user_manager.list_system_users()
    if not success:
        raise HTTPException(status_code=500, detail=result)
    return {"users": result}

@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    """Einen neuen Systembenutzer für E-Mails anlegen."""
    success, message = user_manager.create_system_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=f"Benutzer konnte nicht erstellt werden: {message}")
    return {"message": f"Benutzer {user.username} wurde angelegt"}

@router.put("/{username}/password")
async def change_password(username: str, data: UserPasswordChange):
    """Das Passwort eines bestehenden Benutzers ändern. Erfordert das aktuelle Passwort."""
    # 1. Перевірка актуального пароля
    if not user_manager.verify_user_password(username, data.current_password):
        raise HTTPException(status_code=401, detail="Невірний актуальний пароль")

    # 2. Зміна на новий пароль
    success, message = user_manager.change_user_password(username, data.new_password)
    if not success:
        raise HTTPException(status_code=400, detail=f"Passwort konnte nicht geändert werden: {message}")
    return {"message": f"Passwort für {username} wurde geändert"}



@router.delete("/{username}")
async def delete_user(
    username: str,
    x_admin_password: str = Header(
        ...,
        description="Passwort ",
        json_schema_extra={"format": "password"}
    )
):
    """Einen Benutzer und sein Postfach löschen."""
    import os
    if x_admin_password != os.getenv("SMTP_PASSWORD"):
        raise HTTPException(status_code=403, detail="Ungültiges Admin-Passwort")
        
    success, message = user_manager.delete_system_user(username)
    if not success:
        raise HTTPException(status_code=400, detail=f"Benutzer konnte nicht gelöscht werden: {message}")
    return {"message": f"Benutzer {username} wurde gelöscht"}

