import requests
from tests.e2e import config
import uuid

def create_unique_user():
    """
    Створює унікального користувача для тесту.
    Повертає словник з username та password.
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
    raise Exception(f"Помилка створення тестового користувача: {response.text}")

def delete_user(username, password):
    """
    Видаляє тестового користувача.
    Використовує заголовок X-User-Password для авторизації видалення.
    """
    requests.delete(
        f"{config.BASE_URL}/users/{username}",
        headers={"X-User-Password": password},
        timeout=10
    )
