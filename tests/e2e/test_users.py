import requests
import os
import sys
import logging
from dotenv import load_dotenv

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("e2e_test")

# Umgebungsvariablen laden
load_dotenv()

BASE_URL = "http://127.0.0.1:8090"
ADMIN_PASSWORD = os.getenv("SMTP_PASSWORD")

# Testdaten
TEST_USER = "e2e_test_user"
INITIAL_PASS = "InitialPass123!"
NEW_PASS = "UpdatedPass456!"

def get_users():
    """Ruft die Liste aller Benutzer ab."""
    logger.info("Rufe Benutzerliste ab...")
    resp = requests.get(f"{BASE_URL}/users/")
    if resp.status_code == 200:
        users = resp.json().get("users", [])
        logger.info(f"{len(users)} Benutzer gefunden.")
        return users
    else:
        logger.error(f"Fehler beim Abrufen der Liste: {resp.text}")
        return []

def delete_user(username: str):
    """Löscht einen Benutzer."""
    logger.info(f"Lösche Benutzer {username}...")
    headers = {"X-Admin-Password": ADMIN_PASSWORD}
    resp = requests.delete(f"{BASE_URL}/users/{username}", headers=headers)
    if resp.status_code == 200:
        logger.info(f"Benutzer {username} erfolgreich gelöscht.")
        return True
    else:
        logger.error(f"Fehler beim Löschen: {resp.text}")
        return False

def create_user(username: str, password: str):
    """Erstellt einen neuen Benutzer."""
    logger.info(f"Erstelle Benutzer {username}...")
    payload = {"username": username, "password": password}
    resp = requests.post(f"{BASE_URL}/users/", json=payload)
    if resp.status_code == 201:
        logger.info("Benutzer erfolgreich erstellt.")
        return True
    else:
        logger.error(f"Fehler beim Erstellen: {resp.text}")
        return False

def change_password(username: str, old_pass: str, new_pass: str, expect_success: bool = True):
    """Ändert das Passwort eines Benutzers."""
    logger.info(f"Ändere Passwort für {username} (Erwarteter Erfolg: {expect_success})...")
    payload = {
        "current_password": old_pass,
        "new_password": new_pass
    }
    resp = requests.put(f"{BASE_URL}/users/{username}/password", json=payload)
    
    if expect_success:
        if resp.status_code == 200:
            logger.info("Passwort erfolgreich geändert.")
            return True
        else:
            logger.error(f"Fehler bei Passwortänderung: {resp.text}")
            return False
    else:
        if resp.status_code == 401:
            logger.info("Zugriff wie erwartet verweigert (401 Unauthorized).")
            return True
        else:
            logger.error(f"Unerwarteter Statuscode: {resp.status_code}")
            return False

def run_e2e_test():
    """Führt den vollständigen E2E-Test-Szenario aus."""
    logger.info(f"Starte E2E-Test für Benutzer: {TEST_USER}")
    
    # 1. Vorbereitung
    users = get_users()
    if TEST_USER in users:
        logger.warning(f"Benutzer {TEST_USER} existiert bereits. Bereinige Testumgebung...")
        delete_user(TEST_USER)

    try:
        # 2. Erstellung
        if not create_user(TEST_USER, INITIAL_PASS):
            sys.exit(1)

        # 3. Negativ-Test: Falsches Passwort
        if not change_password(TEST_USER, "FalschesPasswort", NEW_PASS, expect_success=False):
            sys.exit(1)

        # 4. Positiv-Test: Korrektes Passwort
        if not change_password(TEST_USER, INITIAL_PASS, NEW_PASS, expect_success=True):
            sys.exit(1)

        logger.info("E2E-Test erfolgreich abgeschlossen!")

    finally:
        # 5. Abschluss
        delete_user(TEST_USER)

if __name__ == "__main__":
    try:
        run_e2e_test()
    except Exception as e:
        logger.critical(f"Kritischer Fehler während des Tests: {e}")
        sys.exit(1)
