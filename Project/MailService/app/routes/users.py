from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.services import user_manager

router = APIRouter(prefix="/users", tags=["Users"])

class UserCreate(BaseModel):
    username: str
    password: str

class UserPasswordChange(BaseModel):
    password: str

@router.get("/")
async def list_users():
    success, result = user_manager.list_system_users()
    if not success:
        raise HTTPException(status_code=500, detail=result)
    return {"users": result}

@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    success, message = user_manager.create_system_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=f"Не вдалося створити користувача: {message}")
    return {"message": f"Користувач {user.username} створений"}

@router.delete("/{username}")
async def delete_user(username: str, x_admin_password: str = Header(...)):
    # Перевірка пароля адміна (беремо з нашого .env для bnerushev як приклад)
    import os
    if x_admin_password != os.getenv("SMTP_PASSWORD"):
        raise HTTPException(status_code=403, detail="Невірний пароль адміністратора")
        
    success, message = user_manager.delete_system_user(username)
    if not success:
        raise HTTPException(status_code=400, detail=f"Не вдалося видалити користувача: {message}")
    return {"message": f"Користувач {username} видалений"}

@router.put("/{username}/password")
async def change_password(username: str, data: UserPasswordChange):
    success, message = user_manager.change_user_password(username, data.password)
    if not success:
        raise HTTPException(status_code=400, detail=f"Не вдалося змінити пароль: {message}")
    return {"message": f"Пароль для {username} змінено"}
