import os
import logging
from pprint import pprint

from imap_tools import MailBox, AND

logger = logging.getLogger(__name__)

def fetch_emails(username, password, folder='INBOX', limit=10):
    """Отримує список листів з вказаної папки з лімітом."""
    imap_server = os.getenv("IMAP_SERVER", "localhost")

    try:
        with MailBox(imap_server).login(username, password) as mailbox:
            # Перевіряємо наявність папки
            if folder not in [f.name for f in mailbox.folder.list()]:
                logger.warning(f"Folder {folder} does not exist for user {username}. Returning empty list.")
                return True, []
            
            mailbox.folder.set(folder)
            messages = []
            for msg in mailbox.fetch(limit=limit, reverse=True):
                messages.append({
                    "uid": msg.uid,
                    "sender": msg.from_ if msg.from_ else "Unknown",
                    "subject": msg.subject if msg.subject else "(No Subject)",
                    "date": str(msg.date.strftime("%d %b, %H:%M")),
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
        with MailBox(imap_server).login(username, password, folder) as mailbox:
            # Suchen Sie den Brief anhand seiner UID
            for msg in mailbox.fetch(AND(uid=uid)):
                return True, {
                    "uid": msg.uid,
                    "sender": msg.from_ if msg.from_ else "Unknown",
                    "to": msg.to,
                    "subject": msg.subject if msg.subject else "(No Subject)",
                    "date": str(msg.date.strftime("%d %b %Y, %H:%M")),
                    "body": msg.text,
                    "html": msg.html
                }
            return False, "Лист не знайдено"
    except Exception as e:
        logger.error(f"Помилка IMAP (message, {folder}): {str(e)}")
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
