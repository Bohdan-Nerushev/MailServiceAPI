import os
import logging
from app.services.time_service import time_service
from imap_tools import MailBox, AND

logger = logging.getLogger(__name__)

import itertools
import ssl

def get_mailbox(hostname):
    """Отримує налаштований об'єкт MailBox з можливістю відключення перевірки SSL."""
    validate_certs = os.getenv("MAIL_VALIDATE_CERTS", "False").lower() == "true"
    if not validate_certs:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return MailBox(hostname, ssl_context=context)
    return MailBox(hostname)

def fetch_emails(username, password, folder='INBOX', limit=10, offset=0):
    """Отримує список листів з вказаної папки з лімітом."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")

    try:
        with get_mailbox(imap_server).login(username, password) as mailbox:
            # Перевіряємо наявність папки
            if folder not in [f.name for f in mailbox.folder.list()]:
                logger.warning(f"Folder {folder} does not exist for user {username}. Returning empty list.")
                return True, []
            
            mailbox.folder.set(folder)
            messages = []
            for msg in itertools.islice(mailbox.fetch(reverse=True), offset, offset + limit):
                # Конвертуємо в налаштовану таймзону
                date_str = time_service.to_display_string(msg.date, "%d %b, %H:%M") if msg.date else "Невідомо"
                messages.append({
                    "uid": msg.uid,
                    "sender": msg.from_ if msg.from_ else "Unknown",
                    "subject": msg.subject if msg.subject else "(No Subject)",
                    "date": date_str,
                    "text": msg.text,
                    "snippet": msg.text[:100] if msg.text else "",
                    "seen": msg.flags
                })

            return True, messages
    except Exception as e:
        logger.error(f"IMAP-Fehler ({folder}): {str(e)}")
        return False, str(e)


def fetch_message_by_uid(username, password, uid, folder='INBOX'):
    """Erhalten Sie den vollständigen Text eines bestimmten Briefes anhand seiner UID."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        with get_mailbox(imap_server).login(username, password, folder) as mailbox:
            # Suchen Sie den Brief anhand seiner UID
            for msg in mailbox.fetch(AND(uid=uid)):
                date_str = time_service.to_display_string(msg.date, "%d %b %Y, %H:%M") if msg.date else "Невідомо"
                return True, {
                    "uid": msg.uid,
                    "sender": msg.from_ if msg.from_ else "Unknown",
                    "to": msg.to,
                    "subject": msg.subject if msg.subject else "(No Subject)",
                    "date": date_str,
                    "body": msg.text,
                    "html": msg.html
                }
            return False, "Лист не знайдено"
    except Exception as e:
        logger.error(f"Помилка IMAP (message, {folder}): {str(e)}")
        return False, str(e)

def delete_permanent(username, password, uid, folder='INBOX'):
    """Видаляє лист назавжди з вказаної папки."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        with get_mailbox(imap_server).login(username, password, folder) as mailbox:
            mailbox.delete(uid)
            return True, f"Лист {uid} видалено назавжди з {folder}"
    except Exception as e:
        logger.error(f"Помилка видалення (UID {uid}, folder {folder}): {str(e)}")
        return False, str(e)

def move_message(username, password, uid, source_folder, target_folder):
    """Переміщує лист з однієї папки в іншу."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        with get_mailbox(imap_server).login(username, password, source_folder) as mailbox:
            # Створюємо цільову папку, якщо вона не існує
            if target_folder not in [f.name for f in mailbox.folder.list()]:
                 mailbox.folder.create(target_folder)
            
            mailbox.move(uid, target_folder)
            return True, f"Лист переміщено в {target_folder}"
    except Exception as e:
        logger.error(f"Помилка переміщення (UID {uid}, {source_folder} -> {target_folder}): {str(e)}")
        return False, str(e)
def fetch_folder_counts(username, password):
    """Отримує кількість листів у папках INBOX, Sent та Trash."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    counts = {"INBOX": 0, "Sent": 0, "Trash": 0}
    
    try:
        with get_mailbox(imap_server).login(username, password) as mailbox:
            folders = [f.name for f in mailbox.folder.list()]
            for folder in counts.keys():
                if folder in folders:
                    mailbox.folder.set(folder)
                    counts[folder] = mailbox.folder.status(folder).get('MESSAGES', 0)
            return True, counts
    except Exception as e:
        logger.error(f"Помилка отримання лічильників: {str(e)}")
        return False, str(e)

from email.message import EmailMessage
from imap_tools import MailMessageFlags

def append_to_sent(username, password, to_email, subject, body):
    """Saves a sent email to the Sent folder via IMAP APPEND."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    domain = os.getenv("DOMAIN", "localhost")
    from_email = f"{username}@{domain}"

    try:
        with get_mailbox(imap_server).login(username, password) as mailbox:
            folder_names = [f.name for f in mailbox.folder.list()]
            if 'Sent' not in folder_names:
                mailbox.folder.create('Sent')

            import email.utils
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Date'] = email.utils.formatdate(localtime=True)
            msg['Message-ID'] = email.utils.make_msgid(domain=domain)
            msg.set_content(body)

            mailbox.append(
                msg.as_bytes(),
                folder='Sent',
                dt=None,
                flag_set=[MailMessageFlags.SEEN]
            )
            logger.info(f"Email appended to Sent folder for user {username}")
            return True, "Saved to Sent"
    except Exception as e:
        logger.error(f"append_to_sent failed for user {username}: {str(e)}")
        return False, str(e)
