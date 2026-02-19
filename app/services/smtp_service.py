import os
import logging
from email.message import EmailMessage
import aiosmtplib

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, body: str, from_email: str = None):
    """Надсилає лист через асинхронний SMTP клієнт."""
    
    # Створюємо об'єкт повідомлення
    message = EmailMessage()
    message["From"] = from_email or os.getenv("SMTP_USER")
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    # Параметри сервера з .env
    hostname = os.getenv("SMTP_SERVER", "localhost")
    port = int(os.getenv("SMTP_PORT", 587))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")

    try:
        # Для порту 25 на localhost часто не потрібна авторизація
        is_local = hostname in ["localhost", "127.0.0.1"]
        use_auth = not (is_local and port == 25)

        # Параметри підключення
        smtp_args = {
            "hostname": hostname,
            "port": port,
            "use_tls": (port == 465),
            "start_tls": (port == 587)
        }

        # Додаємо авторизацію тільки якщо вона потрібна
        if use_auth and username and password:
            smtp_args["username"] = username
            smtp_args["password"] = password

        await aiosmtplib.send(message, **smtp_args)
        logger.info(f"Лист успішно надіслано на {to_email}")
        return True, "Лист надіслано"
    except Exception as e:
        logger.error(f"Помилка SMTP: {str(e)}")
        return False, str(e)
