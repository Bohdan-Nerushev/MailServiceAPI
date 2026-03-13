import requests
import uuid
from tests.e2e import config
from tests.e2e.utils import user_helper

def test_user_lifecycle():
    """
    Позитивний тест: Створення -> Отримання списку -> Зміна паролю -> Видалення.
    """
    print("Start: test_user_lifecycle")
    
    unique_name = f"{config.TEST_USER_PREFIX}{uuid.uuid4().hex[:6]}"
    password = config.DEFAULT_PASSWORD
    new_password = "NewSecurePassword123!"
    
    try:
        # 1. Створення користувача (Positive)
        create_resp = requests.post(
            f"{config.BASE_URL}/users/",
            json={"username": unique_name, "password": password},
            timeout=10
        )
        assert create_resp.status_code == 201, f"Erwartet 201, erhalten {create_resp.status_code}: {create_resp.text}"
        print(f"  - Benutzer {unique_name} erstellt")

        # 2. Отримання списку та перевірка наявності (List Users)
        list_resp = requests.get(f"{config.BASE_URL}/users/", timeout=10)
        assert list_resp.status_code == 200
        users = list_resp.json().get("users", [])
        assert any(u['username'] == unique_name for u in users), f"Benutzer {unique_name} nicht in der Liste gefunden"
        print("  - Benutzer in der Liste gefunden")

        # 3. Зміна паролю (Change Password)
        change_resp = requests.put(
            f"{config.BASE_URL}/users/{unique_name}/password",
            json={
                "current_password": password,
                "new_password": new_password
            },
            timeout=10
        )
        assert change_resp.status_code == 200
        print("  - Passwort erfolgreich geändert")

        # 4. Перевірка негативного кейсу: спроба створити дублікат (Negative)
        dup_resp = requests.post(
            f"{config.BASE_URL}/users/",
            json={"username": unique_name, "password": password},
            timeout=10
        )
        assert dup_resp.status_code == 400, "Erwartet 400 beim Erstellen eines Duplikats"
        print("  - Prüfung auf Duplikat erfolgreich (Code 400)")

    finally:
        # 5. Löschen (Delete)
        print(f"  - Löschen von Benutzer {unique_name}")
        # Спробуємо видалити з новим паролем (якщо він змінився)
        del_resp = requests.delete(
            f"{config.BASE_URL}/users/{unique_name}",
            headers={"X-User-Password": new_password},
            timeout=10
        )
        # Якщо пароль не встиг змінитися (помилка вище), пробуємо старий
        if del_resp.status_code != 200:
             requests.delete(
                f"{config.BASE_URL}/users/{unique_name}",
                headers={"X-User-Password": password},
                timeout=10
            )

def test_delete_user_invalid_password():
    """
    Негативний тест: Спроба видалення користувача з неправильним паролем.
    """
    print("Start: test_delete_user_invalid_password")
    user = None
    try:
        user = user_helper.create_unique_user()
        resp = requests.delete(
            f"{config.BASE_URL}/users/{user['username']}",
            headers={"X-User-Password": "wrong_password"},
            timeout=10
        )
        assert resp.status_code == 401, f"Erwartet 401, erhalten {resp.status_code}"
        print("  - Test auf falsches Passwort beim Löschen bestanden")
    finally:
        if user:
            user_helper.delete_user(user['username'], user['password'])

def test_create_user_invalid():
    """
    Негативний тест: Спроба створення користувача з некоректними даними.
    """
    print("Start: test_create_user_invalid")
    
    # Порожній пароль
    username1 = f"invalid_{uuid.uuid4().hex[:6]}"
    try:
        resp = requests.post(
            f"{config.BASE_URL}/users",
            json={"username": username1, "password": ""},
            timeout=10
        )
        assert resp.status_code in [400, 422]
        print("  - Validierung leeres Passwort bestanden (leeres Passwort)")
    finally:
        # Спроба видалення на випадок багу сервера
        user_helper.delete_user(username1, "")

    # Порожній юзернейм
    try:
        resp = requests.post(
            f"{config.BASE_URL}/users",
            json={"username": "", "password": "SomePassword123!"},
            timeout=10
        )
        assert resp.status_code in [400, 422]
        print("  - Validierung leerer Benutzername bestanden")
    finally:
        # Тут юзернейм порожній, тому видаляти нікого
        pass

def test_access_alien_data():
    """
    Негативний тест: Спроба доступу до даних іншого користувача.
    """
    print("Start: test_access_alien_data")
    user1 = None
    user2 = None
    try:
        user1 = user_helper.create_unique_user()
        user2_name = f"{config.TEST_USER_PREFIX}{uuid.uuid4().hex[:6]}"
        user2_pass = "DifferentPass123!"
        requests.post(
            f"{config.BASE_URL}/users/",
            json={"username": user2_name, "password": user2_pass},
            timeout=10
        )
        user2 = {"username": user2_name, "password": user2_pass}
        # User1 намагається видалити User2
        resp = requests.delete(
            f"{config.BASE_URL}/users/{user2['username']}",
            headers={"X-User-Password": user1['password']},
            timeout=10
        )
        assert resp.status_code in [401, 403]
        print("  - Verbot des Löschens fremder Accounts bestanden")
    finally:
        if user1:
            user_helper.delete_user(user1['username'], user1['password'])
        if user2:
            user_helper.delete_user(user2['username'], user2['password'])

if __name__ == "__main__":
    try:
        test_user_lifecycle()
        test_delete_user_invalid_password()
        test_create_user_invalid()
        test_access_alien_data()
        print("Alle E2E Tests Users API (positiv & negativ) erfolgreich bestanden!\n")
    except Exception as e:
        print(f"Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
