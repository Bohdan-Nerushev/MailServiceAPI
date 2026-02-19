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
    description="API zur Verwaltung des Mailservers (Postfix/Dovecot)",
    version="0.1.0"
)

# Підключаємо роути
app.include_router(users.router)
app.include_router(mail.router)

from app.services import system_service

@app.get("/health", tags=["System"])
async def health_check():
    """Überprüft den Status des API-Servers und der Mail-Dienste (Postfix/Dovecot)."""
    postfix_active = system_service.get_service_status("postfix")
    dovecot_active = system_service.get_service_status("dovecot")
    
    status = "OK" if postfix_active and dovecot_active else "DEGRADED"
    
    return {
        "status": status,
        "api_service": "running",
        "mail_services": {
            "postfix": "active" if postfix_active else "inactive",
            "dovecot": "active" if dovecot_active else "inactive"
        },
        "environment": {
            "debug_mode": os.getenv("DEBUG", "False"),
            "domain": os.getenv("SMTP_SERVER", "localhost")
        }
    }

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Mail Service API ist aktiv. Gehen Sie zu /docs für die Dokumentation."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
