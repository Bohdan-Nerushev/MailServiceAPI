import requests
from tests.e2e import config

def get_ui_session(username, password):
    """
    Erstellt eine Requests-Session und führt den Login über das UI-Formular durch.
    Gibt ein Session-Objekt mit gesetzten Cookies zurück.
    """
    session = requests.Session()
    
    # Виконуємо вхід через UI форму
    response = session.post(
        f"{config.BASE_URL}/ui/login",
        data={"username": username, "password": password},
        allow_redirects=True,
        timeout=10
    )
    
    # Перевіряємо, чи ми авторизовані (наявність cookie)
    if "mail_sessions" in session.cookies:
        return session
        
    raise Exception(f"Login über UI für {username} fehlgeschlagen")
