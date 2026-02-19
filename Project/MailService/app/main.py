import os
from fastapi import FastAPI
from dotenv import load_dotenv

import logging

# Налаштування логування у файл
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Завантажуємо змінні оточення
load_dotenv()

from app.routes import users, mail

app = FastAPI(
    title="Mail Service API",
    description="API для керування поштовим сервером (Postfix/Dovecot)",
    version="0.1.0"
)

# Підключаємо роути
app.include_router(users.router)
app.include_router(mail.router)

@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "status": "Mail Service is running",
        "debug_mode": os.getenv("DEBUG", "False")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
