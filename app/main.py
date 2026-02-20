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

# Tags Metadaten für die Reihenfolge im Swagger UI
tags_metadata = [
    {
        "name": "System",
        "description": "Betriebsstatus und Gesundheitsprüfung.",
    },
    {
        "name": "Benutzer",
        "description": "Verwaltung von Systembenutzern.",
    },
    {
        "name": "E-Mail",
        "description": "Senden und Empfangen von Nachrichten.",
    },
]

app = FastAPI(
    title="Mail Service API",
    description="API zur Verwaltung des Mailservers (Postfix/Dovecot)",
    version="0.1.0",
    openapi_tags=tags_metadata
)

from app.services import system_service

@app.get("/health", tags=["System"])
async def health_check():
    """Überprüft den Status des API-Servers, der Mail-Dienste und der Server-Ressourcen."""
    postfix_details = system_service.get_service_details("postfix")
    dovecot_details = system_service.get_service_details("dovecot")
    system_metrics = system_service.get_system_info()
    network_info = system_service.get_network_info()
    
    postfix_active = postfix_details.get("is_active", False)
    dovecot_active = dovecot_details.get("is_active", False)
    
    status = "OK" if postfix_active and dovecot_active else "DEGRADED"
    
    return {
        "status": status,
        "api_service": "running",
        "mail_services": {
            "postfix": postfix_details,
            "dovecot": dovecot_details
        },
        "system_info": system_metrics,
        "network_info": network_info,
        "environment": {
            "debug_mode": os.getenv("DEBUG", "False"),
            "domain": os.getenv("SMTP_SERVER", "localhost")
        }
    }

# Підключаємо роути
app.include_router(users.router)
app.include_router(mail.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Mail Service API ist aktiv. Gehen Sie zu /docs für die Dokumentation."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
