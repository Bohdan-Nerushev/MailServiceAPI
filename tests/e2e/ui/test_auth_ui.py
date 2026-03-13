import requests
import uuid
from tests.e2e import config
from tests.e2e.utils import user_helper

def test_ui_registration_and_login():
    """
    Позитивний тест UI: Реєстрація -> Логін -> Перевірка авторизації.
    """
    print("Start: test_ui_registration_and_login")
    session = requests.Session()
    username = f"ui_{uuid.uuid4().hex[:6]}"
    password = config.DEFAULT_PASSWORD

    try:
        # 1. Реєстрація (Registration Flow)
        reg_resp = session.post(
            f"{config.BASE_URL}/ui/register",
            data={
                "username": username,
                "password": password,
                "confirm_password": password
            },
            allow_redirects=True,
            timeout=10
        )
        assert reg_resp.status_code == 200
        assert "reg_success" in reg_resp.text or "успішно" in reg_resp.text.lower()
        print(f"  - Registrierung von Benutzer {username} über UI erfolgreich")

        # 2. Логін (Login Flow)
        login_resp = session.post(
            f"{config.BASE_URL}/ui/login",
            data={"username": username, "password": password},
            allow_redirects=True,
            timeout=10
        )
        assert login_resp.status_code == 200
        assert "mail_sessions" in session.cookies
        print("  - Login über UI erfolgreich (Cookies erhalten)")

        # 3. Перевірка Logout
        logout_resp = session.post(
            f"{config.BASE_URL}/ui/logout",
            params={"user": username},
            allow_redirects=True,
            timeout=10
        )
        assert logout_resp.status_code == 200
        # Cookie повинно бути або видалено, або змінено (якщо сесія пуста)
        print("  - Logout über UI erfolgreich")

    finally:
        user_helper.delete_user(username, password)

def test_ui_change_password():
    """
    Позитивний тест UI: Зміна паролю через веб-форму.
    """
    print("Start: test_ui_change_password")
    session = requests.Session()
    new_password = "NewUISecretPass123!"
    user = None
    try:
        user = user_helper.create_unique_user()
        # Логін
        session.post(f"{config.BASE_URL}/ui/login", data={"username": user['username'], "password": user['password']}, timeout=10)
        
        # Зміна паролю
        resp = session.post(
            f"{config.BASE_URL}/ui/change-password",
            data={
                "username": user['username'],
                "current_password": user['password'],
                "new_password": new_password,
                "confirm_password": new_password
            },
            allow_redirects=True,
            timeout=10
        )
        assert resp.status_code == 200
        assert "chpw_success" in resp.text or "успішно" in resp.text.lower()
        print("  - Passwort erfolgreich über UI geändert")

        # Перевірка нового паролю (через нову сесію)
        new_session = requests.Session()
        login_resp = new_session.post(
            f"{config.BASE_URL}/ui/login",
            data={"username": user['username'], "password": new_password},
            timeout=10
        )
        assert "mail_sessions" in new_session.cookies
        print("  - Login mit neuem Passwort über UI erfolgreich")

    finally:
        # Прибираємо за собою (використовуємо новий пароль для видалення)
        if user:
            requests.delete(f"{config.BASE_URL}/users/{user['username']}", headers={"X-User-Password": new_password}, timeout=10)

def test_ui_delete_user():
    """
    Позитивний тест UI: Видалення аккаунту через веб-форму підтвердження.
    """
    print("Start: test_ui_delete_user")
    session = requests.Session()
    user = None
    try:
        user = user_helper.create_unique_user()
        # Логін
        session.post(f"{config.BASE_URL}/ui/login", data={"username": user['username'], "password": user['password']}, timeout=10)
        
        # Видалення аккаунту
        resp = session.post(
            f"{config.BASE_URL}/ui/delete-user",
            data={
                "username": user['username'],
                "password": user['password'],
                "confirm_delete": "DELETE"
            },
            allow_redirects=True,
            timeout=10
        )
        assert resp.status_code == 200
        assert "del_success" in resp.text or "видалено" in resp.text.lower()
        print(f"  - Benutzer {user['username']} über UI gelöscht")

    finally:
        # Про всяк випадок спроба видалення через API, якщо UI тест провалився
        if user:
            user_helper.delete_user(user['username'], user['password'])

