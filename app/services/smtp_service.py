import os
import logging
import ssl
from email.message import EmailMessage
import aiosmtplib

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, body: str, from_email: str = None):
    """Send an email through an asynchronous SMTP client."""
    
    # Erstellen Sie ein E-Mail-Objekt
    message = EmailMessage()
    message["From"] = from_email or os.getenv("SMTP_USER")
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    # Parameter des Servers aus .env
    hostname = os.getenv("SMTP_SERVER", "localhost")
    port = int(os.getenv("SMTP_PORT", 587))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    
    # SSL-Validierung deaktivieren, falls MAIL_VALIDATE_CERTS=False
    validate_certs = os.getenv("MAIL_VALIDATE_CERTS", "False").lower() == "true"

    try:
        # Für Port 25 auf localhost ist die Authentifizierung oft nicht erforderlich
        is_local = hostname in ["localhost", "127.0.0.1"]
        use_auth = not (is_local and port == 25)

        # Parameter der Verbindung
        smtp_args = {
            "hostname": hostname,
            "port": port,
            "use_tls": (port == 465),
            "start_tls": (port == 587),
            "validate_certs": validate_certs
        }

        # Hinzufugen der Authentifizierung, wenn sie notwendig ist
        if use_auth and username and password:
            smtp_args["username"] = username
            smtp_args["password"] = password

        await aiosmtplib.send(message, **smtp_args)
        logger.info(f"E-Mail erfolgreich versendet an {to_email}")
        return True, "E-Mail versendet"
    except Exception as e:
        logger.error(f"SMTP-Fehler: {str(e)}")
        return False, str(e)
