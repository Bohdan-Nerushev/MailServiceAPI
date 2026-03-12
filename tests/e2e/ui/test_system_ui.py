import requests
from tests.e2e import config
from tests.e2e.utils import user_helper, auth_helper

def test_ui_system_pages():
    """
    Тести системних сторінок UI: Здоров'я та Список користувачів.
    """
    print("Запуск: test_ui_system_pages")
    
    user = user_helper.create_unique_user()
    session = auth_helper.get_ui_session(user['username'], user['password'])
    
    try:
        # 1. Перевірка сторінки Health
        health_resp = session.get(f"{config.BASE_URL}/ui/health", timeout=10)
        assert health_resp.status_code == 200
        assert "Postfix" in health_resp.text
        assert "Dovecot" in health_resp.text
        print("  - Сторінка системного здоров'я відображається коректно")

        # 2. Перевірка списку користувачів
        users_resp = session.get(f"{config.BASE_URL}/ui/users", timeout=10)
        assert users_resp.status_code == 200
        assert user['username'] in users_resp.text
        print(f"  - Користувач {user['username']} знайдений у веб-списку користувачів")

    finally:
        user_helper.delete_user(user['username'], user['password'])

if __name__ == "__main__":
    try:
        test_ui_system_pages()
        print("Усі тести System UI пройшли успішно!\n")
    except Exception as e:
        print(f"Тест провалено: {e}")
        exit(1)
