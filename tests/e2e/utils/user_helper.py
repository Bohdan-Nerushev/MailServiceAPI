import requests
from tests.e2e import config
import uuid

def create_unique_user():
    """
    Erstellt einen eindeutigen Benutzer für den Test.
    Gibt ein Dictionary mit username und password zurück.
    """
    username = f"{config.TEST_USER_PREFIX}{uuid.uuid4().hex[:8]}"
    password = config.DEFAULT_PASSWORD
    
    response = requests.post(
        f"{config.BASE_URL}/users/",
        json={"username": username, "password": password},
        timeout=10
    )
    
    if response.status_code == 201:
        return {"username": username, "password": password}
    raise Exception(f"Fehler bei der Erstellung des Testbenutzers: {response.text}")

def delete_user(username, password):
    """
    Löscht einen Testbenutzer.
    Verwendet den Header X-User-Password zur Autorisierung der Löschung.
    """
    requests.delete(
        f"{config.BASE_URL}/users/{username}",
        headers={"X-User-Password": password},
        timeout=10
    )
