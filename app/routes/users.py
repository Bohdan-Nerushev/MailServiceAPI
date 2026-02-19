from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.services import user_manager

router = APIRouter(prefix="/users", tags=["Benutzer"])

from pydantic import Field

class UserCreate(BaseModel):
    username: str = Field(..., examples=["testuser"])
    password: str = Field(..., examples=["SicheresPasswort123!"])

class UserPasswordChange(BaseModel):
    password: str = Field(..., examples=["NeuesPasswort456!"])

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

@router.delete("/{username}")
async def delete_user(username: str, x_admin_password: str = Header(..., description="Admin-Passwort aus der .env-Datei")):
    """Einen Benutzer und sein Postfach löschen."""
    import os
    if x_admin_password != os.getenv("SMTP_PASSWORD"):
        raise HTTPException(status_code=403, detail="Ungültiges Admin-Passwort")
        
    success, message = user_manager.delete_system_user(username)
    if not success:
        raise HTTPException(status_code=400, detail=f"Benutzer konnte nicht gelöscht werden: {message}")
    return {"message": f"Benutzer {username} wurde gelöscht"}

@router.put("/{username}/password")
async def change_password(username: str, data: UserPasswordChange):
    """Das Passwort eines bestehenden Benutzers ändern."""
    success, message = user_manager.change_user_password(username, data.password)
    if not success:
        raise HTTPException(status_code=400, detail=f"Passwort konnte nicht geändert werden: {message}")
    return {"message": f"Passwort für {username} wurde geändert"}