def test_ui_login_invalid():
    """
    Негативний тест UI: Вхід з неправильним паролем.
    """
    print("Start: test_ui_login_invalid")
    session = requests.Session()
    
    resp = session.post(
        f"{config.BASE_URL}/ui/login",
        data={"username": "non-existent-user", "password": "wrong-password"},
        allow_redirects=True,
        timeout=10
    )
    assert resp.status_code == 200 # Сторінка повинна відрендеритися з помилкою
    assert "login_err_invalid" in resp.text or "невірний" in resp.text.lower()
    print("  - Prüfung auf falsches Login über UI bestanden")

def test_ui_unauthorized_access():
    """
    Негативний тест UI: Спроба доступу до інбоксу без логіну.
    """
    print("Start: test_ui_unauthorized_access")
    session = requests.Session()
    resp = session.get(f"{config.BASE_URL}/ui/inbox", allow_redirects=True, timeout=10)
    # Очікуємо редирект на сторінку логіну
    assert "login" in resp.url
    print("  - Redirect für nicht autorisierten Benutzer zur Login-Seite bestanden")

def test_ui_registration_validation():
    """
    Негативний тест UI: Валідація реєстрації (паролі не збігаються).
    """
    print("Start: test_ui_registration_validation")
    session = requests.Session()
    username = f"fail_reg_{uuid.uuid4().hex[:6]}"
    
    try:
        resp = session.post(
            f"{config.BASE_URL}/ui/register",
            data={
                "username": username,
                "password": "Password123",
                "confirm_password": "MismatchingPassword"
            },
            allow_redirects=True,
            timeout=10
        )
        # Очікуємо, що ми залишимось на сторінці реєстрації або побачимо помилку
        assert "register" in resp.url or "bg-rose-50" in resp.text or "не збігаються" in resp.text.lower()
        print("  - Prüfung auf nicht übereinstimmende Passwörter bei der Registrierung bestanden")
    finally:
        # Про всяк випадок спроба видалення (використовуємо пароль, якщо він випадково встановився)
        user_helper.delete_user(username, "Password123")
        # Також може бути, що користувач був створений без пароля або з іншим паролем у разі бага

def test_ui_change_password_invalid():
    """
    Негативний тест UI: Спроба зміни пароля з неправильним старим паролем.
    """
    print("Start: test_ui_change_password_invalid")
    session = requests.Session()
    user = None
    try:
        user = user_helper.create_unique_user()
        session.post(f"{config.BASE_URL}/ui/login", data={"username": user['username'], "password": user['password']}, timeout=10)
        
        resp = session.post(
            f"{config.BASE_URL}/ui/change-password",
            data={
                "username": user['username'],
                "current_password": "WrongOldPassword",
                "new_password": "NewPass123!",
                "confirm_password": "NewPass123!"
            },
            allow_redirects=True,
            timeout=10
        )
        assert "bg-rose-50" in resp.text or "невірний" in resp.text.lower() or resp.status_code != 200
        print("  - Prüfung на falsches altes Passwort bestanden")
    finally:
        if user:
            user_helper.delete_user(user['username'], user['password'])

def test_ui_delete_user_invalid_confirm():
    """
    Негативний тест UI: Видалення аккаунту з неправильним словом-підтвердженням.
    """
    print("Start: test_ui_delete_user_invalid_confirm")
    session = requests.Session()
    user = None
    try:
        user = user_helper.create_unique_user()
        session.post(f"{config.BASE_URL}/ui/login", data={"username": user['username'], "password": user['password']}, timeout=10)
        
        resp = session.post(
            f"{config.BASE_URL}/ui/delete-user",
            data={
                "username": user['username'],
                "password": user['password'],
                "confirm_delete": "WRONG_WORD"
            },
            allow_redirects=True,
            timeout=10
        )
        # Перевіряємо, що ми все ще бачимо форму видалення або помилку, а не успіх
        assert "DELETE" in resp.text or "bg-rose-50" in resp.text
        print("  - Prüfung auf falsches Bestätigungswort beim Löschen bestanden")
    finally:
        if user:
            user_helper.delete_user(user['username'], user['password'])

if __name__ == "__main__":
    try:
        test_ui_registration_and_login()
        test_ui_change_password()
        test_ui_delete_user()
        test_ui_login_invalid()
        test_ui_unauthorized_access()
        test_ui_registration_validation()
        test_ui_change_password_invalid()
        test_ui_delete_user_invalid_confirm()
        print("Alle Auth UI Tests (positiv & negativ) erfolgreich bestanden!\n")
    except Exception as e:
        print(f"Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
