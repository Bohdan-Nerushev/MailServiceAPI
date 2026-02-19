import os
import logging
from imap_tools import MailBox, AND

logger = logging.getLogger(__name__)

def fetch_inbox(username, password, limit=10):
    """Отримує список останніх листів з папки INBOX."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        # Підключаємося до сервера
        with MailBox(imap_server).login(username, password, 'INBOX') as mailbox:
            messages = []
            # Отримуємо останні N листів (сортування за датою від нових)
            for msg in mailbox.fetch(limit=limit, reverse=True):
                messages.append({
                    "uid": msg.uid,
                    "from": msg.from_,
                    "subject": msg.subject,
                    "date": str(msg.date),
                    "text": msg.text,
                    "seen": msg.flags
                })
            return True, messages
    except Exception as e:
        logger.error(f"Помилка IMAP (fetch): {str(e)}")
        return False, str(e)

def fetch_message_by_uid(username, password, uid):
    """Отримує повний текст конкретного листа за його UID."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        with MailBox(imap_server).login(username, password, 'INBOX') as mailbox:
            # Шукаємо лист за UID
            for msg in mailbox.fetch(AND(uid=uid)):
                return True, {
                    "uid": msg.uid,
                    "from": msg.from_,
                    "to": msg.to,
                    "subject": msg.subject,
                    "date": str(msg.date),
                    "text": msg.text,
                    "html": msg.html
                }
            return False, "Лист не знайдено"
    except Exception as e:
        logger.error(f"Помилка IMAP (message): {str(e)}")
        return False, str(e)

def delete_message_by_uid(username, password, uid):
    """Löscht eine E-Mail anhand ihrer UID."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")
    
    try:
        with MailBox(imap_server).login(username, password, 'INBOX') as mailbox:
            # Markiert die E-Mail als gelöscht und entfernt sie
            mailbox.delete(uid)
            return True, f"E-Mail mit UID {uid} wurde gelöscht"
    except Exception as e:
        logger.error(f"Fehler beim Löschen der E-Mail (UID {uid}): {str(e)}")
        return False, str(e)
