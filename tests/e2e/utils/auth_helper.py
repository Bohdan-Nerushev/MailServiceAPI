import requests
from tests.e2e import config

def get_ui_session(username, password):
    """
    Створює сесію requests та виконує вхід через UI форму login.
    Повертає об'єкт session з встановленими cookies.
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
        
    raise Exception(f"Не вдалося авторизуватися через UI для {username}")
